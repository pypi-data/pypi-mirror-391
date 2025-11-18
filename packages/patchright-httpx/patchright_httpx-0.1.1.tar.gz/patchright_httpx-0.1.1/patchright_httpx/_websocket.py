"""WebSocket 相关功能"""

import time
import json as json_module
from typing import Optional, Callable, Any, Dict, List
from patchright.sync_api import Page as SyncPage, WebSocket as PWWebSocket
from patchright.async_api import Page as AsyncPage


class WebSocketConnection:
    """WebSocket 连接封装
    
    提供类似 httpx/websockets 的接口来处理 WebSocket 连接
    
    内部使用 Playwright 的 WebSocket 对象,支持:
    - 同步发送/接收消息
    - 消息队列
    - 连接状态管理
    """
    
    def __init__(self, page: SyncPage, url: str, timeout: float = 10.0):
        """初始化WebSocket连接
        
        Args:
            page: Playwright页面对象
            url: WebSocket URL
            timeout: 连接超时(秒)
        """
        self._page = page
        self._url = url
        self._timeout = timeout
        self._is_closed = False
        self._pw_websocket: Optional[PWWebSocket] = None
        self._message_queue: List[str] = []
        self._on_message_callbacks: List[Callable[[str], None]] = []
        self._on_close_callbacks: List[Callable[[], None]] = []
        
        # 建立连接
        self._connect()
    
    def _connect(self) -> None:
        """建立WebSocket连接并等待ready"""
        
        # 通过JavaScript创建WebSocket连接并等待open事件
        connection_result = self._page.evaluate("""
            (url) => {
                return new Promise((resolve, reject) => {
                    try {
                        const ws = new WebSocket(url);
                        window.__patchright_ws__ = ws;
                        window.__patchright_ws_messages__ = [];
                        
                        // 超时处理
                        const timeout = setTimeout(() => {
                            reject(new Error('Connection timeout'));
                        }, 10000);
                        
                        ws.onopen = () => {
                            clearTimeout(timeout);
                            resolve({success: true, url: ws.url});
                        };
                        
                        ws.onerror = (error) => {
                            clearTimeout(timeout);
                            reject(new Error('WebSocket connection failed'));
                        };
                        
                        // 缓存接收到的消息
                        ws.onmessage = (event) => {
                            window.__patchright_ws_messages__.push(event.data);
                        };
                        
                        ws.onclose = () => {
                            window.__patchright_ws_closed__ = true;
                        };
                    } catch (error) {
                        reject(error);
                    }
                });
            }
        """, self._url)
        
        if not connection_result.get('success'):
            raise RuntimeError(f"WebSocket连接失败: {self._url}")
        
        # 启动消息轮询
        self._start_message_polling()
    
    def _start_message_polling(self) -> None:
        """启动消息轮询(从JavaScript的消息缓存中读取)"""
        # 不需要单独线程,使用同步轮询
        pass
    
    def _poll_messages(self) -> None:
        """从JavaScript端轮询消息"""
        if self._is_closed:
            return
        
        try:
            # 从JavaScript获取缓存的消息
            messages = self._page.evaluate("""
                () => {
                    const messages = window.__patchright_ws_messages__ || [];
                    window.__patchright_ws_messages__ = [];
                    return messages;
                }
            """)
            
            if messages:
                for msg in messages:
                    self._message_queue.append(msg)
                    
                    # 调用用户回调
                    for callback in self._on_message_callbacks:
                        try:
                            callback(msg)
                        except Exception:
                            pass
            
            # 检查是否已关闭
            is_closed = self._page.evaluate("() => window.__patchright_ws_closed__ || false")
            if is_closed:
                self._is_closed = True
                for callback in self._on_close_callbacks:
                    try:
                        callback()
                    except Exception:
                        pass
        except Exception:
            pass  # 忽略轮询错误
    
    @property
    def url(self) -> str:
        """获取 WebSocket URL"""
        return self._url
    
    @property
    def is_closed(self) -> bool:
        """检查连接是否已关闭"""
        return self._is_closed
    
    def send_text(self, message: str) -> None:
        """发送文本消息
        
        Args:
            message: 要发送的文本消息
            
        Raises:
            RuntimeError: 如果连接已关闭
        """
        if self._is_closed:
            raise RuntimeError("WebSocket已关闭")
        
        # 通过JavaScript发送(确保WebSocket已ready)
        try:
            self._page.evaluate("""
                (message) => {
                    if (window.__patchright_ws__ && window.__patchright_ws__.readyState === WebSocket.OPEN) {
                        window.__patchright_ws__.send(message);
                    } else {
                        throw new Error('WebSocket not ready');
                    }
                }
            """, message)
        except Exception as e:
            raise RuntimeError(f"发送消息失败: {e}")
    
    def send_json(self, data: Dict[str, Any]) -> None:
        """发送 JSON 消息
        
        Args:
            data: 要发送的数据字典
        """
        self.send_text(json_module.dumps(data))
    
    def receive_text(self, timeout: Optional[float] = None) -> str:
        """接收文本消息(阻塞直到收到消息)
        
        Args:
            timeout: 超时时间(秒),None表示使用默认超时
            
        Returns:
            接收到的文本消息
            
        Raises:
            TimeoutError: 超时未收到消息
            RuntimeError: 连接已关闭
        """
        if self._is_closed:
            raise RuntimeError("WebSocket已关闭")
        
        timeout = timeout if timeout is not None else self._timeout
        start_time = time.time()
        
        while not self._message_queue:
            # 轮询新消息
            self._poll_messages()
            
            if self._is_closed:
                raise RuntimeError("WebSocket连接已关闭")
            if time.time() - start_time > timeout:
                raise TimeoutError(f"接收消息超时({timeout}秒)")
            time.sleep(0.05)
        
        return self._message_queue.pop(0)
    
    def receive_json(self, timeout: Optional[float] = None) -> Any:
        """接收 JSON 消息
        
        Args:
            timeout: 超时时间(秒)
            
        Returns:
            解析后的JSON数据
        """
        text = self.receive_text(timeout=timeout)
        return json_module.loads(text)
    
    def iter_messages(self, timeout: Optional[float] = None) -> str:
        """迭代接收消息
        
        Args:
            timeout: 每条消息的超时时间
            
        Yields:
            str: 接收到的消息
        """
        while not self._is_closed:
            try:
                yield self.receive_text(timeout=timeout or 1.0)
            except TimeoutError:
                continue
            except RuntimeError:
                break
    
    def on_message(self, callback: Callable[[str], None]) -> None:
        """注册消息接收回调
        
        Args:
            callback: 回调函数,接收消息文本作为参数
        """
        self._on_message_callbacks.append(callback)
    
    def on_close(self, callback: Callable[[], None]) -> None:
        """注册连接关闭回调
        
        Args:
            callback: 回调函数,无参数
        """
        self._on_close_callbacks.append(callback)
    
    def close(self) -> None:
        """关闭连接"""
        if not self._is_closed:
            try:
                self._page.evaluate("""
                    () => {
                        if (window.__patchright_ws__) {
                            window.__patchright_ws__.close();
                            delete window.__patchright_ws__;
                        }
                    }
                """)
            except Exception:
                pass  # 忽略关闭错误
            finally:
                self._is_closed = True
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def __repr__(self) -> str:
        status = "closed" if self._is_closed else "open"
        return f"<WebSocketConnection [{status}] {self._url}>"


