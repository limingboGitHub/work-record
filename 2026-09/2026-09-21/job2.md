# Job: WAI-V3 美女主题低分辨率批图（官方提示词模板）

## 基本信息

| 字段 | 内容 |
|------|------|
| 日期 | 2026-09-21 |
| 项目/模块 | 文生图 / WAI-Mature-illustrious V3 |
| 状态 | 已完成（512 批 + 高清化 + 已入相册） |
| 预估耗时 | 30 min |
| 实际耗时 | ~5 min（Comfy 已起后） |
| 关联字 | #文生图 #WAI-Mature-illustrious #官方提示词 #美女 #低分辨率 #ComfyUI |

## 任务描述

> 新建 job：**继续用之前的文生图模型 WAI-Mature-illustrious V3**（非 Qwen-Image-2.1），严格套用官方提示词模板，主题「美女」、风格自由发挥，**低分辨率先跑一批**验收。

## 关联工作（文件索引）

| 关系 | 文件路径 | 说明 |
|------|----------|------|
| 前序（模型/工作流/参数） | `../../2026-09-10/job2.md` | WAI-V3 安装、官方模板、512/720/864/1024 实测 |
| 前序（美女向批图流程） | `../../2026-09-10/job3.md` | 国风/瑜伽裤/沙滩等 512 抽卡流程 |
| 误建（本日） | `./job1.md` | Qwen-Image-2.1 调研（**不是本次出图模型**） |
| 误建（本日） | `./file/run_beauty_batch.py` 等 | 已停用的 Qwen 批图脚本 |
| 生成脚本 | `../../../work_record_temp/2026-09/2026-09-21/scripts/gen_beauty_wai512.py` | 本批 WAI 美女 512 批图 |
| 输出目录 | `../../../work_record_temp/2026-09/2026-09-21/output/wai_samples/beauty512/` | 低分辨率成图 + summary |
| Checkpoint | `D:\ComfyUI_windows_portable\ComfyUI\models\checkpoints\waiMatureIllustrious_v30.safetensors` | 已安装 |

## 官方提示词模板（严格使用，不改不加）

来源：WAI-Mature-illustrious V3 模型说明 / job2 笔记。

```text
Positive: masterpiece, best quality, amazing quality,
Negative: bad quality, worst quality, worst detail, sketch, censor,
```

本批拼装规则：

```text
正面 = masterpiece, best quality, amazing quality, 1girl, solo, <风格场景>
负面 = bad quality, worst quality, worst detail, sketch, censor,
```

- **仅使用官方质量词**作为固定前后缀；中间只写主体/风格描述。
- **不混入** `random_promt.txt`（本批不自动拼 NSFW 行）。
- 采样参数沿用 job2/job3 已验证组合。

## 出图参数（低分辨率首跑）

| 参数 | 值 | 依据 |
|------|-----|------|
| Checkpoint | `waiMatureIllustrious_v30.safetensors` | 之前实际在用 |
| 分辨率 | **512×512** | 用户要求低分辨率先跑；≈13s/张 |
| Steps / CFG | **24 / 6.0** | 官方推荐 + 本机已验证 |
| Sampler / Scheduler | **dpmpp_2m / karras** | 同上 |
| 构图 | 1girl, solo + 风格自由 | 主体美女 |
| Seed | 每张随机 | 抽卡 |

## 风格清单（自由发挥，10 组）

| ID | 键 | 风格 |
|----|----|------|
| 01 | soft_window | 自然窗光肖像 |
| 02 | gothic_lace | 哥特蕾丝 |
| 03 | cyber_neon | 赛博霓虹 |
| 04 | hanfu_spring | 汉服春日 |
| 05 | office_chic | 职场干练 |
| 06 | cafe_latte | 咖啡馆休闲 |
| 07 | ice_queen | 冰雪女王幻想 |
| 08 | street_fashion | 都市街拍 |
| 09 | library_soft | 图书馆知性 |
| 10 | rooftop_dusk | 天台黄昏 |

## 待办清单

- [x] 纠正模型：确认为 WAI-Mature-illustrious V3，停用 Qwen 批图 runner
- [x] 固化官方提示词模板与参数
- [x] 启动 ComfyUI（`run_nvidia_gpu.bat`）
- [x] 跑完 512×512 美女批 10/10
- [x] 方案 B 高清化 1024×1024 10/10
- [x] 成片保存常驻相册
- [x] 办公室风格 + random_promt 组合 512 批 10/10
- [x] office_rand512 高清化 1024 10/10
- [x] office hdb 已入常驻相册

## 进度记录

### 22:25 - 模型纠正

- 用户指出「不是这个模型」；查 `2026-09-10/job2.md` + `job3.md`：实际在用 **WAI-Mature-illustrious V3**。
- 官方模板：`masterpiece, best quality, amazing quality,` / `bad quality, worst quality, worst detail, sketch, censor,`
- 已停用本日误建的 Qwen-Image-2.1 批图 runner（权重下载可继续，与本 job 无关）。
- 本 job 改为 WAI-V3 + 官方模板 + 美女 + 512 低分辨率批。

### 22:25–22:28 - 512×512 美女批 10/10 完成

