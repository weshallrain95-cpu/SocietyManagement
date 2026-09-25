"""Live mirror of the Android emulator in a browser tab (for the Claude app's browser pane, beside the chat).

    python3 tools/android-mirror/mirror.py        # then open http://localhost:8090

Click = tap, drag = swipe, mouse wheel = scroll, typing goes to the phone. Buttons: Back, Home, Apps.
Uses adb from ~/Library/Android/sdk/platform-tools. Laptop only; nothing leaves the Mac.
"""

import os
import re
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

ADB = os.path.expanduser("~/Library/Android/sdk/platform-tools/adb")
PORT = int(os.environ.get("MIRROR_PORT", "8090"))

_frame = {"png": b"", "at": 0.0}
_lock = threading.Lock()


def adb(*args, capture=False):
    return subprocess.run([ADB, *args], capture_output=capture, timeout=15).stdout if capture else subprocess.run([ADB, *args], timeout=15)


def grabber():
    while True:
        try:
            png = adb("exec-out", "screencap", "-p", capture=True)
            if png.startswith(b"\x89PNG"):
                with _lock:
                    _frame["png"], _frame["at"] = png, time.time()
        except Exception:  # noqa: BLE001 - emulator restarting; keep trying
            time.sleep(1)


def shell_text(t: str) -> str:
    # `adb shell input text` needs spaces as %s and shell characters escaped.
    t = t.replace("%", "\\%").replace(" ", "%s")
    return re.sub(r"([\\\"'`$&|;<>()\[\]{}*?!~#])", r"\\\1", t) if t else t


PAGE = """<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Android phone</title><style>
body{margin:0;background:#1b1b1b;font-family:-apple-system,sans-serif;display:flex;flex-direction:column;align-items:center;height:100vh}
#bar{display:flex;gap:6px;padding:6px}button{background:#333;color:#eee;border:0;border-radius:8px;padding:6px 12px;font-size:13px;cursor:pointer}
#wrap{flex:1;min-height:0;display:flex;justify-content:center}img{height:100%;max-width:100%;object-fit:contain;cursor:pointer;border-radius:18px;user-select:none;-webkit-user-drag:none}
#hint{color:#888;font-size:11px;padding:4px}</style></head><body>
<div id="bar"><button onclick="key(4)">◀ Back</button><button onclick="key(3)">● Home</button><button onclick="key(187)">■ Apps</button></div>
<div id="wrap"><img id="s" draggable="false"></div><div id="hint">Click to tap · drag to swipe · scroll wheel to scroll · type to enter text</div>
<script>
const s=document.getElementById('s');let down=null;
function next(){const i=new Image();i.onload=()=>{s.src=i.src;setTimeout(next,120)};i.onerror=()=>setTimeout(next,800);i.src='/frame.png?t='+Date.now();}
next();
function pt(e){const r=s.getBoundingClientRect();return [Math.round((e.clientX-r.left)*s.naturalWidth/r.width),Math.round((e.clientY-r.top)*s.naturalHeight/r.height)];}
s.addEventListener('mousedown',e=>{down=pt(e);e.preventDefault();});
s.addEventListener('mouseup',e=>{if(!down)return;const u=pt(e);const d=Math.hypot(u[0]-down[0],u[1]-down[1]);
 fetch(d<20?`/tap?x=${down[0]}&y=${down[1]}`:`/swipe?x1=${down[0]}&y1=${down[1]}&x2=${u[0]}&y2=${u[1]}`);down=null;});
let wheel=0,wt=null;s.addEventListener('wheel',e=>{e.preventDefault();wheel+=e.deltaY;clearTimeout(wt);wt=setTimeout(()=>{const p=pt(e);const dy=Math.max(-900,Math.min(900,-wheel*2));
 fetch(`/swipe?x1=${p[0]}&y1=${p[1]}&x2=${p[0]}&y2=${p[1]+Math.round(dy)}&ms=250`);wheel=0;},120);},{passive:false});
function key(k){fetch('/key?k='+k);}
let buf='',bt=null;function flush(){if(buf){fetch('/text?t='+encodeURIComponent(buf));buf='';}}
document.addEventListener('keydown',e=>{if(e.metaKey||e.ctrlKey)return;
 if(e.key==='Backspace'){flush();key(67);e.preventDefault();}else if(e.key==='Enter'){flush();key(66);}else if(e.key==='Escape'){key(4);}
 else if(e.key.length===1){buf+=e.key;clearTimeout(bt);bt=setTimeout(flush,150);e.preventDefault();}});
</script></body></html>"""


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _ok(self, body=b"ok", ctype="text/plain"):
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        n = lambda k: str(int(float(q[k])))  # noqa: E731
        if u.path == "/":
            return self._ok(PAGE.encode(), "text/html; charset=utf-8")
        if u.path == "/frame.png":
            with _lock:
                png = _frame["png"]
            return self._ok(png, "image/png") if png else self.send_error(503)
        if u.path == "/tap":
            adb("shell", "input", "tap", n("x"), n("y"))
        elif u.path == "/swipe":
            adb("shell", "input", "swipe", n("x1"), n("y1"), n("x2"), n("y2"), q.get("ms", "300"))
        elif u.path == "/key":
            adb("shell", "input", "keyevent", n("k"))
        elif u.path == "/text":
            adb("shell", "input", "text", shell_text(q.get("t", "")))
        else:
            return self.send_error(404)
        self._ok()


if __name__ == "__main__":
    threading.Thread(target=grabber, daemon=True).start()
    print(f"Android mirror on http://localhost:{PORT}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
