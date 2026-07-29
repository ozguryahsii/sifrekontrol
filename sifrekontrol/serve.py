"""Lokal web arayüzü.

Gizlilik tasarımı:
  - Sunucu yalnızca 127.0.0.1'e bağlanır; dış ağdan erişilemez.
  - Şifre tarayıcıdan POST gövdesiyle gelir (URL'ye asla düşmez), bellekte
    analiz edilir ve atılır; diske yazılmaz, loglanmaz.
  - Erişim günlüğünde yalnızca yol (path) görünür, gövde asla yazılmaz.
  - Yanıtlara Cache-Control: no-store konur; tarayıcı da saklamaz.
"""

from __future__ import annotations

import hashlib
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional, Tuple

from .regulations import evaluate
from .report import build_payload
from .store import Store
from .strength import analyze

MAX_BODY = 64 * 1024


def run_check_payload(password: str, data_dir: Path) -> dict:
    """Analiz hattını çalıştırır; şifre bu fonksiyonun dışına sızmaz."""
    store = Store(data_dir)
    digest = hashlib.sha1(password.encode("utf-8")).digest()
    try:
        breach_count: Optional[int] = store.lookup(digest)
    except FileNotFoundError:
        breach_count = None
    strength = analyze(password)
    regulations = evaluate(password, breach_count, strength.score)
    return build_payload(len(password), strength, breach_count, regulations)