- 模型：`waiMatureIllustrious_v30.safetensors`
- 官方模板（严格）：正 `masterpiece, best quality, amazing quality,` / 负 `bad quality, worst quality, worst detail, sketch, censor,`
- 参数：512×512 · Steps24 · CFG6 · dpmpp_2m · karras · 每张随机 seed · **未混** random_promt
- 耗时：首张含加载 **86.7s**，其后稳定 **15.2–16.7s/张**
- 输出：`G:\project\work_record_temp\2026-09\2026-09-21\output\wai_samples\beauty512\`
- 摘要：同目录 `summary_beauty512.json`（副本 `./file/beauty_wai512_summary.json`）
- 风格：soft_window / gothic_lace / cyber_neon / hanfu_spring / office_chic / cafe_latte / ice_queen / street_fashion / library_soft / rooftop_dusk
- 状态：**512 批用户验收通过** → 已做方案 B 高清化。

### 22:42–22:48 - 方案 B 高清化 1024×1024（10/10）

- 方法：`ImageScale bicubic` → img2img **denoise 0.42 / steps 16**（沿用 job3 方案 B）
- 同源 512 批 seed / prompt / 官方负面词
- 输出：`.../beauty512/beauty512_hdb/beauty512_hdb_*.png`
- 摘要：`summary_beauty512_hdb.json`（副本 `./file/beauty_hdb_summary.json`）
- 耗时：首两张 ~56s，其余稳定 **~36s/张**；合计约 6.7 min
- 状态：**待验收**

### 22:57–23:00 - 办公室风格 + random_promt 组合 512 批（10/10）

- 用户选定：沿用 beauty512 的 **office** 风格提示词，与 `~/Downloads/random_promt.txt` 组合
- 提示词顺序：`官方质量词 + office 风格 + random_promt`（random 置后，同沙滩批约定）
- 参数：512×512 · Steps24 · CFG6 · dpmpp_2m/karras · 新随机 seed
- random_promt：4 行轮转配对 10 张（内容不写入 job）
- 输出：`.../wai_samples/office_rand512/office_rand512_01..10_office.png`
- 摘要：`summary_office_rand512.json`（副本 `./file/office_rand512_summary.json`）
- 脚本：`../../../work_record_temp/2026-09/2026-09-21/scripts/gen_office_rand512.py`
- 耗时：~15s/张；**10/10 成功**
- 状态：**低分辨率已验收** → 已高清化。

### 23:02–23:09 - office_rand512 方案 B 高清化 1024（10/10）

- 方法：`ImageScale bicubic` → img2img **d0.42 / steps16**
- 同源 seed / prompt（含 random_promt 混配）/ 官方负面
- 输出：`.../office_rand512/office_rand512_hdb/office_rand512_hdb_*.png`
- 摘要：`summary_office_rand512_hdb.json`（副本 `./file/office_hdb_summary.json`）
- 耗时：~38s/张；**10/10 成功**
- 状态：**待验收 / 可入相册**

## 问题与阻塞

| 问题 | 状态 | 备注 |
|------|------|------|
| 误用 Qwen-Image-2.1 | 已纠正 | 权重仍在后台下，但不作为本次出图模型 |
| ComfyUI 未启动 | 待启动 | `run_nvidia_gpu.bat` |
| random_promt 含 NSFW 行 | 本批不用 | 严格官方质量词；如需混入用户可再说 |

## 附件（file/）

| 文件 | 说明 |
|------|------|
| | 成图与 summary 在 temp，不进 git |

## 大文件索引（archive）

| 日期 | 存档路径 | 用途 / 说明 |
|------|----------|-------------|
| 2026-09-21 | `../../../work_record_archive/albums/beauty_hdb_01_*.png` … `beauty_hdb_10_*.png` | 常驻扁平相册：美女 1024×1024 高清成片 10 张 |
| 2026-09-21 | `../../../work_record_archive/albums/meta_2026-09-21_beauty512_hdb.json` | 美女批 seed / prompt 追溯 |
| 2026-09-21 | `../../../work_record_archive/albums/office_hdb_01_*.png` … `office_hdb_10_*.png` | 办公室+random 批 1024×1024 高清成片 10 张 |
| 2026-09-21 | `../../../work_record_archive/albums/meta_2026-09-21_office_rand512_hdb.json` | 办公室批 seed / prompt 追溯 |

> 相册规则：扁平单目录、不删旧图、只放验收通过成片。中间批（512 原图）仍留在 temp，不进相册。

## 相关链接

- 前序 job: `../../2026-09-10/job2.md`
- Checkpoint: `waiMatureIllustrious_v30.safetensors`

## 明日计划 / 后续跟进

- [ ] 验收 512 批后，可选升 720 或 512×768 竖幅全身
- [ ] 效果好的风格沉淀进提示词库

## 变更记录

| 时间 | 变更说明 |
|------|----------|
| 2026-09-21 22:20 | 初建 job2（误用 Qwen-Image-2.1） |
| 2026-09-21 22:25 | **纠正为 WAI-Mature-illustrious V3**；严格官方模板；美女 512 批准备中 |
| 2026-09-21 22:28 | 512×512 美女批 10/10 成功，用户验收通过 |
| 2026-09-21 22:48 | 方案 B 高清化 1024×1024 10/10 → beauty512_hdb/ |
| 2026-09-21 | 用户要求保存常驻相册：10 张 hdb 已拷入 `work_record_archive/albums/`（`beauty_hdb_*`）+ meta JSON |
| 2026-09-21 23:00 | 办公室风格 + random_promt 组合 512 批 10/10 → office_rand512/ |
| 2026-09-21 23:09 | office_rand512 方案 B 高清化 1024 10/10 → office_rand512_hdb/ |
| 2026-09-21 | office hdb 10 张已拷入常驻相册 `office_hdb_*` + meta JSON |
