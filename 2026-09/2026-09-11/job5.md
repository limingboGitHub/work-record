# Job: 文字九州修仙 —— 【通明】触发条件改为「宠物等级 > 50」

## 基本信息

| 字段 | 内容 |
|------|------|
| 日期 | 2026-09-11 |
| 项目/模块 | 文字九州修仙（godot / text-turn-game，工程名 TextTurnGame）—— 技能熟练度 / 【通明】 |
| 状态 | 已完成（已 push：`origin/master` = `f98866f7`；真机验收待设备） |
| 预估耗时 | 0.5h |
| 实际耗时 | ~30min（15:35~16:05，含 rebase 远端新提交与回归） |
| 关键字 | #文字九州修仙 #TextTurnGame #godot #技能熟练度 #通明 #宠物 #数值平衡 #战斗 |

## 任务描述

> 用户需求：「取消之前最高等级减少10级获得通明状态的设定，改成当宠物大于 50 级时，获得通明状态。其他不变。」

即把【通明】（技能熟练度 ×20）的触发条件从**「角色等级 ≥ 等级上限 − 9」**（当前等级上限 100 → 阈值 91）改为**「宠物等级 > 50」**；倍率 20× 及其他逻辑不变。

## 结论（先给答案）

- 原规则实现在 `src/data/combat/attack/data_base_skill.gd` 的 `add_proficiency(amount, character_level)`：`character_level >= ResManager.character_exp_dic.size() - 9` 时 `amount * 20`。（用户口语「最高等级减 10 级」对应代码里的 `-9`，仅此一处实现，无其它分支/副本。）
- 改后：**只有宠物**（`DataPet`）且**等级 > 50** 时 ×20；非宠物（玩家/怪物）不再享受加速。阈值/倍率已常量化便于后续调整。

## 改动清单

| 文件 | 改动 |
|------|------|
| `src/data/combat/attack/data_base_skill.gd` | 新增常量 `TONG_MING_PET_LEVEL = 50`、`TONG_MING_MULTIPLIER = 20`；`add_proficiency(amount, character_level = 0, is_pet = false)`，判定改为 `is_pet and character_level > TONG_MING_PET_LEVEL`（删除原等级上限推算） |
| `src/data/combat/attack/data_attack_action.gd` | 新增 `character_is_pet`；`execute_attack(level = 0, is_pet = false)` 透传；`complete_cast()` 结算熟练度时带上宠物标识（主动技能路径） |
| `src/data/combat/data_combat_character.gd` | `attack_target()` / `_cast_skill_action()` 的 `execute_attack(data_character.level, data_character is DataPet)`；千面蝶舞触发处补 `is DataPet` |
| `src/data/combat/character_effect_handler.gd` | 幽魂附体（`passive_000017`）与通用被动加熟练度 `_add_passive_skill_proficiency()` 补 `is DataPet` |
| `src/tools/combat_event_handler.gd` | 战斗结算被动熟练度 `character is DataPet` |
| `src/tools/wuxing_xiangsheng_handler.gd` | 五行相生（`passive_310001`）补 `is DataPet` |
| `src/tools/attack_entity_hit_handler.gd` | 含沙射影（`passive_000023`）补 `is DataPet` |
| `src/tools/game_debug_tool.gd` | 调试面板「加熟练度」的宠物循环显式传 `true` |
| `src/ui/skill_help_dialog_control.gd` + `assets/text/text.csv` | 文案改为「当宠物等级大于%d级时，进入【通明】状态（获得20倍技能熟练度）」，弹窗改为读取 `DataBaseSkill.TONG_MING_PET_LEVEL`（不再依赖等级上限推算） |
| `src/test/system/realm_compat_test.gd` | C 段断言重写：非宠物 lv91/lv100 ×1；宠物 lv50 ×1；宠物 lv51/lv100 ×20 |
| `dev_log.md`、`docs/realm_stage_e2e_test_plan.md` | 变更记录与测试计划同步（旧「熟练度加速漂移 lv91」条目按新规则改写） |

未改动（玩家侧，默认 `is_pet=false` 即不再加速）：`src/scenes/game_world.gd:1647`、`src/tools/dialogue_complete_tool2.gd:195`、`src/remote/custom_commands.gd:358`、`src/tools/game_debug_tool.gd` 的玩家分支。

## 关键判定与口径（需用户确认，见「后续跟进」）

1. **「宠物」按 `DataPet` 实例判定**：战斗内 `DataCombatCharacter.data_character` 仍是原 `DataPet` 对象（`combat_init_tool` 只持有引用，`is_player_side` 也是用 `is DataPet` 判定），因此各调用点用 `... is DataPet` 即可，无需新增字段。
2. **玩家不再享受 ×20**：原规则对「角色」生效，玩家 lv91+ 也曾 ×20；按「取消原设定 + 改成宠物…」的口径，玩家现在全程 ×1。若本意是「玩家保留原规则、宠物另加一条」，则只需把判定改为 `(is_pet and lv > 50) or (not is_pet and lv >= max-9)`。
3. **野生怪物也不再 ×20**（lv91+ 怪物）——同上口径。

