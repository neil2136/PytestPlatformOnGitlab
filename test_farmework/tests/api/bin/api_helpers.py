"""
API 测试公共工具类
提供可复用的 API 测试方法
"""
import allure


class APIHelpers:
    """API 测试辅助工具类"""
    
    @staticmethod
    def verify_api_response(response, expected_status=200):
        """验证 API 响应的通用方法"""
        assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code}"
        return response.json()
    
    @staticmethod
    def verify_success_status(response_data):
        """验证响应中的 success 状态"""
        assert "status" in response_data
        assert response_data["status"]["success"] is True
        
        # 验证 CLI 状态
        if "cli" in response_data["status"]:
            cli_info = response_data["status"]["cli"]
            assert cli_info["configuring"] is True
            assert cli_info["pending_config"] is True
            assert cli_info["restart_required"] == "FALSE"
        
        # 验证信息消息
        if "info" in response_data["status"]:
            info_list = response_data["status"]["info"]
            assert len(info_list) > 0
            assert info_list[0]["level"] == "info"
            assert info_list[0]["code"] == "E_OK"
            assert info_list[0]["message"] == "Success."
    
    @staticmethod
    def attach_response_to_allure(response, name="API Response"):
        """将响应附加到 Allure 报告"""
        allure.attach(
            response.text,
            name=name,
            attachment_type=allure.attachment_type.JSON
        )


class BaseAPITest(APIHelpers):
    """API 测试基类，继承 API 辅助工具"""
    pass
