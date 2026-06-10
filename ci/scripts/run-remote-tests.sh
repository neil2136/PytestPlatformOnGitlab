#!/bin/bash
#
# 远程Pytest测试执行脚本
# 用于在GitLab CI中通过SSH连接到远程服务器执行pytest测试
#
# 使用方式: ./run-remote-tests.sh
# 环境变量需要在GitLab CI/CD中设置 REMOTE_SSH_PASSWORD
#

set -e  # 遇到错误立即退出

# 配置变量
REMOTE_HOST="${REMOTE_HOST:-10.103.50.112}"
REMOTE_USER="${REMOTE_USER:-root}"
REMOTE_PASSWORD="${REMOTE_SSH_PASSWORD:-sonicauto}"
REMOTE_PROJECT_PATH="${REMOTE_PROJECT_PATH:-/opt/test_framework}"
REMOTE_VENV_PATH="${REMOTE_VENV_PATH:-/opt/test_framework/.venv}"
PYTEST_ARGS="${PYTEST_ARGS:--v --html=reports/html/test_report.html --self-contained-html}"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查sshpass是否安装
check_sshpass() {
    if ! command -v sshpass &> /dev/null; then
        print_info "Installing sshpass..."
        apt-get update -qq && apt-get install -y -qq sshpass
    fi
    print_success "sshpass is available"
}

# 测试SSH连接
test_ssh_connection() {
    print_info "Testing SSH connection to ${REMOTE_USER}@${REMOTE_HOST}..."
    
    if sshpass -p "$REMOTE_PASSWORD" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 -o BatchMode=no \
        ${REMOTE_USER}@${REMOTE_HOST} "echo 'SSH connection successful'" > /dev/null 2>&1; then
        print_success "SSH connection established"
        return 0
    else
        print_error "Failed to connect to remote server"
        return 1
    fi
}

# 在远程服务器上执行测试
run_remote_pytest() {
    print_info "Executing pytest on remote server..."
    print_info "Remote path: ${REMOTE_PROJECT_PATH}"
    print_info "Virtual env: ${REMOTE_VENV_PATH}"
    print_info "Pytest args: ${PYTEST_ARGS}"
    
    # 通过SSH执行测试
    sshpass -p "$REMOTE_PASSWORD" ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} << EOF
        set -e
        
        # 进入项目目录
        cd ${REMOTE_PROJECT_PATH}
        
        # 激活虚拟环境
        source ${REMOTE_VENV_PATH}/bin/activate
        
        # 显示环境信息
        echo "=========================================="
        echo "Python version: \$(python --version)"
        echo "Pytest version: \$(pytest --version | head -1)"
        echo "Working directory: \$(pwd)"
        echo "=========================================="
        
        # 清理旧报告
        echo "Cleaning old test reports..."
        rm -rf reports/html/*
        mkdir -p reports/html
        
        # 运行pytest测试
        echo "Running pytest tests..."
        pytest tests/ ${PYTEST_ARGS}
        
        TEST_EXIT_CODE=\$?
        echo "Test execution completed with exit code: \$TEST_EXIT_CODE"
        
        # 验证报告生成
        if [ -f "reports/html/test_report.html" ]; then
            echo "HTML report generated: \$(ls -lh reports/html/test_report.html)"
        fi
        
        exit \$TEST_EXIT_CODE
EOF
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        print_success "Remote tests completed successfully"
    else
        print_error "Remote tests failed with exit code: $exit_code"
    fi
    
    return $exit_code
}

# 显示使用帮助
show_help() {
    cat << EOF
远程Pytest测试执行脚本

用法: $0 [OPTIONS]

环境变量:
  REMOTE_HOST          远程服务器IP (默认: 10.103.50.112)
  REMOTE_USER          远程用户名 (默认: root)
  REMOTE_SSH_PASSWORD  SSH密码 (必需，默认: sonicauto)
  REMOTE_PROJECT_PATH  项目路径 (默认: /test_framework)
  REMOTE_VENV_PATH     虚拟环境路径 (默认: /test_framework/.venv)
  PYTEST_ARGS          pytest参数 (默认: -v --html=reports/html/test_report.html --self-contained-html)

示例:
  REMOTE_SSH_PASSWORD=mypassword $0
  REMOTE_HOST=192.168.1.100 PYTEST_ARGS="-v -x" $0

EOF
}

# 主函数
main() {
    # 检查帮助参数
    if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
        show_help
        exit 0
    fi
    
    echo "=========================================="
    echo " 远程Pytest测试执行脚本"
    echo "=========================================="
    
    # 检查必要的环境变量
    if [ -z "$REMOTE_PASSWORD" ]; then
        print_error "REMOTE_SSH_PASSWORD environment variable is required"
        print_info "Usage: REMOTE_SSH_PASSWORD=yourpassword $0"
        exit 1
    fi
    
    # 检查sshpass
    check_sshpass
    
    # 测试SSH连接
    if ! test_ssh_connection; then
        exit 1
    fi
    
    # 执行远程测试
    if run_remote_pytest; then
        print_success "All tests passed!"
        exit 0
    else
        print_error "Some tests failed"
        exit 1
    fi
}

# 运行主函数
main "$@"
