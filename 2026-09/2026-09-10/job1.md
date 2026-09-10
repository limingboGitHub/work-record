# Job: 调研当前应用能否添加飞书通信功能

## 基本信息

| 字段 | 内容 |
|------|------|
| 日期 | 2026-09-10 |
| 项目/模块 | work-record / 工作流集成 |
| 状态 | 已完成 |
| 预估耗时 | 0.5h |
| 实际耗时 | ~0.3h |
| 关键字 | #飞书 #lark-cli #通信 #集成 #调研 |

## 任务描述

> 调研当前工作环境（MiMo Desktop Agent + work-record 工作流）能否添加飞书（Lark）通信能力，评估可行性、现有基础、接入路径与阻塞点。

## 关联工作（文件索引）

| 关系 | 文件路径 | 说明 |
|------|----------|------|
| 前序（续做来源） | | 首次调研 |
| 后续（续做去向） | | 待定：接入实施 job |

## 待办清单

- [x] 梳理当前应用形态与「通信」含义
- [x] 检查本机飞书工具链（lark-cli / skills）
- [x] 核验应用配置与认证状态
- [x] 评估可落地的通信场景与接入路径
- [x] 写出结论与后续建议
- [x] 配置 bot 应用凭证并验证连通
- [x] 把 bot 拉进目标群，验证发消息
- [x] 配置事件订阅并验证实时收消息（p2p）
- [x] 按用户要求收口为**仅私聊**（不用群聊）
- [x] 私聊任务格式联调（收任务 → 执行 → 回写）
- [x] 按 cc-connect 架构部署独立飞书桥接
- [x] 安装并切换 Agent 为 Pi + DeepSeek
- [ ] 在飞书私聊验证 Pi 任务执行
- [ ] 配置 allow_from 限制可访问用户
- [ ] （可选）daemon 开机自启（计划任务需管理员）

## 进度记录

### 10:36 - 明确调研范围

当前仓库 `work-record` 是**工作记录库**（按月/天/job 的 Markdown 结构），本身不是业务应用。这里的「当前应用」按实际工作环境理解为：

1. **MiMo Desktop Agent 会话**（可执行工具、调用 CLI）
2. **work-record 工作流**（记录 job、进度、关联索引）

「飞书通信功能」按 IM 语义理解为：**收发消息、群聊、回复、事件订阅**（而非电信级通信）。

### 10:37 - 检查本机工具链

| 项 | 结果 |
|----|------|
| lark-cli | 已安装，路径 `D:\nodejs\node_global\lark-cli.cmd`，版本 **1.0.23**（可升级至 1.0.94） |
| PowerShell 策略 | `lark-cli.ps1` 被 Execution Policy 拦截，需用 `.cmd` 调用 |
| Agent Skills | 已装全套 lark-* skills（im / event / contact / doc / calendar 等 20+） |
| 飞书开放接口 | `open.feishu.cn`、`mcp.feishu.cn` 均可达 |

### 10:38 - 核验配置与认证（lark-cli doctor）

| 检查项 | 状态 | 说明 |
|--------|------|------|
| cli_version | pass | 1.0.23 |
| cli_update | warn | 可升到 1.0.94 |
| config_file | pass | config.json 存在 |
| app_resolved | pass | 应用 `cli_aac9a85162f81bb4`（飞书），workspace: **hermes** |
| token_exists | **fail** | **当前无用户登录**（user_access_token 缺失） |
| endpoint_open | pass | 开放平台可达 |
| endpoint_mcp | pass | MCP 端点可达 |

**关键结论：应用侧已配置，认证侧未完成登录。**

### 10:39 - 能力矩阵（可做的通信能力）

