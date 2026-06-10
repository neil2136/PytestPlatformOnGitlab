# Pytest Framework 部署指南 - Ubuntu 24.04

## 概述

本指南详细说明如何在 Ubuntu 24.04 机器上搭建完整的 Pytest 测试框架，支持 API、CLI、Functional 和 UI 四种测试类型。

## 系统要求

- **操作系统**: Ubuntu 24.04 LTS
- **内存**: 最少 4GB RAM（推荐 8GB）
- **存储**: 最少 10GB 可用空间
- **网络**: 能够访问目标防火墙设备

## 部署步骤

### 1. 系统准备

#### 1.1 更新系统
```bash
sudo apt update && sudo apt upgrade -y
```

#### 1.2 安装基础依赖
```bash
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    unzip \
    build-essential \
    libffi-dev \
    libssl-dev \
    python3-dev
```

#### 1.3 安装 Playwright 浏览器依赖（UI 测试需要）
```bash
# 安装 Playwright 系统依赖
sudo apt install -y \
    libnss3 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libxss1 \
    libasound2
```

### 2. 创建项目目录和用户

#### 2.1 创建测试用户（可选）
```bash
sudo useradd -m -s /bin/bash testuser
sudo usermod -aG sudo testuser
# 切换到测试用户
su - testuser
```

#### 2.2 创建项目目录
```bash
mkdir -p /home/testuser/test_framework
cd /home/testuser/test_framework
```

### 3. 设置 Python 虚拟环境

#### 3.1 创建虚拟环境
```bash
python3 -m venv .venv
```

#### 3.2 激活虚拟环境
```bash
source .venv/bin/activate
```

#### 3.3 升级 pip
```bash
pip install --upgrade pip
```

### 4. 安装 Python 依赖

#### 4.1 创建 requirements.txt
```bash
cat > requirements.txt << 'EOF'
# 核心框架
pytest==8.0.0

# 报告与覆盖率
allure-pytest==2.13.2
allure-python-commons==2.13.2
pytest-cov==4.1.0
pytest-html==4.1.0

# 并行执行
pytest-xdist==3.5.0

# 环境管理
pytest-env==1.1.0
python-dotenv==1.0.0

# 防火墙连接
requests==2.31.0
paramiko==3.3.0
netmiko==4.2.0

# 数据验证
pydantic==2.5.0

# UI 测试
playwright==1.40.0

# 代码质量
black==24.4.2
ruff==0.1.9
mypy==1.8.0
EOF
```

#### 4.2 安装依赖
```bash
pip install -r requirements.txt
```

#### 4.3 安装 Playwright 浏览器
```bash
playwright install chromium
playwright install-deps chromium
```

### 5. 安装 Allure 报告工具

#### 5.1 下载 Allure
```bash
wget https://github.com/allure-framework/allure2/releases/download/2.24.1/allure_2.24.1-1_all.deb
```

#### 5.2 安装 Allure
```bash
sudo dpkg -i allure_2.24.1-1_all.deb
sudo apt-get install -f  # 解决依赖问题
```

#### 5.3 验证 Allure 安装
```bash
allure --version
```

### 6. 创建项目结构

#### 6.1 创建目录结构
```bash
mkdir -p {src/{core/{utils,plugins},firewall},tests/{api,cli,functional,ui},reports/{allure,html}}
mkdir -p tests/{api,cli,functional,ui}/{bin,testplan}
```

#### 6.2 创建 __init__.py 文件
```bash
touch src/__init__.py
touch src/core/__init__.py
touch src/core/utils/__init__.py
touch src/firewall/__init__.py
touch tests/__init__.py
touch tests/api/__init__.py
touch tests/cli/__init__.py
touch tests/functional/__init__.py
touch tests/ui/__init__.py
touch tests/api/bin/__init__.py
touch tests/cli/bin/__init__.py
touch tests/functional/bin/__init__.py
touch tests/ui/bin/__init__.py
```

### 7. 配置文件设置

#### 7.1 创建 pytest.ini
```bash
cat > pytest.ini << 'EOF'
[pytest]
minversion = 7.0
addopts = 
    -ra
    -q
    --strict-markers
    --alluredir=reports/allure
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    unit: Unit tests
    api: API tests
    cli: CLI tests
    acl: ACL functionality tests
    integration: Integration tests
    slow: Slow running tests
    smoke: Smoke tests
    functional: Functional tests
    ui: UI tests with Playwright
env =
    ENV=test
    LOG_LEVEL=INFO
EOF
```

