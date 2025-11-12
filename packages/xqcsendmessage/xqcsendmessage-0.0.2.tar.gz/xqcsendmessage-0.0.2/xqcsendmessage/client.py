# 作者：Xiaoqiang
# 微信公众号：XiaoqiangClub
# 创建时间：2025-11-12T01:58:39.018Z
# 文件描述：统一的同步和异步消息发送客户端，支持多种发送器类型。
# 文件路径：xqcsendmessage/client.py

from typing import Any, Dict, Type, Union, Optional, Literal, overload

from .core.abc import Sender, AsyncSender
from .core.exceptions import SendMessageError
from .core.logger import default_logger

# 导入所有发送器
from .dingtalk.sender import DingTalkSender, AsyncDingTalkSender
from .wecom.sender import (
    WeComWebhookSender,
    AsyncWeComWebhookSender,
    WeComAppSender,
    AsyncWeComAppSender,
)
from .email.sender import EmailSender, AsyncEmailSender

SenderType = Literal["email", "dingtalk", "wecom_webhook", "wecom_app"]

class BaseClient:
    """
    消息发送客户端的基类，提供发送器注册和动态创建机制。
    """
    _SENDER_MAP: Dict[SenderType, Type[Sender]] = {}
    _ASYNC_SENDER_MAP: Dict[SenderType, Type[AsyncSender]] = {}

    def __init__(self, sender_type: SenderType, **config: Any):
        """
        初始化客户端。

        :param sender_type: 发送器类型字符串 (例如: "email", "dingtalk", "wecom_webhook", "wecom_app")。
        :param config: 发送器初始化所需的配置参数，也可以包含消息的默认参数。
        """
        self._initial_sender_type = sender_type
        self._initial_config = config
        self._sender_instance: Optional[Union[Sender, AsyncSender]] = None
        self.logger = default_logger

        # 存储消息的默认参数
        self._default_message_args: Dict[str, Any] = {}
        if sender_type == "email":
            self._default_message_args["subject"] = config.pop("subject", None)
            self._default_message_args["content"] = config.pop("content", None)
            self._default_message_args["recipients"] = config.pop("recipients", None)
            self._default_message_args["subtype"] = config.pop("subtype", "plain")
        elif sender_type in ["dingtalk", "wecom_webhook", "wecom_app"]:
            # 存储消息的默认参数，这些参数可以在 send 方法中被覆盖
            # 钉钉支持的额外参数：msg_type, at_mobiles, is_at_all
            # 企业微信支持的额外参数：msg_type, touser, toparty, totag
            # 同时兼容旧的 message 参数
            for key in [
                "msg_type", "at_mobiles", "is_at_all",
                "touser", "toparty", "totag",
                "safe", "enable_duplicate_check", "duplicate_check_interval",
                "message" # 兼容旧的 message 参数
            ]:
                if key in config:
                    self._default_message_args[key] = config.pop(key)

    @classmethod
    def register_sender(cls, name: SenderType, sender_class: Type[Sender]):
        """
        注册同步发送器。

        :param name: 发送器名称。
        :param sender_class: 发送器类。
        """
        cls._SENDER_MAP[name] = sender_class

    @classmethod
    def register_async_sender(cls, name: SenderType, sender_class: Type[AsyncSender]):
        """
        注册异步发送器。

        :param name: 发送器名称。
        :param sender_class: 异步发送器类。
        """
        cls._ASYNC_SENDER_MAP[name] = sender_class

    def _get_sender_instance(self, is_async: bool, **override_config: Any) -> Union[Sender, AsyncSender]:
        """
        根据类型和配置获取发送器实例。

        :param is_async: 是否获取异步发送器。
        :param override_config: 覆盖初始化配置的参数。
        :return: 发送器实例。
        """
        sender_map = self._ASYNC_SENDER_MAP if is_async else self._SENDER_MAP
        sender_class = sender_map.get(self._initial_sender_type)

        if not sender_class:
            raise SendMessageError(f"❌ 不支持的发送器类型: {self._initial_sender_type}")

        # 合并配置，override_config 优先
        final_config = {**self._initial_config, **override_config}
        
        # 优化：如果配置未改变且实例已存在，则直接返回现有实例
        # 注意：这里简化处理，实际生产环境可能需要更复杂的缓存策略，例如哈希配置字典进行比较
        if (self._sender_instance
            and self._sender_instance.__class__ == sender_class
            and self._initial_config == final_config): # 简化比较
            return self._sender_instance

        try:
            self._sender_instance = sender_class(**final_config)
            return self._sender_instance
        except TypeError as e:
            raise SendMessageError(f"❌ 发送器 '{self._initial_sender_type}' 初始化失败，请检查配置参数: {e}")

# 注册所有发送器
BaseClient.register_sender("dingtalk", DingTalkSender)
BaseClient.register_async_sender("dingtalk", AsyncDingTalkSender)

