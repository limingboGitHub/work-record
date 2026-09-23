"""Wait for Qwen-Image-2.1 weights, ensure ComfyUI, run beauty low-res batch."""
from __future__ import annotations

import json
import shutil
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
PROMPTS_JSON = Path(r"G:\project\work_record\2026-09\2026-09-21\file\qwen21_beauty_batch_prompts.json")
WF_TEMPLATE = Path(r"G:\project\work_record\2026-09\2026-09-21\file\qwen21_beauty_batch_workflow.json")
OUT_DIR = Path(r"D:\ComfyUI_windows_portable\ComfyUI\output")
INDEX_DIR = Path(r"G:\project\work_record_temp\2026-09\2026-09-21\output")
BASE = "http://127.0.0.1:8188"
LOG = Path(r"G:\project\work_record\2026-09\2026-09-21\file\beauty_batch_run.log")
START_BAT = Path(r"G:\project\work_record\2026-09\2026-09-21\file\run_comfyui_lowvram.bat")
CLIENT_ID = "mimo-job2-beauty"
RESOLUTION = 512
STEPS = 20


def log(msg: str) -> None:
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def wait_weights(timeout_s: int = 6 * 3600) -> bool:
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
            # final rename check
            for path in WEIGHTS:
                if not path.exists():
                    inc = path.with_suffix(path.suffix + ".incomplete")
                    if inc.exists() and inc.stat().st_size >= WEIGHTS[path] * 0.999:
                        try:
                            inc.replace(path)
                            log(f"renamed {inc.name} -> {path.name}")
                        except Exception as e:
                            log(f"rename fail {path.name}: {e}")
            still = [p.name for p in WEIGHTS if not p.exists()]
            if not still:
                log("weights ready")
                return True
            log(f"weights incomplete after rename: {still}")
            ok = False
        time.sleep(45)
    log("weights wait timeout")
    return False


def http_json(url: str, payload=None, timeout: int = 60):
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="GET" if payload is None else "POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def server_up() -> bool:
    try:
        http_json(f"{BASE}/system_stats", timeout=5)
        return True
    except Exception:
        return False


def start_server() -> None:
    if server_up():
        log("server already up")
        return
    log("starting ComfyUI lowvram")
    subprocess.Popen(
        ["cmd", "/c", str(START_BAT)],
        cwd=r"D:\ComfyUI_windows_portable",
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )
    for i in range(180):
        if server_up():
            log("server up")
            return
        time.sleep(5)
        if i % 6 == 0:
            log(f"waiting server {i * 5}s")
    raise RuntimeError("ComfyUI server did not become ready")


def build_workflow(item: dict) -> dict:
    wf = json.loads(WF_TEMPLATE.read_text(encoding="utf-8"))
    prompt = item["prompt"]
    seed = int(item.get("seed", 101))
    prefix = f"qwen21_beauty_lowres_{item['id']}"
    wf["3"]["inputs"]["seed"] = seed
    wf["3"]["inputs"]["steps"] = STEPS
    wf["3"]["inputs"]["cfg"] = 1
    wf["3"]["inputs"]["sampler_name"] = "euler"
    wf["3"]["inputs"]["scheduler"] = "simple"
    wf["5"]["inputs"]["prompt"] = prompt
    wf["5"]["inputs"]["negative_prompt"] = ""
    wf["5"]["inputs"]["resolution"] = RESOLUTION
    wf["6"]["inputs"]["prompt"] = prompt
    wf["6"]["inputs"]["negative_prompt"] = ""
    wf["6"]["inputs"]["resolution"] = RESOLUTION
    wf["11"]["inputs"]["filename_prefix"] = prefix
    return wf


def submit_one(item: dict) -> dict:
    wf = build_workflow(item)
    payload = {"prompt": wf, "client_id": CLIENT_ID}
    log(f"submit {item['id']} style={item.get('style')} template={item.get('template')}")
    result = http_json(f"{BASE}/prompt", payload)
    prompt_id = result.get("prompt_id")
    log(f"  prompt_id={prompt_id}")
    deadline = time.time() + 2 * 3600
    outputs: list[str] = []
    while time.time() < deadline:
        try:
            hist = http_json(f"{BASE}/history/{prompt_id}")
        except Exception as e:
            log(f"  history err {e}")
            time.sleep(15)
            continue
        if prompt_id in hist:
            status = hist[prompt_id].get("status", {})
            completed = status.get("completed")
            status_str = status.get("status_str")
            if completed or status_str in {"success", "error"}:
                log(f"  status={status_str} completed={completed}")
                for node_out in hist[prompt_id].get("outputs", {}).values():
                    for img in node_out.get("images", []):
                        fname = img.get("filename")
                        sub = img.get("subfolder", "")
                        f = OUT_DIR / sub / fname
                        outputs.append(str(f))
                        log(f"  output {f} exists={f.exists()}")
                if status_str == "error":
                    msgs = status.get("messages", [])
                    log(f"  error messages={msgs[-5:]}")
                    return {"id": item["id"], "ok": False, "prompt_id": prompt_id, "outputs": outputs, "error": msgs[-3:]}
                return {"id": item["id"], "ok": True, "prompt_id": prompt_id, "outputs": outputs, "style": item.get("style"), "template": item.get("template")}
        time.sleep(12)
    return {"id": item["id"], "ok": False, "prompt_id": prompt_id, "outputs": outputs, "error": "timeout"}


def main() -> int:
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    LOG.write_text("", encoding="utf-8")
    if not wait_weights():
        return 2
    start_server()
    data = json.loads(PROMPTS_JSON.read_text(encoding="utf-8"))
    items = data["prompts"]
    results = []
    for item in items:
        try:
            r = submit_one(item)
        except Exception as e:
            log(f"RUN_FAIL {item.get('id')}: {e}")
            r = {"id": item.get("id"), "ok": False, "error": str(e)}
        results.append(r)
        # persist progressive index
        (INDEX_DIR / "beauty_batch_results.json").write_text(
            json.dumps({"meta": data.get("meta"), "results": results}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    ok_n = sum(1 for r in results if r.get("ok"))
    log(f"BATCH_DONE ok={ok_n}/{len(results)}")
    # copy index into job file dir for light reference
    shutil.copy2(
        INDEX_DIR / "beauty_batch_results.json",
        Path(r"G:\project\work_record\2026-09\2026-09-21\file\beauty_batch_results.json"),
    )
    return 0 if ok_n == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
