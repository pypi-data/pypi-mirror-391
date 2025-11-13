# 🚀 XQCSendMessage

![XQCSendMessage Logo](https://s2.loli.net/2025/11/12/Ey4Vkr7jgYobidS.jpg)

 [![Python Versions](https://img.shields.io/badge/Python-3.10%2B-blue)](https://github.com/xiaoqiangclub/XQCSendMessage)[![PyPI version](https://img.shields.io/badge/PyPI-0.0.3-blue)](https://github.com/xiaoqiangclub/XQCSendMessage) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

`XQCSendMessage` 是一个自用的 Python 消息发送模块，旨在提供一个相对便捷的途径来通过多种渠道（如邮件、钉钉、企业微信等）发送通知或消息。无论您需要同步还是异步发送，`XQCSendMessage` 都尝试提供简洁、统一的 API。

## 📖 目录

- [✨ 主要特性](#主要特性)
- [📤 安装](#安装)
- [🚀 快速上手](#快速上手)
  - [⚙️ 参数说明](#参数说明)
  - [📧 示例 1.1: 发送一封邮件 (同步)](#示例-11-发送一封邮件-同步)
  - [🤖 示例 1.2: 发送钉钉消息 (同步)](#示例-12-发送钉钉消息-同步)
  - [🏢 示例 1.3: 发送企业微信 Webhook 消息 (同步)](#示例-13-发送企业微信-webhook-消息-同步)
  - [🏢 示例 1.4: 发送企业微信应用消息 (同步)](#示例-14-发送企业微信应用消息-同步)
  - [📧 示例 1.5: 发送邮件 (异步)](#示例-15-发送邮件-异步)
  - [🤖 示例 1.6: 发送钉钉消息 (异步)](#示例-16-发送钉钉消息-异步)
  - [🏢 示例 1.7: 发送企业微信 Webhook 消息 (异步)](#示例-17-发送企业微信-webhook-消息-异步)
  - [🏢 示例 1.8: 发送企业微信应用消息 (异步)](#示例-18-发送企业微信应用消息-异步)
- [📄 许可证](#许可证)
- [🙏 支持我](#支持我)


## 主要特性

- **多渠道支持**:
  - 📧 **邮件**: 支持 SMTP，方便集成邮件服务。
  - 🤖 **钉钉**: 支持 Webhook 机器人，包含签名验证。
  - 🏢 **企业微信**:
    - `Webhook` 机器人模式。
    - `应用消息` 模式，支持更多消息类型。
- **同步与异步**: 提供了同步和异步两种发送模式，以适应不同场景的需求。


## 安装

通过 pip 或 poetry 安装 `xqcsendmessage`:

```bash
# 使用 pip
pip install xqcsendmessage

# 使用 poetry
poetry add xqcsendmessage
```

## 快速上手

`XQCSendMessage` 提供了便捷的顶层函数，可以调用以发送消息，无需显式实例化客户端或发送器。

### 参数说明

这些函数将消息内容作为第一个参数，其余参数作为关键字参数传入。

- `send_email` / `send_email_async`:
  - `message` (str): 邮件正文内容。
  - `email_subject` (str): 邮件主题。
  - `smtp_server` (str): SMTP 服务器地址。
  - `smtp_port` (int): SMTP 服务器端口。
  - `sender_email` (str): 发件人邮箱。
  - `sender_password` (str): 发件人邮箱密码或授权码。
  - `email_recipients` (List[str]): 收件人列表。
  - `email_subtype` (str, default `"plain"`): 邮件内容类型，`"plain"` 或 `"html"`。
  - `use_tls` (bool, default `True`): 是否使用 TLS 加密。
  - `email_attachments` (Optional[List[str]]): 附件文件路径列表。
  - `**kwargs`: 其他可选参数，将传递给底层的 `EmailSender` 或 `AsyncEmailSender`。
- `send_dingtalk` / `send_dingtalk_async`:
  - `message` (Union[str, Dict[str, Any]]): 消息内容，可以是字符串（将作为文本消息发送）或符合钉钉机器人格式的字典。
  - `webhook` (str): 钉钉机器人的 Webhook 地址。
  - `secret` (Optional[str]): 钉钉机器人的密钥，用于签名。
  - `msg_type` (str, default `"text"`): 消息类型，默认为 "text"。
  - `at_mobiles` (Optional[List[str]]): 被 @ 的用户的手机号列表。
  - `is_at_all` (bool, default `False`): 是否 @ 所有人，默认为 False。
  - `**kwargs`: 其他可选参数，会合并到消息字典中。
- `send_wecom_webhook` / `send_wecom_webhook_async`:
  - `message` (Union[str, Dict[str, Any]]): 消息内容，可以是字符串（将作为文本消息发送）或符合企业微信机器人支持的格式。
  - `webhook` (str): 企业微信机器人的 Webhook 地址。
  - `msg_type` (str, default `"text"`): 消息类型，默认为 "text"。
  - `**kwargs`: 其他可选参数，会合并到消息字典中。
- `send_wecom_app` / `send_wecom_app_async`:
  - `message` (Union[str, Dict[str, Any]]): 消息内容，可以是字符串（将作为文本消息发送）或符合企业微信应用消息支持的格式。
  - `corpid` (str): 企业 ID。
  - `corpsecret` (str): 应用的 Secret。
  - `agentid` (int): 应用的 AgentId。
  - `msg_type` (str, default `"text"`): 消息类型，默认为 "text"。
  - `touser` (Optional[Union[str, List[str]]], default `"@all"`): 指定接收消息的成员，成员 ID 列表（最多支持 1000 个）。默认为 "@all"。
  - `toparty` (Optional[Union[str, List[str]]]): 指定接收消息的部门 ID 列表（最多支持 100 个）。
  - `totag` (Optional[Union[str, List[str]]]): 指定接收消息的标签 ID 列表（最多支持 100 个）。
  - `**kwargs`: 其他可选参数，会合并到消息字典中。

### 示例 1.1: 发送一封邮件 (同步)

```python
import os
from xqcsendmessage import send_email

# --- 配置 ---
SMTP_SERVER = "YOUR_SMTP_SERVER"  # ⚠️ 请替换为你的 SMTP 服务器
SMTP_PORT = 587                   # ⚠️ 请替换为你的 SMTP 端口
SENDER_EMAIL = "YOUR_SENDER_EMAIL"  # ⚠️ 请替换为你的邮箱
SENDER_PASSWORD = "YOUR_SENDER_PASSWORD"    # ⚠️ 请替换为你的邮箱密码或授权码
RECIPIENTS = ["YOUR_RECIPIENT_EMAIL"] # ⚠️ 请替换为收件人邮箱列表
# 附件文件路径，请确保文件存在
ATTACHMENT_FILE = os.path.join(os.path.dirname(__file__), "test_attachment_sync.txt")

def main():
    # 创建一个用于测试的附件文件
    with open(ATTACHMENT_FILE, "w") as f:
        f.write("This is a test attachment file for synchronous email example.")

    # 发送不带附件的邮件
    try:
        result_no_attachment = send_email(
            message="这是一封通过 xqcsendmessage 发送的同步测试邮件，不带附件。",
            email_subject="Hello from xqcsendmessage! (Direct Call No Attachment)",
            smtp_server=SMTP_SERVER,
            smtp_port=SMTP_PORT,
            sender_email=SENDER_EMAIL,
            sender_password=SENDER_PASSWORD,
            email_recipients=RECIPIENTS,
            email_subtype="plain"
        )
        print(f"✅ 调用邮件发送成功 (无附件): {result_no_attachment}")

        # 发送带附件的邮件
        result_with_attachment = send_email(
            message="这是一封通过 xqcsendmessage 发送的同步测试邮件，带附件。",
            email_subject="Hello from xqcsendmessage! (Direct Call With Attachment)",
            smtp_server=SMTP_SERVER,
            smtp_port=SMTP_PORT,
            sender_email=SENDER_EMAIL,
            sender_password=SENDER_PASSWORD,
            email_recipients=RECIPIENTS,
            email_subtype="plain",
            email_attachments=[ATTACHMENT_FILE] # 添加附件
        )
        print(f"✅ 调用邮件发送成功 (带附件): {result_with_attachment}")

    except Exception as e:
        print(f"🔥 调用邮件发送失败: {e}")

    # 清理测试附件文件
    os.remove(ATTACHMENT_FILE)

if __name__ == "__main__":
    main()
```

### 🤖 示例 1.2: 发送钉钉消息 (同步)

```python
from xqcsendmessage import send_dingtalk

# --- 配置 ---
# 你的钉钉机器人的 Webhook 和密钥
WEBHOOK_URL = "YOUR_DINGTALK_WEBHOOK_URL"
SECRET = "YOUR_DINGTALK_SECRET"  # 如果没有设置密钥，则为 None

def main():
    # 发送钉钉消息
    try:
        # 发送字符串消息，消息类型和 @ 人相关的参数通过 kwargs 传递
        result_direct_str = send_dingtalk(
            "这是一条来自 xqcsendmessage 发送的同步测试消息 (字符串)。",
            webhook=WEBHOOK_URL,
            secret=SECRET,
            msg_type="text",  # 消息类型为文本
            is_at_all=True  # 发送给所有人
        )
        print(f"✅ 钉钉消息发送成功 (字符串): {result_direct_str}")

        # 发送字符串消息，消息类型和 @ 人相关的参数通过 kwargs 传递
        result_direct_str_at = send_dingtalk(
            "这是一条来自 xqcsendmessage 发送的同步测试消息 (覆盖 @ 人，指定手机号，markdown 类型)。",
            webhook=WEBHOOK_URL,
            secret=SECRET,
            msg_type="markdown",
            at_mobiles=["YOUR_MOBILE_NUMBER"],
            is_at_all=False
        )
        print(f"✅ 钉钉消息发送成功 (覆盖 @ 人): {result_direct_str_at}")


        # 发送字典消息，消息类型和 @ 人相关的参数通过 kwargs 传递
        result_direct_dict = send_dingtalk(
            {
                "msgtype": "markdown",
                "markdown": {
                    "title": "测试标题",
                    "text": "### 【XQCSendMessage】这是一条通过 xqcsendmessage 发送的同步测试消息 (字典，指定手机号，markdown 类型)。"
                }
            },
            webhook=WEBHOOK_URL,
            secret=SECRET,
            msg_type="markdown",
            at_mobiles=["YOUR_MOBILE_NUMBER"],
            is_at_all=False
        )
        print(f"✅ 调用钉钉发送成功 (字典): {result_direct_dict}")
    except Exception as e:
        print(f"🔥 调用钉钉发送失败: {e}")

if __name__ == "__main__":
    main()
```

### 🏢 示例 1.3: 发送企业微信 Webhook 消息 (同步)

```python
from xqcsendmessage import send_wecom_webhook

# --- 配置 ---
# 你的企业微信机器人的 Webhook
WEBHOOK_URL = "YOUR_WECOM_WEBHOOK_URL"

def main():
    # 发送企业微信 Webhook 消息
    try:
        # 发送字符串消息
        result_direct_str = send_wecom_webhook(
            "【XQCSendMessage】这是一条来自 xqcsendmessage 发送的同步 Webhook 测试消息 (字符串)。",
            webhook=WEBHOOK_URL,
            msg_type="text"  # 消息类型为文本
        )
        print(f"✅ 调用企业微信 Webhook 消息发送成功 (字符串): {result_direct_str}")

        # 发送字符串消息，并覆盖默认参数（例如，指定不同的内容）
        result_override_str = send_wecom_webhook(
            {"markdown": {"content": "【XQCSendMessage】这是一条来自 xqcsendmessage 的同步 Webhook 测试消息 (覆盖字符串内容，markdown 类型)。"}},
            webhook=WEBHOOK_URL,
            msg_type="markdown"  # 覆盖为 markdown 类型
        )
        print(f"✅ 企业微信 Webhook 消息发送成功 (覆盖字符串): {result_override_str}")

        # 发送字典消息
        result_direct_dict = send_wecom_webhook(
            {
                "msgtype": "markdown",
                "markdown": {"content": "【XQCSendMessage】这是一条来自 xqcsendmessage 发送的同步 Webhook 测试消息 (字典，markdown 类型)。"}
            },
            webhook=WEBHOOK_URL,
            msg_type="markdown"  # 消息类型为 markdown
        )
        print(f"✅ 调用企业微信 Webhook 消息发送成功 (字典): {result_direct_dict}")

    except Exception as e:
        print(f"🔥 调用企业微信 Webhook 消息发送失败: {e}")

if __name__ == "__main__":
    main()
```

### 🏢 示例 1.4: 发送企业微信应用消息 (同步)

```python
from xqcsendmessage import send_wecom_app

# --- 配置 ---
# 你的企业微信应用配置
CORP_ID = "YOUR_CORP_ID"
CORP_SECRET = "YOUR_CORP_SECRET"
AGENT_ID = YOUR_AGENT_ID  # 你的应用 AgentId

def main():
    # 发送企业微信应用消息
    try:
        # 发送字符串消息
        result_direct_str = send_wecom_app(
            "【XQCSendMessage】这是一条通过企业微信应用发送的同步测试消息 (字符串)。",
            corpid=CORP_ID,
            corpsecret=CORP_SECRET,
            agentid=AGENT_ID,
            msg_type="text",  # 消息类型为文本
            touser="@all"  # 默认 @所有人
        )
        print(f"✅ 调用企业微信应用消息发送成功 (字符串): {result_direct_str}")

        # 发送字符串消息，并覆盖默认参数（例如，指定不同的内容和发送对象）
        result_override_str = send_wecom_app(
            "【XQCSendMessage】这是一条通过企业微信应用发送的同步测试消息 (覆盖字符串内容，指定用户)。",
            corpid=CORP_ID,
            corpsecret=CORP_SECRET,
            agentid=AGENT_ID,
            touser="USERID"  # 覆盖为指定用户
        )
        print(f"✅ 企业微信应用消息发送成功 (覆盖字符串): {result_override_str}")

        # 发送字典消息
        result_direct_dict = send_wecom_app(
            {
                "msgtype": "markdown",
                "markdown": {"content": "【XQCSendMessage】这是一条通过企业微信应用发送的同步测试消息 (字典，指定用户)。"}
            },
            corpid=CORP_ID,
            corpsecret=CORP_SECRET,
            agentid=AGENT_ID,
            msg_type="markdown",  # 消息类型为 markdown
            touser="USERID"  # 可以在这里覆盖 touser
        )
        print(f"✅ 调用企业微信应用消息发送成功 (字典): {result_direct_dict}")

    except Exception as e:
        print(f"🔥 调用企业微信应用消息发送失败: {e}")

if __name__ == "__main__":
    main()
```

### 📧 示例 1.5: 发送邮件 (异步)

```python
import asyncio
import os
from xqcsendmessage import send_email_async

# --- 配置 ---
SMTP_SERVER = "YOUR_SMTP_SERVER"  # ⚠️ 请替换为你的 SMTP 服务器
SMTP_PORT = 587                   # ⚠️ 请替换为你的 SMTP 端口
SENDER_EMAIL = "YOUR_SENDER_EMAIL"  # ⚠️ 请替换为你的邮箱
SENDER_PASSWORD = "YOUR_SENDER_PASSWORD"    # ⚠️ 请替换为你的邮箱密码或授权码
RECIPIENTS = ["YOUR_RECIPIENT_EMAIL"] # ⚠️ 请替换为收件人邮箱列表
# 附件文件路径，请确保文件存在
ATTACHMENT_FILE = os.path.join(os.path.dirname(__file__), "test_attachment_async.txt")

async def main():
    # 创建一个用于测试的附件文件
    with open(ATTACHMENT_FILE, "w") as f:
        f.write("This is a test attachment file for asynchronous email example.")

    # 发送不带附件的邮件
    try:
        result_no_attachment = await send_email_async(
            message="这是一封通过 xqcsendmessage 发送的异步测试邮件，不带附件。",
            email_subject="Hello from xqcsendmessage! (Direct Call No Attachment)",
            smtp_server=SMTP_SERVER,
            smtp_port=SMTP_PORT,
            sender_email=SENDER_EMAIL,
            sender_password=SENDER_PASSWORD,
            email_recipients=RECIPIENTS,
            email_subtype="plain"
        )
        print(f"✅ 调用邮件发送成功 (无附件): {result_no_attachment}")

        # 发送带附件的邮件
        result_with_attachment = await send_email_async(
            message="这是一封通过 xqcsendmessage 发送的异步测试邮件，带附件。",
            email_subject="Hello from xqcsendmessage! (Direct Call With Attachment)",
            smtp_server=SMTP_SERVER,
            smtp_port=SMTP_PORT,
            sender_email=SENDER_EMAIL,
            sender_password=SENDER_PASSWORD,
            email_recipients=RECIPIENTS,
            email_subtype="plain",
            email_attachments=[ATTACHMENT_FILE] # 添加附件
        )
        print(f"✅ 调用邮件发送成功 (带附件): {result_with_attachment}")

    except Exception as e:
        print(f"🔥 调用邮件发送失败: {e}")

    # 清理测试附件文件
    os.remove(ATTACHMENT_FILE)

if __name__ == "__main__":
    asyncio.run(main())
```

### 🤖 示例 1.6: 发送钉钉消息 (异步)

```python
import asyncio
from xqcsendmessage import send_dingtalk_async

# --- 配置 ---
# 你的钉钉机器人的 Webhook 和密钥
WEBHOOK_URL = "YOUR_DINGTALK_WEBHOOK_URL"
SECRET = "YOUR_DINGTALK_SECRET"

async def main():
    # 发送钉钉消息
    try:
        # 发送字符串消息，消息类型和 @ 人相关的参数通过 kwargs 传递
        result_direct_str = await send_dingtalk_async(
            "【XQCSendMessage】这是一条通过 xqcsendmessage 发送的异步测试消息 (字符串)。",
            webhook=WEBHOOK_URL,
            secret=SECRET,
            msg_type="text",  # 消息类型为文本
            is_at_all=True  # 发送给所有人
        )
        print(f"✅ 钉钉消息发送成功 (字符串): {result_direct_str}")

        # 发送字符串消息，消息类型和 @ 人相关的参数通过 kwargs 传递
        result_direct_str_at = await send_dingtalk_async(
            "【XQCSendMessage】这是一条来自 xqcsendmessage 发送的异步测试消息 (覆盖 @ 人，指定手机号，markdown 类型)。",
            webhook=WEBHOOK_URL,
            secret=SECRET,
            msg_type="markdown",
            at_mobiles=["YOUR_MOBILE_NUMBER"],
            is_at_all=False
        )
        print(f"✅ 钉钉消息发送成功 (覆盖 @ 人): {result_direct_str_at}")

        # 发送字典消息，消息类型和 @ 人相关的参数通过 kwargs 传递
        result_direct_dict = await send_dingtalk_async(
            {
                "msgtype": "markdown",
                "markdown": {
                    "title": "测试标题",
                    "text": "### 【XQCSendMessage】这是一条通过 xqcsendmessage 发送的异步测试消息 (字典，指定手机号，markdown 类型)。"
                }
            },
            webhook=WEBHOOK_URL,
            secret=SECRET,
            msg_type="markdown",
            at_mobiles=["YOUR_MOBILE_NUMBER"],
            is_at_all=False
        )
        print(f"✅ 调用钉钉发送成功 (字典): {result_direct_dict}")
    except Exception as e:
        print(f"🔥 调用钉钉发送失败: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 🏢 示例 1.7: 发送企业微信 Webhook 消息 (异步)

```python
import asyncio
from xqcsendmessage import send_wecom_webhook_async

# --- 配置 ---
# 你的企业微信机器人的 Webhook
WEBHOOK_URL = "YOUR_WECOM_WEBHOOK_URL"

async def main():
    # 发送企业微信 Webhook 消息
    try:
        # 发送字符串消息
        result_direct_str = await send_wecom_webhook_async(
            "【XQCSendMessage】这是一条来自 xqcsendmessage 发送的异步 Webhook 测试消息 (字符串)。",
            webhook=WEBHOOK_URL,
            msg_type="text"  # 消息类型为文本
        )
        print(f"✅ 调用企业微信 Webhook 消息发送成功 (字符串): {result_direct_str}")

        # 发送字符串消息，并覆盖默认参数（例如，指定不同的内容）
        result_override_str = await send_wecom_webhook_async(
            {"markdown": {"content": "【XQCSendMessage】这是一条来自 xqcsendmessage 的异步 Webhook 测试消息 (覆盖字符串内容，markdown 类型)。"}},
            webhook=WEBHOOK_URL,
            msg_type="markdown"  # 覆盖为 markdown 类型
        )
        print(f"✅ 企业微信 Webhook 消息发送成功 (覆盖字符串): {result_override_str}")

        # 发送字典消息
        result_direct_dict = await send_wecom_webhook_async(
            {
                "msgtype": "markdown",
                "markdown": {"content": "【XQCSendMessage】这是一条来自 xqcsendmessage 发送的异步 Webhook 测试消息 (字典，markdown 类型)。"}
            },
            webhook=WEBHOOK_URL,
            msg_type="markdown"  # 消息类型为 markdown
        )
        print(f"✅ 调用企业微信 Webhook 消息发送成功 (字典): {result_direct_dict}")

    except Exception as e:
        print(f"🔥 调用企业微信 Webhook 消息发送失败: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 🏢 示例 1.8: 发送企业微信应用消息 (异步)

```python
import asyncio
from xqcsendmessage import send_wecom_app_async

# --- 配置 ---
# 企业微信应用配置
CORP_ID = "YOUR_CORP_ID"
CORP_SECRET = "YOUR_CORP_SECRET"
AGENT_ID = YOUR_AGENT_ID  # 你的应用 AgentId

async def main():
    # 发送企业微信应用消息
    try:
        # 发送字符串消息
        result_direct_str = await send_wecom_app_async(
            "【XQCSendMessage】这是一条通过企业微信应用发送的异步测试消息 (字符串)。",
            corpid=CORP_ID,
            corpsecret=CORP_SECRET,
            agentid=AGENT_ID,
            msg_type="text",  # 消息类型为文本
            touser="@all"  # 默认 @所有人
        )
        print(f"✅ 调用企业微信应用消息发送成功 (字符串): {result_direct_str}")

        # 发送字典消息，并覆盖 touser 参数
        result_direct_dict_override = await send_wecom_app_async(
            {
                "msgtype": "markdown",
                "markdown": {"content": "【XQCSendMessage】这是一条通过企业微信应用发送的异步测试消息 (字典，指定用户)。"},
            },
            corpid=CORP_ID,
            corpsecret=CORP_SECRET,
            agentid=AGENT_ID,
            msg_type="markdown",  # 消息类型为 markdown
            touser="USERID"  # 可以在这里覆盖 touser
        )
        print(f"✅ 调用企业微信应用消息发送成功 (字典): {result_direct_dict_override}")

    except Exception as e:
        print(f"🔥 调用企业微信应用消息发送失败: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```


## 许可证

本项目基于 [MIT License](LICENSE) 开源。

## 支持我

如果您觉得 `XQCSendMessage` 对您有帮助，可以通过以下方式支持我：

[![打赏作者](https://s2.loli.net/2025/11/10/lQRcAvN3Lgxukqb.png)](https://s2.loli.net/2025/11/10/lQRcAvN3Lgxukqb.png)