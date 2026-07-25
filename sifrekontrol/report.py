"""Analiz sonuçlarını terminal raporu veya JSON olarak biçimlendirir.

Rapor şifrenin kendisini, hash'ini veya herhangi bir türevini ASLA içermez;
yalnızca uzunluk gibi türetilmiş nitelikler gösterilir.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from typing import List, Optional

from .regulations import RegulationResult
from .strength import StrengthResult, score_label

GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
BOLD = "\033[1m"
RESET = "\033[0m"


def _mark(passed: Optional[bool], color: bool) -> str:
    if passed is True:
        return f"{GREEN}✔{RESET}" if color else "[+]"
    if passed is False:
        return f"{RED}✘{RESET}" if color else "[-]"
    return f"{YELLOW}?{RESET}" if color else "[?]"


def render_text(
    length: int,
    strength: StrengthResult,
    breach_count: Optional[int],
    regulations: List[RegulationResult],
    color: bool = True,
) -> str:
    b = (lambda s: f"{BOLD}{s}{RESET}") if color else (lambda s: s)
    lines: List[str] = []
    lines.append(b("── ŞİFRE GÜVENLİK RAPORU ──────────────────────────────"))
    lines.append(f"Uzunluk: {length} karakter   (şifre hiçbir yere kaydedilmedi)")
    lines.append("")

    lines.append(b("Güç analizi"))
    lines.append(f"  Skor: {strength.score}/4 ({score_label(strength.score)})")
    lines.append(f"  Tahmini kırılma süresi (hızlı offline saldırı): {strength.crack_time_offline_fast}")
    lines.append(f"  Tahmini kırılma süresi (hız sınırlı online): {strength.crack_time_online}")
    for w in strength.warnings:
        lines.append(f"  Uyarı: {w}")
    for s in strength.suggestions:
        lines.append(f"  Öneri: {s}")
    lines.append("")

    lines.append(b("Sızıntı kontrolü (HIBP offline veri seti)"))
    if breach_count is None:
        lines.append("  Veri seti indirilmemiş — 'sifrekontrol download' ile kurabilirsiniz.")
    elif breach_count > 0:
        n = f"{breach_count:,}".replace(",", ".")
        lines.append(
            f"  {_mark(False, color)} Bu şifre bilinen sızıntılarda {n} kez görüldü."
        )
        lines.append(
            "  Not: Veri seti hangi sitede sızdığını içermez (anonimleştirilmiştir);"
        )
        lines.append("  yalnızca toplam görülme sayısı bilinir. Bu şifreyi KULLANMAYIN.")
    else:
        lines.append(f"  {_mark(True, color)} Bilinen sızıntı listelerinde bulunamadı.")
    lines.append("")

    lines.append(b("Regülasyon / standart uyumluluğu"))
    for reg in regulations:
        lines.append(f"  {_mark(reg.passed, color)} {reg.name}")
        lines.append(f"      Kapsam: {reg.scope}")
        for req in reg.requirements:
            detail = f" — {req.detail}" if req.detail else ""
            lines.append(f"      {_mark(req.passed, color)} {req.description}{detail}")
    lines.append("")

    verdict_parts = []
    failed = [r.name.split(" (")[0] for r in regulations if r.passed is False]
    if breach_count and breach_count > 0:
        verdict_parts.append("şifre sızmış — derhal değiştirin")
    elif strength.score < 3:
        verdict_parts.append("şifre yeterince güçlü değil")
    if failed:
        verdict_parts.append("karşılanmayan standartlar: " + ", ".join(failed))
    if not verdict_parts:
        verdict_parts.append("şifre güçlü görünüyor ve değerlendirilen standartları karşılıyor")
    lines.append(b("Sonuç: ") + "; ".join(verdict_parts))
    return "\n".join(lines)


def render_json(
    length: int,
    strength: StrengthResult,
    breach_count: Optional[int],
    regulations: List[RegulationResult],
) -> str:
    payload = {
        "length": length,
        "strength": asdict(strength),
        "breach_count": breach_count,
        "regulations": [
            {
                "id": r.reg_id,
                "name": r.name,
                "scope": r.scope,
                "passed": r.passed,
                "requirements": [asdict(q) for q in r.requirements],
            }
            for r in regulations
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)
