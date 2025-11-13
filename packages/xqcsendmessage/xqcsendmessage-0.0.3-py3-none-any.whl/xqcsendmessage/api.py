# 作者：Xiaoqiang
# 微信公众号：XiaoqiangClub
# 创建时间：2025-11-12T01:10:00.168Z
# 文件描述：提供统一的同步和异步消息发送函数，作为模块的顶层 API。
# 文件路径：xqcsendmessage/api.py

from typing import Any, Dict, List, Optional, Union
import asyncio

# 导入所有发送器
from .dingtalk.sender import DingTalkSender, AsyncDingTalkSender
from .wecom.sender import (
    WeComWebhookSender,
    AsyncWeComWebhookSender,
    WeComAppSender,
    AsyncWeComAppSender,
)
from .email.sender import EmailSender, AsyncEmailSender
from .core.exceptions import SendMessageError

# --- 辅助函数：消息体构建 ---
def _build_dingtalk_wecom_message(
    message: Union[str, Dict[str, Any]],
    msg_type: str,
    at_mobiles: Optional[List[str]] = None,
    is_at_all: bool = False,
    touser: Optional[Union[str, List[str]]] = None,
    toparty: Optional[Union[str, List[str]]] = None,
    totag: Optional[Union[str, List[str]]] = None,
) -> Dict[str, Any]:
    """
    构建钉钉或企业微信的消息体，处理消息格式和 @ 人等参数。
    """
    final_message_body: Dict[str, Any]
    if isinstance(message, str):
        final_message_body = {
            "msgtype": msg_type,
            "text": {"content": message}
        }
    elif isinstance(message, dict):
        final_message_body = message
        if "msgtype" not in final_message_body:
            final_message_body["msgtype"] = msg_type
    else:
        raise SendMessageError("❌ 消息期望为字符串或字典类型。")

    # 钉钉特有参数
    if at_mobiles or is_at_all:
        final_message_body["at"] = {
            "atMobiles": at_mobiles,
            "isAtAll": is_at_all
        }
    
    # 企业微信应用消息特有参数
    if touser:
        final_message_body["touser"] = touser if isinstance(touser, str) else "|".join(touser)
    if toparty:
        final_message_body["toparty"] = toparty if isinstance(toparty, str) else "|".join(toparty)
    if totag:
        final_message_body["totag"] = totag if isinstance(totag, str) else "|".join(totag)

    return final_message_body


# --- 同步发送函数 ---


