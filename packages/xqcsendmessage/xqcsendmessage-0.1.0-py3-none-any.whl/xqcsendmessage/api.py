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
    send_md: bool = False, 
    at_mobiles: Optional[List[str]] = None,
    at_userids: Optional[List[str]] = None, 
    is_at_all: bool = False,
    touser: Optional[Union[str, List[str]]] = None,
    toparty: Optional[Union[str, List[str]]] = None,
    totag: Optional[Union[str, List[str]]] = None,
    title: Optional[str] = None,
) -> Dict[str, Any]:
    """
    构建钉钉或企业微信的消息体，处理消息格式和 @ 人等参数。
    """
    final_message_body: Dict[str, Any]
    if isinstance(message, str):
        if send_md:
            # 钉钉 Markdown 消息体需要 title 和 text
            if title:
                final_message_body = {
                    "msgtype": "markdown",
                    "markdown": {"title": title, "text": message}
                }
            # 企业微信 Markdown 消息体只需要 content
            else:
                # 钉钉 Markdown 消息体需要 title 和 text, 并且 @ 用户需要添加到 text 中
                at_text = ""
                if at_userids:
                    at_text = "".join([f"@{uid}" for uid in at_userids]) + " "
                
                if title:
                    final_message_body = {
                        "msgtype": "markdown",
                        "markdown": {"title": title, "text": at_text + message}
                    }
                # 企业微信 Markdown 消息体只需要 content, 并且 @ 用户需要添加到 content 中
                else:
                    final_message_body = {
                        "msgtype": "markdown",
                        "markdown": {"content": at_text + message}
                    }
        else:
            final_message_body = {
                "msgtype": "text",
                "text": {"content": message}
            }
    elif isinstance(message, dict):
        final_message_body = message
        if "msgtype" not in final_message_body:
            final_message_body["msgtype"] = "markdown" if send_md else "text"
        
        if send_md:
            # 处理 Markdown 消息体中的 @ 用户
            at_text = ""
            if at_userids:
                at_text = "".join([f"@{uid}" for uid in at_userids]) + " "

            if "markdown" not in final_message_body:
                final_message_body["markdown"] = {"content": at_text + message}
            else:
                if "content" in final_message_body["markdown"]:
                    final_message_body["markdown"]["content"] = at_text + final_message_body["markdown"]["content"]
                if "text" in final_message_body["markdown"]:
                    final_message_body["markdown"]["text"] = at_text + final_message_body["markdown"]["text"]

            if title and "title" not in final_message_body["markdown"]:
                final_message_body["markdown"]["title"] = title
            if "text" not in final_message_body["markdown"] and "content" in final_message_body["markdown"]:
                final_message_body["markdown"]["text"] = final_message_body["markdown"]["content"]
    else:
        raise SendMessageError("❌ 消息期望为字符串或字典类型。")

    # 钉钉特有参数
    if at_mobiles or at_userids or is_at_all:  # 修改判断条件
        final_message_body["at"] = {
            "atMobiles": at_mobiles,
            "atUserIds": at_userids,  # 添加 atUserIds
            "isAtAll": is_at_all
        }
    
    # 企业微信应用消息特有参数
    # 如果指定了 toparty 或 totag，且 touser 仍为默认值 "@all"，则不设置 touser
    if (toparty or totag) and touser == "@all":
        pass
    elif touser:
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
    send_md: bool = False,  # 默认为 False，发送 text 格式
    at_mobiles: Optional[List[str]] = None,
    at_userids: Optional[List[str]] = None,  # 新增 at_userids 参数
    is_at_all: bool = False,
    title: Optional[str] = None,  # Markdown 消息的标题，仅对钉钉 Markdown 消息有效
    **kwargs: Any
) -> Dict[str, Any]:
    """
    直接发送同步钉钉消息。

    :param message: 消息内容。如果 send_md 为 True，则按 Markdown 格式发送；否则按 text 格式发送。
                    如果传入字典，则直接作为消息体发送。
    :param webhook: 钉钉机器人的 Webhook 地址。
    :param secret: 钉钉机器人的密钥，用于签名。
    :param send_md: 是否发送 Markdown 格式消息，默认为 False (发送 text 格式)。
    :param at_mobiles: 被 @ 的用户的手机号列表。
    :param is_at_all: 是否 @ 所有人，默认为 False。
    :param title: Markdown 消息的标题，仅对钉钉 Markdown 消息有效。
    :param kwargs: 其他可选参数，将传递给底层的 `DingTalkSender`。
    :return: 发送结果的字典。
    """
    # 如果指定了 at_mobiles 或 at_userids，则 is_at_all 强制为 False
    if at_mobiles or at_userids:
        is_at_all = False
        
    sender = DingTalkSender(webhook=webhook, secret=secret)
    final_message_body = _build_dingtalk_wecom_message(
        message=message,
        send_md=send_md,
        at_mobiles=at_mobiles,
        at_userids=at_userids,
        is_at_all=is_at_all,
        title=title
    )
    return sender.send(final_message_body, **kwargs)


