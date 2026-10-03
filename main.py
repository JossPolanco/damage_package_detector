from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import traceback

from services.roboflow_service import detect_damage
from services.ocr_service import extract_shipping_label

app = FastAPI(title="Logistics Package Inspection API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {
        "status": "online",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/v1/inspect-package")
async def inspect_package(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")

    try:
        image_bytes = await file.read()
        
        # 1. Detect damage using Roboflow/YOLO
        damage_result = detect_damage(image_bytes)
        is_damaged = damage_result.get("is_damaged", False)
        detected_defects = damage_result.get("defects", [])
        
        if is_damaged:
            package_status = "DAMAGED"
            logistics_action = "BLOCK_DELIVERY"
        else:
            package_status = "OK"
            logistics_action = "PROCEED_TO_ROUTE"
            
        label_extracted_data = {}
        
        # 2. Call OCR to read the label regardless of package status
        ocr_result = extract_shipping_label(image_bytes)
        if ocr_result.get("success"):
            label_extracted_data = ocr_result.get("parsed_data", {})
            label_extracted_data["raw_text"] = ocr_result.get("text", "")
        else:
            label_extracted_data = {"error": "OCR failed or unavailable"}
        
        # 3. Construct and return response
        response_data = {
            "package_status": package_status,
            "detected_defects": detected_defects,
            "label_extracted_data": label_extracted_data,
            "logistics_action": logistics_action,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return response_data

    except Exception as e:
        print(f"Error processing image: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error processing the image.")
