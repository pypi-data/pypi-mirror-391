"""
Patchright HTTPX - 基础功能示例

演示最常用的HTTP请求功能，适合快速上手。
"""

import patchright_httpx as httpx


def example_01_simple_get():
    """示例1: 最简单的GET请求"""
    print("\n=== 示例1: 简单GET请求 ===")
    
    response = httpx.get('https://httpbin.org/get')
    
    print(f"状态码: {response.status_code}")
    print(f"响应头: {response.headers.get('content-type')}")
    print(f"响应成功: {response.ok}")
    print()


def example_02_get_with_params():
    """示例2: GET请求带查询参数"""
    print("\n=== 示例2: GET请求带查询参数 ===")
    
    params = {
        'name': '白岚',
        'age': '18',
        'skill': 'coding'
    }
    
    response = httpx.get('https://httpbin.org/get', params=params)
    data = response.json()
    
    print(f"请求URL: {data['url']}")
    print(f"查询参数: {data['args']}")
    print()


def example_03_post_json():
    """示例3: POST请求发送JSON数据"""
    print("\n=== 示例3: POST发送JSON ===")
    
    payload = {
        'username': '白岚',
        'action': '重构代码',
        'status': '完成'
    }
    
    response = httpx.post('https://httpbin.org/post', json=payload)
    data = response.json()
    
    print(f"状态码: {response.status_code}")
    print(f"服务器收到的JSON: {data['json']}")
    print()


def example_04_post_form():
    """示例4: POST请求发送表单数据"""
    print("\n=== 示例4: POST发送表单 ===")
    
    form_data = {
        'username': 'admin',
        'password': 'secret123'
    }
    
    response = httpx.post('https://httpbin.org/post', data=form_data)
    data = response.json()
    
    print(f"状态码: {response.status_code}")
    print(f"Content-Type: {data['headers']['Content-Type']}")
    print(f"表单数据: {data['form']}")
    print()


def example_05_custom_headers():
    """示例5: 自定义请求头"""
    print("\n=== 示例5: 自定义请求头 ===")
    
    headers = {
        'User-Agent': 'Patchright-HTTPX/1.0',
        'X-Custom-Header': 'Hello from 白岚'
    }
    
    response = httpx.get('https://httpbin.org/headers', headers=headers)
    data = response.json()
    
    print(f"状态码: {response.status_code}")
    print(f"User-Agent: {data['headers'].get('User-Agent')}")
    print(f"自定义头: {data['headers'].get('X-Custom-Header')}")
    print()


def example_06_basic_auth():
    """示例6: 基本认证"""
    print("\n=== 示例6: 基本认证 ===")
    
    response = httpx.get(
        'https://httpbin.org/basic-auth/user/pass',
        auth=('user', 'pass')
    )
    
    print(f"状态码: {response.status_code}")
    print(f"认证成功: {response.ok}")
    
    # 安全地解析JSON
    try:
        data = response.json()
        print(f"响应: {data}")
    except Exception as e:
        print(f"JSON解析失败: {type(e).__name__}")
        print(f"响应文本: {response.text[:200]}")
    
    print()


def example_07_timeout():
    """示例7: 设置超时"""
    print("\n=== 示例7: 设置超时 ===")
    
    try:
        # 设置1秒超时，访问一个故意延迟的端点
        response = httpx.get('https://httpbin.org/delay/5', timeout=1.0)
        print(f"状态码: {response.status_code}")
    except httpx.TimeoutError as e:
        print(f"✓ 请求超时(符合预期): {e}")
    print()


def example_08_response_parsing():
    """示例8: 响应解析"""
    print("\n=== 示例8: 响应解析 ===")
    
    response = httpx.get('https://httpbin.org/json')
    
    # 多种方式访问响应
    print(f"原始字节(前50): {response.content[:50]}")
    print(f"文本(前50): {response.text[:50]}")
    print(f"JSON: {response.json()}")
    print()


def example_09_with_context():
    """示例9: 使用上下文管理器"""
    print("\n=== 示例9: 使用上下文管理器 ===")
    
    with httpx.Client() as client:
        # 可以发送多个请求，共享同一个浏览器实例
        response1 = client.get('https://httpbin.org/get')
        response2 = client.get('https://httpbin.org/user-agent')
        
        print(f"第1个请求状态: {response1.status_code}")
        print(f"第2个请求状态: {response2.status_code}")
    # 退出with块时自动关闭浏览器
    print("✓ 浏览器已自动关闭")
    print()


def example_10_client_reuse():
    """示例10: 客户端复用(提高性能)"""
    print("\n=== 示例10: 客户端复用 ===")
    
    # 创建可复用的客户端
    with httpx.Client(headers={'X-Custom': 'Default-Header'}) as client:
        urls = [
            'https://httpbin.org/get',
            'https://httpbin.org/user-agent',
            'https://httpbin.org/headers',
        ]
        
        for i, url in enumerate(urls, 1):
            response = client.get(url)
            print(f"请求{i}: {response.status_code} - {url}")
    
    print("✓ 3个请求共享同一浏览器，性能更好")
    print()


def main():
    """运行所有基础示例"""
    print("=" * 60)
    print("Patchright HTTPX - 基础功能示例")
    print("=" * 60)
    
    example_01_simple_get()
    example_02_get_with_params()
    example_03_post_json()
    example_04_post_form()
    example_05_custom_headers()
    example_06_basic_auth()
    example_07_timeout()
    example_08_response_parsing()
    example_09_with_context()
    example_10_client_reuse()
    
    print("=" * 60)
    print("✓ 所有基础示例运行完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()

