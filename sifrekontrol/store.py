"""HIBP veri setinin lokal binary deposu.

Düzen:
  <data_dir>/groups/XXX.bin   — XXX: SHA-1 hash'inin ilk 3 hex karakteri (4096 dosya).
                                Her kayıt sabit 24 bayt: 20 bayt SHA-1 + 4 bayt big-endian
                                görülme sayısı. Kayıtlar hash'e göre sıralı tutulur,
                                sorgu mmap üzerinde binary search ile yapılır.
  <data_dir>/etags.tsv        — her 5-hex HIBP aralığı için son bilinen ETag
                                (artımlı güncellemenin temeli).
  <data_dir>/meta.json        — veri seti durumu (son güncelleme, kayıt sayısı).

Şifre veya şifre hash'i bu depoya asla YAZILMAZ; depo yalnızca HIBP'den
indirilen sızmış şifre hash'lerini içerir.
"""

from __future__ import annotations

import json
import mmap
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

RECORD_SIZE = 24  # 20 bayt SHA-1 + 4 bayt sayaç
HASH_SIZE = 20
GROUP_HEX_LEN = 3        # grup dosyası öneki (XXX.bin)
RANGE_HEX_LEN = 5        # HIBP range API öneki (XXXXX)
RANGES_PER_GROUP = 16 ** (RANGE_HEX_LEN - GROUP_HEX_LEN)  # 256
TOTAL_GROUPS = 16 ** GROUP_HEX_LEN                        # 4096
TOTAL_RANGES = 16 ** RANGE_HEX_LEN                        # 1_048_576


def all_groups() -> Iterable[str]:
    """Tüm 3-hex grup öneklerini sırayla üretir: 000, 001, ... FFF."""
    for i in range(TOTAL_GROUPS):
        yield f"{i:03X}"


def ranges_of_group(group: str) -> List[str]:
    """Bir grubun kapsadığı 256 adet 5-hex aralık önekini döndürür."""
    return [f"{group}{i:02X}" for i in range(RANGES_PER_GROUP)]


def pack_records(records: Iterable[Tuple[bytes, int]]) -> bytes:
    """(hash, sayaç) çiftlerini sıralı sabit boyutlu kayıt bloğuna çevirir."""
    out = bytearray()
    for h, count in sorted(records):
        if len(h) != HASH_SIZE:
            raise ValueError(f"gecersiz hash uzunlugu: {len(h)}")
        out += h + min(count, 0xFFFFFFFF).to_bytes(4, "big")
    return bytes(out)


def parse_range_body(prefix: str, body: str) -> List[Tuple[bytes, int]]:
    """HIBP range API gövdesini (SUFFIX:COUNT satırları) kayıtlara çevirir."""
    records = []
    for line in body.splitlines():
        line = line.strip()
        if not line:
            continue
        suffix, _, count = line.partition(":")
        records.append((bytes.fromhex(prefix + suffix), int(count or 0)))
    return records


