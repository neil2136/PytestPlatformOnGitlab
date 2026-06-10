# 基于 pytest 的防火墙自动化测试框架设计 (CLI/API/Functional/UI)

## 1. 设计目标与原则

### 1.1 设计目标

| 目标 | 说明 | 验收标准 |
|------|------|---------|
| **完全本地化** | 所有组件本地部署，无外部云依赖 | 无需外网即可运行 |
| **现代化技术栈** | pytest + GitLab CI | 主流生态，社区活跃 |
| **四测试类型** | CLI 测试 + API 测试 + 功能测试 + UI 测试 | 一套框架支持 |
| **防火墙专用** | 针对 SonicOS 防火墙 API/CLI 优化 | 覆盖核心功能 |
| **固定拓扑支持** | 支持固定网络拓扑环境测试 | 拓扑配置化 |
| **开箱即用** | 最小配置即可运行 | 5 分钟内完成本地环境搭建 |
| **报告可视化** | 本地 HTML 报告 + 历史趋势 | 浏览器直接查看 |
| **CI/CD 集成** | GitLab CI 自动化流水线 | Push/MR 自动触发 |

### 1.2 技术选型

| 组件 | 技术选型 | 版本 | 理由 |
|------|---------|------|------|
| **测试框架** | pytest | 8.0+ | Python 生态标准，插件丰富 |
| **API 测试** | requests + pydantic | 2.31+ | 简单、灵活、数据验证 |
| **CLI 测试** | paramiko + netmiko | 3.3+ | SSH 连接、命令执行 |
| **报告生成** | Allure Report | 2.24+ | 可视化、历史趋势 |
| **覆盖率** | pytest-cov | 4.1+ | 标准覆盖率工具 |
| **CI 平台** | GitLab CI/CD | 16.0+ | 自托管、Docker 原生 |
| **容器化** | Docker + Docker Compose | 24.0+ | 环境隔离、易于部署 |
| **数据存储** | PostgreSQL | 15+ | 主流关系型数据库，支持复杂查询 |
| **Web 服务** | Flask | 3.0+ | 轻量级，本地报告查看 |
| **拓扑管理** | JSON 配置 | - | 灵活定义网络拓扑 |

---

## 2. 整体架构设计

### 2.1 架构全景图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        本地化测试框架架构                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐     │
│  │                        触发层 (Trigger)                             │     │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │     │
│  │  │ Git Push    │  │ Merge Req   │  │  定时触发   │  │  本地命令   │ │     │
│  │  │  (Webhook)  │  │  (Webhook)  │  │  (Schedule) │  │  (pytest)   │ │     │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │     │
│  └─────────────────────────────────────────────────────────────────────┘     │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐     │
│  │                      CI 平台层 (GitLab CI)                            │     │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │     │
│  │  │  Pipeline   │  │  Stages     │  │  Jobs       │                  │     │
│  │  │  定义       │  │  (并行/串行) │  │  (容器执行) │                  │     │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                  │     │
│  └─────────────────────────────────────────────────────────────────────┘     │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐     │
│  │                    测试执行层 (pytest + CLI/API)                       │     │
│  │  ┌─────────────────────────────────────────────────────────────┐    │     │
│  │  │  pytest 核心引擎                                             │    │     │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │    │     │
│  │  │  │  Fixture    │  │  Plugin     │  │  Marker    │           │    │     │
│  │  │  │  依赖注入   │  │  扩展能力   │  │  测试标记   │           │    │     │
│  │  │  └─────────────┘  └─────────────┘  └─────────────┘           │    │     │
│  │  └─────────────────────────────────────────────────────────────┘    │     │
│  │  ┌─────────────────────────────────────────────────────────────┐    │     │
│  │  │  测试类型                                                   │    │     │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │    │     │
│  │  │  │  CLI 测试   │  │  API 测试   │  │  功能测试   │  │  UI 测试    │           │    │     │
│  │  │  │  (paramiko) │  │  (requests) │  │  (集成测试) │  │  (Playwright)│           │    │     │
│  │  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘           │    │     │
│  │  └─────────────────────────────────────────────────────────────┘    │     │
│  └─────────────────────────────────────────────────────────────────────┘     │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐     │
│  │                        结果处理层                                    │     │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │     │
│  │  │ Allure      │  │ JUnit XML   │  │  覆盖率     │  │  PostgreSQL  │ │     │
│  │  │  报告生成   │  │  格式转换   │  │  (pytest-cov)│  │  历史存储   │ │     │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │     │
│  └─────────────────────────────────────────────────────────────────────┘     │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐     │
│  │                        可视化与通知层 (本地)                            │     │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │     │
│  │  │ Allure      │  │ Flask Web   │  │  邮件通知   │  │  桌面通知   │ │     │
│  │  │  HTML 报告  │  │  报告服务器  │  │  (SMTP)    │  │  (可选)    │ │     │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │     │
│  └─────────────────────────────────────────────────────────────────────┘     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 核心组件关系

```
pytest (核心)
  ├── pytest-allure (报告插件)
  ├── pytest-cov (覆盖率插件)
  ├── pytest-xdist (并行执行)
  ├── pytest-html (HTML 报告)
  └── pytest-env (环境变量管理)

防火墙连接
  ├── paramiko (SSH 连接)
  ├── netmiko (CLI 执行)
  └── requests (API 调用)

测试数据
  ├── fixtures (测试夹具)
  ├── conftest.py (共享配置)
  ├── test_data/ (测试数据文件)
  └── topology/ (网络拓扑配置)

报告系统
  ├── Allure (可视化报告)
  ├── PostgreSQL (历史数据)
  └── Flask (Web 服务)
```

---

## 3. 项目目录结构

### 3.1 标准目录结构

