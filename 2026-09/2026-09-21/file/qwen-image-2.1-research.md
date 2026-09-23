# 调研结论：Qwen-Image-2.1 开源版文生图模型

> 调研日期：2026-09-21 · 路径：Playwright CLI（Browser Use/IAB 不可用，经用户确认）
> 主要来源：官方 GitHub README/LICENSE、qwenimages.com 发布博客、Bing SERP

## 1. 基本信息

| 项 | 内容 |
|----|------|
| 模型名 | **Qwen-Image-2.1** |
| 发布日 | **2026-09-20**（昨日开源） |
| 开发方 | 阿里巴巴通义千问团队（Hangzhou Tongyi Laboratory） |
| 定位 | 统一 **文生图 + 图像编辑** 的轻量开源模型 |
| 视觉生成组件 | **7B** 参数 · **32 层 Single-Stream DiT** |
| 文本/条件编码 | **Qwen3-VL 8B**（文本指令 + 条件图统一编码） |
| VAE | **64 通道 RGBA** · **16× 空间压缩**（原生透明） |
| 调度器 | Flow Matching · Euler discrete · dynamic shifting |
| 默认分辨率 | 原生 **2K**（1:1 = 2048×2048） |
| 默认步数 | **40** |
| 许可证 | **Qwen Research License**（非商用；商用需另行申请） |
| 官方仓库 | https://github.com/QwenLM/Qwen-Image-2.1 |
| 权重 | HuggingFace `Qwen/Qwen-Image-2.1` · ModelScope 同名 |

> 注意：7B 指**视觉生成组件**，不含 Qwen3-VL 编码器；整条流水线总参数更大。

## 2. 四大核心能力（官方口径）

1. **紧凑高效**：混合粒度注意力 + prefix KV cache 复用，静态条件（文本/参考图）只算一次，后续去噪步复用。
2. **原生透明 RGBA**：同一模型可生成/编辑带真实 alpha 的透明图，无需后处理抠图；适合贴纸、商品抠图、游戏素材、图标。
3. **多参考编辑**：最多 **10 张参考图**；局部编辑支持 **圆圈 / 涂抹标注 / 独立 mask**；可保人物身份与商品特征。
4. **质感与排版**：改进文字渲染、人像光影与细节。

## 3. 能力边界速查

| 能力 | 支持情况 |
|------|----------|
| 文生图 | ✅ |
| 图像编辑（单图） | ✅ |
| 多参考图合成（≤10） | ✅ |
| 原生 RGBA 透明 | ✅ |
| 局部编辑（圆圈/mask） | ✅ |
| 原生 2K 输出 | ✅ 多种宽高比 |
| 中文文字渲染 | 官方强调强项（一代起） |
| 专用 Prompt Enhancer | ✅ PE-T2I / PE-I2I（Qwen3.5-VL 9B 微调） |

### 推荐分辨率表

| 宽高比 | 分辨率 |
|--------|--------|
| 1:1 | 2048×2048 |
| 4:3 | 2400×1792 |
| 3:4 | 1792×2400 |
| 3:2 | 2528×1696 |
| 2:3 | 1696×2528 |
| 16:9 | 2752×1536 |
| 9:16 | 1536×2752 |

## 4. 部署与生态（Day-0）

| 生态 | 状态 | 说明 |
|------|------|------|
| **Diffusers** | Day-0 | `QwenImage21Pipeline`（PR #14804） |
| **ComfyUI** | Day-0 | 权重 `Comfy-Org/Qwen-Image-2.1`；BF16 扩散约 **14.2GB**，INT8 约 **7.26GB** |
| **vLLM-Omni** | Day-0 | prefix KV cache、CUDA Graph、FP8、TP/Ulysses |
| **SGLang** | Day-0 | Cache-DiT、CUDA graphs、多并行、component offload（PR #39983） |
| **LightX2V** | Day-0 | 推理加速 |
| **ModelScope** | 支持 | DiffSynth-Studio：下载/在线生成/LoRA |
| **AMD ROCm / FlagOS** | 支持 | 多芯片平台零改代码 |

### 最小运行依赖

```
torch>=2.4.0
transformers>=5.17
diffusers (git main)
accelerate
pillow
```

低显存：`pipe.enable_model_cpu_offload()`。

## 5. 许可证（关键决策点）

- 协议：**Qwen Research License Agreement**（2026-09-20）
- **仅限研究/评估非商用**；商用需邮件申请 `model-business@notice.qwencloud.com`
- 再分发须附协议副本与 Notice 声明
- 若用其输出训练/改进其他分发模型，须展示 “Built with Qwen” / “Improved using Qwen”
- 衍生产品不得以 “Qwen” 作主名称
- 管辖：中国法律 · 杭州法院

**选型建议**：研究/内部评估/原型可直接用；**上生产/嵌入商业产品前必须确认商业授权**。

## 6. 与前代/邻居对比（摘要）

| | Qwen-Image 2.0 | **Qwen-Image-2.1** | Qwen Image 3.0（2026-07） |
|--|----------------|--------------------|---------------------------|
| 定位 | 紧凑+2K | 可下载权重 + 编辑向 | 高信息密度云端产品向 |
| 原生 RGBA | — | ✅ | 弱/不同侧重 |
| ≤10 参考图 | — | ✅ | — |
| 本地部署 | ✅ | ✅ | 更偏云端 |
| Comfy/Diffusers Day-0 | — | ✅ | 产品向 |

厂商自报 Qwen-Image-Bench 综合约 **60.28**（vs Nano Banana 2.0 59.82、GPT Image 1.5 59.65）；**非第三方独立评测**，仅作定位参考。

## 7. 快速上手代码（官方 README）

```python
import torch
from diffusers import QwenImage21Pipeline

pipe = QwenImage21Pipeline.from_pretrained(
    "Qwen/Qwen-Image-2.1", torch_dtype=torch.bfloat16
).to("cuda")

image = pipe(
    prompt='A neon shop sign that reads "QWEN IMAGE 2.1", rainy night',
    num_inference_steps=40,
    generator=torch.Generator("cuda").manual_seed(42),
).images[0]
image.save("t2i_example.png")
```

透明图提示词模板：

```
This is an RGBA image with transparency. <描述>. The image has alpha channel and the background is transparent.
```

## 8. 适用场景建议

**适合**
- 需要透明素材/贴纸/电商抠图的一体化工作流
- 多参考拼装（穿搭、合影、室内）
- ComfyUI / Diffusers 本地研究原型
- 中文/复杂文字渲染场景

**需谨慎**
- 商用嵌入（Research License）
- HF 直连可能超时 → 国内优先 **ModelScope**
- 显存：BF16 扩散权重约 14GB+，整链路（含 TE/VAE）更高；低配用 INT8/CPU offload/SGLang offload

## 9. 相关链接

- GitHub: https://github.com/QwenLM/Qwen-Image-2.1
- LICENSE: https://github.com/QwenLM/Qwen-Image-2.1/blob/main/LICENSE
- HF: https://huggingface.co/Qwen/Qwen-Image-2.1 （调研时超时）
- ModelScope: https://www.modelscope.cn/models/Qwen/Qwen-Image-2.1
- 发布解读: https://qwenimages.com/zh/blog/qwen-image-2-1-release
- Comfy: https://comfy.org/zh-CN/qwen-image-2.1
- PE 权重: `Qwen/Qwen-Image-2.1-PE-T2I` / `Qwen/Qwen-Image-2.1-PE-I2I`
