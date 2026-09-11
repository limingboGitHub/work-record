# Job: 文字九州修仙 —— 确认「幻音妖后」是否配置了技能

## 基本信息

| 字段 | 内容 |
|------|------|
| 日期 | 2026-09-11 |
| 项目/模块 | 文字九州修仙（godot / text-turn-game，工程名 TextTurnGame） |
| 状态 | 已完成（Q1 确认；Q2/Q3/Q4 已实施并 push：`origin/master` = `634f6588`；真机验收待设备） |
| 预估耗时 | 0.3h |
| 实际耗时 | ~15min（09:40~09:55 确认技能；10:0x~ 追加 Boss 战配置调整分析） |
| 关键字 | #文字九州修仙 #TextTurnGame #godot #怪物技能 #幻音妖后 #镇妖塔 #战斗配置 #配置确认 |

## 任务描述

> 用户提问①：「幻音妖后」是否配置了技能？
> 用户提问②：它和幻音妖是不是同一个技能？如果是，则「幻音妖后」的辅助技能需要搭配攻击怪 → 调整 `npc_104045` 挂载的战斗配置，把目前 4 只都是幻音妖后的战斗改为「幻音妖后 + 对应地图的攻击怪」。
> 本 job 先做只读核实（配置 → 运行时装载 → 战斗入口三层交叉验证），再定位「4 只幻音妖后」的根因并给出调整方案；**方案选型待用户确认后再动代码**。

## 结论（先给答案）

**是，配置了技能。** `monster_106002`（幻音妖后，Lv.65 精英，`is_magic=true`）的 `skill_actions = ["action_100075"]`，即主动技能 **迷魂音波**；运行时正确装载并装备。

唯一与同级 Boss 不一致的一点：**幻音妖后没有被动技能**——镇妖塔其余三个守关 Boss 都是「主动 1 + 被动 1」。

## 证据链

| # | 层面 | 证据 |
|---|------|------|
| 1 | 怪物配置 | `assets/config/monster/monster_106002.json`：`description=幻音妖后`、`level=65`、`monster_quality=elite`、`is_magic=true`、`skill_actions=["action_100075"]`；`base.attack_range=3`；`enhance`：气血 21075 / 怒气上限 100 / 物伤 975 / 法伤 537 / 防御 534 / 修为 2025000 |
| 2 | 技能定义 | `assets/config/skill_action.json` → `action_100075`：迷魂音波；`rage_cost=40`、`max_level=5`、`cast_time=0.3` / `recovery_time=0.1`；`entity_type=circle_area`、`attack_radius=1`（每级 +0.125）、以自身为中心；`attack_buffs` = 友军 +10 物/法伤、敌军 −10 物/法伤，均持续 20 秒（每级 ±2） |
| 3 | 文案 | `assets/text/text.csv`：`ATTACK_ACTION_NAME_100075=迷魂音波`、`ATTACK_ACTION_DESC_100075=释放声波，1格范围内敌军减少10点物理和法术伤害…`、`MONSTER_106002_NAME=幻音妖后` |
| 4 | 运行时装载 | `src/managers/res_manager.gd:362-375` 遍历 `skill_actions`，主动技能 `add_skill_category("SELF_STUDY")` + `equip_skill()`；**headless 探针实测**：已学技能 `["action_100075"]`、已装备主动技能 `["action_100075"]`，`action_100075` 解析成功（见 `./file/huanyin-skill-probe.txt`） |
| 5 | 战斗入口 | `quest_106009`（二层试炼）→ `dialogue_106009`（`npc_104045` 幻音妖后）→ `combat_106009`（desc：镇妖塔·二层·守关 Boss - 幻音妖后）→ `characters=["monster_106002"]`；`map_npc.json` 的 `map_101018` 放置 `npc_104045`。链路完整可达 |
| 6 | 特化实现 | `src/tools/attack_entity_hit_handler.gd:177`、`3243 _execute_mihun_skill()`：给同队友军加增益，并另行扫描半径内敌军加减益（补足 `entity_effect_target_type=same_team` 的语义） |
| 7 | 校验 | `python validate_configs.py` 全量通过（0 错误；7 个警告均为既有、与本次无关）；同技能的普通怪 `monster_006003`「幻音妖」已有自动化用例（`src/test/combat/test_combat_auto.gd`「幻音妖迷魂音波测试」） |

## 与同级守关 Boss 对照

| Boss | monster_id | 主动技能 | 被动技能 |
|------|------------|----------|----------|
| 千年铜尸（一层） | `monster_106001` | `action_100073` 毒雾吐息 | `passive_000027` 透骨之毒 |
| **幻音妖后（二层）** | `monster_106002` | `action_100075` 迷魂音波 | **无** |
| 狰兽王（三层） | `monster_106003` | `action_100080` 虎啸碎岳 | `passive_000031` 饮血返元 |
| 远古镇狱石魔（四层） | `monster_106004` | `action_100082` 远山御阵 | `passive_000033` 磐石初甲 |

`design/design_monster.md:303-304` 对幻音妖后也只写了「迷魂音波」一条 → **实现与设计文档一致**；但它确实是四个守关 Boss 中唯一没有被动的一个。若需求为「精英守关 Boss 应主被动各一」，则此处属缺口，需另开 job 补配置。

