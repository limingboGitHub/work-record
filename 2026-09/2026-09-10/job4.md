# Job: 文字九州修仙 —— 境界效果改名与说明精简（含弹窗布局修复）

## 基本信息

| 字段 | 内容 |
|------|------|
| 日期 | 2026-09-10 |
| 项目/模块 | 文字九州修仙（godot / text-turn-game，工程名 TextTurnGame） |
| 状态 | 已完成（19:30 已推送 `f889a799`；仅剩真机验收） |
| 预估耗时 | 0.5h |
| 实际耗时 | ~0.8h |
| 关键字 | #文字九州修仙 #TextTurnGame #godot #需求开发 #境界弹窗 #文案改名 #布局修复 #文字贴边 |

## 任务描述

> 1）境界弹窗「突破神通」短名改名：筑基→道基渐稳、金丹→金丹固法、元婴→元婴护体；
> 2）精简冗余说明：炼气「五行初启」只留「五行点数+5」；炼虚「虚境归元」去掉「（免疫一切伤害），仅可触发一次」；
> 3）修复布局：上次加大天阶高度后，下方组件未相应下移、容器高度未增加，天阶面板与底部面板贴靠。

## 关联工作（文件索引）

| 关系 | 文件路径 | 说明 |
|------|----------|------|
| 前序（续做来源） | `./job3.md` | 同项目的前置 job：定位项目、拉取代码、启动主场景截图验证 |
| 后续（续做去向） | —— | 本 job 已闭环（需求实现 + 自测 + 提交 + push），无跨天续做；仅剩设备真机验收待确认 |

## 待办清单

- [x] 同步最新代码（`origin/master` → `f8860cd1`）
- [x] 记录本次拉取带来的变更，便于判断是否影响后续开发
- [x] 明确需求内容与验收标准（**境界效果名称修改** + 说明精简 + 布局修复，见「任务描述」）
- [x] 定位需求涉及的模块 / 文件（`assets/text/text.csv`、`src/ui/stage_dialog_control.*`、两个父弹窗）
- [x] 实现改动（文案 7 处 + 布局 4 处）
- [x] 自测：重编译翻译 + StageUITest 101 checks + RealmTest 73 checks + 布局探针/像素核对
- [x] 收尾：更新本 job、本地提交 `da29ca1b`、`62bceb7d`、`f889a799`（19:30 已全部 push 到 gitee）

## 进度记录

### 18:15 - 收到需求：境界效果名称修改

用户提出「境界效果的名称修改」，但仅给出标题、未给出具体新名称。已排查现状（基线 `f8860cd1`）：

| 境界 | 等级段 | 短名 key | 当前名称 | 说明 key |
|------|--------|----------|----------|----------|
| 0 凡人 | 0-9 | `STAGE_UNLOCK_NONE` | 无 | `STAGE_UNLOCK_NONE_DESC` |
| 1 炼气期 | 10-19 | `STAGE_UNLOCK_1` | 五行初启 | `STAGE_UNLOCK_1_DESC` |
| 2 筑基期 | 20-29 | `STAGE_UNLOCK_2` / `_PET` | 灵兽随行 / 灵体初固 | `STAGE_UNLOCK_2(_PET)_DESC` |
| 3 金丹期 | 30-39 | `STAGE_UNLOCK_3` | 万法归宗 | `STAGE_UNLOCK_3_DESC` |
| 4 元婴期 | 40-49 | `STAGE_UNLOCK_4` | 元婴复活（=`ATTRIBUTE_YUANYING_REVIVE`） | `ATTRIBUTE_YUANYING_REVIVE_DESC` |
| 5 化神期 | 50-59 | `STAGE_UNLOCK_5` / `_PET` | 元神出窍 / 灵性通神 | `ATTRIBUTE_YUANYING_CHUQIAO_DESC` |
| 6 炼虚期 | 60-69 | `STAGE_UNLOCK_6` | 虚境归元（=`ATTRIBUTE_LIANXU_INVINCIBLE`） | `ATTRIBUTE_LIANXU_INVINCIBLE_DESC` |
| 7 合体期 | 70-79 | `STAGE_UNLOCK_HETI` / `_PET` | 元神归位 / 合体传承 | `ATTRIBUTE_HETI_GUIWEI(_CHUANCHENG)_DESC` |
| 8 大乘期 | 80-89 | `STAGE_UNLOCK_DACHENG` / `_PET` | 万兽朝宗 / 灵兽大成 | `STAGE_UNLOCK_DACHENG(_PET)_DESC` |
| 9 渡劫期 | 90-99 | `STAGE_UNLOCK_DUJIE` | 五气朝元（=`ATTRIBUTE_WUQI_CHAOYUAN`） | `ATTRIBUTE_WUQI_CHAOYUAN_DESC` |
| 10 飞升 | 100+ | `STAGE_UNLOCK_FEISHENG` | 飞升蕴灵（=`ATTRIBUTE_FEISHENG_YUNLING`） | `ATTRIBUTE_FEISHENG_YUNLING_DESC` |

