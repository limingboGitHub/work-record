# 本地试跑：Qwen-Image-2.1 量化部署设计（RTX 3060 Ti 8GB）

> 日期：2026-09-22 更新 · 续 job1 调研后的本地落地
> 设备：NVIDIA GeForce RTX 3060 Ti 8GB · 系统内存 16GB · 磁盘 D: 约 600GB 空闲

## 0. 量化版本结论（2026-09-22 修订）

**首选（8GB 卡）：DiT GGUF Q4_K_M + TE W4A8 + VAE BF16**

| 组件 | 方案 | 体积 | 来源 |
|------|------|------|------|
| DiT | **GGUF Q4_K_M** | **4.6 GB** | `abenzerps/Qwen-Image-2.1-GGUF` |
| DiT 备选 | GGUF Q4_0 | 4.05 GB | 同上（画质略降、显存更省） |
| DiT 对照 | Comfy INT8 convrot | 7.26 GB | `Comfy-Org/Qwen-Image-2.1`（已下载，可对照） |
| TE | **W4A8** | 6.31 GB | Comfy-Org（已下载） |
| VAE | BF16 | 0.68 GB | Comfy-Org（已下载） |

**Uncensored-GGUF（用户点名评估）**

- 仓库存在：`KasugaiSakura/Qwen-Image-2.1-Uncensored-GGUF`（及 0xSojalSec / Janchan123 / TBT000 镜像）
- 规格与 abenzerps **同构**：Q4_0 4.05GB / Q4_K_M 4.6GB / Q5_K_M 5.22GB / Q6_K 5.88GB / Q8_0 7.59GB
- 许可证仍标 **qwen-research**
- **不建议作为 job1 主路径**：这是社区 **去审查 / 内容过滤放宽** 分叉，不是官方对齐权重；评估官方 2.1 能力会有偏差
- 技术上 INT4 体积与官方 GGUF 一致，**显存收益相同**；若只是要 8GB 可跑的 DiT，用 **abenzerps Q4_K_M 即可**
- 使用边界：仅本地研究/评估；不要用于违法内容；商用仍受 Research License 限制

### 为什么从 INT8 改优先 GGUF Q4

| DiT 量化 | 体积 | 8GB 峰值估算（组件分阶段） | 结论 |
|----------|------|---------------------------|------|
| INT8 convrot | 7.26 GB | ~7.3GB + 激活 + 驱动 ≈ 8GB 贴边 | 边缘，易 OOM |
| **Q4_K_M** | **4.6 GB** | ~4.6 + 激活 ≈ **5.5–6.5GB** | **有余量** |
| Q4_0 | 4.05 GB | 更低 | 再降一档画质 |

TE W4A8 6.31GB 编码后卸载时，峰值取 max(DiT 阶段, TE 阶段)：Q4 路径约 **6–7GB**，比 INT8 稳。

### 运行时（确认稿）

- ComfyUI：`D:\ComfyUI_windows_portable`（已更新含 qwen_image21）
- 节点：`UnetLoaderGGUF`（ComfyUI-GGUF 已装）+ `CLIPLoader(type=qwen_image)` + `TextEncodeQwenImage21` + `QwenImage21Cache(cpu, int8)`
- 启动：`--lowvram`；仍 OOM 再 `--novram` / 降到 512
- 权重目录：`D:\models\qwen-image-2.1\`（INT8/W4A8/VAE 已齐；GGUF Q4_K_M 可另下）
- 冒烟：768×768 · 20 步 · euler/simple · cfg=1 · seed=42

## 1. 设备约束

| 资源 | 数值 | 含义 |
|------|------|------|
| GPU VRAM | 8191 MB | 必须量化 + 分阶段卸载 |
| RAM | 16GB | CPU offload 空间紧，优先 disk |
| D: | ~600GB | 权重与 offload 落盘 |

## 2. Comfy-Org INT8/W4A8 权重（对照路径，已下载）

| 文件 | 体积 | 用途 |
|------|------|------|
| `diffusion_models/qwen_image_2.1_int8_convrot.safetensors` | 7.26 GB | 对照 / 画质更好但显存紧 |
| `text_encoders/qwen3vl_8b_w4a8.safetensors` | 6.31 GB | **主 TE** |
| `text_encoders/qwen3vl_8b_int8_convrot.safetensors` | 9.35 GB | 不用（太重） |
| `vae/qwen_image_2.1_vae_bf16.safetensors` | 0.68 GB | 主 VAE |

## 3. GGUF 推荐下载

```
hf-mirror.com/abenzerps/Qwen-Image-2.1-GGUF
  qwen-image-2.1-Q4_K_M.gguf   4.6 GB   ← 首选
  qwen-image-2.1-Q4_0.gguf     4.05 GB  ← 显存再紧时
```

落地：`D:\models\qwen-image-2.1\diffusion_models\`

## 4. 执行清单

- [x] 硬件盘点
- [x] INT8/W4A8/VAE 权重下载完成
- [x] ComfyUI 更新 + comfy-aimdo 0.5.5
- [x] ComfyUI-GGUF 节点在位
- [x] 量化方案改为 **Q4_K_M 优先**
- [ ] 下载 `qwen-image-2.1-Q4_K_M.gguf`
- [ ] 用 lowvram + GGUF 工作流冒烟出图
- [ ] 记录 VRAM/耗时/OOM
- [ ] 回写 job1

## 5. 风险

| 风险 | 回退 |
|------|------|
| Q4 画质掉档 | Q5_K_M / Q8_0（显存更紧）/ 对照 INT8 |
| TE 6.3GB 仍 OOM | 编码后立刻卸载；或下 GGUF TE；或 512 分辨率 |
| Uncensored 权重内容/许可 | job1 评估用 abenzerps 对齐版 |
| Research License | 仅研究评估，商用需授权 |
