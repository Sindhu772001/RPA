from fastapi import APIRouter, HTTPException
from app.api.schemas import ContainerTrackingRequest, ShippingContainerTracker

router = APIRouter()

@router.post("/track-container/")
async def track_container_endpoint(request: ContainerTrackingRequest):
    try:
        tracker = ShippingContainerTracker(container_number=request.container_number)
        tracking_methods = {
            "CMA": tracker.track_cma_container,
            "COSCO": tracker.track_cosu_container,
            "HAPAG LLOYD": tracker.track_hlc_container,
            "Maersk": tracker.track_maeu_container,
            "MSC": tracker.track_mscu_container
        }

        if request.website not in tracking_methods:
            raise HTTPException(status_code=400, detail="Unsupported shipping line.")

        result = tracking_methods[request.website](request)

        if not result:
            raise HTTPException(status_code=404, detail="No tracking data found for the container.")
        
        return result
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
