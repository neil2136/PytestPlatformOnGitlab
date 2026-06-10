"""
Test case for firewall interface page using Playwright
Tests:
1. Login to firewall via browser
2. Navigate to network/interfaces page
3. Check if DMZ zone exists in the interface table
"""
import pytest
import allure
from playwright.sync_api import sync_playwright
from tests.ui.bin.ui_helpers import BaseUITest


@pytest.mark.ui
class TestInterfacePage(BaseUITest):
    """Interface page UI test using Playwright"""
    
    @allure.title("测试防火墙接口页面 - 检查 DMZ Zone")
    @allure.description("通过浏览器登录防火墙，进入 network/interfaces 页面，检查是否存在 DMZ zone")
    @allure.tag("ui", "playwright", "interface", "dmz")
    def test_interface_page_has_dmz_zone(self):
        """Test interface page for DMZ zone existence"""
        
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            context = browser.new_context(
                ignore_https_errors=True,
                viewport={'width': 1920, 'height': 1080}
            )
            page = context.new_page()
            
            try:
                with allure.step("Step 1: 登录防火墙"):
                    # Navigate to login page
                    page.goto("https://10.8.105.173/sonicui/7/login", timeout=60000)
                    page.wait_for_load_state('networkidle', timeout=60000)
                    
                    # Take screenshot of login page
                    screenshot = page.screenshot()
                    allure.attach(screenshot, name="Login Page", attachment_type=allure.attachment_type.PNG)
                    
                    # Wait for and fill username
                    page.locator("input[name='username']").wait_for(state='visible', timeout=30000)
                    page.fill("input[name='username']", "admin")
                    page.fill("input[name='password']", "password2")
                    
                    # Click login
                    page.click("text=LOG IN")
                    page.wait_for_timeout(5000)
                    page.wait_for_load_state('networkidle', timeout=30000)
                    
                    # Handle preempt dialog if present
                    if "/login" in page.url:
                        config_button = page.locator("button:has-text('Config')")
                        if config_button.count() > 0:
                            config_button.click()
                            page.wait_for_timeout(5000)
                            page.wait_for_load_state('networkidle', timeout=30000)
                    
                    # Verify login success
                    assert "/dashboard" in page.url or "/mgmt" in page.url, f"Login failed: {page.url}"
                    
                    screenshot = page.screenshot()
                    allure.attach(screenshot, name="After Login", attachment_type=allure.attachment_type.PNG)
                    allure.attach("Login successful", name="Login Status", attachment_type=allure.attachment_type.TEXT)
                
                with allure.step("Step 2: 进入 Network/Interfaces 页面"):
                    # Click NETWORK tab
                    page.click("text=NETWORK")
                    page.wait_for_timeout(3000)
                    page.wait_for_load_state('networkidle', timeout=30000)
                    
                    # Click on IPv4 tab to see interface settings
                    page.click("text=IPv4")
                    page.wait_for_timeout(5000)
                    page.wait_for_load_state('networkidle', timeout=30000)
                    
                    screenshot = page.screenshot()
                    allure.attach(screenshot, name="Interface Page", attachment_type=allure.attachment_type.PNG)
                    
                    # Verify page URL
                    assert "network/interfaces" in page.url, f"Not on interface page: {page.url}"
                    allure.attach("Successfully navigated to interface page", name="Navigation Status", attachment_type=allure.attachment_type.TEXT)
                
                with allure.step("Step 3: 检查 DMZ Zone 是否存在"):
                    # Check for DMZ in page content
                    page_text = page.locator("body").text_content()
                    has_dmz = "DMZ" in page_text
                    
                    # Check interface table for DMZ
                    table = page.locator(".interface-settings-ipv4")
                    if table.count() > 0:
                        rows = table.locator(".sw-table-row").all()
                        for row in rows:
                            row_text = row.text_content()
                            if "DMZ" in row_text:
                                has_dmz = True
                                allure.attach(row_text[:100], name="DMZ Row", attachment_type=allure.attachment_type.TEXT)
                                break
                    
                    screenshot = page.screenshot()
                    allure.attach(screenshot, name="Final Interface Page", attachment_type=allure.attachment_type.PNG)
                    
                    # Assert DMZ zone exists
                    assert has_dmz, "DMZ zone not found in interface table"
                    allure.attach("DMZ zone verified successfully", name="Test Result", attachment_type=allure.attachment_type.TEXT)
                    
            finally:
                page.close()
                context.close()
                browser.close()
