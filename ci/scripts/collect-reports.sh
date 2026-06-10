#!/bin/bash
#
# 测试报告收集脚本
# 从远程服务器复制pytest测试报告到GitLab CI本地
#
# 使用方式: ./collect-reports.sh
#

set -euo pipefail
IFS=$'\n\t'

DEBUG_MODE=0
if [[ "${1:-}" == "--debug" || "${1:-}" == "-x" ]]; then
    DEBUG_MODE=1
    shift
fi
if [[ "${DEBUG_MODE}" -eq 1 ]]; then
    set -x
    SCP_OPTS="-v -o StrictHostKeyChecking=no -r"
else
    SCP_OPTS="-o StrictHostKeyChecking=no -r"
fi

# 配置变量
REMOTE_HOST="${REMOTE_HOST:-10.103.50.112}"
REMOTE_USER="${REMOTE_USER:-root}"
REMOTE_PASSWORD="${REMOTE_SSH_PASSWORD:-sonicauto}"
REMOTE_PROJECT_PATH="${REMOTE_PROJECT_PATH:-/opt/test_framework}"
REMOTE_REPORT_PATH="${REMOTE_REPORT_PATH:-${REMOTE_PROJECT_PATH}/reports}"
LOCAL_REPORT_ROOT="${LOCAL_REPORT_DIR:-/ci/reports}"
LOCAL_REPORT_DIR="${LOCAL_REPORT_ROOT%/}/report_$(date '+%Y%m%d%H%M%S')"

# Expand GitLab variable references if they were passed literally
if [[ "${LOCAL_REPORT_ROOT}" == *'${CI_PROJECT_DIR}'* ]] || [[ "${LOCAL_REPORT_ROOT}" == *'$CI_PROJECT_DIR'* ]]; then
    LOCAL_REPORT_ROOT="${LOCAL_REPORT_ROOT//\$\{CI_PROJECT_DIR\}/${CI_PROJECT_DIR}}"
    LOCAL_REPORT_ROOT="${LOCAL_REPORT_ROOT//\$CI_PROJECT_DIR/${CI_PROJECT_DIR}}"
    LOCAL_REPORT_DIR="${LOCAL_REPORT_ROOT%/}/report_$(date '+%Y%m%d%H%M%S')"
fi

mkdir -p "${LOCAL_REPORT_DIR}"


# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# 检查sshpass
check_sshpass() {
    if ! command -v sshpass &> /dev/null; then
        print_info "Installing sshpass..."
        apt-get update -qq && apt-get install -y -qq sshpass
    fi
}

# 从远程服务器复制报告
collect_reports() {
    print_info "Collecting reports from ${REMOTE_USER}@${REMOTE_HOST}..."
    print_info "Local report root: ${LOCAL_REPORT_ROOT}"
    print_info "Local report directory before realpath: ${LOCAL_REPORT_DIR}"

    mkdir -p "${LOCAL_REPORT_DIR}"
    LOCAL_REPORT_DIR=$(realpath "${LOCAL_REPORT_DIR}")
    print_info "Local report directory: ${LOCAL_REPORT_DIR}"
    print_info "Remote report directory: ${REMOTE_REPORT_PATH}"

    mkdir -p "${LOCAL_REPORT_DIR}/html"
    mkdir -p "${LOCAL_REPORT_DIR}/allure"
    mkdir -p "${LOCAL_REPORT_DIR}/coverage"

    copy_remote_dir "html" "${LOCAL_REPORT_DIR}/html"
    copy_remote_dir "allure" "${LOCAL_REPORT_DIR}/allure"
    copy_remote_dir "coverage" "${LOCAL_REPORT_DIR}/coverage"

    verify_reports
}

