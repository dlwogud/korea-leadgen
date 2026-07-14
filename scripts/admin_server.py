"""Internal admin server — serves the platform AND runs collection from its
Settings tab.

INTERNAL USE ONLY. Binds to 127.0.0.1 (localhost) so it is NOT exposed to the
network or the public. API keys entered in the platform's ⚙️ Settings tab are
written to .env (gitignored) on this machine. For team-wide access, deploy
behind an internal network + auth. No external dependencies (stdlib only).

Run:
    python3 scripts/admin_server.py
    # then open http://localhost:8765  →  the platform, with a working Settings tab
"""
from __future__ import annotations

import csv
import json
import subprocess
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV = ROOT / ".env"
DATA = ROOT / "data"
PORT = 8765

MANAGED_KEYS = ["ANTHROPIC_API_KEY", "SARAMIN_API_KEY", "WANTED_API_KEY",
                "JOBKOREA_API_KEY", "DART_API_KEY"]
# Sources with a working collector today. (Wanted currently uses the scraper;
# when an official Wanted API is obtained, add a source_wanted_api.py and point
# "wanted" here at it.)
SOURCES = {
    "wanted": ["source_wanted.py", "--pages", "5"],
    "saramin": ["source_saramin.py", "--pages", "3"],
}
# Sources without a collector yet — plug in when the company gets API access.
FUTURE = {
    "jobkorea": ("JobKorea has no public API. When the company obtains API or "
                 "partnership access, add scripts/source_jobkorea.py and register "
                 "it in SOURCES — then this button collects from JobKorea."),
}
# Keep this in lockstep with scripts/daily_wanted.sh — same steps, same order.
# export_delivery MUST run before build_platform (the platform embeds the CSV).
PIPELINE_AFTER = [
    ["enrich.py"], ["enrich_dart.py"], ["add_english.py"],
    ["score_leads.py"], ["qualify_leads.py", "--top", "10"],
    ["generate_messages.py", "--top", "10"],
    ["export_delivery.py"], ["build_platform.py"], ["view_delivery.py"],
]


def read_env() -> dict:
    d = {}
    if ENV.exists():
        for line in ENV.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                d[k.strip()] = v.strip()
    return d


def write_env(updates: dict) -> None:
    d = read_env()
    for k, v in updates.items():
        if v.strip():                       # only overwrite when a value is given
            d[k] = v.strip()
    ENV.write_text("\n".join(f"{k}={v}" for k, v in d.items()) + "\n", encoding="utf-8")


WORKSHEET = DATA / "contacts_worksheet.csv"
WS_FIELDS = ["company_name", "full_name", "title", "email", "phone",
             "linkedin_url", "is_decision_maker", "status", "notes"]


def _run(script: str, *args):
    return subprocess.run([sys.executable, str(ROOT / "scripts" / script), *args],
                          capture_output=True, text=True)


def save_contact(company: str, name: str, title: str, email: str, phone: str) -> str:
    """Upsert a contact into contacts_worksheet.csv, rescore, rebuild. Returns new fit."""
    rows = {}
    if WORKSHEET.exists():
        with WORKSHEET.open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                rows[r.get("company_name", "")] = r
    r = rows.get(company, {"company_name": company})
    r.update({"full_name": name, "title": title, "email": email, "phone": phone})
    if name or email:                      # treat an entered contact as the decision-maker
        r["is_decision_maker"] = "y"
    rows[company] = r
    with WORKSHEET.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=WS_FIELDS)
        w.writeheader()
        for rr in rows.values():
            w.writerow({k: rr.get(k, "") for k in WS_FIELDS})
    # recompute score (reachability) + refresh the operational outputs
    for s in ("rescore_with_contacts.py", "export_delivery.py", "build_platform.py"):
        _run(s)
    fl = DATA / "final_leads.csv"
    if fl.exists():
        with fl.open(encoding="utf-8") as f:
            for r2 in csv.DictReader(f):
                if r2.get("company_name") == company:
                    return r2.get("fit_score", "")
    return ""


def run_pipeline(source: str) -> tuple[bool, str]:
    src = SOURCES.get(source)
    if not src:
        return False, FUTURE.get(source, f"Unknown source: {source}")
    out, ok = [], True
    for s in [src] + PIPELINE_AFTER:
        r = subprocess.run([sys.executable, str(ROOT / "scripts" / s[0]), *s[1:]],
                           capture_output=True, text=True)
        out.append(f"$ {s[0]} {' '.join(s[1:])}\n{(r.stdout or '')}{(r.stderr or '')}".strip())
        if r.returncode != 0:
            out.append(f"⚠️ step failed ({s[0]}) — stopping.")
            ok = False
            break
    return ok, "\n\n".join(out)


class Handler(BaseHTTPRequestHandler):
    def _bytes(self, body: bytes, ctype="text/html; charset=utf-8", code=200):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, code=200):
        self._bytes(json.dumps(obj, ensure_ascii=False).encode("utf-8"),
                    ctype="application/json; charset=utf-8", code=code)

    def do_GET(self):
        # serve the platform (which contains the Settings tab) at / and /platform
        path = urllib.parse.urlparse(self.path).path
        if path in ("/", "/index.html", "/platform"):
            f = DATA / "platform.html"
            if f.exists():
                self._bytes(f.read_bytes())
            else:
                self._bytes(b"platform.html not built yet - collect once from Settings.", code=404)
        else:
            self._bytes(b"not found", code=404)

    def _form(self) -> dict:
        n = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(n).decode("utf-8")
        return {k: v[0] for k, v in urllib.parse.parse_qs(raw, keep_blank_values=True).items()}

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        form = self._form()
        if path == "/save":
            write_env({k: form.get(k, "") for k in MANAGED_KEYS})
            self._json({"ok": True, "msg": "✅ Keys saved to .env"})
        elif path == "/run":
            ok, log = run_pipeline(form.get("source", "wanted"))
            self._json({"ok": ok, "log": log})
        elif path == "/save_contact":
            fit = save_contact(form.get("company", ""), form.get("name", ""),
                               form.get("title", ""), form.get("email", ""), form.get("phone", ""))
            self._json({"ok": True, "fit_score": fit})
        else:
            self._json({"ok": False, "msg": "not found"}, code=404)

    def log_message(self, *a):
        pass


def main() -> None:
    print(f"🔐 Admin server on http://localhost:{PORT}  (localhost only — internal)")
    print("   Open it, go to the ⚙️ Settings tab, enter keys, and click Collect. Ctrl+C to stop.")
    HTTPServer(("127.0.0.1", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
