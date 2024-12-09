import time
import random
import os, sys
import json
from datetime import datetime
from RPA.Browser.Selenium import Selenium
import camelot
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.utils.logger import Logger
from .base import ShippingContainer

log = Logger(rotation_type='size').get_logger()

class CMDUContainerBuilder(object):
    def __init__(self, browser, download_folder):
        """
        Initializes the builder with the shared browser instance and download folder.
        Args:
            browser (Selenium): Shared Selenium browser instance.
            download_folder (str): Path to the folder where downloads are stored.
        """
        if browser is None:
            self.browser = Selenium()
        else:
            self.browser = browser
        self.download_folder = download_folder

    def __call__(self, container, **_ignored):
        """
        Creates and returns a CMAContainer instance.
        Args:
            container (str): The container number.
        """
        self._instance = CMAContainer(container, self.browser, self.download_folder)
        return self._instance


class CMAContainer(ShippingContainer):
    def __init__(self, container_number, browser, download_folder):
        """
        Initializes the CMA container with the container number, browser, and download folder.
        Args:
            container_number (str): The CMA container number.
            browser (Selenium): The browser instance used for tracking.
            download_folder (str): Path to the folder where downloads are stored.
        """
        super().__init__(cn=container_number)
        self.shipping_line = "CMA"
        self.browser = browser if browser else Selenium() 
        self.download_folder = download_folder

    def random_sleep(self, min_time, max_time):
        """Pause the execution for a random time between min_time and max_time."""
        sleep_time = random.uniform(min_time, max_time)
        time.sleep(sleep_time)
        return sleep_time

    def open_tracking_page(self):
        """Open the tracking page and handle cookies."""
        try:
            if not self.browser:
                log.error("Browser instance is None.")
                raise ValueError("Browser is not initialized.")
            
            log.info("Opening tracking page...")
            self.browser.open_available_browser(
                "https://www.cma-cgm.com/ebusiness/tracking",
                options={"arguments": ["--start-maximized", "--disable-blink-features=AutomationControlled"]}
            )
            self.random_sleep(3, 5)
            self.handle_cookies()
            log.info("Tracking page opened successfully.")
            return True  
        except Exception as e:
            log.error(f"Error opening tracking page: {e}")
            return False 

    def handle_cookies(self):
        """Handle cookie pop-ups on the webpage."""
        try:
            log.info("Handling cookies...")
            cookie_xpaths = [
                "//button[contains(text(),'Accept All')]",
                "//button[contains(text(),'Accept Cookies')]",
                "//button[contains(text(),'I Accept')]",
                "//button[contains(@aria-label, 'Accept cookies')]"
            ]
            for xpath in cookie_xpaths:
                if self.browser.does_page_contain_element(xpath):
                    self.browser.click_element(xpath)
                    log.info("Cookies accepted.")
                    return
            log.info("No cookies pop-up found.")
        except Exception as e:
            log.error(f"Error handling cookies: {e}")
            raise

    def search_container_and_download_pdf(self, container_number, wait_time=30):
        """Search for the container and download the PDF."""
        try:
            log.info(f"Searching for container {container_number}...")
            input_xpath = '//*[@id="Reference"]'
            export_pdf_button_xpath = "//*[@id='top-details-0']/div/div/div[2]"

            self.browser.wait_until_element_is_visible(input_xpath, timeout=10)
            self.browser.input_text(input_xpath, container_number)
            self.random_sleep(2, 4)
            self.browser.press_keys(input_xpath, 'ENTER')
            self.random_sleep(3, 5)
            self.browser.wait_until_element_is_visible(export_pdf_button_xpath, timeout=15)
            self.browser.click_element(export_pdf_button_xpath)
            log.info("Downloading PDF...")
            time.sleep(wait_time)
            pdf_file = self.get_latest_downloaded_file()
            log.info(f"PDF downloaded: {pdf_file}")
            return pdf_file
        except Exception as e:
            log.error(f"Error searching for container {container_number} or downloading PDF: {e}")
            return None

    def get_latest_downloaded_file(self):
        """Get the most recently downloaded PDF file."""
        try:
            log.info("Fetching the latest downloaded PDF...")
            files = [os.path.join(self.download_folder, f) for f in os.listdir(self.download_folder) if f.endswith(".pdf")]
            if not files:
                raise FileNotFoundError("No PDF files found in the Downloads folder.")
            latest_file = max(files, key=os.path.getctime)
            log.info(f"Latest file found: {latest_file}")
            return latest_file
        except Exception as e:
            log.error(f"Error fetching the latest downloaded PDF: {e}")
            raise

    def extract_pdf_events(self, pdf_file):
        """Extract events from the PDF file."""
        try:
            log.info(f"Extracting events from PDF: {pdf_file}")
            tables = camelot.read_pdf(pdf_file, pages="1", flavor="stream")
            events_data = []

            if not tables:
                log.warning("No tables found in the PDF.")
                return []

            for table in tables:
                df = table.df
                filtered_columns = df.iloc[:, 2:7].dropna(how="all")
                filtered_columns = filtered_columns.loc[~filtered_columns.apply(lambda row: (row == '').all(), axis=1)]
                filtered_columns = filtered_columns.applymap(lambda x: x if x != '' else None).dropna(axis=1, how='all')

                for index, row in filtered_columns.iterrows():
                    processed_row = []
                    for value in row.dropna().values:
                        if '\n' in value:
                            before_newline, after_newline = value.split('\n', 1)
                            processed_row.append(before_newline)
                            processed_row.append(after_newline)
                        else:
                            processed_row.append(value)
                    events_data.append(processed_row)

            events_data = events_data[1:]
            merged_data = []
            for i in range(len(events_data)):
                current_row = events_data[i]
                if len(current_row) == 1 or len(current_row) == 2:
                    merged_data[-1].extend(current_row)
                else:
                    merged_data.append(current_row)

            keys = ['date', 'time', 'event', 'location']
            result = []

            for item in merged_data:
                json_obj = {key: "" for key in keys}
                for i, value in enumerate(item):
                    if i < len(keys):
                        json_obj[keys[i]] = value
                result.append(json_obj)

            log.info("Events extracted successfully.")
            return result
        except Exception as e:
            log.error(f"Error extracting events from PDF: {e}")
            raise

    def extract_container_details(self, pdf_file):
        """Extract container details from the PDF file."""
        try:
            log.info(f"Extracting container details from PDF: {pdf_file}")
            tables = camelot.read_pdf(pdf_file, pages="1", flavor="stream")

            if not tables:
                log.warning("No tables found in the PDF.")
                return {
                    "container_details": [],
                }

            df = tables[0].df.dropna(how="all").reset_index(drop=True)
            log.debug("Extracted DataFrame:")
            log.debug(df)

            filtered_data = df.iloc[:, :2].dropna(how="all")
            result = []

            for index, row in filtered_data.iterrows():
                row_values = [str(value).strip() for value in row if value and str(value).strip()]
                result.extend(row_values)

            exclude_words = [
                "RECEIPT", "CONTAINER", "TERMINAL", "DELIVERY", 
                "Booking reference", "Custom reference", "Exported on"
            ]

            filtered_data = [item for item in result if item not in exclude_words]

            log.info("Filtered container details successfully.")
            container_details = {
                "containerNumber": filtered_data[0] if len(filtered_data) > 0 else "",
                "containerType": filtered_data[1] if len(filtered_data) > 1 else "",
                "pol": filtered_data[2].replace("\n", " ").strip() if len(filtered_data) > 2 else "",
                "pod": filtered_data[4].replace("\n", " ").strip() if len(filtered_data) > 4 else "",
                "terminal": filtered_data[5] if len(filtered_data) > 5 else "",
                "bookingReference": filtered_data[6] if len(filtered_data) > 6 else "",
                "customReference": filtered_data[7] if len(filtered_data) > 7 else "",
                "status": filtered_data[8] if len(filtered_data) > 8 else ""
            }

            eta = {
                "date": filtered_data[10] if len(filtered_data) > 10 else "",
                "time": filtered_data[11] if len(filtered_data) > 11 else ""
            }

            final_data = {
                "container_details": container_details,
                "eta": eta
            }

            log.info("Container details extracted successfully.")
            return final_data
        except Exception as e:
            log.error(f"Error extracting container details from PDF: {e}")
            raise

    def close_browser(self):
        """
        Closes the browser session.
        """
        try:
            self.browser.close_all_browsers()
            log.info("Browser closed successfully.")
        except Exception as e:
            log.error(f"Error closing the browser: {e}")        