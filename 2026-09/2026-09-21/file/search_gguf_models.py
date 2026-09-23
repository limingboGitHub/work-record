from modelscope.hub.api import HubApi

api = HubApi()
candidates = [
    "Qwen-Image-2.1-Uncensored-GGUF",
    "city96/Qwen-Image-2.1-Uncensored-GGUF",
    "QuantStack/Qwen-Image-2.1-Uncensored-GGUF",
    "mradermacher/Qwen-Image-2.1-Uncensored-GGUF",
    "Comfy-Org/Qwen-Image-2.1-GGUF",
    "Qwen/Qwen-Image-2.1-GGUF",
    "city96/Qwen-Image-2.1-GGUF",
    "bulldog76/Qwen-Image-2.1-GGUF",
    "Yisoo/Qwen-Image-2.1-GGUF",
]


def walk(o):
    out = []
    if isinstance(o, list):
        for x in o:
            out.extend(walk(x))
    elif isinstance(o, dict):
        name = o.get("Path") or o.get("Name") or o.get("path")
        size = o.get("Size") or o.get("size")
        if name and size is not None and not any(k in o for k in ("Files", "files")):
            out.append((name, size))
        for k in ("Files", "files", "Data", "data"):
            if k in o:
                out.extend(walk(o[k]))
    return out


for mid in candidates:
    print("=" * 60, mid)
    try:
        files = api.get_model_files(model_id=mid, recursive=True)
        items = walk(files)
        if not items:
            print("no items", type(files), list(files)[:20] if isinstance(files, dict) else "")
        for n, s in items[:50]:
            print(f"{n}\t{s}")
    except Exception as e:
        print(type(e).__name__, str(e)[:400])
