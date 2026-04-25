# 飞书接入配置指南

本指南帮助你将 Crush.skill 接入飞书，实现与恋爱对象的实时对话。

---

## 方案架构

```
用户(飞书) → 飞书应用 → 接收消息 → AI大模型 → 发送回复 → 用户
```

---

## Step 1：创建飞书应用

### 1.1 创建应用

1. 打开 [飞书开放平台](https://open.feishu.cn/)
2. 点击「创建企业自建应用」
3. 填写应用名称（如 `Crush 恋爱助手`）
4. 选择目标企业 → 创建

### 1.2 获取凭证

创建成功后，在应用详情页获取：
- **App ID**：`cli_xxxxxxxxxxxxxx`
- **App Secret**：在「凭证与基础信息」页查看

---

## Step 2：配置应用能力

### 2.1 添加机器人能力

1. 在应用详情页 → 「添加应用能力」
2. 选择「**机器人**」
3. 确认启用

### 2.2 添加 Webhook 能力

1. 「添加应用能力」→ 选择「**Webhook**」
2. 填入你的回调地址（后面 Step 4 获取）

---

## Step 3：配置权限

### 3.1 进入权限管理

应用详情页 → 「权限管理」

### 3.2 添加以下权限

| 权限名称 | 权限码 | 说明 |
|---------|--------|------|
| 接收消息 | `im:message` | 接收用户消息 |
| 发送消息 | `im:message` | 发送回复消息 |
| 读取用户信息 | `contact:user.base:readonly` | 获取用户基本信息 |

### 3.3 发布应用

权限配置完成后：
1. 「版本管理与发布」→ 「创建版本」
2. 填写版本号和说明
3. 「申请发布」或「直接发布」

> 注意：企业版应用需要管理员审批，个人版可能自动通过。

### 3.4 获取应用凭证

在「凭证与基础信息」页面获取：
- **App ID**：`cli_xxxxxxxxxxxxxx`
- **App Secret**：需要单独获取，点击查看

### 3.5 获取 Webhook 地址

1. 「添加应用能力」→「Webhook」
2. 复制 Webhook 地址备用

---

## Step 4：敏感配置（重要）

由于配置文件中包含敏感信息，建议使用环境变量管理。

### 4.1 复制环境变量模板

```bash
cp .env.example .env
```

### 4.2 编辑 .env 文件，填入你的配置

```bash
# 飞书应用凭证（必填）
FEISHU_APP_ID=cli_xxxxxxxxxxxxxx          # Step 3.4 获取
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxxxxxxxx  # Step 3.4 获取
FEISHU_WEBHOOK_URL=https://xxxx.ngrok-free.dev/webhook  # Step 3.5 获取

# AI API 配置（必填）
AI_API_KEY=your_api_key                    # 从 AI 服务商获取
AI_PROVIDER=zhipu                          # 或 deepseek / openai
AI_MODEL=GLM-4.5-Air                      # 或其他你想要的模型

# 恋爱对象配置
CRUSH_NAME=小樱                            # 你的恋爱对象名字
CURRENT_STAGE=陌生                          # 当前关系阶段
PERSONALITY_PATH=./crush-enfp/personality.md  # 性格文件路径
```

### 4.3 配置来源说明

| 配置项 | 获取方式 |
|--------|----------|
| `FEISHU_APP_ID` | 飞书开放平台 → 应用详情 → 凭证与基础信息 |
| `FEISHU_APP_SECRET` | 飞书开放平台 → 应用详情 → 凭证与基础信息（点击查看） |
| `FEISHU_WEBHOOK_URL` | 飞书开放平台 → 添加应用能力 → Webhook |
| `AI_API_KEY` | 智谱 AI / DeepSeek / OpenAI 等平台获取 |
| `AI_MODEL` | 你的 AI 模型名称，如 `GLM-4.5-Air`、`deepseek-chat` 等 |

> **安全提醒**：`.env` 文件包含敏感凭证，请勿提交到 git 或公开分享。已配置 `.gitignore` 忽略此文件。

---

## Step 5：配置内网穿透

飞书需要回调到你的本地服务器，需要内网穿透工具。

### 使用 ngrok（推荐）

```bash
# 安装 ngrok
brew install ngrok

# 配置 authtoken（首次使用需要注册）
ngrok config add-authtoken <your-token>

# 启动穿透
ngrok http 5001
```

复制 ngrok 提供的 HTTPS 地址，格式类似：
```
https://xxxxxx.ngrok-free.dev
```

### 更新飞书 Webhook 地址

飞书开放平台 → 你的应用 → 「添加应用能力」→「Webhook」
- 填入：`https://xxxxxx.ngrok-free.dev/webhook`

---

## Step 6：安装依赖

```bash
pip install -r requirements.txt
```

---

## Step 7：启动机器人

```bash
# 设置环境变量
export $(cat .env | xargs)

# 启动
python3 tools/run_feishu.py
```

---

## Step 8：测试

1. 在飞书中搜索你的应用名称
2. 进入与机器人的私聊
3. 发送消息测试

机器人应该会根据 personality.md 中的设定进行回复。

---

## 事件订阅

如果需要订阅更多事件（如用户进入会话）：

1. 「事件配置」→ 「添加事件」
2. 选择需要的事件：
   - `im.message.receive_v1` - 接收消息（必须）
   - `im.chat.access_event.bot_p2p_chat_entered_v1` - 用户进入会话
3. 添加后需要重新发布应用

---

## 常见问题

### Q: 机器人不回复消息
A: 检查以下几点：
1. ngrok 是否正在运行
2. Webhook 地址是否配置正确
3. 应用是否已发布
4. `im.message.receive_v1` 事件是否已订阅

### Q: 消息发不出去
A:
1. 检查应用权限是否审批通过
2. 确认 `im:message` 权限已开通
3. 查看机器人日志排查错误

### Q: 消息回复太热情，不符合设定
A:
1. 重启机器人：`python3 tools/run_feishu.py`
2. 检查 personality.md 路径是否正确
3. 确认 current_stage 配置正确

### Q: 如何更换恋爱对象？
A:
1. 修改 `.env` 中的 `CRUSH_NAME`
2. 修改 `personality` 路径指向新的 personality.md
3. 重启机器人

### Q: 需要一直开着电脑吗？
A: 是的，需要运行 `run_feishu.py`。可以部署到服务器实现24小时运行。

---

## 进阶：部署到服务器

如需24小时运行：

1. 购买云服务器（阿里云/腾讯云）
2. 安装 Python 和依赖
3. 使用 `screen` 或 `systemd` 保持运行
4. Webhook 需要配置公网域名或使用内网穿透
