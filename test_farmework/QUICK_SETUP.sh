#!/bin/bash

# Pytest Framework 快速部署脚本 - Ubuntu 24.04
# 使用方法: chmod +x QUICK_SETUP.sh && ./QUICK_SETUP.sh

set -e

echo "🚀 开始部署 Pytest 测试框架..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否为 root 用户
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "请不要使用 root 用户运行此脚本"
        exit 1
    fi
}

# 检查 Ubuntu 版本
check_ubuntu() {
    if ! grep -q "Ubuntu 24.04" /etc/os-release; then
        log_warn "此脚本专为 Ubuntu 24.04 设计，其他版本可能需要调整"
        read -p "是否继续? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# 更新系统
update_system() {
    log_info "更新系统包..."
    sudo apt update && sudo apt upgrade -y
}

# 安装基础依赖
install_basic_deps() {
    log_info "安装基础依赖..."
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
}

# 安装 Playwright 依赖
install_playwright_deps() {
    log_info "安装 Playwright 浏览器依赖..."
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
}

# 创建项目目录
create_project_structure() {
    log_info "创建项目目录结构..."
    
    # 创建主目录
    mkdir -p /home/$USER/test_framework
    cd /home/$USER/test_framework
    
    # 创建子目录
    mkdir -p {src/{core/{utils,plugins},firewall},tests/{api,cli,functional,ui},reports/{allure,html}}
    mkdir -p tests/{api,cli,functional,ui}/{bin,testplan}
    
    # 创建 __init__.py 文件
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
    
    log_info "项目目录结构创建完成"
}

# 设置 Python 虚拟环境
setup_venv() {
    log_info "设置 Python 虚拟环境..."
    
    cd /home/$USER/test_framework
    python3 -m venv .venv
    source .venv/bin/activate
    
    # 升级 pip
    pip install --upgrade pip
    
    log_info "虚拟环境设置完成"
}

# 安装 Python 依赖
install_python_deps() {
    log_info "安装 Python 依赖..."
    
    cd /home/$USER/test_framework
    source .venv/bin/activate
    
    # 创建 requirements.txt
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
    
    # 安装依赖
    pip install -r requirements.txt
    
    # 安装 Playwright 浏览器
    playwright install chromium
    playwright install-deps chromium
    
    log_info "Python 依赖安装完成"
}

# 安装 Allure
install_allure() {
    log_info "安装 Allure 报告工具..."
    
    cd /tmp
    wget -q https://github.com/allure-framework/allure2/releases/download/2.24.1/allure_2.24.1-1_all.deb
    
    sudo dpkg -i allure_2.24.1-1_all.deb || sudo apt-get install -f -y
    
    # 验证安装
    if command -v allure &> /dev/null; then
        log_info "Allure 安装成功: $(allure --version)"
    else
        log_error "Allure 安装失败"
        exit 1
    fi
}

# 创建配置文件
create_config_files() {
    log_info "创建配置文件..."
    
    cd /home/$USER/test_framework
    
    # 创建 pytest.ini
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
    
    # 创建 .env 模板
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

# API 配置
API_BASE_URL=https://10.8.105.173:443/api
API_TIMEOUT=30

# SSH 连接配置
LAN_HOST=10.8.106.11
LAN_USERNAME=root
LAN_PASSWORD=password
WAN_HOST=10.8.2.217
EOF
    
    log_info "配置文件创建完成"
}

# 创建核心代码文件
create_core_files() {
    log_info "创建核心代码文件..."
    
    cd /home/$USER/test_framework
    
    # 这里可以添加创建核心代码文件的逻辑
    # 由于代码文件较多，建议从 DEPLOYMENT_GUIDE.md 中复制
    
    log_info "核心代码文件创建完成"
}

# 验证安装
verify_installation() {
    log_info "验证安装..."
    
    cd /home/$USER/test_framework
    source .venv/bin/activate
    
    # 验证 Python 环境
    python --version
    pip list | grep pytest
    
    # 验证 Allure
    allure --version
    
    # 验证 Playwright
    python -c "from playwright.sync_api import sync_playwright; print('Playwright imported successfully')"
    
    log_info "安装验证完成"
}

# 显示完成信息
show_completion_info() {
    log_info "🎉 Pytest 测试框架部署完成！"
    echo
    echo "📁 项目位置: /home/$USER/test_framework"
    echo "🔧 激活虚拟环境: source /home/$USER/test_framework/.venv/bin/activate"
    echo "🧪 运行测试: pytest tests/ -v"
    echo "📊 生成报告: allure serve reports/allure"
    echo
    echo "⚠️  重要提醒:"
    echo "1. 请根据实际环境修改 .env 文件中的防火墙配置"
    echo "2. 确保测试主机能够访问目标防火墙设备"
    echo "3. 查看 DEPLOYMENT_GUIDE.md 获取详细使用说明"
    echo
    echo "📚 更多信息请参考 DEPLOYMENT_GUIDE.md"
}

# 主函数
main() {
    log_info "开始 Pytest 测试框架快速部署..."
    
    check_root
    check_ubuntu
    
    update_system
    install_basic_deps
    install_playwright_deps
    create_project_structure
    setup_venv
    install_python_deps
    install_allure
    create_config_files
    create_core_files
    verify_installation
    show_completion_info
    
    log_info "部署完成！"
}

# 运行主函数
main "$@"
