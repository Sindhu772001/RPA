from fastapi import FastAPI, HTTPException
from app.api.routes import router
from app.core.config import settings
from app.api.schemas import ContainerTrackingRequest
from app.services.tracking_service import track_container

app = FastAPI()

# app.include_router(router, prefix="/api")
app.include_router(router)

@app.post("/track-container/")
async def track_container_endpoint(request: ContainerTrackingRequest):
    try:
        tracking_data = await track_container(request)

        if not tracking_data:
            raise HTTPException(status_code=404, detail="No tracking data found.")
        
        return {"success": True, "data": tracking_data}

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
