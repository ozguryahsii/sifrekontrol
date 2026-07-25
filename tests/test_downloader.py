import tempfile
import unittest
from pathlib import Path

from sifrekontrol.downloader import sync
from sifrekontrol.store import Store, ranges_of_group


class FakeServer:
    """HIBP range API'sini taklit eder: ETag + koşullu istek (304) davranışı."""

    def __init__(self):
        self.data = {}   # prefix -> (etag, body)
        self.requests = []

    def set_range(self, prefix: str, etag: str, suffix_counts):
        body = "\r\n".join(f"{s}:{c}" for s, c in suffix_counts)
        self.data[prefix] = (etag, body)

    def fetch(self, prefix: str, etag):
        self.requests.append((prefix, etag))
        cur_etag, body = self.data.get(prefix, ('"empty"', ""))
        if etag is not None and etag == cur_etag:
            return 304, etag, None
        return 200, cur_etag, body


def suffix(ch: str) -> str:
    return ch * 35


class DownloaderTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.store = Store(Path(self._tmp.name))
        self.server = FakeServer()
        # Testler tek grup üzerinde çalışır (4096 grubun tamamı yerine)
        self.group = "0A0"
        for i, prefix in enumerate(ranges_of_group(self.group)):
            self.server.set_range(prefix, f'"v1-{prefix}"', [(suffix("A"), i + 1)])

    def tearDown(self):
        self._tmp.cleanup()

    def test_initial_download(self):
        stats = sync(
            self.store, mode="download", workers=4,
            fetcher=self.server.fetch, groups=[self.group],
        )
        self.assertEqual(stats.groups_done, 1)
        self.assertEqual(stats.ranges_fetched, 256)
        self.assertEqual(stats.records_written, 256)
        # Sorgu çalışıyor mu?
        h = bytes.fromhex(self.group + "00" + suffix("A"))
        self.assertEqual(self.store.lookup(h), 1)
        # ETag'ler kaydedildi mi?
        self.assertEqual(len(self.store.load_etags()), 256)

    def test_download_resume_skips_complete_groups(self):
        sync(self.store, mode="download", workers=4,
             fetcher=self.server.fetch, groups=[self.group])
        self.server.requests.clear()
        stats = sync(self.store, mode="download", workers=4,
                     fetcher=self.server.fetch, groups=[self.group])
        self.assertEqual(stats.groups_skipped, 1)
        self.assertEqual(self.server.requests, [])  # hiç HTTP isteği atılmadı

    def test_update_unchanged_uses_304(self):
        sync(self.store, mode="download", workers=4,
             fetcher=self.server.fetch, groups=[self.group])
        stats = sync(self.store, mode="update", workers=4,
                     fetcher=self.server.fetch, groups=[self.group])
        self.assertEqual(stats.ranges_unchanged, 256)
        self.assertEqual(stats.ranges_fetched, 0)
        self.assertEqual(stats.records_written, 0)

    def test_update_applies_only_changed_ranges(self):
        sync(self.store, mode="download", workers=4,
             fetcher=self.server.fetch, groups=[self.group])
        # Tek bir aralık değişsin: yeni bir hash eklendi, sayaç güncellendi
        changed_prefix = self.group + "07"
        self.server.set_range(
            changed_prefix, f'"v2-{changed_prefix}"',
            [(suffix("A"), 500), (suffix("B"), 42)],
        )
        stats = sync(self.store, mode="update", workers=4,
                     fetcher=self.server.fetch, groups=[self.group])
        self.assertEqual(stats.ranges_fetched, 1)
        self.assertEqual(stats.ranges_unchanged, 255)

        self.assertEqual(self.store.lookup(bytes.fromhex(changed_prefix + suffix("A"))), 500)
        self.assertEqual(self.store.lookup(bytes.fromhex(changed_prefix + suffix("B"))), 42)
        # Değişmeyen aralık korunmuş olmalı
        self.assertEqual(self.store.lookup(bytes.fromhex(self.group + "00" + suffix("A"))), 1)

    def test_fetch_error_does_not_abort_other_groups(self):
        group2 = "0A1"
        for i, prefix in enumerate(ranges_of_group(group2)):
            self.server.set_range(prefix, f'"v1-{prefix}"', [(suffix("C"), i + 1)])

        def flaky_fetch(prefix, etag):
            if prefix.startswith(self.group):
                raise RuntimeError("simüle ağ hatası")
            return self.server.fetch(prefix, etag)

        stats = sync(self.store, mode="download", workers=4,
                     fetcher=flaky_fetch, groups=[self.group, group2])
        self.assertEqual(len(stats.errors), 1)
        self.assertEqual(stats.groups_done, 1)
        self.assertTrue(self.store.has_group(group2))
        self.assertFalse(self.store.has_group(self.group))


if __name__ == "__main__":
    unittest.main()