| 能力 | 支持情况 | 主要依赖 | 说明 |
|------|----------|----------|------|
| 发消息到群 / 私聊 | ✅ 可用 | `lark-cli im +messages-send` | text / markdown / post / 媒体；需 bot 在群内或 user 已授权 |
| 回复消息（含话题） | ✅ 可用 | `+messages-reply` | 支持 thread |
| 拉取消息 / 搜消息 | ✅ 可用 | `+chat-messages-list` / `+messages-search` | search 需 user 身份 |
| 建群 / 改群 / 成员管理 | ✅ 可用 | `+chat-create` 等 | create 偏 bot 身份 |
| 实时事件订阅 | ✅ 可用 | `lark-cli event consume` | NDJSON 流；适合机器人收消息 |
| 通讯录解析（姓名↔open_id） | ✅ 可用 | lark-contact skill | 发消息前解析收件人 |
| 卡片消息（interactive） | ⚠️ 部分 | 原生 API | 事件订阅侧卡片暂不做 compact 转换 |
| work-record 自动同步到飞书 | ⚠️ 需定制 | 无现成 skill | 可用 im/docs 自行编排 |

### 10:40 - 可行性结论

**可以添加飞书通信功能，技术路径已具备。**

- **结论：可行（条件具备，差登录与场景编排）**
- 已具备：CLI + 应用配置 + 全套 Agent Skills + 网络连通
- 阻塞：`token_exists = fail`，尚未 `auth login`
- 风险：bot 身份与 user 身份权限差异大；发消息前需确认群/用户 ID 与 scope

### 10:41 - 推荐接入路径（按优先级）

1. **最小闭环（推荐先做）**  
   用户登录 → 选一个测试群 → Agent 用 `im +messages-send` 发一条 job 日报摘要。  
   验证：身份、scope、发送链路全通。

2. **工作流增强**  
   收尾 job 时自动：勾待办 → 写进度 → 发飞书「今日 job 摘要」到指定群/私聊。

3. **双向通信（进阶）**  
   `lark-cli event consume` 监听消息事件，把飞书指令（如「查昨天 job」）映射为 Agent 动作。需要事件订阅配置与长期运行进程。

4. **文档协同**  
   非「通信」但常一起做：`lark-doc` / `lark-wiki` 把 job 同步为飞书文档。

### 10:42 - 下一步建议

| 优先级 | 动作 | 备注 |
|--------|------|------|
| P0 | ~~`auth login`~~ | 用户登录被 strict-mode 拦截，已改走 bot |
| P1 | 配置 bot 应用凭证并验证 | **已完成** |
| P2 | 把 bot 拉进目标群，跑通单条发送 | 待操作 |
| P3 | （可选）升级 lark-cli 1.0.23 → 1.0.94 | doctor warn |
| P4 | 若正式接入：新建实施 job，写发送模板与触发约定 | 本 job 仅调研+配置 |

### 10:45 - 用户登录被管理员策略拦截

尝试 `auth login`（IM scope）失败：

```text
strict mode is "bot", only bot identity is allowed.
This setting is managed by the administrator and must not be modified by AI agents.
```

- 旧应用 `cli_aac9a85162f81bb4`：`strict-mode: bot`，禁止 user 身份
- 无法也**不应**由 Agent 修改该策略

### 10:48 - 配置新 bot 凭证（用户提供）

用户提供新应用，已通过 `config init --app-secret-stdin` 写入：

| 项 | 值 |
|----|-----|
| appId | `cli_aac8e5e434b8dbeb` |
| brand | feishu |
| 配置文件 | `C:\Users\67568\.lark-cli\hermes\config.json` |
| secret | 已写入（不在 job 中记录明文） |

### 10:49 - 验证 bot 连通

| 检查 | 结果 |
|------|------|
| doctor / app_resolved | pass：`cli_aac8e5e434b8dbeb (feishu)` |
| strict-mode | **off**（新应用无 bot-only 限制） |
| default-as | auto；当前实际 identity 为 **bot** |
| `im chats list` | **success**（code 0）；当前 bot 所在群列表为空 |

**结论：bot 凭证可用，通信 API 已打通。下一步需把机器人拉进目标群后才能发消息。**

### 10:50 - 发消息连通验证（成功）

