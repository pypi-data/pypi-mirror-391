# 作者：Xiaoqiang
# 微信公众号：XiaoqiangClub
# 创建时间：2025-11-12T00:20:11.637Z
# 文件描述：xqcsendmessage 包的初始化文件，暴露公共 API。
# 文件路径：xqcsendmessage/__init__.py

from .core.exceptions import (
    SendMessageError,
    HttpError,
    AuthError,
    ValidationError,
)
from .api import (
    send_email,
    send_dingtalk,
    send_wecom_webhook,
    send_wecom_app,
    send_email_async,
    send_dingtalk_async,
    send_wecom_webhook_async,
    send_wecom_app_async,
)
from .core.utils import read_file, read_file_async

__all__ = [
    # 发送信息
    "send_email",
    "send_dingtalk",
    "send_wecom_webhook",
    "send_wecom_app",
    "send_email_async",
    "send_dingtalk_async",
    "send_wecom_webhook_async",
    "send_wecom_app_async",

    # 文件读取工具
    "read_file",
    "read_file_async",

    # 异常
    "SendMessageError",
    "HttpError",
    "AuthError",
    "ValidationError",
]
