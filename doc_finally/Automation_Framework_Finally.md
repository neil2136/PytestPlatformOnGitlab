# 基于 pytest 的防火墙自动化测试框架完整实施文档

## 1. 项目概述
    这是一个完整的自动化测试框架，为防火墙设备提供了全面的测试解决方案，支持从API到UI的全方位测试，并通过CI/CD实现了自动化的测试流程。框架采用模块化设计，便于扩展和维护，是企业级防火墙测试的理想选择。

### 1.1 设计目标与实施现状

| 目标 | 设计要求 | 实施状态 | 验收结果 |
|------|---------|---------|---------|
| **完全本地化** | 所有组件本地部署，无外部云依赖 | ✅ 已实现 | 本地化部署，GitLab CI/CD 自托管 |
| **现代化技术栈** | pytest + GitLab CI | ✅ 已实现 | pytest 8.0+ + GitLab CI/CD 16.0+ |
| **四测试类型** | CLI 测试 + API 测试 + 功能测试 + UI 测试 | ✅ 已实现 | 四大测试类型完整覆盖 |
| **防火墙专用** | 针对 SonicOS 防火墙 API/CLI 优化 | ✅ 已实现 | 针对SonicOS深度定制 |
| **固定拓扑支持** | 支持固定网络拓扑环境测试 | ✅ 已实现 | Docker拓扑管理 |
| **开箱即用** | 最小配置即可运行 | ✅ 已实现 | 5分钟环境搭建 |
| **报告可视化** | 本地 HTML 报告 + 历史趋势 | ✅ 已实现 | Allure Docker Service |
| **CI/CD 集成** | GitLab CI 自动化流水线 | ✅ 已实现 | 7阶段完整流水线 |

### 1.2 技术栈实现

| 组件 | 技术选型 | 版本 | 实施状态 | 备注 |
|------|---------|------|---------|------|
| **测试框架** | pytest | 8.0+ | ✅ 已实现 | 核心测试引擎 |
| **API 测试** | requests + pydantic | 2.31+ | ✅ 已实现 | REST API测试 |
| **CLI 测试** | paramiko + netmiko | 3.3+ | ✅ 已实现 | SSH命令执行 |
| **报告生成** | Allure Report | 2.24+ | ✅ 已实现 | Docker化服务 |
| **覆盖率** | pytest-cov | 4.1+ | ✅ 已实现 | 代码覆盖率统计 |
| **CI 平台** | GitLab CI/CD | 16.0+ | ✅ 已实现 | 自托管部署 |
| **容器化** | Docker + Docker Compose | 24.0+ | ✅ 已实现 | 环境隔离 |
| **数据存储** | PostgreSQL | 15+ | ✅ 已实现 | 历史数据存储 |
| **Web 服务** | Flask | 3.0+ | ✅ 已实现 | 本地报告查看 |
| **拓扑管理** | JSON 配置 | - | ✅ 已实现 | 灵活定义拓扑 |

## 2. 完整架构设计

### 2.1 系统架构全景

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        自动化测试框架完整架构                                  │
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
│  │  │  7个阶段     │  │  (并行/串行) │  │  (容器执行) │                  │     │
│  │  │ setup→topology→deploy→test→report→sendmail→cleanup               │     │
│  │  └─────────────┘  └─────────────┘  └─────────────┘                  │     │
│  └─────────────────────────────────────────────────────────────────────┘     │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐     │
│  │                    测试执行层 (pytest + CLI/API)                       │     │
│  │  ┌─────────────────────────────────────────────────────────────┐    │     │
│  │  │  pytest 核心引擎 (8.0+)                                    │    │     │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │    │     │
│  │  │  │  Fixture    │  │  Plugin     │  │  Marker    │           │    │     │
│  │  │  │  依赖注入   │  │  扩展能力   │  │  测试标记   │           │    │     │
│  │  │  └─────────────┘  └─────────────┘  └─────────────┘           │    │     │
│  │  └─────────────────────────────────────────────────────────────┘    │     │
│  │  ┌─────────────────────────────────────────────────────────────┐    │     │
│  │  │  测试类型实现                                                   │    │     │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │    │     │
│  │  │  │  API测试   │  │  CLI测试    │  │  功能测试   │  │  UI测试    │           │    │     │
│  │  │  │  (requests)│  │  (paramiko) │  │  (集成测试) │  │  (Playwright)│           │    │     │
│  │  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘           │    │     │
│  │  └─────────────────────────────────────────────────────────────┘    │     │
│  └─────────────────────────────────────────────────────────────────────┘     │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐     │
│  │                        结果处理层                                    │     │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┘ │     │
│  │  │ Allure      │  │ JUnit XML   │  │  覆盖率     │  │  PostgreSQL  │ │     │
│  │  │  (Docker)   │  │  格式转换   │  │  (pytest-cov)│  │  历史存储   │ │     │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │     │
│  └─────────────────────────────────────────────────────────────────────┘     │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐     │
│  │                        可视化与通知层                                │     │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │     │
│  │  │ Allure UI   │  │ Flask Web   │  │  邮件通知   │  │  容器服务   │ │     │
│  │  │  (58080)    │  │  报告服务器  │  │  (SMTP)    │  │  (5050)    │ │     │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │     │
│  └─────────────────────────────────────────────────────────────────────┘     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 触发层 (Trigger Layer)

