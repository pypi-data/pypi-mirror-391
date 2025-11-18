"""
Patchright HTTPX - 实战场景示例

演示真实项目中的典型应用场景。
"""

import patchright_httpx as httpx
from patchright_httpx import RetryPolicy, RateLimiter


def scenario_01_web_scraping():
    """场景1: 网页爬虫 - 带重试和速率限制"""
    print("\n=== 场景1: 网页爬虫 ===")
    
    # 配置: 速率限制 + 重试策略
    limiter = RateLimiter(requests_per_second=2.0)
    retry = RetryPolicy(max_retries=3, backoff_factor=2.0)
    
    with httpx.Client(
        rate_limiter=limiter,
        retry_policy=retry,
        enable_history=True
    ) as client:
        # 要爬取的URL列表
        urls = [
            'https://httpbin.org/html',
            'https://httpbin.org/links/5',
            'https://httpbin.org/json',
        ]
        
        results = []
        print("开始爬取...")
        for i, url in enumerate(urls, 1):
            try:
                # 自动遵守速率限制
                if limiter:
                    limiter.wait_if_needed()
                
                response = client.get(url)
                results.append({
                    'url': url,
                    'status': response.status_code,
                    'size': len(response.content)
                })
                print(f"  [{i}/{len(urls)}] {url[:40]}... - {response.status_code}")
            except Exception as e:
                print(f"  [{i}/{len(urls)}] {url[:40]}... - 失败: {type(e).__name__}")
        
        # 统计信息
        stats = client.get_history()
        print(f"\n爬取统计:")
        print(f"  成功: {len(results)}/{len(urls)}")
        print(f"  平均耗时: {stats['avg_duration']:.2f}秒")
        print(f"  总大小: {sum(r['size'] for r in results)} 字节")
    print()


def scenario_02_api_testing():
    """场景2: API测试 - 多种HTTP方法"""
    print("\n=== 场景2: API测试 ===")
    
    with httpx.Client(enable_history=True) as client:
        base_url = 'https://httpbin.org'
        
        # 测试用例
        test_cases = [
            ('GET', '/get', None),
            ('POST', '/post', {'name': 'test', 'value': '123'}),
            ('PUT', '/put', {'id': '1', 'update': 'data'}),
            ('DELETE', '/delete', None),
            ('PATCH', '/patch', {'field': 'value'}),
        ]
        
        print("执行API测试...")
        results = []
        for method, path, data in test_cases:
            url = f"{base_url}{path}"
            try:
                if method == 'GET':
                    response = client.get(url)
                elif method == 'POST':
                    response = client.post(url, json=data)
                elif method == 'PUT':
                    response = client.put(url, json=data)
                elif method == 'DELETE':
                    response = client.delete(url)
                elif method == 'PATCH':
                    response = client.patch(url, json=data)
                
                success = response.ok
                results.append((method, success))
                status = "✓" if success else "✗"
                print(f"  {status} {method:6} {path:20} - {response.status_code}")
            except Exception as e:
                results.append((method, False))
                print(f"  ✗ {method:6} {path:20} - {type(e).__name__}")
        
        # 测试报告
        passed = sum(1 for _, success in results if success)
        print(f"\n测试结果: {passed}/{len(results)} 通过")
    print()


def scenario_03_login_session():
    """场景3: 登录会话管理"""
    print("\n=== 场景3: 登录会话管理 ===")
    
    # 步骤1: 登录获取session
    print("步骤1: 执行登录...")
    with httpx.Client() as client:
        # 模拟登录
        login_data = {
            'username': 'demo_user',
            'password': 'demo_pass'
        }
        
        response = client.post('https://httpbin.org/post', json=login_data)
        if response.ok:
            print("  ✓ 登录成功")
            
            # 保存session
            client.save_cookies('examples/output/user_session.json')
            print("  ✓ Session已保存")
    
    # 步骤2: 使用session访问受保护资源
    print("\n步骤2: 使用Session访问...")
    with httpx.Client() as client:
        # 加载session
        client.load_cookies('examples/output/user_session.json')
        
        # 访问用户资料（模拟）
        response = client.get('https://httpbin.org/cookies')
        if response.ok:
            print("  ✓ 访问成功")
            print(f"  Session有效: {bool(response.json().get('cookies'))}")
    
    # 步骤3: 登出
    print("\n步骤3: 登出...")
    with httpx.Client() as client:
        client.load_cookies('examples/output/user_session.json')
        
        # 执行登出
        response = client.post('https://httpbin.org/post', json={'action': 'logout'})
        if response.ok:
            print("  ✓ 登出成功")
    print()


