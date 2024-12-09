from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from RPA.Browser.Selenium import Selenium
from tracking_scripts import ocean

app = FastAPI()

class ShipmentRequest(BaseModel):
    container: str
    scac: str

@app.post("/create-shipment/")
def create_shipment(request: ShipmentRequest):
    try:
        
        browser = Selenium()
        shipment = ocean.container.create(scac=request.scac, cn=request.container, browser=browser)
        shipment.close_browser()
        
        return {"message": "Shipment created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# container = "244520305"
# scac = "MAEU" 

# container = "TRHU6639739"
# scac = "CMDU" 

# container = "TGBU4966739"
# scac = "COSU" 

# container = "HLBU 9461570"
# scac = "HLCU" 

# container = "MSMU1000552"
# scac = "MSCU" 


# MSNU3082912