改名影响面（待新名称确认后同步）：

| 文件 | 用途 |
|------|------|
| `assets/text/text.csv` | 文案源（`STAGE_UNLOCK_*`、`ATTRIBUTE_*`），改后需重编译 `.translation` |
| `src/tools/combat_init_tool.gd` | 战斗层境界效果挂接（名称/ID 若硬编码需同步） |
| `src/data/combat/data_combat_character.gd` | `ASCENSION_BUFF_ID` 的 buff 名「飞升蕴灵」硬编码 |
| `src/test/ui/test_stage_dialog_100.gd` | 断言了各短名文案，改名后需同步 |
| `src/test/system/realm_effects_combat_test.gd` | 「飞升蕴灵」用例断言 |
| `docs/realm_stage_e2e_test_plan.md` | C5 用例名 |

**待用户提供：需要改哪几个境界的名称、改成什么。**

### 18:25 - 用户再次提出「境界效果的名称修改」

仍未给出具体新名称，已把当前「突破神通」短名清单（见上表）回发用户，请其给出「旧名 → 新名」对照表；拿到后按上表逐项改文案并同步测试断言。

### 18:32 - 【缺陷】消息被截断：Agent 只收到首行，多行内容丢失

用户反馈「内容已发过去」，比对 `work_record_temp/2026-09/2026-09-10/output/cc-connect-stdout.log` 确认：

| 项 | 值 |
|----|----|
| 飞书消息 id | `om_x100b651c1c23a0a4b3c5a3b459e2763`（create_time 1789035823049，18:23:42 收到） |
| cc-connect 侧收到 | `content_len=448`（UTF-8 字节），多行文本完整落在日志 payload 里 |
| Agent 实际收到 | 仅第一行「境界效果的名称修改」，**换行后的全部内容丢失** |
| 复现 | 18:14 那条同样多行的消息（`om_x100b651c7eed0ca4b2a0f1e9ab34468`，content_len=451）也只到首行——两次 `turn complete` 的 response 都在问「新名称是什么」 |

结论：**cc-connect → Agent CLI 传参环节在换行处截断**（疑似单行 argv / shell 转义所致），跨轮稳定复现；影响所有多行需求描述。后续发需求建议单行发送，或修复链路后重测。

从日志恢复出的**需求原文**（与原消息逐字一致；用户第二次发送时把半角逗号换成了全角逗号，文字内容相同）：

> 境界效果的名称修改
> 筑基，道基渐稳
> 金丹，金丹固法
> 元婴，元婴护体
>
> 五行初启，五行点数+5（后面的描述删除）
> 虚境归元，免疫一切伤害及后面内容都不用，冗余了
>
> 上一次调整了境界阶段的高度以后，下方的组件没有对应下移，以及整个容器高度应该也要增加，否则，否则你当前这个组件的高度增加了以后，和下面的组件碰到一起了

### 18:35 - 需求对齐并开工

用户回「按照你的理解做」，按如下理解实施（范围内 4 件事）：