## 两点延伸提示（若关心「实战里放不放得出来 / 看不看得出」）

1. **怒气来源不存在死锁**：怪物靠普攻 +15/次、受伤（伤害占最大生命 1% = 1 点，单次上限 20）累积怒气；`rage_max=100`、技能 `rage_cost=40` → 约 3 次普攻即可释放。即「有技能但永远放不出」的情况不成立。
2. **射程与技能范围错配的观感问题**：幻音妖后 `attack_range=3`（远程），而迷魂音波是**以自身为中心半径 1 格**的圆域增/减伤。它保持距离输出时，增益基本只作用于自己，减益要玩家贴到 1 格内才吃得到，实战观感容易「像没放技能」。而设计描述是「能以一己之力覆盖整层空间」——若按设计意图应做大范围，则属于另一项需求（需改半径 / 目标类型）。

---

## 追加（第二轮）：幻音妖后 Boss 战怪物构成调整

### Q2：幻音妖后与幻音妖是同一个技能吗？

**是，同一条技能、且都没有被动**：

| 怪物 | id | 等级 | skill_actions |
|------|----|------|---------------|
| 幻音妖 | `monster_006003` | 63 | `["action_100075"]` |
| 幻音妖后 | `monster_106002` | 65（精英） | `["action_100075"]`（完全相同） |

### 「4 只幻音妖后」的根因（已定位）

`combat_106009` 的 `characters` 实际只有 **1 条**条目（`monster_106002`，位置 `(2,1)~(2,2)`），但带了 `auto_count: true`：

- `src/tools/combat_init_tool.gd:122-134`：`auto_count=true` 时，把配置条目按 `monster_infos[i % monster_infos.size()]` **重复填充到与玩家队伍人数一致**；
- 玩家队伍 4 人 → 单条目被复制 4 份 → **4 只幻音妖后**（2 只落在 `(2,1)/(2,2)`，另 2 只溢出到最近空格，见 `_assign_character_position_from_range` 的 fallback）；
- `MonsterInfo.count` 默认 1。

→ 所以不是「配了 4 条」，而是「单条目 + auto_count 复制 4 份」。4 只辅助怪互相加伤、无人输出，这正是需要引入攻击怪的原因。

### 关键约束：二层「除辅助怪外」只有 1 种攻击怪

| 来源 | 配置 | 怪物 | 技能性质 |
|------|------|------|----------|
| 二层地图战 | `combat_006002`（镇妖塔·二层·幻音迷境 - 幻音妖+魇影） | `monster_006003` 幻音妖 Lv63 | **辅助**（迷魂音波，与 Boss 同技能） |
| 同上 | 同上 | `monster_006004` 魇影 Lv64 | **攻击**：`action_100079` 梦魇（200% 法术伤害 ×2 目标 + 50% 沉睡）；被动 `passive_000030`（沉睡目标苏醒时额外 200% 法术伤害） |

`design/design_monster.md:291-304` 二层怪物就是「幻音妖 + 魇影 + 守关精英幻音妖后」三种。→ 严格按「攻击性技能」筛选，**二层可用的只有魇影**，凑不出「3 种不同」。

### 调整方案（三选一，待用户确认）

| 方案 | 构成 | 说明 |
|------|------|------|
| **A（已采用）** | 1×幻音妖后 + 3×魇影 | 全部来自二层，满足「1 辅助 + 3 攻击位」；缺点是小怪同一种 |
| B | 1×幻音妖后 + 2×魇影 + 1×幻音妖 | 贴合二层地图阵容（`combat_006002`）；但幻音妖也是辅助，攻守配比是 2 辅助 : 2 输出 |
| C | 1×幻音妖后 + 1×魇影(64) + 1×狰兽(65) + 1×伥鬼(66) | 能给出 3 种不同攻击怪，但引入了三层/四层怪，与本层难度梯度不符 |

### 实施技术要点（无论选哪个方案）

1. **把 `auto_count` 改为 `false`，显式写 4 条条目**（沿用游戏既有「Boss + 小怪」惯例：`combat_000005`、`combat_901006`、`combat_005019`）。理由：
   - 若保留 `auto_count=true` 且写 4 条，4 人队伍恰好每种 1 只，但队伍 <4 人时只会随机取子集；
   - `dialogue_106009_2` 的 `requires.kill_monster` 明确要求击杀 `monster_106002` × 1（用于开门 + 移除 NPC），**Boss 缺席会卡任务**。
2. Boss 保留 `(2,1)~(2,2)` 一带，小怪分列 `(1,1)~(1,3)`、`(2,0)`、`(3,1)~(3,3)`（参照 `combat_000005` / `combat_901006` 的落位习惯）。
3. 影响面：仅 `combat_106009`（由 `npc_104045` 对话解锁），不动 `map_101018` 的地图战 `combat_006002`；`src/test/e2e/tests/test_stage7.gd` 用 `complete_quest_direct` 兜底，不校验战斗构成，不会因此失败。
4. 改完需补验证：headless 跑一遍战斗初始化，断言「1 只怪是 monster_106002 + 其余为指定怪物」，并跑 `validate_configs.py`。

