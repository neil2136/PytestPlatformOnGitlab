# GitLab CI远程Pytest测试集成部署指南

## GitLab本地安装指南 (Ubuntu 20)

### 系统要求

- **操作系统**: Ubuntu 20.04 LTS
- **内存**: 最少4GB RAM (推荐8GB+)
- **存储**: 最少20GB可用空间
- **网络**: 稳定的互联网连接
- **权限**: sudo访问权限

### 安装步骤

#### 步骤1: 更新系统并安装依赖

```bash
# 更新系统包
sudo apt-get update && sudo apt-get upgrade -y

# 安装必要的依赖包
sudo apt-get install -y curl openssh-server ca-certificates tzdata perl

# 安装PostgreSQL (GitLab内置版本)
# 注意: GitLab CE 18.11.2需要PostgreSQL >= 16，建议使用GitLab内置PostgreSQL

# 安装Redis (用于缓存)
sudo apt-get install -y redis-server
```

#### 步骤2: 配置Redis

```bash
# 启动Redis服务
sudo systemctl start redis-server
sudo systemctl enable redis-server

# 验证Redis状态
sudo systemctl status redis-server

# 测试Redis连接
redis-cli ping
```

#### 步骤3: 添加GitLab仓库并安装

```bash
# 方法1: 官方安装 (如果网络良好)
# 添加GitLab官方GPG密钥
curl https://packages.gitlab.com/gpg.key 2> /dev/null | sudo apt-key add -

# 添加GitLab CE仓库
sudo curl -sS https://packages.gitlab.com/install/repositories/gitlab/gitlab-ce/script.deb.sh | sudo bash

# 安装GitLab CE (Community Edition)
# 使用EXTERNAL_URL设置您的GitLab访问地址
sudo EXTERNAL_URL="http://10.8.106.150" apt-get install gitlab-ce

# 方法2: 使用aria2c多线程下载 (网络慢时)
# 如果官方下载缓慢，可以使用aria2c下载deb包
aria2c -x 16 -s 16 https://packages.gitlab.com/ubuntu/focal/gitlab-ce_18.11.2-ce.0_amd64.deb
sudo dpkg -i gitlab-ce_18.11.2-ce.0_amd64.deb
```

#### 步骤4: 配置GitLab

```bash
# 编辑GitLab配置文件
sudo nano /etc/gitlab/gitlab.rb

# 主要配置项 (取消注释并修改):
external_url 'http://10.8.106.150'

# 使用GitLab内置PostgreSQL (推荐)
postgresql['enable'] = true

# Redis配置
redis['enable'] = true

# 邮件配置 (可选)
gitlab_rails['smtp_enable'] = true
gitlab_rails['smtp_address'] = "smtp.sonicwall.com"
gitlab_rails['smtp_port'] = 587
gitlab_rails['smtp_user_name'] = "lezhang@sonicwall.com"
gitlab_rails['smtp_password'] = "password"
gitlab_rails['smtp_domain'] = "smtp.sonicwall.com"
gitlab_rails['smtp_authentication'] = "login"
gitlab_rails['smtp_enable_starttls_auto'] = true
```

#### 步骤5: 重新配置并启动GitLab

```bash
# 重新配置GitLab (首次安装需要较长时间)
sudo gitlab-ctl reconfigure

# 检查GitLab状态
sudo gitlab-ctl status

# 启动GitLab服务
sudo gitlab-ctl start
```

#### 步骤6: 访问GitLab并设置管理员密码

```bash
# 查看初始root密码
sudo cat /etc/gitlab/initial_root_password
```

访问 `http://10.8.106.150`:
1. 使用用户名: `root`
2. 使用初始密码: 从上述文件中获取
3. 登录后立即修改密码

#### 步骤7: 配置防火墙 (可选)

```bash
# 允许HTTP和HTTPS流量
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow ssh

# 启用防火墙
sudo ufw enable
```

### 常用管理命令

```bash
# 查看GitLab状态
sudo gitlab-ctl status

# 重启GitLab服务
sudo gitlab-ctl restart

# 停止GitLab服务
sudo gitlab-ctl stop

# 查看日志
sudo gitlab-ctl tail

# 重新配置
sudo gitlab-ctl reconfigure

# 备份GitLab
sudo gitlab-rake gitlab:backup:create

# 查看GitLab版本
sudo gitlab-rake gitlab:env:info
```

### 故障排除

#### 问题1: 内存不足

**症状**: GitLab启动失败或响应缓慢

