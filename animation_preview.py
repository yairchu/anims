"""Local playback/scrubbing UI and asset server shared with the exporter."""
import argparse
import json
import mimetypes
import threading
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from animation_scene import ASSET_FILES, render_scene
from animation_timeline import DEFAULT_TIMELINE, load_timeline, state_at

ROOT = Path(__file__).parent
ASSETS = {key: "/assets/" + value for key, value in ASSET_FILES.items()}

HTML = '''<!doctype html><meta charset="utf-8"><title>Political meters · animation preview</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#e9e9ed;font:15px system-ui;color:#24242a}
#stage{line-height:0;margin:auto;max-width:1200px;background:white}#stage svg{width:100%;height:auto}
nav{max-width:1200px;margin:16px auto;padding:0 16px}button,select{font:inherit;padding:8px 12px;margin-right:8px}
#seek{width:100%;margin:16px 0}#chapters{display:flex;gap:6px;flex-wrap:wrap}#chapters button{font-size:12px}
</style><div id="stage"></div><nav><button id="play">Play</button>
<select id="speed"><option value="0.5">0.5×</option><option selected value="1">1×</option><option value="2">2×</option></select>
<output id="time"></output><input id="seek" aria-label="Timeline time" type="range" min="0" step="0.01">
<div id="chapters"></div><p>Edit timeline.json, then reload to pick up timing changes. Export with export_video.py.</p></nav>
<script>
let config, time=0, playing=false, last=0, busy=false, revision=0;
const stage=document.querySelector('#stage'), seek=document.querySelector('#seek'), button=document.querySelector('#play');
async function draw(t){
  const mine=++revision;
  const response=await fetch('/frame?t='+t);
  const svg=await response.text();
  if(mine!==revision)return;
  stage.innerHTML=svg;seek.value=t;
  document.querySelector('#time').textContent=t.toFixed(2)+' / '+config.duration.toFixed(2)+' s';
}
function pause(){playing=false;button.textContent='Play'}
button.onclick=()=>{if(playing){pause()}else{if(time>=config.duration)time=0;playing=true;last=performance.now();button.textContent='Pause'}};
seek.oninput=()=>{pause();time=Number(seek.value);draw(time)};
async function tick(now){
  if(playing&&!busy){busy=true;time=Math.min(config.duration,time+(now-last)/1000*Number(document.querySelector('#speed').value));last=now;
    try{await draw(time)}finally{busy=false}if(time>=config.duration)pause();}
  requestAnimationFrame(tick);
}
(async()=>{config=await(await fetch('/config')).json();seek.max=config.duration;
  for(const chapter of config.chapters){const b=document.createElement('button');b.textContent=chapter.label;
    b.onclick=()=>{pause();time=chapter.time;draw(time)};document.querySelector('#chapters').append(b)}
  await draw(0);requestAnimationFrame(tick)})();
</script>'''


def make_handler(timeline_path, *, transparent=False, width=None, height=None):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path == "/":
                body, mime = HTML.encode(), "text/html; charset=utf-8"
            elif parsed.path == "/export":
                body = b'<style>html,body{margin:0;background:transparent;overflow:hidden}svg{display:block}</style><div id="stage"></div>'
                mime = "text/html; charset=utf-8"
            elif parsed.path == "/config":
                body, mime = json.dumps(load_timeline(timeline_path)).encode(), "application/json"
            elif parsed.path == "/frame":
                try:
                    t = float(parse_qs(parsed.query).get("t", ["0"])[0])
                    config = load_timeline(timeline_path)
                    body = render_scene(state_at(config, t), assets=ASSETS,
                                        width=width or config["width"], height=height or config["height"],
                                        transparent=transparent).encode()
                except (ValueError, KeyError) as error:
                    self.send_error(400, str(error))
                    return
                mime = "image/svg+xml; charset=utf-8"
            elif parsed.path.startswith("/assets/") and parsed.path[8:] in ASSET_FILES.values():
                path = ROOT / parsed.path[8:]
                body, mime = path.read_bytes(), mimetypes.guess_type(path)[0]
            else:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(body)
    return Handler


@contextmanager
def serve(timeline_path=DEFAULT_TIMELINE, port=0, **kwargs):
    server = ThreadingHTTPServer(("127.0.0.1", port), make_handler(timeline_path, **kwargs))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeline", type=Path, default=DEFAULT_TIMELINE)
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    load_timeline(args.timeline)
    with serve(args.timeline, args.port) as url:
        print(f"Preview: {url}", flush=True)
        try:
            threading.Event().wait()
        except KeyboardInterrupt:
            pass
