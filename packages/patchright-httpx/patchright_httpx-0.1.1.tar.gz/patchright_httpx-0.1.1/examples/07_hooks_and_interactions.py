"""
事件钩子和页面交互示例

演示如何使用event_hooks进行请求/响应拦截，
以及如何使用get_page()进行复杂的页面交互
"""

import time
import patchright_httpx as httpx


# ==================== 事件钩子示例 ====================

def example_01_basic_hooks():
    """示例1: 基础事件钩子"""
    print("\n=== 示例1: 基础事件钩子 ===")
    
    # 定义钩子函数
    def on_request(request):
        print(f"  [Request] {request['method']} {request['url']}")
    
    def on_response(response):
        print(f"  [Response] {response.status_code} - {len(response.content)} bytes")
    
    with httpx.Client(
        event_hooks={
            'request': [on_request],
            'response': [on_response]
        }
    ) as client:
        print("发送请求...")
        client.get('https://httpbin.org/get')
        print("✓ 完成")
    print()


def example_02_request_logging():
    """示例2: 请求日志记录"""
    print("\n=== 示例2: 请求日志记录 ===")
    
    request_log = []
    
    def log_request(request):
        request_log.append({
            'time': time.time(),
            'method': request['method'],
            'url': request['url'],
        })
    
    def log_response(response):
        request_log[-1]['status'] = response.status_code
        request_log[-1]['elapsed'] = response.elapsed
    
    with httpx.Client(
        event_hooks={
            'request': [log_request],
            'response': [log_response]
        }
    ) as client:
        # 发送多个请求
        client.get('https://httpbin.org/get')
        client.post('https://httpbin.org/post', json={'test': 'data'})
        client.get('https://httpbin.org/status/404')
    
    # 打印日志
    print("  请求日志:")
    for i, log in enumerate(request_log, 1):
        print(f"    {i}. {log['method']:6} {log.get('status', '???'):3} - {log['url'][:40]}...")
    print()


def example_03_request_modification():
    """示例3: 请求修改"""
    print("\n=== 示例3: 在钩子中修改请求 ===")
    
    def add_custom_header(request):
        # 注意: 这里只是演示概念,实际headers已经被合并
        print(f"  添加自定义头: X-Request-ID")
    
    def check_response(response):
        # 在响应钩子中可以检查和处理响应
        if response.status_code >= 400:
            print(f"  ⚠ 检测到错误响应: {response.status_code}")
        else:
            print(f"  ✓ 请求成功: {response.status_code}")
    
    with httpx.Client(
        event_hooks={
            'request': [add_custom_header],
            'response': [check_response]
        }
    ) as client:
        client.get('https://httpbin.org/get')
        client.get('https://httpbin.org/status/500')
    print()


def example_04_multiple_hooks():
    """示例4: 多个钩子函数"""
    print("\n=== 示例4: 多个钩子函数 ===")
    
    def hook1(request):
        print(f"  [Hook 1] 准备请求: {request['url'][:30]}...")
    
    def hook2(request):
        print(f"  [Hook 2] 验证请求参数...")
    
    def hook3(request):
        print(f"  [Hook 3] 记录请求到数据库...")
    
    with httpx.Client(
        event_hooks={
            'request': [hook1, hook2, hook3],  # 按顺序执行
        }
    ) as client:
        client.get('https://httpbin.org/get')
    print()


def example_05_error_tracking():
    """示例5: 错误追踪"""
    print("\n=== 示例5: 错误追踪 ===")
    
    error_count = {'count': 0}
    
    def track_errors(response):
        if response.status_code >= 400:
            error_count['count'] += 1
            print(f"  ❌ 错误 #{error_count['count']}: {response.status_code} - {response.url}")
    
    with httpx.Client(
        event_hooks={'response': [track_errors]}
    ) as client:
        urls = [
            'https://httpbin.org/get',
            'https://httpbin.org/status/404',
            'https://httpbin.org/status/500',
            'https://httpbin.org/get',
        ]
        
        for url in urls:
            try:
                client.get(url)
            except Exception:
                pass
    
    print(f"\n  总错误数: {error_count['count']}")
    print()


# ==================== 页面交互示例 ====================

def example_06_page_click():
    """示例6: 页面点击操作"""
    print("\n=== 示例6: 页面点击操作 ===")
    
    with httpx.Client() as client:
        print("  获取页面对象...")
        page = client.get_page()
        
        # 访问页面
        print("  访问页面...")
        page.goto('https://httpbin.org/forms/post')
        
        # 填写表单
        print("  填写表单...")
        page.fill('input[name="custname"]', '白岚')
        page.fill('input[name="custtel"]', '13800138000')
        
        # 点击提交按钮 (这个页面没有提交按钮，仅演示)
        # page.click('button[type="submit"]')
        
        print("  ✓ 操作完成")
        page.close()
    print()


