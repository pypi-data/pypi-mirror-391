"""
浏览器配置示例

演示如何配置不同的浏览器类型和参数
"""

import patchright_httpx as httpx


def example_01_chromium():
    """示例1: 使用Chromium (默认)"""
    print("\n=== 示例1: Chromium浏览器 ===")
    
    with httpx.Client(browser_type="chromium") as client:
        response = client.get('https://httpbin.org/get')
        print(f"  状态码: {response.status_code}")
        print(f"  浏览器: Chromium")
        user_agent = response.json()['headers'].get('User-Agent', '')
        print(f"  User-Agent: {user_agent[:50]}...")
    print()


def example_02_firefox():
    """示例2: 使用Firefox"""
    print("\n=== 示例2: Firefox浏览器 ===")
    
    with httpx.Client(browser_type="firefox") as client:
        response = client.get('https://httpbin.org/get')
        print(f"  状态码: {response.status_code}")
        print(f"  浏览器: Firefox")
        user_agent = response.json()['headers'].get('User-Agent', '')
        print(f"  User-Agent: {user_agent[:50]}...")
    print()


def example_03_webkit():
    """示例3: 使用WebKit (Safari内核)"""
    print("\n=== 示例3: WebKit浏览器 ===")
    
    with httpx.Client(browser_type="webkit") as client:
        response = client.get('https://httpbin.org/get')
        print(f"  状态码: {response.status_code}")
        print(f"  浏览器: WebKit")
        user_agent = response.json()['headers'].get('User-Agent', '')
        print(f"  User-Agent: {user_agent[:50]}...")
    print()


def example_04_full_configuration():
    """示例4: 完整配置"""
    print("\n=== 示例4: 完整配置 ===")
    
    with httpx.Client(
        # 浏览器配置
        browser_type="chromium",
        headless=True,
        viewport={'width': 1920, 'height': 1080},
        
        # 网络配置
        timeout=30.0,
        base_url="https://httpbin.org",
        
        # 高级配置
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
        response = client.get('/get')
        print(f"  状态码: {response.status_code}")
        print(f"  配置:")
        print(f"    - 浏览器: Chromium")
        print(f"    - 无头模式: True")
        print(f"    - 视口: 1920x1080")
        print(f"    - 语言: zh-CN")
        print(f"    - 时区: Asia/Shanghai")
    print()


def example_05_headless_vs_headed():
    """示例5: 无头模式 vs 有头模式"""
    print("\n=== 示例5: 无头模式对比 ===")
    
    # 无头模式 (不显示浏览器窗口)
    print("  测试无头模式...")
    with httpx.Client(headless=True) as client:
        response = client.get('https://httpbin.org/get')
        print(f"    无头模式: 状态码 {response.status_code}")
    
    # 有头模式 (显示浏览器窗口) - 取消注释以测试
    # print("  测试有头模式...")
    # with httpx.Client(headless=False) as client:
    #     response = client.get('https://httpbin.org/get')
    #     print(f"    有头模式: 状态码 {response.status_code}")
    
    print()


def example_06_custom_user_agent():
    """示例6: 自定义User-Agent"""
    print("\n=== 示例6: 自定义User-Agent ===")
    
    custom_ua = "MyCustomBot/1.0 (白岚的爬虫)"
    
    with httpx.Client(user_agent=custom_ua) as client:
        response = client.get('https://httpbin.org/get')
        received_ua = response.json()['headers'].get('User-Agent', '')
        print(f"  设置的UA: {custom_ua}")
        print(f"  收到的UA: {received_ua}")
        print(f"  匹配: {custom_ua == received_ua}")
    print()


def example_07_viewport_configuration():
    """示例7: 视口配置"""
    print("\n=== 示例7: 不同视口大小 ===")
    
    viewports = [
        ('桌面', {'width': 1920, 'height': 1080}),
        ('平板', {'width': 768, 'height': 1024}),
        ('手机', {'width': 375, 'height': 667}),
    ]
    
    for name, viewport in viewports:
        with httpx.Client(viewport=viewport) as client:
            # 执行JavaScript获取窗口大小
            result = client.execute_script(
                """
                return {
                    width: window.innerWidth,
                    height: window.innerHeight
                }
                """,
                url="https://httpbin.org/get"
            )
            print(f"  {name}: 设置 {viewport['width']}x{viewport['height']}")
            print(f"       实际 {result['width']}x{result['height']}")
    print()


def example_08_launch_options():
    """示例8: 浏览器启动参数"""
    print("\n=== 示例8: 自定义启动参数 ===")
    
    with httpx.Client(
        launch_options={
            'args': [
                '--disable-blink-features=AutomationControlled',  # 禁用自动化检测
                '--disable-web-security',                         # 禁用跨域限制
                '--disable-features=IsolateOrigins,site-per-process',
                '--no-sandbox',                                   # 无沙盒模式
            ]
        }
    ) as client:
        response = client.get('https://httpbin.org/get')
        print(f"  状态码: {response.status_code}")
        print(f"  启动参数:")
        print(f"    - 禁用自动化检测")
        print(f"    - 禁用Web安全")
        print(f"    - 无沙盒模式")
    print()


def example_09_context_options():
    """示例9: 上下文选项"""
    print("\n=== 示例9: 浏览器上下文配置 ===")
    
    with httpx.Client(
        context_options={
            'locale': 'zh-CN',                    # 语言
            'timezone_id': 'Asia/Shanghai',        # 时区
            'geolocation': {                       # 地理位置
                'latitude': 39.9042,
                'longitude': 116.4074
            },
            'permissions': ['geolocation'],        # 权限
        }
    ) as client:
        response = client.get('https://httpbin.org/get')
        print(f"  状态码: {response.status_code}")
        print(f"  上下文配置:")
        print(f"    - 语言: zh-CN")
        print(f"    - 时区: Asia/Shanghai")
        print(f"    - 位置: 北京 (39.9042, 116.4074)")
    print()


def example_10_comparison():
    """示例10: 三种浏览器对比"""
    print("\n=== 示例10: 三种浏览器对比 ===")
    
    browsers = ['chromium', 'firefox', 'webkit']
    
    print("  浏览器性能对比:")
    for browser in browsers:
        import time
        start = time.time()
        
        try:
            with httpx.Client(browser_type=browser, headless=True) as client:
                response = client.get('https://httpbin.org/get')
                elapsed = time.time() - start
                
                print(f"    {browser:10} - 状态码: {response.status_code}, 耗时: {elapsed:.2f}秒")
        except Exception as e:
            print(f"    {browser:10} - 错误: {type(e).__name__}")
    print()


def main():
    """运行所有示例"""
    print("=" * 60)
    print("Patchright HTTPX - 浏览器配置示例")
    print("=" * 60)
    
    try:
        example_01_chromium()
        example_02_firefox()
        example_03_webkit()
        example_04_full_configuration()
        example_05_headless_vs_headed()
        example_06_custom_user_agent()
        example_07_viewport_configuration()
        example_08_launch_options()
        example_09_context_options()
        example_10_comparison()
        
        print("=" * 60)
        print("✓ 所有浏览器配置示例运行完成！")
        print("=" * 60)
    except KeyboardInterrupt:
        print("\n\n示例被用户中断")
    except Exception as e:
        print(f"\n\n运行示例时出错: {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()

