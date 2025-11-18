"""Response 和相关模型类"""

import json as json_module
from typing import Dict, Any, Optional, List, Iterator, Generator
from http.cookies import SimpleCookie


class Response:
    """HTTP 响应对象，模仿 httpx.Response 的接口
    
    提供与 httpx.Response 相同的接口来处理 HTTP 响应。
    
    Attributes:
        status_code: HTTP 状态码 (100-599)
        headers: 响应头字典
        content: 响应内容（字节）
        url: 最终 URL（处理重定向后）
        cookies: 响应的 Cookies 字典
        encoding: 内容编码（如 'utf-8', 'gbk' 等）
    
    Example:
        >>> response = Response(200, {}, b'Hello', 'https://example.com')
        >>> print(response.status_code)
        200
        >>> print(response.text)
        Hello
    """
    
    def __init__(
        self,
        status_code: int,
        headers: Dict[str, str],
        content: bytes,
        url: str,
        cookies: Optional[Dict[str, str]] = None,
        encoding: Optional[str] = None,
        elapsed: Optional[float] = None,
        request: Optional[Any] = None,
    ):
        """初始化响应对象
        
        Args:
            status_code: HTTP 状态码
            headers: 响应头字典
            content: 响应内容（字节）
            url: 最终 URL
            cookies: Cookies 字典（可选）
            encoding: 内容编码（可选，自动检测）
            elapsed: 请求耗时（秒）
            request: 原始请求对象引用
        """
        self.status_code = status_code
        self.headers = headers
        self._content = content
        self.url = url
        self._cookies = cookies or {}
        self._encoding = encoding
        self._text: Optional[str] = None
        self._json: Optional[Any] = None
        self.elapsed = elapsed  # 请求耗时（秒）
        self.request = request  # 原始请求对象
    
    @property
    def content(self) -> bytes:
        """获取响应内容（字节）
        
        Returns:
            原始响应内容（bytes）
        """
        return self._content
    
    @property
    def text(self) -> str:
        """获取响应内容（字符串）
        
        自动检测编码并解码响应内容。首先尝试指定的编码，
        如果失败则依次尝试 utf-8, gbk, gb2312, iso-8859-1，
        最后使用 utf-8 并忽略错误。
        
        Returns:
            解码后的字符串内容
        """
        if self._text is None:
            encoding = self.encoding or 'utf-8'
            try:
                self._text = self._content.decode(encoding)
            except UnicodeDecodeError:
                # 尝试其他编码
                for enc in ['utf-8', 'gbk', 'gb2312', 'iso-8859-1']:
                    try:
                        self._text = self._content.decode(enc)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    # 如果都失败，使用 errors='ignore'
                    self._text = self._content.decode('utf-8', errors='ignore')
        return self._text
    
    @property
    def encoding(self) -> Optional[str]:
        """获取内容编码
        
        从 Content-Type 响应头中提取编码，如果没有则默认为 utf-8。
        
        Returns:
            编码名称（如 'utf-8', 'gbk'）
        """
        if self._encoding is None:
            # 尝试从 Content-Type 头中获取
            content_type = self.headers.get('content-type', '')
            if 'charset=' in content_type.lower():
                self._encoding = content_type.lower().split('charset=')[-1].split(';')[0].strip()
            else:
                self._encoding = 'utf-8'
        return self._encoding
    
    def json(self, **kwargs: Any) -> Any:
        """解析 JSON 响应
        
        Args:
            **kwargs: 传递给 json.loads 的参数
            
        Returns:
            解析后的 JSON 对象
            
        Raises:
            json.JSONDecodeError: 如果响应不是有效的 JSON
        """
        if self._json is None:
            self._json = json_module.loads(self.text, **kwargs)
        return self._json
    
    @property
    def cookies(self) -> Dict[str, str]:
        """获取响应的 Cookies
        
        Returns:
            Cookies 字典 {name: value}
        """
        return self._cookies
    
    @property
    def ok(self) -> bool:
        """检查响应是否成功（状态码 200-299）
        
        Returns:
            True 如果状态码在 200-299 之间
        """
        return 200 <= self.status_code < 300
    
    @property
    def is_redirect(self) -> bool:
        """检查响应是否是重定向（状态码 300-399）
        
        Returns:
            True 如果状态码在 300-399 之间
        """
        return 300 <= self.status_code < 400
    
    @property
    def is_error(self) -> bool:
        """检查响应是否是错误（状态码 400+）
        
        Returns:
            True 如果状态码 >= 400
        """
        return self.status_code >= 400
    
    @property
    def is_success(self) -> bool:
        """检查响应是否成功（状态码 200-299）
        
        Returns:
            True 如果状态码在 200-299 之间
        """
        return 200 <= self.status_code < 300
    
    @property
    def is_client_error(self) -> bool:
        """检查响应是否是客户端错误（状态码 400-499）
        
        Returns:
            True 如果状态码在 400-499 之间
        """
        return 400 <= self.status_code < 500
    
    @property
    def is_server_error(self) -> bool:
        """检查响应是否是服务器错误（状态码 500-599）
        
        Returns:
            True 如果状态码在 500-599 之间
        """
        return 500 <= self.status_code < 600
    
    def raise_for_status(self) -> None:
        """如果响应是错误，抛出异常
        
        Raises:
            HTTPStatusError: 如果状态码 >= 400
        """
        if self.is_error:
            raise HTTPStatusError(
                f"HTTP {self.status_code} error for url: {self.url}",
                response=self
            )
    
    def iter_bytes(self, chunk_size: int = 1024) -> Generator[bytes, None, None]:
        """迭代响应内容的字节块
        
        Args:
            chunk_size: 每个块的大小（字节）
            
        Yields:
            bytes: 响应内容的字节块
            
        Example:
            >>> for chunk in response.iter_bytes(chunk_size=4096):
            ...     f.write(chunk)
        """
        content = self.content
        for i in range(0, len(content), chunk_size):
            yield content[i:i + chunk_size]
    
    def iter_text(self, chunk_size: int = 1024) -> Generator[str, None, None]:
        """迭代响应内容的文本块
        
        Args:
            chunk_size: 每个块的大小（字符数）
            
        Yields:
            str: 响应内容的文本块
            
        Example:
            >>> for chunk in response.iter_text():
            ...     print(chunk, end='')
        """
        text = self.text
        for i in range(0, len(text), chunk_size):
            yield text[i:i + chunk_size]
    
    def iter_lines(self) -> Generator[str, None, None]:
        """迭代响应内容的文本行
        
        Yields:
            str: 响应内容的每一行
            
        Example:
            >>> for line in response.iter_lines():
            ...     print(line)
        """
        text = self.text
        for line in text.splitlines():
            yield line
    
    def iter_raw(self, chunk_size: int = 1024) -> Generator[bytes, None, None]:
        """迭代原始响应数据（与 iter_bytes 相同）
        
        Args:
            chunk_size: 每个块的大小（字节）
            
        Yields:
            bytes: 原始响应数据块
        """
        return self.iter_bytes(chunk_size=chunk_size)
    
    def __repr__(self) -> str:
        return f"<Response [{self.status_code}]>"
    
    def __str__(self) -> str:
        return f"<Response [{self.status_code}]>"


class HTTPStatusError(Exception):
    """HTTP 状态错误异常
    
    当响应状态码 >= 400 时由 Response.raise_for_status() 抛出。
    
    Attributes:
        response: 引发异常的 Response 对象
    """
    
    def __init__(self, message: str, response: Response):
        """初始化异常
        
        Args:
            message: 错误消息
            response: 响应对象
        """
        super().__init__(message)
        self.response = response


class RequestError(Exception):
    """请求错误异常
    
    所有请求相关异常的基类。
    """
    pass


class TimeoutError(RequestError):
    """超时错误异常
    
    当请求超过指定超时时间时抛出。
    """
    pass


class ConnectError(RequestError):
    """连接错误异常
    
    当无法连接到目标服务器时抛出（如网络错误、DNS解析失败等）。
    """
    pass

