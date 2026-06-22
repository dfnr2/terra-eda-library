#!/usr/bin/env python3
"""Fetch ADI / Linear Technology datasheets that Akamai blocks for curl.

analog.com sits behind Akamai Bot Manager, which rejects plain curl requests
(the TLS handshake succeeds, then the HTTP/2 stream is reset / a 403 "Access
Denied" page is returned) because there is no JS-generated `_abck` bot cookie.

The fix: drive a real Chrome through the DevTools Protocol, land on the
analog.com origin so Akamai's sensor JS runs and validates the bot cookie,
then `fetch()` each PDF from inside that origin. The request then carries
Chrome's real TLS fingerprint and the validated cookie, so Akamai lets it
through.

Usage:  python3 fetch_adi.py <output-dir> [PART=URL ...]
With no PART overrides it downloads the built-in ADI/LT op-amp list.
Exits 0 even if some parts fail (they are reported); exits non-zero only on
setup failure (no Chrome binary, missing `websockets`).
"""
import asyncio
import base64
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request

HOME = "https://www.analog.com/en/index.html"
MIN_BYTES = 10000  # anything smaller is an error page, not a datasheet

# Built-in ADI / Linear Technology op-amp datasheet list (NAME, URL).
PARTS = [
    ("LT1028",   "https://www.analog.com/media/en/technical-documentation/data-sheets/lt1028.pdf"),
    ("LT1115",   "https://www.analog.com/media/en/technical-documentation/data-sheets/lt1115.pdf"),
    ("LT1818",   "https://www.analog.com/media/en/technical-documentation/data-sheets/lt1818.pdf"),
    ("LT1812",   "https://www.analog.com/media/en/technical-documentation/data-sheets/lt1812.pdf"),
    ("LT1167",   "https://www.analog.com/media/en/technical-documentation/data-sheets/lt1167.pdf"),
    ("LT6018",   "https://www.analog.com/media/en/technical-documentation/data-sheets/lt6018.pdf"),
    ("LT6016",   "https://www.analog.com/media/en/technical-documentation/data-sheets/lt6016.pdf"),
    ("LT3045",   "https://www.analog.com/media/en/technical-documentation/data-sheets/lt3045.pdf"),
    ("LTC2057",  "https://www.analog.com/media/en/technical-documentation/data-sheets/ltc2057.pdf"),
    ("LTC2050",  "https://www.analog.com/media/en/technical-documentation/data-sheets/ltc2050.pdf"),
    ("LTC6362",  "https://www.analog.com/media/en/technical-documentation/data-sheets/ltc6362.pdf"),
    ("LTC6363",  "https://www.analog.com/media/en/technical-documentation/data-sheets/ltc6363.pdf"),
    ("LTC6655",  "https://www.analog.com/media/en/technical-documentation/data-sheets/ltc6655.pdf"),
    ("LT1021",   "https://www.analog.com/media/en/technical-documentation/data-sheets/lt1021.pdf"),
    ("LT1027",   "https://www.analog.com/media/en/technical-documentation/data-sheets/lt1027.pdf"),
    ("AD797",    "https://www.analog.com/media/en/technical-documentation/data-sheets/ad797.pdf"),
    ("AD844",    "https://www.analog.com/media/en/technical-documentation/data-sheets/ad844.pdf"),
    ("ADA4528",  "https://www.analog.com/media/en/technical-documentation/data-sheets/ada4528-1.pdf"),
    ("ADA4898",  "https://www.analog.com/media/en/technical-documentation/data-sheets/ada4898-1.pdf"),
    ("ADA4898_2","https://www.analog.com/media/en/technical-documentation/data-sheets/ada4898-2.pdf"),
]


def find_chrome():
    for b in ("google-chrome", "google-chrome-stable", "chromium",
              "chromium-browser", "chrome"):
        p = shutil.which(b)
        if p:
            return p
    sys.exit("error: no chrome/chromium binary found on PATH")


def chrome_ws(port, tries=60):
    """Poll the DevTools /json endpoint until a page target is ready."""
    for _ in range(tries):
        try:
            data = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json"))
            for t in data:
                if t.get("type") == "page" and t.get("webSocketDebuggerUrl"):
                    return t["webSocketDebuggerUrl"]
        except Exception:
            pass
        time.sleep(0.25)
    raise RuntimeError("timed out waiting for Chrome DevTools target")


