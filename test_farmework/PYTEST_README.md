# Pytest Framework - 模块化测试框架

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Pytest](https://img.shields.io/badge/Pytest-8.0+-green.svg)](https://pytest.org/)
[![Playwright](https://img.shields.io/badge/Playwright-1.40+-red.svg)](https://playwright.dev/)
[![Allure](https://img.shields.io/badge/Allure-2.13+-purple.svg)](https://allurereport.org/)

## 📋 项目概述

这是一个基于 Pytest 的模块化测试框架，专为防火墙设备测试设计。框架支持 API、CLI、Functional 和 UI 四种测试类型，采用公共代码架构和自动化部署系统，提供完整的测试报告和 CI/CD 集成能力。

### 🎯 核心特性

- **🏗️ 模块化架构**: 每个测试类型都有独立的 bin 目录存放公共代码
- **🔄 代码复用**: BaseTest 基类和 Helper 工具类实现代码标准化
- **📊 完整报告**: 支持 Allure 和 HTML 两种报告格式
- **🚀 自动化部署**: 7 个技能模块实现一键部署
- **🧪 多类型测试**: API、CLI、Functional、UI 全覆盖
- **📝 测试计划**: JSON 格式的测试计划文档体系

## 🏗️ 项目架构

```
test_framework/
├── 📁 src/                          # 框架核心代码
│   ├── core/utils/                  # 工具类
│   │   ├── config.py               # 配置管理
│   │   ├── api_client.py           # API 客户端
│   │   ├── cli_client.py           # CLI 客户端
│   │   └── logger.py               # 日志工具
│   └── firewall/                   # 防火墙接口
│       ├── sonicos_api.py          # SonicOS API
│       └── sonicos_cli.py          # SonicOS CLI
├── 📁 tests/                       # 测试用例
│   ├── api/                        # API 测试
│   │   ├── bin/                    # 公共代码
│   │   │   ├── api_helpers.py      # API 辅助工具
│   │   │   └── __init__.py
│   │   ├── testplan/               # 测试计划
│   │   └── test_interface_api.py   # 接口 API 测试
│   ├── cli/                        # CLI 测试
│   │   ├── bin/                    # 公共代码
│   │   │   ├── cli_helpers.py      # CLI 辅助工具
│   │   │   └── __init__.py
│   │   ├── testplan/               # 测试计划
│   │   └── test_interface_config.py # 接口配置测试
│   ├── functional/                 # 功能测试
│   │   ├── bin/                    # 公共代码
│   │   │   ├── functional_helpers.py # 功能辅助工具
│   │   │   └── __init__.py
│   │   ├── testplan/               # 测试计划
│   │   └── test_access_rules.py    # 访问规则测试
│   └── ui/                         # UI 测试
│       ├── bin/                    # 公共代码
│       │   ├── ui_helpers.py       # UI 辅助工具
│       │   ├── base_page.py        # 基础页面
│       │   ├── fw_pages.py         # 防火墙页面
│       │   ├── interface_page.py   # 接口页面
│       │   ├── login_page.py       # 登录页面
│       │   └── __init__.py
│       ├── testplan/               # 测试计划
│       └── test_interface_page.py  # 接口页面测试
├── 📁 skills/                      # 自动化技能系统
│   ├── framework_skills.py         # 技能系统实现
│   ├── README.md                   # 技能系统说明
│   └── network_device_automation_agent/ # 适配资深网络设备自动化工程师的 Agent Skill
├── 📁 reports/                     # 测试报告
│   ├── allure/                     # Allure 报告
│   └── html/                       # HTML 报告
├── 📄 conftest.py                  # Pytest 配置
├── 📄 pytest.ini                  # Pytest 设置
├── 📄 requirements.txt             # Python 依赖
├── 📄 .env                        # 环境变量
├── 📄 QUICK_SETUP.sh              # 快速部署脚本
├── 📄 DEPLOYMENT_GUIDE.md         # 部署指南
└── 📄 README_NEW.md               # 项目说明 (本文件)
```

## 🚀 快速开始

### 环境要求

- **操作系统**: Ubuntu 24.04 LTS (推荐)
- **Python**: 3.10+ 
- **内存**: 4GB+ (推荐 8GB)
- **存储**: 10GB+ 可用空间
- **网络**: 能够访问目标防火墙设备

### 一键部署

```bash
# 克隆项目
git clone <repository-url>
cd test_framework

# 运行快速部署脚本
chmod +x QUICK_SETUP.sh
./QUICK_SETUP.sh
```

### 手动部署

```bash
# 1. 安装系统依赖
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git curl wget build-essential

# 2. 设置虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 3. 安装 Python 依赖
pip install -r requirements.txt

# 4. 安装 Playwright 浏览器
playwright install chromium
playwright install-deps chromium

# # 5. 安装 Allure (可选)
# wget https://github.com/allure-framework/allure2/releases/download/2.24.1/allure_2.24.1-1_all.deb
# sudo dpkg -i allure_2.24.1-1_all.deb
# sudo apt-get install -f -y
```

## 🧪 运行测试

### 配置环境变量

编辑 `.env` 文件，配置防火墙连接信息：

```bash
# 防火墙配置
FIREWALL_HOST=10.8.105.173
FIREWALL_USERNAME=admin
FIREWALL_PASSWORD=password2
FIREWALL_API_PORT=443
FIREWALL_SSH_PORT=22

# 测试环境
ENV=test
LOG_LEVEL=INFO

# API 配置
API_BASE_URL=https://10.8.105.173:443/api
API_TIMEOUT=30

# SSH 连接配置
LAN_HOST=10.8.106.11
LAN_USERNAME=root
LAN_PASSWORD=password
WAN_HOST=10.8.2.217
```

### 运行所有测试

```bash
# 激活虚拟环境
source .venv/bin/activate

# 运行所有测试
pytest tests/ -v

# 生成报告
pytest tests/ --html=reports/html/test_report.html --self-contained-html
```

### 运行特定模块

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

### 生成 Allure 报告

```bash
# 运行测试并生成 Allure 数据
pytest tests/ --alluredir=reports/allure

# 启动 Allure 服务
allure serve reports/allure

# 或生成静态 HTML 报告
allure generate reports/allure -o reports/html/allure --clean
```

## 🤖 自动化技能系统

### 技能架构

```
Pytest Framework Skill System
├── Environment Manager          # 环境管理技能
├── Dependency Installer         # 依赖安装技能  
├── Configuration Manager       # 配置管理技能
├── Test Framework Deployer    # 框架部署技能
├── Code Generator             # 代码生成技能
├── Validation Engine          # 验证引擎技能
└── Report Generator          # 报告生成技能
```

### 使用技能系统

```bash
# 完整框架部署
python skills/framework_skills.py deploy

# 单个技能执行
python skills/framework_skills.py check_environment
python skills/framework_skills.py install_system_deps
python skills/framework_skills.py validate_deployment
```

本项目还包含 `skills/network_device_automation_agent/SKILL.md`，用于定义面向资深网络设备自动化开发与测试工程师的专属 Agent 工作流。

### 技能功能

| 技能 | 功能 | 对应阶段 |
|------|------|----------|
| Environment Manager | 系统要求检查 | 阶段 1-2 |
| Dependency Installer | 依赖安装 | 阶段 3-4 |
| Configuration Manager | 配置管理 | 阶段 5-6 |
| Test Framework Deployer | 框架部署 | 阶段 7-8 |
| Code Generator | 代码生成 | 阶段 9 |
| Validation Engine | 验证检查 | 阶段 10 |
| Report Generator | 报告生成 | 阶段 11 |

## 📊 测试类型详解

### API 测试

- **位置**: `tests/api/`
- **基类**: `BaseAPITest`
- **功能**: REST API 接口测试
- **示例**: 防火墙接口配置测试

```python
@pytest.mark.api
class TestInterfaceAPI(BaseAPITest):
    def test_configure_x2_interface_via_api(self, sonicos_api: SonicOSAPI):
        # API 测试逻辑
        pass
```

### CLI 测试

- **位置**: `tests/cli/`
- **基类**: `BaseCLITest`
- **功能**: SSH 命令行接口测试
- **示例**: 防火墙 CLI 配置测试

```python
@pytest.mark.cli
class TestInterfaceConfigCLI(BaseCLITest):
    def test_configure_x2_ip_via_cli(self, sonicos_cli: SonicOSCLI):
        # CLI 测试逻辑
        pass
```

### Functional 测试

- **位置**: `tests/functional/`
- **基类**: `BaseFunctionalTest`
- **功能**: 端到端功能测试
- **示例**: ACL 规则和网络连通性测试

```python
@pytest.mark.functional
class TestAccessRules(BaseFunctionalTest):
    def test_add_acl_rule_via_api(self, sonicos_api: SonicOSAPI):
        # 功能测试逻辑
        pass
```

### UI 测试

- **位置**: `tests/ui/`
- **基类**: `BaseUITest`
- **功能**: Web UI 自动化测试
- **示例**: 防火墙管理界面测试

```python
@pytest.mark.ui
class TestInterfacePage(BaseUITest):
    def test_interface_page_has_dmz_zone(self):
        # UI 测试逻辑
        pass
```

## 🔧 开发指南

### 添加新的测试用例

1. **选择测试类型** (API/CLI/Functional/UI)
2. **继承对应的基类**
3. **使用 Helper 方法**
4. **添加 Allure 标注**
5. **创建测试计划文档**

```python
# 示例：添加新的 API 测试
@pytest.mark.api
class TestNewFeature(BaseAPITest):
    @allure.title("测试新功能")
    @allure.description("测试新功能的 API 接口")
    def test_new_feature_api(self, sonicos_api: SonicOSAPI):
        with allure.step("发送 API 请求"):
            response = sonicos_api.post("/new-feature", json=payload)
        
        with allure.step("验证响应"):
            self.verify_api_response(response)
            self.attach_response_to_allure(response)
```

### 创建测试计划

在对应模块的 `testplan/` 目录下创建 JSON 文件：

```json
{
  "test_case_01": {
    "steps": "1. 连接防火墙 2. 发送请求 3. 验证响应",
    "initial": "防火墙正常运行，网络连通",
    "id": "test_case_01",
    "title": "新功能测试",
    "result": "API 响应成功，配置生效"
  }
}
```

### 公共代码开发

在对应模块的 `bin/` 目录下添加 Helper 方法：

```python
# 示例：API Helper 方法
class APIHelpers:
    @staticmethod
    def verify_success_status(response_data):
        """验证成功状态"""
        assert "status" in response_data
        assert response_data["status"]["success"] is True
```

## 📈 CI/CD 集成

### GitHub Actions 示例

```yaml
name: Pytest Framework CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        playwright install chromium
    
    - name: Run tests
      run: |
        source .venv/bin/activate && pytest tests/ --html=reports/html/test_report.html --self-contained-html
...
    
    - name: Upload test results
      uses: actions/upload-artifact@v3
      with:
        name: test-results
        path: reports/
```

## 🐛 故障排除

### 常见问题

1. **SSL 证书错误**
   ```bash
   # 解决方案：已在代码中禁用 SSL 验证
   # 或添加防火墙证书到系统信任存储
   ```

2. **Playwright 浏览器启动失败**
   ```bash
   # 重新安装浏览器
   playwright install-deps chromium
   playwright install chromium
   ```

3. **SSH 连接超时**
   ```bash
   # 检查网络连通性
   ping 10.8.105.173
   
   # 检查防火墙 SSH 服务
   nmap -p 22 10.8.105.173
   ```

4. **API 认证失败**
   ```bash
   # 检查防火墙管理员账户
   # 验证 API 访问权限
   # 检查防火墙 API 服务状态
   ```

### 调试模式

```bash
# 详细输出
pytest tests/ -v -s

# 只运行失败的测试
pytest tests/ --lf

# 停在第一个失败
pytest tests/ -x

# 并行执行
pytest tests/ -n auto
```

## 📚 文档资源

- **[部署指南](DEPLOYMENT_GUIDE.md)** - 详细的部署步骤
- **[技能系统说明](skills/README.md)** - 自动化部署系统
- **[对话记录导出](CONVERSATION_EXPORT.md)** - 开发过程记录
- **[框架设计文档](Pytest_Playwright_CI_Framework_Design.md)** - 原始设计文档
- **[项目展示 PPT](doc/基于Pytest的模块化防火墙测试框架.pptx)** - 设计与介绍幻灯片
- **[项目概览 PPT](project_overview.pptx)** - 生成的项目介绍幻灯片

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 👥 团队

- **项目维护者**: [Your Name]
- **技术栈**: Python, Pytest, Playwright, Allure
- **目标**: 提供完整的防火墙测试解决方案

## 📞 支持

如果您遇到问题或有建议，请：

1. 查看 [故障排除](#故障排除) 部分
2. 搜索现有的 [Issues](../../issues)
3. 创建新的 Issue 描述问题
4. 联系项目维护者

---

**注意**: 本框架专为防火墙设备测试设计，使用前请确保网络连通性和权限配置正确。

# pytest running command example
(venv) root@ubt24:/opt/test_framework# source /test_framework/.venv/bin/activate
(.venv) root@ubt24:/opt/test_framework# pytest tests/ -v --html=reports/html/test_report.html --self-contained-html --junitxml=reports/junit/test-results.xml --alluredir=reports/allure --cov=src --cov-report=html:reports/coverage
===================================================== test session starts =====================================================
platform linux -- Python 3.12.3, pytest-7.4.4, pluggy-1.6.0
rootdir: /opt/test_framework
configfile: pytest.ini
plugins: env-1.1.0, cov-4.1.0, playwright-0.4.3, metadata-3.1.1, base-url-2.1.0, html-4.1.0, allure-pytest-2.13.2, xdist-3.5.0
collected 8 items                                                                                                             

tests/api/test_interface_api.py ..                                                                                      [ 25%]
tests/cli/test_interface_config.py ..                                                                                   [ 50%]
tests/functional/test_access_rules.py sss                                                                               [ 87%]
tests/ui/test_interface_page.py .                                                                                       [100%]

====================================================== warnings summary =======================================================
../../test_framework/.venv/lib/python3.12/site-packages/paramiko/pkey.py:100
  /test_framework/.venv/lib/python3.12/site-packages/paramiko/pkey.py:100: CryptographyDeprecationWarning: TripleDES has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.TripleDES and will be removed from cryptography.hazmat.primitives.ciphers.algorithms in 48.0.0.
    "cipher": algorithms.TripleDES,

../../test_framework/.venv/lib/python3.12/site-packages/paramiko/transport.py:258
  /test_framework/.venv/lib/python3.12/site-packages/paramiko/transport.py:258: CryptographyDeprecationWarning: TripleDES has been moved to cryptography.hazmat.decrepit.ciphers.algorithms.TripleDES and will be removed from cryptography.hazmat.primitives.ciphers.algorithms in 48.0.0.
    "class": algorithms.TripleDES,

../../test_framework/.venv/lib/python3.12/site-packages/netmiko/base_connection.py:30
  /test_framework/.venv/lib/python3.12/site-packages/netmiko/base_connection.py:30: DeprecationWarning: 'telnetlib' is deprecated and slated for removal in Python 3.13
    import telnetlib

tests/api/test_interface_api.py::TestInterfaceAPI::test_configure_x2_interface
tests/api/test_interface_api.py::TestInterfaceAPI::test_verify_x2_interface_config
tests/functional/test_access_rules.py::TestAccessRules::test_add_acl_rule_via_api
tests/functional/test_access_rules.py::TestAccessRules::test_complete_acl_workflow
  /test_framework/.venv/lib/python3.12/site-packages/urllib3/connectionpool.py:1097: InsecureRequestWarning: Unverified HTTPS request is being made to host '10.8.105.173'. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/latest/advanced-usage.html#tls-warnings
    warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
--------------------------- generated xml file: /opt/test_framework/reports/junit/test-results.xml ----------------------------

---------- coverage: platform linux, python 3.12.3-final-0 -----------
Coverage HTML written to dir reports/coverage

----------------------- Generated html report: file:///opt/test_framework/reports/html/test_report.html -----------------------
=================================================== short test summary info ===================================================
SKIPPED [2] tests/functional/test_access_rules.py:118: ACL 'auto_rules_01' already exists
SKIPPED [1] tests/functional/test_access_rules.py:243: SSH connection to 10.8.106.11 failed: Connection error: timed out
===================================== 5 passed, 3 skipped, 7 warnings in 97.05s (0:01:37) =====================================
(.venv) root@ubt24:/opt/test_framework# 
