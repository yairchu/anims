"""Local playback/scrubbing UI using the shared SVG renderer."""
import argparse
import json
import mimetypes
import threading
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from animation_scene import available_asset_files, render_scene
from video_formats import FORMATS
from animation_timeline import SCENE_LABELS, load_scene, state_at

ROOT = Path(__file__).parent

HTML = '''<!doctype html><meta charset="utf-8"><title>Political meters · animation preview</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#e9e9ed;font:15px system-ui;color:#24242a}
#stage{line-height:0;margin:auto;max-width:1200px;background:white}#stage svg{width:100%;height:auto}
nav{max-width:1200px;margin:16px auto;padding:0 16px}button,select{font:inherit;padding:8px 12px;margin-right:8px}
#seek{width:100%;margin:16px 0}#chapters{display:flex;gap:6px;flex-wrap:wrap}#chapters button{font-size:12px}
</style><div id="stage"></div><nav><button id="play">Play</button>
<select id="speed"><option value="0.5">0.5×</option><option selected value="1">1×</option><option value="2">2×</option></select>
<select id="scene" aria-label="Scene"></select>
<select id="format" aria-label="Video format"><option value="portrait">Instagram portrait · 9:16</option><option value="landscape">Landscape · 16:9</option></select>
<output id="time"></output><input id="seek" aria-label="Timeline time" type="range" min="0" step="0.01">
<div id="chapters"></div><p>Edit the selected scene’s timeline JSON, then reload. <code id="export-command"></code></p></nav>
<script>
let config, time=0, playing=false, last=0, busy=false, revision=0, selectionRevision=0;
const positions={}, scene=document.querySelector('#scene');
const stage=document.querySelector('#stage'), seek=document.querySelector('#seek'), button=document.querySelector('#play');
async function draw(t){
  const mine=++revision;
  positions[scene.value]=t;
  const format=document.querySelector('#format').value;
  stage.style.maxWidth=format==='portrait'?'405px':'1200px';
  const response=await fetch('/frame?t='+t+'&format='+format+'&scene='+encodeURIComponent(scene.value));
  const svg=await response.text();
  if(mine!==revision)return;
  stage.innerHTML=svg;seek.value=t;
  document.querySelector('#time').textContent=t.toFixed(2)+' / '+config.duration.toFixed(2)+' s';
}
function pause(){playing=false;button.textContent='Play'}
button.onclick=()=>{if(playing){pause()}else{if(time>=config.duration)time=0;playing=true;last=performance.now();button.textContent='Pause'}};
document.querySelector('#format').onchange=()=>{updateExport();draw(time)};
scene.onchange=()=>selectScene();
seek.oninput=()=>{pause();time=Number(seek.value);draw(time)};
async function tick(now){
  if(playing&&!busy){busy=true;time=Math.min(config.duration,time+(now-last)/1000*Number(document.querySelector('#speed').value));last=now;
    try{await draw(time)}finally{busy=false}if(time>=config.duration)pause();}
  requestAnimationFrame(tick);
}
function updateExport(){
  document.querySelector('#export-command').textContent='Export: uv run python export_video.py '+
    (scene.value==='custom'?'--timeline YOUR_TIMELINE.json':'--scene '+scene.value)+
    ' --format '+document.querySelector('#format').value;
}
async function selectScene(){
  pause(); ++revision;
  const mine=++selectionRevision;
  const result=await(await fetch('/config?scene='+encodeURIComponent(scene.value))).json();
  if(mine!==selectionRevision)return;
  config=result; seek.max=config.duration; time=positions[scene.value]||0;
  document.querySelector('#chapters').replaceChildren();
  for(const chapter of config.chapters){const b=document.createElement('button');b.textContent=chapter.label;
    b.onclick=()=>{pause();time=chapter.time;draw(time)};document.querySelector('#chapters').append(b)}
  updateExport(); await draw(time);
}
(async()=>{
  const available=await(await fetch('/scenes')).json();
  for(const [label,value] of Object.entries(available.options)){
    const option=document.createElement('option');option.textContent=label;option.value=value;scene.append(option);
  }
  scene.value=available.selected;
  await selectScene();requestAnimationFrame(tick);
})();
</script>'''


def make_handler(timeline_path=None, *, scene="blocked", transparent=False, width=None, height=None):
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
            elif parsed.path == "/scenes":
                options = {"Custom timeline": "custom"} if timeline_path else SCENE_LABELS
                body = json.dumps(dict(options=options, selected="custom" if timeline_path else scene)).encode()
                mime = "application/json"
            elif parsed.path in {"/config", "/frame"}:
                try:
                    t = float(parse_qs(parsed.query).get("t", ["0"])[0])
                    config = load_scene(parse_qs(parsed.query).get("scene", [scene])[0], timeline_path)
                    selected_format = parse_qs(parsed.query).get("format", [None])[0]
                    frame_width, frame_height = FORMATS[selected_format] if selected_format else (config["width"], config["height"])
                    if parsed.path == "/config":
                        body, mime = json.dumps(config).encode(), "application/json"
                    else:
                        assets = {key: "/assets/" + value for key, value in available_asset_files().items()}
                        body = render_scene(state_at(config, t), assets=assets,
                                            width=width or frame_width, height=height or frame_height,
                                            transparent=transparent).encode()
                        mime = "image/svg+xml; charset=utf-8"
                except (ValueError, KeyError) as error:
                    self.send_error(400, str(error))
                    return
            elif parsed.path.startswith("/assets/") and parsed.path[8:] in available_asset_files().values():
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
def serve(timeline_path=None, port=0, **kwargs):
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
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--timeline", type=Path)
    source.add_argument("--scene", choices=SCENE_LABELS.values(), default="blocked")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    load_scene(args.scene, args.timeline)
    with serve(args.timeline, args.port, scene=args.scene) as url:
        print(f"Preview: {url}", flush=True)
        try:
            threading.Event().wait()
        except KeyboardInterrupt:
            pass
