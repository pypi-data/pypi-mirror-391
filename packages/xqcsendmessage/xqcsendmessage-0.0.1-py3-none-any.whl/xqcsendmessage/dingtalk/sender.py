# 作者：Xiaoqiang
# 微信公众号：XiaoqiangClub
# 创建时间：2025-11-12T00:09:23.823Z
# 文件描述：钉钉消息发送器
# 文件路径：xqcsendmessage/dingtalk/sender.py

import hmac
import hashlib
import base64
import time
import httpx
from typing import Any, Dict, Optional, Union

from ..core.abc import Sender, AsyncSender
from ..core.exceptions import HttpError
from ..core.logger import default_logger


class DingTalkSender(Sender):
    """
    钉钉同步消息发送器。
    """

    def __init__(self, webhook: str, secret: Optional[str] = None):
        """
        初始化钉钉同步发送器。

        :param webhook: 钉钉机器人的 Webhook 地址。
        :param secret: 钉钉机器人的密钥，用于签名。
        """
        self.webhook = webhook
        self.secret = secret
        self.logger = default_logger

    def _sign(self) -> Dict[str, str]:
        """
        生成钉钉 API 所需的签名。

        :return: 包含签名和时间戳的字典。
        """
        if not self.secret:
            return {}

        timestamp = str(round(time.time() * 1000))
        secret_enc = self.secret.encode("utf-8")
        string_to_sign = f"{timestamp}\n{self.secret}"
        string_to_sign_enc = string_to_sign.encode("utf-8")

        hmac_code = hmac.new(
            secret_enc, string_to_sign_enc, digestmod=hashlib.sha256
        ).digest()

        sign = base64.b64encode(hmac_code).decode("utf-8")

        return {"timestamp": timestamp, "sign": sign}

    def send(self, message: Union[str, Dict[str, Any]], **kwargs: Any) -> Dict[str, Any]:
        """
        发送钉钉消息。

        :param message: 消息内容，可以是字符串（将作为文本消息发送）或符合钉钉机器人格式的字典。
        :param kwargs: 其他可选参数，例如 at_mobiles 等，会合并到消息字典中。
        :return: 钉钉 API 的响应。
        """
        if isinstance(message, str):
            message = {"msgtype": "text", "text": {"content": message}}
        message.update(kwargs)  # 合并额外的关键字参数
        headers = {"Content-Type": "application/json"}

        # 解析 webhook URL，获取基础 URL 和已有的查询参数
        from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

        parsed_url = urlparse(self.webhook)
        query_params = parse_qs(parsed_url.query)

        # 将签名参数添加到查询参数中
        signed_params = self._sign()
        for k, v in signed_params.items():
            query_params[k] = [v]  # parse_qs 返回列表，所以这里也用列表

        # 重新构建查询字符串
        new_query_string = urlencode({k: v[0] if isinstance(
            v, list) else v for k, v in query_params.items()})

        # 重新构建 URL
        final_url = urlunparse(parsed_url._replace(query=new_query_string))

        try:
            with httpx.Client() as client:
                response = client.post(
                    final_url, headers=headers, json=message
                )
                response.raise_for_status()
                result = response.json()
                self.logger.info(f"🎉 钉钉消息发送成功: {result}")
                return result
        except httpx.HTTPStatusError as e:
            self.logger.error(f"🔥 钉钉消息发送失败: {e.response.text}")
            raise HttpError(
                f"发送钉钉消息失败: {e.response.text}", e.response.status_code)
        except Exception as e:
            self.logger.error(f"🔥 发送钉钉消息时发生未知错误: {e}")
            raise


class AsyncDingTalkSender(AsyncSender):
    """
    钉钉异步消息发送器。
    """

    def __init__(self, webhook: str, secret: Optional[str] = None):
        """
        初始化钉钉异步发送器。

        :param webhook: 钉钉机器人的 Webhook 地址。
        :param secret: 钉钉机器人的密钥，用于签名。
        """
        self.webhook = webhook
        self.secret = secret
        self.logger = default_logger

    def _sign(self) -> Dict[str, str]:
        """
        生成钉钉 API 所需的签名。

        :return: 包含签名和时间戳的字典。
        """
        if not self.secret:
            return {}

        timestamp = str(round(time.time() * 1000))
        secret_enc = self.secret.encode("utf-8")
        string_to_sign = f"{timestamp}\n{self.secret}"
        string_to_sign_enc = string_to_sign.encode("utf-8")

        hmac_code = hmac.new(
            secret_enc, string_to_sign_enc, digestmod=hashlib.sha256
        ).digest()

        sign = base64.b64encode(hmac_code).decode("utf-8")

        return {"timestamp": timestamp, "sign": sign}

    async def send(self, message: Union[str, Dict[str, Any]], **kwargs: Any) -> Dict[str, Any]:
        """
        异步发送钉钉消息。

        :param message: 消息内容，可以是字符串（将作为文本消息发送）或符合钉钉机器人格式的字典。
        :param kwargs: 其他可选参数，例如 at_mobiles 等，会合并到消息字典中。
        :return: 钉钉 API 的响应。
        """
        if isinstance(message, str):
            message = {"msgtype": "text", "text": {"content": message}}
        message.update(kwargs)  # 合并额外的关键字参数
        headers = {"Content-Type": "application/json"}

        # 解析 webhook URL，获取基础 URL 和已有的查询参数
        from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

        parsed_url = urlparse(self.webhook)
        query_params = parse_qs(parsed_url.query)

        # 将签名参数添加到查询参数中
        signed_params = self._sign()
        for k, v in signed_params.items():
            query_params[k] = [v]

        # 重新构建查询字符串
        new_query_string = urlencode({k: v[0] if isinstance(
            v, list) else v for k, v in query_params.items()})

        # 重新构建 URL
        final_url = urlunparse(parsed_url._replace(query=new_query_string))

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    final_url, headers=headers, json=message
                )
                response.raise_for_status()
                result = response.json()
                self.logger.info(f"🎉 钉钉消息发送成功: {result}")
                return result
        except httpx.HTTPStatusError as e:
            self.logger.error(f"🔥 钉钉消息发送失败: {e.response.text}")
            raise HttpError(
                f"发送钉钉消息失败: {e.response.text}", e.response.status_code)
        except Exception as e:
            self.logger.error(f"🔥 发送钉钉消息时发生未知错误: {e}")
            raise
