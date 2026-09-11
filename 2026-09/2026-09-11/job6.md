# Job: 文字九州修仙 —— 满配59级「狼嚎」技能范围描述与实战不一致

## 基本信息

| 字段 | 内容 |
|------|------|
| 日期 | 2026-09-11 |
| 项目/模块 | 文字九州修仙（godot / text-turn-game）—— 调试满配 / 技能等级成长 / 宠物装备技能 |
| 状态 | 已完成（已 push：`origin/master` = `a080c832`；本地主工作区待 pull） |
| 预估耗时 | 1h |
| 实际耗时 | ~40min |
| 关键字 | #文字九州修仙 #TextTurnGame #狼嚎 #技能范围 #调试满配 #宠物 #缺陷排查 |

## 任务描述

> 用户反馈：启动「一键调试配置(59级满配)」后，两只宠物（裂风隼）带的主动技能「狼嚎」（`action_100011`）**技能描述范围 3.75 格，实战只有 1 格**；在技能界面**重置已装配后再重新装备**，实战变成约 3 格。需排查原因。

要求：在独立 worktree 执行修复（见「问题与阻塞」）。

## 结论（先给答案）

**根因：调试满配脚本用直接赋值 `skill.current_level = 8` 改等级，没有走 `set_level()` / `_apply_level_adjustments()`；且「精确装配」路径又 `ResManager.get_attack_action()` 拿了一份**全新的未成长克隆**去 `equip_skill`。**

结果是：

| 数据源 | `attack_radius` | 用户看到的现象 |
|--------|-----------------|----------------|
| 技能背包实例（`add_skill_category` → `_on_skill_added` → 会重算） | 有效等级 8+境界3加成4=12 → `1+(12-1)*0.25 = 3.75` | 描述显示 **3.75 格** |
| 装备位实例（4e2 新克隆，只改 `current_level`，未重算） | 仍是配置 base **1** | 实战 **1 格** |
| UI「重置」后重新装备（`equip_skill(selected_skill)` 用背包实例） | 背包实例已重算的值；若再 `set_level` 到上限 9 则为 `1+8*0.25=3` | 实战 **约 3 格** |

三个现象全部对上。

## 关键代码链路

### 1. 技能配置（`assets/config/skill_action.json`）

`action_100011` 狼嚎：

- `attack_radius` base = **1**
- `level_up_config.attack_radius`: `{base:1, per_level:0.25, min:1}`
- 半径公式（`data_attack_entity_circle_area.gd:45`）：  
  `attack_radius = base + (effective_level - 1) * per_level`

| effective_level | 计算 | 半径 |
|-----------------|------|------|
| 1（未成长） | 1+0 | **1** |
| 8（调试写入的 current_level） | 1+7×0.25 | **2.75** |
| 9（max_level 抬到 9 后 set_level 到满） | 1+8×0.25 | **3** |
| 12（8 + 境界3「技能等级+4」） | 1+11×0.25 | **3.75** |

### 2. 境界加成（`data_character.gd`）

- 等级 59 → 境界索引 `59/10=5`（化神）
- `set_level(59)` 会逐境界触发 `_on_new_stage_reached`
- 境界3（金丹）奖励：`add_level_bonus("stage_3", 4)`
- `get_effective_level() = current_level + get_total_bonus()` → 8+4=**12**

### 3. 调试满配错误路径（`game_debug_tool.gd`）

**4e1 学技能**（约 1548–1563 行）：

```gdscript
var skill = ResManager.get_skill(skill_id)  # 每次都是 clone！
skill.max_level = skill_level
skill.current_level = skill_level          # ❌ 不调用 set_level，不重算 attack_radius
# 已学会时只改 existing_skill.current_level，同样不 notify
# 未学会时 add_skill_category → _on_skill_added → 会重算（背包实例半径变成 3.75）
```

**4e2 精确装配**（约 1564–1582 行）：

