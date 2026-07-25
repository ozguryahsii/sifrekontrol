import hashlib
import tempfile
import unittest
from pathlib import Path

from sifrekontrol.store import Store, parse_range_body


def fake_hash(group: str, seed: int) -> bytes:
    """Verilen 3-hex grupla başlayan deterministik 20 baytlık hash üretir."""
    body = hashlib.sha1(str(seed).encode()).hexdigest().upper()
    return bytes.fromhex((group + body)[:40])


class StoreTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.store = Store(Path(self._tmp.name))

    def tearDown(self):
        self._tmp.cleanup()

    def test_write_and_lookup(self):
        h1 = fake_hash("ABC", 1)
        h2 = fake_hash("ABC", 2)
        self.store.write_group("ABC", [(h2, 7), (h1, 12345)])
        self.assertEqual(self.store.lookup(h1), 12345)
        self.assertEqual(self.store.lookup(h2), 7)

    def test_lookup_missing_hash_returns_zero(self):
        self.store.write_group("ABC", [(fake_hash("ABC", 1), 5)])
        self.assertEqual(self.store.lookup(fake_hash("ABC", 99)), 0)

    def test_lookup_missing_group_raises(self):
        with self.assertRaises(FileNotFoundError):
            self.store.lookup(fake_hash("DEF", 1))

    def test_lookup_large_group_binary_search(self):
        records = [(fake_hash("012", i), i + 1) for i in range(500)]
        self.store.write_group("012", records)
        for h, c in records[::37]:
            self.assertEqual(self.store.lookup(h), c)

    def test_replace_ranges_incremental_update(self):
        # Aynı grupta iki farklı aralık: ABC00... ve ABC01...
        r0_old = (bytes.fromhex("ABC00" + "0" * 35), 10)
        r1_keep = (bytes.fromhex("ABC01" + "1" * 35), 20)
        self.store.write_group("ABC", [r0_old, r1_keep])

        # ABC00 aralığı değişti: eski kayıt gitmeli, yenisi gelmeli
        r0_new = (bytes.fromhex("ABC00" + "F" * 35), 99)
        self.store.replace_ranges_in_group("ABC", {"ABC00": [r0_new]})

        self.assertEqual(self.store.lookup(r0_old[0]), 0)
        self.assertEqual(self.store.lookup(r0_new[0]), 99)
        self.assertEqual(self.store.lookup(r1_keep[0]), 20)

    def test_parse_range_body(self):
        body = "0018A45C4D1DEF81644B54AB7F969B88D65:3\r\n00D4F6E8FA6EECAD2A3AA415EEC418D38EC:2\n"
        records = parse_range_body("21BD1", body)
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0][0].hex().upper(), "21BD10018A45C4D1DEF81644B54AB7F969B88D65")
        self.assertEqual(records[0][1], 3)

    def test_etag_roundtrip(self):
        etags = {"00000": 'W/"abc"', "FFFFF": '"xyz"'}
        self.store.save_etags(etags)
        self.assertEqual(self.store.load_etags(), etags)

    def test_status(self):
        self.store.write_group("000", [(fake_hash("000", 1), 1)])
        st = self.store.status()
        self.assertEqual(st["groups_present"], 1)
        self.assertEqual(st["records"], 1)
        self.assertFalse(st["complete"])


if __name__ == "__main__":
    unittest.main()
