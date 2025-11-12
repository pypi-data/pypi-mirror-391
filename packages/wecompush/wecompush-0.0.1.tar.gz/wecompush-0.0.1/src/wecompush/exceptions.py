"""
企业微信消息推送异常类

定义了包中使用的各种异常类型
"""


class WecomPushError(Exception):
    """
    企业微信消息推送基础异常类
    """
    pass


class WecomConfigError(WecomPushError):
    """
    企业微信配置错误
    
    当企业微信的配置参数不完整或无效时抛出
    """
    pass


class WecomPushMessageError(WecomPushError):
    """
    企业微信消息推送错误
    
    当发送消息失败时抛出
    """
    def __init__(self, message, errcode=None, errmsg=None):
        """
        初始化消息推送错误
        
        Args:
            message: 错误消息
            errcode: 错误代码
            errmsg: 错误描述
        """
        self.errcode = errcode
        self.errmsg = errmsg
        super().__init__(message)


class WecombotError(WecomPushMessageError):
    """
    企业微信群机器人错误
    
    当群机器人发送消息失败时抛出
    """
    pass