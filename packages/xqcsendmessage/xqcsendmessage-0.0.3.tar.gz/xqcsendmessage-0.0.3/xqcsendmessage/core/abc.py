# 作者：Xiaoqiang
# 微信公众号：XiaoqiangClub
# 创建时间：2025-11-12T00:08:56.180Z
# 文件描述：定义发送器的抽象基类
# 文件路径：xqcsendmessage/core/abc.py

from abc import ABC, abstractmethod
from typing import Any, Dict


class Sender(ABC):
    """
    所有同步发送器的基类。
    """

    @abstractmethod
    def send(self, message: str | Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        """
        发送消息的同步方法。

        :param message: 消息内容，可以是字符串或字典。
        :param kwargs: 发送器所需的关键字参数。
        :return: 发送结果的字典。
        """
        raise NotImplementedError


class AsyncSender(ABC):
    """
    所有异步发送器的基类。
    """

    @abstractmethod
    async def send(self, message: str | Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        """
        发送消息的异步方法。

        :param message: 消息内容，可以是字符串或字典。
        :param kwargs: 发送器所需的关键字参数。
        :return: 发送结果的字典。
        """
        raise NotImplementedError
