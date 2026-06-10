import pytest
import allure
from src.firewall.sonicos_api import SonicOSAPI
from tests.api.bin.api_helpers import BaseAPITest


@pytest.mark.api
class TestInterfaceAPI(BaseAPITest):
    """接口配置 API 测试 - 使用 fw_api_exp 认证方式"""
    
    # X2 接口配置 payload
    X2_INTERFACE_PAYLOAD = {
        "interfaces": [
            {
                "ipv4": {
                    "mac": {"default": True},
                    "multicast": False,
                    "exclude_route": False,
                    "routed_mode": {},
                    "shutdown_port": False,
                    "cos_8021p": False,
                    "management_traffic_only": False,
                    "link_speed": {"auto_negotiate": True},
                    "flow_control": False,
                    "port": {"redundancy_aggregation": False},
                    "asymmetric_route": False,
                    "flow_reporting": True,
                    "mtu": 1500,
                    "management": {
                        "fqdn_assignment": "",
                        "https": True,
                        "https_source": {"any": True},
                        "ping": True,
                        "ping_source": {"any": True},
                        "snmp": False,
                        "snmp_source": {"any": True},
                        "ssh": True,
                        "ssh_source": {"any": True}
                    },
                    "user_login": {"http": False, "https": False},
                    "https_redirect": True,
                    "name": "X2",
                    "ip_assignment": {
                        "zone": "DMZ",
                        "mode": {
                            "static": {
                                "ip": "12.12.1.100",
                                "netmask": "255.255.255.0",
                                "gateway": "0.0.0.0"
                            }
                        }
                    }
                }
            }
        ]
    }
    
    @allure.title("配置 X2 接口")
    @allure.description("通过 API 配置防火墙 X2 接口的 IPv4 设置")
    @allure.tag("interface", "configuration", "x2")
    def test_configure_x2_interface(self, sonicos_api: SonicOSAPI, auth_token: str):
        """测试配置 X2 接口"""
        
        with allure.step("发送 PUT 请求配置 X2 接口"):
            response = sonicos_api._request(
                "PUT",
                "/sonicos/interfaces/ipv4/name/X2",
                json=self.X2_INTERFACE_PAYLOAD
            )
        
        with allure.step("验证响应状态码"):
            response_data = self.verify_api_response(response)
        
        with allure.step("验证配置成功"):
            self.verify_success_status(response_data)
        
        # 检查是否有待处理配置，如果有则提交
        if '"pending_config": true' in response.text:
            with allure.step("提交待处理配置"):
                assert sonicos_api.post_pending_config(), "Failed to post pending configuration"
        
        self.attach_response_to_allure(response)
    
    @allure.title("验证 X2 接口配置")
    @allure.description("获取并验证 X2 接口的当前配置")
    @allure.tag("interface", "verification", "x2")
    def test_verify_x2_interface_config(self, sonicos_api: SonicOSAPI, auth_token: str):
        """测试验证 X2 接口配置"""
        
        with allure.step("获取 X2 接口配置"):
            response = sonicos_api._request("GET", "/sonicos/interfaces/ipv4/name/X2")
        
        with allure.step("验证响应状态码"):
            response_data = self.verify_api_response(response)
        
        with allure.step("验证接口配置"):
            assert "interfaces" in response_data
            
            # 查找 X2 接口
            x2_interface = None
            for interface in response_data["interfaces"]:
                if "ipv4" in interface and interface["ipv4"].get("name") == "X2":
                    x2_interface = interface["ipv4"]
                    break
            
            assert x2_interface is not None, "X2 interface not found in response"
            
            # 验证 IP 配置
            self._verify_ip_assignment(x2_interface)
        
        self.attach_response_to_allure(response, "Interface Configuration")
    
    def _verify_ip_assignment(self, x2_interface):
        """验证 IP 分配配置"""
        assert "ip_assignment" in x2_interface
        ip_assignment = x2_interface["ip_assignment"]
        assert ip_assignment["zone"] == "DMZ"
        assert "mode" in ip_assignment
        assert "static" in ip_assignment["mode"]
        
        static_config = ip_assignment["mode"]["static"]
        assert static_config["ip"] == "12.12.1.100"
        assert static_config["netmask"] == "255.255.255.0"