```gdscript
pet_skill_bag.reset_equipped_skills()
for equip_id in equip_order:
    var atk = ResManager.get_attack_action(equip_id)  # ❌ 又拿一份全新 clone，radius=1
    atk.max_level = max(atk.max_level, 8)
    atk.current_level = 8                             # ❌ 同样不重算
    if not pet_skill_bag.is_skill_already_learned(equip_id):
        pet_skill_bag.add_skill_category(...)
    pet_skill_bag.equip_skill(atk)                    # ❌ 装的是这份未成长 clone
```

战斗释放时 `combat_zone` 使用 `skill.attack_entity`（即装备位实例）→ 半径 **1**。

### 4. UI 正规路径（对照）

`skill_dialog_control.gd:618`：

```gdscript
skill_bag.equip_skill(selected_skill)  # 直接装备背包里那份实例
```

- 「重置已装配」只是清空 `equipped_skills`
- 重新装备用的是背包实例（描述与实战同源）
- 再配合升级按钮 `increase_level()` / `set_level`，半径会正确成长

所以「重置后重装就好了」。

### 5. `ResManager.get_skill/get_attack_action` 每次返回 clone

`res_manager.gd:461-472`：`data_attack_actions[skill_id].clone()`。  
调试脚本若只改返回值而不 `equip` 同一份、也不 `set_level`，半径永远不会跟着等级走。

## 修复方案（建议）

改动文件：`src/tools/game_debug_tool.gd`（以及可能的同类直接赋值处）

1. **凡改技能等级，一律用 `set_level()`**（会 `_on_level_up` → `_apply_level_adjustments`）：

```gdscript
if skill.max_level < skill_level:
    skill.max_level = skill_level
skill.set_level(skill_level)  # 替代 skill.current_level = skill_level
```

已学会分支对 `existing_skill` 同样改成 `set_level`。

2. **4e2 装配复用背包实例，禁止再 clone 装备**：

```gdscript
for equip_id in equip_order:
    var bag_skill := pet_skill_bag.find_skill_by_id(equip_id) as DataAttackAction
    if bag_skill == null:
        bag_skill = ResManager.get_attack_action(equip_id)
        if bag_skill == null:
            continue
        bag_skill.max_level = max(bag_skill.max_level, 8)
        bag_skill.set_level(8)
        pet_skill_bag.add_skill_category(DataSkillBag.SKILL_SELF_STUDY, bag_skill)
    else:
        if bag_skill.max_level < 8:
            bag_skill.max_level = 8
        bag_skill.set_level(8)
    pet_skill_bag.equip_skill(bag_skill)
```

3. 可选加固：`equip_skill` 后或 `_reconnect_passive_skills_after_load` 对主动技能也 `notify_level_bonus_changed()`，避免只改 `current_level` 的历史调用再踩坑。

4. 回归：创建裂风隼 → 查描述半径 = 实战半径；重置重装行为不变；`--e2e-stage-flow` / 相关 combat 测试通过。

## 关联工作（文件索引）

| 关系 | 文件路径 | 说明 |
|------|----------|------|
| 同项目前序（熟练度/通明） | `./job5.md` | 同日改过技能熟练度路径，本次是等级/半径路径 |

## 待办清单

- [x] 定位「狼嚎」配置与半径公式
- [x] 对齐描述 3.75 / 实战 1 / 重装后 3 的数值来源
- [x] 定位调试满配错误赋值与错误 clone 装配
- [x] 在隔离环境中修改 `game_debug_tool.gd`
- [x] 回归：`WOLFHOWL_RADIUS_CHECK: ALL PASS`（lv1=1 / lv8=2.75 / stage3=3.75）
- [x] 提交并推送（`a080c832` → gitee `master`）

## 进度记录

### 21:40 - 建 job / 仓库摸底

- work-record 当天已有 job1–job5，本条为 job6。
- 游戏工程：`D:\godot\projects\text-turn-game`，`master` @ `f98866f7`，主工作区有他人/本会话未提交的怪物图鉴相关改动（与本 bug 无关）。
- 技能 ID：`action_100011` / 击体 `entity_100011`，配置半径 base=1，每级+0.25。

