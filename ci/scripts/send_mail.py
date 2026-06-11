#!/usr/bin/env python3
"""
发送测试报告邮件脚本
从本地路径获取 HTML 报告并发送到指定邮箱
"""

import smtplib
import os
import sys
import argparse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime


# ===== 配置项（可通过环境变量覆盖）=====
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.163.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER", "horace365@163.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "xxxxxxxx")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"

MAIL_FROM = os.getenv("MAIL_FROM", "horace365@163.com")
MAIL_TO = os.getenv("MAIL_TO", "horace365@163.com").split(",")

# 调试模式（生产环境建议关闭）
DEBUG = os.getenv("DEBUG", "false").lower() == "true"


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="发送测试报告邮件")
    parser.add_argument("--report_path", required=True, help="HTML报告文件的路径")
    return parser.parse_args()


def get_test_summary(report_path):
    """从 HTML 报告中提取测试摘要信息"""
    summary = {"total": 0, "passed": 0, "failed": 0, "skipped": 0, "error": 0}

    try:
        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 尝试从 pytest-html 报告中提取摘要
        import re

        # 匹配 pytest-html 的摘要行，例如: "5 tests took 00:01:22."
        ran_match = re.search(r'(\d+)\s+tests?\s+took', content)
        if ran_match:
            summary["total"] = int(ran_match.group(1))

        # 匹配各类结果计数，考虑 HTML 标签和逗号格式
        # 例如: <span class="passed">5 Passed,</span>
        passed_match = re.search(r'<span class="passed">(\d+)\s+Passed,</span>', content)
        if passed_match:
            summary["passed"] = int(passed_match.group(1))

        failed_match = re.search(r'<span class="failed">(\d+)\s+Failed,</span>', content)
        if failed_match:
            summary["failed"] = int(failed_match.group(1))

        skipped_match = re.search(r'<span class="skipped">(\d+)\s+Skipped,</span>', content)
        if skipped_match:
            summary["skipped"] = int(skipped_match.group(1))

        error_match = re.search(r'<span class="error">(\d+)\s+Errors,</span>', content)
        if error_match:
            summary["error"] = int(error_match.group(1))

    except Exception as e:
        print(f"[WARN] 无法解析测试摘要: {e}")

    return summary


def build_email_body(summary):
    """构建邮件正文 HTML"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 根据测试结果决定状态颜色
    if summary["failed"] > 0 or summary["error"] > 0:
        status_color = "#e74c3c"
        status_text = "❌ 存在失败用例"
    else:
        status_color = "#27ae60"
        status_text = "✅ 全部通过"

    body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #2c3e50; color: white; padding: 15px 20px; border-radius: 5.5px 5.5px 0 0; }}
            .content {{ background: #f9f9f9; padding: 20px; border: 1px solid #ddd; border-radius: 0 0 5.5px 5.5px; }}
            .status {{ font-size: 18px; font-weight: bold; padding: 10px; border-radius: 3px; color: white; background: {status_color}; text-align: center; margin: 15px 0; }}
            table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
            th {{ background: #34495e; color: white; padding: 10px; text-align: left; }}
            td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
            .footer {{ margin-top: 20px; color: #888; font-size: 12px; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2 style="margin:0;">🔥 Firewall 自动化测试报告</h2>
            </div>
            <div class="content">
                <div class="status">{status_text}</div>
                <p><strong>报告时间：</strong>{now}</p>
                <p><strong>测试环境：</strong>Static Testbed</p>

                <table>
                    <tr><th>指标</th><th>数量</th></tr>
                    <tr><td>总用例数</td><td>{summary['total']}</td></tr>
                    <tr><td>✅ 通过</td><td>{summary['passed']}</td></tr>
                    <tr><td>❌ 失败</td><td>{summary['failed']}</td></tr>
                    <tr><td>⏭ 跳过</td><td>{summary['skipped']}</td></tr>
                    <tr><td>⚠ 错误</td><td>{summary['error']}</td></tr>
                </table>

                <p>详细测试报告请查看附件 <strong>test_report.html</strong></p>
            </div>
            <div class="footer">
                此邮件由 GitLab CI Pipeline 自动发送，请勿直接回复。
            </div>
        </div>
    </body>
    </html>
    """
    return body


def send_email(report_path):
    """发送带附件的邮件"""
    summary = get_test_summary(report_path)
    print(f"[INFO] 测试摘要: {summary}")

    msg = MIMEMultipart()
    msg["From"] = MAIL_FROM
    msg["To"] = ", ".join(MAIL_TO)
    msg["Subject"] = f"[Firewall CI] 测试报告 - {datetime.now().strftime('%Y-%m-%d %H:%M')} - {'通过' if summary['failed'] == 0 and summary['error'] == 0 else '存在失败'}"

    # HTML 正文
    html_body = build_email_body(summary)
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    # 添加 HTML 报告附件
    with open(report_path, "rb") as f:
        attachment = MIMEApplication(f.read(), _subtype="html")
        attachment.add_header("Content-Disposition", "attachment", filename="test_report.html")
        msg.attach(attachment)

    # 发送邮件
    print(f"[INFO] 连接 SMTP 服务器: {SMTP_HOST}:{SMTP_PORT}")
    try:
        if SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT)
        else:
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)

        if DEBUG:
            print(f"[DEBUG] SMTP 服务器配置: host={SMTP_HOST}, port={SMTP_PORT}, user={SMTP_USER}")
            print(f"[DEBUG] 邮件收发人: from={MAIL_FROM}, to={MAIL_TO}")

        if SMTP_USE_TLS and SMTP_PORT != 465:
            server.starttls()
            if DEBUG:
                print("[DEBUG] TLS 已启用")

        if SMTP_PASSWORD:
            server.login(SMTP_USER, SMTP_PASSWORD)
            if DEBUG:
                print("[DEBUG] SMTP 认证成功")

        server.sendmail(MAIL_FROM, MAIL_TO, msg.as_string())
        server.quit()
        print(f"[INFO] 邮件发送成功! 收件人: {', '.join(MAIL_TO)}")
    except smtplib.SMTPAuthenticationError:
        print("[ERROR] SMTP 认证失败，请检查 SMTP_USER 和 SMTP_PASSWORD")
        sys.exit(1)
    except smtplib.SMTPConnectError:
        print(f"[ERROR] 无法连接 SMTP 服务器: {SMTP_HOST}:{SMTP_PORT}")
        print("[ERROR] 请检查 SMTP_HOST 是否正确，或者网络连接是否正常")
        sys.exit(1)
    except smtplib.SMTPServerDisconnected:
        print("[ERROR] SMTP 服务器断开连接")
        sys.exit(1)
    except smtplib.SMTPException as e:
        print(f"[ERROR] SMTP 错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] 邮件发送失败: {e}")
        import socket
        try:
            socket.gethostbyname(SMTP_HOST)
            print(f"[DEBUG] SMTP 主机 {SMTP_HOST} 解析正常")
        except socket.gaierror:
            print(f"[DEBUG] SMTP 主机 {SMTP_HOST} 解析失败")
        sys.exit(1)


def main():
    # 步骤1: 解析命令行参数
    args = parse_arguments()
    report_path = args.report_path

    # 步骤2: 发送邮件
    send_email(report_path)


if __name__ == "__main__":
    main()
