#!/bin/bash
#
# Allure Docker 一键安装脚本
# 用法: ./install.sh [选项]
#
# 选项:
#   --skip-load    跳过镜像导入（已导入时使用）
#   --uninstall    卸载：停止并删除容器
#   -h, --help     显示帮助
#

set -euo pipefail

# ─── 配置 ───────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DATA_DIR="/ci/auto-test-results"
DEMO_DIR="${SCRIPT_DIR}/project_demo/auto-test-results/projects"
HOST_IP="10.8.106.150"

ALLURE_SERVICE_NAME="allure-service"
ALLURE_UI_NAME="allure-ui"
ALLURE_SERVICE_PORT=5050
ALLURE_UI_PORT=58080

SECURITY_USER="admin"
SECURITY_PASS="password"
KEEP_HISTORY=1
KEEP_HISTORY_LATEST=30

# ─── 颜色 ───────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
error()   { echo -e "${RED}[ERROR]${NC} $1"; }

# ─── 前置检查 ───────────────────────────────────────────
check_docker() {
    if ! command -v docker &>/dev/null; then
        error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    if ! docker info &>/dev/null; then
        error "Docker 服务未运行，请启动 Docker"
        exit 1
    fi
    success "Docker 已就绪"
}

check_images() {
    if docker images --format '{{.Repository}}' | grep -q 'frankescobar/allure-docker-service' && \
       docker images --format '{{.Repository}}' | grep -q 'frankescobar/allure-docker-service-ui'; then
        success "Allure Docker 镜像已存在"
        return 0
    else
        return 1
    fi
}

# ─── 步骤1: 导入镜像 ────────────────────────────────────
load_images() {
    if check_images; then
        info "镜像已存在，跳过导入（使用 --skip-load 强制跳过）"
        return 0
    fi

    info "导入 Allure Docker 镜像..."

    if [[ ! -f "${SCRIPT_DIR}/as.tar" ]]; then
        error "找不到后端镜像文件: ${SCRIPT_DIR}/as.tar"
        exit 1
    fi
    if [[ ! -f "${SCRIPT_DIR}/asu.tar" ]]; then
        error "找不到 UI 镜像文件: ${SCRIPT_DIR}/asu.tar"
        exit 1
    fi

    info "导入后端镜像 as.tar ..."
    docker load -i "${SCRIPT_DIR}/as.tar"

    info "导入 UI 镜像 asu.tar ..."
    docker load -i "${SCRIPT_DIR}/asu.tar"

    success "镜像导入完成"
    docker images | grep allure
}

# ─── 步骤2: 创建数据目录 ────────────────────────────────
setup_data_dir() {
    info "创建数据目录: ${DATA_DIR}/projects"
    mkdir -p "${DATA_DIR}/projects"

    # 从 project_demo 复制项目模板（仅在目录为空时）
    if [[ -d "${DEMO_DIR}" ]]; then
        info "复制项目模板到 ${DATA_DIR}/projects/"
        cp -r "${DEMO_DIR}/"* "${DATA_DIR}/projects/"
    else
        warn "未找到 project_demo 目录，跳过模板复制"
        # 确保至少有 fw-report 项目目录
        mkdir -p "${DATA_DIR}/projects/fw-report/results"
        mkdir -p "${DATA_DIR}/projects/fw-report/reports"
        mkdir -p "${DATA_DIR}/projects/default/results"
        mkdir -p "${DATA_DIR}/projects/default/reports"
    fi

    info "设置目录权限..."
    chmod 777 -R "${DATA_DIR}/"

    success "数据目录准备完成"
    echo "  目录结构:"
    find "${DATA_DIR}/projects" -maxdepth 2 -type d | head -20
}