## 追加（第三轮）：镇妖塔每一层守关 Boss 均为「1 Boss + 3 普通怪」

### 需求

> 「镇妖塔每一层的 npc 怪物战斗配置都需要调整，一个 boss 配 3 个普通怪物。」（2026-09-11）

### 全塔守关 Boss 战清单与改后构成

| 层 | 战斗 | NPC / 触发 | 改前 | 改后（1 Boss + 3 普通怪） |
|----|------|-----------|------|--------------------------|
| 一层 | `combat_106008` | `npc_104044`/`dialogue_106008` | `auto_count` × 4 只千年铜尸 | 千年铜尸 ×1 + 铜尸 ×1 + 妖鼠 ×2 |
| 二层 | `combat_106009` | `npc_104045`/`dialogue_106009` | `auto_count` × 4 只幻音妖后 | 幻音妖后 ×1 + 魇影 ×3 ✅ 已完成 |
| 三层 | `combat_106010` | `npc_104046`/`dialogue_106010` | `auto_count` × 4 只狰兽王 | 狰兽王 ×1 + 狰兽 ×1 + 伥鬼 ×2 |
| 四层 | `combat_106011` | `npc_104047`/`dialogue_106011` | `auto_count` × 4 只远古镇狱石魔 | 远古镇狱石魔 ×1 + 罗刹 ×3 |
| 五层 | `combat_106002` | `npc_104012`（上古剑灵）/`dialogue_106006` | `auto_count` × 4 只剑灵残魂 | **上古剑灵残魂 ×1 + 双首妖狼 ×1 + 噬魂妖将 ×2** ✅ 已完成 |

> 全塔五层已统一：`auto_count: false` + 固定 4 只（1 Boss + 3 只本层普通怪）。

### 选怪规则（沿用二层已确认口径）

1. **一 Boss + 3 只本层普通怪**，且 3 只以「有攻击技能的怪」为准；
2. Boss 与本层某只普通怪同技能对（精英＝普通怪强化版）时，**不使用重复的辅助/无输出怪堆叠**：
   - 二层：Boss 幻音妖后 与 幻音妖 同为辅助 `action_100075` → 3 只全用魇影；
   - 四层：Boss 远古镇狱石魔 与 镇狱石魔 同为「自我减伤 + 护盾」无伤害技能 → 3 只全用罗刹；
   - 一/三层：Boss 自身就是输出怪，两种普通怪均为攻击型 → 按 1 : 2 搭配（同族 1 + 异族 2），兼顾主题与变化。
3. 落位全部统一为菱形（含五层，原剑灵中心位 `(3,2)` 改为与其他层一致的 `(2,1)~(2,2)`）：Boss `(2,1)` / 左 `(1,2)` / 右 `(3,2)` / 前 `(2,3)`。
4. 全部关闭 `auto_count`（用户明确要求），4 条显式条目，保证与队伍人数解耦且 Boss 必出场（任务开门依赖 `kill_monster`）。

### 验证（2026-09-11 11:1x）

- headless 真实初始化路径（`CombatInitTool.init_combat_with_config`）逐场验证 **`combat_106002` + `106008~106011` 全部 5 场**：队伍 1/2/4 人下均固定为 **4 只 = 1 Boss + 3 普通怪**，落位固定，**30 断言全 PASS / 0 FAIL**（输出见 `./file/tower-boss-combats-probe.txt`）。
- `python validate_configs.py`：全量通过（0 错误，7 个既有无关警告）。
- 提交并 push：五层 `d40d4c7d..634f6588`（`origin/master` = `634f6588`）。

## 关联工作（文件索引）

| 关系 | 文件路径 | 说明 |
|------|----------|------|
| 同项目同日 | `./job1.md` | 境界弹窗返工（同仓库同项目，非同一目标） |
| 项目接入背景 | `../2026-09-10/job3.md` | TextTurnGame 首次接入与运行验证 |

## 待办清单

- [x] 配置层核对（怪物 JSON + 技能定义 + 文案）
- [x] 运行时装载核对（headless 探针，确认「已学 + 已装备」）
- [x] 战斗入口链路核对（quest → dialogue → combat → monster）
- [x] 全量配置校验（`validate_configs.py`）
- [x] 与同级 Boss、设计文档对照
- [x] Q2 核对：幻音妖后 = 幻音妖同技能（`action_100075`），且都无被动
- [x] 定位「4 只幻音妖后」根因：单条目 + `auto_count: true` 复制到队伍人数
- [x] 用户选定**方案 A**，并明确要求该 NPC 的战斗**不使用 `auto_count`**
- [x] 实施：`combat_106009` → `auto_count: false` + 4 条显式条目（1×`monster_106002` + 3×`monster_006004`）与落位
- [x] 验证：headless 真实初始化路径断言（队伍 1/2/4 人均为 4 只：1 Boss + 3 魇影、落位固定）+ `validate_configs.py` 全量通过
- [x] 提交与推送：`6fbf042d..04bc7bf0`，`origin/master` = `04bc7bf0`
- [x] Q3：一/三/四层守关 Boss 统一为「1 Boss + 3 只本层攻击型普通怪」，均关闭 `auto_count`，headless 24 断言 PASS
- [x] 提交与推送（第三轮）：`04bc7bf0..d40d4c7d`，`origin/master` = `d40d4c7d`
- [x] Q4：五层上古剑灵战（`combat_106002`）也改为「剑灵 ×1 + 双首妖狼 ×1 + 噬魂妖将 ×2」+ 关闭 `auto_count`，headless 30 断言 PASS
- [x] 提交与推送（第四轮）：`d40d4c7d..634f6588`，`origin/master` = `634f6588`
- [ ] 真机验收（五层守关 Boss 战：不再 4 只剑灵残魂；击败后任务六/开门正常）
- [ ] 真机验收（四层守关 Boss 战：均不再是 4 只 Boss；战后对话开门正常）；如需同步设备跑 `bash sync_android.sh`
- [ ] 待用户确认：是否给幻音妖后补一个被动技能（如需，另开 job 实现）
- [ ] 待用户确认：迷魂音波「半径 1 格 + 自身为中心」是否为预期（若应覆盖整层，另开 job 调整）

