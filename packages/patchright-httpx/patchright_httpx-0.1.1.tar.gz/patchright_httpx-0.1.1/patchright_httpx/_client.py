"""同步客户端实现"""

import json as json_module
import time
from typing import Any, Dict, Optional, Union, Tuple, Callable, Iterator
from urllib.parse import urlencode

from patchright.sync_api import sync_playwright, Browser, BrowserContext, Page, Playwright

from ._models import Response, RequestError, TimeoutError, ConnectError
from ._config import Timeout, Proxy
from ._types import Headers, Cookies, Params, Data, JsonData, Auth, BrowserType, Files
from ._utils import build_url, merge_headers, format_auth_header, merge_url, build_multipart_data
from ._websocket import WebSocketConnection
from ._tools import CookieJar, RequestHistory, RetryPolicy, RateLimiter, RequestCache


class Client:
    """同步 HTTP 客户端，使用 Patchright 浏览器发送请求
    
    提供类似 httpx.Client 的接口，支持持久化浏览器实例以提高性能。
    
    Args:
        headless: 是否使用无头模式（默认 True）
        browser_type: 浏览器类型 ('chromium', 'firefox', 'webkit')，默认 'chromium'
        proxy: 代理配置
        timeout: 默认超时设置
        headers: 默认请求头
        cookies: 默认 Cookies
        follow_redirects: 是否跟随重定向（默认 True）
        user_agent: 自定义 User-Agent
        viewport: 视口大小，如 {'width': 1920, 'height': 1080}
        launch_options: 额外的浏览器启动参数（传递给 browser.launch()）
        context_options: 额外的上下文参数（传递给 browser.new_context()）
    
    Example:
        >>> with Client() as client:
        ...     response = client.get('https://example.com')
        ...     print(response.status_code)
        
        >>> # 高级配置
        >>> with Client(
        ...     launch_options={'args': ['--disable-blink-features=AutomationControlled']},
        ...     context_options={'locale': 'zh-CN'}
        ... ) as client:
        ...     response = client.get('https://example.com')
    """
    
    def __init__(
        self,
        *,
        headless: bool = True,
        browser_type: BrowserType = "chromium",
        proxy: Optional[Proxy] = None,
        timeout: Optional[Union[float, Timeout]] = None,
        headers: Optional[Headers] = None,
        cookies: Optional[Cookies] = None,
        follow_redirects: bool = True,
        user_agent: Optional[str] = None,
        viewport: Optional[Dict[str, int]] = None,
        launch_options: Optional[Dict[str, Any]] = None,
        context_options: Optional[Dict[str, Any]] = None,
        # httpx 兼容参数
        base_url: Optional[str] = None,
        params: Optional[Params] = None,
        max_redirects: int = 20,
        event_hooks: Optional[Dict[str, list]] = None,
        # 高级参数
        retry_policy: Optional[RetryPolicy] = None,
        rate_limiter: Optional[RateLimiter] = None,
        enable_cache: bool = False,
        cache_ttl: int = 300,
        enable_history: bool = False,
        history_size: int = 100,
    ):
        self.headless = headless
        self.browser_type = browser_type
        self.proxy = proxy
        self.default_headers = headers or {}
        self.default_cookies = cookies or {}
        self.follow_redirects = follow_redirects
        self.user_agent = user_agent
        self.viewport = viewport or {"width": 1920, "height": 1080}
        self.launch_options = launch_options or {}
        self.context_options = context_options or {}
        
        # httpx 兼容功能
        self.base_url = base_url.rstrip('/') if base_url else None
        self.default_params = params or {}
        self.max_redirects = max_redirects
        self.event_hooks = event_hooks or {}
        
        # 高级功能
        self.retry_policy = retry_policy
        self.rate_limiter = rate_limiter
        self.cache = RequestCache(ttl=cache_ttl) if enable_cache else None
        self.history = RequestHistory(max_size=history_size) if enable_history else None
        
        # 处理超时设置
        if isinstance(timeout, (int, float)):
            self.timeout = Timeout.from_value(timeout)
        elif isinstance(timeout, Timeout):
            self.timeout = timeout
        else:
            self.timeout = Timeout()
        
        # Playwright 相关对象
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._is_closed = False
    
    def __enter__(self) -> "Client":
        """上下文管理器入口"""
        self._ensure_browser()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """上下文管理器退出"""
        self.close()
    
    def _ensure_browser(self) -> None:
        """确保浏览器已启动"""
        if self._playwright is None:
            self._playwright = sync_playwright().start()
            
            # 选择浏览器类型
            if self.browser_type == "firefox":
                browser_launcher = self._playwright.firefox
            elif self.browser_type == "webkit":
                browser_launcher = self._playwright.webkit
            else:
                browser_launcher = self._playwright.chromium
            
            # 启动浏览器
            final_launch_options: Dict[str, Any] = {
                "headless": self.headless,
                **self.launch_options,  # 用户自定义选项
            }
            
            if self.proxy:
                final_launch_options["proxy"] = self.proxy.to_playwright_proxy()
            
            self._browser = browser_launcher.launch(**final_launch_options)
            
            # 创建上下文
            final_context_options: Dict[str, Any] = {
                "viewport": self.viewport,
                **self.context_options,  # 用户自定义选项
            }
            
            if self.user_agent:
                final_context_options["user_agent"] = self.user_agent
            
            self._context = self._browser.new_context(**final_context_options)
            
            # 设置默认 cookies
            if self.default_cookies:
                cookies_list = [
                    {"name": name, "value": value, "url": "https://example.com"}
                    for name, value in self.default_cookies.items()
                ]
                self._context.add_cookies(cookies_list)
    
    def close(self) -> None:
        """关闭浏览器和清理资源
        
        确保所有资源(context, browser, playwright)都被正确释放,
        即使某个关闭操作失败也会继续关闭其他资源。
        """
        if not self._is_closed:
            # 分别尝试关闭,确保即使某个失败也能继续
            if self._context:
                try:
                    self._context.close()
                except Exception:
                    pass  # 忽略错误,继续关闭其他资源
                finally:
                    self._context = None
            
            if self._browser:
                try:
                    self._browser.close()
                except Exception:
                    pass
                finally:
                    self._browser = None
            
            if self._playwright:
                try:
                    self._playwright.stop()
                except Exception:
                    pass
                finally:
                    self._playwright = None
            
            self._is_closed = True
    
    def request(
        self,
        method: str,
        url: str,
        *,
        params: Optional[Params] = None,
        data: Optional[Data] = None,
        files: Optional[Files] = None,
        json: Optional[JsonData] = None,
        headers: Optional[Headers] = None,
        cookies: Optional[Cookies] = None,
        timeout: Optional[Union[float, Timeout]] = None,
        follow_redirects: Optional[bool] = None,
        auth: Optional[Auth] = None,
    ) -> Response:
        """发送 HTTP 请求
        
        Args:
            method: HTTP 方法（GET, POST, PUT, DELETE 等）
            url: 请求的 URL（可以是相对路径，会与 base_url 合并）
            params: URL 查询参数
            data: 表单数据
            files: 文件上传，格式:
                - {'field': 'path/to/file'}  # 文件路径
                - {'field': ('filename', b'content')}  # 文件名和内容
                - {'field': ('filename', b'content', 'content-type')}  # 完整格式
            json: JSON 数据
            headers: 自定义请求头
            cookies: Cookies
            timeout: 超时设置
            follow_redirects: 是否跟随重定向
            auth: 基本认证（用户名，密码）
            
        Returns:
            Response 对象
        """
        self._ensure_browser()
        
        # 合并 base_url 和 url
        url = merge_url(self.base_url, url)
        
        # 合并默认参数和请求参数
        merged_params = {**self.default_params, **(params or {})}
        
        # 构建完整 URL
        full_url = build_url(url, merged_params)
        
        # 合并请求头
        merged_headers = merge_headers(self.default_headers, headers)
        
        # 处理认证
        if auth:
            merged_headers["Authorization"] = format_auth_header(auth[0], auth[1])
        
        # 处理请求体
        if files:
            # 文件上传 - 构造 multipart/form-data
            body_data, content_type = build_multipart_data(data=data, files=files)
            merged_headers["Content-Type"] = content_type
        elif json is not None:
            merged_headers["Content-Type"] = "application/json"
            body_data = json_module.dumps(json)
        elif data is not None:
            merged_headers["Content-Type"] = "application/x-www-form-urlencoded"
            body_data = urlencode(data)
        else:
            body_data = None
        
        # 处理超时
        if isinstance(timeout, (int, float)):
            timeout_obj = Timeout.from_value(timeout)
        elif isinstance(timeout, Timeout):
            timeout_obj = timeout
        else:
            timeout_obj = self.timeout
        
        timeout_ms = timeout_obj.to_playwright_timeout()
        
        # 记录开始时间（用于历史统计）
        start_time = time.time()
        
        # 构建请求信息（用于钩子和 response.request）
        request_info = {
            'method': method.upper(),
            'url': full_url,
            'headers': merged_headers,
        }
        
        # 调用 request 钩子
        if 'request' in self.event_hooks:
            for hook in self.event_hooks['request']:
                hook(request_info)
        
        # 创建新页面
        page = self._context.new_page()
        
        try:
            # 设置额外的请求头和 cookies
            if merged_headers or cookies:
                page.set_extra_http_headers(merged_headers)
            
            if cookies:
                cookies_list = [
                    {"name": name, "value": value, "url": full_url}
                    for name, value in cookies.items()
                ]
                self._context.add_cookies(cookies_list)
            
            # 发送请求
            if method.upper() in ["POST", "PUT", "PATCH"] and body_data:
                # 对于需要 body 的请求，使用 route 拦截
                response = self._request_with_body(
                    page, method, full_url, body_data, timeout_ms
                )
            else:
                # GET, DELETE, HEAD, OPTIONS 等
                response = page.goto(
                    full_url,
                    wait_until="networkidle",
                    timeout=timeout_ms,
                )
            
            if response is None:
                raise RequestError(f"Failed to load page: {full_url}")
            
            # 提取响应数据
            status_code = response.status
            response_headers = response.headers
            final_url = page.url
            
            # 获取响应内容（原始响应体，而不是渲染后的 HTML）
            try:
                content = response.body()
            except Exception:
                # 如果无法获取原始响应体，回退到页面内容
                content = page.content().encode('utf-8')
            
            # 获取 cookies
            response_cookies = {
                cookie['name']: cookie['value']
                for cookie in self._context.cookies()
            }
            
            # 计算请求耗时
            elapsed_time = time.time() - start_time
            
            # 创建响应对象
            response_obj = Response(
                status_code=status_code,
                headers=response_headers,
                content=content,
                url=final_url,
                cookies=response_cookies,
                elapsed=elapsed_time,
                request=request_info,
            )
            
            # 调用 response 钩子
            if 'response' in self.event_hooks:
                for hook in self.event_hooks['response']:
                    hook(response_obj)
            
            # 记录到历史（如果启用）
            if self.history:
                duration = time.time() - start_time
                self.history.add(method.upper(), full_url, status_code, duration)
            
            return response_obj
            
        except Exception as e:
            # 记录失败的请求到历史（如果启用）
            if self.history:
                duration = time.time() - start_time
                # 失败请求用状态码 0 表示
                self.history.add(method.upper(), full_url, 0, duration)
            
            if "timeout" in str(e).lower():
                raise TimeoutError(f"Request timeout: {full_url}") from e
            elif "net::" in str(e).lower():
                raise ConnectError(f"Connection error: {full_url}") from e
            else:
                raise RequestError(f"Request failed: {str(e)}") from e
        finally:
            page.close()
    
    def _request_with_body(
        self, page: Page, method: str, url: str, body: str, timeout: float
    ) -> Any:
        """发送带 body 的请求"""
        # 使用 route 拦截请求并修改方法和 body
        def handle_route(route):
            route.continue_(method=method, post_data=body)
        
        page.route(url, handle_route)
        response = page.goto(url, wait_until="networkidle", timeout=timeout)
        page.unroute(url)
        return response
    
    def get(
        self,
        url: str,
        *,
        params: Optional[Params] = None,
        headers: Optional[Headers] = None,
        cookies: Optional[Cookies] = None,
        timeout: Optional[Union[float, Timeout]] = None,
        follow_redirects: Optional[bool] = None,
        auth: Optional[Auth] = None,
    ) -> Response:
        """发送 GET 请求"""
        return self.request(
            "GET",
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            follow_redirects=follow_redirects,
            auth=auth,
        )
    
    def post(
        self,
        url: str,
        *,
        params: Optional[Params] = None,
        data: Optional[Data] = None,
        files: Optional[Files] = None,
        json: Optional[JsonData] = None,
        headers: Optional[Headers] = None,
        cookies: Optional[Cookies] = None,
        timeout: Optional[Union[float, Timeout]] = None,
        follow_redirects: Optional[bool] = None,
        auth: Optional[Auth] = None,
    ) -> Response:
        """发送 POST 请求"""
        return self.request(
            "POST",
            url,
            params=params,
            data=data,
            files=files,
            json=json,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            follow_redirects=follow_redirects,
            auth=auth,
        )
    
    def put(
        self,
        url: str,
        *,
        params: Optional[Params] = None,
        data: Optional[Data] = None,
        files: Optional[Files] = None,
        json: Optional[JsonData] = None,
        headers: Optional[Headers] = None,
        cookies: Optional[Cookies] = None,
        timeout: Optional[Union[float, Timeout]] = None,
        follow_redirects: Optional[bool] = None,
        auth: Optional[Auth] = None,
    ) -> Response:
        """发送 PUT 请求"""
        return self.request(
            "PUT",
            url,
            params=params,
            data=data,
            files=files,
            json=json,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            follow_redirects=follow_redirects,
            auth=auth,
        )
    
    def delete(
        self,
        url: str,
        *,
        params: Optional[Params] = None,
        headers: Optional[Headers] = None,
        cookies: Optional[Cookies] = None,
        timeout: Optional[Union[float, Timeout]] = None,
        follow_redirects: Optional[bool] = None,
        auth: Optional[Auth] = None,
    ) -> Response:
        """发送 DELETE 请求"""
        return self.request(
            "DELETE",
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            follow_redirects=follow_redirects,
            auth=auth,
        )
    
    def patch(
        self,
        url: str,
        *,
        params: Optional[Params] = None,
        data: Optional[Data] = None,
        files: Optional[Files] = None,
        json: Optional[JsonData] = None,
        headers: Optional[Headers] = None,
        cookies: Optional[Cookies] = None,
        timeout: Optional[Union[float, Timeout]] = None,
        follow_redirects: Optional[bool] = None,
        auth: Optional[Auth] = None,
    ) -> Response:
        """发送 PATCH 请求"""
        return self.request(
            "PATCH",
            url,
            params=params,
            data=data,
            files=files,
            json=json,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            follow_redirects=follow_redirects,
            auth=auth,
        )
    
    def head(
        self,
        url: str,
        *,
        params: Optional[Params] = None,
        headers: Optional[Headers] = None,
        cookies: Optional[Cookies] = None,
        timeout: Optional[Union[float, Timeout]] = None,
        follow_redirects: Optional[bool] = None,
        auth: Optional[Auth] = None,
    ) -> Response:
        """发送 HEAD 请求"""
        return self.request(
            "HEAD",
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            follow_redirects=follow_redirects,
            auth=auth,
        )
    
    def options(
        self,
        url: str,
        *,
        params: Optional[Params] = None,
        headers: Optional[Headers] = None,
        cookies: Optional[Cookies] = None,
        timeout: Optional[Union[float, Timeout]] = None,
        follow_redirects: Optional[bool] = None,
        auth: Optional[Auth] = None,
    ) -> Response:
        """发送 OPTIONS 请求"""
        return self.request(
            "OPTIONS",
            url,
            params=params,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            follow_redirects=follow_redirects,
            auth=auth,
        )
    
    def execute_script(self, script: str, url: Optional[str] = None) -> Any:
        """在页面中执行 JavaScript 代码
        
        Args:
            script: JavaScript 代码
            url: 可选的页面 URL，如果提供则先访问该页面
            
        Returns:
            JavaScript 执行结果
            
        Example:
            >>> with Client() as client:
            ...     result = client.execute_script(
            ...         "return document.title",
            ...         url="https://example.com"
            ...     )
            ...     print(result)
        """
        self._ensure_browser()
        page = self._context.new_page()
        
        try:
            if url:
                page.goto(url, wait_until="networkidle")
            
            result = page.evaluate(script)
            return result
        finally:
            page.close()
    
    def get_page(self):
        """获取一个新的 Page 对象，用于更复杂的浏览器操作
        
        Returns:
            Playwright Page 对象
            
        Example:
            >>> with Client() as client:
            ...     page = client.get_page()
            ...     page.goto('https://example.com')
            ...     page.screenshot(path='screenshot.png')
            ...     page.close()
        """
        self._ensure_browser()
        return self._context.new_page()
    
    def screenshot(
        self, 
        url: str, 
        path: Optional[str] = None,
        full_page: bool = False,
        viewport: Optional[Dict[str, int]] = None,
    ) -> bytes:
        """对页面进行截图
        
        Args:
            url: 页面 URL
            path: 保存截图的路径（可选）
            full_page: 是否截取整个页面（默认 False）
            viewport: 视口大小,如 {'width': 1920, 'height': 1080}（可选）
            
        Returns:
            截图的字节数据
            
        Example:
            >>> with Client() as client:
            ...     # 默认viewport
            ...     screenshot = client.screenshot('https://example.com')
            ...     
            ...     # 自定义viewport
            ...     screenshot = client.screenshot(
            ...         'https://example.com',
            ...         viewport={'width': 375, 'height': 667}
            ...     )
        """
        self._ensure_browser()
        
        # 如果指定了viewport,创建一个新的临时context
        if viewport:
            temp_context = self._browser.new_context(viewport=viewport)
            page = temp_context.new_page()
            try:
                page.goto(url, wait_until="networkidle")
                screenshot_bytes = page.screenshot(path=path, full_page=full_page)
                return screenshot_bytes
            finally:
                page.close()
                temp_context.close()
        else:
            # 使用默认context
            page = self._context.new_page()
            try:
                page.goto(url, wait_until="networkidle")
                screenshot_bytes = page.screenshot(path=path, full_page=full_page)
                return screenshot_bytes
            finally:
                page.close()
    
    def websocket_connect(
        self,
        url: str,
        *,
        on_message: Optional[Callable[[str], None]] = None,
        on_close: Optional[Callable[[], None]] = None,
        headers: Optional[Headers] = None,
        timeout: float = 10.0,
    ) -> WebSocketConnection:
        """连接 WebSocket
        
        Args:
            url: WebSocket URL
            on_message: 消息接收回调函数
            on_close: 连接关闭回调函数
            headers: 额外的请求头
            timeout: 连接超时(秒),默认10秒
            
        Returns:
            WebSocketConnection 对象
            
        Example:
            >>> with Client() as client:
            ...     ws = client.websocket_connect('wss://echo.websocket.org')
            ...     ws.send_text('Hello WebSocket!')
            ...     response = ws.receive_text()
            ...     print(response)
            ...     ws.close()
        """
        self._ensure_browser()
        page = self._context.new_page()
        
        # 创建WebSocket连接(自动等待ready)
        ws_conn = WebSocketConnection(page, url, timeout=timeout)
        
        # 注册用户回调
        if on_message:
            ws_conn.on_message(on_message)
        if on_close:
            ws_conn.on_close(on_close)
        
        return ws_conn
    
    def stream(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> Iterator[bytes]:
        """流式请求（通过监听网络响应实现）
        
        Args:
            method: HTTP 方法
            url: 请求 URL
            **kwargs: 其他请求参数
            
        Yields:
            响应数据块
            
        Example:
            >>> with Client() as client:
            ...     for chunk in client.stream('GET', 'https://example.com/large-file'):
            ...         process(chunk)
        """
        self._ensure_browser()
        page = self._context.new_page()
        
        chunks = []
        
        def handle_response(response):
            if response.url == url:
                try:
                    body = response.body()
                    chunks.append(body)
                except:
                    pass
        
        page.on("response", handle_response)
        
        try:
            # 构建完整 URL
            full_url = build_url(url, kwargs.get('params'))
            
            # 发送请求
            page.goto(full_url, wait_until="load")
            page.wait_for_timeout(1000)
            
            # 返回数据块
            for chunk in chunks:
                # 将大数据分块
                chunk_size = 8192
                for i in range(0, len(chunk), chunk_size):
                    yield chunk[i:i+chunk_size]
        finally:
            page.close()
    
    def on_request(self, callback: Callable[[Any], None]) -> None:
        """设置请求钩子
        
        Args:
            callback: 请求回调函数
            
        Example:
            >>> def log_request(request):
            ...     print(f"Request: {request.method} {request.url}")
            >>> 
            >>> client.on_request(log_request)
        """
        self._ensure_browser()
        self._context.on("request", callback)
    
    def on_response(self, callback: Callable[[Any], None]) -> None:
        """设置响应钩子
        
        Args:
            callback: 响应回调函数
            
        Example:
            >>> def log_response(response):
            ...     print(f"Response: {response.status} {response.url}")
            >>> 
            >>> client.on_response(log_response)
        """
        self._ensure_browser()
        self._context.on("response", callback)
    
    def save_cookies(self, filepath: str = "cookies.json") -> None:
        """保存当前 cookies 到文件
        
        Args:
            filepath: 保存路径
            
        Example:
            >>> with Client() as client:
            ...     client.get('https://example.com')
            ...     client.save_cookies('my_cookies.json')
        """
        self._ensure_browser()
        cookies = self._context.cookies()
        jar = CookieJar(filepath)
        jar.save(cookies)
    
    def load_cookies(self, filepath: str = "cookies.json") -> None:
        """从文件加载 cookies
        
        Args:
            filepath: 文件路径
            
        Example:
            >>> with Client() as client:
            ...     client.load_cookies('my_cookies.json')
            ...     client.get('https://example.com')  # 自动携带 cookies
        """
        self._ensure_browser()
        jar = CookieJar(filepath)
        cookies = jar.load()
        if cookies:
            self._context.add_cookies(cookies)
    
    def get_history(self) -> Optional[Dict[str, Any]]:
        """获取请求历史统计
        
        Returns:
            历史统计信息，如果未启用则返回 None
            
        Example:
            >>> client = Client(enable_history=True)
            >>> with client:
            ...     client.get('https://example.com')
            ...     stats = client.get_history()
            ...     print(f"总请求数: {stats['total_requests']}")
        """
        if self.history:
            return self.history.get_stats()
        return None
    
    def clear_cache(self) -> None:
        """清除请求缓存
        
        Example:
            >>> client = Client(enable_cache=True)
            >>> with client:
            ...     client.clear_cache()
        """
        if self.cache:
            self.cache.clear()
    
    def emulate_device(self, device_name: str) -> None:
        """模拟移动设备
        
        Args:
            device_name: 设备名称（如 'iPhone 12', 'Pixel 5' 等）
            
        Example:
            >>> with Client() as client:
            ...     client.emulate_device('iPhone 12')
            ...     response = client.get('https://example.com')
        """
        # 这需要在创建 context 之前设置，这里提供一个简化版本
        # 实际使用中应该在初始化时配置
        devices = {
            'iPhone 12': {
                'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)',
                'viewport': {'width': 390, 'height': 844},
                'device_scale_factor': 3,
                'is_mobile': True,
                'has_touch': True,
            },
            'Pixel 5': {
                'user_agent': 'Mozilla/5.0 (Linux; Android 11; Pixel 5)',
                'viewport': {'width': 393, 'height': 851},
                'device_scale_factor': 2.75,
                'is_mobile': True,
                'has_touch': True,
            },
        }
        
        if device_name in devices:
            print(f"提示: 设备模拟应在 Client 初始化时通过 context_options 设置")
            print(f"示例: Client(context_options={devices[device_name]})")
    
    def set_geolocation(self, latitude: float, longitude: float) -> None:
        """设置地理位置
        
        Args:
            latitude: 纬度
            longitude: 经度
            
        Example:
            >>> with Client() as client:
            ...     client.set_geolocation(31.2304, 121.4737)  # 上海
            ...     response = client.get('https://example.com')
        """
        self._ensure_browser()
        self._context.set_geolocation({
            "latitude": latitude,
            "longitude": longitude
        })
        # 授予地理位置权限
        self._context.grant_permissions(["geolocation"])

