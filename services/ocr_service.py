import os
import requests
from dotenv import load_dotenv

load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

def extract_shipping_label(image_bytes: bytes) -> dict:
    """
    Extracts text from package label using a RapidAPI OCR service.
    Uses a mock response if API key is not configured or in case of error.
    """
    if not RAPIDAPI_KEY or RAPIDAPI_KEY == "your_rapidapi_key_here":
        print("WARN: Usando mock para OCR. Configura RAPIDAPI_KEY en .env")
        return {
            "success": True,
            "text": "TRACKING NO: 1Z9999999999999999\nDELIVER TO: 123 MAIN ST, CITY, ST 12345",
            "parsed_data": {
                "tracking_number": "1Z9999999999999999",
                "recipient_address": "123 MAIN ST, CITY, ST 12345"
            }
        }

    try:
        # Endpoint de ejemplo de RapidAPI (OCR Extract Text)
        # Nota: Ajusta la URL y el Host si eliges una API de OCR diferente en RapidAPI.
        url = "https://ocr-extract-text.p.rapidapi.com/ocr"
        
        headers = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": "ocr-extract-text.p.rapidapi.com"
        }
        
        files = {
            "image": ("image.jpg", image_bytes, "image/jpeg")
        }
        
        response = requests.post(url, files=files, headers=headers)
        
        # Manejo de error si la respuesta no es 200 OK
        if response.status_code != 200:
            return {
                "success": False,
                "text": "",
                "error": f"API Error {response.status_code}: {response.text}"
            }
            
        data = response.json()
        
        # Dependiendo del API específica de RapidAPI, la estructura de 'data' cambia.
        # Generalmente traen la llave 'text' o algo similar.
        extracted_text = data.get("text", "")
        
        return {
            "success": True,
            "text": extracted_text,
            "parsed_data": {} # Aquí podrías agregar Expresiones Regulares para extraer datos
        }

    except Exception as e:
        print(f"Error calling OCR API: {e}")
        return {
            "success": False,
            "text": "",
            "error": str(e)
        }
