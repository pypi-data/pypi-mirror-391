"""工具函数"""

import io
import uuid
from typing import Dict, Any, Optional, Union, Tuple
from urllib.parse import urlencode, urlparse, urlunparse, parse_qs, urljoin


def build_url(url: str, params: Optional[Dict[str, Any]] = None) -> str:
    """构建完整的 URL（包含查询参数）
    
    Args:
        url: 基础 URL
        params: 查询参数字典
        
    Returns:
        完整的 URL 字符串
    """
    if not params:
        return url
    
    parsed = urlparse(url)
    query_dict = parse_qs(parsed.query)
    
    # 合并现有参数和新参数
    for key, value in params.items():
        query_dict[key] = [str(value)]
    
    # 重新构建查询字符串
    query_string = urlencode(query_dict, doseq=True)
    
    return urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        query_string,
        parsed.fragment
    ))


def merge_headers(
    default_headers: Optional[Dict[str, str]] = None,
    custom_headers: Optional[Dict[str, str]] = None,
) -> Dict[str, str]:
    """合并请求头
    
    Args:
        default_headers: 默认请求头
        custom_headers: 自定义请求头
        
    Returns:
        合并后的请求头字典
    """
    headers = {}
    if default_headers:
        headers.update(default_headers)
    if custom_headers:
        headers.update(custom_headers)
    return headers


def format_auth_header(username: str, password: str) -> str:
    """生成基本认证的 Authorization 头
    
    Args:
        username: 用户名
        password: 密码
        
    Returns:
        Basic Auth 字符串
    """
    import base64
    credentials = f"{username}:{password}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded}"


def merge_url(base_url: Optional[str], url: str) -> str:
    """合并 base_url 和相对 URL
    
    Args:
        base_url: 基础 URL
        url: 相对或绝对 URL
        
    Returns:
        完整的 URL
        
    Example:
        >>> merge_url('https://api.example.com', '/users')
        'https://api.example.com/users'
        >>> merge_url('https://api.example.com', 'https://other.com')
        'https://other.com'
    """
    if not base_url:
        return url
    
    # 如果 url 已经是完整 URL，直接返回
    if url.startswith(('http://', 'https://')):
        return url
    
    # 合并 base_url 和相对路径
    return urljoin(base_url + '/', url.lstrip('/'))


def build_multipart_data(
    data: Optional[Dict[str, Any]] = None,
    files: Optional[Dict[str, Union[str, Tuple[str, bytes], Tuple[str, bytes, str]]]] = None,
) -> Tuple[bytes, str]:
    """构造 multipart/form-data 请求体
    
    Args:
        data: 表单字段数据
        files: 文件数据，格式:
            - {'field': 'path/to/file'}  # 文件路径
            - {'field': ('filename', b'content')}  # 文件名和内容
            - {'field': ('filename', b'content', 'content-type')}  # 完整格式
    
    Returns:
        (请求体字节, Content-Type头值)
        
    Example:
        >>> body, content_type = build_multipart_data(
        ...     data={'name': 'test'},
        ...     files={'file': ('test.txt', b'hello', 'text/plain')}
        ... )
    """
    boundary = f'----WebKitFormBoundary{uuid.uuid4().hex[:16]}'
    parts = []
    
    # 添加普通表单字段
    if data:
        for name, value in data.items():
            parts.append(f'--{boundary}'.encode())
            parts.append(f'Content-Disposition: form-data; name="{name}"'.encode())
            parts.append(b'')
            parts.append(str(value).encode('utf-8'))
    
    # 添加文件字段
    if files:
        for field_name, file_info in files.items():
            parts.append(f'--{boundary}'.encode())
            
            # 解析文件信息
            if isinstance(file_info, str):
                # 文件路径 - 读取文件
                with open(file_info, 'rb') as f:
                    file_content = f.read()
                filename = file_info.split('/')[-1].split('\\')[-1]
                content_type = 'application/octet-stream'
            elif isinstance(file_info, tuple):
                if len(file_info) == 2:
                    filename, file_content = file_info
                    content_type = 'application/octet-stream'
                else:
                    filename, file_content, content_type = file_info
            else:
                raise ValueError(f"Invalid file format for field '{field_name}'")
            
            # 构造文件字段头
            parts.append(
                f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"'.encode()
            )
            parts.append(f'Content-Type: {content_type}'.encode())
            parts.append(b'')
            parts.append(file_content if isinstance(file_content, bytes) else file_content.encode())
    
    # 结束边界
    parts.append(f'--{boundary}--'.encode())
    parts.append(b'')
    
    # 组合所有部分
    body = b'\r\n'.join(parts)
    content_type_header = f'multipart/form-data; boundary={boundary}'
    
    return body, content_type_header