def example_07_complex_interaction():
    """示例7: 复杂页面交互"""
    print("\n=== 示例7: 复杂页面交互 ===")
    
    with httpx.Client() as client:
        page = client.get_page()
        
        # 访问页面
        print("  访问页面...")
        page.goto('https://example.com')
        
        # 等待元素出现
        print("  等待元素加载...")
        page.wait_for_selector('h1')
        
        # 获取元素文本
        title = page.text_content('h1')
        print(f"  页面标题: {title}")
        
        # 执行JavaScript
        print("  执行JavaScript...")
        result = page.evaluate('() => document.title')
        print(f"  文档标题: {result}")
        
        # 截图
        print("  截图...")
        page.screenshot(path='examples/output/interaction.png')
        
        page.close()
        print("  ✓ 完成")
    print()


def example_08_form_automation():
    """示例8: 表单自动化"""
    print("\n=== 示例8: 表单自动化 ===")
    
    with httpx.Client() as client:
        page = client.get_page()
        
        print("  访问表单页面...")
        page.goto('https://httpbin.org/forms/post')
        
        # 自动填写所有字段
        form_data = {
            'custname': '张三',
            'custtel': '13800138000',
            'custemail': 'zhangsan@example.com',
            'size': 'medium',
        }
        
        print("  自动填写表单...")
        for field, value in form_data.items():
            try:
                selector = f'input[name="{field}"], select[name="{field}"]'
                if page.query_selector(f'select[name="{field}"]'):
                    # 下拉框
                    page.select_option(f'select[name="{field}"]', value)
                else:
                    # 输入框
                    page.fill(f'input[name="{field}"]', value)
                print(f"    ✓ {field}: {value}")
            except Exception as e:
                print(f"    ✗ {field}: 跳过 ({type(e).__name__})")
        
        page.close()
        print("  ✓ 完成")
    print()


def example_09_wait_for_navigation():
    """示例9: 等待页面导航"""
    print("\n=== 示例9: 等待页面导航 ===")
    
    with httpx.Client() as client:
        page = client.get_page()
        
        print("  访问初始页面...")
        page.goto('https://httpbin.org/html')
        
        # 点击链接并等待导航
        # (这个页面没有导航链接，仅演示概念)
        print("  页面操作演示...")
        print(f"  当前URL: {page.url}")
        
        # 等待特定条件
        page.wait_for_load_state('networkidle')
        print("  ✓ 页面加载完成")
        
        page.close()
    print()


def example_10_combined_usage():
    """示例10: 组合使用 - 钩子 + 页面交互"""
    print("\n=== 示例10: 组合使用 ===")
    
    # 定义钩子
    def log_request(request):
        print(f"  [Hook] 发送请求: {request['url'][:40]}...")
    
    def log_response(response):
        print(f"  [Hook] 收到响应: {response.status_code}")
    
    with httpx.Client(
        event_hooks={
            'request': [log_request],
            'response': [log_response]
        }
    ) as client:
        # 先用httpx接口发送请求
        print("阶段1: 使用httpx接口")
        response = client.get('https://httpbin.org/get')
        print(f"  数据: {list(response.json().keys())}")
        
        # 再用页面交互做复杂操作
        print("\n阶段2: 使用页面交互")
        page = client.get_page()
        page.goto('https://example.com')
        title = page.text_content('h1')
        print(f"  [Page] 页面标题: {title}")
        page.close()
        
        print("\n✓ 组合使用完成")
    print()


def main():
    """运行所有示例"""
    print("=" * 60)
    print("Patchright HTTPX - 事件钩子和页面交互示例")
    print("=" * 60)
    
    try:
        # 事件钩子示例
        example_01_basic_hooks()
        example_02_request_logging()
        example_03_request_modification()
        example_04_multiple_hooks()
        example_05_error_tracking()
        
        # 页面交互示例
        example_06_page_click()
        example_07_complex_interaction()
        example_08_form_automation()
        example_09_wait_for_navigation()
        example_10_combined_usage()
        
        print("=" * 60)
        print("✓ 所有示例运行完成！")
        print("=" * 60)
    except KeyboardInterrupt:
        print("\n\n示例被用户中断")
    except Exception as e:
        print(f"\n\n运行示例时出错: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

