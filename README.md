# Crush.skill

Crush.skill 是一个优先适配飞书机器人的 AI 陪伴原型。它不只是把消息转发给大模型，而是围绕 persona、关系阶段、长期记忆和多用户状态做了一层轻量应用逻辑。

> 飞书接入、Webhook、权限和事件订阅配置见 [config-feishu.md](./config-feishu.md)。

## 核心能力

- **飞书私聊机器人**：接收飞书文本消息，调用模型生成回复，再发送回用户。
- **用户独立状态**：每个飞书用户单独保存 persona、关系阶段、好感度、对话轮数、最近对话和长期记忆。
- **角色创建流程**：用户可在聊天里通过 `/crush` 逐步创建自己的恋爱对象设定。
- **风格化 persona**：内置多种恋爱风格模板，影响语言、关心方式、吃醋表现、冲突反应和和好方式。
- **关系阶段推进**：根据互动内容累计好感度，并在阶段变化时写入阶段事件。
- **结构化长期记忆**：从用户消息中提取偏好、称呼、近期安排、情绪线索和边界提醒。
- **多模型接入**：支持 `zhipu`、`deepseek`、`openai` 风格的标准 `chat completions` 接口。

## 适用场景

- 飞书内的 AI 娱乐机器人
- 角色扮演式 AI Companion 原型
- 情绪陪伴和轻社交练习
- 多 persona 聊天体验实验
- 带状态机的聊天应用 demo

## 工作流

```text
飞书用户
  -> 飞书事件回调
  -> Flask Webhook
  -> 命令处理 / 状态读取
  -> persona + 记忆 + 阶段规则组装 prompt
  -> 大模型生成回复
  -> 更新关系状态和长期记忆
  -> 飞书机器人回复用户
```

## 当前能力详情

### 角色创建

用户发送 `/crush` 后，会逐步录入：

- 名字、性别、年龄段
- 用户 MBTI 和目标 MBTI
- 恋爱风格、主动度、回复节奏
- 关心方式、浪漫方式、吃醋表现
- 口头禅、表情、称呼、小爱好
- 初始关系阶段

确认后会生成独立的 `personality.md`，并绑定到当前飞书用户。

### 关系阶段

内置阶段顺序：

```text
陌生 -> 认识 -> 暧昧 -> 表白 -> 恋爱 -> 磨合 -> 长期
```

每个阶段都有独立回应指导。关系升级时会写入阶段事件，例如从“陌生”进入“认识”后，机器人会更主动记住用户偏好，但仍保持边界感。

### 风格模板

当前内置风格：

- 温柔粘人
- 高冷傲娇
- 热情主动
- 成熟稳重
- 甜酷拽
- 理性冷静
- 幽默风趣
- 被动慢热

风格模板集中维护在 [crush_service/style_library.py](./crush_service/style_library.py)。

### 长期记忆

当前记忆系统会从用户消息中提取并保存：

- 偏好：例如喜欢的地方、食物、内容
- 称呼：例如用户希望被怎么叫
- 近期安排：例如考试、面试、加班、约会
- 情绪线索：例如累、焦虑、开心、难过
- 边界提醒：例如不喜欢、害怕、明确提出不要的事

状态默认写入本地 SQLite：`./data/crush.db`。

## 常用命令

| 命令 | 作用 |
|------|------|
| `/crush` | 开始创建专属恋爱对象 |
| `/crush preview` | 预览当前创建中的设定 |
| `/crush confirm` | 确认并生成角色 |
| `/crush cancel` | 取消本次创建 |
| `/crush-status` | 查看阶段、好感度、对话轮数 |
| `/crush-set-stage 暧昧` | 手动调整关系阶段 |
| `/crush-persona` | 查看当前绑定角色 |

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制模板：

```bash
cp .env.example .env
```

填写必要配置：

```dotenv
FEISHU_APP_ID=your_feishu_app_id
FEISHU_APP_SECRET=your_feishu_app_secret
FEISHU_WEBHOOK_URL=https://your-domain.example/webhook

AI_API_KEY=your_api_key
AI_PROVIDER=zhipu
AI_MODEL=GLM-4.5-Air
```

推荐优先使用 `.env`，项目启动时会自动读取。

### 3. 启动服务

```bash
python3 tools/run_feishu.py
```

默认监听：

- `APP_HOST=0.0.0.0`
- `APP_PORT=5001`

### 4. 配置飞书

按照 [config-feishu.md](./config-feishu.md) 创建飞书应用、开启机器人能力、配置事件订阅和 Webhook。

## 项目结构

```text
crush-default/             默认人格设定
crush_service/             服务核心模块
  app.py                   Flask 路由与消息主流程
  ai_client.py             大模型调用封装
  commands.py              聊天命令处理
  config.py                .env / config.json 配置加载
  feishu_client.py         飞书鉴权与发消息
  memory.py                结构化长期记忆提取
  persona.py               persona 文件加载
  persona_builder.py       创建器与 persona 文本生成
  prompting.py             系统提示词组装
  relationship.py          关系阶段、好感度和阶段事件
  state_store.py           SQLite 状态存储
  style_library.py         恋爱风格库
personas/                  按用户生成的角色文件
prompts/                   创建流程与人格模板参考
tests/                     基础单元测试
tools/run_feishu.py        启动入口
tools/mbti_lib.py          MBTI 匹配逻辑
```

## 测试

```bash
python3 -m unittest discover tests
```

当前测试覆盖配置加载、prompt 组装、关系推进、记忆提取、persona 创建和风格差异。

## 当前状态

这是一个可运行的原型项目，已经具备飞书消息收发、多用户状态隔离、角色创建、风格化 persona、关系阶段推进、结构化记忆和阶段事件提示。

后续可以继续增强：

- 基于模型的长期记忆总结与遗忘策略
- 更丰富的节日、纪念日和冲突修复事件
- 多渠道接入层
- 更强的安全边界和危机场景处理
- 更完整的线上部署和观测能力

## 安全边界

- 这是 AI 陪伴项目，不是真实人类关系。
- 不应诱导用户与现实世界隔离或形成极端依赖。
- 如遇严重情绪困扰、自伤或伤人风险，应建议用户尽快联系现实中的专业支持与身边可信任的人。
- 不要把 `.env`、API Key、飞书 App Secret 等敏感信息提交到仓库。

## 开发提示

- 默认人格文件在 [crush-default/personality.md](./crush-default/personality.md)。
- 用户生成的人格文件会落在 `personas/`。
- 本地状态数据库默认是 `./data/crush.db`。
- 扩展恋爱风格时优先修改 [crush_service/style_library.py](./crush_service/style_library.py)，不要把新风格硬写进主流程。
