# 作者：Xiaoqiang
# 微信公众号：XiaoqiangClub
# 创建时间：2025-11-12T00:08:23.216Z
# 文件描述：日志模块，提供统一的日志配置
# 文件路径：xqcsendmessage/core/logger.py

import logging
import sys
from typing import TextIO


def get_logger(name: str, level: int = logging.INFO, stream: TextIO = sys.stdout) -> logging.Logger:
    """
    获取一个配置好的 Logger 实例。

    :param name: Logger 的名称。
    :param level: 日志级别。
    :param stream: 日志输出流。
    :return: 配置好的 Logger 实例。
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 避免重复添加 handler
    if not logger.handlers:
        handler = logging.StreamHandler(stream)
        formatter = logging.Formatter(
            "ℹ%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


# 预先获取一个默认的 logger
default_logger = get_logger("xqcsendmessage")