1. 境界弹窗短名改名：筑基「灵兽随行」→ **道基渐稳**、金丹「万法归宗」→ **金丹固法**、元婴「元婴复活」→ **元婴护体**；宠物侧（灵体初固/灵性通神/合体传承/灵兽大成）不动。
2. 炼气说明 `STAGE_UNLOCK_1_DESC`：`五行点数+5，可在属性界面强化五行` → **`五行点数+5`**。
3. 炼虚说明 `ATTRIBUTE_LIANXU_INVINCIBLE_DESC`：删掉「（免疫一切伤害），仅可触发一次」（「5秒无敌」已含此意）→ **`血量首次降至30%以下时，获得5秒无敌`**。
4. 布局：天阶区加高后与底部面板贴靠，需给足高度并把下方组件下移、加大容器总高。

### 18:45 - 实现：文案 + 布局

文案（`assets/text/text.csv`，7 处）：

| key | 旧 | 新 |
|-----|----|----|
| `STAGE_UNLOCK_2` | 灵兽随行 | 道基渐稳 |
| `STAGE_UNLOCK_3` | 万法归宗 | 金丹固法 |
| `STAGE_UNLOCK_4` | 元婴复活 | 元婴护体 |
| `ATTRIBUTE_YUANYING_REVIVE` | 元婴复活 | 元婴护体 |
| `EFFECT_100042_NAME` | 元婴复活 | 元婴护体 |
| `ATTRIBUTE_LIANXU_INVINCIBLE_DESC` | 血量首次降至30%以下时，获得5秒无敌（免疫一切伤害），仅可触发一次 | 血量首次降至30%以下时，获得5秒无敌 |
| `STAGE_UNLOCK_1_DESC` | 五行点数+5，可在属性界面强化五行 | 五行点数+5 |

> 元婴效果有四处名字（境界卡短名 / 属性帮助·境界分区 / `effect_100042` buff 名 / 战斗复活播报硬编码）。本次把用户可见的前三处统一为「元婴护体」，避免同一效果两处叫法不一致；战斗内部标识 `effect_100042` 不变。

布局（真实原因：**面板被自身最小尺寸顶出去**）：

| 文件 | 改动 |
|------|------|
| `src/ui/stage_dialog_control.tscn` | 天阶面板/卡组区高 352→**356**（11 行×32 内容实需 356，原先只给 352 导致 PanelContainer 被撑到 356、底边压到 426 贴住面板）；底部面板 428..618 → **438..628**；弹窗 620x**640**（原 628） |
| `src/ui/stage_dialog_control.gd` | 卡组中心 `ZONE_CENTER` y 176→**178**（卡组区 356 取中）；`STAGE_REWARDS` 注释补新短名 |
| `src/ui/attribute_dialog_control.tscn` | 内嵌境界弹窗偏移 250→**238**（底边仍与属性弹窗 878 对齐） |
| `src/ui/pet_attri_dialog_control.tscn` | 内嵌偏移 ±314 → **±320**（仍垂直居中） |

结果：天阶底到面板顶 **12px**、卡组底到面板顶 **12px**，弹窗下边距 12px（原先天阶面板底边与底部面板仅 2px）。

### 18:55 - 自测与验证

| 项 | 命令 / 方式 | 结果 |
|----|-------------|------|
| 重编译翻译 | `godot --headless --path . --import` | `assets/text/text.zh_CN.translation` 重编译；新文案命中、旧文案（灵兽随行/万法归宗/仅可触发一次/可在属性界面强化五行）0 命中 |
| 境界弹窗 UI 断言 | `godot --path . --headless -- --e2e-stage-dialog` | **ALL PASS (101 checks)**（原 91 项，新增布局不碰撞 6 项 + 元婴短名/说明精简 3 项） |
| 境界效果战斗层回归 | `--e2e-realm-test` | **ALL PASS (73 checks)**，无 `SCRIPT ERROR` |
| 布局探针 | 临时场景（已删）打印各组件 rect | 独立弹窗 root=620x640；天阶/卡组 70..426（356）；底部面板 438..628；间距 12px |
| 真实挂载路径 | 属性弹窗内嵌境界弹窗 screenshot + rect 核对 | 境界弹窗底边绝对 878 == 属性弹窗底边 878，内嵌无溢出 |
| 像素核对 | 对截图列向采样 | 天阶面板底边与底部面板顶边之间是对话框背景，存在可辨间隙 |
| 视觉产物 | `test_stage_dialog_screenshot.gd`（裁剪区 496x503→496x512） | 5 张截图重生成；另出内嵌属性弹窗图，已发飞书 |

