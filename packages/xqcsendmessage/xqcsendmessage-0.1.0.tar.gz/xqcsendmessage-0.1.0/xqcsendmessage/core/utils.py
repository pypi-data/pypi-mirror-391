# 作者：Xiaoqiang
# 微信公众号：XiaoqiangClub
# 创建时间：2025-11-13T04:51:40.349Z
# 文件描述：提供核心工具函数，如文件读取。
# 文件路径：xqcsendmessage/core/utils.py

import aiofiles
from typing import Optional

from .exceptions import SendMessageError

def read_file(file_path: str, encoding: str = "utf-8") -> str:
    """
    同步读取文件内容。

    :param file_path: 文件路径。
    :param encoding: 文件编码，默认为 'utf-8'。
    :return: 文件内容字符串。
    """
    try:
        with open(file_path, "r", encoding=encoding) as f:
            return f.read()
    except FileNotFoundError:
        raise SendMessageError(f"❌ 文件未找到: {file_path}")
    except Exception as e:
        raise SendMessageError(f"❌ 读取文件时发生错误: {e}")

async def read_file_async(file_path: str, encoding: str = "utf-8") -> str:
    """
    异步读取文件内容。

    :param file_path: 文件路径。
    :param encoding: 文件编码，默认为 'utf-8'。
    :return: 文件内容字符串。
    """
    try:
        async with aiofiles.open(file_path, "r", encoding=encoding) as f:
            return await f.read()
    except FileNotFoundError:
        raise SendMessageError(f"❌ 文件未找到: {file_path}")
    except Exception as e:
        raise SendMessageError(f"❌ 读取文件时发生错误: {e}")