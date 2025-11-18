# Patchright HTTPX - 示例说明

本目录包含 Patchright HTTPX 的完整示例代码。

## 📁 示例文件

### 01_basic.py - 基础功能示例
**适合**: 新手入门  
**内容**: 
- 简单GET/POST请求
- 查询参数和JSON数据
- 自定义请求头
- 基本认证
- 超时设置
- 响应解析
- 客户端复用

### 02_advanced.py - 高级功能示例  
**适合**: 进阶使用  
**内容**:
- 自定义浏览器配置
- JavaScript执行
- 页面截图和PDF生成
- 使用原生Playwright API
- 多页面操作
- 代理设置
- 异步操作

### 03_professional.py - 专业功能示例
**适合**: 专业开发  
**内容**:
- Cookie持久化
- 请求历史和统计
- 自动重试策略
- 速率限制
- 请求缓存
- 地理位置模拟
- 组合使用多功能
- 生产级配置

### 04_real_world.py - 实战场景示例
**适合**: 实际项目  
**内容**:
- 网页爬虫
- API测试
- 登录会话管理
- 数据提取
- 表单自动化
- 网站监控
- 批量处理
- 错误恢复
- 生产级爬虫

### 05_websocket.py - WebSocket示例
**适合**: 实时通信  
**内容**:
- 基础WebSocket连接
- 回调函数
- JSON消息传递
- 二进制数据
- Ping/Pong保活
- 多连接管理
- 错误处理
- 聊天模拟
- 断线重连
- 流式数据

## 🚀 快速开始

### 运行单个示例

```bash
# 基础功能
python examples/01_basic.py

# 高级功能
python examples/02_advanced.py

# 专业功能
python examples/03_professional.py

# 实战场景
python examples/04_real_world.py

# WebSocket
python examples/05_websocket.py
```

### 运行特定示例函数

```python
from examples import basic

# 只运行特定示例
basic.example_01_simple_get()
basic.example_03_post_json()
```

## 📦 依赖要求

```bash
pip install patchright httpx
patchright install
```

## 💡 使用建议

1. **新手**: 从 `01_basic.py` 开始
2. **进阶**: 学习 `02_advanced.py` 的浏览器功能
3. **专业**: 掌握 `03_professional.py` 的高级特性
4. **实战**: 参考 `04_real_world.py` 的实际场景
5. **实时**: 查看 `05_websocket.py` 的WebSocket用法

## 🎯 示例索引

### 按功能分类

#### HTTP基础
- `01_basic.py`: 示例1-10

#### 浏览器功能
- `02_advanced.py`: 示例1-9

#### 性能优化
- `03_professional.py`: 示例2,4,5,7
- `04_real_world.py`: 示例1,7,10

#### 会话管理
- `03_professional.py`: 示例1,8
- `04_real_world.py`: 示例3

#### 自动化
- `04_real_world.py`: 示例4,5

#### 实时通信
- `05_websocket.py`: 示例1-10

## 📝 输出文件

某些示例会在 `examples/output/` 目录生成文件:
- `session.json` - Cookie会话
- `screenshot.png` - 页面截图
- `page.pdf` - 页面PDF
- 等等

## ⚠️ 注意事项

1. **网络依赖**: 示例需要访问外部网站，确保网络连接正常
2. **速率限制**: 某些网站有速率限制，请合理使用
3. **WebSocket**: WebSocket示例需要服务器支持
4. **文件权限**: 确保有权限创建output目录和写入文件

## 🤝 贡献

欢迎贡献更多示例! 请遵循以下规范:
- 每个示例函数独立完整
- 添加清晰的注释和print输出
- 包含错误处理
- 遵循现有的代码风格

## 📞 支持

- GitHub Issues: 报告问题
- 文档: 查看完整文档
- 示例: 参考这些示例代码

---

**快乐编程! 🎉**