```
test_framework/
├── .git/                          # Git 仓库
├── .gitlab-ci.yml                 # GitLab CI 配置
├── .gitignore                     # Git 忽略文件
├── README.md                      # 项目说明
├── pyproject.toml                 # 项目配置 (PEP 518)
├── requirements.txt               # Python 依赖
├── requirements-dev.txt           # 开发依赖
│
├── pytest.ini                     # pytest 配置
├── conftest.py                    # 全局 fixtures
│
├── src/                           # 源代码
│   ├── __init__.py
│   ├── core/                      # 核心框架
│   │   ├── __init__.py
│   │   ├── fixtures.py            # 自定义 fixtures
│   │   ├── plugins/               # pytest 插件
│   │   │   ├── __init__.py
│   │   │   ├── allure_helper.py   # Allure 辅助
│   │   │   ├── db_helper.py       # 数据库辅助
│   │   │   └── env_helper.py      # 环境辅助
│   │   └── utils/                 # 工具函数
│   │       ├── __init__.py
│   │       ├── api_client.py      # API 客户端
│   │       ├── cli_client.py      # CLI 客户端
│   │       ├── config.py          # 配置管理
│   │       └── logger.py          # 日志工具
│   │
│   └── firewall/                  # 防火墙专用模块
│       ├── __init__.py
│       ├── sonicos_api.py         # SonicOS API 封装
│       ├── sonicos_cli.py         # SonicOS CLI 封装
│       └── access_helper.py       # 访问控制操作辅助
│
├── tests/                         # 测试用例
│   ├── __init__.py
│   ├── conftest.py                # 测试 fixtures
│   │
│   ├── unit/                      # 单元测试
│   │   ├── __init__.py
│   │   ├── test_utils.py
│   │   └── test_api_client.py
│   │
│   ├── api/                       # API 测试
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_firewall_config.py
│   │   └── test_network_policy.py
│   │
│   ├── cli/                       # CLI 测试
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_cli_auth.py
│   │   ├── test_cli_config.py
│   │   └── test_cli_commands.py
│   │
│   ├── functional/                # 功能测试
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_access_rules.py   # 访问规则测试
│   │   ├── test_firewall_policies.py # 防火墙策略测试
│   │   └── test_network_security.py  # 网络安全测试
│   │
│   └── ui/                        # UI 测试
│       ├── __init__.py
│       ├── conftest.py
│       ├── test_login_page.py     # 登录页面测试
│       ├── test_dashboard.py      # 仪表板测试
│       └── test_config_pages.py   # 配置页面测试
│
├── topology/                      # 网络拓扑配置
│   ├── basic_topology.json        # 基础拓扑
│   ├── acl_test_topology.json    # ACL 测试拓扑
│   └── topology_loader.py        # 拓扑加载器
│
├── test_data/                     # 测试数据
│   ├── firewall_config.json       # 防火墙配置
│   ├── acl_rules.json             # ACL 规则
│   └── payloads/                  # API 载荷
│       ├── create_acl.json
│       └── update_policy.json
│
├── reports/                       # 报告输出
│   ├── allure/                    # Allure 原始数据
│   ├── allure-report/             # Allure HTML 报告
│   ├── html/                      # pytest HTML 报告
│   └── coverage/                  # 覆盖率报告
│
├── data/                          # 数据存储
│   └── init_db.sql                # PostgreSQL 初始化脚本
│
├── docker/                        # Docker 配置
│   ├── Dockerfile                 # 测试镜像
│   ├── docker-compose.yml        # 本地编排
│   └── docker-compose.ci.yml      # CI 编排
│
├── scripts/                       # 辅助脚本
│   ├── setup.sh                   # 环境初始化
│   ├── run_tests.sh               # 运行测试
│   ├── generate_report.sh         # 生成报告
│   └── serve_report.sh           # 启动报告服务
│
└── docs/                          # 文档
    ├── installation.md            # 安装指南
    ├── usage.md                   # 使用指南
    ├── writing_tests.md           # 编写测试
    └── troubleshooting.md         # 故障排查
```

### 3.2 配置文件说明

**pyproject.toml**:
```toml
[project]
name = "test-framework"
version = "1.0.0"
description = "Firewall test framework with pytest (CLI/API/Functional/UI)"
requires-python = ">=3.10"
dependencies = [
    "pytest>=8.0.0",
    "pytest-allure-adaptor>=1.0.0",
    "pytest-cov>=4.1.0",
    "pytest-xdist>=3.5.0",
    "pytest-html>=4.1.0",
    "pytest-env>=1.1.0",
    "allure-python>=2.24.0",
    "requests>=2.31.0",
    "paramiko>=3.3.0",
    "playwright>=1.40.0",
    "pytest-playwright>=0.5.0",
    "pydantic>=2.5.0",
    "python-dotenv>=1.0.0",
    "psycopg2-binary>=2.9.0",
    "sqlalchemy>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "black>=24.0.0",
    "ruff>=0.1.0",
    "mypy>=1.8.0",
    "pre-commit>=3.6.0",
]

[tool.pytest.ini_options]
minversion = "8.0"
addopts = [
    "-ra",
    "-q",
    "--strict-markers",
    "--alluredir=reports/allure",
    "--cov=src",
    "--cov-report=html:reports/coverage",
    "--cov-report=term-missing",
]
testpaths = ["tests"]
markers = [
    "unit: Unit tests",
    "api: API tests",
    "cli: CLI tests",
    "functional: Functional tests",
    "ui: UI tests",
    "integration: Integration tests",
    "slow: Slow running tests",
    "smoke: Smoke tests",
]

[tool.black]
line-length = 100
target-version = ["py310"]

[tool.ruff]
line-length = 100
select = ["E", "F", "I", "N", "W"]
```

**pytest.ini**:
```ini
[pytest]
minversion = 8.0
addopts = 
    -ra
    -q
    --strict-markers
    --alluredir=reports/allure
    --cov=src
    --cov-report=html:reports/coverage
    --cov-report=term-missing
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    unit: Unit tests
    api: API tests
    cli: CLI tests
    functional: Functional tests
    ui: UI tests
    integration: Integration tests
    slow: Slow running tests
    smoke: Smoke tests
env =
    ENV=test
    LOG_LEVEL=INFO
```

---

## 4. pytest 配置与插件体系

### 4.1 核心插件配置

**requirements.txt**:
```txt
# 核心框架
pytest==8.0.0

# 报告与覆盖率
pytest-allure-adaptor==1.0.0
allure-python==2.24.0
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

# UI 测试
playwright==1.40.0
pytest-playwright==0.5.0

# 数据验证
pydantic==2.5.0

# 数据库
psycopg2-binary==2.9.0
sqlalchemy==2.0.0

# 代码质量
black==24.0.0
ruff==0.1.0
mypy==1.8.0
```

### 4.2 自定义 Fixtures

**src/core/fixtures.py**:
```python
import pytest
import requests
from typing import Generator
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
    return Logger(config.log_level)

# API 客户端
@pytest.fixture(scope="session")
def api_client(config: Config, logger: Logger) -> APIClient:
    """API 客户端"""
    return APIClient(
        base_url=config.api_base_url,
        timeout=config.api_timeout,
        logger=logger
    )

# CLI 客户端
@pytest.fixture(scope="session")
def cli_client(config: Config, logger: Logger) -> CLIClient:
    """CLI 客户端"""
    return CLIClient(
        host=config.firewall_host,
        username=config.firewall_username,
        password=config.firewall_password,
        port=config.firewall_ssh_port,
        logger=logger
    )

# SonicOS API
@pytest.fixture(scope="session")
def sonicos_api(config: Config, logger: Logger) -> SonicOSAPI:
    """SonicOS API 客户端"""
    return SonicOSAPI(
        host=config.firewall_host,
        username=config.firewall_username,
        password=config.firewall_password,
        port=config.firewall_api_port,
        logger=logger
    )

# SonicOS CLI
@pytest.fixture(scope="session")
def sonicos_cli(config: Config, logger: Logger) -> SonicOSCLI:
    """SonicOS CLI 客户端"""
    return SonicOSCLI(
        host=config.firewall_host,
        username=config.firewall_username,
        password=config.firewall_password,
        port=config.firewall_ssh_port,
        logger=logger
    )

# 数据库会话
@pytest.fixture(scope="session")
def db_session(config: Config):
    """数据库会话"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    engine = create_engine(config.database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

# 测试数据清理
@pytest.fixture(autouse=True)
def cleanup_after_test(db_session):
    """每个测试后清理"""
    yield
    # 清理逻辑
    pass

# 认证 Token
@pytest.fixture(scope="session")
def auth_token(sonicos_api: SonicOSAPI, config: Config) -> str:
    """获取认证 Token"""
    return sonicos_api.login(
        username=config.firewall_username,
        password=config.firewall_password
    )

# 拓扑配置
@pytest.fixture(scope="session")
def topology_config(config: Config):
    """加载网络拓扑配置"""
    import json
    from pathlib import Path
    topo_file = Path("topology") / config.topology_file
    with open(topo_file) as f:
        return json.load(f)
```