**解决方案**:
```bash
# 创建Swap文件
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

#### 问题2: 端口被占用

**症状**: GitLab无法启动，提示端口被占用

**解决方案**:
```bash
# 查看端口占用
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443

# 停止占用端口的服务
sudo systemctl stop nginx  # 如果有nginx运行
```

#### 问题3: GitLab版本兼容性

**症状**: PostgreSQL版本不兼容错误

**解决方案**:
```bash
# GitLab CE 18.11.2需要PostgreSQL >= 16
# 建议使用GitLab内置PostgreSQL，不要手动安装外部PostgreSQL

# 检查GitLab内置PostgreSQL状态
sudo gitlab-ctl status postgresql

# 如果已安装外部PostgreSQL，需要卸载
sudo apt-get remove --purge postgresql*
```

### 性能优化建议

1. **增加内存**: 建议至少8GB RAM
2. **使用SSD**: 提高I/O性能
3. **配置反向代理**: 使用Nginx作为前端代理
4. **定期备份**: 设置自动备份任务
5. **监控资源**: 使用`gitlab-ctl status`监控服务状态

---

## 概述

本指南介绍如何在本地GitLab CI上集成远程服务器(10.103.50.112)上已部署的pytest测试项目，实现自动化的测试执行和报告收集。

## 环境信息

- **GitLab服务器**: 本地部署
- **远程测试服务器**: 10.103.50.112
- **远程SSH认证**: root/sonicauto
- **远程项目路径**: `/test_framework/`
- **远程虚拟环境**: `/test_framework/.venv/`
- **测试执行命令**: `pytest tests/ --html=reports/html/test_report.html --self-contained-html`

## 部署步骤

### 步骤1: 安装GitLab Runner

GitLab Runner是执行CI/CD任务的代理程序。

#### 1.1 安装Runner

```bash
# 添加GitLab官方仓库
curl -L https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh | sudo bash

# 安装GitLab Runner
sudo apt-get install gitlab-runner

# 验证安装
gitlab-runner --version
```

#### 1.2 注册Runner到GitLab

```bash
# 注册Runner（需要GitLab的注册令牌）
sudo gitlab-runner register

# 交互式输入:
# - GitLab实例URL: http://your-gitlab-server (您的GitLab地址)
# - 注册令牌: 从GitLab项目页面获取 (Settings > CI/CD > Runners > New project runner)
# - Runner描述: Remote Pytest Runner
# - Runner标签: shell
# - 执行器类型: shell
```

#### 1.3 启动Runner服务

```bash
# 启动Runner
sudo gitlab-runner start

# 查看Runner状态
sudo gitlab-runner status

# 列出已注册的Runner
sudo gitlab-runner list
```

### 步骤2: 安装必要依赖

在GitLab Runner服务器上安装SSH密码认证工具：

```bash
# 安装sshpass（用于SSH密码认证）
sudo apt-get update
sudo apt-get install -y sshpass

# 验证安装
sshpass -V

# 安装其他必要工具
sudo apt-get install -y openssh-client
```

### 步骤3: 配置GitLab CI/CD变量

在GitLab项目中配置敏感信息：

1. 进入GitLab项目页面
2. 点击 **Settings** > **CI/CD** > **Variables** > **Add variable**
3. 添加以下变量：

| 变量名 | 值 | 保护 | 屏蔽 | 说明 |
|--------|-----|------|------|------|
| `REMOTE_SSH_PASSWORD` | `sonicauto` | ✓ | ✓ | SSH密码 |
| `REMOTE_HOST` | `10.103.50.112` | | | 远程服务器IP |
| `REMOTE_USER` | `root` | | | SSH用户名 |

**注意**: 
- 启用"保护"表示只在受保护分支使用
- 启用"屏蔽"表示在日志中隐藏该值

### 步骤4: 创建CI/CD配置文件

#### 4.1 创建 `.gitlab-ci.yml` 文件

在项目根目录创建`.gitlab-ci.yml`文件（已提供）：

```yaml
# 该文件已包含在项目中，路径: /ci/.gitlab-ci.yml
# 主要功能：
# - setup阶段: 测试SSH连接
# - topology阶段: 使用docker建立测试拓扑网络
# - deploy阶段: 克隆代码到远程服务器
# - test阶段: 远程执行pytest测试
# - report阶段: 收集测试报告、提取Allure JSON、生成Allure报告
# - sendmail阶段: 发送测试报告邮件
# - cleanup阶段: 清理远程服务器
```

#### 4.2 关键配置说明

**流水线阶段 (stages)**:
```yaml
stages:
  - setup      # 测试SSH连接
  - topology   # 使用docker建立测试拓扑网络
  - deploy     # 克隆代码到远程服务器
  - test       # 远程执行pytest测试
  - report     # 收集报告并生成Allure报告
  - sendmail   # 发送测试报告邮件
  - cleanup    # 清理远程服务器
