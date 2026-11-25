#!/usr/bin/env python3
"""Local release archive portal server (portable, zero hardcoded workspace paths)."""
import hashlib
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ARCHIVE = Path(
    os.environ.get(
        "SCY_ARCHIVE_PATH",
        str(PROJECT_ROOT.parent / "scy-shell-v1.0.0.zip"),
    )
)
ARCHIVE = DEFAULT_ARCHIVE if DEFAULT_ARCHIVE.exists() else (PROJECT_ROOT / "scy-shell-v1.0.0.zip")
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get("PORT", "8080"))


def compute_sha256(path: Path) -> str:
    if not path.exists():
        return "ARCHIVE_NOT_BUILT_YET"
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


SHA256 = compute_sha256(ARCHIVE)
SIZE_BYTES = ARCHIVE.stat().st_size if ARCHIVE.exists() else 0
SIZE_MB = f"{SIZE_BYTES / (1024 * 1024):.2f} MB"
FNAME = ARCHIVE.name

HTML = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Scy-Shell v1.0.0 — Definitive Release Download</title>
<style>
  :root {{ color-scheme: dark; }}
  body {{
    margin: 0; min-height: 100vh; display: grid; place-items: center;
    font-family: Inter, system-ui, -apple-system, sans-serif;
    background: radial-gradient(circle at 20% 10%, #2a1834 0%, #121016 55%, #0b0a0e 100%);
    color: #f4edf7;
  }}
  .card {{
    max-width: 720px; width: calc(100% - 48px); padding: 36px;
    border-radius: 28px; background: rgba(34, 28, 41, 0.86);
    border: 1px solid rgba(255, 177, 209, 0.24);
    box-shadow: 0 24px 64px rgba(0,0,0,0.55);
  }}
  .badge {{
    display: inline-block; padding: 6px 14px; border-radius: 999px;
    background: rgba(255, 177, 209, 0.16); color: #ffb1d1;
    font-size: 12px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase;
  }}
  h1 {{ margin: 16px 0 8px; font-size: 32px; letter-spacing: -0.02em; }}
  p {{ color: #d5c4d1; line-height: 1.6; margin: 0 0 22px; }}
  .meta {{
    background: rgba(16, 13, 20, 0.72); border-radius: 18px; padding: 16px 20px;
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 13px;
    margin-bottom: 26px; border: 1px solid rgba(255,255,255,0.08); word-break: break-all;
  }}
  .meta div {{ margin: 6px 0; }}
  .label {{ color: #a995a4; }}
  .btn {{
    display: inline-flex; align-items: center; gap: 10px;
    padding: 15px 28px; border-radius: 999px; text-decoration: none;
    background: #ffb1d1; color: #521433; font-weight: 700; font-size: 16px;
  }}
  .grid {{
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 26px;
  }}
  .stat {{
    background: rgba(255,255,255,0.04); border-radius: 16px; padding: 14px;
    border: 1px solid rgba(255,255,255,0.06);
  }}
  .stat b {{ display: block; font-size: 20px; color: #ffd9e6; }}
  .stat span {{ font-size: 12px; color: #baa6b5; }}
</style>
</head>
<body>
  <div class="card">
    <span class="badge">Definitive Release · CachyOS / Arch Hyprland</span>
    <h1>Scy-Shell v1.0.0</h1>
    <p>Unified Material 3 Expressive Wayland Shell combining <b>Lucid</b> (Quickshell QML) + <b>Mandara</b> (Rust GPUI) with reversible Phase 1 provenance, 1,875 lossless settings, 89 plugins, 20 Looks, and complete shortcut accounting (67 compositor + 17/22 DesktopIcons + 25 Mandara).</p>
    <div class="meta">
      <div><span class="label">File:</span> {FNAME}</div>
      <div><span class="label">Size:</span> {SIZE_MB} ({SIZE_BYTES:,} bytes)</div>
      <div><span class="label">SHA-256:</span> {SHA256}</div>
    </div>
    <a class="btn" href="/{quote(FNAME)}" download="{FNAME}">⬇ Download {FNAME} ({SIZE_MB})</a>
    <div class="grid">
      <div class="stat"><b>1,875</b><span>Unified Settings (643 + 1,232)</span></div>
      <div class="stat"><b>67 + 22</b><span>Compositor + DesktopIcons Keys</span></div>
      <div class="stat"><b>3,708</b><span>SHA-256 Provenance Files</span></div>
    </div>
  </div>
</body>
</html>
""".encode("utf-8")


class ReusableThreadingHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        pass

    def do_HEAD(self):
        self._serve(head_only=True)

    def do_GET(self):
        self._serve(head_only=False)

    def _serve(self, head_only: bool):
        path = self.path.split("?", 1)[0]
        if path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(HTML)))
            self.send_header("Connection", "close")
            self.end_headers()
            if not head_only:
                self.wfile.write(HTML)
            return

        if path == f"/{FNAME}" or path == "/download":
            if not ARCHIVE.exists():
                self.send_error(404, "Archive not found")
                return
            self.send_response(200)
            self.send_header("Content-Type", "application/zip")
            self.send_header("Content-Disposition", f'attachment; filename="{FNAME}"')
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("ETag", f'"{SHA256[:16]}"')
            self.send_header("Content-Length", str(SIZE_BYTES))
            self.send_header("Connection", "close")
            self.end_headers()
            if not head_only:
                with ARCHIVE.open("rb") as f:
                    while True:
                        buf = f.read(1 << 20)
                        if not buf:
                            break
                        try:
                            self.wfile.write(buf)
                        except (BrokenPipeError, ConnectionResetError):
                            break
            return

        if path == "/sha256":
            body = f"{SHA256}  {FNAME}\n".encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Connection", "close")
            self.end_headers()
            if not head_only:
                self.wfile.write(body)
            return

        self.send_response(404)
        self.send_header("Content-Length", "0")
        self.send_header("Connection", "close")
        self.end_headers()


if __name__ == "__main__":
    srv = ReusableThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Serving {ARCHIVE} ({SIZE_MB}) on http://0.0.0.0:{PORT}/", flush=True)
    srv.serve_forever()