### 19:30 - 推送远端

用户回复「推送」，执行 `git fetch --prune origin` + `git push origin master`：

| 项 | 值 |
|----|-----|
| 推送前远端 | `da29ca1b`（比预期早一步：`da29ca1b` 已在远端，不是仅本地） |
| 推送 | `da29ca1b..f889a799  master -> master`（`62bceb7d`、`f889a799` 两个新提） |
| 推送后 | `origin/master` = `f889a799`，工作区干净（仅遗留未跟踪 `update_code.sh`） |
| 待办 | 设备真机验收（如需：`bash sync_android.sh`） |

### 19:20 - 追加修复：合体说明去前缀 + 满级不再隐藏经验百分比

用户追加两项反馈，均已修复并提交 **`f889a799`**：

| # | 反馈 | 定位 | 修复 |
|---|------|------|------|
| 2 | 人物/宠物的合体描述不要「（人物）/（宠物）」前缀 | `assets/text/text.csv` 的 `ATTRIBUTE_HETI_GUIWEI_DESC`（人物）、`ATTRIBUTE_HETI_CHUANCHENG_DESC`（宠物） | 删除前缀；人物/宠物由卡组变体（`STAGE_UNLOCK_HETI` vs `_PET`）与短名（元神归位/合体传承）区分，前缀冗余 |
| 3 | 满级后经验槽右侧文本被隐藏，不需要隐藏 | `src/ui/stage_dialog_control.gd` `check_and_handle_level_max()` 里 `exp_percent_label.hide()` | 删除 hide/show，满级时「经验：x%」照常显示 |

自测：

| 项 | 结果 |
|----|------|
| 重编译翻译 | `godot --headless --path . --import`；`.translation` 中「（人物）/（宠物）」命中数 **0** |
| UI 断言 | 新增 `pet85_heti_desc_no_prefix`、`human85_heti_desc_no_prefix`、`lv100_exp_percent_text_kept`（并把 `lv100_exp_percent_hidden` 反转为 `visible`）→ **ALL PASS (110 checks)** |
| 境界效果战斗层回归 | `--e2e-realm-test` **ALL PASS (73 checks)** |
| 截图像素核对 | lv100 经验文本区（dialog x462..602, y444..470）现有文字像素 74 个（修复前该区无文字）；lv53 对照 94 个 |
| 备注 | 满级时文本显示的是自然计算结果（测试人物为空经验→`经验：0%`；实战中为槽内实际比例） |

### 19:12 - 追加修复：卡片「境界突破描述」文字右侧贴边

用户反馈「卡片中的境界突破描述右边需要留点边距，否则右边贴边了」。定位为坐标叠加缺陷：

| 项 | 值 |
|----|-----|
| 现象 | 卡内说明文字左侧有 16px 留白、右侧 0px，长行/换行后的文字紧贴卡片右边框 |
| 原因 | `_build_stage_cards()` 里三行 Label 的 `position.x = 8`，而父 `content` 已被 PanelContainer 的 `content_margin_left = 8` 内缩——8+8 叠加到左侧，右侧因此归零 |
| 修复 | 抽出 `CARD_PADDING := 8.0` 常量（同时用于 `content_margin_left/right` 与 `inner_width = CARD_SIZE.x - CARD_PADDING*2`），三行 Label 的 `position.x` 改为 **0** |
| 副带效果 | 境界名/神通短名原中心偏右 8px，现回到卡片正中（卡中心 x=182） |

自测：

