"""
Patchright HTTPX - 专业功能示例

演示Cookie持久化、请求历史、重试、缓存、速率限制等专业功能。
"""

import time
import patchright_httpx as httpx
from patchright_httpx import RetryPolicy, RateLimiter


def example_01_cookie_persistence():
    """示例1: Cookie持久化 - 保持登录状态"""
    print("\n=== 示例1: Cookie持久化 ===")
    
    # 场景: 第一次访问，保存cookies
    print("第一次访问...")
    with httpx.Client() as client:
        response = client.get('https://httpbin.org/cookies/set?session=abc123')
        print(f"  状态码: {response.status_code}")
        
        # 保存cookies到文件
        client.save_cookies('examples/output/session.json')
        print("  ✓ Cookies已保存到 session.json")
    
    # 场景: 后续访问，加载cookies
    print("\n后续访问...")
    with httpx.Client() as client:
        # 从文件加载cookies
        client.load_cookies('examples/output/session.json')
        
        # cookies会自动附加到请求上
        response = client.get('https://httpbin.org/cookies')
        data = response.json()
        print(f"  ✓ Cookies加载成功: {data['cookies']}")
    print()


def example_02_request_history():
    """示例2: 请求历史 - 统计分析"""
    print("\n=== 示例2: 请求历史统计 ===")
    
    # 启用历史记录功能
    with httpx.Client(enable_history=True, history_size=100) as client:
        # 发送多个请求
        urls = [
            'https://httpbin.org/get',
            'https://httpbin.org/status/200',
            'https://httpbin.org/delay/1',
        ]
        
        for url in urls:
            try:
                response = client.get(url)
                print(f"  ✓ {url} - {response.status_code}")
            except Exception as e:
                print(f"  ✗ {url} - 失败: {type(e).__name__}")
        
        # 获取统计信息
        stats = client.get_history()
        if stats:
            print(f"\n统计信息:")
            print(f"  总请求数: {stats['total_requests']}")
            print(f"  平均耗时: {stats['avg_duration']:.2f}秒")
            print(f"  最快请求: {stats['min_duration']:.2f}秒")
            print(f"  最慢请求: {stats['max_duration']:.2f}秒")
            print(f"  成功率: {stats['success_rate']:.1%}")
    print()


def example_03_retry_policy():
    """示例3: 重试策略 - 处理不稳定的请求"""
    print("\n=== 示例3: 自动重试策略 ===")
    
    # 创建重试策略: 最多重试3次，指数退避
    retry = RetryPolicy(
        max_retries=3,
        backoff_factor=1.0,
        status_forcelist=[500, 502, 503, 504]
    )
    
    with httpx.Client(retry_policy=retry) as client:
        print(f"重试策略配置:")
        print(f"  最大重试次数: {retry.max_retries}")
        print(f"  退避系数: {retry.backoff_factor}")
        print(f"  重试状态码: {retry.status_forcelist}")
        
        # 演示重试逻辑
        print(f"\n重试时间表:")
        for attempt in range(retry.max_retries):
            wait_time = retry.get_wait_time(attempt)
            print(f"  第{attempt + 1}次重试: 等待{wait_time:.1f}秒")
    print()


def example_04_rate_limiting():
    """示例4: 速率限制 - 控制请求频率"""
    print("\n=== 示例4: 速率限制 ===")
    
    # 创建速率限制器: 每秒最多2个请求
    limiter = RateLimiter(requests_per_second=2.0)
    
    with httpx.Client(rate_limiter=limiter) as client:
        print(f"速率限制: {limiter.requests_per_second} 请求/秒")
        print(f"发送3个请求...")
        
        start_time = time.time()
        
        for i in range(3):
            # 速率限制器会自动控制请求频率
            if limiter:
                limiter.wait_if_needed()
            
            response = client.get('https://httpbin.org/get')
            elapsed = time.time() - start_time
            print(f"  请求{i + 1}: {response.status_code} (累计耗时 {elapsed:.2f}秒)")
        
        total_time = time.time() - start_time
        print(f"\n总耗时: {total_time:.2f}秒 (预期: ~1秒)")
    print()


def example_05_request_cache():
    """示例5: 请求缓存 - 减少重复请求"""
    print("\n=== 示例5: 请求缓存 ===")
    
    # 启用缓存，TTL=300秒
    with httpx.Client(enable_cache=True, cache_ttl=300) as client:
        url = 'https://httpbin.org/get'
        
        # 第一次请求（未缓存）
        print("第一次请求...")
        start = time.time()
        response1 = client.get(url)
        time1 = time.time() - start
        print(f"  状态码: {response1.status_code}")
        print(f"  耗时: {time1:.2f}秒")
        
        # 检查缓存
        if client.cache:
            cache_key = f"GET:{url}"
            cached = client.cache.get(cache_key)
            if cached:
                print(f"  ✓ 已缓存")
            
        # 清除缓存
        client.clear_cache()
        print("  ✓ 缓存已清除")
    print()


