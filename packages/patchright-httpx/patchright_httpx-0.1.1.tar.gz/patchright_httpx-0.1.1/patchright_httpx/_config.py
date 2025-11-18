"""配置类定义"""

from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class Timeout:
    """超时配置
    
    Attributes:
        connect: 连接超时（秒）
        read: 读取超时（秒）
        write: 写入超时（秒）
        total: 总超时（秒）
    """
    connect: Optional[float] = None
    read: Optional[float] = None
    write: Optional[float] = None
    total: Optional[float] = 30.0
    
    @classmethod
    def from_value(cls, value: float) -> "Timeout":
        """从单个超时值创建 Timeout 对象"""
        return cls(total=value)
    
    def to_playwright_timeout(self) -> float:
        """转换为 Playwright 的超时格式（毫秒）"""
        if self.total is not None:
            return self.total * 1000
        return 30000  # 默认 30 秒


@dataclass
class Proxy:
    """代理配置
    
    Attributes:
        server: 代理服务器地址（如 'http://proxy.example.com:8080'）
        username: 代理用户名
        password: 代理密码
        bypass: 不使用代理的域名列表
    """
    server: str
    username: Optional[str] = None
    password: Optional[str] = None
    bypass: Optional[str] = None
    
    def to_playwright_proxy(self) -> Dict[str, Any]:
        """转换为 Playwright 的代理格式"""
        proxy_dict = {"server": self.server}
        if self.username:
            proxy_dict["username"] = self.username
        if self.password:
            proxy_dict["password"] = self.password
        if self.bypass:
            proxy_dict["bypass"] = self.bypass
        return proxy_dict


@dataclass
class Limits:
    """并发限制配置
    
    Attributes:
        max_connections: 最大连接数
        max_keepalive_connections: 最大保持连接数
    """
    max_connections: int = 100
    max_keepalive_connections: int = 20


