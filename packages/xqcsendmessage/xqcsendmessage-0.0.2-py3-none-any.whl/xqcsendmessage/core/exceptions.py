# 作者：Xiaoqiang
# 微信公众号：XiaoqiangClub
# 创建时间：2025-11-12T00:08:33.408Z
# 文件描述：定义模块的自定义异常
# 文件路径：xqcsendmessage/core/exceptions.py

class SendMessageError(Exception):
    """基础异常类，所有其他异常都继承自此类。"""
    pass


class HttpError(SendMessageError):
    """当 HTTP 请求失败时引发的异常。"""

    def __init__(self, message: str, status_code: int = None):
        """
        初始化 HttpError 异常。

        :param message: 错误信息。
        :param status_code: HTTP 状态码。
        """
        super().__init__(message)
        self.status_code = status_code

    def __str__(self) -> str:
        if self.status_code:
            return f"HTTP Error {self.status_code}: {super().__str__()}"
        return super().__str__()


class AuthError(SendMessageError):
    """当认证失败时引发的异常，例如 Token 无效。"""
    pass


class ValidationError(SendMessageError):
    """当输入数据验证失败时引发的异常。"""
    pass