BaseClient.register_sender("wecom_webhook", WeComWebhookSender)
BaseClient.register_async_sender("wecom_webhook", AsyncWeComWebhookSender)

BaseClient.register_sender("wecom_app", WeComAppSender)
BaseClient.register_async_sender("wecom_app", AsyncWeComAppSender)

BaseClient.register_sender("email", EmailSender)
BaseClient.register_async_sender("email", AsyncEmailSender)


class SyncClient(BaseClient):
    """
    同步消息发送客户端，封装了同步发送器的调用。
    """
    @overload
    def send(self, message: str, **kwargs: Any) -> Dict[str, Any]: ...

    @overload
    def send(self, message: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]: ...

    def send(self, message: Optional[Union[str, Dict[str, Any]]] = None, **kwargs: Any) -> Dict[str, Any]:
        """
        通过指定的发送器发送消息。

        :param message: 要发送的消息内容。
                        对于邮件，可以是 subject (str), content (str), recipients (List[str]), subtype (str)。
                        对于钉钉/企业微信，可以是消息体字典，或者直接是字符串（将自动封装为 text 消息）。
        :param kwargs: 其他发送器所需的关键字参数，会覆盖初始化时设置的默认配置。
                       对于邮件，可以包含 subject, content, recipients, subtype 等。
                       对于钉钉/企业微信，会直接传递给底层的 sender.send 方法。
        :return: API 响应。
        """
        # 允许 send 方法中的参数覆盖初始化时的配置参数
        override_config = {k: v for k, v in kwargs.items() if k in self._initial_config}
        
        sender = self._get_sender_instance(is_async=False, **override_config)

        if self._initial_sender_type == "email":
            # 邮件发送器期望 subject, content, recipients, subtype 作为单独的参数
            # message 参数对于邮件类型不适用，从 kwargs 或 _default_message_args 获取
            subject = kwargs.get("subject", self._default_message_args.get("subject"))
            content = kwargs.get("content", self._default_message_args.get("content"))

            if content is None and isinstance(message, str):
                content = message
            elif isinstance(message, Dict):
                raise SendMessageError("❌ 邮件发送的 message 参数不能是字典类型，请使用 content 参数指定邮件内容。")
            
            recipients = kwargs.get("recipients", self._default_message_args.get("recipients"))
            subtype = kwargs.get("subtype", self._default_message_args.get("subtype", "plain"))

            if not subject or not content or not recipients:
                raise SendMessageError("❌ 邮件发送缺少必要的参数：subject, content 或 recipients。")
            
            # 邮件发送器不接受 message 参数，因此直接传递其他参数
            # 过滤掉 kwargs 中与 subject, content, recipients, subtype 重复的参数
            email_kwargs = {k: v for k, v in kwargs.items() if k not in ["subject", "content", "recipients", "subtype"]}
            return sender.send(subject=subject, content=content, recipients=recipients, subtype=subtype, **email_kwargs)
        else:
            # 钉钉/企业微信发送器
            # 合并默认消息参数和 send 方法传入的 kwargs
            # send 方法中的参数（message, kwargs）优先于初始化时的默认参数
            merged_kwargs = {**self._default_message_args, **kwargs}

            # 提取 msg_type，默认为 "text"
            msg_type = merged_kwargs.pop("msg_type", "text")

            # 如果传入的 message 是字符串，则构造一个文本消息字典
            if isinstance(message, str):
                final_message_body = {
                    "msgtype": msg_type,
                    "text": {"content": message}
                }
            elif isinstance(message, dict):
                final_message_body = message
                # 如果 message 是字典，且没有 msgtype 字段，则使用从 merged_kwargs 中提取的 msg_type
                if "msgtype" not in final_message_body:
                    final_message_body["msgtype"] = msg_type
            else:
                raise SendMessageError(f"❌ 发送器 '{self._initial_sender_type}' 期望消息为字符串或字典类型。")
            
            # 将钉钉和企业微信特有的参数添加到 merged_kwargs 中
            if self._initial_sender_type == "dingtalk":
                # 钉钉的 @ 成员参数
                at_mobiles = merged_kwargs.pop("at_mobiles", None)
                is_at_all = merged_kwargs.pop("is_at_all", False)
                if at_mobiles or is_at_all:
                    final_message_body["at"] = {
                        "atMobiles": at_mobiles,
                        "isAtAll": is_at_all
                    }
            elif self._initial_sender_type == "wecom_app":
                # 企业微信应用消息的发送对象参数
                touser = merged_kwargs.pop("touser", None)
                toparty = merged_kwargs.pop("toparty", None)
                totag = merged_kwargs.pop("totag", None)
                if touser:
                    final_message_body["touser"] = touser if isinstance(touser, str) else "|".join(touser)
                if toparty:
                    final_message_body["toparty"] = toparty if isinstance(toparty, str) else "|".join(toparty)
                if totag:
                    final_message_body["totag"] = totag if isinstance(totag, str) else "|".join(totag)

            # 确保 message 不会再次被作为 kwargs 传递
            merged_kwargs.pop("message", None)
            
            return sender.send(final_message_body, **merged_kwargs)