**触发机制**：
- **自动触发**：代码推送到 `main`/`develop` 分支或创建 Merge Request 时自动触发
- **手动触发**：在 GitLab Pipeline 页面手动运行
- **定时触发**：配置定时任务（如每天凌晨 2 点）
- **Webhook 触发**：支持外部系统通过 Webhook 调用触发

**触发配置**：
```yaml
# .gitlab-ci.yml 中的触发配置示例
trigger:
  include:
    - project: 'root/test_framework'
      branch: 'main'
```

### 2.4 CI 平台层 (CI Platform Layer)

**GitLab CI/CD 配置**：
- **配置文件**：`.gitlab-ci.yml` - 完整的 CI/CD 流水线配置
- **流水线阶段**：7阶段流水线（setup → topology → deploy → test → report → sendmail → cleanup）
- **远程执行**：通过 SSH 在远程服务器（10.103.50.112）上执行测试
- **Docker 集成**：使用 Docker 建立测试环境拓扑

**CI/CD 配置示例**：
```yaml
stages:
  - setup      # SSH 连接测试
  - topology   # Docker 测试拓扑
  - deploy     # 代码部署
  - test       # 测试执行
  - report     # 报告收集
  - sendmail   # 邮件通知
  - cleanup    # 环境清理

# 远程服务器配置
variables:
  REMOTE_HOST: "10.103.50.112"
  REMOTE_USER: "root"
  REMOTE_SSH_PASSWORD: "sonicauto"
  REMOTE_PROJECT_PATH: "/opt/test_framework"
  REMOTE_REPORT_PATH: "/opt/test_framework/reports"
  REMOTE_VENV_PATH: "/test_framework/.venv"

# Pytest 测试参数
variables:
  PYTEST_ARGS: "-v --html=reports/html/test_report.html --self-contained-html --junitxml=reports/junit/test-results.xml --alluredir=reports/allure --cov=src --cov-report=html:reports/coverage"
```

**脚本工具集**：
- `run-remote-tests.sh` - 远程测试执行脚本
- `collect-reports.sh` - 报告收集与处理脚本
- `verify_ci_pipeline.sh` - CI 流水线验证脚本
- `simple_verify.sh` - 简化验证脚本

### 2.5 可视化与通知层 (Visualization & Notification Layer)

**Allure 报告系统**：
- **Allure Docker Service**（后端）：端口 5050，管理项目数据并生成报告
- **Allure Docker Service UI**（前端）：端口 58080，浏览器访问报告界面
- **数据目录**：`/ci/auto-test-results/projects/` - 存储测试结果和报告

**目录结构**：
```
/ci/auto-test-results/projects/
├── default/              # 默认项目
│   ├── results/          # Allure 原始 JSON 结果
│   └── reports/          # 生成的 HTML 报告
└── fw-report/            # 防火墙测试项目（CI 使用）
    ├── results/          # pytest allure 插件输出的 JSON
    └── reports/          # Allure Docker 生成的可视化报告
```

**服务启动**：
```bash
# 启动后端
docker run -d --name allure-service --restart always \
  -p 5050:5050 \
  -e SECURITY_USER=admin \
  -e SECURITY_PASS=password \
  -e CHECK_RESULTS_EVERY_SECONDS=NONE \
  -e KEEP_HISTORY=1 \
  -e KEEP_HISTORY_LATEST=30 \
  -v /ci/auto-test-results/projects:/app/projects \
  frankescobar/allure-docker-service

# 启动 UI
docker run -d --name allure-ui --restart always \
  -p 58080:5252 \
  -e ALLURE_DOCKER_PUBLIC_API_URL=http://10.8.106.150:5050 \
  frankescobar/allure-docker-service-ui
```