```

**SSH连接配置**:
```yaml
# 使用sshpass进行密码认证
sshpass -p "$REMOTE_SSH_PASSWORD" ssh -o StrictHostKeyChecking=no \
    ${REMOTE_USER}@${REMOTE_HOST} "命令"
```

**远程测试执行**:
```yaml
# 激活虚拟环境并执行pytest
cd /opt/test_framework
source /test_framework/.venv/bin/activate
pytest tests/ -v --html=reports/html/test_report.html --self-contained-html --junitxml=reports/junit/test-results.xml --alluredir=reports/allure --cov=src --cov-report=html:reports/coverage
```

**报告收集与Allure生成**:
```yaml
# collect_reports job 完整流程：
# 1. 从远程服务器SCP拷贝报告到本地时间戳目录
# 2. 清理旧JSON文件并复制allure结果到统一目录 /ci/auto-test-results/projects/fw-report/results/
# 3. 复制报告到GitLab工作目录用于制品上传
# 4. 调用Allure Docker Service生成可视化报告（如服务不可用则跳过）
```

#### 4.3 重要注意事项

**避免YAML嵌套深度错误**:
GitLab CI限制script配置最多10级嵌套深度。以下配置会导致错误：

```yaml
# ❌ 错误示例 - 会导致嵌套深度错误
script:
  - |
    sshpass -p "$REMOTE_SSH_PASSWORD" ssh ${REMOTE_USER}@${REMOTE_HOST} << 'EOF'
      # 复杂的多行脚本
      if [ condition ]; then
        echo "复杂逻辑"
      fi
    EOF
```

**正确配置方式**:
```yaml
# ✅ 正确示例 - 使用单行命令
script:
  - sshpass -p "$REMOTE_SSH_PASSWORD" ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} "cd ${REMOTE_PROJECT_PATH} && source ${REMOTE_VENV_PATH}/bin/activate && pytest tests/ ${PYTEST_ARGS}"
```

**变量配置**:
```yaml
variables:
  # 远程服务器配置
  REMOTE_HOST: "10.103.50.112"
  REMOTE_USER: "root"
  REMOTE_SSH_PASSWORD: "sonicauto"
  REMOTE_PROJECT_PATH: "/opt/test_framework"
  REMOTE_REPORT_PATH: "/opt/test_framework/reports"
  REMOTE_VENV_PATH: "/test_framework/.venv"
  LOCAL_REPORT_DIR: "/ci/reports"
  GITLAB_USER: "root"
  GITLAB_PASSWORD: "SHpass12!"
  GIT_REPO_URL: "http://root:SHpass12!@10.8.106.150/root/test_framework.git"
  # pytest参数
  PYTEST_ARGS: "-v --html=reports/html/test_report.html --self-contained-html --junitxml=reports/junit/test-results.xml --alluredir=reports/allure --cov=src --cov-report=html:reports/coverage"
```

### 步骤5: 验证脚本和调试

#### 5.1 创建验证脚本

为了便于调试，我们创建了验证脚本：

**完整验证脚本**: `/ci/verify_ci_pipeline.sh`
```bash
#!/bin/bash
# 完整的CI流水线验证脚本
# 包含SSH连接、测试执行、报告收集的完整流程
```

**简化验证脚本**: `/ci/simple_verify.sh`
```bash
#!/bin/bash
# 简化版本，专注于核心功能验证
```

#### 5.2 命令行验证流程

```bash
# 1. 验证SSH连接
sshpass -p "$REMOTE_SSH_PASSWORD" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 ${REMOTE_USER}@${REMOTE_HOST} "echo 'SSH连接成功'"

# 2. 验证测试环境
sshpass -p "$REMOTE_SSH_PASSWORD" ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} "cd $REMOTE_PROJECT_PATH && source $REMOTE_VENV_PATH/bin/activate && python --version && pytest --version"

# 3. 执行远程测试
sshpass -p "$REMOTE_SSH_PASSWORD" ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} "cd $REMOTE_PROJECT_PATH && source $REMOTE_VENV_PATH/bin/activate && pytest tests/ $PYTEST_ARGS"

# 4. 验证报告生成
sshpass -p "$REMOTE_SSH_PASSWORD" ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} "test -f $REMOTE_PROJECT_PATH/reports/html/test_report.html"

