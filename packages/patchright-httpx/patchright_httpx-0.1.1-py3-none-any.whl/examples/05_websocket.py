"""
Patchright HTTPX - WebSocket示例

演示WebSocket连接和实时通信功能。
"""

import time
import json
import patchright_httpx as httpx


def example_01_basic_websocket():
    """示例1: 基础WebSocket连接"""
    print("\n=== 示例1: 基础WebSocket连接 ===")
    
    with httpx.Client() as client:
        print("连接到 WebSocket Echo 服务器...")
        
        # 创建WebSocket连接
        ws = client.websocket_connect('wss://echo.websocket.org')
        
        # 发送消息
        message = "Hello from 白岚!"
        ws.send_text(message)
        print(f"  发送: {message}")
        
        # 接收消息(echo服务器会回显)
        response = ws.receive_text()
        print(f"  接收: {response}")
        
        # 关闭连接
        ws.close()
        print("  ✓ 连接已关闭")
    print()


def example_02_json_messaging():
    """示例2: JSON消息传递"""
    print("\n=== 示例2: JSON消息传递 ===")
    
    with httpx.Client() as client:
        print("连接到WebSocket服务器...")
        ws = client.websocket_connect('wss://echo.websocket.org')
        
        # 发送JSON消息
        json_data = {
            'type': 'greeting',
            'from': '白岚',
            'message': 'Hello WebSocket!',
            'timestamp': time.time()
        }
        
        ws.send_json(json_data)
        print(f"  发送JSON: {json_data}")
        
        # 接收响应
        response = ws.receive_text()
        print(f"  收到响应: {response[:100]}")
        print(f"  注意: echo.websocket.org返回的是服务器信息，不是原JSON数据")
        
        ws.close()
        print("  ✓ 连接已关闭")
    print()


def example_03_multiple_messages():
    """示例3: 发送多条消息"""
    print("\n=== 示例3: 发送多条消息 ===")
    
    with httpx.Client() as client:
        print("连接到WebSocket服务器...")
        ws = client.websocket_connect('wss://echo.websocket.org')
        
        # 发送多条消息
        messages = ["消息1", "消息2", "消息3"]
        for i, msg in enumerate(messages, 1):
            ws.send_text(msg)
            print(f"  发送第{i}条: {msg}")
            time.sleep(0.3)
        
        # 接收所有响应
        print("  接收响应...")
        for i in range(len(messages)):
            try:
                response = ws.receive_text(timeout=2.0)
                print(f"  收到第{i+1}条: {response}")
            except Exception as e:
                print(f"  第{i+1}条接收超时")
        
        ws.close()
        print("  ✓ 连接已关闭")
    print()


def example_04_with_callbacks():
    """示例4: 使用回调函数"""
    print("\n=== 示例4: 使用回调函数 ===")
    
    message_count = {'count': 0}
    
    def on_message(msg):
        message_count['count'] += 1
        print(f"  [回调] 收到消息{message_count['count']}: {msg[:50]}")
    
    def on_close():
        print("  [回调] 连接已关闭")
    
    with httpx.Client() as client:
        print("连接到WebSocket服务器...")
        
        ws = client.websocket_connect(
            'wss://echo.websocket.org',
            on_message=on_message,
            on_close=on_close
        )
        
        # 发送消息
        ws.send_text("测试回调1")
        ws.send_text("测试回调2")
        
        # 等待消息处理
        print("  等待消息处理...")
        time.sleep(2)
        
        ws.close()
    print()


def example_05_error_handling():
    """示例5: 错误处理"""
    print("\n=== 示例5: 错误处理 ===")
    
    with httpx.Client() as client:
        try:
            print("测试连接超时...")
            # 使用一个不存在的服务器测试超时
            ws = client.websocket_connect(
                'wss://invalid-websocket-server-that-does-not-exist.example.com',
                timeout=2.0
            )
        except Exception as e:
            print(f"  ✓ 正确捕获错误: {type(e).__name__}")
            print(f"  错误信息: {str(e)[:100]}")
    print()


def example_06_context_manager():
    """示例6: 使用上下文管理器"""
    print("\n=== 示例6: 使用上下文管理器 ===")
    
    with httpx.Client() as client:
        print("使用with语句自动管理连接...")
        
        # WebSocketConnection支持with语句
        with client.websocket_connect('wss://echo.websocket.org') as ws:
            ws.send_text("Hello from context manager!")
            response = ws.receive_text()
            print(f"  收到: {response}")
            print("  ✓ 退出with时自动关闭")
    print()


def main():
    """运行所有示例"""
    print("=" * 60)
    print("Patchright HTTPX - WebSocket示例")
    print("=" * 60)
    print()
    print("注意: 这些示例需要连接到真实的WebSocket服务器")
    print("如果服务器不可用,某些示例可能会失败")
    print()
    
    try:
        example_01_basic_websocket()
        example_02_json_messaging()
        example_03_multiple_messages()
        example_04_with_callbacks()
        example_05_error_handling()
        example_06_context_manager()
        
        print("=" * 60)
        print("✓ 所有WebSocket示例运行完成！")
        print("=" * 60)
    except KeyboardInterrupt:
        print("\n\n示例被用户中断")
    except Exception as e:
        print(f"\n\n运行示例时出错: {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