#### 7.2 创建 conftest.py
```bash
cat > conftest.py << 'EOF'
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
    return Logger(level=config.LOG_LEVEL)

# API 客户端
@pytest.fixture(scope="session")
def api_client(config: Config) -> APIClient:
    """API 客户端 fixture"""
    return APIClient(
        base_url=config.API_BASE_URL,
        timeout=config.API_TIMEOUT
    )

# CLI 客户端
@pytest.fixture(scope="session")
def cli_client(config: Config) -> CLIClient:
    """CLI 客户端 fixture"""
    return CLIClient(
        host=config.FIREWALL_HOST,
        username=config.FIREWALL_USERNAME,
        password=config.FIREWALL_PASSWORD,
        port=config.FIREWALL_SSH_PORT
    )

# SonicOS API
@pytest.fixture(scope="session")
def sonicos_api(api_client: APIClient) -> SonicOSAPI:
    """SonicOS API fixture"""
    return SonicOSAPI(api_client)

# SonicOS CLI
@pytest.fixture(scope="session")
def sonicos_cli(cli_client: CLIClient) -> SonicOSCLI:
    """SonicOS CLI fixture"""
    return SonicOSCLI(cli_client)

# 认证令牌
@pytest.fixture(scope="session")
def auth_token(sonicos_api: SonicOSAPI) -> str:
    """获取认证令牌"""
    return sonicos_api.get_auth_token()
EOF
```

#### 7.3 创建 .env 文件
```bash
cat > .env << 'EOF'
# 防火墙配置
FIREWALL_HOST=10.8.105.173
FIREWALL_USERNAME=admin
FIREWALL_PASSWORD=password2
FIREWALL_API_PORT=443
FIREWALL_SSH_PORT=22

# 测试环境
ENV=test
LOG_LEVEL=INFO

# 拓扑配置
TOPOLOGY_FILE=basic_topology.json

# API 配置
API_BASE_URL=https://10.8.105.173:443/api
API_TIMEOUT=30

# SSH 连接配置
LAN_HOST=10.8.106.11
LAN_USERNAME=root
LAN_PASSWORD=password
WAN_HOST=10.8.2.217
EOF
```

### 8. 核心代码文件创建

#### 8.1 创建配置管理
```bash
cat > src/core/utils/config.py << 'EOF'
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
EOF
```

#### 8.2 创建 API 客户端
```bash
cat > src/core/utils/api_client.py << 'EOF'
import requests
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class APIClient:
    """API 客户端类"""
    
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.verify = False  # 忽略 SSL 证书验证
        
    def get(self, endpoint: str, params: Optional[Dict] = None) -> requests.Response:
        """GET 请求"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        logger.info(f"GET: {url}")
        return self.session.get(url, params=params, timeout=self.timeout)
    
    def post(self, endpoint: str, json: Optional[Dict] = None, data: Optional[Dict] = None) -> requests.Response:
        """POST 请求"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        logger.info(f"POST: {url}")
        return self.session.post(url, json=json, data=data, timeout=self.timeout)
    
    def put(self, endpoint: str, json: Optional[Dict] = None) -> requests.Response:
        """PUT 请求"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        logger.info(f"PUT: {url}")
        return self.session.put(url, json=json, timeout=self.timeout)
    
    def delete(self, endpoint: str) -> requests.Response:
        """DELETE 请求"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        logger.info(f"DELETE: {url}")
        return self.session.delete(url, timeout=self.timeout)
EOF
```

#### 8.3 创建 CLI 客户端
```bash
cat > src/core/utils/cli_client.py << 'EOF'
import paramiko
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class CLIClient:
    """CLI 客户端类"""
    
    def __init__(self, host: str, username: str, password: str, port: int = 22):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.client = None
        
    def connect(self):
        """建立 SSH 连接"""
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(
            hostname=self.host,
            username=self.username,
            password=self.password,
            port=self.port,
            timeout=30
        )
        
    def disconnect(self):
        """断开连接"""
        if self.client:
            self.client.close()
            
    def execute_command(self, command: str, timeout: int = 30) -> str:
        """执行命令"""
        if not self.client:
            self.connect()
            
        stdin, stdout, stderr = self.client.exec_command(command, timeout=timeout)
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        if error:
            logger.error(f"Command error: {error}")
            raise Exception(f"Command failed: {error}")
            
        return output
    
    def __enter__(self):
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
EOF
```

