"""HIBP Pwned Passwords veri setini indirir ve artımlı olarak günceller.

HIBP artık tek parça bir dump yayınlamıyor; resmi yöntem, range API'sindeki
1.048.576 aralık dosyasını (https://api.pwnedpasswords.com/range/XXXXX)
indirmektir. Her aralık bir ETag ile sunulur ve Cloudflare üzerinden
önbelleklenir. Güncelleme bu yüzden artımlıdır:

  - İlk indirme: tüm aralıklar çekilir, ETag'leri kaydedilir.
  - Güncelleme: her aralık If-None-Match ile sorulur; değişmeyenler 304 döner
    (gövde indirilmez), yalnızca değişen aralıklar yeniden indirilir ve
    ilgili grup dosyası yerinde yeniden yazılır.

Bu sayede günlük (veya istenen sıklıkta) güncelleme mümkündür; tipik bir
güncelleme turunda trafiğin büyük kısmı gövdesiz 304 yanıtlarıdır.
"""

from __future__ import annotations

import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

from . import __version__
from .store import Store, all_groups, parse_range_body, ranges_of_group

BASE_URL = "https://api.pwnedpasswords.com/range/"
USER_AGENT = f"sifrekontrol/{__version__} (yerel sifre denetleyicisi)"
RETRIES = 5
ETAG_FLUSH_EVERY = 32  # kaç grupta bir etags.tsv diske yazılsın

# (status, etag, body) — 304'te body None döner
FetchResult = Tuple[int, Optional[str], Optional[str]]
Fetcher = Callable[[str, Optional[str]], FetchResult]


def http_fetch(prefix: str, etag: Optional[str]) -> FetchResult:
    """Tek bir HIBP aralığını çeker; etag verilirse koşullu istek yapar."""
    req = urllib.request.Request(BASE_URL + prefix, headers={"User-Agent": USER_AGENT})
    if etag:
        req.add_header("If-None-Match", etag)
    last_err: Exception = RuntimeError("erisim denenmedi")
    for attempt in range(RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.status, resp.headers.get("ETag"), resp.read().decode("ascii")
        except urllib.error.HTTPError as e:
            if e.code == 304:
                return 304, etag, None
            last_err = e
            if e.code not in (429, 500, 502, 503, 504):
                raise
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            last_err = e
        time.sleep(min(2 ** attempt, 30))
    raise RuntimeError(f"aralik {prefix} indirilemedi: {last_err}")


@dataclass
class SyncStats:
    groups_done: int = 0
    groups_skipped: int = 0
    ranges_fetched: int = 0
    ranges_unchanged: int = 0
    records_written: int = 0
    errors: List[str] = field(default_factory=list)


def sync(
    store: Store,
    mode: str = "download",
    workers: int = 32,
    fetcher: Fetcher = http_fetch,
    progress: Optional[Callable[[str], None]] = None,
    groups: Optional[List[str]] = None,
) -> SyncStats:
    """Veri setini indirir (mode="download") veya günceller (mode="update").

    download: ETag'leri tam olan ve dosyası mevcut gruplara hiç istek atmaz
              (yarıda kesilen indirme kaldığı yerden sürer).
    update:   her aralık için koşullu istek atar; yalnızca 200 dönen
              aralıkların bulunduğu grup dosyaları yeniden yazılır.
    """
    if mode not in ("download", "update"):
        raise ValueError(f"gecersiz mod: {mode}")
    say = progress or (lambda msg: None)
    etags = store.load_etags()
    stats = SyncStats()
    group_list = groups if groups is not None else list(all_groups())
    dirty_etags = 0

    with ThreadPoolExecutor(max_workers=workers) as pool:
        for group in group_list:
            prefixes = ranges_of_group(group)

            if (
                mode == "download"
                and store.has_group(group)
                and all(p in etags for p in prefixes)
            ):
                stats.groups_skipped += 1
                continue

            def task(prefix: str) -> Tuple[str, FetchResult]:
                known = etags.get(prefix) if mode == "update" else None
                return prefix, fetcher(prefix, known)

            changed: Dict[str, List] = {}
            try:
                for prefix, (status, etag, body) in pool.map(task, prefixes):
                    if status == 304:
                        stats.ranges_unchanged += 1
                        continue
                    stats.ranges_fetched += 1
                    changed[prefix] = parse_range_body(prefix, body or "")
                    if etag:
                        etags[prefix] = etag
            except Exception as e:  # tek grup hatası tüm senkronu düşürmesin
                stats.errors.append(f"{group}: {e}")
                say(f"HATA grup {group}: {e}")
                continue

            if changed:
                if mode == "update" and store.has_group(group):
                    n = store.replace_ranges_in_group(group, changed)
                else:
                    records = [r for recs in changed.values() for r in recs]
                    n = store.write_group(group, records)
                stats.records_written += n
                dirty_etags += 1
                if dirty_etags >= ETAG_FLUSH_EVERY:
                    store.save_etags(etags)
                    dirty_etags = 0

            stats.groups_done += 1
            done = stats.groups_done + stats.groups_skipped
            if done % 64 == 0 or done == len(group_list):
                say(
                    f"[{done}/{len(group_list)}] grup tamam — "
                    f"{stats.ranges_fetched} aralik indirildi, "
                    f"{stats.ranges_unchanged} degismedi"
                )

    if dirty_etags:
        store.save_etags(etags)
    store.save_meta(last_sync=mode, ranges_with_etag=len(etags))
    return stats


def print_progress(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)