def scenario_04_data_extraction():
    """场景4: 数据提取 - 使用JavaScript"""
    print("\n=== 场景4: 数据提取 ===")
    
    with httpx.Client() as client:
        # 场景: 提取页面中的所有链接
        links = client.execute_script(
            """
            Array.from(document.querySelectorAll('a'))
                .map(a => ({
                    text: a.textContent.trim(),
                    href: a.href
                }))
                .filter(link => link.href)
            """,
            url="https://example.com"
        )
        
        print(f"提取到 {len(links)} 个链接:")
        for i, link in enumerate(links[:5], 1):  # 只显示前5个
            print(f"  {i}. {link['text'][:30]} -> {link['href'][:50]}")
        
        # 提取页面元数据
        metadata = client.execute_script(
            """
            ({
                title: document.title,
                description: document.querySelector('meta[name="description"]')?.content || '',
                keywords: document.querySelector('meta[name="keywords"]')?.content || '',
                h1Count: document.querySelectorAll('h1').length,
                h2Count: document.querySelectorAll('h2').length,
            })
            """,
            url="https://example.com"
        )
        
        print(f"\n页面元数据:")
        print(f"  标题: {metadata['title']}")
        print(f"  H1数量: {metadata['h1Count']}")
        print(f"  H2数量: {metadata['h2Count']}")
    print()


def scenario_05_form_automation():
    """场景5: 表单自动化"""
    print("\n=== 场景5: 表单自动化 ===")
    
    with httpx.Client() as client:
        page = client.get_page()
        
        print("访问表单页面...")
        page.goto('https://httpbin.org/forms/post')
        
        # 自动填写表单
        form_data = {
            'custname': '张三',
            'custtel': '13800138000',
            'custemail': 'zhangsan@example.com',
        }
        
        print("自动填写表单...")
        for field_name, value in form_data.items():
            try:
                page.fill(f'input[name="{field_name}"]', value)
                print(f"  ✓ 填写 {field_name}: {value}")
            except Exception as e:
                print(f"  ○ 跳过 {field_name}: {type(e).__name__}")
        
        print("✓ 表单填写完成")
        page.close()
    print()


def scenario_06_monitoring():
    """场景6: 网站监控"""
    print("\n=== 场景6: 网站监控 ===")
    
    # 监控多个网站的可用性
    sites = [
        ('Example', 'https://example.com'),
        ('HTTPBin', 'https://httpbin.org/get'),
        ('JSONPlaceholder', 'https://jsonplaceholder.typicode.com/posts/1'),
    ]
    
    with httpx.Client(timeout=10.0, enable_history=True) as client:
        print("开始监控...")
        results = []
        
        for name, url in sites:
            try:
                import time
                start = time.time()
                response = client.get(url)
                duration = time.time() - start
                
                status = "在线" if response.ok else "异常"
                results.append({
                    'name': name,
                    'status': status,
                    'code': response.status_code,
                    'time': duration
                })
                
                print(f"  {name:15} - {status} ({response.status_code}) - {duration:.2f}秒")
            except Exception as e:
                results.append({
                    'name': name,
                    'status': '离线',
                    'code': 0,
                    'time': 0
                })
                print(f"  {name:15} - 离线 - {type(e).__name__}")
        
        # 监控报告
        online = sum(1 for r in results if r['status'] == '在线')
        print(f"\n监控报告: {online}/{len(sites)} 个网站在线")
    print()


def scenario_07_batch_processing():
    """场景7: 批量处理 - 性能优化"""
    print("\n=== 场景7: 批量处理 ===")
    
    # 使用同一个客户端处理多个任务，提高性能
    with httpx.Client(
        enable_cache=True,
        rate_limiter=RateLimiter(requests_per_second=5.0)
    ) as client:
        # 批量获取用户数据（模拟）
        user_ids = [1, 2, 3, 4, 5]
        
        print(f"批量处理 {len(user_ids)} 个任务...")
        import time
        start_time = time.time()
        
        for user_id in user_ids:
            # 速率限制
            if client.rate_limiter:
                client.rate_limiter.wait_if_needed()
            
            # 发送请求
            response = client.get(f'https://httpbin.org/get?user_id={user_id}')
            print(f"  处理用户{user_id}: {response.status_code}")
        
        elapsed = time.time() - start_time
        print(f"\n✓ 批量处理完成")
        print(f"  总耗时: {elapsed:.2f}秒")
        print(f"  平均每个: {elapsed/len(user_ids):.2f}秒")
    print()