class AsyncWebSocketConnection:
    """异步 WebSocket 连接封装
    
    提供类似 websockets 的异步接口
    """
    
    def __init__(self, page: AsyncPage, url: str, timeout: float = 10.0):
        """初始化异步WebSocket连接
        
        Args:
            page: Playwright异步页面对象
            url: WebSocket URL
            timeout: 连接超时(秒)
        """
        self._page = page
        self._url = url
        self._timeout = timeout
        self._is_closed = False
        self._pw_websocket: Optional[PWWebSocket] = None
        self._message_queue: List[str] = []
        self._on_message_callbacks: List[Callable[[str], None]] = []
        self._on_close_callbacks: List[Callable[[], None]] = []
    
    async def _connect(self) -> None:
        """建立WebSocket连接并等待ready"""
        import asyncio
        
        ws_captured = []
        
        def handle_websocket(ws: PWWebSocket):
            """捕获WebSocket对象"""
            if ws.url == self._url:
                ws_captured.append(ws)
                
                # 设置消息接收处理
                def on_frame_received(payload):
                    text = payload if isinstance(payload, str) else str(payload)
                    self._message_queue.append(text)
                    
                    # 调用用户回调
                    for callback in self._on_message_callbacks:
                        try:
                            callback(text)
                        except Exception:
                            pass
                
                # 设置关闭处理
                def on_socket_close(ws):
                    self._is_closed = True
                    for callback in self._on_close_callbacks:
                        try:
                            callback()
                        except Exception:
                            pass
                
                ws.on("framereceived", on_frame_received)
                ws.on("close", lambda: on_socket_close(ws))
        
        # 注册WebSocket监听器
        self._page.on("websocket", handle_websocket)
        
        # 通过JavaScript创建WebSocket连接
        await self._page.evaluate("""
            (url) => {
                return new Promise((resolve, reject) => {
                    const ws = new WebSocket(url);
                    
                    ws.onopen = () => {
                        window.__patchright_ws__ = ws;
                        resolve(true);
                    };
                    
                    ws.onerror = (error) => {
                        reject(new Error('WebSocket connection failed'));
                    };
                });
            }
        """, self._url)
        
        # 等待playwright捕获WebSocket对象
        start_time = time.time()
        while not ws_captured:
            if time.time() - start_time > self._timeout:
                raise TimeoutError(f"WebSocket连接超时: {self._url}")
            await asyncio.sleep(0.1)
        
        self._pw_websocket = ws_captured[0]
    
    @property
    def url(self) -> str:
        """获取 WebSocket URL"""
        return self._url
    
    @property
    def is_closed(self) -> bool:
        """检查连接是否已关闭"""
        return self._is_closed
    
    async def send_text(self, message: str) -> None:
        """发送文本消息
        
        Args:
            message: 要发送的文本消息
            
        Raises:
            RuntimeError: 如果连接已关闭
        """
        if self._is_closed:
            raise RuntimeError("WebSocket已关闭")
        
        try:
            await self._page.evaluate("""
                (message) => {
                    if (window.__patchright_ws__ && window.__patchright_ws__.readyState === WebSocket.OPEN) {
                        window.__patchright_ws__.send(message);
                    } else {
                        throw new Error('WebSocket not ready');
                    }
                }
            """, message)
        except Exception as e:
            raise RuntimeError(f"发送消息失败: {e}")
    
    async def send_json(self, data: Dict[str, Any]) -> None:
        """发送 JSON 消息
        
        Args:
            data: 要发送的数据字典
        """
        await self.send_text(json_module.dumps(data))
    
    async def receive_text(self, timeout: Optional[float] = None) -> str:
        """接收文本消息(异步等待)
        
        Args:
            timeout: 超时时间(秒),None表示使用默认超时
            
        Returns:
            接收到的文本消息
            
        Raises:
            TimeoutError: 超时未收到消息
            RuntimeError: 连接已关闭
        """
        import asyncio
        
        if self._is_closed:
            raise RuntimeError("WebSocket已关闭")
        
        timeout = timeout if timeout is not None else self._timeout
        start_time = time.time()
        
        while not self._message_queue:
            if self._is_closed:
                raise RuntimeError("WebSocket连接已关闭")
            if time.time() - start_time > timeout:
                raise TimeoutError(f"接收消息超时({timeout}秒)")
            await asyncio.sleep(0.05)
        
        return self._message_queue.pop(0)
    
    async def receive_json(self, timeout: Optional[float] = None) -> Any:
        """接收 JSON 消息
        
        Args:
            timeout: 超时时间(秒)
            
        Returns:
            解析后的JSON数据
        """
        text = await self.receive_text(timeout=timeout)
        return json_module.loads(text)
    
    async def iter_messages(self, timeout: Optional[float] = None):
        """异步迭代接收消息
        
        Args:
            timeout: 每条消息的超时时间
            
        Yields:
            str: 接收到的消息
        """
        while not self._is_closed:
            try:
                yield await self.receive_text(timeout=timeout or 1.0)
            except TimeoutError:
                continue
            except RuntimeError:
                break
    
    def on_message(self, callback: Callable[[str], None]) -> None:
        """注册消息接收回调
        
        Args:
            callback: 回调函数,接收消息文本作为参数
        """
        self._on_message_callbacks.append(callback)
    
    def on_close(self, callback: Callable[[], None]) -> None:
        """注册连接关闭回调
        
        Args:
            callback: 回调函数,无参数
        """
        self._on_close_callbacks.append(callback)
    
    async def close(self) -> None:
        """关闭连接"""
        if not self._is_closed:
            try:
                await self._page.evaluate("""
                    () => {
                        if (window.__patchright_ws__) {
                            window.__patchright_ws__.close();
                            delete window.__patchright_ws__;
                        }
                    }
                """)
            except Exception:
                pass
            finally:
                self._is_closed = True
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    def __repr__(self) -> str:
        status = "closed" if self._is_closed else "open"
        return f"<AsyncWebSocketConnection [{status}] {self._url}>"
