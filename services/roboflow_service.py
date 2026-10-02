import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY")
ROBOFLOW_MODEL_ENDPOINT = os.getenv("ROBOFLOW_MODEL_ENDPOINT", "mock_endpoint")

def detect_damage(image_bytes: bytes) -> dict:
    """
    Detects package damage using Roboflow Inference API.
    Uses a mock response if API key is not configured or in case of error.
    """
    if not ROBOFLOW_API_KEY or ROBOFLOW_API_KEY == "your_roboflow_api_key_here":
        # Mock Response
        return {
            "is_damaged": True,
            "defects": ["dented_box", "torn_label"],
            "confidence": 0.95
        }

    try:
        # Example API Call structure (adjust according to your specific Roboflow API)
        url = f"https://detect.roboflow.com/{ROBOFLOW_MODEL_ENDPOINT}?api_key={ROBOFLOW_API_KEY}"
        
        # headers = {"Content-Type": "application/x-www-form-urlencoded"}
        # response = requests.post(url, data=image_bytes, headers=headers)
        # response.raise_for_status()
        # data = response.json()
        
        # This is a placeholder parsing, adjust based on actual Roboflow response structure
        # return {
        #     "is_damaged": len(data.get("predictions", [])) > 0,
        #     "defects": [p["class"] for p in data.get("predictions", [])],
        #     "confidence": max([p["confidence"] for p in data.get("predictions", [])] + [0])
        # }
        
        # Fallback to mock for now since it's a stub
        return {
            "is_damaged": True,
            "defects": ["mock_damage_from_api"],
            "confidence": 0.88
        }
    except Exception as e:
        print(f"Error calling Roboflow API: {e}")
        return {
            "is_damaged": False,
            "defects": [],
            "error": str(e)
        }