**报告访问**：
- Allure UI：http://<服务器IP>:58080
- HTML 报告：`reports/html/test_report.html`
- JUnit XML 报告：`reports/junit/test-results.xml`
- 代码覆盖率报告：`reports/coverage/index.html`

**邮件通知**：
- 使用 `send_mail.py` 脚本发送测试结果邮件
- 支持 SMTP 配置和自定义邮件模板
- 可选功能，可在 CI 流水线中启用或禁用

**CI 报告收集流程**：
1. 从远程测试服务器 SCP 拷贝报告到 `/ci/reports/report_<timestamp>/`
2. 清理旧 JSON：`rm -f /ci/auto-test-results/projects/fw-report/results/*.json`
3. 复制新 JSON：`cp -f <report_dir>/allure/*.json /ci/auto-test-results/projects/fw-report/results/`
4. 触发报告生成：`curl http://10.8.106.150:5050/allure-docker-service/generate-report?project_id=fw-report`

### 2.6 测试执行层 (Test Execution Layer)

**pytest 核心引擎**：
- **测试框架**：pytest 8.0+，支持参数化测试和测试夹具
- **测试用例结构**：模块化设计，每个测试类型包含独立的测试用例
- **测试标记**：使用 pytest markers 标记不同类型的测试（api、cli、functional、ui）

**测试类型实现**：
- **API 测试**：使用 requests 库进行 REST API 测试
  - 文件：`tests/api/` 目录
  - 功能：验证防火墙设备 API 接口的正确性
  - 示例：`test_interface_api.py` - 接口配置 API 测试

- **CLI 测试**：使用 paramiko + netmiko 进行 SSH 命令执行测试
  - 文件：`tests/cli/` 目录
  - 功能：验证 CLI 配置和命令执行
  - 示例：`test_interface_config.py` - 接口配置 CLI 测试

- **功能测试**：集成测试，验证核心业务功能
  - 文件：`tests/functional/` 目录
  - 功能：验证访问规则、防火墙策略等核心功能
  - 示例：`test_access_rules.py` - 访问规则测试

- **UI 测试**：使用 Playwright 进行浏览器自动化测试
  - 文件：`tests/ui/` 目录
  - 功能：验证用户界面交互和功能
  - 示例：`test_interface_page.py` - 接口页面测试

**测试执行配置**：
```python
# pytest.ini 配置
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
```

**测试计划文档体系**：
- 每个测试模块包含 `testplan/` 目录，存放 JSON 格式的测试计划文档
- 测试计划包含测试步骤、初始条件、测试用例ID、标题和预期结果
- 便于测试用例的追溯和管理

**公共代码架构**：
- 每个测试模块包含 `bin/` 目录，存放可被所有case使用的公共代码
- API 测试：`bin/api_helpers.py` - API辅助工具方法
- CLI 测试：`bin/cli_helpers.py` - CLI辅助工具方法
- Functional 测试：`bin/functional_helpers.py` - 功能测试辅助工具
- UI 测试：`bin/ui_helpers.py`, `bin/base_page.py`, `bin/login_page.py` - UI测试辅助工具和页面对象

### 2.7 结果处理层 (Result Processing Layer)

**报告生成**：
- **Allure 报告**：使用 Allure 插件生成详细的测试报告
  - 输出目录：`reports/allure/`
  - 包含测试步骤、附件、历史记录等详细信息

- **HTML 报告**：生成自包含的 HTML 报告
  - 输出文件：`reports/html/test_report.html`
  - 包含测试结果、错误信息、测试统计等

- **JUnit XML 报告**：生成 JUnit 格式的 XML 报告
  - 输出文件：`reports/junit/test-results.xml`
  - 便于与其他 CI/CD 工具集成

- **代码覆盖率报告**：使用 pytest-cov 生成代码覆盖率报告
  - 输出目录：`reports/coverage/`
  - 包含覆盖率统计、行覆盖率、分支覆盖率等


### 2.6 测试执行层 (Test Execution Layer)

**pytest 核心引擎**：
- **测试框架**：pytest 8.0+，支持参数化测试和测试夹具
- **测试用例结构**：模块化设计，每个测试类型包含独立的测试用例
- **测试标记**：使用 pytest markers 标记不同类型的测试（api、cli、functional、ui）

