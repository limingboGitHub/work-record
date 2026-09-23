# Job: 调研 QwenImage 2.1 开源版文生图模型

## 基本信息

| 字段 | 内容 |
|------|------|
| 日期 | 2026-09-21 |
| 项目/模块 | 文生图模型调研（QwenImage 2.1 开源版） |
| 状态 | 已完成 |
| 预估耗时 | 30 min |
| 实际耗时 | ~25 min |
| 关键字 | #调研 #文生图 #QwenImage #开源模型 #AIGC #ResearchLicense #Diffusers #ComfyUI |

## 任务描述

> 新建今日 job：调研通义千问系新的文生图模型 **QwenImage 2.1 开源版本**，摸清其开源状态、能力边界、部署方式与适用场景，为后续选型/接入做参考。

## 关联工作（文件索引）

| 关系 | 文件路径 | 说明 |
|------|----------|------|
| 后续（批图试跑） | `./job2.md` | 官方提示词模板 · 美女主题低分辨率批图 |
| 附件 | `./file/qwen-image-2.1-research.md` | 开源调研结论 |
| 附件 | `./file/qwen-image-2.1-local-quant-plan.md` | **当前设备量化部署设计（确认稿）** |
| 附件 | `./file/qwen21_comfy_api_smoke.json` | ComfyUI API 冒烟工作流 |
| 附件 | `./file/run_comfyui_lowvram.bat` | 8GB 低显存启动脚本 |
| 附件 | `./file/run_local_smoke.py` / `.bat` | 等权重→起服务→提交工作流 |
| 附件 | `./file/download_qwen_image21_weights.py` | ModelScope 权重下载脚本 |
| 权重 | `D:\models\qwen-image-2.1\` | INT8 DiT + W4A8 TE + VAE（下载中） |
| 运行时 | `D:\ComfyUI_windows_portable\` | 已更新到含 Qwen-Image-2.1 的 master |

路径约定：以**本 job 文件所在目录**为基准的相对路径（`./` 当天、`../` 上级、`../../` 回到月层再进其他月/天）。

## 待办清单

- [x] 网络调研：确认 QwenImage 2.1 是否开源、发布渠道与许可证
- [x] 梳理模型能力：文生图/图生图、分辨率、提示词理解、中文场景等
- [x] 整理部署与生态：权重体积、推理框架、显存需求、在线体验入口
- [x] 沉淀调研结论到本 job（对比前代 / 适用建议）

## 进度记录

### 20:15 - 创建 job

按模板创建今日 `job1.md`，开始调研 QwenImage 2.1 开源版。

### 20:20 - 网络调研入口检查

- 已加载 `websearch` 技能；edition 默认引擎 Bing 中国，浏览器偏好 `iab`。
- **Browser Use/IAB 无法启动**：当前会话无 `agent.browsers` / `cua_repl`；`mimo-browser-use` 技能不存在；MCP 配置中也无 Browser Use 入口。
- 按 websearch 规则：不得静默改用 webfetch 做主检索路径，需先向用户说明并确认替代方案。
- **用户选定**：Playwright CLI 浏览器调研。

### 20:23 - SERP + 官方源读取（Playwright）

- Bing 中国 SERP（`QwenImage 2.1 open source text-to-image`）→ 打开官方 GitHub、发布博客、Comfy 页。
- **GitHub README**（https://github.com/QwenLM/Qwen-Image-2.1）：开源确认、架构、Quick Start、Day-0 生态、许可证声明。
- **LICENSE 全文**：Qwen Research License（2026-09-20），非商用 only。
- **发布解读**（qwenimages.com）：能力对比、Comfy 权重体积、许可证解读、与 2.0/3.0 差异。
- HuggingFace 直连超时（网络）；ModelScope/Comfy 页面抓取不完整，关键事实已由 GitHub + 博客交叉覆盖。

### 20:40 - 调研结论沉淀

- 完整结论写入 `./file/qwen-image-2.1-research.md`。
- 关键结论：
  1. **2026-09-20 正式开源**，官方名 **Qwen-Image-2.1**（非 QwenImage 2.1 商业 API 名混用）。
  2. **7B DiT + Qwen3-VL 8B + 64ch RGBA VAE**，文生图/编辑统一，原生 2K/RGBA/≤10 参考图。
  3. Diffusers/ComfyUI/vLLM/SGLang **Day-0**；Comfy BF16 扩散约 14.2GB、INT8 约 7.26GB。
  4. **Research License：研究可用，商用须单独授权** —— 选型红线。
  5. 附带 **PE-T2I / PE-I2I** 提示词改写模型（Qwen3.5-VL 9B）。

### 本地试跑结果（2026-09-22 深夜）

- **结论：8GB 卡本地试跑成功**
- 路径：ComfyUI 0.37.0 `--lowvram` + DiT **INT8 convrot** + TE **W4A8** + VAE BF16
- 参数：768×768 · 20 步 · euler/simple · cfg=1 · seed=42
- 输出：`D:\ComfyUI_windows_portable\ComfyUI\output\qwen21_local_8g_00001_.png`（约 846KB）
- 耗时：约 **30 分钟**（首次加载 + lowvram 换页；后续会快一些）
- 关键修复：
  1. `comfy_aimdo.storage` → 升级 aimdo 0.2.5→0.5.5
  2. `int8_linear(input_act_weight=...)` → **ops.py 兼容 shim**（过滤 kitchen 0.2.33 不认识的参数）
  3. GGUF 路径：ComfyUI-GGUF `detect_arch` 已补 `qwen_image21`（Q4_K_M 可作更省显存备选，本次未跑）
- Uncensored-GGUF：同构 INT4（4.05–4.6GB），**不作 job1 评估路径**

## 问题与阻塞

| 问题 | 状态 | 备注 |
|------|------|------|
| Browser Use/IAB 不可用 | 已解决 | 用户确认改走 Playwright CLI，完成 SERP→读页闭环 |
| HuggingFace 打开超时 | 已解决 | 以 GitHub/ModelScope/博客覆盖；HF 链接已记录 |
| Comfy/ModelScope 正文抽取不完整 | 已解决 | 关键参数来自官方 README + 发布博客交叉验证 |
| 本机 8GB 显存无法跑 BF16 | 已解决 | 选定 Comfy INT8 DiT + W4A8 TE + BF16 VAE |
| ComfyUI 0.35.0 无 2.1 节点 | 已解决 | git pull 到 master（含 qwen_image21 / TextEncodeQwenImage21） |
| comfy_aimdo 缺少 storage 模块 | 已解决 | 升级 comfy-aimdo 至 0.5.5 |
| 量化权重下载体积大/网络慢 | 进行中 | 后台续传 D:\models\qwen-image-2.1（INT8 DiT + W4A8 TE + VAE） |
| comfy-kitchen 0.2.35 升级慢 | 进行中 | 与权重下载争带宽；旧版 0.2.33 已含 int8_convrot/w4a8 dequant 能力 |

## 今日续做：量化版本确认 + 本地试跑（2026-09-21 晚）

### 设备与量化方案（已确认）

| 项 | 值 |
|----|----|
| GPU | RTX 3060 Ti **8GB** |
| RAM | 16GB（空闲约 6GB） |
| 磁盘 | D: 约 600GB 空闲 |
| 选定量化版 | **Comfy-Org：DiT INT8 convrot (7.26GB) + TE W4A8 (6.31GB) + VAE BF16 (0.68GB)** |
| 运行时 | `D:\ComfyUI_windows_portable` + `--lowvram` + `QwenImage21Cache(device=cpu,dtype=int8)` |
| 权重路径 | `D:\models\qwen-image-2.1\`（extra_model_paths.yaml 已配置） |
| 首跑参数 | 768×768 · 20 步 · euler/simple · cfg=1 · seed=42 |
| 不走路径 | Diffusers BF16 / SGLang 4090+ / LightX2V 5090 FP8 / FlagOS ARM |

### 已完成动作

1. 硬件盘点 + ModelScope 量化权重清单
2. 量化部署设计：`./file/qwen-image-2.1-local-quant-plan.md`
3. ComfyUI portable：`git pull` 至含 `qwen_image21` 的 master
4. 升级 `comfy-aimdo==0.5.5`（修复 `comfy_aimdo.storage` 导入）
5. 配置 `extra_model_paths.yaml` → `D:/models/qwen-image-2.1`
6. 启动权重后台续传；准备 API smoke workflow：`./file/qwen21_comfy_api_smoke.json`
7. 启动脚本：`./file/run_comfyui_lowvram.bat` · `./file/run_download_weights.bat`

### 本地试跑路径

```text
ComfyUI portable + lowvram
  ├─ UNETLoader: qwen_image_2.1_int8_convrot.safetensors
  ├─ CLIPLoader(type=qwen_image): qwen3vl_8b_w4a8.safetensors
  ├─ VAELoader: qwen_image_2.1_vae_bf16.safetensors
  ├─ QwenImage21Cache(device=cpu, dtype=int8)
  ├─ TextEncodeQwenImage21 → KSampler → VAEDecode → SaveImage
  └─ 输出前缀: qwen21_local_8g
