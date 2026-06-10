import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Config:
    """配置管理类"""
    
    # 防火墙配置
    FIREWALL_HOST: str = os.getenv("FIREWALL_HOST", "192.168.1.1")
    FIREWALL_USERNAME: str = os.getenv("FIREWALL_USERNAME", "admin")
    FIREWALL_PASSWORD: str = os.getenv("FIREWALL_PASSWORD", "password")
    FIREWALL_API_PORT: int = int(os.getenv("FIREWALL_API_PORT", "443"))
    FIREWALL_SSH_PORT: int = int(os.getenv("FIREWALL_SSH_PORT", "22"))
    
    # API 配置
    API_BASE_URL: str = os.getenv("API_BASE_URL", f"https://{FIREWALL_HOST}:{FIREWALL_API_PORT}/api")
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "30"))
    
    # 测试环境
    ENV: str = os.getenv("ENV", "test")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # 拓扑配置
    TOPOLOGY_FILE: str = os.getenv("TOPOLOGY_FILE", "basic_topology.json")
    
    # 数据库配置（本机测试不需要，保留配置）
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    
    @classmethod
    def validate(cls) -> bool:
        """验证配置"""
        if not cls.FIREWALL_HOST:
            raise ValueError("FIREWALL_HOST is required")
        if not cls.FIREWALL_USERNAME:
            raise ValueError("FIREWALL_USERNAME is required")
        if not cls.FIREWALL_PASSWORD:
            raise ValueError("FIREWALL_PASSWORD is required")
        return True