**测试类型实现**：
- **API 测试**：使用 requests 库进行 REST API 测试
  - 文件：`tests/api/` 目录
  - 功能：验证防火墙设备 API 接口的正确性
  - 示例：`test_interface_api.py` - 接口配置 API 测试

- **CLI 测试**：使用 paramiko + netmiko 进行 SSH 命令执行测试
  - 文件：`tests/cli/` 目录
  - 功能：验证 CLI 配置和命令执行
  - 示例：`test_interface_config.py` - 接口配置 CLI 测试

- **功能测试**：集成测试，验证核心业务功能
  - 文件：`tests/functional/` 目录
  - 功能：验证访问规则、防火墙策略等核心功能
  - 示例：`test_access_rules.py` - 访问规则测试

- **UI 测试**：使用 Playwright 进行浏览器自动化测试
  - 文件：`tests/ui/` 目录
  - 功能：验证用户界面交互和功能
  - 示例：`test_interface_page.py` - 接口页面测试

**测试执行配置**：
```python
# pytest.ini 配置
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
```

**测试计划文档体系**：
- 每个测试模块包含 `testplan/` 目录，存放 JSON 格式的测试计划文档
- 测试计划包含测试步骤、初始条件、测试用例ID、标题和预期结果
- 便于测试用例的追溯和管理

**公共代码架构**：
- 每个测试模块包含 `bin/` 目录，存放可被所有case使用的公共代码
- API 测试：`bin/api_helpers.py` - API辅助工具方法
- CLI 测试：`bin/cli_helpers.py` - CLI辅助工具方法
- Functional 测试：`bin/functional_helpers.py` - 功能测试辅助工具
- UI 测试：`bin/ui_helpers.py`, `bin/base_page.py`, `bin/login_page.py` - UI测试辅助工具和页面对象

### 2.7 结果处理层 (Result Processing Layer)

**报告生成**：
- **Allure 报告**：使用 Allure 插件生成详细的测试报告
  - 输出目录：`reports/allure/`
  - 包含测试步骤、附件、历史记录等详细信息

- **HTML 报告**：生成自包含的 HTML 报告
  - 输出文件：`reports/html/test_report.html`
  - 包含测试结果、错误信息、测试统计等

- **JUnit XML 报告**：生成 JUnit 格式的 XML 报告
  - 输出文件：`reports/junit/test-results.xml`
  - 便于与其他 CI/CD 工具集成

- **代码覆盖率报告**：使用 pytest-cov 生成代码覆盖率报告
  - 输出目录：`reports/coverage/`
  - 包含覆盖率统计、行覆盖率、分支覆盖率等

**报告配置**：
```python
# Pytest 参数配置
PYTEST_ARGS: "-v --html=reports/html/test_report.html --self-contained-html --junitxml=reports/junit/test-results.xml --alluredir=reports/allure --cov=src --cov-report=html:reports/coverage"
```

**结果处理流程**：
1. **测试执行**：pytest 执行测试用例，生成原始结果
2. **报告生成**：pytest 插件生成各种格式的报告
3. **报告收集**：CI 流水线收集报告到指定目录
4. **Allure 集成**：将 Allure JSON 数据发送到 Allure Docker Service
5. **可视化展示**：通过 Allure UI 展示测试结果

**数据存储**：
- **PostgreSQL 数据库**：存储历史测试数据
  - 初始化脚本：`data/init_db.sql`
  - 用于历史数据存储和趋势分析

**报告输出目录结构**：
```
reports/
├── allure/                    # Allure 原始数据
├── allure-report/             # Allure HTML 报告
├── html/                      # pytest HTML 报告
└── coverage/                  # 代码覆盖率报告
```