## 验证

| 验证项 | 结果 |
|--------|------|
| `godot --path . --headless -- --e2e-realm-compat` | **ALL PASS (25 checks)**，含 `tong_ming_threshold_is_50`、`non_pet_lv91_no_acceleration`、`pet_lv50_still_below_threshold_x1`、`pet_lv51_accelerated_x20`、`pet_lv100_accelerated_x20` |
| `godot --path . --headless -- --e2e-stage-flow` | ALL PASS (41 checks)（含 85 级宠物注入 / 境界效果战斗路径回归） |
| `python validate_configs.py` | 全部通过（0 错误；7 个警告均为既有、与本次无关） |
| 语法检查 | 改动文件随 E2E 加载无脚本编译错误（`--check-only` 单文件模式因 autoload 未注册会误报 `ResManager` 未找到，未修改文件同样报错，非本次引入） |

## 进度记录

### 15:35 - 定位实现

- 全项目检索 `通明`：仅 `assets/text/text.csv`（帮助文案）与 `dev_log.md`（历史记录）命中 → 机制实现在技能熟练度入口 `DataBaseSkill.add_proficiency`。
- 原实现（`git show 52cf9435` 引入）：等级 ≥ 上限 − 9 时 ×10（后续改为 ×20）；判定随等级上限 59→100 由 50 上移到 91。用户所说「最高等级减少10级」即指该规则。

### 15:45 - 实施与自测

- 按「宠物等级 > 50，其他不变」实现：新增 `is_pet` 入参 + 常量，补齐全部 8 个调用点（主动技能走 `execute_attack` 透传，被动走触发处判定）。
- 文案与测试同步；`--e2e-realm-compat` 25 断言全绿。

### 15:50 - 提交、rebase 与推送

- 提交 `fc7b23e7`；push 时被拒：远端已有他人两条新提交（`633881ac`「61-100 级怪物被动技能熟练度统一为战斗胜利后获得」、`f496d6ad`「61-70 暗雷普通怪血量+100%/攻击+20%」）。
- `git rebase origin/master` 无冲突（对方改的是 `character_effect_handler.gd` 的调用点与 `combat_event_handler.gd` 白名单，与本改动相邻但不重叠）→ 新提交 `f98866f7`，重跑 `--e2e-realm-compat` 仍 25 断言全绿后 push 成功。
- 备注：`633881ac` 把怪物被动熟练度统一到「战斗胜利后结算」，正好走 `combat_event_handler._check_and_increase_proficiency_for_skills(character)`，本次已在其上补 `character is DataPet`，两条改动语义一致、无冲突。

## 问题与阻塞

| 问题 | 状态 | 备注 |
|------|------|------|
| 玩家/野生怪物是否也应保留「≥上限−9」的 ×20 | 待确认 | 本次按字面「取消原设定、改成宠物>50」实现（非宠物不加速）；如需保留，1 行判定即可恢复 |
| push 被远端新提交拒绝 | 已解决 | rebase 后重测通过再 push，无冲突 |

## 附件（file/）

| 文件 | 说明 |
|------|------|
| — | 本次无截图；验证为 headless 断言输出（见「验证」表） |

## 相关链接

- 项目：`D:\godot\projects\text-turn-game`（远端 `https://gitee.com/sdf2311d/text-turn-game.git`，分支 `master`）
- 本次基线提交：`634f6588` → rebase 到 `f496d6ad` → 本次提交 **`f98866f7`**
- 核心文件：`src/data/combat/attack/data_base_skill.gd`（`add_proficiency`）、`src/data/combat/attack/data_attack_action.gd`、`src/ui/skill_help_dialog_control.gd`
- 历史来源：`52cf9435 feat: 新增高等级角色技能熟练度10倍加速机制及帮助弹窗`（原规则引入）

## 明日计划 / 后续跟进

- [ ] 确认「宠物 > 50 才通明、玩家不再 ×20」是否为最终口径；若玩家需保留旧规则，改判定为「宠物>50 或 非宠物≥上限−9」
- [ ] 真机验收：宠物过 50 级后打一场，确认技能熟练度实际按 20 倍增长；技能说明弹窗文案显示「宠物等级大于50级」
- [ ] 评估平衡影响：宠物（经验按 1/3.5 成长）过 50 级后技能成长提速 20 倍，是否会导致宠物技能过早满级；必要时评估是否同时上调宠物技能熟练度阈值

## 变更记录

| 时间 | 变更说明 |
|------|----------|
| 2026-09-11 15:35 | 创建 job；定位原规则实现（等级≥上限−9 → ×20） |
| 2026-09-11 15:45 | 实施新规则（宠物>50 ×20、非宠物不加速），文案/测试/文档同步；`--e2e-realm-compat` 25 断言 PASS |
| 2026-09-11 15:50 | rebase 远端 2 条新提交后 push：`origin/master` = `f98866f7`；并记录「玩家是否保留旧规则」待确认项 |
