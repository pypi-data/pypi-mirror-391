# 作者：Xiaoqiang
# 微信公众号：XiaoqiangClub
# 创建时间：2025-11-12T01:10:00.168Z
# 文件描述：提供便捷的顶层函数，用于直接发送消息。
# 文件路径：xqcsendmessage/api.py

from typing import Any, Dict, List, Optional, Union

from .client import SyncClient, AsyncClient
from .core.exceptions import SendMessageError

# --- 同步发送函数 ---

def send_email(
    message: Union[str, Dict[str, Any]], # 将 message 作为第一个参数
    smtp_server: str,
    smtp_port: int,
    sender_email: str,
    sender_password: str,
    recipients: List[str],
    subject: Optional[str] = None, # subject 可以从 message 中获取或单独提供
    content: Optional[str] = None, # content 可以从 message 中获取或单独提供
    subtype: str = "plain",
    use_tls: bool = True,
    **kwargs: Any
) -> Dict[str, Any]:
    """
    直接发送同步邮件。

    :param message: 邮件内容。如果为字符串，则作为 content；如果为字典，则可以包含 subject, content, recipients, subtype。
    :param smtp_server: SMTP 服务器地址。
    :param smtp_port: SMTP 服务器端口。
    :param sender_email: 发件人邮箱。
    :param sender_password: 发件人邮箱密码或授权码。
    :param recipients: 收件人列表。
    :param subject: 邮件主题，如果 message 为字符串，则必须提供。
    :param content: 邮件内容，如果 message 为字典且未包含 content，则必须提供。
    :param subtype: 邮件内容类型，'plain' 或 'html'。
    :param use_tls: 是否使用 TLS 加密。
    :param kwargs: 其他可选参数，将传递给底层的 `EmailSender`。
    :return: 发送结果的字典。
    """
    if isinstance(message, dict):
        final_subject = message.get("subject", subject)
        final_content = message.get("content", content)
        final_recipients = message.get("recipients", recipients)
        final_subtype = message.get("subtype", subtype)
    else:
        final_subject = subject
        final_content = message
        final_recipients = recipients
        final_subtype = subtype

    if not final_subject or not final_content or not final_recipients:
        raise SendMessageError("❌ 邮件发送缺少必要的参数：subject, content 或 recipients。")

    client = SyncClient(
        sender_type="email",
        smtp_server=smtp_server,
        smtp_port=smtp_port,
        sender_email=sender_email,
        sender_password=sender_password,
        use_tls=use_tls,
        subject=final_subject,
        content=final_content,
        recipients=final_recipients,
        subtype=final_subtype
    )
    return client.send(final_content, subject=final_subject, recipients=final_recipients, subtype=final_subtype, **kwargs)


def send_dingtalk(
    message: Union[str, Dict[str, Any]],
    webhook: str,
    secret: Optional[str] = None,
    msg_type: str = "text", # 默认消息类型为文本
    at_mobiles: Optional[List[str]] = None,
    is_at_all: bool = True, # 默认 @ 所有人
    **kwargs: Any
) -> Dict[str, Any]:
    """
    直接发送同步钉钉消息。

    :param message: 消息内容，支持多种格式（text, markdown, link, actionCard, feedCard）。
                    如果为 text 类型，可以直接传入字符串；其他类型需要传入字典。
    :param webhook: 钉钉机器人的 Webhook 地址。
    :param secret: 钉钉机器人的密钥，用于签名。
    :param msg_type: 消息类型，默认为 "text"。
    :param at_mobiles: 被 @ 的用户的手机号列表。
    :param is_at_all: 是否 @ 所有人，默认为 True。
    :param kwargs: 其他可选参数，将传递给底层的 `DingTalkSender`。
    :return: 发送结果的字典。
    """
    client = SyncClient(
        sender_type="dingtalk",
        webhook=webhook,
        secret=secret,
        msg_type=msg_type,
        at_mobiles=at_mobiles,
        is_at_all=is_at_all,
        message=message
    )
    return client.send(message, msg_type=msg_type, at_mobiles=at_mobiles, is_at_all=is_at_all, **kwargs)


