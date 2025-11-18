"""
Patchright HTTPX - 高级功能示例

演示浏览器配置、JavaScript执行、截图等高级功能。
"""

import asyncio
import patchright_httpx as httpx


def example_01_browser_config():
    """示例1: 自定义浏览器配置"""
    print("\n=== 示例1: 自定义浏览器配置 ===")
    
    with httpx.Client(
        headless=True,
        launch_options={
            'args': [
                '--disable-blink-features=AutomationControlled',  # 隐藏自动化特征
            ]
        },
        context_options={
            'locale': 'zh-CN',
            'timezone_id': 'Asia/Shanghai',
        }
    ) as client:
        response = client.get('https://httpbin.org/headers')
        data = response.json()
        
        print(f"语言设置: {data['headers'].get('Accept-Language', 'N/A')}")
        print("✓ 浏览器配置成功")
    print()


def example_02_custom_user_agent():
    """示例2: 自定义User-Agent"""
    print("\n=== 示例2: 自定义User-Agent ===")
    
    mobile_ua = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
    
    with httpx.Client(user_agent=mobile_ua) as client:
        response = client.get('https://httpbin.org/user-agent')
        data = response.json()
        
        print(f"User-Agent: {data['user-agent'][:50]}...")
        print("✓ 模拟移动设备成功")
    print()


def example_03_execute_javascript():
    """示例3: 执行JavaScript"""
    print("\n=== 示例3: 执行JavaScript ===")
    
    with httpx.Client() as client:
        # 获取页面标题
        title = client.execute_script(
            "document.title",
            url="https://example.com"
        )
        print(f"页面标题: {title}")
        
        # 执行复杂脚本
        page_info = client.execute_script(
            """
            ({
                url: window.location.href,
                width: window.innerWidth,
                height: window.innerHeight
            })
            """,
            url="https://example.com"
        )
        print(f"页面信息: {page_info}")
    print()


def example_04_screenshot():
    """示例4: 页面截图"""
    print("\n=== 示例4: 页面截图 ===")
    
    with httpx.Client(headless=True) as client:
        screenshot = client.screenshot(
            'https://example.com',
            path='examples/output/screenshot.png',
            full_page=True
        )
        print(f"✓ 截图已保存，大小: {len(screenshot)} 字节")
    print()


def example_05_native_page_api():
    """示例5: 使用原生Playwright API"""
    print("\n=== 示例5: 使用原生Playwright API ===")
    
    with httpx.Client() as client:
        page = client.get_page()
        
        # 访问页面
        page.goto('https://example.com')
        
        # 等待元素
        page.wait_for_selector('h1')
        
        # 获取元素文本
        h1_text = page.locator('h1').text_content()
        print(f"H1标题: {h1_text}")
        
        # 获取当前URL
        print(f"当前URL: {page.url}")
        
        page.close()
    print()


def example_06_multiple_pages():
    """示例6: 同时操作多个页面"""
    print("\n=== 示例6: 同时操作多个页面 ===")
    
    with httpx.Client() as client:
        # 创建两个页面
        page1 = client.get_page()
        page2 = client.get_page()
        
        # 同时访问不同URL
        page1.goto('https://httpbin.org/delay/1')
        page2.goto('https://example.com')
        
        print(f"页面1标题: {page1.title()}")
        print(f"页面2标题: {page2.title()}")
        
        page1.close()
        page2.close()
    print()


def example_07_pdf_generation():
    """示例7: 生成PDF"""
    print("\n=== 示例7: 生成PDF ===")
    
    with httpx.Client(headless=True) as client:
        page = client.get_page()
        page.goto('https://example.com')
        
        page.pdf(path='examples/output/page.pdf')
        print("✓ PDF已生成: examples/output/page.pdf")
        
        page.close()
    print()


def example_08_proxy_usage():
    """示例8: 使用代理"""
    print("\n=== 示例8: 使用代理(演示配置) ===")
    
    # 注意: 需要实际可用的代理地址
    proxy = httpx.Proxy(
        server="http://proxy.example.com:8080",
        username="user",  # 可选
        password="pass"   # 可选
    )
    
    print("代理配置示例:")
    print(f"  服务器: {proxy.server}")
    print("  (需要实际可用的代理才能运行)")
    print()


def example_09_viewport_size():
    """示例9: 自定义视口大小"""
    print("\n=== 示例9: 自定义视口大小 ===")
    
    with httpx.Client(viewport={'width': 1920, 'height': 1080}) as client:
        info = client.execute_script(
            """
            ({
                width: window.innerWidth,
                height: window.innerHeight
            })
            """,
            url="https://example.com"
        )
        print(f"视口大小: {info['width']}x{info['height']}")
    print()


async def example_10_async_operations():
    """示例10: 异步操作"""
    print("\n=== 示例10: 异步操作 ===")
    
    async with httpx.AsyncClient() as client:
        # 异步发送请求
        response = await client.get('https://httpbin.org/get')
        print(f"异步请求状态: {response.status_code}")
        
        # 异步执行JavaScript
        title = await client.execute_script(
            "document.title",
            url="https://example.com"
        )
        print(f"异步获取标题: {title}")
    print()


def main():
    """运行所有高级示例"""
    print("=" * 60)
    print("Patchright HTTPX - 高级功能示例")
    print("=" * 60)
    
    example_01_browser_config()
    example_02_custom_user_agent()
    example_03_execute_javascript()
    example_04_screenshot()
    example_05_native_page_api()
    example_06_multiple_pages()
    example_07_pdf_generation()
    example_08_proxy_usage()
    example_09_viewport_size()
    
    # 运行异步示例
    print("\n--- 异步示例 ---")
    asyncio.run(example_10_async_operations())
    
    print("=" * 60)
    print("✓ 所有高级示例运行完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()

