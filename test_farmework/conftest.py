import pytest
import os
import sys
from pathlib import Path

# 添加 src 到 Python 路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

# 导入 fixtures
from src.core.utils.config import Config
from src.core.utils.api_client import APIClient
from src.core.utils.cli_client import CLIClient
from src.firewall.sonicos_api import SonicOSAPI
from src.firewall.sonicos_cli import SonicOSCLI
from src.core.utils.logger import Logger

# 全局配置
@pytest.fixture(scope="session")
def config() -> Config:
    """加载配置"""
    return Config()

# 日志
@pytest.fixture(scope="session")
def logger(config: Config) -> Logger:
    """初始化日志"""
    return Logger(config.LOG_LEVEL)

# API 客户端
@pytest.fixture(scope="session")
def api_client(config: Config, logger: Logger) -> APIClient:
    """API 客户端"""
    return APIClient(
        base_url=config.API_BASE_URL,
        timeout=config.API_TIMEOUT,
        logger=logger
    )

# CLI 客户端
@pytest.fixture(scope="session")
def cli_client(config: Config, logger: Logger) -> CLIClient:
    """CLI 客户端"""
    return CLIClient(
        host=config.FIREWALL_HOST,
        username=config.FIREWALL_USERNAME,
        password=config.FIREWALL_PASSWORD,
        port=config.FIREWALL_SSH_PORT,
        logger=logger
    )

# SonicOS API
@pytest.fixture(scope="session")
def sonicos_api(config: Config, logger: Logger) -> SonicOSAPI:
    """SonicOS API 客户端"""
    return SonicOSAPI(
        host=config.FIREWALL_HOST,
        username=config.FIREWALL_USERNAME,
        password=config.FIREWALL_PASSWORD,
        port=config.FIREWALL_API_PORT,
        logger=logger
    )

# SonicOS CLI
@pytest.fixture(scope="session")
def sonicos_cli(config: Config, logger: Logger) -> SonicOSCLI:
    """SonicOS CLI 客户端"""
    return SonicOSCLI(
        host=config.FIREWALL_HOST,
        username=config.FIREWALL_USERNAME,
        password=config.FIREWALL_PASSWORD,
        port=config.FIREWALL_SSH_PORT,
        logger=logger
    )

# 认证 Token
@pytest.fixture(scope="session")
def auth_token(sonicos_api: SonicOSAPI, config: Config) -> str:
    """获取认证 Token"""
    try:
        return sonicos_api.login(
            username=config.FIREWALL_USERNAME,
            password=config.FIREWALL_PASSWORD
        )
    except Exception as e:
        pytest.skip(f"Failed to login: {e}")

# 拓扑配置
@pytest.fixture(scope="session")
def topology_config(config: Config):
    """加载网络拓扑配置"""
    import json
    from pathlib import Path
    topo_file = Path("topology") / config.TOPOLOGY_FILE
    if topo_file.exists():
        with open(topo_file) as f:
            return json.load(f)
    return None

@pytest.fixture(scope="session", autouse=True)
def setup_environment():
    """设置测试环境"""
    os.environ.setdefault("ENV", "test")
    os.environ.setdefault("LOG_LEVEL", "INFO")
    yield
    # 清理逻辑
    pass

@pytest.fixture(scope="session")
def run_id():
    """生成运行 ID"""
    from datetime import datetime
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def pytest_configure(config):
    """pytest 配置钩子"""
    # 注册自定义标记
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "api: API tests")
    config.addinivalue_line("markers", "cli: CLI tests")
    config.addinivalue_line("markers", "acl: ACL functionality tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "smoke: Smoke tests")
    config.addinivalue_line("markers", "ui: UI tests with Playwright")

def pytest_collection_modifyitems(config, items):
    """修改测试收集"""
    # 自动添加标记
    for item in items:
        # 根据文件路径自动添加标记
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "api" in str(item.fspath):
            item.add_marker(pytest.mark.api)
        elif "cli" in str(item.fspath):
            item.add_marker(pytest.mark.cli)
        elif "acl" in str(item.fspath):
            item.add_marker(pytest.mark.acl)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "ui" in str(item.fspath):
            item.add_marker(pytest.mark.ui)