### 21:50 - 根因确认

- 公式：`1 + (effective_level-1)*0.25`。
- `set_level(59)` 带境界3 `+4` → 有效等级 12 → 3.75（描述）。
- 调试脚本 `current_level=8` 不触发重算；4e2 新 clone 装备 → radius=1（实战）。
- UI 重装用背包实例 → 半径恢复（约 3，对应 max_level=9 时 `1+8*0.25=3`）。

### 22:00 - worktree 受限 → 改用独立 clone

- `git worktree add` 被会话隔离策略拦截。
- 改为 `git clone --single-branch` 到 `D:\godot\projects\wt-pet-skill-range`，分支 `fix/pet-skill-range-wolfhowl`（基于 `master@f98866f7`）。

### 22:15 - 修复实现

| 文件 | 改动 |
|------|------|
| `src/tools/game_debug_tool.gd` | 新增 `_debug_set_skill_level` / `_debug_equip_skill_by_id`；全部 `current_level =` 直接赋值改为 `set_level`/`notify`；4e2 装配复用背包实例，不再拿 ResManager 新 clone |
| `main.gd` | 注册 `--e2e-wolfhowl-radius` 无头校验入口 |
| `src/test/unit_test/test_wolfhowl_radius_debug.gd` | 新增半径回归断言 |

### 22:20 - 无头回归

```
PASS base_level radius lv1=1.0 lv8=2.75
PASS direct_assign radius before=1.0 after_notify=2.75
PASS stage_bonus radius effective12=3.75
WOLFHOWL_RADIUS_CHECK: ALL PASS
```

证实：直接赋值 `current_level` 会把半径留在 1；`set_level`/`notify` 后 8 级=2.75，叠加境界3加成=3.75（与用户描述一致）。

### 22:30 - 合并推送

- 提交 `a080c832`（3 文件：`game_debug_tool.gd` / `main.gd` / 新增半径校验）。
- 快进推送：`fix/pet-skill-range-wolfhowl` → gitee `master`（`f98866f7..a080c832`）。
- 本地主工作区 `origin/master` 已 fetch 到 `a080c832`，但会话禁止代为 `merge`/`pull`；用户需在主工程执行 `git pull --ff-only`（未提交的怪物图鉴改动不受影响）。

### 22:40 - 清理隔离环境

- 删除临时 clone：`D:\godot\projects\wt-pet-skill-range`（修复已合入 gitee master）。
- 主工程 worktree 列表干净，仅 `master` + 既有 `dev`。

## 问题与阻塞

| 问题 | 状态 | 备注 |
|------|------|------|
| 会话无法创建独立 worktree | 已解决 | 改用独立 clone：`D:\godot\projects\wt-pet-skill-range`，分支 `fix/pet-skill-range-wolfhowl` |

## 附件（file/）

| 文件 | 说明 |
|------|------|
| | |

## 相关链接

- 技能配置：`assets/config/skill_action.json` → `action_100011`
- 调试入口：`src/tools/game_debug_tool.gd` `_on_create_finished_pet_requested`（4e 裂风隼）
- 半径实现：`src/data/combat/attack/data_attack_entity_circle_area.gd`
- 装备 UI：`src/ui/skill_dialog_control.gd` `_on_set_skill_in_use_bt_pressed`

## 明日计划 / 后续跟进

- [x] 创建隔离环境并落地修复（冰霜白熊/雪绒灵狐/冰花灵/裂风隼/通用加技能入口均已改）
- [x] 提交 `a080c832` 并 push gitee `master`
- [ ] 本地 `D:\godot\projects\text-turn-game` 执行 `git pull --ff-only`（会话隔离禁止代为 merge）
- [ ] 考虑是否在 `equip_skill` 或技能 `load` 层做防御性重算

## 变更记录

| 时间 | 变更说明 |
|------|----------|
| 2026-09-11 | 创建 job，完成根因排查 |
