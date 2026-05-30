# Crush.skill

一个可以放在飞书里的 AI 恋爱对象项目。

它不是简单的聊天转发脚本，而是一个带有：
- 人格模板
- 关系阶段推进
- 用户独立状态
- 角色创建流程
- 可扩展风格库

的轻量陪伴型机器人原型。

> 当前优先适配飞书机器人。飞书接入细节见 [config-feishu.md](./config-feishu.md)。

---

## 项目亮点

- 支持飞书私聊机器人接入，消息链路清晰
- 每个用户拥有独立的关系阶段、好感度和最近记忆
- 支持在聊天中通过 `/crush` 一步步创建自己的专属角色
- 支持把生成的人格绑定到当前用户，不再共用单一默认设定
- 恋爱风格已经抽成独立风格库，便于继续扩展更多角色类型
- 支持 `zhipu`、`deepseek`、`openai` 风格的标准 `chat completions` 接口

---

## 适合做什么

- 深夜陪伴型聊天机器人
- 情绪陪伴 / 轻社交练习
- 角色扮演式 AI Companion 原型
- 飞书内的 AI 助手 / 娱乐型 Bot
- 多 persona 聊天体验实验

---

## 当前能力

### 1. 角色创建

用户可以直接在飞书里发 `/crush` 进入创建流程，然后逐步回答：
- 名字
- 性别
- 年龄段
- MBTI
- 恋爱风格
- 主动度
- 回复节奏
- 关心方式
- 浪漫方式
- 吃醋表现
- 口头禅 / 表情 / 称呼 / 爱好
- 初始关系阶段

确认后会自动生成独立的 `personality.md`，并绑定到当前用户。

### 2. 关系推进

项目内置基础关系状态机：

```text
陌生 -> 认识 -> 暧昧 -> 表白 -> 恋爱 -> 磨合 -> 长期
```

机器人会根据互动内容累计好感度，并自动推进关系阶段。

### 3. 风格差异

当前已经内置多种风格模板：
- 温柔粘人
- 高冷傲娇
- 热情主动
- 成熟稳重
- 甜酷拽
- 理性冷静
- 幽默风趣
- 被动慢热

这些风格不是只换标签，而是会影响：
- 日常说话方式
- 表达喜欢的方式
- 约会偏好
- 联系频率
- 吃醋方式
- 冲突反应
- 和好方式

### 4. 用户独立状态

每个飞书用户会单独保存：
- 当前 persona
- 当前关系阶段
- 当前好感度
- 累计对话轮数
- 最近对话
- 简单长期记忆

状态默认写入本地 SQLite：`./data/crush.db`

---

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

---

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

然后填写：
- `FEISHU_APP_ID`
- `FEISHU_APP_SECRET`
- `FEISHU_WEBHOOK_URL`
- `AI_API_KEY`
- `AI_PROVIDER`
- `AI_MODEL`

推荐优先使用 `.env`，项目启动时会自动读取。

### 3. 启动服务

```bash
python tools/run_feishu.py
```

默认监听：
- `APP_HOST=0.0.0.0`
- `APP_PORT=5001`

### 4. 接入飞书

飞书应用配置、Webhook、权限和事件订阅说明见：

- [config-feishu.md](./config-feishu.md)

---

## 项目结构

```text
crush-default/           默认人格设定
crush_service/           服务核心模块
personas/                按用户生成的角色文件
prompts/                 创建流程与人格模板参考
tests/                   基础单元测试
tools/run_feishu.py      启动入口
tools/mbti_lib.py        MBTI 匹配逻辑
```

### `crush_service/` 模块说明

- `app.py`：Flask 路由与消息主流程
- `config.py`：加载 `.env` / `config.json`
- `ai_client.py`：统一模型调用
- `feishu_client.py`：飞书鉴权与发消息
- `persona.py`：加载人格文件
- `persona_builder.py`：创建器与 persona 文本生成
- `style_library.py`：风格库，集中维护风格差异
- `prompting.py`：系统提示词组装
- `relationship.py`：关系阶段与好感度逻辑
- `state_store.py`：SQLite 状态存储
- `commands.py`：聊天命令处理

---

## 当前状态

目前这个仓库更接近一个“可用原型”，已经具备：
- 基础飞书消息收发
- 基础多用户状态隔离
- 人格创建与绑定
- 风格化 persona 输出
- 关系阶段推进
- 结构化长期记忆：偏好、称呼、近期安排、情绪线索和边界提醒
- 阶段事件提示：阶段变化时会写入关系事件，并在回应中使用阶段指导

还可以继续增强的方向包括：
- 基于模型的长期记忆总结与遗忘策略
- 更丰富的节日、纪念日和冲突修复事件
- 多渠道接入层
- 更完整的测试覆盖
- 更强的安全边界和危机场景处理

---

## 注意事项

- 这是 AI 陪伴项目，不是真实人类关系
- 如遇严重情绪困扰，请寻求现实中的专业帮助
- 请不要把敏感密钥提交到仓库

---

## 开发说明

- 默认人格文件在 [crush-default/personality.md](./crush-default/personality.md)
- 用户生成的人格文件会落在 `personas/`
- 本地状态数据库默认是 `./data/crush.db`
- 恋爱风格库在 [crush_service/style_library.py](./crush_service/style_library.py)

如果你想继续扩展风格，优先改 `style_library.py`，不要直接把新风格硬写进主流程。
