import pytest
import allure
from src.firewall.sonicos_api import SonicOSAPI
from tests.functional.bin.functional_helpers import BaseFunctionalTest


@pytest.mark.functional
class TestAccessRules(BaseFunctionalTest):
    """访问规则功能性测试"""
    
    # ACL 规则配置
    ACCESS_RULE_PAYLOAD = {
        "access_rules": [
            {
                "ipv4": {
                    "name": "auto_rules_01",
                    "comment": "",
                    "action": "allow",
                    "priority": {
                        "auto": True
                    },
                    "enable": True,
                    "from": "LAN",
                    "source": {
                        "address": {
                            "group": "LAN Subnets"
                        },
                        "port": {
                            "any": True
                        }
                    },
                    "to": "WAN",
                    "destination": {
                        "address": {
                            "any": True
                        }
                    },
                    "service": {
                        "any": True
                    },
                    "users": {
                        "included": {
                            "all": True
                        },
                        "excluded": {
                            "none": True
                        }
                    },
                    "tcp": {
                        "timeout": 15,
                        "urgent": False
                    },
                    "udp": {
                        "timeout": 30
                    },
                    "dpi": True,
                    "dpi_ssl": {
                        "client": True,
                        "server": True
                    },
                    "quality_of_service": {
                        "class_of_service": {},
                        "dscp": {
                            "preserve": True
                        }
                    },
                    "botnet_filter": False,
                    "geo_ip_filter": {
                        "enable": False
                    },
                    "logging": True,
                    "flow_reporting": False,
                    "connection_limit": {
                        "source": {},
                        "destination": {}
                    },
                    "sip": False,
                    "h323": False,
                    "fragments": True,
                    "management": False,
                    "max_connections": 100,
                    "packet_monitoring": False,
                    "reflexive": False,
                    "redirect_unauthenticated_users_to_log_in": True,
                    "saml_authentication": False
                }
            }
        ]
    }
    
    @allure.title("通过 API 添加防火墙 ACL 规则")
    @allure.description("使用 API 添加防火墙访问控制规则，包含查询保护逻辑")
    @allure.tag("acl", "api", "functional")
    def test_add_acl_rule_via_api(self, sonicos_api: SonicOSAPI, auth_token: str):
        """测试通过 API 添加 ACL 规则"""
        
        acl_name = "auto_rules_01"
        
        with allure.step("查询现有 ACL 规则"):
            # 先查询是否已存在同名 ACL
            response = sonicos_api._request("GET", "/sonicos/access-rules/ipv4")
            response_data = self.verify_api_response(response)
            
            existing_acls = response_data.get("access_rules", [])
            acl_exists = False
            
            for acl in existing_acls:
                if acl.get("ipv4", {}).get("name") == acl_name:
                    acl_exists = True
                    break
            
            if acl_exists:
                allure.attach(
                    f"ACL '{acl_name}' already exists, skipping creation",
                    name="ACL Status",
                    attachment_type=allure.attachment_type.TEXT
                )
                pytest.skip(f"ACL '{acl_name}' already exists")
        
        with allure.step("添加新的 ACL 规则"):
            # 打印请求 payload 用于调试
            print(f"ACL Payload: {self.ACCESS_RULE_PAYLOAD}")
            
            response = sonicos_api._request(
                "POST",
                "/sonicos/access-rules/ipv4",
                json=self.ACCESS_RULE_PAYLOAD
            )
            
            # 打印响应用于调试
            print(f"Creation Response: {response.text}")
            
            response_data = self.verify_api_response(response)
            self.verify_success_status(response_data)
            self.attach_response_to_allure(response, "ACL Creation Response")
        
        # 检查是否有待处理配置，如果有则提交
        print(f"Checking pending_config: {'pending_config' in response.text}")
        print(f"Response text contains pending_config: {'pending_config' in response.text}")
        print(f"Response text contains 'pending_config': true': {'\"pending_config\": true' in response.text}")
        
        if '"pending_config": true' in response.text:
            with allure.step("提交待处理配置"):
                post_result = sonicos_api.post_pending_config()
                print(f"Post pending config result: {post_result}")
                assert post_result, "Failed to post pending configuration"
                
                # 等待配置生效
                import time
                time.sleep(2)
        else:
            # 强制提交配置以确保生效
            with allure.step("强制提交配置"):
                post_result = sonicos_api.post_pending_config()
                print(f"Force post pending config result: {post_result}")
                # 等待配置生效
                import time
                time.sleep(2)
        
        # 验证 ACL 是否真正创建成功
        with allure.step("验证 ACL 创建结果"):
            verify_response = sonicos_api._request("GET", "/sonicos/access-rules/ipv4")
            verify_data = self.verify_api_response(verify_response)
            
            # 记录当前 ACL 列表
            allure.attach(
                str(verify_data),
                name="Current ACL List",
                attachment_type=allure.attachment_type.JSON
            )
            
            existing_acls = verify_data.get("access_rules", [])
            acl_found = False
            
            # 检查 ACL 名称
            acl_names = []
            for acl in existing_acls:
                acl_name_current = acl.get("ipv4", {}).get("name")
                acl_names.append(acl_name_current)
                if acl_name_current == acl_name:
                    acl_found = True
                    allure.attach(
                        f"ACL '{acl_name}' found in firewall configuration",
                        name="Verification Result",
                        attachment_type=allure.attachment_type.TEXT
                    )
                    break
            
            # 记录所有 ACL 名称
            allure.attach(
                str(acl_names),
                name="All ACL Names",
                attachment_type=allure.attachment_type.TEXT
            )
            
            if not acl_found:
                allure.attach(
                    f"ACL '{acl_name}' NOT found in firewall configuration after creation",
                    name="Verification Result",
                    attachment_type=allure.attachment_type.TEXT
                )
                pytest.fail(f"ACL '{acl_name}' was not actually created on firewall")
    
    @allure.title("验证 ACL 规则生效性")
    @allure.description("通过 SSH 连接测试 ACL 规则是否生效")
    @allure.tag("acl", "ssh", "connectivity", "functional")
    def test_acl_rule_connectivity(self):
        """测试 ACL 规则的连通性"""
        
        # 从环境变量获取配置
        import os
        lan_host = os.getenv("LAN_HOST", "10.8.106.11")
        lan_username = os.getenv("LAN_USERNAME", "root")
        lan_password = os.getenv("LAN_PASSWORD", "qaauto")  # 默认密码
        wan_host = os.getenv("WAN_HOST", "10.8.2.217")
        
        with allure.step("从 LAN 主机 ping WAN 主机"):
            output, error = self.execute_ssh_command(
                lan_host, lan_username, lan_password, f"ping -c 3 {wan_host}"
            )
            
            if output:
                self.attach_response_to_allure(
                    output,
                    "Ping Output"
                )
                
                # 验证 ping 结果
                assert "64 bytes from" in output, "Ping failed - ACL may be blocking traffic"
                assert "0% packet loss" in output or "0 received" not in output, "All packets lost - ACL may be blocking traffic"
                
                allure.attach(
                    "Ping test successful - ACL rule is working correctly",
                    name="Test Result",
                    attachment_type=allure.attachment_type.TEXT
                )
            else:
                allure.attach(
                    f"SSH connection failed: {error}",
                    name="Connection Error",
                    attachment_type=allure.attachment_type.TEXT
                )
                pytest.skip(f"SSH connection to {lan_host} failed: {error}")
    
    @allure.title("完整 ACL 功能测试流程")
    @allure.description("完整的 ACL 创建和验证流程")
    @allure.tag("acl", "end-to-end", "functional")
    def test_complete_acl_workflow(self, sonicos_api: SonicOSAPI, auth_token: str):
        """测试完整的 ACL 工作流程"""
        
        try:
            # 步骤 1: 添加 ACL 规则
            self.test_add_acl_rule_via_api(sonicos_api, auth_token)
            
            # 步骤 2: 验证连通性
            self.test_acl_rule_connectivity()
            
            allure.attach(
                "Complete ACL workflow test passed",
                name="Workflow Result",
                attachment_type=allure.attachment_type.TEXT
            )
            
        except Exception as e:
            allure.attach(
                str(e),
                name="Workflow Error",
                attachment_type=allure.attachment_type.TEXT
            )
            raise e