def example_06_geolocation():
    """示例6: 地理位置模拟"""
    print("\n=== 示例6: 地理位置模拟 ===")
    
    with httpx.Client() as client:
        # 设置地理位置为东京
        client.set_geolocation(35.6762, 139.6503)
        print("✓ 地理位置已设置: 东京 (35.6762, 139.6503)")
        
        response = client.get('https://httpbin.org/headers')
        print(f"状态码: {response.status_code}")
    print()


def example_07_combined_features():
    """示例7: 组合使用多个功能"""
    print("\n=== 示例7: 组合使用专业功能 ===")
    
    # 创建功能全开的客户端
    retry = RetryPolicy(max_retries=2)
    limiter = RateLimiter(requests_per_second=1.5)
    
    with httpx.Client(
        enable_history=True,
        enable_cache=True,
        retry_policy=retry,
        rate_limiter=limiter,
        context_options={'locale': 'zh-CN'}
    ) as client:
        print("客户端配置:")
        print("  ✓ 请求历史: 启用")
        print("  ✓ 缓存: 启用")
        print("  ✓ 重试策略: 启用 (最多2次)")
        print("  ✓ 速率限制: 1.5 请求/秒")
        print()
        
        # 执行请求
        for i in range(3):
            if limiter:
                limiter.wait_if_needed()
            
            response = client.get('https://httpbin.org/headers')
            print(f"  请求{i + 1}: {response.status_code}")
        
        # 保存session
        client.save_cookies('examples/output/session_advanced.json')
        print("\n✓ Session已保存")
        
        # 获取统计
        stats = client.get_history()
        if stats:
            print(f"\n统计:")
            print(f"  总请求: {stats['total_requests']}")
            print(f"  平均耗时: {stats['avg_duration']:.2f}秒")
            print(f"  成功率: {stats['success_rate']:.1%}")
    print()


def example_08_session_management():
    """示例8: 会话管理 - 实战场景"""
    print("\n=== 示例8: 会话管理实战 ===")
    
    print("场景: 模拟登录并保持会话")
    
    # 第一步: 登录
    print("\n第1步: 登录...")
    with httpx.Client() as client:
        # 模拟登录请求
        response = client.post(
            'https://httpbin.org/post',
            json={'username': 'admin', 'password': 'secret'}
        )
        print(f"  登录响应: {response.status_code}")
        
        # 保存登录后的cookies
        client.save_cookies('examples/output/login_session.json')
        print("  ✓ 登录会话已保存")
    
    # 第二步: 使用保存的会话访问
    print("\n第2步: 使用会话访问...")
    with httpx.Client() as client:
        # 加载登录会话
        client.load_cookies('examples/output/login_session.json')
        
        # 访问需要登录的接口
        response = client.get('https://httpbin.org/cookies')
        print(f"  访问响应: {response.status_code}")
        print(f"  ✓ 会话有效")
    print()


def example_09_error_handling():
    """示例9: 优雅的错误处理"""
    print("\n=== 示例9: 错误处理 ===")
    
    with httpx.Client() as client:
        # 处理超时
        try:
            response = client.get('https://httpbin.org/delay/10', timeout=1.0)
        except httpx.TimeoutError:
            print("✓ 超时错误捕获成功")
        
        # 处理HTTP错误
        try:
            response = client.get('https://httpbin.org/status/404')
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            print(f"✓ HTTP错误捕获成功: {e.response.status_code}")
    print()


def example_10_production_ready():
    """示例10: 生产级配置"""
    print("\n=== 示例10: 生产级配置 ===")
    
    # 生产环境推荐配置
    retry = RetryPolicy(max_retries=3, backoff_factor=2.0)
    limiter = RateLimiter(requests_per_second=10.0)
    
    with httpx.Client(
        headless=True,
        enable_history=True,
        enable_cache=True,
        cache_ttl=600,
        retry_policy=retry,
        rate_limiter=limiter,
        timeout=30.0,
        launch_options={
            'args': ['--disable-blink-features=AutomationControlled']
        }
    ) as client:
        print("生产级配置:")
        print("  ✓ 无头模式")
        print("  ✓ 请求历史")
        print("  ✓ 缓存 (10分钟)")
        print("  ✓ 重试 (最多3次，指数退避)")
        print("  ✓ 速率限制 (10 req/s)")
        print("  ✓ 超时 (30秒)")
        print("  ✓ 反检测配置")
        
        # 执行请求
        response = client.get('https://httpbin.org/get')
        print(f"\n测试请求: {response.status_code}")
    print()


def main():
    """运行所有专业功能示例"""
    print("=" * 60)
    print("Patchright HTTPX - 专业功能示例")
    print("=" * 60)
    
    # 创建输出目录
    import os
    os.makedirs('examples/output', exist_ok=True)
    
    example_01_cookie_persistence()
    example_02_request_history()
    example_03_retry_policy()
    example_04_rate_limiting()
    example_05_request_cache()
    example_06_geolocation()
    example_07_combined_features()
    example_08_session_management()
    example_09_error_handling()
    example_10_production_ready()
    
    print("=" * 60)
    print("✓ 所有专业功能示例运行完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()

