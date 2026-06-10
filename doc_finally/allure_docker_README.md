# Allure Docker Service 部署与使用指南

基于 [frankescobar/allure-docker-service](https://github.com/fescobar/allure-docker-service) 的 Allure 报告可视化服务，用于展示 CI 流水线生成的 pytest 测试报告。

## 架构概览

```
┌─────────────────────┐       ┌──────────────────────────┐       ┌──────────────────┐
│  GitLab CI Pipeline │──────>│  /ci/auto-test-results   │<──────│  Allure Docker   │
│  (collect_reports)  │ copy  │  /projects/fw-report/    │ mount │  Service (5050)  │
│                     │ json  │    results/*.json        │  -v   │  UI      (58080) │
└─────────────────────┘       └──────────────────────────┘       └──────────────────┘
```

- **Allure Docker Service** (后端): 端口 `5050`，管理项目数据并生成报告
- **Allure Docker Service UI** (前端): 端口 `58080`，浏览器访问报告界面
- 数据卷: 宿主机 `/ci/auto-test-results/projects` 映射到容器 `/app/projects`

## 快速安装

### 1. 导入镜像

```bash
cd /ci/allure_docker

# 导入 Allure 后端镜像
docker load -i as.tar

# 导入 Allure UI 镜像
docker load -i asu.tar

# 验证导入
docker images | grep allure
```

### 2. 创建数据目录

```bash
# 创建映射到容器 /app/projects 的宿主机目录
mkdir -p /ci/auto-test-results/projects

# 从 project_demo 复制项目模板
cp -r /ci/allure_docker/project_demo/auto-test-results/projects/* /ci/auto-test-results/projects/

# 提权（Allure 容器需要写入权限）
chmod 777 -R /ci/auto-test-results/
```

目录结构说明:

```
/ci/auto-test-results/projects/
├── default/              # 默认项目
│   ├── results/          # Allure 原始 JSON 结果
│   └── reports/          # 生成的 HTML 报告
└── fw-report/            # 防火墙测试项目（CI 使用）
    ├── results/          # pytest allure 插件输出的 JSON
    └── reports/          # Allure Docker 生成的可视化报告
```

### 3. 启动服务

```bash
# 停止旧容器（如存在）
docker rm -f allure-service allure-ui

# 启动后端
docker run -d \
  --name allure-service \
  --restart always \
  -p 58080:5050 \
  -e SECURITY_USER=admin \
  -e SECURITY_PASS=password \
  -e CHECK_RESULTS_EVERY_SECONDS=NONE \
  -e KEEP_HISTORY=1 \
  -e KEEP_HISTORY_LATEST=30 \
  -v /ci/auto-test-results/projects:/app/projects \
  frankescobar/allure-docker-service

# 启动 UI
docker run -d \
  --name allure-ui \
  --restart always \
  -p 58080:5252 \
  -e ALLURE_DOCKER_PUBLIC_API_URL=http://10.8.106.150:5050 \
  frankescobar/allure-docker-service-ui
```

### 4. 验证

```bash
# 检查容器状态（2 个 UP 即成功）
docker ps | grep allure

# 访问 UI
# http://<服务器IP>:58080
```

## CI 集成

GitLab CI 的 `collect_reports` stage 会自动将 allure 结果推送到 Docker 服务：

1. 从远程测试服务器 SCP 拷贝报告到 `/ci/reports/report_<timestamp>/`
2. 清理旧 JSON: `rm -f /ci/auto-test-results/projects/fw-report/results/*.json`
3. 复制新 JSON: `cp -f <report_dir>/allure/*.json /ci/auto-test-results/projects/fw-report/results/`
4. 触发报告生成: `curl ... http://10.8.106.150:5050/allure-docker-service/generate-report?project_id=fw-report&execution_type=gitlab&execution_name=GitlabCI`

详见 [.gitlab-ci.yml](../.gitlab-ci.yml) 中 `collect_reports` job。

## 手动操作

### 手动上传测试报告

```bash
# 1. 清理旧结果
rm -rf /ci/auto-test-results/projects/fw-report/results/*.json

# 2. 复制 allure JSON 文件
cp -f /ci/reports/report_<timestamp>/allure/*.json /ci/auto-test-results/projects/fw-report/results/

# 3. 触发报告生成
curl -v --request GET \
  --url "http://10.8.106.150:5050/allure-docker-service/generate-report?project_id=fw-report&execution_type=gitlab&execution_name=GitlabCI"
```

### 常用维护命令

```bash
# 查看后端日志（排查问题）
docker logs -f allure-service

# 查看最近 200 行日志
docker logs -f --tail 200 allure-service

# 重启服务
docker restart allure-service allure-ui

# 停止服务
docker stop allure-service allure-ui

# 彻底删除容器
docker rm -f allure-service allure-ui

# 进入后端容器 shell
docker exec -it allure-service bash
```

## 环境变量说明

| 变量 | 值 | 说明 |
|------|-----|------|
| `SECURITY_USER` | `admin` | 后端登录用户名 |
| `SECURITY_PASS` | `password` | 后端登录密码 |
| `CHECK_RESULTS_EVERY_SECONDS` | `NONE` | 自动检测间隔，NONE 表示仅手动触发 |
| `KEEP_HISTORY` | `1` | 保留历史报告 |
| `KEEP_HISTORY_LATEST` | `30` | 保留最近 30 次历史 |
| `ALLURE_DOCKER_PUBLIC_API_URL` | `http://10.8.106.150:5050` | UI 连接后端的地址 |

## 故障排除

| 问题 | 解决方案 |
|------|---------|
| UI 无法连接后端 | 确认 `ALLURE_DOCKER_PUBLIC_API_URL` 可从浏览器访问，检查 5050 端口 |
| 报告未更新 | 检查 `/ci/auto-test-results/projects/fw-report/results/` 下是否有新 JSON 文件 |
| 容器启动失败 | `docker logs allure-service` 查看日志，确认端口未被占用 |
| 权限错误 | `chmod 777 -R /ci/auto-test-results/` |
| CI 报告生成失败 | 检查 curl 返回值，确认 Allure Docker Service 正在运行 |