# JS run inside the analog.com page: fetch a URL and return it base64-encoded.
FETCH_JS = """(async () => {
  try {
    const r = await fetch(%s, {credentials: 'include'});
    if (!r.ok) return JSON.stringify({ok: false, status: r.status});
    const b = new Uint8Array(await r.arrayBuffer());
    let s = ''; const C = 0x8000;
    for (let i = 0; i < b.length; i += C) {
      s += String.fromCharCode.apply(null, b.subarray(i, i + C));
    }
    return JSON.stringify({ok: true, status: r.status, len: b.length, b64: btoa(s)});
  } catch (e) { return JSON.stringify({ok: false, err: String(e)}); }
})()"""


class CDP:
    def __init__(self, ws):
        self.ws = ws
        self.id = 0

    async def cmd(self, method, params=None):
        self.id += 1
        this = self.id
        await self.ws.send(json.dumps({"id": this, "method": method, "params": params or {}}))
        while True:
            msg = json.loads(await self.ws.recv())
            if msg.get("id") == this:
                if "error" in msg:
                    raise RuntimeError(f"{method}: {msg['error']}")
                return msg.get("result", {})

    async def evaluate(self, expr):
        res = await self.cmd("Runtime.evaluate",
                             {"expression": expr, "awaitPromise": True,
                              "returnByValue": True})
        return res.get("result", {}).get("value")


async def wait_for_bot_cookie(cdp, timeout=30):
    """Wait until Akamai validates the _abck cookie (value contains '~0~')."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        ck = await cdp.cmd("Network.getCookies", {"urls": [HOME]})
        for c in ck.get("cookies", []):
            if c["name"] == "_abck" and "~0~" in c["value"]:
                return True
        await asyncio.sleep(1)
    return False  # proceed anyway; per-part retries cover the slow case


async def run(parts, outdir):
    try:
        import websockets
    except ImportError:
        sys.exit("error: the 'websockets' package is required "
                 "(pip install websockets)")

    os.makedirs(outdir, exist_ok=True)
    todo = []
    for name, url in parts:
        out = os.path.join(outdir, f"{name}.pdf")
        if os.path.isfile(out) and os.path.getsize(out) > MIN_BYTES:
            print(f"  [skip] {name} (already exists)")
        else:
            todo.append((name, url, out))
    if not todo:
        return 0

    chrome = find_chrome()
    port = 9333
    prof = "/tmp/chrome-fetch-adi"
    shutil.rmtree(prof, ignore_errors=True)
    proc = subprocess.Popen(
        [chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
         "--disable-blink-features=AutomationControlled",
         "--window-size=1920,1080", "--lang=en-US",
         f"--remote-debugging-port={port}", f"--user-data-dir={prof}",
         "--no-first-run", "--no-default-browser-check", "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    ok = fail = 0
    try:
        ws_url = chrome_ws(port)
        async with websockets.connect(ws_url, max_size=None) as ws:
            cdp = CDP(ws)
            await cdp.cmd("Page.enable")
            await cdp.cmd("Runtime.enable")
            await cdp.cmd("Network.enable")
            await cdp.cmd("Page.navigate", {"url": HOME})
            await wait_for_bot_cookie(cdp)

            for name, url, out in todo:
                print(f"  {name:<20} ", end="", flush=True)
                obj = None
                for attempt in range(3):
                    val = await cdp.evaluate(FETCH_JS % json.dumps(url))
                    obj = json.loads(val) if val else {"ok": False, "err": "no result"}
                    if obj.get("ok") and obj.get("len", 0) > MIN_BYTES:
                        break
                    # likely an unvalidated cookie — reload origin and retry
                    await cdp.cmd("Page.navigate", {"url": HOME})
                    await wait_for_bot_cookie(cdp, timeout=15)

                if obj.get("ok") and obj.get("len", 0) > MIN_BYTES:
                    with open(out, "wb") as f:
                        f.write(base64.b64decode(obj["b64"]))
                    print(f"OK  ({obj['len']} bytes)")
                    ok += 1
                else:
                    detail = obj.get("status") or obj.get("err") or "unknown"
                    print(f"FAIL  ({detail})")
                    fail += 1
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except Exception:
            proc.kill()

    print(f"\n  {ok} ok, {fail} failed")
    return 0


def parse_overrides(argv):
    parts = []
    for a in argv:
        if "=" in a:
            name, url = a.split("=", 1)
            parts.append((name, url))
    return parts or PARTS


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: fetch_adi.py <output-dir> [PART=URL ...]")
    outdir = sys.argv[1]
    parts = parse_overrides(sys.argv[2:])
    return asyncio.run(run(parts, outdir))


if __name__ == "__main__":
    sys.exit(main())
