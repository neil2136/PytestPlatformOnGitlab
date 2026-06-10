from src.core.utils.cli_client import CLIClient
from typing import Dict, List


class SonicOSCLI(CLIClient):
    """SonicOS CLI 专用客户端"""
    
    def __init__(self, host: str, username: str, password: str, 
                 port: int = 22, logger=None):
        super().__init__(host, username, password, port, logger)
        self.device_type = 'sonicwall'  # 使用 sonicwall 设备类型
    
    def get_system_info(self) -> Dict:
        """获取系统信息"""
        output = self.execute_command("show system")
        return self._parse_system_info(output)
    
    def get_interface_status(self, interface: str = None) -> Dict:
        """获取接口状态"""
        cmd = f"show interface {interface}" if interface else "show interface"
        output = self.execute_command(cmd)
        return self._parse_interface_status(output)
    
    def configure_acl(self, acl_name: str, rules: List[Dict]) -> str:
        """配置 ACL"""
        commands = [f"access-list {acl_name}"]
        for rule in rules:
            commands.append(self._format_acl_rule(rule))
        commands.append("exit")
        return self.execute_config(commands)
    
    def show_acl(self, acl_name: str) -> str:
        """显示 ACL 配置"""
        return self.execute_command(f"show access-list {acl_name}")
    
    def _parse_system_info(self, output: str) -> Dict:
        """解析系统信息输出"""
        # 实现解析逻辑
        return {"raw_output": output}
    
    def _parse_interface_status(self, output: str) -> Dict:
        """解析接口状态输出"""
        # 实现解析逻辑
        return {"raw_output": output}
    
    def _format_acl_rule(self, rule: Dict) -> str:
        """格式化 ACL 规则"""
        # 实现格式化逻辑
        action = rule.get("action", "permit")
        source = rule.get("source", "any")
        destination = rule.get("destination", "any")
        protocol = rule.get("protocol", "ip")
        return f"{action} {protocol} {source} {destination}"
