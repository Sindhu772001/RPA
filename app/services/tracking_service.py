from app.api.schemas import ContainerTrackingRequest
from app.api.schemas import ShippingContainerTracker

async def track_container(request: ContainerTrackingRequest):
    try:
        website = request.website.strip()
        container_number = request.container_number.strip()

        if not website or not container_number:
            raise ValueError("Both website and container number are required.")

        supported_websites = ["CMA", "COSCO", "HAPAG LLOYD", "Maersk", "MSC"]

        if website.upper() not in supported_websites:
            raise ValueError(f"Unsupported website: {website}. Supported websites are: {', '.join(supported_websites)}.")

        return {"message": "Validation successful", "data": {"website": website, "container_number": container_number}}

    except Exception as e:
        return {"message": "Error occurred", "error": str(e)}