### 9. 防火墙接口类创建

#### 9.1 创建 SonicOS API 类
```bash
cat > src/firewall/sonicos_api.py << 'EOF'
import requests
import json
import logging
from typing import Dict, Any
from src.core.utils.api_client import APIClient

logger = logging.getLogger(__name__)

class SonicOSAPI:
    """SonicOS API 接口类"""
    
    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        self.auth_token = None
        
    def get_auth_token(self) -> str:
        """获取认证令牌"""
        payload = {
            "username": "admin",
            "password": "password2"
        }
        response = self.api_client.post("/auth", json=payload)
        if response.status_code == 200:
            data = response.json()
            self.auth_token = data.get("token")
            return self.auth_token
        else:
            raise Exception(f"Authentication failed: {response.status_code}")
    
    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """通用请求方法"""
        headers = kwargs.pop('headers', {})
        if self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'
        
        if method == 'GET':
            return self.api_client.get(endpoint, headers=headers, **kwargs)
        elif method == 'POST':
            return self.api_client.post(endpoint, headers=headers, **kwargs)
        elif method == 'PUT':
            return self.api_client.put(endpoint, headers=headers, **kwargs)
        elif method == 'DELETE':
            return self.api_client.delete(endpoint, headers=headers, **kwargs)
        else:
            raise ValueError(f"Unsupported method: {method}")
    
    def post_pending_config(self) -> bool:
        """提交待处理配置"""
        try:
            response = self._request('POST', '/sonicos/pending-config')
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to post pending config: {e}")
            return False
EOF
```

#### 9.2 创建 SonicOS CLI 类
```bash
cat > src/firewall/sonicos_cli.py << 'EOF'
import logging
from src.core.utils.cli_client import CLIClient

logger = logging.getLogger(__name__)

class SonicOSCLI:
    """SonicOS CLI 接口类"""
    
    def __init__(self, cli_client: CLIClient):
        self.cli_client = cli_client
        
    def execute_command(self, command: str, timeout: int = 30) -> str:
        """执行 CLI 命令"""
        try:
            return self.cli_client.execute_command(command, timeout)
        except Exception as e:
            logger.error(f"CLI command failed: {e}")
            raise
    
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass  # CLIClient 会自动管理连接
EOF
```

### 10. 测试用例和公共代码

#### 10.1 创建各模块公共代码
```bash
# API 模块公共代码
cat > tests/api/bin/api_helpers.py << 'EOF'
"""
API 测试公共工具类
"""
import allure

class APIHelpers:
    """API 测试辅助工具类"""
    
    @staticmethod
    def verify_api_response(response, expected_status=200):
        """验证 API 响应的通用方法"""
        assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"
        return response.json()
    
    @staticmethod
    def attach_response_to_allure(response, name="API Response"):
        """将响应附加到 Allure 报告"""
        allure.attach(
            response.text,
            name=name,
            attachment_type=allure.attachment_type.JSON
        )

class BaseAPITest(APIHelpers):
    """API 测试基类，继承 API 辅助工具"""
    pass
EOF

# CLI 模块公共代码
cat > tests/cli/bin/cli_helpers.py << 'EOF'
"""
CLI 测试公共工具类
"""
import allure

class CLIHelpers:
    """CLI 测试辅助工具类"""
    
    @staticmethod
    def verify_cli_output(output, expected_patterns=None):
        """验证 CLI 输出的通用方法"""
        if expected_patterns:
            for pattern in expected_patterns:
                assert pattern in output, f"Expected pattern '{pattern}' not found in CLI output"
        return output
    
    @staticmethod
    def attach_cli_output_to_allure(output, name="CLI Output"):
        """将 CLI 输出附加到 Allure 报告"""
        allure.attach(
            output,
            name=name,
            attachment_type=allure.attachment_type.TEXT
        )

class BaseCLITest(CLIHelpers):
    """CLI 测试基类，继承 CLI 辅助工具"""
    pass
EOF

# Functional 模块公共代码
cat > tests/functional/bin/functional_helpers.py << 'EOF'
"""
Functional 测试公共工具类
"""
import allure
import paramiko

class FunctionalHelpers:
    """Functional 测试辅助工具类"""
    
    @staticmethod
    def verify_api_response(response, expected_status=200):
        """验证 API 响应的通用方法"""
        assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"
        return response.json()
    
    @staticmethod
    def attach_response_to_allure(response, name="API Response"):
        """将响应附加到 Allure 报告"""
        content = response.text if hasattr(response, 'text') else str(response)
        attachment_type = allure.attachment_type.JSON if hasattr(response, 'text') else allure.attachment_type.TEXT
        allure.attach(
            content,
            name=name,
            attachment_type=attachment_type
        )

class BaseFunctionalTest(FunctionalHelpers):
    """Functional 测试基类，继承 Functional 辅助工具"""
    pass
EOF

# UI 模块公共代码
cat > tests/ui/bin/ui_helpers.py << 'EOF'
"""
UI 测试公共工具类
"""
import allure
from playwright.sync_api import sync_playwright

class UIHelpers:
    """UI 测试辅助工具类"""
    
    @staticmethod
    def create_browser_context(headless=True):
        """创建浏览器上下文"""
        p = sync_playwright().start()
        browser = p.chromium.launch(
            headless=headless,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        context = browser.new_context(
            ignore_https_errors=True,
            viewport={'width': 1920, 'height': 1080}
        )
        return browser, context

class BaseUITest(UIHelpers):
    """UI 测试基类，继承 UI 辅助工具"""
    pass
EOF
```