### 4.3 自定义插件

**src/core/plugins/allure_helper.py**:
```python
import pytest
import allure
from typing import Any
import json

def allure_attach_json(name: str, data: Any):
    """附加 JSON 到 Allure 报告"""
    allure.attach(
        json.dumps(data, indent=2, ensure_ascii=False),
        name=name,
        attachment_type=allure.attachment_type.JSON
    )

def allure_attach_command_output(command: str, output: str, name: str = "command_output"):
    """附加 CLI 命令输出到 Allure 报告"""
    allure.attach(
        f"Command: {command}\n\nOutput:\n{output}",
        name=name,
        attachment_type=allure.attachment_type.TEXT
    )

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """捕获测试结果并附加信息"""
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call":
        # 附加测试参数
        if hasattr(item, "funcargs"):
            params = {k: str(v) for k, v in item.funcargs.items()}
            allure_attach_json("Test Parameters", params)
        
        # 失败时附加防火墙配置 (CLI/API 测试)
        if report.failed and ("cli" in item.keywords or "api" in item.keywords):
            if "sonicos_cli" in item.funcargs:
                cli = item.funcargs["sonicos_cli"]
                try:
                    output = cli.execute_command("show configuration")
                    allure_attach_command_output("show configuration", output, "failure_config")
                except:
                    pass
```

**src/core/plugins/db_helper.py**:
```python
import pytest
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class TestResult(Base):
    """测试结果表"""
    __tablename__ = 'test_results'
    id = Column(Integer, primary_key=True, autoincrement=True)
    test_name = Column(String(255), nullable=False)
    test_type = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False)
    duration = Column(Float)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    error_message = Column(Text)
    environment = Column(String(50))
    run_id = Column(String(100))

class TestHistory(Base):
    """测试历史表"""
    __tablename__ = 'test_history'
    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(100), unique=True, nullable=False)
    total_tests = Column(Integer)
    passed = Column(Integer)
    failed = Column(Integer)
    skipped = Column(Integer)
    duration = Column(Float)
    timestamp = Column(DateTime)
    environment = Column(String(50))

class DBHelper:
    """数据库辅助类"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)
        self._init_db()
    
    def _init_db(self):
        """初始化数据库表"""
        Base.metadata.create_all(self.engine)
    
    def save_test_result(self, test_name: str, test_type: str, 
                        status: str, duration: float, 
                        error_message: str = None, run_id: str = None):
        """保存测试结果"""
        session = self.Session()
        try:
            result = TestResult(
                test_name=test_name,
                test_type=test_type,
                status=status,
                duration=duration,
                start_time=datetime.now(),
                end_time=datetime.now(),
                error_message=error_message,
                environment=pytest.config.getoption("env") or "test",
                run_id=run_id
            )
            session.add(result)
            session.commit()
        finally:
            session.close()
    
    def save_run_summary(self, run_id: str, total: int, passed: int, 
                        failed: int, skipped: int, duration: float):
        """保存运行摘要"""
        session = self.Session()
        try:
            history = TestHistory(
                run_id=run_id,
                total_tests=total,
                passed=passed,
                failed=failed,
                skipped=skipped,
                duration=duration,
                timestamp=datetime.now(),
                environment=pytest.config.getoption("env") or "test"
            )
            session.merge(history)  # 使用 merge 避免 run_id 冲突
            session.commit()
        finally:
            session.close()
    
    def get_test_history(self, limit: int = 100):
        """获取测试历史"""
        session = self.Session()
        try:
            return session.query(TestHistory).order_by(
                TestHistory.timestamp.desc()
            ).limit(limit).all()
        finally:
            session.close()

@pytest.fixture(scope="session")
def db_helper(config):
    """数据库辅助 fixture"""
    return DBHelper(config.database_url)
```

### 4.4 全局 conftest.py

**conftest.py** (项目根目录):
```python
import pytest
import os
import sys
from pathlib import Path

# 添加 src 到 Python 路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

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
```

---

## 5. CLI 测试实现

### 5.1 CLI 客户端封装

**src/core/utils/cli_client.py**:
```python
import paramiko
from netmiko import ConnectHandler
from typing import Optional, List
from src.core.utils.logger import Logger
from src.core.plugins.allure_helper import allure_attach_command_output

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
            'device_type': 'cisco_ios',  # 可根据防火墙类型调整
            'host': self.host,
            'username': self.username,
            'password': self.password,
            'port': self.port,
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
        output = self.connection.send_command(command, read_timeout=timeout)
        
        # 附加到 Allure
        allure_attach_command_output(command, output)
        
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
```

### 5.2 SonicOS CLI 封装

**src/firewall/sonicos_cli.py**:
```python
from src.core.utils.cli_client import CLIClient
from typing import Dict, List

class SonicOSCLI(CLIClient):
    """SonicOS CLI 专用客户端"""
    
    def __init__(self, host: str, username: str, password: str, 
                 port: int = 22, logger=None):
        super().__init__(host, username, password, port, logger)
        self.device_type = 'sonicos'  # 自定义设备类型
    
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
        return {}
    
    def _parse_interface_status(self, output: str) -> Dict:
        """解析接口状态输出"""
        # 实现解析逻辑
        return {}
    
    def _format_acl_rule(self, rule: Dict) -> str:
        """格式化 ACL 规则"""
        # 实现格式化逻辑
        return ""
```

### 5.3 CLI 测试示例

**tests/cli/test_cli_auth.py**:
```python
import pytest
from src.firewall.sonicos_cli import SonicOSCLI

@pytest.mark.cli
class TestCLIAuth:
    """CLI 认证测试"""
    
    def test_ssh_connection(self, sonicos_cli: SonicOSCLI):
        """测试 SSH 连接"""
        with sonicos_cli:
            output = sonicos_cli.execute_command("show version")
            assert "SonicOS" in output
    
    def test_cli_login(self, sonicos_cli: SonicOSCLI, config):
        """测试 CLI 登录"""
        with sonicos_cli:
            output = sonicos_cli.execute_command("show user")
            assert config.firewall_username in output
```

**tests/cli/test_cli_config.py**:
```python
import pytest
from src.firewall.sonicos_cli import SonicOSCLI

@pytest.mark.cli
class TestCLIConfig:
    """CLI 配置测试"""
    
    def test_show_configuration(self, sonicos_cli: SonicOSCLI):
        """测试显示配置"""
        with sonicos_cli:
            output = sonicos_cli.execute_command("show configuration")
            assert len(output) > 0
    
    def test_interface_status(self, sonicos_cli: SonicOSCLI):
        """测试接口状态"""
        with sonicos_cli:
            status = sonicos_cli.get_interface_status()
            assert "interfaces" in status
```

---

## 6. 功能测试实现

### 6.1 访问控制辅助类

