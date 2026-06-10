# pages/login_page.py, Page Methods for Login Page
from .base_page import BasePage
import logging

logger = logging.getLogger('login_page')


class LoginPage(BasePage):
    # Element locators
    USERNAME_INPUT = "input[name='username']"
    PASSWORD_INPUT = "input[name='password']"
    LOGIN_BUTTON = "text=LOG IN"
    CONTINUE_BUTTON = "text=Continue"
    CONFIG_BUTTON = "button[text='Config']"
    LAUNCH_SCREEN_CONTAINER = ".fw-mgmt-launch-screen__bottom-container"
    MANUAL_CONFIGURE_LINK = ".fw-mgmt-launch-screen__info-text div:nth-of-type(2) a"
    PREEMPT_LINE = ".login-ftr-preempt__line .sw-typo-heading-4"
    MAIN_PAGE = ".fw-app-content"
    
    def __init__(self, page, base_url="https://10.8.105.173/sonicui/7"):
        super().__init__(page)
        self.url = base_url + '/login'

    def navigate_to_login_page(self):
        """navigate to login page"""
        logger.info(f'Navigating to: {self.url}')
        self.page.goto(self.url, timeout=60000)
        # Wait for page to be fully loaded
        self.page.wait_for_load_state('networkidle', timeout=60000)
        # Additional wait for JavaScript rendering
        self.page.wait_for_timeout(5000)
        logger.info('Login page loaded')

    def login(self, username='admin', password='password2'):
        # logger.info('Click accept button')
        # self.click('text=I Accept')
        logger.info(f'Login FW with user name: {username}')
        
        # Wait for username field to be visible
        logger.info('Waiting for username field...')
        try:
            self.page.locator(self.USERNAME_INPUT).wait_for(state='visible', timeout=60000)
            logger.info('Username field is visible')
        except Exception as e:
            logger.error(f'Username field not visible: {e}')
            raise
        
        self.fill(self.USERNAME_INPUT, username)
        logger.info(f'Fill user password: {password}')
        self.fill(self.PASSWORD_INPUT, password)
        logger.info('Click login button')
        self.click(self.LOGIN_BUTTON)

        # Wait for navigation after login
        self.page.wait_for_load_state('networkidle', timeout=30000)
        
        # Handle launch screen if present (for new installations)
        try:
            if self.page.locator(self.LAUNCH_SCREEN_CONTAINER).is_visible(timeout=5000):
                logger.info('Get launch screen container and click manual configure link')
                self.click(self.MANUAL_CONFIGURE_LINK)
                self.page.wait_for_load_state('networkidle', timeout=10000)
        except Exception as e:
            logger.info(f'No launch screen detected: {e}')

        # Handle config mode preempt if present
        try:
            config_button = self.page.get_by_role("button", name='Config', exact=True)
            if config_button.is_visible(timeout=5000):
                logger.info('Preempt to config mode')
                config_button.click()
                self.page.wait_for_load_state('networkidle', timeout=10000)
        except Exception as e:
            logger.info(f'No config mode button detected: {e}')
        
        # Handle proceed button if present
        try:
            proceed_button = self.page.get_by_role("button", name='Proceed', exact=True)
            if proceed_button.is_visible(timeout=5000):
                logger.info('Proceed to config mode')
                proceed_button.click()
                self.page.wait_for_load_state('networkidle', timeout=10000)
        except Exception as e:
            logger.info(f'No proceed button detected: {e}')

        logger.info('Wait for main page to load......')
        try:
            self.wait_for_selector(self.MAIN_PAGE, timeout=30000)
        except Exception as e:
            logger.warning(f'Main page selector not found: {e}')
   
        res = self.is_login_successful()
        logger.info(f'Check login status......{res}')

        if not res:
            try:
                error_msg = self.get_error_message()
                logger.error(f'Login failed with error message: {error_msg}')
            except:
                pass
        
        return res

    def get_error_message(self) -> str:
        """Get login error message"""
        return self.get_text(self.STATUS_MESSAGE)
    
    def is_login_successful(self) -> bool:
        """Check login status"""
        url = self.page.url
        return "/dashboard" in url or "/mgmt" in url or "/sonicui" in url