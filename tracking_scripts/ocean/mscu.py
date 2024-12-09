import time
import json
import random
import os, sys
from .base import ShippingContainer
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.utils.logger import Logger
from RPA.Browser.Selenium import Selenium

log = Logger(rotation_type='size').get_logger()

class MSCUContainerBuilder(object):
    
    def __init__(self, browser):
        self.browser = browser

    def __call__(self, container, **_ignored):
        self._instance = MSCUContainer(container, self.browser)
        return self._instance
    
class MSCUContainer(ShippingContainer):
    """
    MSCU specific container class inheriting from ShippingContainer.
    """
    def __init__(self, container_number, browser):
        super().__init__(cn=container_number)
        self.shipping_line = "CMA"
        self.browser = browser if browser else Selenium() 
        
    def random_sleep(self, min_time, max_time):
        """
        Introduces a random delay to simulate user behavior.
        """
        try:
            sleep_time = random.uniform(min_time, max_time)
            time.sleep(sleep_time)
            log.info(f"Random sleep for {sleep_time:.2f} seconds.")
            return sleep_time
        except Exception as e:
            log.error(f"Error during random sleep: {e}")
            raise

    def open_tracking_page(self):
        """
        Opens the tracking page and handles cookies.
        """
        try:
            self.browser.open_available_browser(
                "https://www.msc.com/en/track-a-shipment",
                options={"arguments": ["--start-maximized", "--disable-blink-features=AutomationControlled"]}
            )
            log.info("Browser opened. Navigating to the tracking page.")
            self.random_sleep(3, 5)
            self.handle_cookies()
            log.info("Tracking page ready.")
        except Exception as e:
            log.error(f"Error opening the tracking page: {e}")
            raise

    def handle_cookies(self):
        """
        Handles cookie banners dynamically.
        """
        try:
            log.info("Checking for cookie banners...")
            cookie_xpaths = [
                "//button[contains(text(),'Accept All')]",
                "//button[contains(text(),'Accept Cookies')]",
                "//button[contains(text(),'I Accept')]",
                "//button[contains(@aria-label, 'Accept cookies')]"
            ]
            for xpath in cookie_xpaths:
                if self.browser.does_page_contain_element(xpath):
                    self.browser.click_element(xpath)
                    log.info(f"Cookie banner handled using: {xpath}")
                    return
            log.info("No cookie banner detected.")
        except Exception as e:
            log.error(f"Error handling cookies: {e}")
            raise

    def search_container(self, container_number):
        """
        Inputs the container number into the tracking field and submits the form.
        """
        try:
            log.info(f"Searching for container number {container_number}...")
            input_xpath = '//*[@id="trackingNumber"]'
            self.browser.wait_until_element_is_visible(input_xpath, timeout=10)
            self.browser.input_text(input_xpath, container_number)
            self.random_sleep(2, 4)
            log.info(f"Container number {container_number} entered.")

            self.browser.press_keys(input_xpath, 'ENTER')
            self.random_sleep(3, 5)
            log.info("Enter key pressed to submit the form.")
            return self.extract_data_from_page()
        except Exception as e:
            log.error(f"Error searching for container {container_number}: {e}")
            return None
    def extract_data_from_page(self):
        """
        Extracts data fields from the page using a predefined JSON mapping.
        """

        data = {}
        try:
            log.info("Extracting data fields from the page...")
            fields_to_extract = {
                "containerNumber": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[2]/ul/li[1]/div[1]/span[2]",
                "conatinerType": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[1]/div/div[2]/div/div/div/span[2]",
                "pol": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[2]/ul/li[3]/span[2]/span[1]",
                "pod": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[2]/ul/li[4]/span[2]/span[1]",
                "priceCalculationDate": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[2]/ul/li[7]/span[2]",
            }

            for field, xpath in fields_to_extract.items():
                self.browser.wait_until_element_is_visible(xpath, timeout=10)
                data[field] = self.browser.get_text(xpath)

            transhipment_ports_xpaths = [
                "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[2]/ul/li[6]/span[2]",
                "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[2]/ul/li[6]/span[3]"
            ]
            data["transhipmentPorts"] = [
                self.browser.get_text(xpath) for xpath in transhipment_ports_xpaths
            ]

            shipment_dates_fields = {
                "priceCalculation": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[2]/ul/li[7]/span[2]",
                "eta": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[1]/div/div[4]/div/div/div/span[2]",
                "estimatedArrival": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[2]/div[2]/div[1]/div/div[2]/div/div/span[2]"
            }
            data["shipmentDates"] = {
                field: self.browser.get_text(xpath)
                for field, xpath in shipment_dates_fields.items()
            }

            transhipments_xpaths = [
                {
                    "location": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div[3]/div/div/span",
                    "vessel": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div[5]/div",
                    "event": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div[4]/div/div/span",
                    "date": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[2]/div[2]/div[3]/div/div[2]/div/div/span[2]"
                },
                {
                    "location": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[2]/div[2]/div[4]/div/div[3]/div/div/span",
                    "vessel": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[2]/div[2]/div[4]/div/div[5]/div",
                    "event": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[2]/div[2]/div[5]/div/div[4]/div/div/span",
                    "date": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[2]/div[2]/div[4]/div/div[2]/div/div/span[2]"
                },
                {
                    "location": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[2]/div[2]/div[6]/div/div[3]/div/div/span",
                    "vessel": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[2]/div[2]/div[6]/div/div[5]/div/div/span/span",
                    "event": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[2]/div[2]/div[6]/div/div[4]/div/div/span",
                    "date": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[2]/div[2]/div[6]/div/div[2]/div/div/span[2]"
                },
                {
                    "location": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[2]/div[2]/div[7]/div/div[3]/div/div/span",
                    "vessel": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[2]/div[2]/div[6]/div/div[5]/div/div/span/span",
                    "event": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[2]/div[2]/div[6]/div/div[4]/div/div/span",
                    "date": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[2]/div[2]/div[6]/div/div[2]/div/div/span[2]"
                },
                {
                    "location": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[2]/div[2]/div[7]/div/div[3]/div/div/span",
                    "vessel": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[2]/div[2]/div[7]/div/div[5]/div",
                    "event": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[2]/div[2]/div[7]/div/div[4]/div/div/span",
                    "date": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[2]/div[2]/div[7]/div/div[2]/div/div/span[2]"
                },
                {
                    "location": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[2]/div[2]/div[8]/div/div[3]/div/div/span",
                    "vessel": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[2]/div[2]/div[8]/div/div[5]/div",
                    "event": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[2]/div[2]/div[8]/div/div[4]/div/div/span",
                    "date": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[2]/div[2]/div[8]/div/div[2]/div/div/span[2]"
                },
                {
                    "location": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[2]/div[2]/div[9]/div/div[3]/div/div/span",
                    "vessel": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[2]/div[2]/div[9]/div/div[5]/div/div/span/span",
                    "event": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[2]/div[2]/div[9]/div/div[4]/div/div/span",
                    "date": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[2]/div[2]/div[9]/div/div[2]/div/div/span[2]"
                },
                {
                    "location": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[2]/div[2]/div[10]/div/div[3]/div/div/span",
                    "vessel": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[2]/div[2]/div[10]/div/div[5]/div/div/span/span",
                    "event": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[2]/div[2]/div[10]/div/div[4]/div/div/span",
                    "date": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[2]/div[2]/div[10]/div/div[2]/div/div/span[2]",
                    "status": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[2]/div[2]/div[10]/div/div[5]/div/div/span/span"
                }
            ]
            data["transhipments"] = []
            for transhipment_field_set in transhipments_xpaths:
                transhipment_data = {}
                for field, xpath in transhipment_field_set.items():
                    self.browser.wait_until_element_is_visible(xpath, timeout=10)
                    transhipment_data[field] = self.browser.get_text(xpath)
                data["transhipments"].append(transhipment_data)

            latest_move_fields = {
                "location": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[1]/div/div[3]/div/div/div/span[2]",
                "eta": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[1]/div/div[4]/div/div/div/span[2]"
            }
            data["latestMove"] = {
                field: self.browser.get_text(xpath)
                for field, xpath in latest_move_fields.items()
            }

            vessel_info_xpaths = [
                {
                    "name": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[2]/div[2]/div[2]/div/div[5]/div",
                    "event": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[2]/div[2]/div[2]/div/div[4]/div/div/span",
                    "location": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[2]/div[2]/div[2]/div/div[3]/div/div/span",
                    "date": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[2]/div[2]/div[2]/div/div[2]/div/div/span[2]"
                },
                {
                    "name": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[2]/div[2]/div[1]/div/div[5]/div",
                    "event": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[2]/div[2]/div[1]/div/div[4]/div/div/span",
                    "location": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[2]/div[2]/div[1]/div/div[3]/div/div/span",
                    "date": "xpath://*[@id='main']/div[1]/div/div[3]/div/div/div/div[1]/div/div/div[3]/div/div/div[2]/div[2]/div[1]/div/div[2]/div/div/span[2]"
                }
            ]
            data["vesselInfo"] = []
            for vessel_field_set in vessel_info_xpaths:
                vessel_data = {}
                for field, xpath in vessel_field_set.items():
                    self.browser.wait_until_element_is_visible(xpath, timeout=10)
                    vessel_data[field] = self.browser.get_text(xpath)
                data["vesselInfo"].append(vessel_data)
            data = json.dumps(data, indent=4)
            log.info("Data extraction complete.")
        except Exception as e:
            log.error(f"Error extracting data: {e}")
            raise
        print("Data Extracted : ", data)
        return data

    def close_browser(self):
        """
        Closes the browser session.
        """
        try:
            self.browser.close_all_browsers()
            log.info("Browser closed successfully.")
        except Exception as e:
            log.error(f"Error closing the browser: {e}")        