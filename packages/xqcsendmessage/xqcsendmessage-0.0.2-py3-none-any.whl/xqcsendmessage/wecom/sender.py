# 作者：Xiaoqiang
# 微信公众号：XiaoqiangClub
# 创建时间：2025-11-12T00:09:58.674Z
# 文件描述：企业微信消息发送器
# 文件路径：xqcsendmessage/wecom/sender.py

import httpx
from typing import Any, Dict, Union

from ..core.abc import Sender, AsyncSender
from ..core.exceptions import HttpError, AuthError
from ..core.logger import default_logger


class WeComWebhookSender(Sender):
    """
    企业微信 Webhook 同步消息发送器。
    """

    def __init__(self, webhook: str):
        """
        初始化企业微信 Webhook 同步发送器。

        :param webhook: 企业微信机器人的 Webhook 地址。
        """
        self.webhook = webhook
        self.logger = default_logger

    def send(self, message: Union[str, Dict[str, Any]], **kwargs: Any) -> Dict[str, Any]:
        """
        发送企业微信 Webhook 消息。

        :param message: 消息内容，可以是字符串（将作为文本消息发送）或符合企业微信机器人支持的格式。
        :param kwargs: 其他可选参数，会合并到消息字典中。
        :return: API 响应。
        """
        if isinstance(message, str):
            message = {"msgtype": "text", "text": {"content": message}}
        message.update(kwargs) # 合并额外的关键字参数
        headers = {"Content-Type": "application/json"}
        try:
            with httpx.Client() as client:
                response = client.post(
                    self.webhook, headers=headers, json=message)
                response.raise_for_status()
                result = response.json()
                if result.get("errcode") != 0:
                    raise HttpError(f"发送企业微信消息失败: {result.get('errmsg')}")
                self.logger.info(f"🎉 企业微信 Webhook 消息发送成功: {result}")
                return result
        except httpx.HTTPStatusError as e:
            self.logger.error(f"🔥 企业微信 Webhook 消息发送失败: {e.response.text}")
            raise HttpError(
                f"发送企业微信消息失败: {e.response.text}", e.response.status_code)
        except Exception as e:
            self.logger.error(f"🔥 发送企业微信 Webhook 消息时发生未知错误: {e}")
            raise


class AsyncWeComWebhookSender(AsyncSender):
    """
    企业微信 Webhook 异步消息发送器。
    """

    def __init__(self, webhook: str):
        """
        初始化企业微信 Webhook 异步发送器。

        :param webhook: 企业微信机器人的 Webhook 地址。
        """
        self.webhook = webhook
        self.logger = default_logger

    async def send(self, message: Union[str, Dict[str, Any]], **kwargs: Any) -> Dict[str, Any]:
        """
        异步发送企业微信 Webhook 消息。

        :param message: 消息内容，可以是字符串（将作为文本消息发送）或符合企业微信机器人支持的格式。
        :param kwargs: 其他可选参数，会合并到消息字典中。
        :return: API 响应。
        """
        if isinstance(message, str):
            message = {"msgtype": "text", "text": {"content": message}}
        message.update(kwargs) # 合并额外的关键字参数
        headers = {"Content-Type": "application/json"}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.webhook, headers=headers, json=message)
                response.raise_for_status()
                result = response.json()
                if result.get("errcode") != 0:
                    raise HttpError(f"发送企业微信消息失败: {result.get('errmsg')}")
                self.logger.info(f"🎉 企业微信 Webhook 消息发送成功: {result}")
                return result
        except httpx.HTTPStatusError as e:
            self.logger.error(f"🔥 企业微信 Webhook 消息发送失败: {e.response.text}")
            raise HttpError(
                f"发送企业微信消息失败: {e.response.text}", e.response.status_code)
        except Exception as e:
            self.logger.error(f"🔥 发送企业微信 Webhook 消息时发生未知错误: {e}")
            raise


