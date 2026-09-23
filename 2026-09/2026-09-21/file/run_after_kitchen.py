"""After kitchen upgrade: restart ComfyUI lowvram if needed, run INT8 smoke."""
from __future__ import annotations

import json
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = "http://127.0.0.1:8188"
WF_INT8 = Path(r"G:\project\work_record\2026-09\2026-09-21\file\qwen21_comfy_api_smoke.json")
OUT_DIR = Path(r"D:\ComfyUI_windows_portable\ComfyUI\output")
LOG = Path(r"G:\project\work_record\2026-09\2026-09-21\file\post_kitchen_run.log")
BAT = r"G:\project\work_record\2026-09\2026-09-21\file\run_comfyui_lowvram.bat"


def log(m: str) -> None:
    line = f"[{time.strftime('%H:%M:%S')}] {m}"
    print(line, flush=True)
    LOG.open("a", encoding="utf-8").write(line + "\n")


def http_json(url, payload=None, timeout=60):
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
        http_json(f"{BASE}/system_stats", timeout=8)
        return True
    except Exception:
        return False


def restart_server():
    log("restart ComfyUI to pick up kitchen 0.2.35")
    subprocess.run(["taskkill", "/F", "/FI", "WINDOWTITLE eq *ComfyUI*"], capture_output=True)
    # kill python hosting main.py lowvram if still up after we want clean restart
    if server_up():
        subprocess.run(
            ["powershell", "-Command", "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*ComfyUI\\\\main.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"],
            capture_output=True,
        )
        time.sleep(3)
    subprocess.Popen(["cmd", "/c", BAT], cwd=r"D:\ComfyUI_windows_portable", creationflags=subprocess.CREATE_NEW_CONSOLE)
    for i in range(90):
        if server_up():
            log("server up")
            return
        time.sleep(5)
    raise RuntimeError("server not up")


def wait_kitchen(timeout_s=1800) -> bool:
    log("wait kitchen 0.2.35 install")
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        logf = Path(r"G:\project\work_record\2026-09\2026-09-21\file\kitchen_dl.log")
        text = logf.read_text(encoding="utf-8", errors="replace") if logf.exists() else ""
        if "PIP_EXIT=0" in text or "Successfully installed comfy_kitchen-0.2.35" in text:
            log("kitchen installed")
            return True
        if "PIP_EXIT=" in text and "PIP_EXIT=0" not in text:
            log(f"pip failed: {text[-300:]}")
            return False
        whl = Path(r"D:\Temp\comfy_kitchen-0.2.35-cp312-abi3-win_amd64.whl")
        sz = whl.stat().st_size / 1e6 if whl.exists() else 0
        log(f"kitchen whl {sz:.1f}MB")
        time.sleep(30)
    return False


def run_wf(path: Path, tag: str) -> int:
    wf = json.loads(path.read_text(encoding="utf-8"))
    result = http_json(f"{BASE}/prompt", {"prompt": wf, "client_id": tag}, timeout=120)
    pid = result.get("prompt_id")
    log(f"{tag} prompt_id={pid} errors={result.get('node_errors')}")
    deadline = time.time() + 3 * 3600
    while time.time() < deadline:
        hist = http_json(f"{BASE}/history/{pid}")
        if pid in hist:
            st = hist[pid].get("status", {})
            log(f"{tag} status={st.get('status_str')} completed={st.get('completed')}")
            if st.get("status_str") == "error":
                for m in st.get("messages", []):
                    if m[0] == "execution_error":
                        log(f"{tag} ERR {m[1].get('exception_type')}: {m[1].get('exception_message')}")
                return 4
            if st.get("completed") or st.get("status_str") == "success":
                for out in hist[pid].get("outputs", {}).values():
                    for img in out.get("images", []):
                        f = OUT_DIR / img.get("subfolder", "") / img["filename"]
                        log(f"{tag} OUT {f} exists={f.exists()}")
                return 0
        time.sleep(20)
    log(f"{tag} timeout")
    return 5


def main() -> int:
    LOG.write_text("", encoding="utf-8")
    if not wait_kitchen():
        return 2
    restart_server()
    rc = run_wf(WF_INT8, "int8")
    if rc == 0:
        log("RUN_OK int8")
        return 0
    log(f"int8 failed rc={rc}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