```

## 附件（file/）

| 文件 | 说明 |
|------|------|
| `./file/qwen-image-2.1-research.md` | 完整调研结论（架构/能力/生态/许可证/对比/上手） |

## 大文件索引（archive）

| 日期 | 存档路径 | 用途 / 说明 |
|------|----------|-------------|
| | | |

## 相关链接

- 官方仓库: https://github.com/QwenLM/Qwen-Image-2.1
- 许可证: https://github.com/QwenLM/Qwen-Image-2.1/blob/main/LICENSE
- ModelScope: https://www.modelscope.cn/models/Qwen/Qwen-Image-2.1
- HuggingFace: https://huggingface.co/Qwen/Qwen-Image-2.1 （调研时超时）
- 发布解读: https://qwenimages.com/zh/blog/qwen-image-2-1-release
- Comfy: https://comfy.org/zh-CN/qwen-image-2.1

## 明日计划 / 后续跟进

- [ ] 视硬件决定是否本地试跑（Diffusers 或 ComfyUI；低配用 INT8 / CPU offload）
- [ ] 若有商用意向：评估是否申请商业授权（model-business@notice.qwencloud.com）
- [ ] 可选：与 Qwen Image 3.0 产品向能力做场景选型对比

## 变更记录

| 时间 | 变更说明 |
|------|----------|
| 2026-09-21 | 创建 job1；启动 QwenImage 2.1 开源版调研 |
| 2026-09-21 | Browser Use 不可用→用户确认 Playwright CLI；完成 SERP 与官方源调研 |
| 2026-09-21 | 结论写入 file/qwen-image-2.1-research.md；状态改为已完成 |
| 2026-09-21 晚 | 续做本地量化：确认 8GB 方案 INT8 DiT + W4A8 TE；更新 ComfyUI；修 aimdo；权重后台下载中 |
| 2026-09-22 | 权重齐（INT8/W4A8/VAE/Q4_K_M）；GGUF 架构未识别→补丁；INT8 卡 kitchen API；补装 comfy-kitchen 0.2.35 后自动重跑 |
| 2026-09-22 深夜 | **本地试跑成功**：INT8+W4A8+lowvram 出图；ops.py kitchen 兼容 shim；结果与耗时写入 job1 |
| 2026-09-21 22:20 | 新建 job2 续做：官方提示词模板 + 美女低分辨率批图 |

## 附件（file/）

| 文件 | 说明 |
|------|------|
| | |

## 大文件索引（archive）

| 日期 | 存档路径 | 用途 / 说明 |
|------|----------|-------------|
| | | |

## 相关链接

- PR / Issue:
- 文档:
- 日志/监控:

## 明日计划 / 后续跟进

- [ ] 视调研结果决定是否做本地部署试跑 / API 接入验证

## 变更记录

| 时间 | 变更说明 |
|------|----------|
| 2026-09-21 | 创建 job1；启动 QwenImage 2.1 开源版调研 |
