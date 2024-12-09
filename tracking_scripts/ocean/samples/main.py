import os, sys, json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.logger import Logger
from cma_cgm import CMAContainerTracking
from msc import MSCContainerTracker
from test import MaerskContainerTracker
from RPA.Browser.Selenium import Selenium



log = Logger(rotation_type='size').get_logger()

def main():
    container_number = input("Enter the container number: ").strip()
    if not container_number:
        print("Container number is required. Exiting.")
        return

    print("Choose tracking system:")
    print("1: CMA-CGM")
    print("2: MSC")
    print("3: Maersk")
    choice = input("Enter your choice (1, 2, or 3): ").strip()

    browser = Selenium()
    tracker = None

    try:
        if choice == "1":
            download_folder = "/home/Sindhuja.Periyasamy/Downloads"
            if not download_folder:
                print("Download folder path is required for CMA-CGM. Exiting.")
                return
            tracker = CMAContainerTracking(browser, download_folder)
        elif choice == "2":
            tracker = MSCContainerTracker(browser)
        elif choice == "3":
            tracker = MaerskContainerTracker(browser)
        else:
            print("Invalid choice. Exiting.")
            return

        tracker.open_tracking_page(container_number)

        if isinstance(tracker, CMAContainerTracking):
            pdf_file = tracker.search_container_and_download_pdf(container_number)
            if pdf_file:
                container_details = tracker.extract_container_details(pdf_file)
                events = tracker.extract_pdf_events(pdf_file)

                result = {
                    "container_details": container_details.get("container_details"),
                    "eta": container_details.get("eta"),
                    "events": events
                }

                log.info("Final Result:")
                log.info(json.dumps(result, indent=4))
                print("CMA tracking process completed successfully.")
        elif isinstance(tracker, MSCContainerTracker):
            result = tracker.search_container(container_number)
            if result:
                print("MSC tracking process completed successfully.")
                print(result)
        elif isinstance(tracker, MaerskContainerTracker):
            result = tracker.extract_data_from_page()
            if result:
                print("Maersk tracking process completed successfully.")
                log.info("Final Result:")
                log.info(json.dumps(result, indent=4))
                print(result)

    except Exception as e:
        log.error(f"An error occurred: {e}")
    finally:
        browser.close_all_browsers()
        log.info("Browser session closed.")

if __name__ == "__main__":
    main()