| 项 | 结果 |
|----|------|
| 布局断言（新增 6 项） | 修复前 `左/右边距 = 16.0/0.0 px`（3 项 fail）；修复后 `8.0/8.0 px`，**StageUITest ALL PASS (107 checks)**（101→107） |
| 境界效果战斗层回归 | `--e2e-realm-test` **ALL PASS (73 checks)** |
| 截图像素核对（496x512，0.8 缩放） | lv100 满级卡文字区最右列距右边框 10.0 逻辑px（左右对称）；lv53 左/右 16.2/13.8 px，均不再贴边 |
| 截图重生成 | `test_stage_dialog_screenshot.gd` 5 张（另 5 张未变：`6_attr_dialog_embedded.png` 非本次脚本输出，未重跑） |

提交：**`62bceb7d`** `fix(境界): 境界卡说明文字右侧贴边——子节点坐标与 content_margin 叠加`（2 files changed，本地提交，未 push）。

### 19:05 - 提交

| 项 | 值 |
|----|-----|
| 提交 | **`da29ca1b`** feat(境界): 境界效果改名与说明精简，并修复天阶面板挤压底部面板 |
| 范围 | 7 files changed（`text.csv`、`stage_dialog_control.gd/.tscn`、`attribute_dialog_control.tscn`、`pet_attri_dialog_control.tscn`、2 个测试） |
| 状态 | 仅本地提交，**未 push**（待用户确认后 push 到 gitee / 同步到 Android 设备） |

### 18:12 - 同步最新代码

| 项 | 值 |
|----|-----|
| 项目 | `D:\godot\projects\text-turn-game` |
| 远程 | `origin` = https://gitee.com/sdf2311d/text-turn-game.git |
| 分支 | `master`（跟踪 `origin/master`） |
| 操作 | `git fetch --prune origin` → `git pull --ff-only` |
| 结果 | 快进 **`9611edad` → `f8860cd1`**（落后 5 个提交，已拉全，无冲突） |
| 变更量 | 21 files changed, **+498 / −2281** |
| 工作区 | 干净；仅遗留未跟踪 `update_code.sh`（Termux 端同步脚本，见 job3） |
| 引擎 | 本机 `D:\godot\Godot_v4.6.1-stable_win64.exe`（4.6.1.stable） |

本次拉到的 5 个提交（新 → 旧）：

| 提交 | 说明 | 影响面 |
|------|------|--------|
| `f8860cd1` | style(境界): 卡片再加宽加高、行高放宽，并为低境界补四字神通名 | `stage_dialog_control.gd/.tscn`、`assets/text/text.csv`、测试 |
| `803ebadf` | style(境界): 天阶收窄放大字体，卡片加宽放大字号并一屏五张 | `stage_dialog_control.gd/.tscn` |
| `9818679d` | docs(同步): 补充设备端强制同步脚本与 /sdcard cwd 故障处理 | `ANDROID_SYNC.md` |
| `c27d7efa` | chore: 本地脚本与工具目录不再纳入版本控制 | `.gitignore`（新增 `/scripts/`、`.zcode/` 忽略），删除 11 个 `scripts/*.js|py` |
| `b08b35b9` | feat(境界): 弹窗卡片减半并改为自由拖动吸附，天阶恢复固定高亮 | `stage_dialog_control.gd/.tscn`、`attribute_dialog_control.tscn`、`pet_attri_dialog_control.tscn`、测试 |

值得注意的点（对后续开发有影响）：

1. **境界弹窗（`src/ui/stage_dialog_control.gd/.tscn`）正在密集迭代**：连续 3 个提交都在改它（拖动吸附、一屏五张、字号/卡片尺寸）。若新需求涉及境界/神通界面，需以 `f8860cd1` 为基线，避免与在改动线冲突。
2. **`/scripts/` 已移出版本控制**：本地一次性数据修补脚本、设备同步脚本仅本地保留；新写的一次性脚本不要再提交（放本地或被忽略目录）。
3. **`.uid` / `.import` 必须入库**（`.gitignore` 顶部有说明）：跨设备 UID 不一致会导致字体等资源加载失败——涉及新增资源时要连 `.import`/`.uid` 一起提交。
4. 设备侧同步看 `ANDROID_SYNC.md`（本次补充了强制同步与 `/sdcard` cwd 故障处理）。