## 进度记录

### 09:40 - 静态核对

- 全仓检索 `幻音妖后`：命中 `monster_106002.json`、`combat.json`（combat_106009）、`npc.json`（npc_104045）、`dialogues.json`（dialogue_106009/106009_2）、`design_monster.md`。
- 读取 `monster_106002.json`：确认 `skill_actions=["action_100075"]`。

### 09:44 - 技能与文案核对

- `skill_action.json` 中 `action_100075` = 迷魂音波（主动，cost 40，圆域 1 格，友军增伤 / 敌军减伤 20s）。
- `text.csv` 文案齐全；`attack_entity_hit_handler.gd` 有该技能的特化实现 `_execute_mihun_skill`。

### 09:47 - headless 运行时探针

- 临时探针场景加载 Autoload（FileCacheTool + ResManager），`create_monster_instance("monster_106002")` 后打印技能背包：**已学 `["action_100075"]`、已装备 `["action_100075"]`**；同时对比了 `monster_006003/106001/106003/106004`，确认只有幻音妖后无被动。
- 探针脚本已移出工程目录（工程 `git status` 仅剩既有未跟踪文件 `update_code.sh`，无本次残留）。

### 09:52 - 校验与结论

- `python validate_configs.py`：258 文件语法通过、引用完整性通过（7 个既有无关警告）。
- 结论输出给用户；跟进项（是否补被动 / 是否改范围）留待确认。

### 10:05 - 第二轮追问：同技能核对 + 4 只幻音妖后根因

- 核对 `monster_006003`（幻音妖）与 `monster_106002`（幻音妖后）：`skill_actions` 完全相同，均为 `["action_100075"]`，均无被动 → 回答用户「是同一个技能」。
- 读 `combat_init_tool.gd:122-134` + `data_combat_config.gd`：`auto_count=true` 会把单条目重复到队伍人数 → 定位「4 只幻音妖后」根因（非 4 条配置）。
- 查二层地图阵容 `combat_006002` 与 `design_monster.md`：二层除两只辅助怪外，只有 `monster_006004` 魇影是攻击怪 → 「3 只不同攻击怪」在二层内无法满足，需用户选型（A/B/C）。
- 查任务依赖 `dialogue_106009_2.requires.kill_monster=[monster_106002×1]` → 实施时应关 `auto_count` 以保证 Boss 必出场。
- 本轮只做分析，未改动游戏代码；方案待确认后实施。

### 10:25 - 实施方案 A（已 push）

用户选定 **A**，并额外要求「这个 NPC 配置的战斗不要使用 `auto_count` 参数」。

`assets/config/combat.json` → `combat_106009` 改动：

| 项 | 改前 | 改后 |
|----|------|------|
| desc | 镇妖塔·二层·守关Boss - 幻音妖后 | 镇妖塔·二层·守关Boss - 幻音妖后（辅助）+ 魇影×3 |
| auto_count | `true` | **`false`** |
| characters | 1 条（`monster_106002`） | 4 条：`monster_106002` ×1 + `monster_006004` ×3 |

落位（敌人区 y=1..3，玩家在 y=4/5）：

```text
y=1:           幻音妖后(2,1)
y=2:  魇影(1,2)         魇影(3,2)
y=3:           魇影(2,3)
```

（Boss 保留原 `(2,1)~(2,2)` 范围；三只魇影分列左/右/前，形成「辅助在后、输出在前」的护阵）

### 10:30 - 验证

- **headless 真实初始化路径**（`CombatInitTool.init_combat_with_config` + 真实 `ResManager.get_combat_config`）：队伍 1/2/4 人三种情况**均为 4 只敌人 = 1×幻音妖后 + 3×魇影**，落位固定 `(2,1)/(1,2)/(3,2)/(2,3)`，断言全部 **PASS** → 证明构成不再随队伍人数漂移（`auto_count` 已关闭生效）。输出见 `./file/combat-106009-probe.txt`。
- `python validate_configs.py`：全量通过（0 错误，仅 7 个既有无关警告）。
- 相关技能已有既有自动化用例覆盖：`action_100075` 迷魂音波（`test_combat_auto`「幻音妖迷魂音波测试」）、`action_100079` 梦魇 + `passive_000030`（同文件梦魇用例）。
- 提交：`04bc7bf0`，已 push（`origin/master` = `04bc7bf0`）。