**src/firewall/access_helper.py**:
```python
from typing import Dict, List
from src.firewall.sonicos_api import SonicOSAPI
from src.firewall.sonicos_cli import SonicOSCLI

class AccessHelper:
    """访问控制操作辅助类"""
    
    def __init__(self, api_client: SonicOSAPI = None, cli_client: SonicOSCLI = None):
        self.api_client = api_client
        self.cli_client = cli_client
    
    def create_access_rule_via_api(self, rule_name: str, rules: List[Dict]) -> Dict:
        """通过 API 创建访问规则"""
        if not self.api_client:
            raise ValueError("API client not configured")
        
        payload = {
            "name": rule_name,
            "rules": rules
        }
        return self.api_client.post("/api/access-control", json=payload)
    
    def create_access_rule_via_cli(self, rule_name: str, rules: List[Dict]) -> str:
        """通过 CLI 创建访问规则"""
        if not self.cli_client:
            raise ValueError("CLI client not configured")
        
        return self.cli_client.configure_access_control(rule_name, rules)
    
    def delete_access_rule_via_api(self, rule_name: str) -> Dict:
        """通过 API 删除访问规则"""
        if not self.api_client:
            raise ValueError("API client not configured")
        
        return self.api_client.delete(f"/api/access-control/{rule_name}")
    
    def delete_access_rule_via_cli(self, rule_name: str) -> str:
        """通过 CLI 删除访问规则"""
        if not self.cli_client:
            raise ValueError("CLI client not configured")
        
        commands = [
            f"no access-list {rule_name}",
            "exit"
        ]
        return self.cli_client.execute_config(commands)
    
    def verify_access_rule(self, rule_name: str, rule: Dict) -> bool:
        """验证访问规则"""
        if self.cli_client:
            output = self.cli_client.show_access_control(rule_name)
            return self._rule_in_output(rule, output)
        elif self.api_client:
            response = self.api_client.get(f"/api/access-control/{rule_name}")
            return self._rule_in_response(rule, response.json())
        return False
    
    def _rule_in_output(self, rule: Dict, output: str) -> bool:
        """检查规则是否在 CLI 输出中"""
        # 实现检查逻辑
        return True
    
    def _rule_in_response(self, rule: Dict, response: Dict) -> bool:
        """检查规则是否在 API 响应中"""
        # 实现检查逻辑
        return True
```

### 6.2 功能测试示例

**tests/functional/test_access_rules.py**:
```python
import pytest
from src.firewall.access_helper import AccessHelper

@pytest.mark.functional
class TestAccessRules:
    """访问规则功能测试"""
    
    @pytest.fixture(scope="function")
    def access_helper(self, sonicos_api, sonicos_cli):
        """访问控制辅助 fixture"""
        return AccessHelper(api_client=sonicos_api, cli_client=sonicos_cli)
    
    def test_create_access_rule_via_api(self, access_helper: AccessHelper):
        """测试通过 API 创建访问规则"""
        rule_name = "test_access_api"
        rules = [
            {
                "action": "permit",
                "source": "192.168.1.0/24",
                "destination": "any",
                "protocol": "tcp"
            }
        ]
        
        response = access_helper.create_access_rule_via_api(rule_name, rules)
        assert response.status_code == 201
        
        # 清理
        access_helper.delete_access_rule_via_api(rule_name)
    
    def test_create_access_rule_via_cli(self, access_helper: AccessHelper):
        """测试通过 CLI 创建访问规则"""
        rule_name = "test_access_cli"
        rules = [
            {
                "action": "deny",
                "source": "10.0.0.0/8",
                "destination": "any",
                "protocol": "ip"
            }
        ]
        
        output = access_helper.create_access_rule_via_cli(rule_name, rules)
        assert "Success" in output
        
        # 清理
        access_helper.delete_access_rule_via_cli(rule_name)
    
    def test_verify_access_rule(self, access_helper: AccessHelper):
        """测试验证访问规则"""
        rule_name = "test_access_verify"
        rules = [
            {
                "action": "permit",
                "source": "172.16.0.0/16",
                "destination": "any",
                "protocol": "tcp"
            }
        ]
        
        access_helper.create_access_rule_via_api(rule_name, rules)
        
        # 验证规则
        assert access_helper.verify_access_rule(rule_name, rules[0])
        
        # 清理
        access_helper.delete_access_rule_via_api(rule_name)
```

**tests/functional/test_firewall_policies.py**:
```python
import pytest
from src.firewall.access_helper import AccessHelper

@pytest.mark.functional
class TestFirewallPolicies:
    """防火墙策略功能测试"""
    
    @pytest.fixture(scope="function")
    def access_helper(self, sonicos_api, sonicos_cli):
        return AccessHelper(api_client=sonicos_api, cli_client=sonicos_cli)
    
    def test_create_firewall_policy(self, access_helper: AccessHelper):
        """测试创建防火墙策略"""
        policy_name = "test_firewall_policy"
        policy_data = {
            "name": policy_name,
            "action": "allow",
            "source_zone": "LAN",
            "destination_zone": "WAN",
            "service": "HTTP"
        }
        
        response = access_helper.create_policy_via_api(policy_data)
        assert response.status_code == 201
        
        # 清理
        access_helper.delete_policy_via_api(policy_name)
    
    def test_policy_order(self, access_helper: AccessHelper):
        """测试策略顺序"""
        # 创建多个策略
        policies = [
            {"name": "policy_1", "priority": 100},
            {"name": "policy_2", "priority": 200}
        ]
        
        for policy in policies:
            access_helper.create_policy_via_api(policy)
        
        # 验证顺序
        policy_list = access_helper.get_policy_list()
        assert policy_list[0]["name"] == "policy_1"
        
        # 清理
        for policy in policies:
            access_helper.delete_policy_via_api(policy["name"])
```

---

## 7. UI 测试实现

### 7.1 Playwright 配置

**tests/ui/conftest.py**:
```python
import pytest
from playwright.sync_api import Page, expect
from src.core.utils.config import Config

@pytest.fixture(scope="function")
def ui_page(page: Page, config: Config):
    """UI 页面 fixture"""
    page.goto(config.firewall_ui_url)
    page.set_viewport_size({"width": 1280, "height": 720})
    return page

@pytest.fixture(scope="function")
def authenticated_page(page: Page, config: Config):
    """已认证页面 fixture"""
    page.goto(config.firewall_ui_url)
    
    # 登录
    page.fill("input[name='username']", config.firewall_username)
    page.fill("input[name='password']", config.firewall_password)
    page.click("button[type='submit']")
    
    # 等待登录成功
    expect(page.locator(".dashboard")).to_be_visible()
    
    return page
```

### 7.2 UI 测试示例

**tests/ui/test_login_page.py**:
```python
import pytest
from playwright.sync_api import Page, expect

@pytest.mark.ui
class TestLoginPage:
    """登录页面 UI 测试"""
    
    def test_page_title(self, ui_page: Page):
        """测试页面标题"""
        expect(ui_page).to_have_title("SonicOS Login")
    
    def test_login_form_elements(self, ui_page: Page):
        """测试登录表单元素"""
        expect(ui_page.locator("input[name='username']")).to_be_visible()
        expect(ui_page.locator("input[name='password']")).to_be_visible()
        expect(ui_page.locator("button[type='submit']")).to_be_visible()
    
    def test_successful_login(self, ui_page: Page, config: Config):
        """测试成功登录"""
        ui_page.fill("input[name='username']", config.firewall_username)
        ui_page.fill("input[name='password']", config.firewall_password)
        ui_page.click("button[type='submit']")
        
        expect(ui_page.locator(".dashboard")).to_be_visible()
    
    def test_login_with_invalid_credentials(self, ui_page: Page):
        """测试无效凭据登录"""
        ui_page.fill("input[name='username']", "invalid")
        ui_page.fill("input[name='password']", "invalid")
        ui_page.click("button[type='submit']")
        
        expect(ui_page.locator(".error-message")).to_be_visible()
        expect(ui_page.locator(".error-message")).to_contain_text("Invalid credentials")
```