def send_email(
    message: str,
    email_subject: str,
    smtp_server: str,
    smtp_port: int,
    sender_email: str,
    sender_password: str,
    email_recipients: List[str],
    email_subtype: str = "plain",
    use_tls: bool = True,
    email_attachments: Optional[List[str]] = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """
    直接发送同步邮件。

    :param message: 邮件内容。
    :param email_subject: 邮件主题。
    :param smtp_server: SMTP 服务器地址。
    :param smtp_port: SMTP 服务器端口。
    :param sender_email: 发件人邮箱。
    :param sender_password: 发件人邮箱密码或授权码。
    :param email_recipients: 收件人列表。
    :param email_subtype: 邮件内容类型，'plain' 或 'html'。
    :param use_tls: 是否使用 TLS 加密。
    :param email_attachments: 附件文件路径列表。
    :param kwargs: 其他可选参数，将传递给底层的 `EmailSender`。
    :return: 发送结果的字典。
    """
    if not email_subject or not message or not email_recipients:
        raise SendMessageError("❌ 邮件发送缺少必要的参数：message, email_subject 或 email_recipients。")

    sender = EmailSender(
        smtp_server=smtp_server,
        smtp_port=smtp_port,
        sender_email=sender_email,
        sender_password=sender_password,
        use_tls=use_tls,
    )
    return sender.send(
        message=message,
        email_subject=email_subject,
        email_recipients=email_recipients,
        email_subtype=email_subtype,
        email_attachments=email_attachments,
        **kwargs
    )


def send_dingtalk(
    message: Union[str, Dict[str, Any]],
    webhook: str,
    secret: Optional[str] = None,
    msg_type: str = "text",
    at_mobiles: Optional[List[str]] = None,
    is_at_all: bool = False,
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
    :param is_at_all: 是否 @ 所有人，默认为 False。
    :param kwargs: 其他可选参数，将传递给底层的 `DingTalkSender`。
    :return: 发送结果的字典。
    """
    sender = DingTalkSender(webhook=webhook, secret=secret)
    final_message_body = _build_dingtalk_wecom_message(
        message=message,
        msg_type=msg_type,
        at_mobiles=at_mobiles,
        is_at_all=is_at_all,
    )
    return sender.send(final_message_body, **kwargs)


def send_wecom_webhook(
    message: Union[str, Dict[str, Any]],
    webhook: str,
    msg_type: str = "text",
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
    sender = WeComWebhookSender(webhook=webhook)
    final_message_body = _build_dingtalk_wecom_message(
        message=message,
        msg_type=msg_type,
    )
    return sender.send(final_message_body, **kwargs)


def send_wecom_app(
    message: Union[str, Dict[str, Any]],
    corpid: str,
    corpsecret: str,
    agentid: int,
    msg_type: str = "text",
    touser: Optional[Union[str, List[str]]] = "@all",
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
    sender = WeComAppSender(corpid=corpid, corpsecret=corpsecret, agentid=agentid)
    final_message_body = _build_dingtalk_wecom_message(
        message=message,
        msg_type=msg_type,
        touser=touser,
        toparty=toparty,
        totag=totag,
    )
    return sender.send(final_message_body, **kwargs)


# --- 异步发送函数 ---


async def send_email_async(
    message: str,
    email_subject: str,
    smtp_server: str,
    smtp_port: int,
    sender_email: str,
    sender_password: str,
    email_recipients: List[str],
    email_subtype: str = "plain",
    use_tls: bool = True,
    email_attachments: Optional[List[str]] = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """
    直接发送异步邮件。

    :param message: 邮件内容。
    :param email_subject: 邮件主题。
    :param smtp_server: SMTP 服务器地址。
    :param smtp_port: SMTP 服务器端口。
    :param sender_email: 发件人邮箱。
    :param sender_password: 发件人邮箱密码或授权码。
    :param email_recipients: 收件人列表。
    :param email_subtype: 邮件内容类型，'plain' 或 'html'。
    :param use_tls: 是否使用 TLS 加密。
    :param email_attachments: 附件文件路径列表。
    :param kwargs: 其他可选参数，将传递给底层的 `AsyncEmailSender`。
    :return: 发送结果的字典。
    """
    if not email_subject or not message or not email_recipients:
        raise SendMessageError("❌ 邮件发送缺少必要的参数：message, email_subject 或 email_recipients。")

    sender = AsyncEmailSender(
        smtp_server=smtp_server,
        smtp_port=smtp_port,
        sender_email=sender_email,
        sender_password=sender_password,
        use_tls=use_tls,
    )
    return await sender.send(
        message=message,
        email_subject=email_subject,
        email_recipients=email_recipients,
        email_subtype=email_subtype,
        email_attachments=email_attachments,
        **kwargs
    )


async def send_dingtalk_async(
    message: Union[str, Dict[str, Any]],
    webhook: str,
    secret: Optional[str] = None,
    msg_type: str = "text",
    at_mobiles: Optional[List[str]] = None,
    is_at_all: bool = False,
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
    :param is_at_all: 是否 @ 所有人，默认为 False。
    :param kwargs: 其他可选参数，将传递给底层的 `AsyncDingTalkSender`。
    :return: 发送结果的字典。
    """
    sender = AsyncDingTalkSender(webhook=webhook, secret=secret)
    final_message_body = _build_dingtalk_wecom_message(
        message=message,
        msg_type=msg_type,
        at_mobiles=at_mobiles,
        is_at_all=is_at_all,
    )
    return await sender.send(final_message_body, **kwargs)


async def send_wecom_webhook_async(
    message: Union[str, Dict[str, Any]],
    webhook: str,
    msg_type: str = "text",
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
    sender = AsyncWeComWebhookSender(webhook=webhook)
    final_message_body = _build_dingtalk_wecom_message(
        message=message,
        msg_type=msg_type,
    )
    return await sender.send(final_message_body, **kwargs)


async def send_wecom_app_async(
    message: Union[str, Dict[str, Any]],
    corpid: str,
    corpsecret: str,
    agentid: int,
    msg_type: str = "text",
    touser: Optional[Union[str, List[str]]] = "@all",
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
    sender = AsyncWeComAppSender(corpid=corpid, corpsecret=corpsecret, agentid=agentid)
    final_message_body = _build_dingtalk_wecom_message(
        message=message,
        msg_type=msg_type,
        touser=touser,
        toparty=toparty,
        totag=totag,
    )
    return await sender.send(final_message_body, **kwargs)