| 项 | 值 |
|----|-----|
| 群名 | 排市 |
| chat_id | `oc_ef2f66f3fe0425db256abfcfee30c562` |
| 身份 | bot |
| message_id | `om_x100b6515fe5008a0b30509e659abdcc` |
| 时间 | 2026-09-10 10:50:50 |
| 结果 | `ok: true` |

已发送文本：`【连通测试】来自 work-record 工作流的 bot 消息。飞书通信链路已打通。`

**调研闭环：当前应用可以添加飞书通信功能，bot 路径已跑通。**

### 11:10 - 真实需求收敛为「实时收任务」

用户确认选路径 1：飞书发消息触发 Agent（实时）。  
已给出开发者后台配置清单（bot 能力 + 长连接事件订阅 `im.message.receive_v1` + 权限：p2p / group_at_msg / 可选 group_msg）。  
CLI 侧 `event consume` + WebSocket 已验证可连，等待后台配置后联调。

### 11:12 - 实时收消息联调成功（p2p）

用户确认后台已启用 `im.message.receive_v1` + 权限。监听 120s，3 秒内收到：

| 字段 | 值 |
|------|-----|
| content | `测试消息` |
| chat_type | p2p |
| chat_id | `oc_3940a11afa94a3c57e7ec5ac8bae9a55` |
| sender_id | `ou_45f18a27baa23812ecf16cb75d5f9d93` |
| message_id | `om_x100b65164eebf0a4b03330cd1203a96` |

已 bot 回复确认，双向打通。  
**结论：实时「飞书 → Agent」可行，当前 p2p 路径已跑通。**

### 11:16 - 收口为私聊任务通道

用户明确：**不要群聊，只用私聊**。

| 项 | 值 |
|----|-----|
| 会话 | p2p / bot |
| chat_id | `oc_3940a11afa94a3c57e7ec5ac8bae9a55` |
| sender | `ou_45f18a27baa23812ecf16cb75d5f9d93` |
| 监听 | PS Job `feishu-p2p`，`event consume im.message.receive_v1` |
| 落盘 | `../work_record_temp/2026-09/2026-09-10/output/feishu-p2p-inbox.ndjson` |
| 状态 | WebSocket connected，常驻收单聊 |

群聊路径不再作为默认。

### 11:19 - 首条私聊任务闭环成功

| 步骤 | 结果 |
|------|------|
| 收 | `content`: **当前工作目录是什么**（p2p，event `744bb53aac260b2b3d60fa44db72b951`） |
| 做 | 答案：`D:\projects\work-record` |
| 回 | 已 bot 回写到同一 p2p 会话 |

注意：inbox 用 PowerShell 默认编码读会乱码，需 `Get-Content -Encoding UTF8`。

**私聊派任务路径完整可用。**

### 11:25 - 修正目标架构：纯飞书闭环

用户指出：最终应 **只通过飞书收发**，不需要在 MiMo 会话里再说话。

正确链路：

```text
飞书私聊 → 常驻监听落盘 inbox
         → 自动循环消费 inbox（去重）
         → 执行任务
         → lark-cli 回写飞书
```

已做：
- 常驻 Python 监听 `listen_feishu_p2p.py`
- cron 循环 `*/1 * * * *`（job `94afb466`）自动读 inbox、执行、飞书回写
- 已处理消息移入 `feishu-p2p-processed.ndjson`

限制（需知悉）：
- 循环在**本会话打开且空闲**时才触发；关掉 MiMo 会话即停
- 若需 7×24 不开会话：要 durable 定时任务，或独立服务（非本会话 loop）

### 11:35 - 改用 cc-connect 正确架构（用户指出）