# 5. 收集报告到本地
mkdir -p /tmp/ci_test_reports
sshpass -p "$REMOTE_SSH_PASSWORD" scp -o StrictHostKeyChecking=no -r ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PROJECT_PATH}/reports/html/* /tmp/ci_test_reports/
```

#### 5.3 运行验证脚本

```bash
# 运行完整验证
chmod +x /ci/verify_ci_pipeline.sh
/ci/verify_ci_pipeline.sh

# 运行简化验证
chmod +x /ci/simple_verify.sh
/ci/simple_verify.sh
```

### 步骤6: 测试配置

git 上传后触发pipeline 执行，可用过ui页面查看执行结果和log
root@vlab:/ci# git add .gitlab-ci.yml && git commit -m "modify gitlab-ci files" && git push origin master

#### 7.1 本地测试SSH连接

```bash
# 测试SSH连接（在GitLab Runner服务器上）
sshpass -p "sonicauto" ssh -o StrictHostKeyChecking=no root@10.103.50.112 "echo 'Connection OK'"
```

#### 7.2 测试远程pytest执行

```bash
# 执行测试脚本
REMOTE_SSH_PASSWORD=sonicauto ./scripts/run-remote-tests.sh
```

#### 7.3 测试报告收集

```bash
# 收集报告
REMOTE_SSH_PASSWORD=sonicauto ./scripts/collect-reports.sh

# 查看收集的报告
ls -la reports/html/
```

### 步骤7: 在GitLab中验证

#### 7.1 提交配置文件

```bash
# 添加文件到Git
git add .gitlab-ci.yml
git add scripts/
git commit -m "Add GitLab CI configuration for remote pytest execution"
git push origin main
```

#### 7.2 查看CI/CD流水线

1. 进入GitLab项目页面
2. 点击 **CI/CD** > **Pipelines**
3. 查看流水线执行状态

#### 7.3 查看测试报告

1. 进入Pipeline详情页
2. 点击 **Jobs** 标签
3. 点击具体Job查看日志
4. 在Job详情页查看 **Artifacts** 中的报告文件

## 文件结构

```
/ci/
├── .gitlab-ci.yml                    # GitLab CI主配置
├── scripts/
│   ├── run-remote-tests.sh           # 远程测试执行脚本
│   └── collect-reports.sh            # 报告收集脚本
├── docs/
│   └── GITLAB_CI_DEPLOYMENT.md       # 本部署文档
└── README_NEW.md                     # 项目说明
```

## 使用方式

### 自动触发

配置完成后，以下操作会自动触发CI流水线：

- 提交代码到`main`分支
- 提交代码到`develop`分支
- 创建Merge Request

### 手动触发

在GitLab项目页面：
1. 点击 **CI/CD** > **Pipelines**
2. 点击 **Run pipeline** 按钮
3. 选择分支
4. 点击 **Run pipeline**

### 定时触发（可选）

在`.gitlab-ci.yml`中添加：

```yaml
workflow:
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule"
    - if: $CI_PIPELINE_SOURCE == "push"
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
```

在GitLab中配置定时任务：
1. 点击 **CI/CD** > **Schedules**
2. 点击 **New schedule**
3. 设置定时规则（如: `0 2 * * *` 每天凌晨2点）

## 故障排除

### 问题1: YAML嵌套深度错误

**症状**: `script config should be a string or a nested array of strings up to 10 levels deep`

**解决方案**:
```yaml
# ❌ 错误配置 - 使用heredoc语法
script:
  - |
    sshpass -p "$REMOTE_SSH_PASSWORD" ssh ${REMOTE_USER}@${REMOTE_HOST} << 'EOF'
      # 多行脚本
    EOF

# ✅ 正确配置 - 使用单行命令
script:
  - sshpass -p "$REMOTE_SSH_PASSWORD" ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} "单行命令"
```

### 问题2: SSH连接失败

**症状**: `sshpass: command not found` 或连接超时

**解决方案**:
```bash
# 安装sshpass
sudo apt-get install -y sshpass

# 测试连接
sshpass -p "sonicauto" ssh -o StrictHostKeyChecking=no root@10.103.50.112 "echo test"
```

### 问题3: 远程虚拟环境激活失败

**症状**: `pytest: command not found`

**解决方案**:
```bash
# 手动检查远程环境
sshpass -p "sonicauto" ssh root@10.103.50.112 "
    cd /test_framework
    source /test_framework/.venv/bin/activate
    which pytest
    pytest --version
"
```

### 问题4: 报告文件未生成

**症状**: `reports/html/test_report.html not found`

**解决方案**:
```bash
# 在远程服务器上手动执行测试
cd /test_framework
source .venv/bin/activate
pytest tests/ --html=reports/html/test_report.html --self-contained-html

# 检查报告是否生成
ls -la reports/html/
```

### 问题5: GitLab Runner未执行

**症状**: Pipeline一直处于pending状态

**解决方案**:
```bash
# 检查Runner状态
sudo gitlab-runner status

# 检查Runner标签匹配
# .gitlab-ci.yml中的tags必须与Runner注册时的标签一致

# 查看Runner日志
sudo tail -f /var/log/gitlab-runner.log
```

### 问题6: CI变量未生效

**症状**: `REMOTE_SSH_PASSWORD: unbound variable`

**解决方案**:
1. 检查GitLab中变量是否正确设置
2. 确认变量已启用"保护"或"全部环境"
3. 重新保存变量设置

### 问题7: Playwright浏览器未安装

**症状**: `Executable doesn't exist at /root/.cache/ms-playwright/chromium-1091/chrome-linux/chrome`

**解决方案**:
```bash
# 在远程服务器上安装Playwright浏览器
sshpass -p "sonicauto" ssh root@10.103.50.112 "
    cd /test_framework
    source .venv/bin/activate
    playwright install
"
```

## 安全注意事项

1. **密码保护**: 使用GitLab CI/CD变量存储SSH密码，不要硬编码在配置文件中
2. **网络安全**: 确保GitLab Runner服务器可以访问10.103.50.112的22端口
3. **权限控制**: 限制GitLab Runner服务器的访问权限
4. **日志清理**: CI变量设置为"屏蔽"，避免密码泄露在日志中

## 高级配置

### 启用Allure报告（可选）

修改`.gitlab-ci.yml`中的pytest参数：

```yaml
variables:
  PYTEST_ARGS: "-v --html=reports/html/test_report.html --self-contained-html --alluredir=reports/allure"
```

### 并行执行测试

在远程服务器上使用pytest-xdist：

```bash
# 安装pytest-xdist
pip install pytest-xdist

# 并行执行
pytest tests/ -n auto --html=reports/html/test_report.html
```

### 添加测试覆盖率

```yaml
variables:
  PYTEST_ARGS: "-v --html=reports/html/test_report.html --self-contained-html --cov=src --cov-report=html:reports/coverage"
```

## 总结

### 实际验证结果

经过完整的安装、配置和验证流程，我们成功实现了：

1. **✅ GitLab CE 18.11.2 安装**: 使用aria2c解决网络下载问题
2. **✅ 内置PostgreSQL配置**: 避免版本兼容性问题
3. **✅ SSH连接认证**: sshpass密码认证正常工作
4. **✅ 远程测试执行**: pytest在远程服务器正常运行
5. **✅ 测试报告生成**: HTML报告成功生成（46KB）
6. **✅ 报告收集传输**: SCP成功收集报告到本地
7. **✅ GitLab CI配置**: 解决YAML嵌套深度限制问题

### 验证测试结果

```
============= 5 passed, 3 skipped, 7 warnings in 84.30s ==============
tests/api/test_interface_api.py ..                    ✅
tests/cli/test_interface_config.py ..                 ✅  
tests/functional/test_access_rules.py sss             ⚠️ (跳过)
tests/ui/test_interface_page.py .                    ✅ (UI测试通过)
```

### 关键经验教训

1. **网络问题**: 使用aria2c多线程下载解决GitLab CE下载缓慢问题
2. **版本兼容**: GitLab CE 18.11.2需要PostgreSQL >= 16，建议使用内置版本
3. **YAML限制**: GitLab CI script配置最多10级嵌套深度，避免heredoc语法
4. **环境变量**: 敏感信息使用GitLab CI/CD变量存储
5. **Playwright**: UI测试需要安装浏览器，可通过`playwright install`解决

### 最终配置状态

- **GitLab服务器**: `http://10.8.106.150`
- **远程测试服务器**: `10.103.50.112`
- **CI/CD流水线**: 3阶段（setup → test → report）
- **测试框架**: Python 3.12.3 + pytest 7.4.4
- **报告格式**: HTML自包含报告

完成以上步骤后，您的GitLab CI已成功集成远程pytest测试项目。每次代码提交或Merge Request都会自动触发远程测试，并将测试报告收集到GitLab中展示。

如有问题，请查看：
- GitLab CI/CD日志
- Runner服务器日志: `/var/log/gitlab-runner.log`
- 远程服务器上的pytest输出
- 验证脚本: `/ci/verify_ci_pipeline.sh` 和 `/ci/simple_verify.sh`
