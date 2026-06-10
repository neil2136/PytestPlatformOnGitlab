import paramiko
from netmiko import ConnectHandler
from typing import Optional, List
from src.core.utils.logger import Logger


class CLIClient:
    """CLI 客户端基类"""
    
    def __init__(self, host: str, username: str, password: str, 
                 port: int = 22, logger: Logger = None):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.logger = logger or Logger()
        self.connection: Optional[ConnectHandler] = None
    
    def connect(self):
        """建立 SSH 连接"""
        device = {
            'device_type': 'generic_termserver',  # 使用通用终端服务器类型
            'host': self.host,
            'username': self.username,
            'password': self.password,
            'port': self.port,
            # 'session_log': 'ssh_session.log',  # 禁用会话日志以避免临时文件
            'global_delay_factor': 0.5,  # 减少延迟
            'banner_timeout': 20,  # 增加 banner 超时
            'conn_timeout': 10,  # 连接超时
        }
        self.connection = ConnectHandler(**device)
        self.logger.info(f"Connected to {self.host}:{self.port}")
    
    def disconnect(self):
        """断开连接"""
        if self.connection:
            self.connection.disconnect()
            self.logger.info(f"Disconnected from {self.host}")
    
    def execute_command(self, command: str, timeout: int = 30) -> str:
        """执行 CLI 命令"""
        if not self.connection:
            self.connect()
        
        self.logger.info(f"Executing command: {command}")
        
        # 处理 SonicWall 特殊情况
        if command == "show version":
            # 发送回车键获取提示符
            output = self.connection.read_channel()
            output += self.connection.send_command("\n", read_timeout=5)
            output += self.connection.send_command(command, read_timeout=timeout)
        else:
            output = self.connection.send_command(command, read_timeout=timeout)
        
        return output
    
    def execute_config(self, config_commands: List[str]) -> str:
        """执行配置命令"""
        if not self.connection:
            self.connect()
        
        self.logger.info(f"Executing config commands: {config_commands}")
        output = self.connection.send_config_set(config_commands)
        
        return output
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