def scenario_08_screenshot_comparison():
    """场景8: 页面截图对比"""
    print("\n=== 场景8: 页面截图对比 ===")
    
    with httpx.Client(headless=True) as client:
        # 截取同一页面的不同视口
        viewports = [
            ('desktop', {'width': 1920, 'height': 1080}),
            ('tablet', {'width': 768, 'height': 1024}),
            ('mobile', {'width': 375, 'height': 667}),
        ]
        
        print("生成不同视口的截图...")
        for name, viewport in viewports:
            # 直接传递viewport参数给screenshot方法
            screenshot = client.screenshot(
                'https://example.com',
                path=f'examples/output/screenshot_{name}.png',
                viewport=viewport
            )
            
            print(f"  ✓ {name:10} ({viewport['width']}x{viewport['height']}) - {len(screenshot)} 字节")
        
        print(f"\n✓ 截图已保存到 examples/output/")
    print()


def scenario_09_error_recovery():
    """场景9: 错误恢复策略"""
    print("\n=== 场景9: 错误恢复 ===")
    
    retry = RetryPolicy(max_retries=3, backoff_factor=1.0)
    
    with httpx.Client(retry_policy=retry, enable_history=True) as client:
        # 测试URL，包括一些会失败的
        urls = [
            'https://httpbin.org/get',
            'https://httpbin.org/status/500',  # 服务器错误
            'https://httpbin.org/delay/10',    # 会超时
            'https://httpbin.org/status/200',
        ]
        
        print("测试错误恢复...")
        for url in urls:
            try:
                # 设置短超时以快速失败
                response = client.get(url, timeout=2.0)
                print(f"  ✓ {url[:40]}... - {response.status_code}")
            except httpx.TimeoutError:
                print(f"  ⏱ {url[:40]}... - 超时")
            except httpx.HTTPStatusError as e:
                print(f"  ✗ {url[:40]}... - {e.response.status_code}")
            except Exception as e:
                print(f"  ✗ {url[:40]}... - {type(e).__name__}")
        
        # 统计
        stats = client.get_history()
        print(f"\n结果: 成功率 {stats['success_rate']:.1%}")
    print()


def scenario_10_production_crawler():
    """场景10: 生产级爬虫"""
    print("\n=== 场景10: 生产级爬虫 ===")
    
    # 完整的生产配置
    retry = RetryPolicy(max_retries=3, backoff_factor=2.0)
    limiter = RateLimiter(requests_per_second=2.0)
    
    with httpx.Client(
        headless=True,
        enable_history=True,
        enable_cache=True,
        cache_ttl=3600,  # 1小时缓存
        retry_policy=retry,
        rate_limiter=limiter,
        timeout=30.0,
        launch_options={
            'args': [
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
            ]
        },
        context_options={
            'locale': 'zh-CN',
            'timezone_id': 'Asia/Shanghai',
        }
    ) as client:
        print("生产级爬虫配置:")
        print("  ✓ 无头模式")
        print("  ✓ 请求历史和缓存")
        print("  ✓ 自动重试和速率限制")
        print("  ✓ 反检测配置")
        print("  ✓ 中文本地化")
        
        # 执行爬取任务
        print("\n开始爬取...")
        urls = [
            'https://httpbin.org/html',
            'https://httpbin.org/json',
            'https://httpbin.org/xml',
        ]
        
        for i, url in enumerate(urls, 1):
            try:
                if limiter:
                    limiter.wait_if_needed()
                
                response = client.get(url)
                print(f"  [{i}/{len(urls)}] {url} - {response.status_code}")
            except Exception as e:
                print(f"  [{i}/{len(urls)}] {url} - 失败: {type(e).__name__}")
        
        # 保存结果
        client.save_cookies('examples/output/crawler_session.json')
        
        # 最终统计
        stats = client.get_history()
        print(f"\n爬取完成:")
        print(f"  总请求: {stats['total_requests']}")
        print(f"  成功率: {stats['success_rate']:.1%}")
        print(f"  平均耗时: {stats['avg_duration']:.2f}秒")
    print()


def main():
    """运行所有实战场景"""
    print("=" * 60)
    print("Patchright HTTPX - 实战场景示例")
    print("=" * 60)
    
    # 创建输出目录
    import os
    os.makedirs('examples/output', exist_ok=True)
    
    scenario_01_web_scraping()
    scenario_02_api_testing()
    scenario_03_login_session()
    scenario_04_data_extraction()
    scenario_05_form_automation()
    scenario_06_monitoring()
    scenario_07_batch_processing()
    scenario_08_screenshot_comparison()
    scenario_09_error_recovery()
    scenario_10_production_crawler()
    
    print("=" * 60)
    print("✓ 所有实战场景示例运行完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()

