"""Submit Qwen-Image-2.1 GGUF smoke to running ComfyUI and wait for image."""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from pathlib import Path

WF = Path(r"G:\project\work_record\2026-09\2026-09-21\file\qwen21_comfy_api_smoke.json")
OUT_DIR = Path(r"D:\ComfyUI_windows_portable\ComfyUI\output")
BASE = "http://127.0.0.1:8188"
LOG = Path(r"G:\project\work_record\2026-09\2026-09-21\file\gguf_smoke.log")


def log(msg: str) -> None:
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def http_json(url: str, payload=None, timeout=60):
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="GET" if payload is None else "POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
        text = raw.decode("utf-8", errors="replace")
        log(f"HTTP {resp.status} {url} body[:200]={text[:200]!r}")
        return json.loads(text)


def main() -> int:
    LOG.write_text("", encoding="utf-8")
    try:
        stats = http_json(f"{BASE}/system_stats")
        log(f"comfyui={stats.get('system', {}).get('comfyui_version')}")
    except Exception as e:
        log(f"system_stats fail: {e}")
        return 1

    wf = json.loads(WF.read_text(encoding="utf-8"))
    # ensure UnetLoaderGGUF model name is used
    log(f"nodes={list(wf.keys())} unet={wf['9']['inputs']['unet_name']}")

    try:
        result = http_json(f"{BASE}/prompt", {"prompt": wf, "client_id": "mimo-job1-gguf"}, timeout=120)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        log(f"prompt HTTPError {e.code}: {body[:500]}")
        return 2
    except Exception as e:
        log(f"prompt fail: {type(e).__name__}: {e}")
        return 2

    prompt_id = result.get("prompt_id")
    log(f"prompt_id={prompt_id} node_errors={result.get('node_errors')}")
    if not prompt_id:
        log(f"no prompt_id in {result}")
        return 3

    deadline = time.time() + 3 * 3600
    while time.time() < deadline:
        try:
            hist = http_json(f"{BASE}/history/{prompt_id}")
        except Exception as e:
            log(f"history err {e}")
            time.sleep(15)
            continue
        if prompt_id in hist:
            item = hist[prompt_id]
            status = item.get("status", {})
            log(f"status={status.get('status_str')} completed={status.get('completed')}")
            if status.get("status_str") == "error" or (
                status.get("completed") is False and status.get("status_str") == "error"
            ):
                log(f"error msgs={status.get('messages', [])[-5:]}")
                return 4
            if status.get("completed") or status.get("status_str") == "success":
                outputs = item.get("outputs", {})
                for node_out in outputs.values():
                    for img in node_out.get("images", []):
                        fname = img.get("filename")
                        sub = img.get("subfolder", "")
                        f = OUT_DIR / sub / fname
                        log(f"output {f} exists={f.exists()}")
                return 0
        time.sleep(15)
    log("timeout")
    return 5


if __name__ == "__main__":
    raise SystemExit(main())