### 10:35 - 遗留与提示
- 本轮**未改**怪物技能与 `monster_106002.json`（无被动、技能范围等两个待确认项仍保留在待办）。
- 平衡提示：3×魇影的梦魇带 50% 沉睡（×2 目标），搭配 Boss 的增/减伤光环，实际难度可能明显上提；如需调弱可把 1 只魇影换回 `monster_006003` 或降等级，待真机体验后再定。

### 10:50 - 第三轮：全塔守关 Boss 统一（已 push）

用户要求「镇妖塔每一层的 npc 怪物战斗配置都需要调整，一个 boss 配 3 个普通怪物」。

- 先枚举全塔 NPC 挂载的 Boss 战：`dialogue_106008~106011` → `combat_106008~106011`（一层~四层，NPC 104044~104047）；五层是 `dialogue_106006`（npc_104012 上古剑灵）→ `combat_106002`。
- 核对每层普通怪技能性质（防止再次出现「一对辅助/坦克怪没人输出」）：
  - 一层：铜尸（毒雾吐息）、妖鼠（瘟疫齿刃）——均攻击型；
  - 二层：幻音妖（辅助）、魇影（梦魇）——已按方案 A；
  - 三层：狰兽（虎啸碎岳）、伥鬼（无痕暗刺）——均攻击型；
  - 四层：镇狱石魔（远山御阵：仅自我减伤）、罗刹（千刹掠影）→ **石魔无伤害技能**，与 Boss 同技能对。
- 实施：
  - `combat_106008`：千年铜尸 ×1 + 铜尸 ×1 + 妖鼠 ×2
  - `combat_106010`：狰兽王 ×1 + 狰兽 ×1 + 伥鬼 ×2
  - `combat_106011`：远古镇狱石魔 ×1 + 罗刹 ×3
  - 三者均 `auto_count: false` + 4 条显式条目，落位沿用二层菱形。
- 验证：headless 对 106008~106011 逐场跑真实初始化，队伍 1/2/4 人下构成与落位全固定，**24 PASS / 0 FAIL**；`validate_configs.py` 全量通过。
- 提交并 push：`d40d4c7d`。
- 五层 `combat_106002` 已按用户回覆（「也需要改」）同步调整。

### 11:15 - 第四轮：五层同步（已 push）

- 用户回「也需要改」→ `combat_106002`：`auto_count: false`，4 条显式条目：上古剑灵残魂 `monster_900025` ×1 + 双首妖狼 `monster_006009` ×1 + 噬魂妖将 `monster_006010` ×2（沿用全塔「两种普通怪 1:2」规则，第二只放 2 个）；Boss 落位由 `(3,2)` 改为与其他层一致的 `(2,1)~(2,2)`。
- 设计文档原本将五层定义为 1v1「剑术对决」，本条改动以用户指示为准；已在该层 Boss 为「不删除的可重复挑战 Boss」的设定下评估，改动不影响该机制（只改变每次挑战的敌人构成）。
- 验证：扩展探针至 5 场战斗（106002 + 106008~106011），**30 PASS / 0 FAIL**；`validate_configs.py` 全量通过。
- 提交并 push：`d40d4c7d..634f6588`。

## 追加（第五轮）：五层最终 Boss「上古剑灵残魂」技能核实（只读）

### 需求

> 「上古剑灵这个 boss 技能是怎么样的？具体什么效果」

### 对象澄清

- **NPC `npc_104012`「上古剑灵」**：五层任务 NPC（`dialogue_106006`「剑灵传承」），不是战斗单位。
- **战斗 Boss = `monster_900025`「上古剑灵残魂」**：Lv70 / `epic` / `monster_type=boss` / `attack_range=2`，`combat_106002` 的敌方主将。两者是「虚影 NPC」与「其残魂」的关系（对白 `TEXT_DIALOGUE_NPC_104012_DEFAULT`：上古剑灵的虚影；`TEXT_DIALOGUE_106006_4`：战胜剑灵残魂后收剑）。

### 技能总览

| 类型 | id | 名称 | 运行时装载 |
|------|----|------|-----------|
| 主动 | `action_100086` | **万剑覆雨** | 已学 + 已装备（`equipped=[action_100086]`） |
| 被动 | `passive_000037` | **不灭残魂**（`effect_100089`） | 已学（`learned=[action_100086, passive_000037]`） |

> 配置里 `skill_actions` 同时放主动与被动 id，`res_manager.gd` 按 `passive_` 前缀分流（被动进技能背包、主动额外 `equip_skill`）——实现正常。

### 主动技能：万剑覆雨（action_100086，默认 lv1/5）

