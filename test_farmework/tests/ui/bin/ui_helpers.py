"""
UI 测试公共工具类
提供可复用的 UI 测试方法
"""
import allure
from playwright.sync_api import sync_playwright


class UIHelpers:
    """UI 测试辅助工具类"""
    
    @staticmethod
    def create_browser_context(headless=True):
        """创建浏览器上下文"""
        p = sync_playwright().start()
        browser = p.chromium.launch(
            headless=headless,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        context = browser.new_context(
            ignore_https_errors=True,
            viewport={'width': 1920, 'height': 1080}
        )
        return browser, context
    
    @staticmethod
    def login_to_firewall(page, username="admin", password="password2"):
        """标准登录防火墙流程"""
        page.goto("https://10.8.105.173/sonicui/7/login", timeout=60000)
        page.wait_for_load_state('networkidle', timeout=60000)
        
        # 填写凭据
        page.locator("input[name='username']").wait_for(state='visible', timeout=30000)
        page.fill("input[name='username']", username)
        page.fill("input[name='password']", password)
        page.click("text=LOG IN")
        
        # 等待登录
        page.wait_for_timeout(5000)
        page.wait_for_load_state('networkidle', timeout=30000)
        
        # 处理 preempt 对话框
        if "/login" in page.url:
            config_button = page.locator("button:has-text('Config')")
            if config_button.count() > 0:
                config_button.click()
                page.wait_for_timeout(5000)
                page.wait_for_load_state('networkidle', timeout=30000)
        
        # 验证登录成功
        assert "/dashboard" in page.url or "/mgmt" in page.url, f"Login failed: {page.url}"
        
        return page
    
    @staticmethod
    def attach_screenshot_to_allure(page, name="Screenshot"):
        """截取屏幕并附加到 Allure 报告"""
        screenshot = page.screenshot()
        allure.attach(screenshot, name=name, attachment_type=allure.attachment_type.PNG)
    
    @staticmethod
    def wait_and_click(page, selector, timeout=30000):
        """等待元素可点击并点击"""
        page.locator(selector).wait_for(state='visible', timeout=timeout)
        page.click(selector)
    
    @staticmethod
    def wait_and_fill(page, selector, value, timeout=30000):
        """等待元素可见并填充值"""
        page.locator(selector).wait_for(state='visible', timeout=timeout)
        page.fill(selector, value)


class BaseUITest(UIHelpers):
    """UI 测试基类，继承 UI 辅助工具"""
    pass
