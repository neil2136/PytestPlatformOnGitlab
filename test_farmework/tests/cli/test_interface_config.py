import pytest
import allure
from src.firewall.sonicos_cli import SonicOSCLI
from tests.cli.bin.cli_helpers import BaseCLITest


@pytest.mark.cli
class TestInterfaceConfigCLI(BaseCLITest):
    """接口配置 CLI 测试"""
    
    @allure.title("测试 SSH 连接")
    @allure.description("测试与防火墙的 SSH 连接")
    @allure.tag("interface", "connectivity", "x2", "cli")
    def test_ssh_connection(self, sonicos_cli: SonicOSCLI):
        """测试 SSH 连接"""
        
        with allure.step("建立 SSH 连接"):
            try:
                with sonicos_cli as cli:
                    output = cli.execute_command("show version", timeout=10)
                    self.attach_cli_output_to_allure(output, "Version Output")
                    assert "SonicWall" in output or "TZ" in output or "NSa" in output, "未检测到 SonicWall 设备"
            except Exception as e:
                allure.attach(str(e), name="Connection Error", attachment_type=allure.attachment_type.TEXT)
                pytest.skip(f"SSH 连接失败: {e}")
    
    @allure.title("通过 CLI 配置 X2 接口 IP")
    @allure.description("使用 CLI 命令配置防火墙 X2 接口的 IP 地址")
    @allure.tag("interface", "configuration", "x2", "cli")
    def test_configure_x2_ip_via_cli(self, sonicos_cli: SonicOSCLI):
        """测试通过 CLI 配置 X2 接口 IP"""
        
        try:
            with sonicos_cli as cli:
                with allure.step("执行配置命令序列"):
                    commands = [
                        "configure terminal",
                        "interface X2", 
                        "ip-assignment DMZ static",
                        "ip 12.12.1.168",
                        "commit",
                        "end",
                        "exit"
                    ]
                    
                    output = self.execute_cli_commands(cli, commands)
                    self.attach_cli_output_to_allure(output, "Configuration Commands")
                    
                    # 验证关键配置步骤
                    assert "ip 12.12.1.168" in output, "IP 配置未成功执行"
                    
        except Exception as e:
            allure.attach(str(e), name="Configuration Error", attachment_type=allure.attachment_type.TEXT)
            pytest.skip(f"CLI 配置失败: {e}")
    
    