**tests/ui/test_dashboard.py**:
```python
import pytest
from playwright.sync_api import Page, expect

@pytest.mark.ui
class TestDashboard:
    """仪表板 UI 测试"""
    
    def test_dashboard_header(self, authenticated_page: Page):
        """测试仪表板标题"""
        expect(authenticated_page.locator("h1")).to_contain_text("Dashboard")
    
    def test_system_info_widget(self, authenticated_page: Page):
        """测试系统信息组件"""
        expect(authenticated_page.locator(".system-info")).to_be_visible()
        expect(authenticated_page.locator(".system-status")).to_be_visible()
    
    def test_navigation_menu(self, authenticated_page: Page):
        """测试导航菜单"""
        expect(authenticated_page.locator(".nav-menu")).to_be_visible()
        expect(authenticated_page.locator("a[href='/config']")).to_be_visible()
        expect(authenticated_page.locator("a[href='/monitor']")).to_be_visible()
    
    def test_logout_functionality(self, authenticated_page: Page):
        """测试登出功能"""
        authenticated_page.click("button.logout")
        
        expect(authenticated_page.locator(".login-form")).to_be_visible()
```

**tests/ui/test_config_pages.py**:
```python
import pytest
from playwright.sync_api import Page, expect

@pytest.mark.ui
class TestConfigPages:
    """配置页面 UI 测试"""
    
    def test_access_rules_page(self, authenticated_page: Page):
        """测试访问规则页面"""
        authenticated_page.click("a[href='/config/access-rules']")
        
        expect(authenticated_page.locator("h1")).to_contain_text("Access Rules")
        expect(authenticated_page.locator(".rules-table")).to_be_visible()
        expect(authenticated_page.locator("button.add-rule")).to_be_visible()
    
    def test_create_access_rule_dialog(self, authenticated_page: Page):
        """测试创建访问规则对话框"""
        authenticated_page.click("a[href='/config/access-rules']")
        authenticated_page.click("button.add-rule")
        
        expect(authenticated_page.locator(".modal")).to_be_visible()
        expect(authenticated_page.locator("input[name='rule-name']")).to_be_visible()
        expect(authenticated_page.locator("select[name='action']")).to_be_visible()
    
    def test_firewall_settings_page(self, authenticated_page: Page):
        """测试防火墙设置页面"""
        authenticated_page.click("a[href='/config/firewall']")
        
        expect(authenticated_page.locator("h1")).to_contain_text("Firewall Settings")
        expect(authenticated_page.locator(".settings-form")).to_be_visible()
        expect(authenticated_page.locator("button.save-settings")).to_be_visible()
```

---

## 8. API 测试实现

### 8.1 SonicOS API 封装

**src/firewall/sonicos_api.py**:
```python
import requests
from typing import Dict, Any, Optional
from src.core.utils.logger import Logger
from src.core.plugins.allure_helper import allure_attach_json

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
    
    def login(self, username: str = None, password: str = None) -> str:
        """登录获取 Token"""
        username = username or self.username
        password = password or self.password
        
        response = self.session.post(
            f"{self.base_url}/auth/login",
            json={"username": username, "password": password},
            verify=False,
            timeout=self.timeout
        )
        
        if response.status_code == 200:
            self.token = response.json().get("token")
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
            return self.token
        else:
            raise Exception(f"Login failed: {response.text}")
    
    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """通用请求方法"""
        url = f"{self.base_url}{endpoint}"
        
        self.logger.info(f"{method} {url}")
        
        # 附加到 Allure
        allure_attach_json(f"Request ({method})", {
            "url": url,
            "headers": dict(self.session.headers),
            "body": kwargs.get("json") or kwargs.get("data")
        })
        
        response = self.session.request(method, url, verify=False, timeout=self.timeout, **kwargs)
        
        self.logger.info(f"Response: {response.status_code}")
        
        # 附加响应到 Allure
        try:
            allure_attach_json(f"Response ({response.status_code})", response.json())
        except:
            allure_attach_json(f"Response ({response.status_code})", {"text": response.text})
        
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
```

### 8.2 API 测试示例

**tests/api/test_firewall_config.py**:
```python
import pytest
from src.firewall.sonicos_api import SonicOSAPI

@pytest.mark.api
class TestFirewallConfigAPI:
    """防火墙配置 API 测试"""
    
    def test_get_system_info(self, sonicos_api: SonicOSAPI):
        """测试获取系统信息"""
        info = sonicos_api.get_system_info()
        assert "hostname" in info
        assert "version" in info
        assert "model" in info
    
    def test_get_interface_config(self, sonicos_api: SonicOSAPI):
        """测试获取接口配置"""
        config = sonicos_api.get_interface_config()
        assert "interfaces" in config
        assert isinstance(config["interfaces"], list)
    
    def test_get_specific_interface(self, sonicos_api: SonicOSAPI):
        """测试获取指定接口配置"""
        config = sonicos_api.get_interface_config("X0")
        assert "name" in config
        assert config["name"] == "X0"
```

**tests/api/test_network_policy.py**:
```python
import pytest
from src.firewall.sonicos_api import SonicOSAPI

@pytest.mark.api
class TestNetworkPolicyAPI:
    """网络策略 API 测试"""
    
    def test_get_acl_list(self, sonicos_api: SonicOSAPI):
        """测试获取 ACL 列表"""
        acl_list = sonicos_api.get_acl_list()
        assert "acls" in acl_list
        assert isinstance(acl_list["acls"], list)
    
    def test_get_specific_acl(self, sonicos_api: SonicOSAPI):
        """测试获取指定 ACL"""
        # 假设存在一个测试 ACL
        acl = sonicos_api.get_acl("test_acl")
        assert "name" in acl
        assert acl["name"] == "test_acl"
    
    def test_create_acl_via_api(self, sonicos_api: SonicOSAPI):
        """测试通过 API 创建 ACL"""
        acl_data = {
            "name": "test_api_acl",
            "rules": [
                {
                    "action": "permit",
                    "source": "192.168.1.0/24",
                    "destination": "any",
                    "protocol": "tcp"
                }
            ]
        }
        
        response = sonicos_api.post("/acl", json=acl_data)
        assert response.status_code == 201
        
        # 清理
        sonicos_api.delete(f"/acl/test_api_acl")
```


---

## 9. GitLab CI/CD 集成

### 9.1 GitLab CI 配置

