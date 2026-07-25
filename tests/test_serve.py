import hashlib
import json
import tempfile
import threading
import unittest
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

from sifrekontrol.serve import Handler
from sifrekontrol.store import Store


class ServeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        data_dir = Path(cls._tmp.name)
        store = Store(data_dir)
        leaked = hashlib.sha1(b"password123").digest()
        store.write_group(leaked.hex().upper()[:3], [(leaked, 999)])

        handler = type("H", (Handler,), {"data_dir": data_dir})
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), handler)  # boş port
        cls.port = cls.httpd.server_address[1]
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls._tmp.cleanup()

    def _post(self, path, payload):
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.port}{path}",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req) as resp:
                return resp.status, json.loads(resp.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())

    def test_index_page(self):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/") as resp:
            body = resp.read().decode()
            self.assertEqual(resp.status, 200)
            self.assertEqual(resp.headers["Cache-Control"], "no-store")
            self.assertIn("sifrekontrol", body)

    def test_check_leaked_password(self):
        status, d = self._post("/api/check", {"password": "password123"})
        self.assertEqual(status, 200)
        self.assertEqual(d["breach_count"], 999)
        self.assertEqual(d["length"], 11)
        self.assertTrue(any(r["id"] == "nist-800-63b" and r["passed"] is False
                            for r in d["regulations"]))
        # Yanıt şifrenin kendisini içermemeli
        self.assertNotIn("password123", json.dumps(d))

    def test_check_unknown_group_reports_missing_dataset(self):
        # Grubu hiç olmayan bir şifre: veri seti eksik → breach_count null
        status, d = self._post("/api/check", {"password": "TamamenFarkliBirSifre#42x"})
        self.assertEqual(status, 200)
        self.assertIsNone(d["breach_count"])

    def test_empty_password_rejected(self):
        status, d = self._post("/api/check", {"password": ""})
        self.assertEqual(status, 400)

    def test_status_endpoint(self):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/api/status") as resp:
            d = json.loads(resp.read())
            self.assertEqual(d["groups_present"], 1)


if __name__ == "__main__":
    unittest.main()