# ─── 步骤3: 启动服务 ────────────────────────────────────
start_services() {
    # 停止旧容器
    info "停止旧容器（如存在）..."
    docker rm -f "${ALLURE_SERVICE_NAME}" 2>/dev/null || true
    docker rm -f "${ALLURE_UI_NAME}" 2>/dev/null || true

    info "启动 Allure Docker Service (后端)..."
    docker run -d \
        --name "${ALLURE_SERVICE_NAME}" \
        --restart always \
        -p ${ALLURE_SERVICE_PORT}:5050 \
        -e SECURITY_USER="${SECURITY_USER}" \
        -e SECURITY_PASS="${SECURITY_PASS}" \
        -e CHECK_RESULTS_EVERY_SECONDS=NONE \
        -e KEEP_HISTORY=${KEEP_HISTORY} \
        -e KEEP_HISTORY_LATEST=${KEEP_HISTORY_LATEST} \
        -v "${DATA_DIR}/projects:/app/projects" \
        frankescobar/allure-docker-service

    info "启动 Allure Docker Service UI (前端)..."
    docker run -d \
        --name "${ALLURE_UI_NAME}" \
        --restart always \
        -p ${ALLURE_UI_PORT}:5252 \
        -e ALLURE_DOCKER_PUBLIC_API_URL="http://${HOST_IP}:${ALLURE_SERVICE_PORT}" \
        frankescobar/allure-docker-service-ui

    success "服务启动完成"
}

# ─── 步骤4: 验证 ────────────────────────────────────────
verify() {
    echo ""
    echo "=========================================="
    echo "  Allure Docker 安装验证"
    echo "=========================================="

    # 检查容器状态
    local running
    running=$(docker ps --filter "name=allure" --format '{{.Names}} {{.Status}}' 2>/dev/null || true)

    if echo "$running" | grep -q "${ALLURE_SERVICE_NAME}" && echo "$running" | grep -q "${ALLURE_UI_NAME}"; then
        success "容器运行正常"
        echo "$running"
    else
        error "容器异常，请检查日志: docker logs ${ALLURE_SERVICE_NAME}"
        echo "$running"
        return 1
    fi

    # 检查后端 API
    info "检查后端 API..."
    if curl -sf --max-time 5 "http://localhost:${ALLURE_SERVICE_PORT}/allure-docker-service/version" &>/dev/null; then
        success "后端 API 可访问"
    else
        warn "后端 API 暂未就绪，服务可能仍在启动中"
    fi

    echo ""
    echo "=========================================="
    success "安装完成！"
    echo "  UI 访问地址: http://${HOST_IP}:${ALLURE_UI_PORT}"
    echo "  后端 API:    http://${HOST_IP}:${ALLURE_SERVICE_PORT}"
    echo "  登录用户:    ${SECURITY_USER}"
    echo "  登录密码:    ${SECURITY_PASS}"
    echo "=========================================="
}

# ─── 卸载 ───────────────────────────────────────────────
uninstall() {
    info "停止并删除 Allure Docker 容器..."
    docker rm -f "${ALLURE_SERVICE_NAME}" 2>/dev/null || true
    docker rm -f "${ALLURE_UI_NAME}" 2>/dev/null || true
    success "容器已删除"
    echo ""
    warn "数据目录 ${DATA_DIR} 未删除，如需清理请手动执行:"
    echo "  rm -rf ${DATA_DIR}"
}

# ─── 帮助 ───────────────────────────────────────────────
show_help() {
    cat <<EOF
Allure Docker 一键安装脚本

用法: $0 [选项]

选项:
  --skip-load      跳过镜像导入步骤
  --uninstall      卸载：停止并删除容器（不删除数据）
  -h, --help       显示帮助

环境变量:
  HOST_IP          后端 API 对外地址 (默认: ${HOST_IP})

示例:
  $0                     # 完整安装
  $0 --skip-load         # 跳过镜像导入
  HOST_IP=192.168.1.1 $0 # 指定对外 IP
  $0 --uninstall         # 卸载
EOF
}

# ─── 主流程 ─────────────────────────────────────────────
main() {
    local skip_load=false
    local do_uninstall=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --skip-load)   skip_load=true;  shift ;;
            --uninstall)   do_uninstall=true; shift ;;
            -h|--help)     show_help; exit 0 ;;
            *)             error "未知选项: $1"; show_help; exit 1 ;;
        esac
    done

    echo "=========================================="
    echo "  Allure Docker 一键安装"
    echo "=========================================="

    if [[ "$do_uninstall" == true ]]; then
        check_docker
        uninstall
        exit 0
    fi

    check_docker

    if [[ "$skip_load" == false ]]; then
        load_images
    else
        info "跳过镜像导入"
    fi

    setup_data_dir
    start_services
    verify
}

main "$@"