PAGE = """<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>sifrekontrol — lokal şifre denetleyicisi</title>
<style>
  :root { color-scheme: light dark; }
  body { font-family: system-ui, sans-serif; max-width: 760px; margin: 2rem auto;
         padding: 0 1rem; line-height: 1.5; }
  h1 { font-size: 1.4rem; }
  .privacy { font-size: .85rem; opacity: .75; }
  form { display: flex; gap: .5rem; margin: 1rem 0; }
  input[type=password] { flex: 1; font-size: 1rem; padding: .55rem .7rem;
         border: 1px solid #8888; border-radius: 8px; }
  button { font-size: 1rem; padding: .55rem 1.1rem; border: 0; border-radius: 8px;
         background: #2563eb; color: #fff; cursor: pointer; }
  button:disabled { opacity: .5; }
  .card { border: 1px solid #8884; border-radius: 10px; padding: .9rem 1.1rem;
         margin: .8rem 0; }
  .ok { color: #16a34a; } .bad { color: #dc2626; } .unk { color: #ca8a04; }
  .score { font-weight: 700; }
  ul { margin: .4rem 0 .2rem; padding-left: 1.3rem; }
  li { margin: .15rem 0; }
  .scope { font-size: .82rem; opacity: .7; }
  .verdict { font-weight: 700; }
  .hidden { display: none; }
</style>
</head>
<body>
<p style="border:1px solid #8886;border-radius:10px;padding:.6rem .9rem;
   font-size:.85rem;background:rgba(120,120,255,.08)">
ℹ️ Bu sayfa, analiz motorunun <b>yedek basit arayüzüdür</b>. Modern dashboard
için <a href="http://localhost:3002">http://localhost:3002</a> adresini açın
(frontend dizininde <code>npm run dev</code> çalışıyor olmalı).
</p>
<h1>🔐 sifrekontrol</h1>
<p class="privacy">Tamamen lokal çalışır: şifreniz yalnızca bu makinedeki analize gider
(127.0.0.1), hiçbir yerde saklanmaz, loglanmaz, internete gönderilmez.</p>
<form id="f" autocomplete="off">
  <input id="pw" type="password" placeholder="Kontrol edilecek şifre"
         autocomplete="new-password" required>
  <button id="btn" type="submit">Kontrol et</button>
</form>
<div id="out" class="hidden"></div>
<script>
const mark = p => p === true ? '<span class="ok">✔</span>'
             : p === false ? '<span class="bad">✘</span>'
             : '<span class="unk">?</span>';
const esc = s => String(s).replace(/[&<>"]/g, c =>
  ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const labels = ['çok zayıf','zayıf','orta','güçlü','çok güçlü'];

document.getElementById('f').addEventListener('submit', async e => {
  e.preventDefault();
  const btn = document.getElementById('btn'), out = document.getElementById('out');
  btn.disabled = true;
  try {
    const resp = await fetch('/api/check', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({password: document.getElementById('pw').value})
    });
    if (!resp.ok) throw new Error('HTTP ' + resp.status);
    const d = await resp.json();
    let html = '<div class="card"><b>Güç analizi</b><br>' +
      'Skor: <span class="score">' + d.strength.score + '/4 (' +
      labels[d.strength.score] + ')</span><br>' +
      'Kırılma süresi (hızlı offline saldırı): ' + esc(d.strength.crack_time_offline_fast) + '<br>' +
      'Kırılma süresi (hız sınırlı online): ' + esc(d.strength.crack_time_online);
    for (const w of d.strength.warnings) html += '<br>⚠️ ' + esc(w);
    for (const s of d.strength.suggestions) html += '<br>💡 ' + esc(s);
    html += '</div>';

    html += '<div class="card"><b>Sızıntı kontrolü (HIBP offline)</b><br>';
    if (d.breach_count === null) {
      html += '<span class="unk">?</span> Veri seti indirilmemiş — ' +
              '<code>sifrekontrol download</code> ile kurabilirsiniz.';
    } else if (d.breach_count > 0) {
      html += mark(false) + ' Bu şifre bilinen sızıntılarda <b>' +
              d.breach_count.toLocaleString('tr-TR') + ' kez</b> görüldü. ' +
              'Veri seti hangi sitede sızdığını içermez (anonimleştirilmiştir); ' +
              'yalnızca toplam görülme sayısı bilinir. <b>Bu şifreyi kullanmayın.</b>';
    } else {
      html += mark(true) + ' Bilinen sızıntı listelerinde bulunamadı.';
    }
    html += '</div>';

    html += '<div class="card"><b>Regülasyon / standart uyumluluğu</b>';
    for (const r of d.regulations) {
      html += '<div style="margin-top:.6rem">' + mark(r.passed) + ' <b>' +
              esc(r.name) + '</b><div class="scope">' + esc(r.scope) + '</div><ul>';
      for (const q of r.requirements) {
        html += '<li>' + mark(q.passed) + ' ' + esc(q.description) +
                (q.detail ? ' — <i>' + esc(q.detail) + '</i>' : '') + '</li>';
      }
      html += '</ul></div>';
    }
    html += '</div>';

    let verdict;
    if (d.breach_count > 0) verdict = ['bad', 'Şifre sızmış — derhal değiştirin.'];
    else if (d.strength.score < 3) verdict = ['bad', 'Şifre yeterince güçlü değil.'];
    else verdict = ['ok', 'Şifre güçlü görünüyor.'];
    html += '<p class="verdict ' + verdict[0] + '">Sonuç: ' + verdict[1] + '</p>';

    out.innerHTML = html;
    out.classList.remove('hidden');
  } catch (err) {
    out.innerHTML = '<div class="card bad">Hata: ' + esc(err.message) + '</div>';
    out.classList.remove('hidden');
  } finally {
    btn.disabled = false;
  }
});
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    data_dir: Path  # serve() tarafından atanır

    def log_message(self, fmt, *args):  # gövde asla loglanmaz; yol yeterli
        pass

    def _send(self, code: int, content_type: str, body: bytes) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, code: int, payload: dict) -> None:
        self._send(code, "application/json; charset=utf-8",
                   json.dumps(payload, ensure_ascii=False).encode("utf-8"))

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, "text/html; charset=utf-8", PAGE.encode("utf-8"))
        elif self.path == "/api/status":
            self._send_json(200, Store(self.data_dir).status())
        else:
            self._send_json(404, {"error": "bulunamadi"})

    def do_POST(self):
        if self.path != "/api/check":
            self._send_json(404, {"error": "bulunamadi"})
            return
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0 or length > MAX_BODY:
            self._send_json(400, {"error": "gecersiz istek govdesi"})
            return
        try:
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            password = body.get("password") or ""
        except (ValueError, UnicodeDecodeError):
            self._send_json(400, {"error": "gecersiz JSON"})
            return
        if not password:
            self._send_json(400, {"error": "sifre bos olamaz"})
            return
        self._send_json(200, run_check_payload(password, self.data_dir))


def serve(data_dir: Path, port: int = 3003, host: str = "127.0.0.1") -> Tuple[str, int]:
    """Web arayüzünü başlatır (bloklar). Yalnızca loopback'e bağlanır."""
    handler = type("BoundHandler", (Handler,), {"data_dir": Path(data_dir)})
    httpd = ThreadingHTTPServer((host, port), handler)
    print(f"sifrekontrol web arayüzü: http://{host}:{port}  (Ctrl+C ile durdurun)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nDurduruldu.")
    finally:
        httpd.server_close()
    return host, port
