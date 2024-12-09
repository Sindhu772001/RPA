import time
import json
import random
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.utils.logger import Logger
from RPA.Browser.Selenium import Selenium

log = Logger(rotation_type='size').get_logger()

class MAEUContainerBuilder(object):
    def __init__(self, browser):
        self.browser = browser

    def __call__(self, container, **_ignored):
        instance = MAEUContainer(container_number=container, browser=self.browser)
        instance.extract_data()
        return instance
    
class MAEUContainer:
    """
    Class to handle Maersk container tracking and data extraction.
    """

    BASE_TRACKING_URL = "https://www.maersk.com/tracking/{container_number}"

    def __init__(self, container_number, browser):
        self.container_number = container_number
        self.browser = browser
        self.shipping_line = "Maersk"
        self.data = {}
        self.milestones = []
        self.tracking_url = self.BASE_TRACKING_URL.format(container_number=container_number)
        self.open_tracking_page()

    def open_tracking_page(self):
        try:
            self.browser.open_available_browser(
                self.tracking_url,
                options={"arguments": ["--start-maximized", "--disable-blink-features=AutomationControlled"]}
            )
            self.random_sleep(3, 5)
            self.handle_cookies()
        except Exception as e:
            raise RuntimeError(f"Error opening tracking page: {e}")

    def handle_cookies(self):
        try:
            cookie_xpaths = [
                "//button[contains(text(),'Accept All')]",
                "//button[contains(text(),'Accept Cookies')]",
                "//button[contains(text(),'I Accept')]",
                "//button[contains(text(),'Allow all')]",
                "//button[contains(@aria-label, 'Accept cookies')]"
            ]
            for xpath in cookie_xpaths:
                if self.browser.does_page_contain_element(xpath):
                    self.browser.click_element(xpath)
                    return
        except Exception as e:
            raise RuntimeError(f"Error handling cookies: {e}")

    def extract_data(self):
        try:
            self.extract_main_fields()
            self.extract_milestones()
        except Exception as e:
            raise RuntimeError(f"Error extracting data: {e}")

    def extract_main_fields(self):
        fields = {
            "ContainerNo": "xpath://*[@id='maersk-app']/div/main/div[1]/dl/div[1]/dd",
            "From": "xpath://*[@id='maersk-app']/div/main/div[1]/dl/div[2]/div[1]/dd",
            "To": "xpath://*[@id='maersk-app']/div/main/div[1]/dl/div[2]/div[2]/dd",
            "ContainerType": "xpath://*[@id='maersk-app']/div/main/div[2]/div/header/mc-text-and-icon[1]/span[3]",
            "EstimatedArrivalDate": "xpath://*[@id='maersk-app']/div/main/div[2]/div/div[1]/mc-text-and-icon[1]//div/span/slot[2]/text()",
            "LastLocation": "xpath://*[@id='maersk-app']/div/main/div[2]/div/div[1]/mc-text-and-icon[2]/span"
        }

        for field, xpath in fields.items():
            try:
                if self.browser.does_page_contain_element(xpath):
                    text = self.browser.get_text(xpath)
                    self.data[field] = text.strip()
            except Exception:
                self.data[field] = None

    def extract_milestones(self):
        list_items_xpath = "//ul[@data-test='transport-plan-list']/li[@data-test='transport-plan-item-complete']"
        try:
            milestones_elements = self.browser.find_elements(list_items_xpath)
            for index, element in enumerate(milestones_elements, start=1):
                milestone_xpath = f"({list_items_xpath})[{index}]"
                data = {}
                try:
                    data['status'] = self.browser.get_text(f"{milestone_xpath}//div[@data-test='milestone']/span")
                    data['date'] = self.browser.get_text(f"{milestone_xpath}//div[@data-test='milestone']//span[@data-test='milestone-date']")
                    data['location'] = self.browser.get_text(f"{milestone_xpath}//div[@data-test='location-name']/strong")
                except Exception:
                    pass
                self.milestones.append(data)
        except Exception:
            raise RuntimeError("Error extracting milestones")

    def random_sleep(self, min_time, max_time):
        sleep_time = random.uniform(min_time, max_time)
        time.sleep(sleep_time)

    def close_browser(self):
        try:
            self.browser.close_all_browsers()
        except Exception:
            pass