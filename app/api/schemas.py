from pydantic import BaseModel
from tracking_scripts.ocean import utils
from app.utils.logger import Logger
from RPA.Browser.Selenium import Selenium
from fastapi.responses import JSONResponse
import json
from tracking_scripts.ocean import CMDUContainerBuilder, COSUContainerBuilder,HLCUContainerBuilder,MAEUContainerBuilder,MSCUContainerBuilder

log = Logger(rotation_type='size').get_logger()

class ContainerTrackingRequest(BaseModel):
    website: str
    container_number: str



class ShippingContainerTracker:
    def __init__(self, container_number, browser=None, download_folder=None):
        self.container_number = container_number
        self.browser = browser or Selenium() 
        self.download_folder = download_folder
        self.shipping_line = None
        self.updates = []
        self.result = {}

    def track_cma_container(self, request: ContainerTrackingRequest, download_folder="/home/Sindhuja.Periyasamy/Downloads"):
        self.shipping_line = "CMA"
        cmdu_obj = CMDUContainerBuilder(browser=self.browser, download_folder=download_folder)
    
        try:
            cma_obj = cmdu_obj(self.container_number)
            
            if not cma_obj.open_tracking_page():
                log.error(f"Failed to open tracking page for container {self.container_number}.")
                return {"error": f"Tracking page not accessible for container {self.container_number}"}

            pdf_file = cma_obj.search_container_and_download_pdf(self.container_number)
            if not pdf_file:
                log.error(f"PDF not found for container {self.container_number}.")
                return {"error": f"PDF not found for container {self.container_number}"}

            container_details = cma_obj.extract_container_details(pdf_file)
            events = cma_obj.extract_pdf_events(pdf_file)

            self.result = {
                "container_details": container_details.get("container_details"),
                "eta": container_details.get("eta"),
                "events": events,
            }

            log.info("Final Result:")
            log.info(json.dumps(self.result, indent=4))

        except Exception as e:
            log.error(f"Error during CMA container tracking: {e}")
            self.result = {"error": str(e)}

        finally:
            cma_obj.close_browser()

        return self.result



    def track_cosu_container(self, request: ContainerTrackingRequest):
        self.container_number = request.container_number  
        self.shipping_line = "COSCO"
        separated = utils.validate_container_number(number=self.container_number, separate=True)
        searchable_number = separated[0] + "  " + separated[1]
        tracking_url = f"https://elines.coscoshipping.com/ebusiness/cargoTracking?trackingType=CONTAINER&number={self.container_number}"
        cosu_container_builder = COSUContainerBuilder()
        cosu_container = cosu_container_builder(self.container_number)
        updates = cosu_container.get_updates() 
        result = json.loads(updates) 
        return JSONResponse(content=result)


    def track_hlc_container(self, request: ContainerTrackingRequest):
        self.shipping_line = "HAPAG LLOYD"
        separated = utils.validate_container_number(number=self.container_number, separate=True)
        searchable_number = separated[0] + "  " + separated[1]
        tracking_url = f"https://www.hapag-lloyd.com/en/online-business/tracing/tracing-by-container.html?container={self.container_number}"
        hlcu_container_builder = HLCUContainerBuilder()
        hlcu_container = hlcu_container_builder(self.container_number)
        updates = hlcu_container.get_updates()
        result = json.loads(updates) 
        return JSONResponse(content=result)



    def track_maeu_container(self, request: ContainerTrackingRequest):
        self.shipping_line = "Maersk"
        maersk_obj_builder = MAEUContainerBuilder(browser=self.browser)
        maersk_obj = maersk_obj_builder(self.container_number)          
        container_details = maersk_obj.extract_data()
        result = json.loads(container_details) 
        return JSONResponse(content=result)



    def track_mscu_container(self, request: ContainerTrackingRequest):
        self.shipping_line = "MSC"
        msc_obj_builder = MSCUContainerBuilder(browser=self.browser)
        msc_obj = msc_obj_builder(self.container_number)
        try:
            msc_obj.open_tracking_page()
        except Exception as e:
            log.error(f"Error in opening tracking page for container {self.container_number}: {e}")
            return {"error": f"Tracking page not accessible for container {self.container_number}"}
        try:
            msc_obj.search_container(self.container_number)
        except Exception as e:
            log.error(f"Error in searching for container {self.container_number}: {e}")
            return {"error": f"Container not found for {self.container_number}"}

        container_details = msc_obj.extract_data_from_page()
        result = json.loads(container_details) 
        return JSONResponse(content=result)