class WeComAppSender(Sender):
    """
    企业微信应用同步消息发送器。
    """

    def __init__(self, corpid: str, corpsecret: str, agentid: int):
        """
        初始化企业微信应用同步发送器。

        :param corpid: 企业 ID。
        :param corpsecret: 应用的 Secret。
        :param agentid: 应用的 AgentId。
        """
        self.corpid = corpid
        self.corpsecret = corpsecret
        self.agentid = agentid
        self.logger = default_logger
        self._access_token = None

    def _get_access_token(self) -> str:
        """
        获取 Access Token。

        :return: Access Token。
        """
        if self._access_token:
            return self._access_token

        url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={self.corpid}&corpsecret={self.corpsecret}"
        try:
            with httpx.Client() as client:
                response = client.get(url)
                response.raise_for_status()
                data = response.json()
                if "access_token" in data:
                    self._access_token = data["access_token"]
                    return self._access_token
                else:
                    raise AuthError(
                        f"获取 Access Token 失败: {data.get('errmsg')}")
        except httpx.HTTPStatusError as e:
            raise AuthError(f"获取 Access Token 请求失败: {e.response.text}")

    def send(self, message: Union[str, Dict[str, Any]], **kwargs: Any) -> Dict[str, Any]:
        """
        发送企业微信应用消息。

        :param message: 消息内容，可以是字符串（将作为文本消息发送）或符合企业微信应用消息支持的格式。
        :param kwargs: 其他可选参数，会合并到消息字典中。
        :return: API 响应。
        """
        if isinstance(message, str):
            message = {"msgtype": "text", "text": {"content": message}}
        message.update(kwargs) # 合并额外的关键字参数
        access_token = self._get_access_token()
        url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}"

        message["agentid"] = self.agentid

        headers = {"Content-Type": "application/json"}
        try:
            with httpx.Client() as client:
                response = client.post(url, headers=headers, json=message)
                response.raise_for_status()
                result = response.json()
                if result.get("errcode") != 0:
                    raise HttpError(f"发送企业微信应用消息失败: {result.get('errmsg')}")
                self.logger.info(f"🎉 企业微信应用消息发送成功: {result}")
                return result
        except httpx.HTTPStatusError as e:
            self.logger.error(f"🔥 企业微信应用消息发送失败: {e.response.text}")
            raise HttpError(
                f"发送企业微信应用消息失败: {e.response.text}", e.response.status_code)
        except Exception as e:
            self.logger.error(f"🔥 发送企业微信应用消息时发生未知错误: {e}")
            raise


class AsyncWeComAppSender(AsyncSender):
    """
    企业微信应用异步消息发送器。
    """

    def __init__(self, corpid: str, corpsecret: str, agentid: int):
        """
        初始化企业微信应用异步发送器。

        :param corpid: 企业 ID。
        :param corpsecret: 应用的 Secret。
        :param agentid: 应用的 AgentId。
        """
        self.corpid = corpid
        self.corpsecret = corpsecret
        self.agentid = agentid
        self.logger = default_logger
        self._access_token = None

    async def _get_access_token(self) -> str:
        """
        异步获取 Access Token。

        :return: Access Token。
        """
        if self._access_token:
            return self._access_token

        url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={self.corpid}&corpsecret={self.corpsecret}"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                if "access_token" in data:
                    self._access_token = data["access_token"]
                    return self._access_token
                else:
                    raise AuthError(
                        f"获取 Access Token 失败: {data.get('errmsg')}")
        except httpx.HTTPStatusError as e:
            raise AuthError(f"获取 Access Token 请求失败: {e.response.text}")

    async def send(self, message: Union[str, Dict[str, Any]], **kwargs: Any) -> Dict[str, Any]:
        """
        异步发送企业微信应用消息。

        :param message: 消息内容，可以是字符串（将作为文本消息发送）或符合企业微信应用消息支持的格式。
        :param kwargs: 其他可选参数，会合并到消息字典中。
        :return: API 响应。
        """
        if isinstance(message, str):
            message = {"msgtype": "text", "text": {"content": message}}
        message.update(kwargs) # 合并额外的关键字参数
        access_token = await self._get_access_token()
        url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}"

        message["agentid"] = self.agentid

        headers = {"Content-Type": "application/json"}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=message)
                response.raise_for_status()
                result = response.json()
                if result.get("errcode") != 0:
                    raise HttpError(f"发送企业微信应用消息失败: {result.get('errmsg')}")
                self.logger.info(f"🎉 企业微信应用消息发送成功: {result}")
                return result
        except httpx.HTTPStatusError as e:
            self.logger.error(f"🔥 企业微信应用消息发送失败: {e.response.text}")
            raise HttpError(
                f"发送企业微信应用消息失败: {e.response.text}", e.response.status_code)
        except Exception as e:
            self.logger.error(f"🔥 发送企业微信应用消息时发生未知错误: {e}")
            raise