**测试执行示例**：
```bash
# 运行所有测试
pytest tests/ -v

# 运行特定模块
pytest tests/api/ -v
pytest tests/cli/ -v
pytest tests/functional/ -v
pytest tests/ui/ -v

# 生成报告
pytest tests/ --html=reports/html/test_report.html --self-contained-html
pytest tests/ --alluredir=reports/allure
allure serve reports/allure


pytest测试项目目录结构（test_framework）


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
│   ├── api/                       # API 测试
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── testplan/              # 测试计划
│   │   ├── bin/api_helpers.py     # API 辅助工具
│   │   └── test_interface_api.py  # 接口 API 测试
│   │
│   ├── cli/                       # CLI 测试
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── testplan/              # 测试计划
│   │   ├── bin/cli_helpers.py     # CLI 辅助工具
│   │   └── test_interface_config.py # 接口配置测试
│   │
│   ├── functional/                # 功能测试
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── testplan/              # 测试计划
│   │   ├── bin/functional_helpers.py # 功能辅助工具
│   │   └── test_access_rules.py   # 访问规则测试
│   │
│   └── ui/                        # UI 测试
│       ├── __init__.py
│       ├── conftest.py
│       ├── testplan/              # 测试计划
│       ├── bin/                   # 公共代码
│       │   ├── ui_helpers.py      # UI 辅助工具
│       │   ├── base_page.py      # 基础页面
│       │   ├── fw_pages.py       # 防火墙页面
│       │   ├── interface_page.py # 接口页面
│       │   └── login_page.py     # 登录页面
│       └── test_interface_page.py # 接口页面测试
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
├── skills/                        # 自动化技能系统
│   ├── framework_skills.py        # 技能系统实现
│   └── network_device_automation_agent/ # 网络设备自动化 Agent
│
└── docs/                          # 文档
    ├── installation.md            # 安装指南
    ├── usage.md                   # 使用指南
    ├── writing_tests.md           # 编写测试
    └── troubleshooting.md         # 故障排查

## 9. GitLab CI 项目目录结构

### 9.1 CI 项目目录结构（/ci）

```
ci/
├── .git/                          # Git 仓库
├── .github/                       # GitHub 配置
│   └── workflows/                 # GitHub Actions 工作流（可选）
│       └── ci.yml                 # GitHub CI 配置
├── .gitlab-ci.yml                 # GitLab CI/CD 配置文件
├── AGENTS.md                      # Agent 配置文档
├── CI_README.md                   # CI 项目说明文档
├── allure_docker/                 # Allure Docker 服务配置
│   ├── allure_docker_cmd.md        # Allure 命令参考
│   ├── allure_docker_README.md     # Allure 部署指南
│   ├── allure_install.sh          # Allure 安装脚本
│   ├── as.tar                     # Allure 后端镜像
│   ├── asu.tar                    # Allure UI 镜像
│   └── project_demo/              # 项目演示模板
│       └── auto-test-results/      # 测试结果示例
│           └── projects/
│               └── default/       # 默认项目
│                   ├── results/   # Allure JSON 结果
│                   └── reports/   # HTML 报告
├── auto-test-results/             # 自动测试结果存储
│   └── projects/                 # 项目目录
│       └── fw-report/             # 防火墙测试项目（CI 使用）
│           ├── results/          # pytest allure 插件输出的 JSON
│           └── reports/          # Allure Docker 生成的可视化报告
├── gitlab_ci_docs/                # GitLab CI 文档
│   ├── GITLAB_CI_DEPLOYMENT.md     # GitLab CI 部署指南
│   ├── Pytest_Playwright_CI_Framework_Design.md  # Pytest Playwright CI 框架设计
│   └── pytest_readme.md           # Pytest 说明文档
├── reports/                      # 本地报告存储
│   ├── report_topo-dev_20260522163736/  # 历史报告 1
│   │   ├── allure/                # Allure 原始数据
│   │   ├── coverage/              # 代码覆盖率报告
│   │   ├── html/                 # HTML 报告
│   │   └── junit/                 # JUnit XML 报告
│   └── report_topo-dev_20260522165456/  # 历史报告 2
│       ├── allure/                # Allure 原始数据
│       ├── coverage/              # 代码覆盖率报告
│       ├── html/                 # HTML 报告
│       └── junit/                 # JUnit XML 报告
├── scripts/                      # 辅助脚本
│   ├── collect-reports.sh         # 报告收集脚本
│   ├── run-remote-tests.sh        # 远程测试执行脚本
│   └── send_mail.py              # 邮件发送脚本
└── test_docker/                   # 测试 Docker 镜像
    └── py3.13.tar                # Python 3.13 测试镜像
