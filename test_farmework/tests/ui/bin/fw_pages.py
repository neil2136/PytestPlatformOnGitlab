# pages/fw_page.py, Firewall pages manager class for accessing different page objects
from .base_page import BasePage
from .login_page import LoginPage
from .interface_page import InterfacePage
from playwright.sync_api import Page


class FWPage(BasePage):
    """Firewall pages manager class for accessing different page objects"""
    
    def __init__(self, page: Page, base_url="https://10.8.105.173/sonicui/7"):
        super().__init__(page)
        self.page = page
        self.base_url = base_url
        self._pages = {}  # Page instance cache
    
    # ========== Page Objects Accessor ==========
    
    @property
    def login(self):
        """Access all methods of LoginPage"""
        if 'login' not in self._pages:
            self._pages['login'] = LoginPage(self.page, self.base_url)
        return self._pages['login']

    @property
    def interface(self):
        """Access all methods of Interface pages"""
        if 'interface' not in self._pages:
            self._pages['interface'] = InterfacePage(self.page, self.base_url)
        return self._pages['interface']