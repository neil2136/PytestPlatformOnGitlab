# pages/Network/System/interface.py, Page Methods for Interface Page
from .base_page import BasePage
from playwright.sync_api import Locator
import logging

logger = logging.getLogger('interface')


class InterfacePage(BasePage):
    """Interface page for checking interface configuration"""
    
    # Interface table selectors
    INTERFACE_TABLE = ".interface-settings-ipv4"
    INTERFACE_ROW = ".sw-table-row"
    ZONE_COLUMN = "td:nth-child(3)"  # Zone column in interface table
    
    def __init__(self, page, base_url="https://10.8.105.173/sonicui/7"):
        super().__init__(page)
        self.base_url = base_url
        self.interface_url = base_url + "/mgmt/network/interfaces"
    
    def navigate_to_interface_page(self):
        """Navigate to network/interfaces page"""
        logger.info(f'Navigating to interface page: {self.interface_url}')
        self.page.goto(self.interface_url)
        # Wait for page to load
        self.page.wait_for_load_state('networkidle')
        logger.info('Interface page loaded')
    
    def has_dmz_zone(self) -> bool:
        """Check if DMZ zone exists in the interface table"""
        logger.info('Checking for DMZ zone in interface table')
        
        try:
            # Get all rows in the interface table
            rows = self.page.locator(f"{self.INTERFACE_TABLE} {self.INTERFACE_ROW}").all()
            
            for row in rows:
                # Get the zone text from the zone column
                zone_text = row.locator(self.ZONE_COLUMN).text_content()
                if zone_text:
                    zone_text = zone_text.strip()
                    logger.info(f'Found zone: {zone_text}')
                    if zone_text == "DMZ":
                        logger.info('DMZ zone found!')
                        return True
            
            logger.info('DMZ zone not found in interface table')
            return False
            
        except Exception as e:
            logger.error(f'Error checking for DMZ zone: {e}')
            return False
    
    def get_interface_zone(self, interface_name: str) -> str:
        """Get zone for specific interface"""
        logger.info(f'Getting zone for interface: {interface_name}')
        
        try:
            # Find row with interface name
            rows = self.page.locator(f"{self.INTERFACE_TABLE} {self.INTERFACE_ROW}").all()
            
            for row in rows:
                name_text = row.locator("td:first-child").text_content()
                if name_text and interface_name in name_text:
                    zone_text = row.locator(self.ZONE_COLUMN).text_content()
                    if zone_text:
                        return zone_text.strip()
            
            return ""
            
        except Exception as e:
            logger.error(f'Error getting interface zone: {e}')
            return ""