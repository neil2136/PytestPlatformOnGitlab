import requests
from typing import Dict, Any, Optional
from src.core.utils.logger import Logger


class APIClient:
    """通用 API 客户端"""
    
    def __init__(self, base_url: str, timeout: int = 30, logger: Logger = None):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.verify = False  # 生产环境应使用有效证书
        self.logger = logger or Logger()
        self.token: Optional[str] = None
    
    def set_token(self, token: str):
        """设置认证 Token"""
        self.token = token
        self.session.headers.update({"Authorization": f"Bearer {token}"})
    
    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """通用请求方法"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        self.logger.info(f"{method} {url}")
        
        response = self.session.request(
            method, url, verify=False, timeout=self.timeout, **kwargs
        )
        
        self.logger.info(f"Response: {response.status_code}")
        
        return response
    
    def get(self, endpoint: str, params: Dict = None) -> requests.Response:
        """GET 请求"""
        return self._request("GET", endpoint, params=params)
    
    def post(self, endpoint: str, json: Dict = None, data: Any = None) -> requests.Response:
        """POST 请求"""
        return self._request("POST", endpoint, json=json, data=data)
    
    def put(self, endpoint: str, json: Dict = None) -> requests.Response:
        """PUT 请求"""
        return self._request("PUT", endpoint, json=json)
    
    def delete(self, endpoint: str) -> requests.Response:
        """DELETE 请求"""
        return self._request("DELETE", endpoint)
