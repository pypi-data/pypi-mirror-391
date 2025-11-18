"""高级工具和辅助功能"""

import json
import pickle
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta


class CookieJar:
    """Cookie 持久化管理器"""
    
    def __init__(self, filepath: Optional[str] = None):
        self.filepath = filepath or "cookies.json"
    
    def save(self, cookies: List[Dict[str, Any]]) -> None:
        """保存 cookies 到文件"""
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, indent=2, ensure_ascii=False)
    
    def load(self) -> List[Dict[str, Any]]:
        """从文件加载 cookies"""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def clear(self) -> None:
        """清除保存的 cookies"""
        if Path(self.filepath).exists():
            Path(self.filepath).unlink()


class RequestHistory:
    """请求历史记录器
    
    用于记录和统计 HTTP 请求历史，提供请求成功率、耗时等统计信息。
    
    Attributes:
        max_size: 最大历史记录数量
        history: 历史记录列表
    """
    
    def __init__(self, max_size: int = 100):
        """初始化历史记录器
        
        Args:
            max_size: 最大保存的历史记录数量，超过后自动删除最旧的记录
        """
        self.max_size = max_size
        self.history: List[Dict[str, Any]] = []
    
    def add(self, method: str, url: str, status: int, duration: float) -> None:
        """添加请求记录到历史
        
        Args:
            method: HTTP 方法 (GET/POST/PUT/DELETE/PATCH/HEAD/OPTIONS)
            url: 请求的完整 URL
            status: HTTP 状态码 (100-599)
            duration: 请求耗时(秒)
        
        Returns:
            None
        
        Side Effects:
            - 添加记录到 self.history
            - 如果超过 max_size 则删除最旧的记录
        
        Example:
            >>> history = RequestHistory(max_size=100)
            >>> history.add('GET', 'https://example.com', 200, 0.5)
        """
        record = {
            'timestamp': datetime.now().isoformat(),
            'method': method,
            'url': url,
            'status': status,
            'duration': duration,
        }
        
        self.history.append(record)
        
        # 保持最大数量限制
        if len(self.history) > self.max_size:
            self.history.pop(0)
    
    def get_all(self) -> List[Dict[str, Any]]:
        """获取所有历史记录
        
        Returns:
            历史记录列表的副本，每条记录包含 timestamp/method/url/status/duration
        """
        return self.history.copy()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息
        
        Returns:
            统计信息字典，包含以下键：
            - total_requests: 总请求数
            - avg_duration: 平均耗时(秒)
            - min_duration: 最快请求耗时(秒)
            - max_duration: 最慢请求耗时(秒)
            - success_rate: 成功率 (0.0-1.0，状态码 2xx 视为成功)
            
            如果没有历史记录则返回空字典
        """
        if not self.history:
            return {}
        
        durations = [r['duration'] for r in self.history]
        statuses = [r['status'] for r in self.history]
        
        return {
            'total_requests': len(self.history),
            'avg_duration': sum(durations) / len(durations),
            'min_duration': min(durations),
            'max_duration': max(durations),
            'success_rate': sum(1 for s in statuses if 200 <= s < 300) / len(statuses),
        }
    
    def clear(self) -> None:
        """清除所有历史记录
        
        Side Effects:
            清空 self.history 列表
        """
        self.history.clear()


class RetryPolicy:
    """重试策略"""
    
    def __init__(
        self,
        max_retries: int = 3,
        backoff_factor: float = 1.0,
        status_forcelist: Optional[List[int]] = None,
    ):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.status_forcelist = status_forcelist or [500, 502, 503, 504]
    
    def should_retry(self, status_code: int, attempt: int) -> bool:
        """判断是否应该重试"""
        if attempt >= self.max_retries:
            return False
        return status_code in self.status_forcelist
    
    def get_wait_time(self, attempt: int) -> float:
        """获取等待时间（指数退避）"""
        return self.backoff_factor * (2 ** attempt)


class RateLimiter:
    """速率限制器"""
    
    def __init__(self, requests_per_second: float = 1.0):
        self.requests_per_second = requests_per_second
        self.min_interval = 1.0 / requests_per_second
        self.last_request_time: Optional[datetime] = None
    
    def wait_if_needed(self) -> None:
        """如果需要则等待"""
        import time
        
        if self.last_request_time is None:
            self.last_request_time = datetime.now()
            return
        
        elapsed = (datetime.now() - self.last_request_time).total_seconds()
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        
        self.last_request_time = datetime.now()


class SessionStorage:
    """会话存储管理器"""
    
    def __init__(self, filepath: str = "session.pkl"):
        self.filepath = filepath
    
    def save(self, context_state: Dict[str, Any]) -> None:
        """保存浏览器会话状态"""
        with open(self.filepath, 'wb') as f:
            pickle.dump(context_state, f)
    
    def load(self) -> Optional[Dict[str, Any]]:
        """加载浏览器会话状态"""
        try:
            with open(self.filepath, 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            return None
    
    def clear(self) -> None:
        """清除会话文件"""
        if Path(self.filepath).exists():
            Path(self.filepath).unlink()


class RequestCache:
    """简单的请求缓存"""
    
    def __init__(self, ttl: int = 300):
        self.ttl = ttl  # 缓存有效期（秒）
        self.cache: Dict[str, tuple] = {}  # {key: (response, timestamp)}
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if key not in self.cache:
            return None
        
        response, timestamp = self.cache[key]
        
        # 检查是否过期
        if (datetime.now() - timestamp).total_seconds() > self.ttl:
            del self.cache[key]
            return None
        
        return response
    
    def set(self, key: str, response: Any) -> None:
        """设置缓存"""
        self.cache[key] = (response, datetime.now())
    
    def clear(self) -> None:
        """清除所有缓存"""
        self.cache.clear()
    
    def cleanup(self) -> None:
        """清理过期缓存"""
        now = datetime.now()
        expired_keys = [
            key for key, (_, timestamp) in self.cache.items()
            if (now - timestamp).total_seconds() > self.ttl
        ]
        for key in expired_keys:
            del self.cache[key]

