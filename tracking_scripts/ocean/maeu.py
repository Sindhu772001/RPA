import time
import json
import random
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.utils.logger import Logger
from RPA.Browser.Selenium import Selenium

log = Logger(rotation_type='size').get_logger()

class MAEUContainerBuilder(object):
    def __init__(self, browser):
        self.browser = browser

    def __call__(self, container, **kwargs):
        instance = MAEUContainer(container_number=container, browser=self.browser)
        instance.extract_data()
        return instance
    
class MAEUContainer:
    BASE_TRACKING_URL = "https://www.maersk.com/tracking/{container_number}"

    def __init__(self, container_number, browser):
        self.container_number = container_number
        self.browser = browser
        self.shipping_line = "Maersk"
        self.data = {}
        self.milestones = []
        self.tracking_url = self.BASE_TRACKING_URL.format(container_number=container_number)
        self.open_tracking_page()
        self.extract_data()

    def open_tracking_page(self):
        try:
            self.browser.open_available_browser(
                self.tracking_url,
                options={"arguments": ["--start-maximized", "--disable-blink-features=AutomationControlled"]}
            )
            self.random_sleep(3, 5)
            self.handle_cookies()
        except Exception as e:
            log.error(f"Error opening tracking page: {e}")
            raise RuntimeError(f"Error opening tracking page: {e}")

    def random_sleep(self, min_seconds, max_seconds):
        sleep_time = random.randint(min_seconds, max_seconds)
        log.info(f"Sleeping for {sleep_time} seconds...")
        time.sleep(sleep_time)

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
                    log.info(f"Clicking cookie consent button with xpath: {xpath}")
                    self.browser.click_element(xpath)
                    return
            log.info("No cookie consent button found.")
        except Exception as e:
            log.error(f"Error handling cookies: {e}")
            raise RuntimeError(f"Error handling cookies: {e}")

    def extract_data(self):
        try:
            self.data = self.extract_main_fields()
            self.milestones = self.extract_milestones()
            data = json.dumps(self.data, indent=4)
            log.info(f"Data extracted: {data}")

        except Exception as e:
            log.error(f"Error extracting data: {e}")
            raise RuntimeError(f"Error extracting data: {e}")
        return data

    def extract_main_fields(self):
        fields = {
            "ContainerNo": "xpath://*[@id='maersk-app']/div/main/div[1]/dl/div[1]/dd",
            "From": "xpath://*[@id='maersk-app']/div/main/div[1]/dl/div[2]/div[1]/dd",
            "To": "xpath://*[@id='maersk-app']/div/main/div[1]/dl/div[2]/div[2]/dd",
            "ContainerType": "xpath://*[@id='maersk-app']/div/main/div[2]/div/header/mc-text-and-icon[1]/span[3]",
            "EstimatedArrivalDate": "xpath://*[@id='maersk-app']/div/main/div[2]/div/div[1]/mc-text-and-icon[1]//div/span/slot[2]/text()",
            "LastLocation": "xpath://*[@id='maersk-app']/div/main/div[2]/div/div[1]/mc-text-and-icon[2]/span"
        }
        extracted_fields = {}
        try:
            for field_name, xpath in fields.items():
                if self.browser.is_element_visible(xpath):
                    text = self.browser.get_text(xpath)
                    if field_name == "LastLocation" and text:
                        parts = text.split("•")
                        if len(parts) >= 2:
                            extracted_fields[field_name] = parts[1].strip()
                        else:
                            extracted_fields[field_name] = text.strip()
                    else:
                        extracted_fields[field_name] = text
                else:
                    extracted_fields[field_name] = None
        
            milestones = self.extract_milestones()
            extracted_fields["Milestones"] = milestones
        except Exception as e:
            log.error(f"Error extracting main fields: {e}")
        return extracted_fields

    def extract_milestones(self):
        tracking_events = []
        previous_location = None
        try:
            list_items_xpath = "//ul[@data-test='transport-plan-list']/li[@data-test='transport-plan-item-complete']"
            list_items = self.browser.find_elements(list_items_xpath)

            if not list_items:
                return tracking_events

            for index, item in enumerate(list_items, start=1):
                location_xpath = f"({list_items_xpath})[{index}]//div[@data-test='location-name']/strong"
                port_xpath = f"({list_items_xpath})[{index}]//div[@data-test='location-name']/br"
                milestone_xpath = f"({list_items_xpath})[{index}]//div[@data-test='milestone']/span"
                date_xpath = f"({list_items_xpath})[{index}]//div[@data-test='milestone']//span[@data-test='milestone-date']"
                vessel_xpath = f"({list_items_xpath})[{index}]//div[@data-test='milestone']/span[contains(text(), 'Vessel')]"

                location = self.browser.find_element(location_xpath).text if self.browser.is_element_visible(location_xpath) else None
                port = self.browser.find_element(port_xpath).text if self.browser.is_element_visible(port_xpath) else None
                milestone = self.browser.find_element(milestone_xpath).text if self.browser.is_element_visible(milestone_xpath) else None
                date = self.browser.find_element(date_xpath).text if self.browser.is_element_visible(date_xpath) else None

                if location and port:
                    location = f"{location}, {port}"
                elif location is None and port is None:
                    location = previous_location if previous_location else ""
                elif location is None:
                    location = port

                tracking_event = {
                    "status": milestone,
                    "date": date,
                    "location": location
                }

                tracking_event = {key: value for key, value in tracking_event.items() if value is not None}

                tracking_events.append(tracking_event)

                previous_location = location
        except Exception as e:
            log.error(f"Error during browser operation: {e}")

        return tracking_events

    def close_browser(self):
        """
        Closes the browser session.
        """
        try:
            self.browser.close_all_browsers()
            log.info("Browser closed successfully.")
        except Exception as e:
            log.error(f"Error closing the browser: {e}")    
