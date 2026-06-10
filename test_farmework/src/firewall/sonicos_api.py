import requests
from typing import Dict, Any, Optional
from src.core.utils.logger import Logger
from src.core.utils.api_client import APIClient


class SonicOSAPI:
    """SonicOS API 专用客户端"""
    
    def __init__(self, host: str, username: str, password: str, 
                 port: int = 443, logger: Logger = None):
        self.base_url = f"https://{host}:{port}/api"
        self.username = username
        self.password = password
        self.timeout = 30
        self.session = requests.Session()
        self.session.verify = False  # 生产环境应使用有效证书
        self.logger = logger or Logger()
        self.token: Optional[str] = None
        self.config_mode: bool = False
    
    def login(self, username: str = None, password: str = None) -> str:
        """登录获取 Token - 使用 fw_api_exp 认证方式"""
        username = username or self.username
        password = password or self.password
        
        # 使用 fw_api_exp 的认证方式
        response = self.session.post(
            f"{self.base_url}/sonicos/auth",
            json={"override": False, "snwl": True},
            auth=(username, password),
            verify=False,
            timeout=self.timeout
        )
        
        if response.status_code == 200:
            resp_data = response.json()
            status = resp_data.get("status")
            info = status.get("info")
            
            if status["success"]:
                self.logger.info(f"Get token from firewall = {resp_data['status']['info']}")
                fw_login = [
                    (i["bearer_token"], i["config_mode"])
                    for i in info
                    if "bearer_token" in i
                ]
                token, config_mode = fw_login[0] if fw_login else ("", False)
                self.token = token
                self.config_mode = config_mode == "Yes"
                
                # 设置 Authorization header
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                
                # 如果不在配置模式，尝试进入配置模式
                if not self.config_mode:
                    self.set_config_mode()
                
                return self.token
            else:
                raise Exception(f"Login failed: {resp_data}")
        else:
            raise Exception(f"Login failed: {response.text}")
    
    def set_config_mode(self):
        """设置配置模式"""
        response = self.session.post(
            f"{self.base_url}/sonicos/config-mode",
            headers={"Authorization": f"Bearer {self.token}"},
            verify=False,
            timeout=self.timeout
        )
        
        if response.status_code == 200:
            resp_data = response.json()
            if resp_data["status"]["success"]:
                self.logger.info(f"Set config mode in firewall = {resp_data}")
                self.config_mode = True
                return True
        else:
            raise Exception(f"Failed to set config mode: {response.text}")
    
    def check_heartbeat(self):
        """检查心跳"""
        response = self.session.post(
            f"{self.base_url}/sonicos/user-status/heartbeat",
            headers={"Authorization": f"Bearer {self.token}"},
            verify=False,
            timeout=self.timeout
        )
        
        if response.status_code == 200:
            self.logger.info(f"User heartbeat status = {response.json()}")
            return True
        else:
            self.logger.error(f"Heartbeat failed: {response.text}")
            return False
    
    def post_pending_config(self):
        """提交待处理配置"""
        response = self.session.post(
            f"{self.base_url}/sonicos/config/pending",
            json={},
            headers={"Authorization": f"Bearer {self.token}"},
            verify=False,
            timeout=self.timeout
        )
        
        if response.status_code == 200:
            resp_data = response.json()
            status = resp_data.get("status")
            cli = status.get("cli")
            
            if status["success"] and not cli.get("pending_config"):
                self.logger.info("Pending settings are posted.")
                return True
        else:
            self.logger.error(f"Failed to post pending config: {response.text}")
            return False
    
    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """通用请求方法"""
        url = f"{self.base_url}{endpoint}"
        
        self.logger.info(f"{method} {url}")
        
        response = self.session.request(method, url, verify=False, timeout=self.timeout, **kwargs)
        
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
    
    def get_system_info(self) -> Dict:
        """获取系统信息"""
        response = self.get("/system/info")
        return response.json()
    
    def get_interface_config(self, interface: str = None) -> Dict:
        """获取接口配置"""
        endpoint = f"/interfaces/{interface}" if interface else "/interfaces"
        response = self.get(endpoint)
        return response.json()
    
    def get_acl_list(self) -> Dict:
        """获取 ACL 列表"""
        response = self.get("/acl")
        return response.json()
    
    def get_acl(self, acl_name: str) -> Dict:
        """获取指定 ACL"""
        response = self.get(f"/acl/{acl_name}")
        return response.json()