**.gitlab-ci.yml**:
```yaml
# 全局变量
variables:
  PYTHON_VERSION: "3.11"
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: ""
  ALLURE_RESULTS_DIR: "reports/allure"
  ALLURE_REPORT_DIR: "reports/allure-report"

# 定义阶段
stages:
  - lint
  - unit
  - api
  - cli
  - functional
  - ui
  - integration
  - report
  - deploy

# 缓存配置
cache:
  key: ${CI_COMMIT_REF_SLUG}
  paths:
    - .venv/
    - .pip-cache/

# 代码检查
lint:python:
  stage: lint
  image: python:${PYTHON_VERSION}-slim
  before_script:
    - pip install black ruff mypy
  script:
    - black --check src/ tests/
    - ruff check src/ tests/
    - mypy src/
  only:
    - merge_requests
    - main

# 单元测试
test:unit:
  stage: unit
  image: python:${PYTHON_VERSION}-slim
  before_script:
    - pip install -r requirements.txt
    - pip install -r requirements-dev.txt
  script:
    - pytest tests/unit/ -v --junitxml=reports/unit-junit.xml
  artifacts:
    reports:
      junit: reports/unit-junit.xml
    paths:
      - reports/
    expire_in: 7 days

# API 测试
test:api:
  stage: api
  image: python:${PYTHON_VERSION}-slim
  services:
    - name: postgres:15
      alias: postgres
    - name: redis:7
      alias: redis
  variables:
    POSTGRES_DB: testdb
    POSTGRES_USER: testuser
    POSTGRES_PASSWORD: testpass
    DATABASE_URL: postgresql://testuser:testpass@postgres:5432/testdb
    REDIS_URL: redis://redis:6379
  before_script:
    - pip install -r requirements.txt
  script:
    - pytest tests/api/ -v --junitxml=reports/api-junit.xml --alluredir=$ALLURE_RESULTS_DIR
  artifacts:
    reports:
      junit: reports/api-junit.xml
    paths:
      - $ALLURE_RESULTS_DIR/
    expire_in: 7 days

# CLI 测试
test:cli:
  stage: cli
  image: python:${PYTHON_VERSION}-slim
  before_script:
    - pip install -r requirements.txt
  script:
    - pytest tests/cli/ -v --junitxml=reports/cli-junit.xml --alluredir=$ALLURE_RESULTS_DIR
  artifacts:
    reports:
      junit: reports/cli-junit.xml
    paths:
      - $ALLURE_RESULTS_DIR/
    expire_in: 7 days

# 功能测试
test:functional:
  stage: functional
  image: python:${PYTHON_VERSION}-slim
  before_script:
    - pip install -r requirements.txt
  script:
    - pytest tests/functional/ -v --junitxml=reports/functional-junit.xml --alluredir=$ALLURE_RESULTS_DIR
  artifacts:
    reports:
      junit: reports/functional-junit.xml
    paths:
      - $ALLURE_RESULTS_DIR/
    expire_in: 7 days

# UI 测试
test:ui:
  stage: ui
  image: mcr.microsoft.com/playwright:v1.40.0
  before_script:
    - pip install -r requirements.txt
    - playwright install chromium
  script:
    - pytest tests/ui/ -v --junitxml=reports/ui-junit.xml --alluredir=$ALLURE_RESULTS_DIR
  artifacts:
    reports:
      junit: reports/ui-junit.xml
    paths:
      - $ALLURE_RESULTS_DIR/
    expire_in: 7 days

# 集成测试
test:integration:
  stage: integration
  image: python:${PYTHON_VERSION}-slim
  before_script:
    - pip install -r requirements.txt
  script:
    - pytest tests/integration/ -v --junitxml=reports/integration-junit.xml --alluredir=$ALLURE_RESULTS_DIR
  artifacts:
    reports:
      junit: reports/integration-junit.xml
    paths:
      - $ALLURE_RESULTS_DIR/
    expire_in: 7 days

# 生成 Allure 报告
report:allure:
  stage: report
  image: python:${PYTHON_VERSION}-slim
  dependencies:
    - test:api
    - test:cli
    - test:functional
    - test:ui
    - test:integration
  before_script:
    - pip install allure-pytest
  script:
    - allure generate $ALLURE_RESULTS_DIR -o $ALLURE_REPORT_DIR --clean
  artifacts:
    when: always
    paths:
      - $ALLURE_REPORT_DIR/
    expire_in: 30 days
  only:
    - main
    - merge_requests

# 部署报告
deploy:report:
  stage: deploy
  image: alpine:3.18
  dependencies:
    - report:allure
  script:
    - apk add --no-cache rsync openssh-client
    - mkdir -p ~/.ssh
    - echo "$SSH_PRIVATE_KEY" > ~/.ssh/id_rsa
    - chmod 600 ~/.ssh/id_rsa
    - rsync -avz -e "ssh -o StrictHostKeyChecking=no" $ALLURE_REPORT_DIR/ $REPORT_SERVER:/var/www/allure/$CI_COMMIT_SHORT_SHA/
  only:
    - main
```

### 9.2 Docker 镜像构建

**docker/Dockerfile**:
```dockerfile
FROM python:3.11-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    curl \
    git \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 设置环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import pytest; print('OK')" || exit 1

# 默认命令
CMD ["pytest", "-v"]
```

**docker/docker-compose.yml**:
```yaml
version: '3.8'

services:
  test-framework:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    volumes:
      - ../tests:/app/tests
      - ../src:/app/src
      - ../test_data:/app/test_data
      - ../topology:/app/topology
      - ../reports:/app/reports
    environment:
      - ENV=test
      - LOG_LEVEL=INFO
      - FIREWALL_HOST=${FIREWALL_HOST:-192.168.1.1}
      - FIREWALL_USERNAME=${FIREWALL_USERNAME:-admin}
      - FIREWALL_PASSWORD=${FIREWALL_PASSWORD:-password}
      - FIREWALL_API_PORT=${FIREWALL_API_PORT:-443}
      - FIREWALL_SSH_PORT=${FIREWALL_SSH_PORT:-22}
      - DATABASE_URL=postgresql://testuser:testpass@postgres:5432/testdb
    depends_on:
      - postgres
    networks:
      - test-network

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: testdb
      POSTGRES_USER: testuser
      POSTGRES_PASSWORD: testpass
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ../data/init_db.sql:/docker-entrypoint-initdb.d/init_db.sql
    networks:
      - test-network

  allure:
    image: frankescobar/allure-docker-service
    ports:
      - "5050:5050"
    volumes:
      - ../reports/allure:/app/allure-results
      - allure-reports:/app/allure-report
    environment:
      - CHECK_RESULTS_EVERY_SECONDS=5
      - KEEP_HISTORY=1
    networks:
      - test-network

networks:
  test-network:
    driver: bridge

volumes:
  postgres-data:
  allure-reports:
```

---

## 10. 本地化报告与数据存储

### 10.1 Allure 报告本地化

**scripts/serve_report.sh**:
```bash
#!/bin/bash

# 启动 Allure 报告服务
cd "$(dirname "$0")/.."

# 生成报告
allure generate reports/allure -o reports/allure-report --clean

# 启动服务
echo "Starting Allure report server at http://localhost:5050"
allure open reports/allure-report --port 5050
```

**scripts/generate_report.sh**:
```bash
#!/bin/bash

# 生成 Allure 报告
cd "$(dirname "$0")/.."

echo "Generating Allure report..."
allure generate reports/allure -o reports/allure-report --clean

echo "Report generated at reports/allure-report/index.html"
```

### 10.2 Flask 报告服务器

