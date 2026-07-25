"""sifrekontrol komut satırı arayüzü.

Gizlilik ilkeleri:
  - Şifre yalnızca etkileşimli gizli girişle (getpass) veya stdin'den alınır;
    komut satırı argümanı olarak KABUL EDİLMEZ (kabuk geçmişine düşmesin diye).
  - Şifre ve hash'i diske yazılmaz, loglanmaz, ağa gönderilmez.
  - Sızıntı sorgusu tamamen lokal veri seti üzerinde çalışır.
"""

from __future__ import annotations

import argparse
import getpass
import hashlib
import os
import sys
from pathlib import Path
from typing import Optional

from . import __version__
from .store import Store


def default_data_dir() -> Path:
    env = os.environ.get("SIFREKONTROL_DATA")
    if env:
        return Path(env)
    xdg = os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local" / "share"))
    return Path(xdg) / "sifrekontrol"


def _read_password(use_stdin: bool) -> str:
    if use_stdin:
        pw = sys.stdin.readline().rstrip("\n")
    else:
        pw = getpass.getpass("Kontrol edilecek şifre (ekranda görünmez): ")
    if not pw:
        print("Boş şifre girildi.", file=sys.stderr)
        sys.exit(2)
    return pw


def cmd_check(args: argparse.Namespace) -> int:
    from .regulations import evaluate
    from .report import render_json, render_text
    from .strength import analyze

    password = _read_password(args.stdin)
    length = len(password)

    breach_count: Optional[int] = None
    store = Store(args.data_dir)
    digest = hashlib.sha1(password.encode("utf-8")).digest()
    try:
        breach_count = store.lookup(digest)
    except FileNotFoundError:
        breach_count = None

    strength = analyze(password)
    regulations = evaluate(password, breach_count, strength.score)
    del password, digest  # bellekteki referansları en erken noktada bırak

    if args.json:
        print(render_json(length, strength, breach_count, regulations))
    else:
        color = sys.stdout.isatty() and not args.no_color
        print(render_text(length, strength, breach_count, regulations, color=color))

    if breach_count:
        return 1  # betiklerde kullanım için: sızmış şifre = çıkış kodu 1
    return 0


def _run_sync(args: argparse.Namespace, mode: str) -> int:
    from .downloader import print_progress, sync

    store = Store(args.data_dir)
    label = "indirme" if mode == "download" else "güncelleme"
    print(f"HIBP veri seti {label} başlıyor (hedef: {store.data_dir})", file=sys.stderr)
    if mode == "download":
        print(
            "Uyarı: tam veri seti ~%s GB disk kullanır ve ilk indirme saatler sürebilir.\n"
            "Yarıda kesilirse aynı komut kaldığı yerden devam eder." % "25-30",
            file=sys.stderr,
        )
    stats = sync(store, mode=mode, workers=args.workers, progress=print_progress)
    print(
        f"Bitti: {stats.groups_done} grup işlendi, {stats.groups_skipped} atlandı, "
        f"{stats.ranges_fetched} aralık indirildi, {stats.ranges_unchanged} değişmedi.",
        file=sys.stderr,
    )
    if stats.errors:
        print(
            f"{len(stats.errors)} grup hata verdi; komutu tekrar çalıştırmak "
            "eksikleri tamamlar.",
            file=sys.stderr,
        )
        return 1
    return 0


def cmd_download(args: argparse.Namespace) -> int:
    return _run_sync(args, "download")


def cmd_update(args: argparse.Namespace) -> int:
    return _run_sync(args, "update")


def cmd_status(args: argparse.Namespace) -> int:
    st = Store(args.data_dir).status()
    gb = st["size_bytes"] / (1024**3)
    records = f"{st['records']:,}".replace(",", ".")
    print(f"Veri dizini      : {st['data_dir']}")
    print(f"Grup dosyaları   : {st['groups_present']}/{st['groups_total']}"
          + ("  (tam)" if st["complete"] else "  (eksik — 'download' ile tamamlayın)"))
    print(f"Kayıt sayısı     : {records} sızmış şifre hash'i")
    print(f"Disk kullanımı   : {gb:.1f} GB")
    print(f"Son senkron      : {st['last_sync'] or '-'} @ {st['updated_at'] or '-'}")
    return 0


def main(argv: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="sifrekontrol",
        description="Tamamen lokal şifre güvenlik denetleyicisi "
        "(HIBP offline veri seti + güç analizi + regülasyon uyumluluğu).",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=default_data_dir(),
        help="HIBP veri seti dizini (varsayılan: %(default)s)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_check = sub.add_parser("check", help="Bir şifreyi analiz et (şifre asla saklanmaz)")
    p_check.add_argument("--stdin", action="store_true", help="şifreyi stdin'den oku")
    p_check.add_argument("--json", action="store_true", help="raporu JSON olarak yazdır")
    p_check.add_argument("--no-color", action="store_true", help="renkli çıktıyı kapat")
    p_check.set_defaults(func=cmd_check)

    p_dl = sub.add_parser("download", help="HIBP veri setini indir (kaldığı yerden sürer)")
    p_dl.add_argument("--workers", type=int, default=32, help="eşzamanlı istek sayısı")
    p_dl.set_defaults(func=cmd_download)

    p_up = sub.add_parser("update", help="Veri setini artımlı güncelle (ETag ile)")
    p_up.add_argument("--workers", type=int, default=32, help="eşzamanlı istek sayısı")
    p_up.set_defaults(func=cmd_update)

    p_st = sub.add_parser("status", help="Lokal veri setinin durumunu göster")
    p_st.set_defaults(func=cmd_status)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