def send_wecom_webhook(
    message: Union[str, Dict[str, Any]],
    webhook: str,
    msg_type: str = "text", # 默认消息类型为文本
    **kwargs: Any
) -> Dict[str, Any]:
    """
    直接发送同步企业微信 Webhook 消息。

    :param message: 消息内容。如果为 text 类型，可以直接传入字符串；其他类型需要传入字典。
    :param webhook: 企业微信机器人的 Webhook 地址。
    :param msg_type: 消息类型，默认为 "text"。支持 "text", "markdown", "image", "news", "file", "textcard", "template_card" 等。
    :param kwargs: 其他可选参数，将传递给底层的 `WeComWebhookSender`。
    :return: 发送结果的字典。
    """
    client = SyncClient(
        sender_type="wecom_webhook",
        webhook=webhook,
        msg_type=msg_type,
        message=message
    )
    return client.send(message, msg_type=msg_type, **kwargs)


def send_wecom_app(
    message: Union[str, Dict[str, Any]],
    corpid: str,
    corpsecret: str,
    agentid: int,
    msg_type: str = "text", # 默认消息类型为文本
    touser: Optional[Union[str, List[str]]] = "@all", # 默认 @所有人
    toparty: Optional[Union[str, List[str]]] = None,
    totag: Optional[Union[str, List[str]]] = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """
    直接发送同步企业微信应用消息。

    :param message: 消息内容。如果为 text 类型，可以直接传入字符串；其他类型需要传入字典。
    :param corpid: 企业 ID。
    :param corpsecret: 应用的 Secret。
    :param agentid: 应用的 AgentId。
    :param msg_type: 消息类型，默认为 "text"。支持 "text", "image", "voice", "video", "file", "textcard", "news", "mpnews", "markdown", "miniprogram_notice", "template_card" 等。
    :param touser: 指定接收消息的成员，成员 ID 列表（最多支持 1000 个）。默认为 "@all"。
    :param toparty: 指定接收消息的部门 ID 列表（最多支持 100 个）。
    :param totag: 指定接收消息的标签 ID 列表（最多支持 100 个）。
    :param kwargs: 其他可选参数，将传递给底层的 `WeComAppSender`。
    :return: 发送结果的字典。
    """
    client = SyncClient(
        sender_type="wecom_app",
        corpid=corpid,
        corpsecret=corpsecret,
        agentid=agentid,
        msg_type=msg_type,
        touser=touser,
        toparty=toparty,
        totag=totag,
        message=message
    )
    return client.send(message, msg_type=msg_type, touser=touser, toparty=toparty, totag=totag, **kwargs)


# --- 异步发送函数 ---

async def send_email_async(
    message: Union[str, Dict[str, Any]], # 将 message 作为第一个参数
    smtp_server: str,
    smtp_port: int,
    sender_email: str,
    sender_password: str,
    recipients: List[str],
    subject: Optional[str] = None,
    content: Optional[str] = None,
    subtype: str = "plain",
    use_tls: bool = True,
    **kwargs: Any
) -> Dict[str, Any]:
    """
    直接发送异步邮件。

    :param message: 邮件内容。如果为字符串，则作为 content；如果为字典，则可以包含 subject, content, recipients, subtype。
    :param smtp_server: SMTP 服务器地址。
    :param smtp_port: SMTP 服务器端口。
    :param sender_email: 发件人邮箱。
    :param sender_password: 发件人邮箱密码或授权码。
    :param recipients: 收件人列表。
    :param subject: 邮件主题，如果 message 为字符串，则必须提供。
    :param content: 邮件内容，如果 message 为字典且未包含 content，则必须提供。
    :param subtype: 邮件内容类型，'plain' 或 'html'。
    :param use_tls: 是否使用 TLS 加密。
    :param kwargs: 其他可选参数，将传递给底层的 `AsyncEmailSender`。
    :return: 发送结果的字典。
    """
    if isinstance(message, dict):
        final_subject = message.get("subject", subject)
        final_content = message.get("content", content)
        final_recipients = message.get("recipients", recipients)
        final_subtype = message.get("subtype", subtype)
    else:
        final_subject = subject
        final_content = message
        final_recipients = recipients
        final_subtype = subtype

    if not final_subject or not final_content or not final_recipients:
        raise SendMessageError("❌ 邮件发送缺少必要的参数：subject, content 或 recipients。")

    client = AsyncClient(
        sender_type="email",
        smtp_server=smtp_server,
        smtp_port=smtp_port,
        sender_email=sender_email,
        sender_password=sender_password,
        use_tls=use_tls,
        subject=final_subject,
        content=final_content,
        recipients=final_recipients,
        subtype=final_subtype
    )
    return await client.send(final_content, subject=final_subject, recipients=final_recipients, subtype=final_subtype, **kwargs)


async def send_dingtalk_async(
    message: Union[str, Dict[str, Any]],
    webhook: str,
    secret: Optional[str] = None,
    msg_type: str = "text", # 默认消息类型为文本
    at_mobiles: Optional[List[str]] = None,
    is_at_all: bool = True, # 默认 @ 所有人
    **kwargs: Any
) -> Dict[str, Any]:
    """
    直接发送异步钉钉消息。

    :param message: 消息内容，支持多种格式（text, markdown, link, actionCard, feedCard）。
                    如果为 text 类型，可以直接传入字符串；其他类型需要传入字典。
    :param webhook: 钉钉机器人的 Webhook 地址。
    :param secret: 钉钉机器人的密钥，用于签名。
    :param msg_type: 消息类型，默认为 "text"。
    :param at_mobiles: 被 @ 的用户的手机号列表。
    :param is_at_all: 是否 @ 所有人，默认为 True。
    :param kwargs: 其他可选参数，将传递给底层的 `AsyncDingTalkSender`。
    :return: 发送结果的字典。
    """
    client = AsyncClient(
        sender_type="dingtalk",
        webhook=webhook,
        secret=secret,
        msg_type=msg_type,
        at_mobiles=at_mobiles,
        is_at_all=is_at_all,
        message=message
    )
    return await client.send(message, msg_type=msg_type, at_mobiles=at_mobiles, is_at_all=is_at_all, **kwargs)


async def send_wecom_webhook_async(
    message: Union[str, Dict[str, Any]],
    webhook: str,
    msg_type: str = "text", # 默认消息类型为文本
    **kwargs: Any
) -> Dict[str, Any]:
    """
    直接发送异步企业微信 Webhook 消息。

    :param message: 消息内容。如果为 text 类型，可以直接传入字符串；其他类型需要传入字典。
    :param webhook: 企业微信机器人的 Webhook 地址。
    :param msg_type: 消息类型，默认为 "text"。支持 "text", "markdown", "image", "news", "file", "textcard", "template_card" 等。
    :param kwargs: 其他可选参数，将传递给底层的 `AsyncWeComWebhookSender`。
    :return: 发送结果的字典。
    """
    client = AsyncClient(
        sender_type="wecom_webhook",
        webhook=webhook,
        msg_type=msg_type,
        message=message
    )
    return await client.send(message, msg_type=msg_type, **kwargs)


async def send_wecom_app_async(
    message: Union[str, Dict[str, Any]],
    corpid: str,
    corpsecret: str,
    agentid: int,
    msg_type: str = "text", # 默认消息类型为文本
    touser: Optional[Union[str, List[str]]] = "@all", # 默认 @所有人
    toparty: Optional[Union[str, List[str]]] = None,
    totag: Optional[Union[str, List[str]]] = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """
    直接发送异步企业微信应用消息。

    :param message: 消息内容。如果为 text 类型，可以直接传入字符串；其他类型需要传入字典。
    :param corpid: 企业 ID。
    :param corpsecret: 应用的 Secret。
    :param agentid: 应用的 AgentId。
    :param msg_type: 消息类型，默认为 "text"。支持 "text", "image", "voice", "video", "file", "textcard", "news", "mpnews", "markdown", "miniprogram_notice", "template_card" 等。
    :param touser: 指定接收消息的成员，成员 ID 列表（最多支持 1000 个）。默认为 "@all"。
    :param toparty: 指定接收消息的部门 ID 列表（最多支持 100 个）。
    :param totag: 指定接收消息的标签 ID 列表（最多支持 100 个）。
    :param kwargs: 其他可选参数，将传递给底层的 `AsyncWeComAppSender`。
    :return: 发送结果的字典。
    """
    client = AsyncClient(
        sender_type="wecom_app",
        corpid=corpid,
        corpsecret=corpsecret,
        agentid=agentid,
        msg_type=msg_type,
        touser=touser,
        toparty=toparty,
        totag=totag,
        message=message
    )
    return await client.send(message, msg_type=msg_type, touser=touser, toparty=toparty, totag=totag, **kwargs)