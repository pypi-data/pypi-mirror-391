"""类型定义"""

from typing import Dict, Any, Union, Optional, Tuple

# 基础类型
Headers = Dict[str, str]
Cookies = Dict[str, str]
Params = Dict[str, Any]
Data = Dict[str, Any]
JsonData = Dict[str, Any]
Files = Dict[str, Union[str, Tuple[str, bytes, str]]]

# 认证类型
Auth = Optional[Tuple[str, str]]

# 浏览器类型
BrowserType = str  # 'chromium', 'firefox', 'webkit'


