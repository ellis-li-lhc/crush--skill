#!/usr/bin/env python3
"""
飞书恋爱对象机器人 - 支持公网回调

需要：
1. 先运行 ngrok http 5000 得到公网地址
2. 把地址配置到飞书应用的Webhook
3. 再运行这个脚本

配置方式：
- 方式1：设置环境变量（推荐，更安全）
- 方式2：使用 config.json 文件
"""

import json
import os
import sys
import time
import requests
from pathlib import Path
from flask import Flask, request, jsonify

CONFIG_PATH = Path(__file__).parent.parent / "config.json"


def load_config() -> dict:
    """
    加载配置，优先使用环境变量，否则使用 config.json
    """
    # 尝试从环境变量加载
    feishu_app_id = os.getenv("FEISHU_APP_ID")
    feishu_app_secret = os.getenv("FEISHU_APP_SECRET")
    feishu_webhook_url = os.getenv("FEISHU_WEBHOOK_URL")
    ai_api_key = os.getenv("AI_API_KEY")
    ai_provider = os.getenv("AI_PROVIDER", "zhipu")
    ai_model = os.getenv("AI_MODEL", "GLM-4.5-Air")
    crush_name = os.getenv("CRUSH_NAME", "小樱")
    current_stage = os.getenv("CURRENT_STAGE", "陌生")
    personality_path = os.getenv("PERSONALITY_PATH", "./crush-default/personality.md")

    # 如果环境变量都设置了，直接使用
    if feishu_app_id and feishu_app_secret and feishu_webhook_url and ai_api_key:
        return {
            "feishu": {
                "app_id": feishu_app_id,
                "app_secret": feishu_app_secret,
                "webhook_url": feishu_webhook_url
            },
            "ai": {
                "type": "api",
                "provider": ai_provider,
                "api_key": ai_api_key,
                "model": ai_model
            },
            "personality": {
                "path": personality_path
            },
            "crush_name": crush_name,
            "current_stage": current_stage
        }

    # 否则尝试从 config.json 加载
    if not CONFIG_PATH.exists():
        print(f"错误：配置文件 {CONFIG_PATH} 不存在，且未设置环境变量")
        print("请设置环境变量或创建 config.json 文件")
        sys.exit(1)
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def get_token(config: dict) -> str:
    """获取 app_access_token"""
    feishu = config.get("feishu", {})
    url = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal"
    data = {"app_id": feishu.get("app_id"), "app_secret": feishu.get("app_secret")}
    resp = requests.post(url, json=data)
    result = resp.json()
    if result.get("code") != 0:
        raise Exception(f"获取token失败: {result}")
    return result["app_access_token"]


def send_message(token: str, receive_id: str, content: str) -> dict:
    """发送消息"""
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    params = {"receive_id_type": "open_id"}
    headers = {"Authorization": f"Bearer {token}"}
    data = {"receive_id": receive_id, "msg_type": "text", "content": json.dumps({"text": content})}
    resp = requests.post(url, params=params, json=data, headers=headers)
    return resp.json()


def call_ai(config: dict, user_message: str) -> str:
    """调用 AI 生成回复"""
    ai_config = config.get("ai", {})
    provider = ai_config.get("provider", "zhipu")
    api_key = ai_config.get("api_key", "")
    model = ai_config.get("model", "glm-4-flash")

    # 加载性格设定
    personality_path = config.get("personality", {}).get("path", "")
    if personality_path:
        p = Path(__file__).parent.parent / personality_path
        if p.exists():
            personality = p.read_text(encoding="utf-8")
        else:
            personality = "你是一个性格高冷的女生"
    else:
        personality = "你是一个性格高冷的女生"

    current_stage = config.get("current_stage", "陌生")
    crush_name = config.get("crush_name", "小樱")

    system_prompt = f"""{personality}

当前阶段：{current_stage}

重要规则：
1. 你是 {crush_name}，现在是{current_stage}阶段
2. {current_stage}阶段的行为：陌生阶段要非常高冷，不会太热情
3. 回复要简短、冷淡，符合高冷傲娇风格
4. 不要太热情，不要太主动

用户消息：{user_message}

请直接回复她的回答，保持高冷风格。"""

    if provider == "zhipu":
        url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        }
    elif provider == "deepseek":
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        data = {"model": model, "messages": [{"role": "system", "content": system_prompt}]}
    else:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        data = {"model": model, "messages": [{"role": "system", "content": system_prompt}]}

    try:
        resp = requests.post(url, headers=headers, json=data, timeout=30)
        result = resp.json()
        return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"AI调用失败: {e}")
        return "嗯..."


# 全局变量用于事件去重
processed_events = set()


def main():
    config = load_config()
    feishu_config = config.get("feishu", {})

    app = Flask(__name__)

    @app.route("/webhook", methods=["GET", "POST"])
    def handle_webhook():
        # 飞书 Webhook 验证
        if request.method == "GET":
            challenge = request.args.get("challenge")
            if challenge:
                return jsonify({"code": 0, "challenge": challenge})
            return jsonify({"code": 1})

        # 处理消息
        data = request.json

        # 事件去重 - 使用 event_id
        header = data.get("header", {})
        event_id = header.get("event_id")
        if event_id and event_id in processed_events:
            return jsonify({"code": 0})
        if event_id:
            processed_events.add(event_id)
            if len(processed_events) > 1000:
                processed_events.clear()

        # 获取事件数据
        event = data.get("event", {})
        if not event:
            event = data

        # 处理文本消息
        message = event.get("message", {})
        if not message:
            message = event

        msg_type = message.get("message_type") or message.get("type")

        if msg_type != "text":
            return jsonify({"code": 0})

        # 获取消息内容
        content_str = message.get("content", "{}")
        content = json.loads(content_str) if isinstance(content_str, str) else content_str
        user_message = content.get("text", "")

        # 获取发送者ID
        sender = event.get("sender", {})
        sender_id = sender.get("sender_id", {})
        user_id = sender_id.get("open_id", "")

        if not user_message or not user_id:
            return jsonify({"code": 0})

        # 调用 AI 生成回复
        reply = call_ai(config, user_message)

        # 发送回复
        try:
            token = get_token(config)
            send_message(token, user_id, reply)
        except Exception as e:
            print(f"发送失败: {e}")
        
        return jsonify({"code": 0})

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"})

    print("=" * 40)
    print("飞书恋爱对象机器人已启动")
    print("=" * 40)
    print("服务运行中...")
    print("=" * 40)

    app.run(host="0.0.0.0", port=5001)


if __name__ == "__main__":
    main()