def send_markdown(
    message: str,
    platform: str,
    webhook: Optional[str] = None,
    secret: Optional[str] = None,
    corpid: Optional[str] = None,
    corpsecret: Optional[str] = None,
    agentid: Optional[int] = None,
    touser: Optional[Union[str, List[str]]] = "@all",
    toparty: Optional[Union[str, List[str]]] = None,
    totag: Optional[Union[str, List[str]]] = None,
    title: str = "Markdown消息", # 为钉钉 Markdown 消息添加 title 参数
    **kwargs: Any
) -> Dict[str, Any]:
    """
    统一发送同步 Markdown 消息。

    :param message: Markdown 格式的消息内容。
    :param platform: 目标平台，支持 "dingtalk", "wecom_webhook", "wecom_app"。
    :param webhook: 钉钉或企业微信 Webhook 地址。
    :param secret: 钉钉机器人的密钥。
    :param corpid: 企业微信企业 ID。
    :param corpsecret: 企业微信应用 Secret。
    :param agentid: 企业微信应用 AgentId。
    :param touser: 企业微信应用消息接收成员。
    :param toparty: 企业微信应用消息接收部门。
    :param totag: 企业微信应用消息接收标签。
    :param title: Markdown 消息的标题，仅对钉钉 Markdown 消息有效。
    :param kwargs: 其他可选参数。
    :return: 发送结果的字典。
    """
    if platform == "dingtalk":
        if not webhook:
            raise SendMessageError("❌ 钉钉发送 Markdown 消息缺少 webhook。")
        return send_dingtalk(
            message=message,
            webhook=webhook,
            secret=secret,
            send_md=True,
            title=title,
            **kwargs
        )
    elif platform == "wecom_webhook":
        if not webhook:
            raise SendMessageError("❌ 企业微信 Webhook 发送 Markdown 消息缺少 webhook。")
        return send_wecom_webhook(
            message=message,
            webhook=webhook,
            send_md=True,
            **kwargs
        )
    elif platform == "wecom_app":
        if not (corpid and corpsecret and agentid):
            raise SendMessageError("❌ 企业微信应用发送 Markdown 消息缺少 corpid, corpsecret 或 agentid。")
        return send_wecom_app(
            message=message,
            corpid=corpid,
            corpsecret=corpsecret,
            agentid=agentid,
            send_md=True,
            touser=touser,
            toparty=toparty,
            totag=totag,
            **kwargs
        )
    else:
        raise SendMessageError(f"❌ 不支持的平台: {platform}")


def send_wecom_webhook(
    message: Union[str, Dict[str, Any]],
    webhook: str,
    send_md: bool = False,  # 默认为 False，发送 text 格式
    **kwargs: Any
) -> Dict[str, Any]:
    """
    直接发送同步企业微信 Webhook 消息。

    :param message: 消息内容。如果 send_md 为 True，则按 Markdown 格式发送；否则按 text 格式发送。
                    如果传入字典，则直接作为消息体发送。
    :param webhook: 企业微信机器人的 Webhook 地址。
    :param send_md: 是否发送 Markdown 格式消息，默认为 False (发送 text 格式)。
    :param kwargs: 其他可选参数，将传递给底层的 `WeComWebhookSender`。
    :return: 发送结果的字典。
    """
    sender = WeComWebhookSender(webhook=webhook)
    final_message_body = _build_dingtalk_wecom_message(
        message=message,
        send_md=send_md,
    )
    return sender.send(final_message_body, **kwargs)


