"""Regülasyon ve standart uyumluluk kural motoru.

Her standart, şifreye uygulanabilir gereksinimlerinin listesini üretir.
Kontroller yalnızca şifrenin kendisi, sızıntı sayısı ve güç skoru üzerinden
lokal olarak değerlendirilir; hiçbir kural şifreyi dışarı çıkarmaz.

Not: Bu standartların çoğu şifre *politikası* tanımlar (deneme kilitleme,
MFA, saklama biçimi gibi). Burada yalnızca tek bir şifrenin kendisine
uygulanabilir maddeler değerlendirilir; kapsam her standardın "scope"
alanında belirtilir.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Requirement:
    description: str
    passed: Optional[bool]  # None = veri seti yokken değerlendirilemedi
    detail: str = ""


@dataclass
class RegulationResult:
    reg_id: str
    name: str
    scope: str
    requirements: List[Requirement] = field(default_factory=list)

    @property
    def passed(self) -> Optional[bool]:
        results = [r.passed for r in self.requirements]
        if any(r is False for r in results):
            return False
        if any(r is None for r in results):
            return None
        return True


def _breach_req(breach_count: Optional[int]) -> Requirement:
    if breach_count is None:
        return Requirement(
            "Bilinen sızıntı listelerinde bulunmamalı",
            None,
            "HIBP veri seti indirilmemiş; kontrol yapılamadı",
        )
    if breach_count > 0:
        return Requirement(
            "Bilinen sızıntı listelerinde bulunmamalı",
            False,
            f"sızıntılarda {breach_count:,} kez görüldü".replace(",", "."),
        )
    return Requirement("Bilinen sızıntı listelerinde bulunmamalı", True)


def evaluate(
    password: str, breach_count: Optional[int], strength_score: int
) -> List[RegulationResult]:
    n = len(password)
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(not c.isalnum() for c in password)
    has_alpha = has_lower or has_upper

    results: List[RegulationResult] = []

    nist = RegulationResult(
        "nist-800-63b",
        "NIST SP 800-63B (ABD dijital kimlik rehberi)",
        "Bellek tabanlı doğrulayıcılar (memorized secrets) için şifre gereksinimleri",
    )
    nist.requirements = [
        Requirement("En az 8 karakter", n >= 8, f"uzunluk: {n}"),
        _breach_req(breach_count),
        Requirement(
            "Karmaşıklık dayatması aranmaz (uzunluk + sızıntı kontrolü esastır)",
            True,
            "bilgi amaçlı: NIST bileşim kuralı zorunlu tutmaz",
        ),
    ]
    results.append(nist)

    pci = RegulationResult(
        "pci-dss-4",
        "PCI DSS v4.0 (ödeme kartı endüstrisi)",
        "Gereksinim 8.3.6 — kullanıcı parolası asgari nitelikleri",
    )
    pci.requirements = [
        Requirement("En az 12 karakter", n >= 12, f"uzunluk: {n}"),
        Requirement("Hem harf hem rakam içermeli", has_alpha and has_digit),
    ]
    results.append(pci)

    owasp = RegulationResult(
        "owasp-asvs-4",
        "OWASP ASVS 4.0 (uygulama güvenliği doğrulama standardı)",
        "V2.1 — parola güvenliği gereksinimleri (L1)",
    )
    owasp.requirements = [
        Requirement("En az 12 karakter (2.1.1)", n >= 12, f"uzunluk: {n}"),
        Requirement("128 karakteri aşmamalı (2.1.2)", n <= 128),
        _breach_req(breach_count),
    ]
    results.append(owasp)

    cis = RegulationResult(
        "cis-password-guide",
        "CIS Parola Politikası Rehberi",
        "MFA olmadan yalnız parola ile kimlik doğrulama senaryosu",
    )
    cis.requirements = [
        Requirement("En az 14 karakter (MFA yoksa)", n >= 14, f"uzunluk: {n}"),
        _breach_req(breach_count),
    ]
    results.append(cis)

    kvkk = RegulationResult(
        "kvkk-rehber",
        "KVKK Kişisel Veri Güvenliği Rehberi (Türkiye)",
        "Rehberde önerilen güçlü parola nitelikleri (tavsiye niteliğinde)",
    )
    kvkk.requirements = [
        Requirement("En az 8 karakter", n >= 8, f"uzunluk: {n}"),
        Requirement(
            "Büyük/küçük harf, rakam ve sembol birlikte kullanılmalı",
            has_lower and has_upper and has_digit and has_symbol,
        ),
    ]
    results.append(kvkk)

    iso = RegulationResult(
        "iso-27002",
        "ISO/IEC 27002:2022 (5.17 kimlik doğrulama bilgileri)",
        "Kolay tahmin edilir olmama ilkesi (standart sayısal eşik vermez)",
    )
    iso.requirements = [
        Requirement(
            "Kolay tahmin edilebilir olmamalı (güç skoru en az 3/4)",
            strength_score >= 3,
            f"güç skoru: {strength_score}/4",
        ),
        _breach_req(breach_count),
    ]
    results.append(iso)

    return results
