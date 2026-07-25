import unittest

from sifrekontrol.regulations import evaluate


def by_id(results, reg_id):
    return next(r for r in results if r.reg_id == reg_id)


class RegulationTests(unittest.TestCase):
    def test_strong_long_password_passes_all(self):
        results = evaluate("Kx9#mQ2$vLp8@wZr4!", breach_count=0, strength_score=4)
        for r in results:
            self.assertTrue(r.passed, f"{r.reg_id} gecmeliydi")

    def test_breached_password_fails_breach_dependent(self):
        results = evaluate("Kx9#mQ2$vLp8@wZr4!", breach_count=1000, strength_score=4)
        for reg_id in ("nist-800-63b", "owasp-asvs-4", "cis-password-guide", "iso-27002"):
            self.assertFalse(by_id(results, reg_id).passed, reg_id)
        # PCI 8.3.6 yalnızca uzunluk+bileşim tanımlar; sızıntıdan etkilenmez
        self.assertTrue(by_id(results, "pci-dss-4").passed)

    def test_short_password_fails_length_rules(self):
        results = evaluate("Ab1!xyz", breach_count=0, strength_score=2)  # 7 karakter
        self.assertFalse(by_id(results, "nist-800-63b").passed)
        self.assertFalse(by_id(results, "pci-dss-4").passed)
        self.assertFalse(by_id(results, "owasp-asvs-4").passed)
        self.assertFalse(by_id(results, "cis-password-guide").passed)
        self.assertFalse(by_id(results, "kvkk-rehber").passed)

    def test_no_dataset_yields_indeterminate(self):
        results = evaluate("Kx9#mQ2$vLp8@wZr4!", breach_count=None, strength_score=4)
        nist = by_id(results, "nist-800-63b")
        self.assertIsNone(nist.passed)  # sızıntı kontrolü yapılamadı → belirsiz
        self.assertTrue(by_id(results, "pci-dss-4").passed)  # sızıntıdan bağımsız

    def test_pci_requires_letters_and_digits(self):
        results = evaluate("abcdefghijkl", breach_count=0, strength_score=3)  # rakam yok
        self.assertFalse(by_id(results, "pci-dss-4").passed)

    def test_kvkk_requires_mixed_classes(self):
        results = evaluate("alllowercase1!", breach_count=0, strength_score=3)
        self.assertFalse(by_id(results, "kvkk-rehber").passed)  # büyük harf yok


if __name__ == "__main__":
    unittest.main()
