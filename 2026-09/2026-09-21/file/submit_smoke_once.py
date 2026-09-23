"""Submit current smoke workflow once and print result summary."""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from pathlib import Path

WF = Path(r"G:\project\work_record\2026-09\2026-09-21\file\qwen21_comfy_api_smoke.json")
OUT_DIR = Path(r"D:\ComfyUI_windows_portable\ComfyUI\output")
BASE = "http://127.0.0.1:8188"


def http_json(url: str, payload=None, timeout=60):
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="GET" if payload is None else "POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def main() -> int:
    wf = json.loads(WF.read_text(encoding="utf-8"))
    print("unet", wf["9"]["class_type"], wf["9"]["inputs"].get("unet_name"), flush=True)
    result = http_json(f"{BASE}/prompt", {"prompt": wf, "client_id": "mimo-int8"}, timeout=120)
    prompt_id = result.get("prompt_id")
    print("prompt_id", prompt_id, "node_errors", result.get("node_errors"), flush=True)
    deadline = time.time() + 3 * 3600
    while time.time() < deadline:
        hist = http_json(f"{BASE}/history/{prompt_id}")
        if prompt_id in hist:
            status = hist[prompt_id].get("status", {})
            msgs = status.get("messages", [])
            last = msgs[-1] if msgs else None
            print("status", status.get("status_str"), "completed", status.get("completed"), "last", str(last)[:300], flush=True)
            if status.get("status_str") == "error":
                for m in msgs:
                    if m[0] == "execution_error":
                        print("ERROR", m[1].get("exception_type"), m[1].get("exception_message"), flush=True)
                return 4
            if status.get("completed") or status.get("status_str") == "success":
                for node_out in hist[prompt_id].get("outputs", {}).values():
                    for img in node_out.get("images", []):
                        f = OUT_DIR / img.get("subfolder", "") / img["filename"]
                        print("output", f, f.exists(), flush=True)
                return 0
        time.sleep(20)
    print("timeout", flush=True)
    return 5


if __name__ == "__main__":
    raise SystemExit(main())