| 项 | 值 |
|----|----|
| 文案 | `ATTACK_ACTION_NAME_100086` = 万剑覆雨；描述「召唤{sword_count}把残剑覆盖整个战场，每把剑造成{0}%物理伤害」 |
| 怒气 | **120**（全塔守关 Boss 最高：铜尸/狰兽王/石魔 80、幻音妖后 40） |
| 时序 | 读条 0.8s → 释放 10s → 后摇 0.5s |
| 击体 | `entity_100086`，`entity_type=sword_rain`，`entity_fly_target_type=diff_team`（只打敌方），`entity_duration=10`，`hit_interval=0.03` |
| 数量/伤害 | `sword_count=100`（每级 +5），每把剑 **50% 物理伤害**（每级 +1%），`source_type/damage_type=physical` |
| 附加效果 | **无**（`attack_effects` 为空）——纯伤害技能 |

**实际表现**（实现层 `src/scenes/attack_effect/attack_effect_sword_rain.gd` + `attack_effect_sword_rain.tscn`）：

1. 每 **0.3s 生成一波 × 每波 10 把**（`total_waves = ceil(sword_count/10)`）→ 100 把 = **10 波 / 生成窗口约 3.0s**，之后不再生成；
2. 每把剑在战场上方**随机水平位置**出现、竖直向下飞（场景 `move_speed=500`，`horizontal_spread=700`）；
3. 剑与敌人距离 ≤ `hit_threshold(35px)` 即命中：**该剑消失 + 结算一次 50% 物理伤害**（`target_hit` 信号 → `attack_entity_hit_handler`）；
4. 未命中的剑穿场飞出屏幕（`despawn_y=720`）自动回收；全部回收后击体结束；
5. 理论满命中伤害 = 100 × 50% = **5000% 物理**（多目标时按各自被撞到的剑数分摊）。

**两处配置不生效（实现层忽略，非本次改动）**：

- `move_speed: 400`：`DataBaseAttackEntity` 无此字段，剑雨场景用自带 `move_speed=500`；
- `hit_interval: 0.03`：剑雨走场景自有波次逻辑（`wave_interval=0.3`），不走 `DataBaseAttackEntity` 的 `next_hit_time` 多段间隔。

**怒气可达性（重点核对）**：Boss 配置 `rage_max=100` < 技能 `rage_cost=120`，但实战中**怒气槽上限取技能 rage_cost**（`combat_init_tool` 初始化即 `data_character.update_rage_value(action.rage_value, action.rage_cost, ...)` → `_update_rage_value_max()` 覆写 `max_value`）。headless 实测：注入后 `rage_value.max_value = 120`（`rage_cost_multiplier` 属性=0，无加成）→ **普攻 8 次（15/次）或受击（1% 最大生命=1 点、单次上限 20）即可放出**，不存在「怒气上限 100 < 需求 120 导致技能永远放不出」的死锁。

### 被动技能：不灭残魂（passive_000037 → effect_100089，默认 lv1/5）

| 项 | lv1 | 每级成长 | lv5 |
|----|-----|----------|-----|
| 复活概率 | 100% | — | 100% |
| 复活延迟 | 1s | — | 1s |
| 复活血量 | **20% 最大生命** | +3% | 32% |
| 每场次数 | 1 次 | — | 1 次 |

文案：`SKILL_PASSIVE_DESC_000037` 为**空字符串**（`""`），但效果 `effect_100089` 本身有 `EFFECT_100089_DESC`「死亡后{0:%}概率{1}秒后以{2:%}血量复活，每场最多{3}次」→ 技能说明若直接读 `skill_desc` 会显示空白（表现问题，非功能问题）。

实现链：`character_effect_handler.gd` → `can_revive()` 优先检查 `effect_100089` → `_check_revive_effect()`（概率 100%、次数按 4 值格式取 index 3=1）→ `process_reviving()`（1s 后按 `hp_max × 20%` 回血并回到 IDLE）。

### 本战其他成员（同一场战斗的完整构成）

| 位 | 怪物 | 等级 | 主动技能 | 被动 |
|----|------|------|----------|------|
| Boss | `monster_900025` 上古剑灵残魂 | 70 | `action_100086` 万剑覆雨（120 怒，剑雨） | `passive_000037` 不灭残魂 |
| 普通 | `monster_006009` 双首妖狼 | 69 | `action_100084` 双噬怒击（同时打 2 目标，命中 2 个回 50% 怒气） | `passive_000035` 怒意叠锋 |
| 普通×2 | `monster_006010` 噬魂妖将 | 70 | `action_100085` 噬灵爆焰（法术伤害 + 减目标 30% 伤害抵抗） | `passive_000036` 咒音回弹 |

### 证据链