copy_remote_dir() {
    local remote_subdir="$1"
    local local_subdir="$2"
    local remote_dir="${REMOTE_REPORT_PATH}/${remote_subdir}"

    print_info "Copying ${remote_subdir} reports from ${remote_dir}..."

    if sshpass -p "$REMOTE_PASSWORD" ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} "test -d '${remote_dir}'" > /dev/null 2>&1; then
        print_info "Remote directory exists: ${REMOTE_USER}@${REMOTE_HOST}:${remote_dir}"
        print_info "Listing remote content for ${remote_dir}..."
        sshpass -p "$REMOTE_PASSWORD" ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} "ls -la '${remote_dir}' || true"
        local remote_file_count
        remote_file_count=$(sshpass -p "$REMOTE_PASSWORD" ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} "find '${remote_dir}' -maxdepth 1 -type f | wc -l || true")
        print_info "Remote ${remote_subdir} file count: ${remote_file_count}"

        print_info "Copying from ${REMOTE_USER}@${REMOTE_HOST}:${remote_dir} to ${local_subdir}"
        # 核心修复：使用 remote_dir/. 将远程目录内容复制到本地目标目录，而不是把目录本身嵌套进来
        if sshpass -p "$REMOTE_PASSWORD" scp ${SCP_OPTS} \
            "${REMOTE_USER}@${REMOTE_HOST}:${remote_dir}/." "${local_subdir}/"; then
            print_success "${remote_subdir^} reports copied successfully"
            local local_file_count=$(find "${local_subdir}" -type f | wc -l)
            print_info "Local ${remote_subdir} file count after copy: ${local_file_count}"
        else
            local scp_exit=$?
            print_warning "Failed to copy ${remote_subdir} reports from ${remote_dir}, scp exit code ${scp_exit}"
            print_info "Verify remote path exists and SSH credentials are correct"
        fi
    else
        print_warning "Remote directory not found: ${remote_dir}"
    fi
}

# 验证报告
verify_reports() {
    print_info "Verifying collected reports..."

    for subdir in html allure coverage; do
        local dir="${LOCAL_REPORT_DIR}/${subdir}"
        print_info "Checking ${subdir} reports in ${dir}"

        if [ -d "${dir}" ]; then
            local file_count=$(find "${dir}" -type f | wc -l)
            if [ ${file_count} -gt 0 ]; then
                print_success "Found ${file_count} file(s) in ${subdir}"
                ls -lh "${dir}"
            else
                print_warning "No files found in ${subdir}"
            fi
        else
            print_warning "Directory does not exist: ${dir}"
        fi
    done
}

# 创建报告索引页面
create_report_index() {
    :
}

# 显示使用帮助
show_help() {
    cat <<'EOF'
Usage: ./scripts/collect-reports.sh [OPTIONS]

Options:
  -x, --debug      Enable bash debug mode (set -x) and show each executed command
  -h, --help       Show this help message and exit

Environment variables:
  REMOTE_HOST         Remote server address (default: 10.103.50.112)
  REMOTE_USER         Remote SSH user (default: root)
  REMOTE_SSH_PASSWORD Remote SSH password (default: sonicauto)
  REMOTE_PROJECT_PATH Remote project path (default: /opt/test_framework)
  REMOTE_REPORT_PATH  Remote report path (default: ${REMOTE_PROJECT_PATH}/reports)
  LOCAL_REPORT_DIR    Local report root directory (default: /ci/reports)
EOF
}

# 主函数
main() {
    if [ "$#" -gt 0 ]; then
        case "$1" in
            -h|--help)
                show_help
                exit 0
                ;;
            -x|--debug)
                # Debug mode is already enabled at script startup.
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    fi
    
    echo "=========================================="
    echo " 测试报告收集脚本"
    echo "=========================================="
    
    # 检查密码
    if [ -z "$REMOTE_PASSWORD" ]; then
        print_error "REMOTE_SSH_PASSWORD environment variable is required"
        exit 1
    fi
    
    # 检查sshpass
    check_sshpass
    
    # 收集报告
    collect_reports
    
    print_success "Report collection completed!"
}

main "$@"