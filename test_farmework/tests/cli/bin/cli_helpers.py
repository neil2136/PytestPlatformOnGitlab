"""
CLI 测试公共工具类
提供可复用的 CLI 测试方法
"""
import allure


class CLIHelpers:
    """CLI 测试辅助工具类"""
    
    @staticmethod
    def verify_cli_output(output, expected_patterns=None):
        """验证 CLI 输出的通用方法"""
        if expected_patterns:
            for pattern in expected_patterns:
                assert pattern in output, f"Expected pattern '{pattern}' not found in CLI output"
        return output
    
    @staticmethod
    def attach_cli_output_to_allure(output, name="CLI Output"):
        """将 CLI 输出附加到 Allure 报告"""
        allure.attach(
            output,
            name=name,
            attachment_type=allure.attachment_type.TEXT
        )
    
    @staticmethod
    def execute_cli_commands(cli_client, commands):
        """批量执行 CLI 命令"""
        outputs = []
        for cmd in commands:
            try:
                output = cli_client.execute_command(cmd, timeout=30)
                outputs.append(f"{cmd}\n{output}")
            except Exception as e:
                outputs.append(f"{cmd}\nError: {str(e)}")
        return "\n".join(outputs)


class BaseCLITest(CLIHelpers):
    """CLI 测试基类，继承 CLI 辅助工具"""
    pass