## 问题与阻塞

| 问题 | 状态 | 备注 |
|------|------|------|
| cc-connect 多行消息在换行处截断 | 未解决（链路缺陷） | 见 18:32 条目；本次靠读 cc-connect 日志恢复需求原文。给需求时建议单行发送 |
| 真机/设备验收未做 | 待用户确认 | 本机已验证（断言 + 截图）；设备侧如需验收，用 `bash sync_android.sh` |
| 仓库根遗留未跟踪 `update_code.sh` | 未解决 | Termux 端脚本，本机无用；待确认删除或加入 `.gitignore`（项目侧 `.gitignore` 由项目自行管理） |

## 附件（file/）

| 文件 | 说明 |
|------|------|
| `./file/stage-dialog-names-620x640.png` | lv100 满级弹窗：11 张卡全部解锁，可见新短名（道基渐稳/金丹固法/元婴护体）与精简后的说明 |
| `./file/stage-dialog-layout-gap.png` | lv53 弹窗：天阶/卡组区与底部面板留 12px 间距（布局修复验收图） |
| `./file/stage-dialog-card-desc-padding.png` | lv100 满级弹窗（`4_lv100_max.png`）：卡片说明文字左右各留 8px，不再贴右边框 |
| `./file/stage-dialog-exp-label-max.png` | lv100 满级弹窗：经验槽右侧「经验：x%」不再隐藏（修复 3 验收图） |
| `./file/stage-dialog-heti-no-prefix.png` | 宠物 lv85 弹窗：合体说明已无「（宠物）」前缀（修复 2 验收图） |

## 大文件索引（archive）

| 日期 | 存档路径 | 用途 / 说明 |
|------|----------|-------------|
| | | |

## 相关链接

- PR / Issue:
- 文档: 项目内 `README.md`、`ANDROID_SYNC.md`；引擎 Godot 4.6 文档 https://docs.godotengine.org
- 日志/监控: 运行日志落在项目 `user://logs`（`project.godot` 开启 file_logging，最多 3 个）

## 明日计划 / 后续跟进

- [x] 征得用户同意后 `git push origin master`（`f889a799`；`da29ca1b` 推送前已在远端）；仍待按需 `bash sync_android.sh` 同步到设备真机验收
- [ ] 若用户只想要境界弹窗改名、不希望动属性帮助/buff 名，回滚 `ATTRIBUTE_YUANYING_REVIVE`、`EFFECT_100042_NAME` 两处（改回「元婴复活」即可）
- [ ] cc-connect 多行消息截断问题：另开 job 定位修复（换行处丢内容）
- [ ] 需求做完/未做完时的跨天衔接：新建当天 `jobN.md`，与本文件在「关联工作」互指

## 变更记录

| 时间 | 变更说明 |
|------|----------|
| 2026-09-10 18:12 | 创建 job（新需求开发），完成开工前的代码同步：`9611edad` → `f8860cd1` |
| 2026-09-10 18:25 | 用户复述需求「境界效果名称修改」，仍缺具体新名称；已回发现状清单待其确认对照表 |
| 2026-09-10 18:32 | 发现并定位「多行消息被截断」链路缺陷；从 cc-connect 日志恢复需求原文 |
| 2026-09-10 19:05 | 需求实现完成（文案 7 处 + 布局 4 处），自测全绿，本地提交 `da29ca1b`；job 收尾 |
| 2026-09-10 19:30 | `git push origin master`：`da29ca1b..f889a799`（两个修复提已上远端），job 收尾 |
| 2026-09-10 19:20 | 追加修复：合体说明去「（人物）/（宠物）」前缀；满级后不再隐藏经验百分比，断言 107→110，提交 `f889a799` |
| 2026-09-10 19:12 | 追加修复：卡片说明文字右侧贴边（position.x 与 content_margin 叠加），新增 6 项布局断言，提交 `62bceb7d` |
