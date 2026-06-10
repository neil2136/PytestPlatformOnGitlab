一键导入镜像
cd /ci/allure_docker

# 导入 Allure 后端
docker load -i as.tar

# 导入 Allure UI
docker load -i asu.tar
查看是否导入成功
docker images | grep allure

一键启动 Allure Docker 服务
# 停止旧容器
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
访问地址：
http://你的服务器IP:58080
常用维护命令
# 查看日志（排查问题用）
docker logs -f allure-service

# 重启服务
docker restart allure-service allure-ui

# 停止服务
docker stop allure-service allure-ui

# 彻底删除服务
docker rm -f allure-service allure-ui
查看是否正常运行
docker ps | grep allure
出现 2 个 UP 状态的容器就成功了！

在本地创建映射到docker /app/projects的目录：
mkdir -p /ci/auto-test-results
mkdir -p /ci/auto-test-results/projects

复制project_dome内的目录到/ci下作为映射目录：
。。。
给复制的目录提权
chmod 777 -R /ci/auto-test-results/

等待远端测试环境的pytest出报告后并自动同步到/ci/auto-test-results后，即可在UI上查看allure报告

进入docker shell：
docker exec -it allure-service bash
检查docker log：
docker logs -f --tail 200 allure-service

手动在本地添加测试报告的方式
rm -rf /ci/auto-test-results/projects/fw-report/results/*.json
cp -f /ci/reports/report_20260515111519/allure/*.json /ci/auto-test-results/projects/fw-report/results/ 

curl -v --request GET --url http://10.8.106.150:5050/allure-docker-service/generate-report?project_id=fw-report&execution_type=gitlab&execution_name=GitlabCI