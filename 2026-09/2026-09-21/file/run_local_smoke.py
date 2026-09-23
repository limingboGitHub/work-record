"""Wait for weights, start ComfyUI lowvram, submit smoke workflow, collect result."""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from pathlib import Path
import subprocess
import sys

WEIGHTS = {
    Path(r"D:\models\qwen-image-2.1\diffusion_models\qwen_image_2.1_int8_convrot.safetensors"): 7_256_783_064,
    Path(r"D:\models\qwen-image-2.1\text_encoders\qwen3vl_8b_w4a8.safetensors"): 6_312_105_364,
    Path(r"D:\models\qwen-image-2.1\vae\qwen_image_2.1_vae_bf16.safetensors"): 675_509_688,
}
WF = Path(r"G:\project\work_record\2026-09\2026-09-21\file\qwen21_comfy_api_smoke.json")
OUT_DIR = Path(r"D:\ComfyUI_windows_portable\ComfyUI\output")
BASE = "http://127.0.0.1:8188"
LOG = Path(r"G:\project\work_record\2026-09\2026-09-21\file\local_run.log")


def log(msg: str) -> None:
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def wait_weights(timeout_s: int = 4 * 3600) -> bool:
    log("waiting for weights")
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        ok = True
        parts = []
        for path, size in WEIGHTS.items():
            incomplete = path.with_suffix(path.suffix + ".incomplete")
            if path.exists() and path.stat().st_size >= size * 0.999:
                parts.append(f"{path.name}=OK({path.stat().st_size})")
                continue
            if incomplete.exists():
                parts.append(f"{path.name}={incomplete.stat().st_size}/{size}")
                ok = False
            else:
                parts.append(f"{path.name}=MISSING")
                ok = False
        log(" | ".join(parts))
        if ok:
            log("weights ready")
            return True
        time.sleep(60)
    log("weights wait timeout")
    return False


def http_json(url: str, payload=None):
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="GET" if payload is None else "POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def server_up() -> bool:
    try:
        http_json(f"{BASE}/system_stats")
        return True
    except Exception:
        return False


def start_server():
    bat = r"G:\project\work_record\2026-09\2026-09-21\file\run_comfyui_lowvram.bat"
    if server_up():
        log("server already up")
        return
    log("starting ComfyUI lowvram")
    subprocess.Popen(
        ["cmd", "/c", bat],
        cwd=r"D:\ComfyUI_windows_portable",
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )
    for i in range(120):
        if server_up():
            log("server up")
            return
        time.sleep(5)
        if i % 6 == 0:
            log(f"waiting server {i*5}s")
    raise RuntimeError("ComfyUI server did not become ready")


def submit_and_wait(prompt_id: str) -> None:
    wf = json.loads(WF.read_text(encoding="utf-8"))
    payload = {"prompt": wf, "client_id": "mimo-job1"}
    log("posting workflow")
    result = http_json(f"{BASE}/prompt", payload)
    prompt_id = result.get("prompt_id")
    log(f"prompt_id={prompt_id}")
    deadline = time.time() + 2 * 3600
    while time.time() < deadline:
        try:
            hist = http_json(f"{BASE}/history/{prompt_id}")
        except Exception as e:
            log(f"history err {e}")
            time.sleep(20)
            continue
        if prompt_id in hist:
            item = hist[prompt_id]
            status = item.get("status", {})
            log(f"status={status.get('status_str')} completed={status.get('completed')}")
            if status.get("completed") or status.get("status_str") in {"success", "error"}:
                outputs = item.get("outputs", {})
                for node_out in outputs.values():
                    for img in node_out.get("images", []):
                        fname = img.get("filename")
                        sub = img.get("subfolder", "")
                        f = OUT_DIR / sub / fname
                        log(f"output {f} exists={f.exists()}")
                if status.get("status_str") == "error":
                    msgs = status.get("messages", [])
                    log(f"error messages={msgs[-3:]}")
                    raise RuntimeError("workflow failed")
                return
        time.sleep(20)
    raise RuntimeError("workflow timeout")


def main() -> int:
    LOG.write_text("", encoding="utf-8")
    if not wait_weights():
        return 2
    start_server()
    try:
        submit_and_wait("")
    except Exception as e:
        log(f"RUN_FAIL {e}")
        return 1
    log("RUN_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