| # | 层面 | 证据 |
|---|------|------|
| 1 | 怪物配置 | `assets/config/monster/monster_900025.json`：`level=70`、`boss`、`epic`、`attack_range=2`、`skill_actions=[action_100086, passive_000037]` |
| 2 | 主动技能配置 | `skill_action.json` → `action_100086`：万剑覆雨，`rage_cost=120`、`cast_time=0.8`、`recovery_time=0.5`、`release_duration=10`；击体 `entity_type=sword_rain`、`sword_count=100`、`damage_percent=0.5(+0.01/级)`、无 `attack_effects` |
| 3 | 被动/效果配置 | `skill_passive.json` → `passive_000037`（`attack_effects=[effect_100089]`）；`attack_effect.json` → `effect_100089` `effect_values=[1,1,0.2,1]`、`per_level=[0,0,0.03,0]` |
| 4 | 运行时装载 | headless 探针：`equipped=[action_100086]`、`learned=[action_100086, passive_000037]`；注入后 `rage_value.max_value=120`；全塔怒耗对照 120 / 80 / 80 / 80 / 40 |
| 5 | 表现实现 | `attack_effect_sword_rain.gd`（10 把/波、0.3s 一波、随机水平位置、命中即消失并结算伤害）+ `data_attack_action.gd:381`（`sword_rain` → `DataAttackEntityLotFlySword`） |
| 6 | 复活实现 | `character_effect_handler.gd:732/754/802`（`can_revive` 优先 100089 → `_check_revive_effect` 取 index 3 次数 → `process_reviving` 按 `hp_max × effect[2]` 回血） |

### 核实结论（三点待拍板）

| # | 现象 | 判断 |
|---|------|------|
| 1 | 剑雨每把剑**随机水平落点**，多目标时可能大量落空 | 与文案「覆盖整个战场」尚不矛盾；若体感「像没打中」，可改确定性落点（按敌方分布）或提高 `hit_threshold` |
| 2 | 数据 `release_duration/entity_duration=10`，但实测 `sword_count=100` 使生成窗口只有 **3.0s**（实现取 `ceil(100/10)×0.3`） | 两者不一致：若「释放 10 秒」是设计意图，需把 `sword_count` 提到 ≥340，或让实现以 duration 为准；当前以 `sword_count` 为准 |
| 3 | `SKILL_PASSIVE_DESC_000037` 文案为空 | 面板/技能说明可能显示空白，建议补文案（属独立小需求，本次未改） |

> 本轮仅只读核实，**未改动任何配置或代码**；探针输出见 `./file/jianling-skill-probe.txt`。

## 追加（第六轮）：本战三个被动技能效果核实（只读）

### 需求

> 「帮我看看这个被动技能是什么效果」（指代不明，按最可能的 Boss 被动「不灭残魂」为主答，并一并列出同战另两个被动）

### 三个被动效果对照

| 被动 | 携带者 | effect | 配置值 | 每级成长 | 实际效果（技能 lv1） |
|------|--------|--------|--------|----------|----------------------|
| `passive_000037` 不灭残魂 | 上古剑灵残魂（Boss） | `effect_100089` | `[1, 1, 0.2, 1]` | `[0, 0, +0.03, 0]` | 死亡后 **100% 概率、1s 后以 20% 最大生命复活，每场最多 1 次**（lv5：32% 血） |
| `passive_000035` 怒意叠锋 | 双首妖狼 | `effect_100087` | `[0.25]` | `[+0.025]` | **每恢复 1 点怒气，本场战斗累计 +0.25 物理伤害**（lv5：0.35/点）；实现：`gain_rage()` 累加到 `effect_100087_stack` buff（`is_combat_alive`，战斗内有效） |
| `passive_000036` 咒音回弹 | 噬魂妖将 | `effect_100088` | `[0.5, 0.5, 2]` | `[+0.02, 0, 0]` | **单体指向技能 50% 概率弹射至另一敌人，伤害衰减至 50%，最多弹 2 次**（lv5：概率 58%）；实现：`_handle_zhouyin_chain()`，仅对 `entity_type == "directed"` 生效 |

### 两处发现（待拍板，本次未改）

| # | 发现 | 说明 |
|---|------|------|
| 1 | `SKILL_PASSIVE_DESC_000035`（怒意叠锋）文案写「每恢复1点怒气，本场战斗增加**0.5**物理伤害」，但 effect 基础值只有 **0.25**（lv5 也只为 0.35） | 文案与配置不一致，二者需对齐（要么改 effect 为 0.5，要么改文案） |
| 2 | `SKILL_PASSIVE_DESC_000037`（不灭残魂）为空字符串，而 `EFFECT_100089_DESC` 已有完整描述 | 面板显示空白；建议把效果描述补回 `SKILL_PASSIVE_DESC_000037`（与前一条同一类文案问题） |

### 证据链

| # | 层面 | 证据 |
|---|------|------|
| 1 | 配置 | `skill_passive.json`：`passive_000035→[effect_100087]`、`passive_000036→[effect_100088]`、`passive_000037→[effect_100089]` |
| 2 | 数值 | `attack_effect.json`：`effect_100087=[0.25]/(+0.025)`、`effect_100088=[0.5,0.5,2]/(+0.02)`、`effect_100089=[1,1,0.2,1]/(0,0,+0.03,0)` |
| 3 | 实现 | `data_combat_character.gd:826` 怒意叠锋累加；`attack_entity_hit_handler.gd:3860` 咒音回弹弹射；`character_effect_handler.gd:732/754/802` 不灭残魂复活 |
| 4 | 文案 | `text.csv`：`SKILL_PASSIVE_DESC_000035=…0.5物理伤害`、`SKILL_PASSIVE_DESC_000036=单体攻击技能有50%概率衰减至50%弹射至另一敌人，最多2次`、`SKILL_PASSIVE_DESC_000037=""` |

