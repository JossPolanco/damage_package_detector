import os
import requests
from dotenv import load_dotenv

load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

def extract_text_from_label(image_bytes: bytes) -> dict:
    """
    Extracts text from package label using a RapidAPI OCR service.
    Uses a mock response if API key is not configured or in case of error.
    """
    if not RAPIDAPI_KEY or RAPIDAPI_KEY == "your_rapidapi_key_here":
        # Mock Response
        return {
            "success": True,
            "text": "TRACKING NO: 1Z9999999999999999\nDELIVER TO: 123 MAIN ST, CITY, ST 12345",
            "parsed_data": {
                "tracking_number": "1Z9999999999999999",
                "recipient_address": "123 MAIN ST, CITY, ST 12345"
            }
        }

    try:
        # Example API Call structure for a generic RapidAPI OCR
        # You will need to replace the URL and Host with your specific chosen API
        url = "https://ocr-extract-text.p.rapidapi.com/ocr"
        
        headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": "ocr-extract-text.p.rapidapi.com"
            # Content-Type might vary depending on API
        }
        
        # files = {"image": ("image.jpg", image_bytes, "image/jpeg")}
        # response = requests.post(url, files=files, headers=headers)
        # response.raise_for_status()
        # data = response.json()
        
        # Return parsed data based on specific API response
        # return {
        #     "success": True,
        #     "text": data.get("text", ""),
        # }
        
        # Fallback to mock for now since it's a stub
        return {
            "success": True,
            "text": "MOCK TEXT FROM API CALL",
            "parsed_data": {}
        }

    except Exception as e:
        print(f"Error calling OCR API: {e}")
        return {
            "success": False,
            "text": "",
            "error": str(e)
        }