class AsyncClient(BaseClient):
    """
    异步消息发送客户端，封装了异步发送器的调用。
    """
    @overload
    async def send(self, message: str, **kwargs: Any) -> Dict[str, Any]: ...

    @overload
    async def send(self, message: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]: ...

    async def send(self, message: Optional[Union[str, Dict[str, Any]]] = None, **kwargs: Any) -> Dict[str, Any]:
        """
        通过指定的发送器异步发送消息。

        :param message: 要发送的消息内容。
                        对于邮件，可以是 subject (str), content (str), recipients (List[str]), subtype (str)。
                        对于钉钉/企业微信，可以是消息体字典，或者直接是字符串（将自动封装为 text 消息）。
        :param kwargs: 其他发送器所需的关键字参数，会覆盖初始化时设置的默认配置。
                       对于邮件，可以包含 subject, content, recipients, subtype 等。
                       对于钉钉/企业微信，会直接传递给底层的 sender.send 方法。
        :return: API 响应。
        """
        # 允许 send 方法中的参数覆盖初始化时的配置参数
        override_config = {k: v for k, v in kwargs.items() if k in self._initial_config}

        sender = self._get_sender_instance(is_async=True, **override_config)

        if self._initial_sender_type == "email":
            # 邮件发送器期望 subject, content, recipients, subtype 作为单独的参数
            # message 参数对于邮件类型不适用，从 kwargs 或 _default_message_args 获取
            subject = kwargs.get("subject", self._default_message_args.get("subject"))
            content = kwargs.get("content", self._default_message_args.get("content"))
            
            if content is None and isinstance(message, str):
                content = message
            elif isinstance(message, Dict):
                raise SendMessageError("❌ 邮件发送的 message 参数不能是字典类型，请使用 content 参数指定邮件内容。")

            recipients = kwargs.get("recipients", self._default_message_args.get("recipients"))
            subtype = kwargs.get("subtype", self._default_message_args.get("subtype", "plain"))

            if not subject or not content or not recipients:
                raise SendMessageError("❌ 邮件发送缺少必要的参数：subject, content 或 recipients。")
            
            # 邮件发送器不接受 message 参数，因此直接传递其他参数
            # 过滤掉 kwargs 中与 subject, content, recipients, subtype 重复的参数
            email_kwargs = {k: v for k, v in kwargs.items() if k not in ["subject", "content", "recipients", "subtype"]}
            return await sender.send(subject=subject, content=content, recipients=recipients, subtype=subtype, **email_kwargs)
        else:
            # 钉钉/企业微信发送器
            # 合并默认消息参数和 send 方法传入的 kwargs
            # send 方法中的参数（message, kwargs）优先于初始化时的默认参数
            merged_kwargs = {**self._default_message_args, **kwargs}

            # 提取 msg_type，默认为 "text"
            msg_type = merged_kwargs.pop("msg_type", "text")

            # 如果传入的 message 是字符串，则构造一个文本消息字典
            if isinstance(message, str):
                final_message_body = {
                    "msgtype": msg_type,
                    "text": {"content": message}
                }
            elif isinstance(message, dict):
                final_message_body = message
                # 如果 message 是字典，且没有 msgtype 字段，则使用从 merged_kwargs 中提取的 msg_type
                if "msgtype" not in final_message_body:
                    final_message_body["msgtype"] = msg_type
            else:
                raise SendMessageError(f"❌ 发送器 '{self._initial_sender_type}' 期望消息为字符串或字典类型。")
            
            # 将钉钉和企业微信特有的参数添加到 merged_kwargs 中
            if self._initial_sender_type == "dingtalk":
                # 钉钉的 @ 成员参数
                at_mobiles = merged_kwargs.pop("at_mobiles", None)
                is_at_all = merged_kwargs.pop("is_at_all", False)
                if at_mobiles or is_at_all:
                    final_message_body["at"] = {
                        "atMobiles": at_mobiles,
                        "isAtAll": is_at_all
                    }
            elif self._initial_sender_type == "wecom_app":
                # 企业微信应用消息的发送对象参数
                touser = merged_kwargs.pop("touser", None)
                toparty = merged_kwargs.pop("toparty", None)
                totag = merged_kwargs.pop("totag", None)
                if touser:
                    final_message_body["touser"] = touser if isinstance(touser, str) else "|".join(touser)
                if toparty:
                    final_message_body["toparty"] = toparty if isinstance(toparty, str) else "|".join(toparty)
                if totag:
                    final_message_body["totag"] = totag if isinstance(totag, str) else "|".join(totag)

            # 确保 message 不会再次被作为 kwargs 传递
            merged_kwargs.pop("message", None)
            
            return await sender.send(final_message_body, **merged_kwargs)