class Store:
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.groups_dir = self.data_dir / "groups"
        self.etags_path = self.data_dir / "etags.tsv"
        self.meta_path = self.data_dir / "meta.json"

    # ---- grup dosyaları ----

    def group_path(self, group: str) -> Path:
        return self.groups_dir / f"{group.upper()}.bin"

    def has_group(self, group: str) -> bool:
        return self.group_path(group).exists()

    def write_group(self, group: str, records: Iterable[Tuple[bytes, int]]) -> int:
        """Grup dosyasını atomik olarak (tmp + rename) yazar, kayıt sayısını döndürür."""
        data = pack_records(records)
        self.groups_dir.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=self.groups_dir, suffix=".tmp")
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(data)
            os.replace(tmp, self.group_path(group))
        except BaseException:
            if os.path.exists(tmp):
                os.unlink(tmp)
            raise
        return len(data) // RECORD_SIZE

    def read_group(self, group: str) -> List[Tuple[bytes, int]]:
        path = self.group_path(group)
        if not path.exists():
            return []
        raw = path.read_bytes()
        return [
            (raw[i : i + HASH_SIZE], int.from_bytes(raw[i + HASH_SIZE : i + RECORD_SIZE], "big"))
            for i in range(0, len(raw), RECORD_SIZE)
        ]

    def replace_ranges_in_group(
        self, group: str, new_by_range: Dict[str, List[Tuple[bytes, int]]]
    ) -> int:
        """Artımlı güncelleme: grup içindeki yalnızca değişen aralıkları değiştirir.

        Değişmeyen aralıkların kayıtları mevcut dosyadan korunur; değişen
        aralıkların eski kayıtları atılıp yenileri konur.
        """
        changed = {p.upper() for p in new_by_range}
        kept = [
            rec
            for rec in self.read_group(group)
            if rec[0].hex().upper()[:RANGE_HEX_LEN] not in changed
        ]
        for recs in new_by_range.values():
            kept.extend(recs)
        return self.write_group(group, kept)

    # ---- sorgu ----

    def lookup(self, sha1_digest: bytes) -> int:
        """Hash'in sızıntılarda kaç kez görüldüğünü döndürür (0 = kayıt yok).

        Sorgu tamamen lokaldir; hash hiçbir yere yazılmaz veya gönderilmez.
        """
        if len(sha1_digest) != HASH_SIZE:
            raise ValueError("SHA-1 digest 20 bayt olmali")
        group = sha1_digest.hex().upper()[:GROUP_HEX_LEN]
        path = self.group_path(group)
        if not path.exists():
            raise FileNotFoundError(
                f"grup dosyasi eksik: {path} — once 'sifrekontrol download' calistirin"
            )
        with open(path, "rb") as f:
            size = os.fstat(f.fileno()).st_size
            if size == 0:
                return 0
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                lo, hi = 0, size // RECORD_SIZE
                while lo < hi:
                    mid = (lo + hi) // 2
                    off = mid * RECORD_SIZE
                    h = mm[off : off + HASH_SIZE]
                    if h < sha1_digest:
                        lo = mid + 1
                    elif h > sha1_digest:
                        hi = mid
                    else:
                        return int.from_bytes(mm[off + HASH_SIZE : off + RECORD_SIZE], "big")
        return 0

    # ---- ETag manifesti ----

    def load_etags(self) -> Dict[str, str]:
        etags: Dict[str, str] = {}
        if self.etags_path.exists():
            with open(self.etags_path, "r", encoding="utf-8") as f:
                for line in f:
                    prefix, _, etag = line.rstrip("\n").partition("\t")
                    if prefix and etag:
                        etags[prefix] = etag
        return etags

    def save_etags(self, etags: Dict[str, str]) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=self.data_dir, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                for prefix in sorted(etags):
                    f.write(f"{prefix}\t{etags[prefix]}\n")
            os.replace(tmp, self.etags_path)
        except BaseException:
            if os.path.exists(tmp):
                os.unlink(tmp)
            raise

    # ---- meta ----

    def load_meta(self) -> dict:
        if self.meta_path.exists():
            return json.loads(self.meta_path.read_text(encoding="utf-8"))
        return {}

    def save_meta(self, **updates) -> dict:
        meta = self.load_meta()
        meta.update(updates)
        meta["updated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.meta_path.write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return meta

    def status(self) -> dict:
        """Veri seti durumu: grup sayısı, kayıt sayısı, boyut, son güncelleme."""
        present = 0
        total_bytes = 0
        if self.groups_dir.exists():
            for entry in os.scandir(self.groups_dir):
                if entry.name.endswith(".bin"):
                    present += 1
                    total_bytes += entry.stat().st_size
        meta = self.load_meta()
        return {
            "data_dir": str(self.data_dir),
            "groups_present": present,
            "groups_total": TOTAL_GROUPS,
            "complete": present == TOTAL_GROUPS,
            "records": total_bytes // RECORD_SIZE,
            "size_bytes": total_bytes,
            "updated_at": meta.get("updated_at"),
            "last_sync": meta.get("last_sync"),
        }