```

### 9.2 目录功能说明

**核心配置文件**：
- `.gitlab-ci.yml`：完整的 GitLab CI/CD 流水线配置
- `CI_README.md`：CI 项目说明和使用指南

**Allure 报告系统**：
- `allure_docker/`：Allure Docker 服务配置和镜像
- `auto-test-results/`：自动测试结果存储目录
- 包含项目模板和演示数据

**文档和指南**：
- `gitlab_ci_docs/`：GitLab CI 相关文档
- 包含部署指南、框架设计和 pytest 说明

**报告管理**：
- `reports/`：本地报告存储目录
- 按时间戳组织的历史报告

**脚本工具**：
- `scripts/`：辅助脚本集合
- 包含报告收集、远程测试执行和邮件发送功能

**Docker 支持**：
- `test_docker/`：测试 Docker 镜像
- 包含 Python 测试环境镜像

### 9.3 CI 流水线配置示例

```yaml
# .gitlab-ci.yml 示例
stages:
  - setup      # SSH 连接测试
  - topology   # Docker 测试拓扑
  - deploy     # 代码部署
  - test       # 测试执行
  - report     # 报告收集
  - sendmail   # 邮件通知
  - cleanup    # 环境清理

variables:
  REMOTE_HOST: "10.103.50.112"
  REMOTE_USER: "root"
  REMOTE_SSH_PASSWORD: "sonicauto"
  REMOTE_PROJECT_PATH: "/opt/test_framework"
  REMOTE_REPORT_PATH: "/opt/test_framework/reports"
  REMOTE_VENV_PATH: "/test_framework/.venv"

setup:
  stage: setup
  script:
    - echo "验证 SSH 连接到远程服务器"
    - sshpass -p "$REMOTE_SSH_PASSWORD" ssh -o StrictHostKeyChecking=no "$REMOTE_USER@$REMOTE_HOST" "echo '连接成功'"

topology:
  stage: topology
  script:
    - echo "建立 Docker 测试拓扑"
    - docker-compose -f docker-compose.ci.yml up -d

deploy:
  stage: deploy
  script:
    - echo "部署测试框架到远程服务器"
    - git clone <repository-url> "$REMOTE_PROJECT_PATH"

test:
  stage: test
  script:
    - echo "执行 pytest 测试"
    - sshpass -p "$REMOTE_SSH_PASSWORD" ssh "$REMOTE_USER@$REMOTE_HOST" "
        cd $REMOTE_PROJECT_PATH
        source $REMOTE_VENV_PATH/bin/activate
        pytest tests/ $PYTEST_ARGS
      "

report:
  stage: report
  script:
    - echo "收集测试报告"
    - ./scripts/collect-reports.sh

sendmail:
  stage: sendmail
  script:
    - echo "发送测试结果邮件"
    - python scripts/send_mail.py

cleanup:
  stage: cleanup
  script:
    - echo "清理临时文件"
    - sshpass -p "$REMOTE_SSH_PASSWORD" ssh "$REMOTE_USER@$REMOTE_HOST" "rm -rf /tmp/*"
```

### 9.4 关键脚本功能

**collect-reports.sh**：
```bash
#!/bin/bash
# 收集测试报告脚本
echo "开始收集测试报告..."

# 从远程服务器拷贝报告
scp -r root@10.103.50.112:/opt/test_framework/reports /ci/reports/report_$(date +%Y%m%d_%H%M%S)/

# 清理旧 JSON 文件
rm -f /ci/auto-test-results/projects/fw-report/results/*.json

# 复制新 JSON 文件
cp -f /ci/reports/report_$(date +%Y%m%d_%H%M%S)/allure/*.json /ci/auto-test-results/projects/fw-report/results/

# 触发 Allure 报告生成
curl http://10.8.106.150:5050/allure-docker-service/generate-report?project_id=fw-report

echo "报告收集完成"
```

**run-remote-tests.sh**：
```bash
#!/bin/bash
# 远程测试执行脚本
echo "开始执行远程测试..."

# SSH 连接到远程服务器并执行测试
sshpass -p "sonicauto" ssh root@10.103.50.112 "
    cd /opt/test_framework
    source .venv/bin/activate
    pytest tests/ -v --html=reports/html/test_report.html --self-contained-html --junitxml=reports/junit/test-results.xml --alluredir=reports/allure
"

echo "远程测试执行完成"
```

### 9.5 项目协同工作流

```
ci-project (GitLab 仓库)
    ↓ 提交代码 / 推送触发
GitLab CI/CD 流水线
    ↓ 自动部署
test_framework (远程服务器 10.103.50.112)
    ↓ 执行测试
生成测试报告
    ↓ 收集报告
Allure 可视化报告 (端口 58080)
```

