# Patchright HTTPX

**English** | [中文](#中文)

---

## 🌐 English

### Overview

**Patchright HTTPX** is a modern HTTP client library that combines the simplicity of HTTPX with the power of real browser automation using Patchright (Playwright).

### ✨ Key Features

- 🎯 **HTTPX-Compatible API** - Drop-in replacement for httpx with identical interface
- 🌐 **Real Browser** - Powered by Patchright/Playwright for authentic requests
- 🚀 **WebSocket Support** - Full WebSocket client implementation
- 🔧 **Event Hooks** - Request/response interceptors
- 🍪 **Cookie Persistence** - Save and load cookies easily
- 📊 **Request History** - Built-in statistics and monitoring
- 🔄 **Auto Retry** - Configurable retry policies
- ⚡ **Rate Limiting** - Control request frequency
- 💾 **Request Cache** - Reduce redundant requests
- 🎭 **Multiple Browsers** - Chromium, Firefox, WebKit support

### 📦 Installation

```bash
pip install patchright-httpx
```

### 🚀 Quick Start

#### Basic Usage

```python
import patchright_httpx as httpx

# Simple GET request
response = httpx.get('https://api.github.com')
print(response.json())

# POST with JSON
response = httpx.post('https://httpbin.org/post', json={'key': 'value'})

# Using Client
with httpx.Client() as client:
    response = client.get('https://example.com')
    print(response.status_code)
```

#### Advanced Features

```python
import patchright_httpx as httpx

# Cookie persistence
with httpx.Client() as client:
    client.load_cookies('session.json')
    response = client.get('https://example.com')
    client.save_cookies('session.json')

# Request history and statistics
with httpx.Client(enable_history=True) as client:
    for i in range(10):
        client.get(f'https://api.example.com/page/{i}')
    
    stats = client.get_history()
    print(f"Success rate: {stats['success_rate']:.1%}")
    print(f"Average time: {stats['average_duration']:.2f}s")

# Auto retry with rate limiting
retry = httpx.RetryPolicy(max_retries=3, backoff_factor=2.0)
limiter = httpx.RateLimiter(requests_per_second=5.0)

with httpx.Client(retry_policy=retry, rate_limiter=limiter) as client:
    response = client.get('https://api.example.com')
```

#### WebSocket

```python
import patchright_httpx as httpx

with httpx.Client() as client:
    ws = client.websocket_connect('wss://echo.websocket.org')
    
    ws.send_text('Hello WebSocket!')
    response = ws.receive_text()
    print(f"Received: {response}")
    
    ws.close()
```

#### Event Hooks

```python
import patchright_httpx as httpx

def log_request(request):
    print(f"Sending: {request['method']} {request['url']}")

def log_response(response):
    print(f"Received: {response.status_code}")

with httpx.Client(
    event_hooks={
        'request': [log_request],
        'response': [log_response]
    }
) as client:
    client.get('https://example.com')
```

#### Browser Configuration

```python
import patchright_httpx as httpx

# Use different browsers
with httpx.Client(browser_type='firefox') as client:
    response = client.get('https://example.com')

# Configure viewport
with httpx.Client(viewport={'width': 375, 'height': 667}) as client:
    screenshot = client.screenshot('https://example.com', path='mobile.png')

# Advanced options
with httpx.Client(
    browser_type='chromium',
    headless=True,
    launch_options={
        'args': ['--disable-blink-features=AutomationControlled']
    },
    context_options={
        'locale': 'en-US',
        'timezone_id': 'America/New_York'
    }
) as client:
    response = client.get('https://example.com')
```

### 📚 Documentation

For more examples, see the [examples](examples/) directory:

- `01_basic.py` - Basic HTTP operations
- `02_advanced.py` - Advanced features
- `03_professional.py` - Professional usage patterns
- `04_real_world.py` - Real-world scenarios
- `05_websocket.py` - WebSocket examples
- `06_browser_config.py` - Browser configuration
- `07_hooks_and_interactions.py` - Hooks and page interactions

### 🔧 API Reference

#### Client

```python
httpx.Client(
    browser_type='chromium',      # 'chromium', 'firefox', 'webkit'
    headless=True,                # Run in headless mode
    timeout=30.0,                 # Default timeout
    proxy=None,                   # Proxy configuration
    base_url=None,                # Base URL for requests
    enable_cache=False,           # Enable request cache
    enable_history=False,         # Enable request history
    retry_policy=None,            # Auto retry policy
    rate_limiter=None,            # Rate limiting
    event_hooks=None,             # Request/response hooks
)
```

#### Response

```python
response.status_code    # HTTP status code
response.headers        # Response headers
response.content        # Raw bytes
response.text           # Decoded text
response.json()         # Parse JSON
response.elapsed        # Request duration
response.cookies        # Response cookies
```

### 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

### 🙏 Acknowledgments

This project is built on top of:

- [httpx](https://github.com/encode/httpx) - Modern HTTP client
- [playwright](https://github.com/microsoft/playwright) - Browser automation
- [patchright](https://github.com/Kaliiiiiiiiii-Vinyzu/patchright) - Enhanced Playwright

---

## 🇨🇳 中文

### 概述

**Patchright HTTPX** 是一个现代化的 HTTP 客户端库，结合了 HTTPX 的简洁 API 和 Patchright (Playwright) 的真实浏览器自动化能力。

### ✨ 核心特性

- 🎯 **HTTPX 兼容 API** - 与 httpx 完全兼容的接口
- 🌐 **真实浏览器** - 基于 Patchright/Playwright 的真实请求
- 🚀 **WebSocket 支持** - 完整的 WebSocket 客户端实现
- 🔧 **事件钩子** - 请求/响应拦截器
- 🍪 **Cookie 持久化** - 轻松保存和加载 cookies
- 📊 **请求历史** - 内置统计和监控
- 🔄 **自动重试** - 可配置的重试策略
- ⚡ **速率限制** - 控制请求频率
- 💾 **请求缓存** - 减少重复请求
- 🎭 **多浏览器** - 支持 Chromium、Firefox、WebKit

### 📦 安装

```bash
pip install patchright-httpx
```

### 🚀 快速开始

#### 基础用法

```python
import patchright_httpx as httpx

# 简单的 GET 请求
response = httpx.get('https://api.github.com')
print(response.json())

# POST JSON 数据
response = httpx.post('https://httpbin.org/post', json={'key': 'value'})

# 使用 Client
with httpx.Client() as client:
    response = client.get('https://example.com')
    print(response.status_code)
```

#### 高级功能

```python
import patchright_httpx as httpx

# Cookie 持久化
with httpx.Client() as client:
    client.load_cookies('session.json')
    response = client.get('https://example.com')
    client.save_cookies('session.json')

# 请求历史和统计
with httpx.Client(enable_history=True) as client:
    for i in range(10):
        client.get(f'https://api.example.com/page/{i}')
    
    stats = client.get_history()
    print(f"成功率: {stats['success_rate']:.1%}")
    print(f"平均耗时: {stats['average_duration']:.2f}秒")

# 自动重试和速率限制
retry = httpx.RetryPolicy(max_retries=3, backoff_factor=2.0)
limiter = httpx.RateLimiter(requests_per_second=5.0)

with httpx.Client(retry_policy=retry, rate_limiter=limiter) as client:
    response = client.get('https://api.example.com')
```

#### WebSocket

```python
import patchright_httpx as httpx

with httpx.Client() as client:
    ws = client.websocket_connect('wss://echo.websocket.org')
    
    ws.send_text('Hello WebSocket!')
    response = ws.receive_text()
    print(f"收到: {response}")
    
    ws.close()
```

#### 事件钩子

```python
import patchright_httpx as httpx

def log_request(request):
    print(f"发送: {request['method']} {request['url']}")

def log_response(response):
    print(f"收到: {response.status_code}")

with httpx.Client(
    event_hooks={
        'request': [log_request],
        'response': [log_response]
    }
) as client:
    client.get('https://example.com')
```

#### 浏览器配置

```python
import patchright_httpx as httpx

# 使用不同浏览器
with httpx.Client(browser_type='firefox') as client:
    response = client.get('https://example.com')

# 配置视口
with httpx.Client(viewport={'width': 375, 'height': 667}) as client:
    screenshot = client.screenshot('https://example.com', path='mobile.png')

# 高级选项
with httpx.Client(
    browser_type='chromium',
    headless=True,
    launch_options={
        'args': ['--disable-blink-features=AutomationControlled']
    },
    context_options={
        'locale': 'zh-CN',
        'timezone_id': 'Asia/Shanghai'
    }
) as client:
    response = client.get('https://example.com')
```

### 📚 文档

更多示例请查看 [examples](examples/) 目录:

- `01_basic.py` - 基础 HTTP 操作
- `02_advanced.py` - 高级功能
- `03_professional.py` - 专业用法
- `04_real_world.py` - 实战场景
- `05_websocket.py` - WebSocket 示例
- `06_browser_config.py` - 浏览器配置
- `07_hooks_and_interactions.py` - 钩子和页面交互

### 🔧 API 参考

#### Client 客户端

```python
httpx.Client(
    browser_type='chromium',      # 浏览器类型: 'chromium', 'firefox', 'webkit'
    headless=True,                # 无头模式
    timeout=30.0,                 # 默认超时
    proxy=None,                   # 代理配置
    base_url=None,                # 基础 URL
    enable_cache=False,           # 启用缓存
    enable_history=False,         # 启用历史记录
    retry_policy=None,            # 重试策略
    rate_limiter=None,            # 速率限制
    event_hooks=None,             # 事件钩子
)
```

#### Response 响应

```python
response.status_code    # HTTP 状态码
response.headers        # 响应头
response.content        # 原始字节
response.text           # 解码文本
response.json()         # 解析 JSON
response.elapsed        # 请求耗时
response.cookies        # 响应 cookies
```

### 🤝 贡献

欢迎贡献! 请随时提交 Pull Request。

### 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件。

### 🙏 致谢

本项目基于以下优秀开源项目:

- [httpx](https://github.com/encode/httpx) - 现代 HTTP 客户端
- [playwright](https://github.com/microsoft/playwright) - 浏览器自动化
- [patchright](https://github.com/Kaliiiiiiiiii-Vinyzu/patchright) - 增强版 Playwright

---

**Author / 作者**: awaa-col 

**Repository / 仓库**: https://github.com/awaa-col/patchright-httpx

**License / 许可**: MIT

[![PyPI](https://img.shields.io/pypi/v/patchright-httpx)](https://pypi.org/project/patchright-httpx/)
[![Python](https://img.shields.io/pypi/pyversions/patchright-httpx)](https://pypi.org/project/patchright-httpx/)
[![License](https://img.shields.io/github/license/awaa-col/patchright-httpx)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/awaa-col/patchright-httpx?style=social)](https://github.com/awaa-col/patchright-httpx)
