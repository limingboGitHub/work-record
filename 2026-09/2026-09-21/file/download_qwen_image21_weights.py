"""Download only the 8GB-device Qwen-Image-2.1 weights."""
from __future__ import annotations

import sys
from pathlib import Path

from modelscope import snapshot_download

DEST = Path(r"D:\models\qwen-image-2.1")

FILES = [
    "diffusion_models/qwen_image_2.1_int8_convrot.safetensors",
    "text_encoders/qwen3vl_8b_w4a8.safetensors",
    "vae/qwen_image_2.1_vae_bf16.safetensors",
    "README.md",
]

META = [
    "processor/*",
    "scheduler/*",
    "model_index.json",
    "configuration.json",
]


def main() -> int:
    DEST.mkdir(parents=True, exist_ok=True)
    print("START_WEIGHTS", flush=True)
    path = snapshot_download(
        model_id="Comfy-Org/Qwen-Image-2.1",
        allow_patterns=FILES,
        local_dir=str(DEST),
    )
    print("WEIGHTS_DONE", path, flush=True)
    print("START_META", flush=True)
    meta = snapshot_download(
        model_id="Qwen/Qwen-Image-2.1",
        allow_patterns=META,
        local_dir=str(DEST / "official_meta"),
    )
    print("META_DONE", meta, flush=True)
    print("ALL_DOWNLOADS_OK", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