### 11. 网络配置验证

#### 11.1 验证防火墙连通性
```bash
# 测试 API 连通性
curl -k https://10.8.105.173/api

# 测试 SSH 连通性
ssh -o StrictHostKeyChecking=no admin@10.8.105.173 "show version"
```

#### 11.2 验证网络拓扑
```bash
# 从测试主机 ping 防火墙
ping -c 3 10.8.105.173

# 验证端口连通性
nmap -p 22,443 10.8.105.173
```

### 12. 运行测试

#### 12.1 激活虚拟环境
```bash
source /home/testuser/test_framework/.venv/bin/activate
cd /home/testuser/test_framework
```

#### 12.2 运行所有测试
```bash
pytest tests/ -v
```

#### 12.3 运行特定模块测试
```bash
# API 测试
pytest tests/api/ -v

# CLI 测试
pytest tests/cli/ -v

# Functional 测试
pytest tests/functional/ -v

# UI 测试
pytest tests/ui/ -v
```

#### 12.4 生成测试报告
```bash
# 生成 Allure 报告
pytest tests/ --alluredir=reports/allure
allure serve reports/allure

# 生成 HTML 报告
pytest tests/ --html=reports/html/test_report.html --self-contained-html
```

### 13. 故障排除

#### 13.1 常见问题

**问题 1**: SSL 证书验证失败
```bash
# 解决方案：在代码中禁用 SSL 验证（已在代码中实现）
# 或添加防火墙证书到系统信任存储
```

**问题 2**: Playwright 浏览器启动失败
```bash
# 重新安装浏览器依赖
playwright install-deps chromium
playwright install chromium
```

**问题 3**: SSH 连接超时
```bash
# 检查防火墙 SSH 服务状态
# 验证网络连通性
# 检查防火墙规则
```

**问题 4**: API 认证失败
```bash
# 检查防火墙管理员账户状态
# 验证 API 访问权限
# 检查防火墙 API 服务状态
```

#### 13.2 日志查看
```bash
# 查看 pytest 日志
pytest tests/ -v -s

# 查看 Allure 报告
allure generate reports/allure -o reports/html/allure --clean
allure open reports/html/allure
```

### 14. 维护和更新

#### 14.1 更新依赖
```bash
pip install --upgrade -r requirements.txt
playwright install-deps chromium
```

#### 14.2 清理缓存
```bash
# 清理 Python 缓存
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete

# 清理 pytest 缓存
rm -rf .pytest_cache
```

#### 14.3 备份配置
```bash
# 备份重要配置文件
cp .env .env.backup
cp pytest.ini pytest.ini.backup
cp conftest.py conftest.py.backup
```

## 总结

按照本指南完成部署后，您将拥有一个完整的 Pytest 测试框架，支持：

- **API 测试**: 通过 REST API 测试防火墙功能
- **CLI 测试**: 通过 SSH 连接测试防火墙命令行接口
- **Functional 测试**: 端到端功能测试
- **UI 测试**: 通过 Playwright 进行 Web UI 自动化测试

框架提供了完整的测试报告、并行执行、环境管理和代码复用功能，适用于持续集成和自动化测试场景。
