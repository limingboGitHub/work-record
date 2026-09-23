import json
import traceback
from modelscope.hub.api import HubApi

api = HubApi()
candidates = [
    "Qwen/Qwen-Image-2.1",
    "Qwen/Qwen-Image-2.1-PE-T2I",
    "Comfy-Org/Qwen-Image-2.1",
    "Qwen/Qwen-Image-2512",
    "FlagRelease/Qwen-Image-2.1-W8A8-arm-FlagOS",
    "lightx2v/Qwen-Image-2.1",
]

def flatten(obj, prefix=""):
    out = []
    if isinstance(obj, list):
        for x in obj:
            out.extend(flatten(x, prefix))
    elif isinstance(obj, dict):
        # common modelscope shapes
        name = obj.get("Path") or obj.get("Name") or obj.get("path") or obj.get("name")
        size = obj.get("Size") or obj.get("size")
        if name and not any(k in obj for k in ("Files", "files", "Subfolder", "Tree")):
            out.append((name, size))
        for k in ("Files", "files", "Data", "data", "Subfolder", "children", "Tree"):
            if k in obj:
                out.extend(flatten(obj[k], prefix))
    return out

for mid in candidates:
    print("=" * 70)
    print("MODEL", mid)
    try:
        files = api.get_model_files(model_id=mid, recursive=True)
        items = flatten(files)
        if not items and isinstance(files, dict):
            print("RAW_KEYS", list(files.keys())[:30])
            print(json.dumps(files, ensure_ascii=False, default=str)[:2000])
        else:
            print("COUNT", len(items))
            for name, size in items:
                print(f"  {name}\t{size}")
    except Exception as e:
        print("ERR", type(e).__name__, e)
        traceback.print_exc()
