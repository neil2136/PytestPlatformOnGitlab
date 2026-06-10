# GitLab CI/CD 集成测试框架
基于 Pytest + Playwright 的自动化测试框架，通过 GitLab CI/CD 实现远程服务器测试执行、报告收集和可视化展示。
## 项目概述
本仓库提供完整的 GitLab CI/CD 集成方案，支持：
- 远程服务器自动化测试执行
- 多格式测试报告生成（HTML、Allure、Junit）
- 自动化报告收集与传输
- 测试覆盖率统计
- Allure 可视化报告集成
### 核心特性
- **自动化测试**: 集成 Pytest 测试框架，支持 API、CLI、Functional、UI 四大测试类型
- **远程执行**: 通过 SSH 在远程服务器（10.103.50.112）上执行测试
- **多格式报告**: 生成 HTML 自包含报告、Allure JSON 数据、Junit XML 报告
- **覆盖率统计**: 代码覆盖率报告（HTML 格式）
- **可视化展示**: Allure 报告生成与集成
- **CI/CD 集成**: 完整的 GitLab CI 流水线配置
## 项目组成
本 GitLab 仓库包含两个核心项目，协同完成自动化测试的完整流程：
### 1. test_framework 项目
**项目地址**: [http://10.8.106.150/root/test_framework](http://10.8.106.150/root/test_framework)
**项目类型**: 测试框架项目（Administrator / pytest_framework）
**主要功能**:
- **完整测试套件**: 包含 API、CLI、Functional、UI 四大测试类型的完整测试代码
  - `tests/api/` - 接口自动化测试，验证防火墙设备 API 的正确性
  - `tests/cli/` - 命令行接口测试，验证 CLI 配置和命令执行
  - `tests/functional/` - 功能测试，验证核心业务功能的正确性
  - `tests/ui/` - Playwright UI 自动化测试，验证用户界面交互
- **测试框架**: 基于 Python 3.10+ 和 Pytest 7.4.4 构建
  - 使用 Pytest fixtures 和 fixtures 管理测试环境
  - 集成 Playwright 进行 UI 自动化测试
  - 支持参数化测试和测试夹具
- **远程执行环境**: 在远程服务器（10.103.50.112）上运行
  - 远程项目路径: `/opt/test_framework`
  - Python 虚拟环境: `/test_framework/.venv/`
  - 自动化测试拓扑: 使用 Docker 建立测试环境
- **报告生成**: 支持多种测试报告格式
  - HTML 自包含报告: `reports/html/test_report.html`
  - Allure JSON 数据: `reports/allure/`
  - JUnit XML 报告: `reports/junit/test-results.xml`
  - 代码覆盖率报告: `reports/coverage/index.html`
- **测试覆盖范围**:
  - SonicOS 风格防火墙设备的 API 接口测试
  - CLI 配置和命令执行测试
  - 核心功能（如访问规则、防火墙策略等）测试
  - 用户界面交互和功能验证测试
**使用方式**:
```bash
# 在远程服务器上执行所有测试
sshpass -p "sonicauto" ssh root@10.103.50.112 "
    cd /opt/test_framework
    source .venv/bin/activate
    pytest tests/ -v --html=reports/html/test_report.html --self-contained-html --alluredir=reports/allure
"
# 执行特定测试类型
pytest tests/api/ -v
pytest tests/cli/ -v
pytest tests/functional/ -v
pytest tests/ui/ -v
```
**测试执行示例**:
```
tests/api/test_interface_api.py ..                    # API 测试通过
tests/cli/test_interface_config.py ..                 # CLI 测试通过
tests/functional/test_access_rules.py sss             # 功能测试跳过
tests/ui/test_interface_page.py .                    # UI 测试通过
============= 5 passed, 3 skipped, 7 warnings in 84.30s ==============
```
### 2. ci-project 项目
**项目地址**: [http://10.8.106.150/root/ci-project](http://10.8.106.150/root/ci-project)
**项目类型**: CI/CD 集成项目（Administrator / ci-project）
**主要功能**:
- **GitLab CI/CD 配置**: 完整的 `.gitlab-ci.yml` 配置文件
  - 7 阶段流水线：setup → topology → deploy → test → report → sendmail → cleanup
  - SSH 远程连接和认证配置
  - Docker 测试拓扑建立
  - 代码自动部署到远程服务器
  - 自动化测试执行
  - 报告收集和 Allure 生成
  - 邮件通知（可选）
- **自动化测试流水线**:
  - **setup 阶段**: 验证 SSH 连接到远程服务器
  - **topology 阶段**: 使用 Docker 建立测试环境拓扑
  - **deploy 阶段**: 克隆代码到远程服务器（`/opt/test_framework`）
  - **test 阶段**: 远程执行 Pytest 测试
  - **report 阶段**: 收集测试报告并生成 Allure 可视化报告
  - **sendmail 阶段**: 发送测试结果邮件
  - **cleanup 阶段**: 清理远程服务器临时文件
- **脚本工具集**:
  - `run-remote-tests.sh` - 远程测试执行脚本
  - `collect-reports.sh` - 报告收集与处理脚本
  - `verify_ci_pipeline.sh` - CI 流水线验证脚本
  - `simple_verify.sh` - 简化验证脚本
- **报告管理**:
  - 本地报告目录: `/ci/reports/`
  - 固定报告目录: `/ci/auto-test-results/projects/fw-report/`
  - Allure 报告生成和集成
  - HTML、Junit、Coverage 多格式报告支持
- **CI/CD 触发方式**:
  - 自动触发：代码推送到 main/develop 分支或创建 Merge Request
  - 手动触发：在 GitLab Pipeline 页面手动运行
  - 定时触发：配置定时任务（如每天凌晨 2 点）
**配置说明**:
```yaml
# 远程服务器配置
REMOTE_HOST: "10.103.50.112"
REMOTE_USER: "root"
REMOTE_SSH_PASSWORD: "sonicauto"
REMOTE_PROJECT_PATH: "/opt/test_framework"
REMOTE_REPORT_PATH: "/opt/test_framework/reports"
REMOTE_VENV_PATH: "/test_framework/.venv"
# Pytest 参数
PYTEST_ARGS: "-v --html=reports/html/test_report.html --self-contained-html --junitxml=reports/junit/test-results.xml --alluredir=reports/allure --cov=src --cov-report=html:reports/coverage"
```
**使用方式**:
```bash
# 提交代码触发 CI 流水线
git add .
git commit -m "Update test cases"
git push origin main
# 在 GitLab 中手动触发 Pipeline
# CI/CD > Pipelines > Run pipeline
# 验证 CI 流水线
chmod +x /ci/verify_ci_pipeline.sh
/ci/verify_ci_pipeline.sh
```
**CI 流水线示例**:
```yaml
stages:
  - setup      # SSH 连接测试
  - topology   # Docker 测试拓扑
  - deploy     # 代码部署
  - test       # 测试执行
  - report     # 报告收集
  - sendmail   # 邮件通知
  - cleanup    # 环境清理
```
**项目协同工作流**:
```
ci-project (GitLab 仓库)
    ↓ 提交代码 / 推送触发
GitLab CI/CD 流水线
    ↓ 自动部署
test_framework (远程服务器 10.103.50.112)
    ↓ 执行测试
生成测试报告
    ↓ 收集报告
Allure 可视化报告
```
**关键特性**:
- **自动化**: 代码提交后自动触发远程测试
- **可视化**: Allure 报告提供直观的测试结果展示
- **多格式**: 支持 HTML、Allure、Junit、Coverage 多种报告格式
- **远程执行**: 在隔离的远程服务器上执行测试，不影响本地环境
- **可扩展**: 支持并行测试、自定义参数、环境变量配置
- **易于维护**: 清晰的文档和脚本工具，便于维护和扩展
## 目录结构
```
/ci/
├── .gitlab-ci.yml                    # GitLab CI 主配置文件
├── README.md                         # 本文档
├── AGENTS.md                         # AI Agent 指南
├── scripts/
│   ├── run-remote-tests.sh           # 远程测试执行脚本
│   └── collect-reports.sh            # 报告收集与处理脚本
├── docs/
│   ├── GITLAB_CI_DEPLOYMENT.md       # GitLab CI 部署指南
│   └── Pytest_Playwright_CI_Framework_Design.md  # 架构设计文档
├── reports/                          # 本地报告目录
│   ├── report_topo-dev_YYYYMMDDHHMMSS/
│   │   ├── allure/                   # Allure 报告数据
│   │   ├── coverage/                 # 覆盖率报告
│   │   ├── html/                     # HTML 报告
│   │   └── junit/                    # JUnit XML 报告
└── auto-test-results/
    └── projects/
        └── fw-report/                # 固定报告目录
            ├── results/               # Allure 结果
            ├── reports/               # Allure 报告
            ├── coverage/              # 覆盖率报告
            └── html/                  # HTML 报告
```
## 快速开始
### 前置要求
#### 本地环境
- **操作系统**: Ubuntu 20.04+ 或兼容系统
- **GitLab CE**: 18.11.2+
- **GitLab Runner**: 最新版本
- **SSH 工具**: sshpass
- **网络**: 稳定的互联网连接
#### 远程服务器
- **操作系统**: Linux（支持 Docker）
- **Python**: 3.10+
- **Pytest**: 7.4.4+
- **Playwright**: 最新版本
- **内存**: 最少 4GB RAM（推荐 8GB+）
- **存储**: 最少 20GB 可用空间
### 安装步骤
#### 1. 安装 GitLab
参考 [GitLab 部署指南](docs/GITLAB_CI_DEPLOYMENT.md) 进行安装和配置。
**快速安装命令**:
```bash
# 更新系统并安装依赖
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y curl openssh-server ca-certificates tzdata perl
# 添加 GitLab 官方仓库
curl -L https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh | sudo bash
# 安装 GitLab CE
sudo EXTERNAL_URL="http://your-gitlab-server" apt-get install gitlab-ce
# 重新配置
sudo gitlab-ctl reconfigure
# 启动服务
sudo gitlab-ctl start
```
#### 2. 安装 GitLab Runner
```bash
# 安装 Runner
sudo apt-get install gitlab-runner
# 注册 Runner
sudo gitlab-runner register
# - GitLab URL: http://your-gitlab-server
# - 注册令牌: 从 GitLab 项目设置获取
# - 描述: Remote Pytest Runner
# - 标签: shell
# - 执行器: shell
```
#### 3. 配置 SSH 认证
在 GitLab Runner 服务器上安装 sshpass：
```bash
sudo apt-get install -y sshpass
```
#### 4. 配置 GitLab CI/CD 变量
在 GitLab 项目中添加以下变量：
| 变量名 | 值 | 说明 |
|--------|-----|------|
| `REMOTE_SSH_PASSWORD` | `sonicauto` | SSH 密码 |
| `REMOTE_HOST` | `10.103.50.112` | 远程服务器 IP |
| `REMOTE_USER` | `root` | SSH 用户名 |
**配置步骤**:
1. 进入 GitLab 项目页面
2. 点击 **Settings** > **CI/CD** > **Variables** > **Add variable**
3. 添加上述变量（建议启用"保护"和"屏蔽"）
## GitLab CI/CD 流水线
### 流水线阶段
```
setup → topology → deploy → test → report → sendmail → cleanup
```
#### 阶段说明
| 阶段 | 说明 | 关键操作 |
|------|------|----------|
| **setup** | SSH 连接测试 | 验证远程服务器连接 |
| **topology** | 测试拓扑网络 | 使用 Docker 建立测试环境 |
| **deploy** | 代码部署 | 克隆代码到远程服务器 |
| **test** | 测试执行 | 远程执行 Pytest 测试 |
| **report** | 报告收集 | 收集测试报告并生成 Allure |
| **sendmail** | 邮件通知 | 发送测试结果邮件（可选） |
| **cleanup** | 环境清理 | 清理远程服务器临时文件 |
### 配置文件
#### `.gitlab-ci.yml`
完整的 CI/CD 配置文件位于项目根目录：
```yaml
# 该文件已包含在项目中
# 主要功能：
# - SSH 连接测试
# - Docker 测试拓扑建立
# - 远程代码部署
# - Pytest 测试执行
# - 报告收集与 Allure 生成
# - 邮件通知（可选）
# - 环境清理
```
### 触发方式
#### 自动触发
以下操作会自动触发 CI 流水线：
- 推送代码到 `main` 分支
- 推送代码到 `develop` 分支
- 创建 Merge Request
#### 手动触发
在 GitLab 项目页面：
1. 点击 **CI/CD** > **Pipelines**
2. 点击 **Run pipeline** 按钮
3. 选择分支
4. 点击 **Run pipeline**
#### 定时触发（可选）
在 `.gitlab-ci.yml` 中添加定时任务：
```yaml
workflow:
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule"
    - if: $CI_PIPELINE_SOURCE == "push"
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
```
在 GitLab 中配置：
1. **CI/CD** > **Schedules** > **New schedule**
2. 设置定时规则（如：每天凌晨 2 点）
## 使用指南
### 执行测试
#### 本地验证
```bash
# 1. 验证 SSH 连接
sshpass -p "sonicauto" ssh -o StrictHostKeyChecking=no root@10.103.50.112 "echo 'SSH连接成功'"
# 2. 验证测试环境
sshpass -p "sonicauto" ssh root@10.103.50.112 "cd /test_framework && source .venv/bin/activate && pytest --version"
# 3. 执行远程测试
REMOTE_SSH_PASSWORD=sonicauto ./scripts/run-remote-tests.sh
# 4. 收集报告
REMOTE_SSH_PASSWORD=sonicauto ./scripts/collect-reports.sh
# 5. 查看报告
ls -la reports/html/
```
#### GitLab CI 触发
```bash
# 提交代码触发 CI
git add .
git commit -m "Update test cases"
git push origin main
```
### 查看测试报告
#### HTML 报告
1. 进入 GitLab Pipeline 详情页
2. 点击具体 Job
3. 在 **Artifacts** 中下载 `reports/html/test_report.html`
4. 在浏览器中打开查看
#### Allure 报告
1. 进入 Pipeline 详情页
2. 在 **Artifacts** 中下载 `auto-test-results/projects/fw-report/allure/`
3. 使用 Allure 命令生成可视化报告：
```bash
# 生成 Allure 报告
allure generate auto-test-results/projects/fw-report/allure -o auto-test-results/projects/fw-report/html --clean
# 启动 Allure 服务器
allure serve auto-test-results/projects/fw-report/allure
```
#### JUnit 报告
JUnit XML 报告会自动生成在 `reports/junit/` 目录中，可集成到 CI/CD 工具中。
### 测试覆盖率
覆盖率报告会生成在 `reports/coverage/` 目录中：
```bash
# 查看 HTML 覆盖率报告
open reports/coverage/index.html
```
## 测试类型
本项目支持四种测试类型：
| 测试类型 | 说明 | 示例 |
|----------|------|------|
| **API 测试** | 接口自动化测试 | `tests/api/` |
| **CLI 测试** | 命令行接口测试 | `tests/cli/` |
| **Functional 测试** | 功能测试 | `tests/functional/` |
| **UI 测试** | Playwright UI 自动化测试 | `tests/ui/` |
### 运行特定测试类型
```bash
# 运行 API 测试
pytest tests/api/ -v
# 运行 CLI 测试
pytest tests/cli/ -v
# 运行 Functional 测试
pytest tests/functional/ -v
# 运行 UI 测试
pytest tests/ui/ -v
```
## 配置说明
### Pytest 参数配置
在 `.gitlab-ci.yml` 中配置 Pytest 参数：
```yaml
variables:
  PYTEST_ARGS: "-v --html=reports/html/test_report.html --self-contained-html --junitxml=reports/junit/test-results.xml --alluredir=reports/allure --cov=src --cov-report=html:reports/coverage"
```
### 自定义配置
#### 修改远程服务器信息
编辑 `.gitlab-ci.yml`:
```yaml
variables:
  REMOTE_HOST: "10.103.50.112"
  REMOTE_USER: "root"
  REMOTE_SSH_PASSWORD: "your-password"
  REMOTE_PROJECT_PATH: "/opt/test_framework"
```
#### 修改报告路径
```yaml
variables:
  REMOTE_REPORT_PATH: "/opt/test_framework/reports"
  LOCAL_REPORT_DIR: "/ci/reports"
```
#### 启用邮件通知
在 `.gitlab-ci.yml` 中添加 `sendmail` 阶段（已默认启用）。
## 故障排除
### 常见问题
#### 1. YAML 嵌套深度错误
**症状**: `script config should be a string or a nested array of strings up to 10 levels deep`
**解决方案**: 使用单行命令，避免 heredoc 语法：
```yaml
# ❌ 错误
script:
  - |
    sshpass -p "$PASSWORD" ssh user@host "command"
# ✅ 正确
script:
  - sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no user@host "command"
```
#### 2. SSH 连接失败
**症状**: `sshpass: command not found` 或连接超时
**解决方案**:
```bash
# 安装 sshpass
sudo apt-get install -y sshpass
# 测试连接
sshpass -p "sonicauto" ssh -o StrictHostKeyChecking=no root@10.103.50.112 "echo test"
```
#### 3. 远程虚拟环境激活失败
**症状**: `pytest: command not found`
**解决方案**:
```bash
# 手动检查远程环境
sshpass -p "sonicauto" ssh root@10.103.50.112 "
    cd /test_framework
    source .venv/bin/activate
    which pytest
    pytest --version
"
```
#### 4. Playwright 浏览器未安装
**症状**: `Executable doesn't exist at /root/.cache/ms-playwright/chromium-1091/chrome-linux/chrome`
**解决方案**:
```bash
sshpass -p "sonicauto" ssh root@10.103.50.112 "
    cd /test_framework
    source .venv/bin/activate
    playwright install
"
```
#### 5. GitLab Runner 未执行
**症状**: Pipeline 一直处于 pending 状态
**解决方案**:
```bash
# 检查 Runner 状态
sudo gitlab-runner status
# 检查 Runner 标签匹配
# .gitlab-ci.yml 中的 tags 必须与 Runner 注册时的标签一致
# 查看 Runner 日志
sudo tail -f /var/log/gitlab-runner.log
```
#### 6. CI 变量未生效
**症状**: `REMOTE_SSH_PASSWORD: unbound variable`
**解决方案**:
1. 检查 GitLab 中变量是否正确设置
2. 确认变量已启用"保护"或"全部环境"
3. 重新保存变量设置
### 调试技巧
#### 查看详细日志
```bash
# 在 GitLab Pipeline 页面查看详细日志
# Settings > CI/CD > Pipelines > Pipeline Details > Job Log
```
#### 本地验证脚本
使用提供的验证脚本进行测试：
```bash
# 完整验证脚本
chmod +x /ci/verify_ci_pipeline.sh
/ci/verify_ci_pipeline.sh
# 简化验证脚本
chmod +x /ci/simple_verify.sh
/ci/simple_verify.sh
```
#### 手动执行测试步骤
```bash
# 1. SSH 连接测试
sshpass -p "sonicauto" ssh -o StrictHostKeyChecking=no root@10.103.50.112 "echo 'SSH连接成功'"
# 2. 克隆代码
sshpass -p "sonicauto" ssh root@10.103.50.112 "git clone http://root:SHpass12!@10.8.106.150/root/test_framework.git /opt/test_framework"
# 3. 执行测试
sshpass -p "sonicauto" ssh root@10.103.50.112 "cd /opt/test_framework && source .venv/bin/activate && pytest tests/ -v"
# 4. 收集报告
sshpass -p "sonicauto" scp -r root@10.103.50.112:/opt/test_framework/reports/html /tmp/test_reports
```
## 安全注意事项
1. **密码保护**: 使用 GitLab CI/CD 变量存储敏感信息，不要硬编码在配置文件中
2. **网络安全**: 确保 GitLab Runner 服务器可以访问远程服务器的 22 端口
3. **权限控制**: 限制 GitLab Runner 服务器的访问权限
4. **日志清理**: 敏感信息变量设置为"屏蔽"，避免密码泄露在日志中
5. **定期更新**: 保持 GitLab、Runner 和依赖包的最新版本
## 高级配置
### 启用 Allure 报告
Allure 报告已默认启用，会自动收集并生成。
### 并行执行测试
在远程服务器上使用 pytest-xdist 进行并行测试：
```bash
# 安装 pytest-xdist
pip install pytest-xdist
# 并行执行
pytest tests/ -n auto --html=reports/html/test_report.html
```
### 添加测试覆盖率
```yaml
variables:
  PYTEST_ARGS: "-v --html=reports/html/test_report.html --self-contained-html --cov=src --cov-report=html:reports/coverage"
```
### 自定义 Allure 报告集成
如果使用 Allure Docker 服务，修改 `.gitlab-ci.yml` 中的报告收集步骤：
```yaml
# 使用 Allure Docker Service 生成可视化报告
allure generate auto-test-results/projects/fw-report/allure -o auto-test-results/projects/fw-report/html --clean
allure open auto-test-results/projects/fw-report/html
```
## 项目文档
### 主要文档
- **[GitLab CI 部署指南](docs/GITLAB_CI_DEPLOYMENT.md)** - GitLab 和 Runner 的完整安装配置指南
- **[架构设计文档](docs/Pytest_Playwright_CI_Framework_Design.md)** - 项目架构和组件边界说明
- **[Pytest 使用说明](docs/pytest_readme.md)** - Pytest 测试框架使用指南
### 脚本工具
- **[run-remote-tests.sh](scripts/run-remote-tests.sh)** - 远程测试执行脚本
- **[collect-reports.sh](scripts/collect-reports.sh)** - 报告收集与处理脚本
- **[verify_ci_pipeline.sh](verify_ci_pipeline.sh)** - CI 流水线验证脚本
- **[simple_verify.sh](simple_verify.sh)** - 简化验证脚本
## 维护与更新
### 依赖管理
定期更新项目依赖：
```bash
# 更新 Pytest
pip install --upgrade pytest
# 更新 Playwright
playwright install --deps
# 更新其他依赖
pip install --upgrade -r requirements.txt
```
### CI/CD 配置更新
修改 `.gitlab-ci.yml` 后提交并推送：
```bash
git add .gitlab-ci.yml
git commit -m "Update CI/CD configuration"
git push origin main
```
### 报告管理
定期清理旧报告：
```bash
# 清理 7 天前的报告
find reports/ -type d -mtime +7 -exec rm -rf {} \;
```
## 贡献指南
### 提交代码
1. 创建功能分支：`git checkout -b feature/new-feature`
2. 提交更改：`git commit -m "Add new feature"`
3. 推送到远程：`git push origin feature/new-feature`
4. 创建 Merge Request
### 代码规范
- 遵循 PEP 8 代码规范
- 添加必要的注释和文档字符串
- 编写测试用例
- 更新相关文档
## 许可证
本项目采用 MIT 许可证。
