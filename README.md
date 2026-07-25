# sifrekontrol

Tamamen **lokal** çalışan şifre güvenlik denetleyicisi. Girilen şifreyi:

- **Sızıntı veritabanına karşı kontrol eder** — Have I Been Pwned (HIBP)
  *Pwned Passwords* veri setinin (850M+ sızmış şifre hash'i) offline kopyası
  üzerinde, milisaniyeler içinde binary search ile.
- **Güç analizinden geçirir** — zxcvbn motoru ile skor, tahmini kırılma
  süreleri, uyarılar ve öneriler (Türkçe).
- **Regülasyon/standart uyumluluğunu raporlar** — NIST SP 800-63B,
  PCI DSS v4.0, OWASP ASVS 4.0, CIS Parola Rehberi, KVKK Kişisel Veri
  Güvenliği Rehberi, ISO/IEC 27002:2022.

Ve en önemlisi: **şifre asla saklanmaz, loglanmaz veya ağa gönderilmez.**

## Gizlilik garantileri

- Şifre yalnızca gizli etkileşimli girişle (`getpass`, ekranda görünmez) veya
  `--stdin` ile alınır; komut satırı argümanı olarak **kabul edilmez**
  (kabuk geçmişine düşmesin diye).
- SHA-1 hash'i yalnızca bellekte hesaplanır, lokal veri setinde aranır ve
  atılır. Sorgu sırasında **hiçbir ağ isteği yapılmaz**.
- Rapor şifreyi veya hash'ini içermez; yalnızca uzunluk gibi türetilmiş
  bilgiler gösterilir.
- Bilinen sınırlama: Python string'leri değişmez (immutable) olduğundan
  bellekteki kopyanın anında sıfırlanması garanti edilemez; referanslar en
  erken noktada bırakılır ve süreç sonlanınca bellek serbest kalır.

## Kurulum

```bash
pip install .        # depo kökünde; tek bağımlılık: zxcvbn
```

## Kullanım

```bash
# 1) Veri setini indir (bir kere; ~25-30 GB disk, ilk indirme saatler sürebilir.
#    Yarıda kesilirse aynı komut kaldığı yerden devam eder.)
sifrekontrol download

# 2) Şifre kontrol et (şifre gizli sorulur, ekranda görünmez)
sifrekontrol check

# JSON çıktı (başka araçlara beslemek için)
sifrekontrol check --json

# Veri seti durumu
sifrekontrol status

# Web arayüzü: http://127.0.0.1:3002 (yalnızca bu makineden erişilebilir)
sifrekontrol serve --port 3002

# 3) Veri setini güncelle (artımlı — aşağıya bakın)
sifrekontrol update
```

Veri dizini varsayılan olarak `~/.local/share/sifrekontrol`'dür;
`--data-dir` veya `SIFREKONTROL_DATA` ortam değişkeni ile değiştirilebilir.
`check` komutu sızmış şifre için `1`, temiz şifre için `0` çıkış kodu döndürür
(betiklerde kullanım için).

## Güncelleme nasıl çalışıyor? Günlük güncellenebilir mi?

**Evet, günlük güncellenebilir — ve tam veri yeniden indirilmez.**

HIBP artık tek parça sürümlü dump yayınlamıyor; veri **sürekli** güncelleniyor
(FBI ve NCA gibi kaynaklardan akan yeni sızıntılar dahil) ve resmi dağıtım
yöntemi, 1.048.576 küçük "aralık" dosyasını API'den indirmek
(`api.pwnedpasswords.com/range/00000` … `/FFFFF`). Her aralık dosyası bir
**ETag** ile sunulur. `sifrekontrol update` bunu şöyle kullanır:

1. İlk indirmede her aralığın ETag'i `etags.tsv` dosyasına kaydedilir.
2. Güncellemede her aralık `If-None-Match: <etag>` başlığıyla sorulur.
3. Değişmemiş aralıklar gövdesiz **304 Not Modified** döner (birkaç yüz bayt);
   yalnızca **değişen** aralıklar yeniden indirilir ve ilgili grup dosyası
   yerinde yeniden yazılır.

Yani bir güncelleme turu, 1M civarı hafif koşullu istekten ibarettir; indirilen
gerçek veri yalnızca o günden beri değişen aralıklar kadardır. 32 paralel
işçiyle bir tur tipik olarak 1 saatin altında biter. Pratikte **haftalık**
güncelleme çoğu kullanım için yeterlidir; isterseniz günlük de çalıştırın:

```cron
# crontab -e — her gece 03:15'te güncelle
15 3 * * * sifrekontrol update >> ~/.local/share/sifrekontrol/update.log 2>&1
```

Güncelleme yarıda kesilirse veri seti bozulmaz: grup dosyaları atomik yazılır
(tmp + rename) ve bir sonraki `update` kalan işi tamamlar.

## Neler söyleyemez? (dürüst sınırlamalar)

- **"Şifre hangi sitede sızdı?" bilgisi verilemez.** HIBP şifre veri seti
  bilerek anonimleştirilmiştir: bir şifrenin *hangi* ihlalden geldiği tutulmaz
  (aynı şifreyi milyonlarca kişi kullanır). Bilinebilen şey, şifrenin
  sızıntılarda **kaç kez** görüldüğüdür. Site bazlı ihlal bilgisi ancak
  e-posta adresi sorgusuyla mümkündür ve o çevrimiçi bir servistir — bu
  uygulamanın "tamamen lokal" kapsamının dışında tutulmuştur.
- Regülasyon kontrolleri, tek bir şifreye uygulanabilir maddelerle sınırlıdır.
  Standartların hesap kilitleme, MFA, saklama (hash'leme) gibi politika
  maddeleri şifrenin kendisinden değerlendirilemez.

## Mimari

```
sifrekontrol/
  store.py        # 4096 grup dosyası (ilk 3 hex), 24 baytlık sabit kayıtlar,
                  # mmap + binary search sorgu, ETag manifesti
  downloader.py   # paralel indirme, ETag'li artımlı güncelleme, atomik yazım
  strength.py     # zxcvbn (yoksa entropi tabanlı yedek) + Türkçe çeviriler
  regulations.py  # standart bazlı kural motoru
  report.py       # terminal / JSON rapor (şifre içermez)
  serve.py        # lokal web arayüzü (yalnızca 127.0.0.1, no-store, log'suz)
  cli.py          # check / download / update / serve / status komutları
tests/            # python3 -m unittest discover -s tests
```

Depolama düzeni: her kayıt 20 bayt SHA-1 + 4 bayt görülme sayısı. Hash'ler
ilk 3 hex karakterine göre 4096 dosyaya bölünür (~5-7 MB/dosya); sorgu tek
dosya açıp binary search yapar, tam veri setinde bile milisaniye sürer.
