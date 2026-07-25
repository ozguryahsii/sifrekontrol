"""Şifre gücü analizi.

Birincil motor zxcvbn'dir (sözlük, klavye deseni, tarih, tekrar analizi).
zxcvbn kurulu değilse basit bir karakter kümesi entropi tahminine düşülür,
böylece uygulama sıfır bağımlılıkla da çalışabilir.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional

try:
    from zxcvbn import zxcvbn as _zxcvbn
except ImportError:  # pragma: no cover
    _zxcvbn = None


@dataclass
class StrengthResult:
    score: int                  # 0 (çok zayıf) .. 4 (çok güçlü)
    guesses_log10: float
    crack_time_offline_fast: str   # hızlı offline saldırı (10^10 tahmin/sn)
    crack_time_online: str         # hız sınırlı online saldırı (100 tahmin/saat)
    warnings: List[str]
    suggestions: List[str]
    engine: str                 # "zxcvbn" veya "fallback"


_SCORE_LABELS = {
    0: "çok zayıf",
    1: "zayıf",
    2: "orta",
    3: "güçlü",
    4: "çok güçlü",
}


def score_label(score: int) -> str:
    return _SCORE_LABELS.get(score, "?")


def _humanize_seconds(seconds: float) -> str:
    if seconds < 1:
        return "1 saniyeden az"
    units = [
        (60, "saniye"),
        (60, "dakika"),
        (24, "saat"),
        (365, "gün"),
        (100, "yıl"),
    ]
    value = seconds
    for factor, name in units:
        if value < factor:
            return f"{int(value)} {name}"
        value /= factor
    return "yüzyıllar"


_WARNING_TR = {
    "This is a top-10 common password": "Bu, en yaygın 10 şifreden biri",
    "This is a top-100 common password": "Bu, en yaygın 100 şifreden biri",
    "This is a very common password": "Bu çok yaygın bir şifre",
    "This is similar to a commonly used password": "Yaygın kullanılan bir şifreye çok benziyor",
    "A word by itself is easy to guess": "Tek başına bir sözcük kolay tahmin edilir",
    "Names and surnames by themselves are easy to guess": "Tek başına isim/soyisim kolay tahmin edilir",
    "Common names and surnames are easy to guess": "Yaygın isimler kolay tahmin edilir",
    "Straight rows of keys are easy to guess": "Klavyede yan yana tuşlar kolay tahmin edilir",
    "Short keyboard patterns are easy to guess": "Kısa klavye desenleri kolay tahmin edilir",
    'Repeats like "aaa" are easy to guess': '"aaa" gibi tekrarlar kolay tahmin edilir',
    'Repeats like "abcabcabc" are only slightly harder to guess than "abc"':
        '"abcabcabc" gibi tekrarlar "abc"den çok az daha zordur',
    'Sequences like abc or 6543 are easy to guess': '"abc" veya "6543" gibi diziler kolay tahmin edilir',
    "Recent years are easy to guess": "Yakın yıllar kolay tahmin edilir",
    "Dates are often easy to guess": "Tarihler genellikle kolay tahmin edilir",
}

_SUGGESTION_TR = {
    "Use a few words, avoid common phrases": "Birkaç sözcük kullanın, yaygın kalıplardan kaçının",
    "No need for symbols, digits, or uppercase letters":
        "Uzunluk yeterliyse sembol/rakam/büyük harf zorunlu değildir",
    "Add another word or two. Uncommon words are better.":
        "Bir iki sözcük daha ekleyin; nadir sözcükler daha iyidir",
    "Use a longer keyboard pattern with more turns":
        "Daha uzun ve yön değiştiren bir desen kullanın",
    "Avoid repeated words and characters": "Tekrarlanan sözcük ve karakterlerden kaçının",
    "Avoid sequences": "Ardışık dizilerden kaçının",
    "Avoid recent years": "Yakın yıllardan kaçının",
    "Avoid years that are associated with you": "Sizinle ilişkili yıllardan kaçının",
    "Avoid dates and years that are associated with you":
        "Sizinle ilişkili tarih ve yıllardan kaçının",
    "Capitalization doesn't help very much": "Baş harfi büyütmek pek yardımcı olmaz",
    "All-uppercase is almost as easy to guess as all-lowercase":
        "Tümü büyük harf, tümü küçük harf kadar kolay tahmin edilir",
    "Reversed words aren't much harder to guess": "Ters yazılmış sözcükler pek daha zor değildir",
    "Predictable substitutions like '@' instead of 'a' don't help very much":
        "'a' yerine '@' gibi öngörülebilir değişimler pek yardımcı olmaz",
}


def _translate(text: str, table: dict) -> str:
    # zxcvbn sürümüne göre metinler sonda nokta içerebiliyor
    return table.get(text) or table.get(text.rstrip(".")) or text


def analyze(password: str) -> StrengthResult:
    if _zxcvbn is not None:
        r = _zxcvbn(password)
        guesses = float(r["guesses"])
        feedback = r.get("feedback") or {}
        warning = feedback.get("warning") or ""
        return StrengthResult(
            score=int(r["score"]),
            guesses_log10=math.log10(max(guesses, 1.0)),
            crack_time_offline_fast=_humanize_seconds(guesses / 1e10),
            crack_time_online=_humanize_seconds(guesses / (100 / 3600)),
            warnings=[_translate(warning, _WARNING_TR)] if warning else [],
            suggestions=[
                _translate(s, _SUGGESTION_TR) for s in feedback.get("suggestions") or []
            ],
            engine="zxcvbn",
        )
    return _fallback_analyze(password)


def _fallback_analyze(password: str) -> StrengthResult:
    """zxcvbn yoksa kaba entropi tahmini: karakter kümesi ^ uzunluk."""
    charset = 0
    if any(c.islower() for c in password):
        charset += 26
    if any(c.isupper() for c in password):
        charset += 26
    if any(c.isdigit() for c in password):
        charset += 10
    if any(not c.isalnum() for c in password):
        charset += 33
    charset = max(charset, 1)
    guesses = float(charset) ** len(password)
    log10 = len(password) * math.log10(charset)
    score = min(4, max(0, int((log10 - 3) / 3)))
    return StrengthResult(
        score=score,
        guesses_log10=log10,
        crack_time_offline_fast=_humanize_seconds(guesses / 1e10),
        crack_time_online=_humanize_seconds(guesses / (100 / 3600)),
        warnings=["zxcvbn kurulu değil; kaba entropi tahmini kullanıldı"],
        suggestions=["Daha isabetli analiz için 'pip install zxcvbn' kurun"],
        engine="fallback",
    )