def send_wecom_app(
    message: Union[str, Dict[str, Any]],
    corpid: str,
    corpsecret: str,
    agentid: int,
    send_md: bool = False,  # 默认为 False，发送 text 格式
    touser: Optional[Union[str, List[str]]] = "@all",
    toparty: Optional[Union[str, List[str]]] = None,
    totag: Optional[Union[str, List[str]]] = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """
    直接发送同步企业微信应用消息。

    :param message: 消息内容。如果 send_md 为 True，则按 Markdown 格式发送；否则按 text 格式发送。
                    如果传入字典，则直接作为消息体发送。
    :param corpid: 企业 ID。
    :param corpsecret: 应用的 Secret。
    :param agentid: 应用的 AgentId。
    :param send_md: 是否发送 Markdown 格式消息，默认为 False (发送 text 格式)。
    :param touser: 指定接收消息的成员，成员 ID 列表（最多支持 1000 个）。默认为 "@all"。
    :param toparty: 指定接收消息的部门 ID 列表（最多支持 100 个）。
    :param totag: 指定接收消息的标签 ID 列表（最多支持 100 个）。
    :param kwargs: 其他可选参数，将传递给底层的 `WeComAppSender`。
    :return: 发送结果的字典。
    """
    # 如果指定了 toparty 或 totag，且 touser 仍为默认值 "@all"，则将其设为 ""，避免冲突
    if (toparty or totag) and touser == "@all":
        touser = ""

    sender = WeComAppSender(corpid=corpid, corpsecret=corpsecret, agentid=agentid)
    final_message_body = _build_dingtalk_wecom_message(
        message=message,
        send_md=send_md,
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
    send_md: bool = False,  # 默认为 False，发送 text 格式
    at_mobiles: Optional[List[str]] = None,
    at_userids: Optional[List[str]] = None,  # 新增 at_userids 参数
    is_at_all: bool = False,
    title: Optional[str] = None,  # Markdown 消息的标题，仅对钉钉 Markdown 消息有效
    **kwargs: Any
) -> Dict[str, Any]:
    """
    直接发送异步钉钉消息。

    :param message: 消息内容。如果 send_md 为 True，则按 Markdown 格式发送；否则按 text 格式发送。
                    如果传入字典，则直接作为消息体发送。
    :param webhook: 钉钉机器人的 Webhook 地址。
    :param secret: 钉钉机器人的密钥，用于签名。
    :param send_md: 是否发送 Markdown 格式消息，默认为 False (发送 text 格式)。
    :param at_mobiles: 被 @ 的用户的手机号列表。
    :param is_at_all: 是否 @ 所有人，默认为 False。
    :param title: Markdown 消息的标题，仅对钉钉 Markdown 消息有效。
    :param kwargs: 其他可选参数，将传递给底层的 `AsyncDingTalkSender`。
    :return: 发送结果的字典。
    """
    # 如果指定了 at_mobiles 或 at_userids，则 is_at_all 强制为 False
    if at_mobiles or at_userids:
        is_at_all = False
        
    sender = AsyncDingTalkSender(webhook=webhook, secret=secret)
    final_message_body = _build_dingtalk_wecom_message(
        message=message,
        send_md=send_md,
        at_mobiles=at_mobiles,
        at_userids=at_userids,
        is_at_all=is_at_all,
        title=title
    )
    return await sender.send(final_message_body, **kwargs)


async def send_wecom_webhook_async(
    message: Union[str, Dict[str, Any]],
    webhook: str,
    send_md: bool = False,  # 默认为 False，发送 text 格式
    **kwargs: Any
) -> Dict[str, Any]:
    """
    直接发送异步企业微信 Webhook 消息。

    :param message: 消息内容。如果 send_md 为 True，则按 Markdown 格式发送；否则按 text 格式发送。
                    如果传入字典，则直接作为消息体发送。
    :param webhook: 企业微信机器人的 Webhook 地址。
    :param send_md: 是否发送 Markdown 格式消息，默认为 False (发送 text 格式)。
    :param kwargs: 其他可选参数，将传递给底层的 `AsyncWeComWebhookSender`。
    :return: 发送结果的字典。
    """
    sender = AsyncWeComWebhookSender(webhook=webhook)
    final_message_body = _build_dingtalk_wecom_message(
        message=message,
        send_md=send_md,
    )
    return await sender.send(final_message_body, **kwargs)


async def send_wecom_app_async(
    message: Union[str, Dict[str, Any]],
    corpid: str,
    corpsecret: str,
    agentid: int,
    send_md: bool = False,  # 默认为 False，发送 text 格式
    touser: Optional[Union[str, List[str]]] = "@all",
    toparty: Optional[Union[str, List[str]]] = None,
    totag: Optional[Union[str, List[str]]] = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """
    直接发送异步企业微信应用消息。

    :param message: 消息内容。如果 send_md 为 True，则按 Markdown 格式发送；否则按 text 格式发送。
                    如果传入字典，则直接作为消息体发送。
    :param corpid: 企业 ID。
    :param corpsecret: 应用的 Secret。
    :param agentid: 应用的 AgentId。
    :param send_md: 是否发送 Markdown 格式消息，默认为 False (发送 text 格式)。
    :param touser: 指定接收消息的成员，成员 ID 列表（最多支持 1000 个）。默认为 "@all"。
    :param toparty: 指定接收消息的部门 ID 列表（最多支持 100 个）。
    :param totag: 指定接收消息的标签 ID 列表（最多支持 100 个）。
    :param kwargs: 其他可选参数，将传递给底层的 `AsyncWeComAppSender`。
    :return: 发送结果的字典。
    """
    # 如果指定了 toparty 或 totag，且 touser 仍为默认值 "@all"，则将其设为 ""，避免冲突
    if (toparty or totag) and touser == "@all":
        touser = ""
        
    sender = AsyncWeComAppSender(corpid=corpid, corpsecret=corpsecret, agentid=agentid)
    final_message_body = _build_dingtalk_wecom_message(
        message=message,
        send_md=send_md,
        touser=touser,
        toparty=toparty,
        totag=totag,
    )
    return await sender.send(final_message_body, **kwargs)