> 本轮仅只读核实，未改动任何配置或代码。

## 问题与阻塞

| 问题 | 状态 | 备注 |
|------|------|------|
| 无 | — | 本次为只读核实，无阻塞 |

## 附件（file/）

| 文件 | 说明 |
|------|------|
| `./file/huanyin-skill-probe.txt` | headless 探针输出：幻音妖后及同级 Boss 的技能配置 vs 运行时已学/已装备技能 |
| `./file/combat-106009-probe.txt` | headless 探针输出：`combat_106009` 改后构成与落位（队伍 1/2/4 人下均为 1 幻音妖后 + 3 魇影，断言 PASS） |
| `./file/tower-boss-combats-probe.txt` | headless 探针输出：全塔 5 场守关 Boss 战（`combat_106002` + `106008~106011`）构成与落位（30 断言 PASS） |
| `./file/jianling-skill-probe.txt` | headless 探针输出：五层 Boss 上古剑灵残魂（`monster_900025`）的技能配置/运行时装载/击体参数/不灭残魂效果值/怒气槽上限（120）全塔怒耗对照 |

临时探针脚本（不入 git）：`../../../work_record_temp/2026-09/2026-09-11/scripts/`下的 `check_huanyin_skill.gd`、`check_combat_106009.gd`、`check_tower_boss_combats.gd`。

## 相关链接

- 项目：`D:\godot\projects\text-turn-game`（远端 `https://gitee.com/sdf2311d/text-turn-game.git`，分支 `master`）
- 本次基线提交：`6fbf042d`（本轮实施后 `origin/master` = `04bc7bf0`）
- 相关文件：`assets/config/monster/monster_106002.json`、`assets/config/skill_action.json`（action_100075）、`assets/config/combat.json`（combat_106009）、`src/managers/res_manager.gd`、`src/tools/attack_entity_hit_handler.gd`

## 明日计划 / 后续跟进

- [ ] 真机验收：五层守关 Boss 战均为 1 Boss + 3 普通怪（不再 4 只 Boss），战后对话能正常开门并移除 NPC
- [ ] 待拍板：五层上古剑灵战是否也加 3 只普通怪（涉难度与「剑术对决」叙事）
- [ ] 真机体验后评估难度：二层 3×魇影（梦魇 50% 沉睡×2 目标）/ 四层 3×罗刹（10 次 50% 均摊）/ 五层 2×噬魂妖将（500% 法术 + 减抗 30%）是否过强
- [ ] 等用户确认是否为幻音妖后补被动技能；如需要，按「同级 Boss 主动+被动」的标准补一条并加断言测试
- [ ] 如确认迷魂音波范围不符合「覆盖整层」的设计意图，评估改 `attack_radius` / 目标类型
- [ ] 五层剑灵：拍板剑雨「释放 10s vs 实际 3s 生成」与「随机落点」是否符合预期；并补 `SKILL_PASSIVE_DESC_000037`（不灭残魂）空白文案

## 变更记录

| 时间 | 变更说明 |
|------|----------|
| 2026-09-11 09:55 | 创建 job；写入核实结论与证据链；附 headless 探针输出 |
| 2026-09-11 10:10 | 追加第二轮：同技能核对、4 只幻音妖后根因（auto_count）、二层可用攻击怪约束、A/B/C 三个调整方案与实施要点（待选型） |
| 2026-09-11 10:35 | 按用户选定方案 A 实施：`combat_106009` 关闭 `auto_count` + 改为 1×幻音妖后 + 3×魇影（含落位），headless 断言 PASS，提交 `04bc7bf0` 并 push |
| 2026-09-11 11:00 | 第三轮：一/三/四层守关 Boss 统一为 1 Boss + 3 攻击型普通怪（含四层因 Boss/石魔无伤害技能改 3×罗刹），全部关闭 `auto_count`；headless 24 断言 PASS；提交 `d40d4c7d` 并 push；五层剑灵战待拍板 |
| 2026-09-11 11:15 | 第四轮：五层上古剑灵战同步改为 1 剑灵 + 双首妖狼 + 噬魂妖将×2，关闭 `auto_count`，落位统一；headless 探针扩至 5 场共 30 断言 PASS；提交 `634f6588` 并 push → 全塔五层守关 Boss 统一完成 |
| 2026-09-11 16:35 | 第五轮（只读）：核实五层最终 Boss「上古剑灵残魂」技能——主动 `action_100086` 万剑覆雨（120 怒 / 100 把剑 / 每把 50% 物伤 / 无附加效果）、被动 `passive_000037` 不灭残魂（100% 概率 1s 后 20% 血复活，每场 1 次）；实测怒气槽上限取 rage_cost=120 故可放出；记录「随机落点」「10s 释放 vs 3s 生成」「被动文案为空」三项待拍板 |
| 2026-09-11 18:20 | 第六轮（只读）：同战三个被动效果对照（不灭残魂 20% 血复活1次 / 怒意叠锋 每点怒气 +0.25 物伤 / 咒音回弹 50% 概率弹射 2 次）；新发现怒意叠锋文案 0.5 与 effect 0.25 不一致 |