用户反馈 inbox+cron 方案失败，建议参考开源 **[chenhg5/cc-connect](https://github.com/chenhg5/cc-connect)**。

正确架构（与错误方案对比）：

| | 错误方案 | cc-connect |
|--|----------|------------|
| 处理者 | 本 MiMo 会话 + cron | **独立常驻进程** |
| 依赖桌面会话 | 是 | **否** |
| Agent | 无完整 CLI 会话 | 直接 spawn **Claude Code CLI** |
| 链路 | 飞书→文件→会话轮询 | 飞书 WS → cc-connect → claude |

本机资产：
- `claude` CLI 2.1.263（WinGet）
- `cc-connect` npm v1.5.0 / amd64 二进制可用（ARM64 包不可用）
- 已有历史 `~/.cc-connect/config.toml`（其它项目）

已做：
1. 取消无效 cron `94afb466`，停掉 lark event 监听（避免 WS 冲突）
2. 写独立配置 `~/.cc-connect/config-work-record.toml`
   - agent: claudecode
   - work_dir: `D:\projects\work-record`
   - mode: yolo（远程免终端确认）
   - feishu app: `cli_aac8e5e434b8dbeb`
3. 用 Python DETACHED 启动 cc-connect（pid 22536）
4. 日志确认：`cc-connect is running` + `connected to wss://msg-frontier.feishu.cn`

**正确用法：只在飞书私聊机器人，不必开 MiMo 会话。**

### 12:43 - Agent 切换为 Pi

用户不想用 Claude Code，要求安装 Pi（cc-connect 支持的 Cursor Background Agent 系 CLI）。

| 项 | 结果 |
|----|------|
| 包名 | `@mariozechner/pi-coding-agent` |
| 本机 | 已有 `pi` 0.85.1（`D:\nodejs\node_global\pi.cmd`） |
| Provider | DeepSeek（环境变量 `DEEPSEEK_API_KEY` 已就绪，`auth check` ready） |
| 默认模型 | `deepseek-v4-pro`（已写 `~/.pi/agent/settings.json`） |
| cc-connect | `type = "pi"`，`mode = "yolo"`，已重启 |
| 日志 | `engine started agent=pi`；旧 claudecode 会话已失效重建 |

另写 `AGENTS.md` 供 Pi 使用 cc-connect cron/send 自然语言调度。

**飞书私聊现走 Pi + DeepSeek，不再依赖 Claude Code。**

### 12:57 - DeepSeek 新增模型并设为默认

| 项 | 值 |
|----|-----|
| 模型 ID | `deepseek-v4.1-flash-expires-on-0910` |
| 写入 | `~/.pi/agent/settings.json`（defaultModel + enabledModels） |
| 目录 | `~/.pi/agent/models-store.json` |
| cc-connect | `model = "deepseek/deepseek-v4.1-flash-expires-on-0910"` |
| 验证 | pi 直调该 ID 成功（custom model id，API 可用） |
| 状态 | cc-connect 已重启，agent=pi |

注意：模型名含 `expires-on-0910`，过期后需换回 v4-pro / v4-flash。

### 13:00 - 撤销自定义模型，改回默认 V4 Flash

用户取消 `deepseek-v4.1-flash-expires-on-0910`，改用官方默认 `deepseek-v4-flash`。

| 项 | 值 |
|----|-----|
| pi defaultModel | `deepseek-v4-flash` |
| enabledModels | v4-flash、v4-pro |
| models-store | 已移除自定义 ID |
| cc-connect | `model = "deepseek/deepseek-v4-flash"` |
| 状态 | 已重启，agent=pi |

### 13:01 - 修复 `Unknown option: --auto-approve`

飞书测试报错：`Error: Unknown option: --auto-approve`。

原因：旧二进制 **cc-connect 1.4.0-beta.2** 在 `mode=yolo` 时给 pi 传了已废弃参数；当前 pi 0.85.1 不识别。新版改用环境变量注入权限模式。

处理：
- 启动脚本改为 npm **cc-connect v1.5.0**（`D:\nodejs\node_global\node_modules\cc-connect\bin\cc-connect.exe`）
- 已重启，`agent=pi`，WS 已连

飞书侧建议先发 `/new` 开新会话再测。

### 13:05 - 思考力度默认改为 high

| 项 | 值 |
|----|-----|
| cc-connect | `thinking = "high"`（原 medium） |
| pi settings | `defaultThinking = "high"` |
| 模型 | `deepseek/deepseek-v4-flash` 不变 |
| 状态 | 已重启 |

## 问题与阻塞

| 问题 | 状态 | 备注 |
|------|------|------|
| 用户登录，无 user_access_token | 阻塞（策略） | 旧应用 strict-mode=bot，管理员限制；已改用 bot 身份 |
| PowerShell 无法直接执行 lark-cli.ps1 | 已解决 | 改用 `lark-cli.cmd` |
| bot 未加入任何群，`chats list` 为空 | 已解决 | 已加入「排市」，发消息成功 |
| 未明确「通信」具体场景（日报推送 / 收指令 / 群机器人） | 未解决 | 调研默认按 IM 收发覆盖；场景待用户确认后再实施 |

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
- 文档: 飞书开放平台 https://open.feishu.cn/document/ ；lark-cli https://github.com/larksuite/cli
- 日志/监控: `lark-cli doctor`

## 明日计划 / 后续跟进

- [x] 与用户确认要落地的通信场景 → 已选定 bot 发消息到「排市」并跑通
- [x] 把 bot 拉进目标群，验证发消息（bot 路径，不依赖 user login）
- [ ] 若需要 user 身份（搜消息、代表用户操作）：找管理员放开 strict-mode 或换可 user 登录的应用
- [ ] 若继续：升级 lark-cli 至最新版
- [ ] 若正式接入：另开实施 job，写发送规范与触发时机（如 job 收尾自动推日报）

## 变更记录

| 时间 | 变更说明 |
|------|----------|
| 2026-09-10 10:36 | 创建 job，完成可行性调研 |
| 2026-09-10 10:48 | 用户登录被 strict-mode 拦截；改配新 bot 凭证 `cli_aac8e5e434b8dbeb` 并验证连通 |
| 2026-09-10 10:50 | 定位群「排市」并成功发送测试消息，通信链路打通 |
| 2026-09-10 11:05 | 明确真实需求：接收飞书任务并执行（非单向推送）。event consume WS 可连，90s 内 0 条事件；读消息 API 230027 |
| 2026-09-10 11:10 | 用户选定实时路径；输出后台配置清单，待用户完成事件订阅与权限后联调 |
| 2026-09-10 11:12 | 后台配置生效；p2p 实时收到「测试消息」并回复确认，双向打通 |
| 2026-09-10 11:16 | 用户要求仅私聊；起常驻 P2P 监听（PS Job），事件写入 inbox NDJSON |
| 2026-09-10 11:18 | 改用独立 Python 进程挂住 stdin，监听常驻成功 |
| 2026-09-10 11:19 | 收到私聊任务「当前工作目录是什么」，已回复 `D:\projects\work-record`，闭环成功 |
| 2026-09-10 11:25 | 架构修正为纯飞书闭环；挂 1 分钟自动消费循环 94afb466 |
| 2026-09-10 11:35 | 放弃会话内循环；按 cc-connect 架构部署独立桥接进程，飞书↔Claude Code 打通 |
| 2026-09-10 12:43 | 按用户要求安装/启用 Pi，DeepSeek 为默认模型，cc-connect agent 切换为 pi |
| 2026-09-10 12:57 | 添加 DeepSeek 模型 deepseek-v4.1-flash-expires-on-0910 并设为默认，重启 cc-connect |
| 2026-09-10 13:00 | 撤销自定义模型，改回默认 deepseek-v4-flash |
| 2026-09-10 13:01 | 修复 --auto-approve：升级使用 cc-connect 1.5.0（npm） |
| 2026-09-10 13:05 | thinking/effort 默认改为 high |
| 2026-09-10 13:20 | job 本地提交 git（`1c062ed`），未推远程 |

### 13:25 - 关闭过程消息，只回最终结果

用户反馈飞书刷屏。改 display：

| 配置 | 原值 | 新值 |
|------|------|------|
| tool_messages | true | **false** |
| thinking_messages | false | false |

已重启 cc-connect。飞书 `/new` 后生效。
