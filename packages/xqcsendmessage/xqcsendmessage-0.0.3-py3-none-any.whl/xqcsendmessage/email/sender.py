# 作者：Xiaoqiang
# 微信公众号：XiaoqiangClub
# 创建时间：2025-11-12T00:11:45.483Z
# 文件描述：邮件发送器
# 文件路径：xqcsendmessage/email/sender.py

import smtplib
import aiosmtplib
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import Any, Dict, List, Optional

from ..core.abc import Sender, AsyncSender
from ..core.exceptions import SendMessageError
from ..core.logger import default_logger


class EmailSender(Sender):
    """
    邮件同步发送器。
    """

    def __init__(self, smtp_server: str, smtp_port: int, sender_email: str, sender_password: str, use_tls: bool = True):
        """
        初始化邮件同步发送器。

        :param smtp_server: SMTP 服务器地址。
        :param smtp_port: SMTP 服务器端口。
        :param sender_email: 发件人邮箱。
        :param sender_password: 发件人邮箱密码或授权码。
        :param use_tls: 是否使用 TLS 加密。
        """
        self.smtp_server = smtp_server
        self.smtp_port = int(smtp_port)
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.use_tls = use_tls
        self.logger = default_logger

    def send(self, message: str,  email_subject: str, email_recipients: List[str], email_subtype: str = "plain", email_attachments: Optional[List[str]] = None, **kwargs: Any) -> Dict[str, Any]:
        """
        发送邮件。

        :param message: 邮件内容。
        :param email_subject: 邮件主题。
        :param email_recipients: 收件人列表。
        :param email_subtype: 邮件内容类型，'plain' 或 'html'。
        :param email_attachments: 附件文件路径列表。
        :param kwargs: 其他可选参数。
        :return: 发送结果。
        """
        msg_root = MIMEMultipart()
        msg_root["From"] = self.sender_email
        msg_root["To"] = ", ".join(email_recipients)
        if email_subject is None:
            raise SendMessageError("发送邮件失败: 邮件主题 (email_subject) 不能为空。")
        msg_root["Subject"] = str(Header(email_subject, "utf-8"))
        msg_root.attach(MIMEText(message, email_subtype, "utf-8"))

        if email_attachments:
            for file_path in email_attachments:
                try:
                    with open(file_path, "rb") as f:
                        part = MIMEApplication(
                            f.read(), Name=file_path.split("/")[-1])
                    part["Content-Disposition"] = f'attachment; filename="{file_path.split("/")[-1]}"'
                    msg_root.attach(part)
                except Exception as e:
                    self.logger.warning(f"⚠️ 添加附件 {file_path} 失败: {e}")

        try:
            # 对于端口 465，通常直接使用 SMTP_SSL
            if self.smtp_port == 465:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                if self.use_tls:
                    server.starttls()

            with server:
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, email_recipients,
                                msg_root.as_string())
                self.logger.info(f"🎉 邮件发送成功至: {email_recipients}")
                return {"status": "success", "recipients": email_recipients}
        except Exception as e:
            self.logger.error(f"🔥 发送邮件时发生错误: {e}")
            raise SendMessageError(f"发送邮件失败: {e}")


class AsyncEmailSender(AsyncSender):
    """
    邮件异步发送器。
    """

    def __init__(self, smtp_server: str, smtp_port: int, sender_email: str, sender_password: str, use_tls: bool = True):
        """
        初始化邮件异步发送器。

        :param smtp_server: SMTP 服务器地址。
        :param smtp_port: SMTP 服务器端口。
        :param sender_email: 发件人邮箱。
        :param sender_password: 发件人邮箱密码或授权码。
        :param use_tls: 是否使用 TLS 加密。
        """
        self.smtp_server = smtp_server
        self.smtp_port = int(smtp_port)
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.use_tls = use_tls
        self.logger = default_logger

    async def send(self, message: str, email_subject: str, email_recipients: List[str],  email_subtype: str = "plain", email_attachments: Optional[List[str]] = None, **kwargs: Any) -> Dict[str, Any]:
        """
        异步发送邮件。

        :param message: 邮件内容。
        :param email_subject: 邮件主题。
        :param email_recipients: 收件人列表。
        :param email_subtype: 邮件内容类型，'plain' 或 'html'。
        :param email_attachments: 附件文件路径列表。
        :param kwargs: 其他可选参数，将传递给底层的 `AsyncEmailSender`。
        :return: 发送结果。
        """
        msg_root = MIMEMultipart()
        msg_root["From"] = self.sender_email
        msg_root["To"] = ", ".join(email_recipients)
        if email_subject is None:
            raise SendMessageError("发送邮件失败: 邮件主题 (email_subject) 不能为空。")
        msg_root["Subject"] = str(Header(email_subject, "utf-8"))
        msg_root.attach(MIMEText(message, email_subtype, "utf-8"))

        if email_attachments:
            for file_path in email_attachments:
                try:
                    with open(file_path, "rb") as f:
                        part = MIMEApplication(
                            f.read(), Name=file_path.split("/")[-1])
                    part["Content-Disposition"] = f'attachment; filename="{file_path.split("/")[-1]}"'
                    msg_root.attach(part)
                except Exception as e:
                    self.logger.warning(f"⚠️ 添加附件 {file_path} 失败: {e}")

        try:
            # 对于端口 465，aiosmtplib 的 use_tls 应该设置为 True
            if self.smtp_port == 465:
                server = aiosmtplib.SMTP(
                    hostname=self.smtp_server, port=self.smtp_port, use_tls=True)
            else:
                server = aiosmtplib.SMTP(
                    hostname=self.smtp_server, port=self.smtp_port, use_tls=self.use_tls)

            async with server:
                await server.login(self.sender_email, self.sender_password)
                await server.sendmail(self.sender_email, email_recipients, msg_root.as_string())
                self.logger.info(f"🎉 邮件发送成功至: {email_recipients}")
                return {"status": "success", "recipients": email_recipients}
        except Exception as e:
            self.logger.error(f"🔥 发送邮件时发生错误: {e}")
            raise SendMessageError(f"发送邮件失败: {e}")