**src/report_server/app.py**:
```python
from flask import Flask, render_template, send_from_directory, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.plugins.db_helper import TestHistory, TestResult
from pathlib import Path
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# 配置
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://testuser:testpass@localhost:5432/testdb')
ALLURE_REPORT_PATH = Path(__file__).parent.parent.parent / "reports" / "allure-report"

# 数据库连接
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

@app.route('/')
def index():
    """首页"""
    return render_template('index.html')

@app.route('/api/test-history')
def test_history():
    """获取测试历史"""
    session = Session()
    try:
        thirty_days_ago = datetime.now() - timedelta(days=30)
        history = session.query(TestHistory).filter(
            TestHistory.timestamp >= thirty_days_ago
        ).order_by(TestHistory.timestamp.desc()).all()
        
        return jsonify([{
            'run_id': h.run_id,
            'total_tests': h.total_tests,
            'passed': h.passed,
            'failed': h.failed,
            'skipped': h.skipped,
            'duration': h.duration,
            'timestamp': h.timestamp.isoformat() if h.timestamp else None
        } for h in history])
    finally:
        session.close()

@app.route('/api/test-results/<run_id>')
def test_results(run_id):
    """获取指定运行的测试结果"""
    session = Session()
    try:
        results = session.query(TestResult).filter(
            TestResult.run_id == run_id
        ).order_by(TestResult.start_time).all()
        
        return jsonify([{
            'test_name': r.test_name,
            'test_type': r.test_type,
            'status': r.status,
            'duration': r.duration,
            'start_time': r.start_time.isoformat() if r.start_time else None,
            'error_message': r.error_message
        } for r in results])
    finally:
        session.close()

@app.route('/allure')
def allure_report():
    """重定向到 Allure 报告"""
    return send_from_directory(ALLURE_REPORT_PATH, 'index.html')

@app.route('/allure/<path:path>')
def allure_files(path):
    """Allure 静态文件"""
    return send_from_directory(ALLURE_REPORT_PATH, path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

**src/report_server/templates/index.html**:
```html
<!DOCTYPE html>
<html>
<head>
    <title>Test Report Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .card { background: #f5f5f5; padding: 20px; margin: 10px 0; border-radius: 8px; }
        .btn { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .btn:hover { background: #0056b3; }
        #chart { height: 300px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Test Report Dashboard</h1>
        
        <div class="card">
            <h2>Test History (Last 30 Days)</h2>
            <canvas id="chart"></canvas>
        </div>
        
        <div class="card">
            <h2>Actions</h2>
            <button class="btn" onclick="window.location.href='/allure'">View Allure Report</button>
        </div>
        
        <div class="card">
            <h2>Recent Runs</h2>
            <table id="runs-table">
                <thead>
                    <tr>
                        <th>Run ID</th>
                        <th>Total</th>
                        <th>Passed</th>
                        <th>Failed</th>
                        <th>Duration</th>
                        <th>Timestamp</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>
    </div>
    
    <script>
        // 加载测试历史
        fetch('/api/test-history')
            .then(response => response.json())
            .then(data => {
                // 渲染图表
                renderChart(data);
                // 渲染表格
                renderTable(data);
            });
        
        function renderChart(data) {
            const ctx = document.getElementById('chart').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.map(d => d.timestamp),
                    datasets: [{
                        label: 'Pass Rate (%)',
                        data: data.map(d => (d.passed / d.total_tests * 100).toFixed(2)),
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1
                    }]
                }
            });
        }
        
        function renderTable(data) {
            const tbody = document.querySelector('#runs-table tbody');
            data.forEach(run => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${run.run_id}</td>
                    <td>${run.total_tests}</td>
                    <td>${run.passed}</td>
                    <td>${run.failed}</td>
                    <td>${run.duration}s</td>
                    <td>${run.timestamp}</td>
                `;
                tbody.appendChild(row);
            });
        }
    </script>
</body>
</html>
```

### 10.3 PostgreSQL 数据库初始化

**data/init_db.sql**:
```sql
-- 测试结果表
CREATE TABLE IF NOT EXISTS test_results (
    id SERIAL PRIMARY KEY,
    test_name VARCHAR(255) NOT NULL,
    test_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    duration REAL,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    error_message TEXT,
    environment VARCHAR(50),
    run_id VARCHAR(100)
);

-- 测试历史表
CREATE TABLE IF NOT EXISTS test_history (
    id SERIAL PRIMARY KEY,
    run_id VARCHAR(100) UNIQUE NOT NULL,
    total_tests INTEGER,
    passed INTEGER,
    failed INTEGER,
    skipped INTEGER,
    duration REAL,
    timestamp TIMESTAMP,
    environment VARCHAR(50)
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_test_results_run_id ON test_results(run_id);
CREATE INDEX IF NOT EXISTS idx_test_results_timestamp ON test_results(start_time);
CREATE INDEX IF NOT EXISTS idx_test_history_timestamp ON test_history(timestamp);
```

---

## 11. 网络拓扑配置

### 11.1 拓扑配置文件

**topology/basic_topology.json**:
```json
{
  "name": "basic_firewall_test",
  "description": "Basic firewall testing topology",
  "devices": [
    {
      "name": "firewall",
      "type": "sonicos",
      "host": "192.168.1.1",
      "role": "dut",
      "interfaces": [
        {
          "name": "X0",
          "ip": "192.168.1.1",
          "subnet": "192.168.1.0/24",
          "zone": "LAN"
        },
        {
          "name": "X1",
          "ip": "10.0.0.1",
          "subnet": "10.0.0.0/24",
          "zone": "WAN"
        }
      ]
    },
    {
      "name": "pc1",
      "type": "linux",
      "host": "192.168.1.100",
      "role": "client",
      "gateway": "192.168.1.1"
    },
    {
      "name": "pc2",
      "type": "linux",
      "host": "10.0.0.100",
      "role": "server",
      "gateway": "10.0.0.1"
    }
  ],
  "connections": [
    {
      "source": "pc1",
      "source_interface": "eth0",
      "destination": "firewall",
      "destination_interface": "X0"
    },
    {
      "source": "firewall",
      "source_interface": "X1",
      "destination": "pc2",
      "destination_interface": "eth0"
    }
  ]
}
```

**topology/acl_test_topology.json**:
```json
{
  "name": "acl_test_topology",
  "description": "ACL functionality testing topology",
  "devices": [
    {
      "name": "firewall",
      "type": "sonicos",
      "host": "192.168.1.1",
      "role": "dut",
      "interfaces": [
        {
          "name": "X0",
          "ip": "192.168.1.1",
          "subnet": "192.168.1.0/24",
          "zone": "LAN"
        },
        {
          "name": "X1",
          "ip": "10.0.0.1",
          "subnet": "10.0.0.0/24",
          "zone": "WAN"
        },
        {
          "name": "X2",
          "ip": "172.16.0.1",
          "subnet": "172.16.0.0/24",
          "zone": "DMZ"
        }
      ]
    },
    {
      "name": "lan_client",
      "type": "linux",
      "host": "192.168.1.100",
      "role": "client",
      "gateway": "192.168.1.1"
    },
    {
      "name": "wan_server",
      "type": "linux",
      "host": "10.0.0.100",
      "role": "server",
      "gateway": "10.0.0.1"
    },
    {
      "name": "dmz_server",
      "type": "linux",
      "host": "172.16.0.100",
      "role": "server",
      "gateway": "172.16.0.1"
    }
  ]
}
```

### 11.2 拓扑加载器

**topology/topology_loader.py**:
```python
import json
from pathlib import Path
from typing import Dict, List

class TopologyLoader:
    """网络拓扑加载器"""
    
    def __init__(self, topology_file: str):
        self.topology_file = Path("topology") / topology_file
        self.topology = self._load_topology()
    
    def _load_topology(self) -> Dict:
        """加载拓扑配置"""
        with open(self.topology_file) as f:
            return json.load(f)
    
    def get_device(self, name: str) -> Dict:
        """获取设备信息"""
        for device in self.topology["devices"]:
            if device["name"] == name:
                return device
        raise ValueError(f"Device {name} not found in topology")
    
    def get_dut(self) -> Dict:
        """获取 DUT (被测设备)"""
        for device in self.topology["devices"]:
            if device.get("role") == "dut":
                return device
        raise ValueError("No DUT found in topology")
    
    def get_devices_by_role(self, role: str) -> List[Dict]:
        """根据角色获取设备列表"""
        return [d for d in self.topology["devices"] if d.get("role") == role]
    
    def get_connection(self, source: str, destination: str) -> Dict:
        """获取连接信息"""
        for conn in self.topology["connections"]:
            if conn["source"] == source and conn["destination"] == destination:
                return conn
        raise ValueError(f"Connection {source} -> {destination} not found")
```

---

## 12. 快速开始指南

### 12.1 环境初始化

**scripts/setup.sh**:
```bash
#!/bin/bash

echo "Setting up firewall test framework..."

# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 初始化 PostgreSQL 数据库
sudo -u postgres psql -c "CREATE DATABASE testdb;" 2>/dev/null || true
sudo -u postgres psql -c "CREATE USER testuser WITH PASSWORD 'testpass';" 2>/dev/null || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE testdb TO testuser;" 2>/dev/null || true
psql -U testuser -d testdb -f data/init_db.sql

# 创建报告目录
mkdir -p reports/allure
mkdir -p reports/html
mkdir -p reports/coverage
mkdir -p data
mkdir -p topology

echo "Setup complete!"
```

### 12.2 配置环境变量

**.env**:
```bash
# 防火墙配置
FIREWALL_HOST=192.168.1.1
FIREWALL_USERNAME=admin
FIREWALL_PASSWORD=your_password
FIREWALL_API_PORT=443
FIREWALL_SSH_PORT=22

# 测试环境
ENV=test
LOG_LEVEL=INFO

# 拓扑配置
TOPOLOGY_FILE=basic_topology.json

# 数据库
DATABASE_URL=postgresql://testuser:testpass@localhost:5432/testdb
```

### 12.3 运行测试

**scripts/run_tests.sh**:
```bash
#!/bin/bash

# 运行所有测试
pytest -v

# 运行特定类型测试
pytest -v -m unit          # 单元测试
pytest -v -m api           # API 测试
pytest -v -m cli           # CLI 测试
pytest -v -m functional    # 功能测试
pytest -v -m ui            # UI 测试
pytest -v -m integration   # 集成测试

# 并行执行
pytest -v -n auto

# 生成报告
pytest -v --alluredir=reports/allure
allure generate reports/allure -o reports/allure-report
```

### 12.4 本地开发工作流

```bash
# 1. 环境初始化
./scripts/setup.sh

# 2. 运行测试
pytest -v

# 3. 查看报告
./scripts/serve_report.sh

# 4. 代码检查
black src/ tests/
ruff check src/ tests/

# 5. 提交代码
git add .
git commit -m "Add new tests"
git push
```

---

## 13. 实施路线图

### 13.1 分阶段实施

| 阶段 | 任务 | 周期 | 交付物 |
|------|------|------|--------|
| **Phase 1** | 基础框架搭建 | 1 周 | 项目结构、pytest 配置 |
| **Phase 2** | API 测试框架 | 1 周 | API 客户端、测试用例 |
| **Phase 3** | CLI 测试框架 | 1 周 | CLI 客户端、测试用例 |
| **Phase 4** | 功能测试框架 | 1 周 | 访问控制、策略测试 |
| **Phase 5** | UI 测试框架 | 1 周 | Playwright、页面测试 |
| **Phase 6** | 报告系统 | 1 周 | Allure + PostgreSQL + Flask |
| **Phase 7** | GitLab CI 集成 | 1 周 | CI/CD 流水线 |
| **Phase 8** | Docker 容器化 (可选) | 1 周 | Dockerfile + Compose |
| **Phase 9** | 文档与培训 | 1 周 | 使用文档、培训材料 |

### 13.2 验收标准

| 标准 | 描述 |
|------|------|
| **本地运行** | 无需外网即可运行所有测试 |
| **报告生成** | 测试完成后自动生成 HTML 报告 |
| **CI 集成** | Git Push 自动触发 CI 流水线 |
| **并行执行** | 支持多进程并行执行测试 |
| **历史追溯** | PostgreSQL 存储历史测试结果 |
| **功能测试** | 功能测试覆盖核心功能 |
| **UI 测试** | UI 测试覆盖主要页面 |
| **API 测试** | API 测试覆盖核心接口 |

---

## 14. 附录

### 14.1 常用命令

```bash
# 运行测试
pytest -v                                    # 详细输出
pytest -v -s                                 # 显示 print 输出
pytest -v -n auto                            # 并行执行
pytest -v -m "not slow"                     # 跳过慢速测试
pytest -v -k "test_login"                   # 运行匹配的测试

# 覆盖率
pytest --cov=src --cov-report=html

# Allure 报告
pytest --alluredir=reports/allure
allure generate reports/allure -o reports/allure-report
allure open reports/allure-report

# 功能测试
pytest tests/functional/ -v              # 运行功能测试
# UI 测试
pytest tests/ui/ -v                      # 运行 UI 测试
pytest tests/ui/ -v --headed             # 显示浏览器运行
```

### 14.2 环境变量

```bash
# .env
ENV=test
LOG_LEVEL=INFO
FIREWALL_UI_URL=https://192.168.1.1:443
DATABASE_URL=postgresql://testuser:testpass@localhost:5432/testdb
TEST_USERNAME=testuser
TEST_PASSWORD=testpass
```

### 14.3 故障排查

| 问题 | 解决方案 |
|------|---------|
| PostgreSQL 服务未启动 | 运行 `sudo systemctl start postgresql` |
| 数据库连接失败 | 检查 PostgreSQL 服务是否运行，连接配置是否正确 |
| CI 并发问题 | 使用 `pytest-xdist` 的 `--dist=loadscope` |
| Allure 报告不显示 | 确保 `--alluredir` 路径正确 |
| Playwright 浏览器问题 | 运行 `playwright install chromium` |
| UI 测试超时 | 检查页面加载速度，增加超时时间 |

---

**设计总结**: 本框架采用 pytest + GitLab CI 构建完全本地化的测试体系，支持 CLI/API/Functional/UI 测试，所有组件本地部署，无需外部云服务。通过 PostgreSQL 存储历史数据，Flask 提供本地报告查看，Allure 生成可视化报告，实现开箱即用的现代化测试框架。
