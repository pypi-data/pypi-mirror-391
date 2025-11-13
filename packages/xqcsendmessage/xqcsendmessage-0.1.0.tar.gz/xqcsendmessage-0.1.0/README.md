# 🚀 XQCSendMessage

![XQCSendMessage Logo](https://s2.loli.net/2025/11/12/Ey4Vkr7jgYobidS.jpg)

[![Python Versions](https://img.shields.io/badge/Python-3.10%2B-blue)](https://github.com/xiaoqiangclub/XQCSendMessage)[![PyPI version](https://img.shields.io/badge/PyPI-0.1.0-blue)](https://github.com/xiaoqiangclub/XQCSendMessage) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

`XQCSendMessage` 是一个为 Python 设计的、统一且便捷的消息发送模块，支持通过邮件、钉钉、企业微信等多种渠道发送通知。无论同步还是异步场景，它都提供了简洁的 API。

## 📖 目录

- [✨ 主要特性](#-主要特性)
- [📥 安装](#-安装)
- [🚀 快速上手](#-快速上手)
- [⚙️ API & 参数说明](#️-api--参数说明)
  - [邮件发送](#邮件发送)
  - [钉钉机器人](#钉钉机器人)
  - [企业微信 Webhook](#企业微信-webhook)
  - [企业微信应用消息](#企业微信应用消息)
  - [通用 Markdown 发送](#通用-markdown-发送)
  - [文件读取工具](#文件读取工具)
- [📝 示例代码](#-示例代码)
  - [同步发送](#同步发送)
  - [异步发送](#异步发送)
- [📄 许可证](#-许可证)
- [🙏 支持我](#-支持我)

## ✨ 主要特性

- **多渠道支持**:
  - 📧 **邮件**: 支持 SMTP，可自定义附件和 HTML 内容。
  - 🤖 **钉钉**: 支持 Webhook 机器人，包含签名验证和多种 @ 用户方式。
  - 🏢 **企业微信**: 同时支持 `Webhook` 和 `应用消息` 两种模式。
- **同步与异步**: 为每个发送功能都提供了同步和异步 (`_async`) 版本。
- **便捷工具**:
  - 内置 `send_markdown` 函数，可直接读取 Markdown 文件并发送。
  - 提供 `read_file` 和 `read_file_async` 工具，方便读取文件内容后发送。

## 📥 安装

```bash
# 使用 pip
pip install xqcsendmessage

# 使用 poetry
poetry add xqcsendmessage
```

## 🚀 快速上手

所有功能都可以通过 `xqcsendmessage` 的顶层函数直接调用。

```python
from xqcsendmessage import send_dingtalk

# 发送一条钉钉消息
try:
    send_dingtalk(
        message="Hello from XQCSendMessage!",
        webhook="YOUR_DINGTALK_WEBHOOK_URL",
        secret="YOUR_DINGTALK_SECRET"
    )
    print("✅ 钉钉消息发送成功")
except Exception as e:
    print(f"🔥 发送失败: {e}")
```

## ⚙️ API & 参数说明

### 邮件发送

`send_email(message, email_subject, smtp_server, smtp_port, sender_email, sender_password, email_recipients, **kwargs)`
`send_email_async(...)`

- `message` (str): 邮件正文，支持纯文本或 HTML。
- `email_subject` (str): 邮件主题。
- `smtp_server`, `smtp_port`, `sender_email`, `sender_password`: SMTP 服务器配置。
- `email_recipients` (List[str]): 收件人列表。
- `email_subtype` (str): 内容类型，`"plain"` (默认) 或 `"html"`。
- `email_attachments` (Optional[List[str]]): 附件的文件路径列表。

### 钉钉机器人

`send_dingtalk(message, webhook, secret=None, **kwargs)`
`send_dingtalk_async(...)`

- `message` (Union[str, Dict]): 消息内容。
- `webhook` (str), `secret` (Optional[str]): 钉钉机器人的凭据。
- `send_md` (bool): `True` 表示以 Markdown 格式发送，默认为 `False` (Text 格式)。
- `title` (Optional[str]): Markdown 消息的标题。
- `at_mobiles` (Optional[List[str]]): 要 @ 的用户手机号列表。
- `at_userids` (Optional[List[str]]): 要 @ 的用户 ID 列表。
- `is_at_all` (bool): 是否 @ 所有人。**注意：如果 `at_mobiles` 或 `at_userids` 被指定，此参数将被自动忽略。**

### 企业微信 Webhook

`send_wecom_webhook(message, webhook, **kwargs)`
`send_wecom_webhook_async(...)`

- `message` (Union[str, Dict]): 消息内容。
- `webhook` (str): 企业微信机器人的 Webhook 地址。
- `send_md` (bool): `True` 表示以 Markdown 格式发送，默认为 `False` (Text 格式)。

### 企业微信应用消息

`send_wecom_app(message, corpid, corpsecret, agentid, **kwargs)`
`send_wecom_app_async(...)`

- `message` (Union[str, Dict]): 消息内容。
- `corpid`, `corpsecret`, `agentid`: 企业微信应用的凭据。
- `send_md` (bool): `True` 表示以 Markdown 格式发送，默认为 `False` (Text 格式)。
- `touser` (Optional[str]): 接收者 ID，多个用 `|` 分隔。默认为 `@all`。
- `toparty` (Optional[str]): 接收部门 ID。
- `totag` (Optional[str]): 接收标签 ID。
- **注意：如果 `toparty` 或 `totag` 被指定，`touser` 的 `@all` 默认值将被忽略。**

### 通用 Markdown 发送

`send_markdown(file_path, channels, **kwargs)`

- `file_path` (str): Markdown 文件的路径。
- `channels` (List[str]): 要发送的通道列表，支持 `"email"`, `"dingtalk"`, `"wecom_webhook"`, `"wecom_app"`。
- `**kwargs`: 包含所有目标通道所需的凭据和参数（例如 `dingtalk_webhook`, `email_subject` 等）。

### 文件读取工具

`read_file(file_path, encoding="utf-8")`
`read_file_async(file_path, encoding="utf-8")`

- `file_path` (str): 要读取的文件的路径。
- `encoding` (str): 文件编码，默认为 `utf-8`。

## 📝 示例代码

### 同步发送

**发送邮件**
```python
from xqcsendmessage import send_email

send_email(
    message="这是一封测试邮件。",
    email_subject="同步邮件测试",
    smtp_server="YOUR_SMTP_SERVER",
    smtp_port=465,
    sender_email="YOUR_SENDER_EMAIL",
    sender_password="YOUR_SENDER_PASSWORD",
    email_recipients=["recipient1@example.com"],
)
```

**发送钉钉 Markdown 消息并 @ 指定用户**
```python
from xqcsendmessage import send_dingtalk

send_dingtalk(
    message="### 项目更新\n- 已完成 A 模块开发。",
    webhook="YOUR_DINGTALK_WEBHOOK_URL",
    secret="YOUR_DINGTALK_SECRET",
    send_md=True,
    title="项目更新通知",
    at_mobiles=["13900000000"]
)
```

### 异步发送

**发送企业微信应用消息**
```python
import asyncio
from xqcsendmessage import send_wecom_app_async

async def main():
    await send_wecom_app_async(
        message="这是一条异步发送的企业微信应用消息。",
        corpid="YOUR_CORP_ID",
        corpsecret="YOUR_CORP_SECRET",
        agentid=YOUR_AGENT_ID,
        touser="@all"
    )

if __name__ == "__main__":
    asyncio.run(main())
```

**读取文件内容并异步发送**
```python
import asyncio
from xqcsendmessage import read_file_async, send_dingtalk_async

async def main():
    try:
        content = await read_file_async("daily_report.txt")
        await send_dingtalk_async(
            message=f"今日报告内容：\n{content}",
            webhook="YOUR_DINGTALK_WEBHOOK_URL",
            secret="YOUR_DINGTALK_SECRET"
        )
    except Exception as e:
        print(f"发送失败: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 📄 许可证

本项目基于 [MIT License](LICENSE) 开源。

## 🙏 支持我

如果您觉得 `XQCSendMessage` 对您有帮助，可以通过以下方式支持我：

[![打赏作者](https://s2.loli.net/2025/11/10/lQRcAvN3Lgxukqb.png)](https://s2.loli.net/2025/11/10/lQRcAvN3Lgxukqb.png)