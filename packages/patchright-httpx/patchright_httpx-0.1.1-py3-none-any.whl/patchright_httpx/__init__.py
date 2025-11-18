"""
Patchright HTTPX - 使用 Patchright 封装的类 HTTPX 库

提供与 httpx 相似的 API，但使用真实浏览器（Patchright）来发送请求，
可以轻松绕过反爬虫检测，同时保持简洁易用的接口。

Example:
    >>> import patchright_httpx as httpx
    >>> response = httpx.get('https://example.com')
    >>> print(response.status_code)
    200
"""

from typing import Any, Dict, Optional, Union

from ._client import Client
from ._async_client import AsyncClient
from ._models import Response, HTTPStatusError, RequestError, TimeoutError, ConnectError
from ._config import Timeout, Proxy
from ._tools import CookieJar, RequestHistory, RetryPolicy, RateLimiter, RequestCache, SessionStorage

__version__ = "0.4.0"
__all__ = [
    "Client",
    "AsyncClient",
    "Response",
    "Timeout",
    "Proxy",
    "HTTPStatusError",
    "RequestError",
    "TimeoutError",
    "ConnectError",
    "CookieJar",
    "RequestHistory",
    "RetryPolicy",
    "RateLimiter",
    "RequestCache",
    "SessionStorage",
    "get",
    "post",
    "put",
    "delete",
    "patch",
    "head",
    "options",
]


def get(
    url: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    cookies: Optional[Dict[str, str]] = None,
    timeout: Optional[Union[float, Timeout]] = None,
    follow_redirects: bool = True,
    auth: Optional[tuple] = None,
    **kwargs: Any,
) -> Response:
    """发送 GET 请求
    
    Args:
        url: 请求的 URL
        params: URL 查询参数
        headers: 自定义请求头
        cookies: Cookies
        timeout: 超时设置（秒）
        follow_redirects: 是否跟随重定向
        auth: 基本认证（用户名，密码）
        **kwargs: 其他参数传递给 Client
        
    Returns:
        Response 对象
    """
    with Client(**kwargs) as client:
        return client.get(
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            follow_redirects=follow_redirects,
        )


def post(
    url: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    json: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    cookies: Optional[Dict[str, str]] = None,
    timeout: Optional[Union[float, Timeout]] = None,
    follow_redirects: bool = True,
    **kwargs: Any,
) -> Response:
    """发送 POST 请求
    
    Args:
        url: 请求的 URL
        params: URL 查询参数
        data: 表单数据
        json: JSON 数据
        headers: 自定义请求头
        cookies: Cookies
        timeout: 超时设置（秒）
        follow_redirects: 是否跟随重定向
        **kwargs: 其他参数传递给 Client
        
    Returns:
        Response 对象
    """
    with Client(**kwargs) as client:
        return client.post(
            url,
            params=params,
            data=data,
            json=json,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            follow_redirects=follow_redirects,
        )


def put(
    url: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    json: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    cookies: Optional[Dict[str, str]] = None,
    timeout: Optional[Union[float, Timeout]] = None,
    follow_redirects: bool = True,
    **kwargs: Any,
) -> Response:
    """发送 PUT 请求"""
    with Client(**kwargs) as client:
        return client.put(
            url,
            params=params,
            data=data,
            json=json,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            follow_redirects=follow_redirects,
        )


def delete(
    url: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    cookies: Optional[Dict[str, str]] = None,
    timeout: Optional[Union[float, Timeout]] = None,
    follow_redirects: bool = True,
    auth: Optional[tuple] = None,
    **kwargs: Any,
) -> Response:
    """发送 DELETE 请求"""
    with Client(**kwargs) as client:
        return client.delete(
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            follow_redirects=follow_redirects,
            auth=auth,
        )


def patch(
    url: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    json: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    cookies: Optional[Dict[str, str]] = None,
    timeout: Optional[Union[float, Timeout]] = None,
    follow_redirects: bool = True,
    **kwargs: Any,
) -> Response:
    """发送 PATCH 请求"""
    with Client(**kwargs) as client:
        return client.patch(
            url,
            params=params,
            data=data,
            json=json,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            follow_redirects=follow_redirects,
        )


def head(
    url: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    cookies: Optional[Dict[str, str]] = None,
    timeout: Optional[Union[float, Timeout]] = None,
    follow_redirects: bool = True,
    auth: Optional[tuple] = None,
    **kwargs: Any,
) -> Response:
    """发送 HEAD 请求"""
    with Client(**kwargs) as client:
        return client.head(
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            follow_redirects=follow_redirects,
        )


def options(
    url: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    cookies: Optional[Dict[str, str]] = None,
    timeout: Optional[Union[float, Timeout]] = None,
    follow_redirects: bool = True,
    auth: Optional[tuple] = None,
    **kwargs: Any,
) -> Response:
    """发送 OPTIONS 请求"""
    with Client(**kwargs) as client:
        return client.options(
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            follow_redirects=follow_redirects,
        )

