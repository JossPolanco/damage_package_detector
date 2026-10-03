import os
import io
from PIL import Image
from dotenv import load_dotenv

try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None

load_dotenv()

# La ruta a tu modelo entrenado localmente. 
# Se recomienda crear esta variable en .env o dejar el valor por defecto que coincide con tu entrenamiento.
MODEL_PATH = os.getenv("YOLO_MODEL_PATH", "runs/classify/train/weights/best.pt")

# Si el path no existe porque guardó con doble carpeta (runs/classify/runs/...), probamos el otro
if not os.path.exists(MODEL_PATH) and os.path.exists("runs/classify/runs/classify/train/weights/best.pt"):
    MODEL_PATH = "runs/classify/runs/classify/train/weights/best.pt"

model = None
if YOLO:
    try:
        model = YOLO(MODEL_PATH)
        print(f"Modelo YOLO cargado exitosamente desde {MODEL_PATH}")
    except Exception as e:
        print(f"Error cargando el modelo YOLO: {e}")

def detect_damage(image_bytes: bytes) -> dict:
    """
    Detects package damage using a locally trained YOLO model.
    """
    if model is None:
        print("WARN: Modelo YOLO no encontrado o Ultralytics no instalado. Usando Mock.")
        return {
            "is_damaged": True,
            "defects": ["mock_damage_model_missing"],
            "confidence": 0.95
        }

    try:
        # Convertimos la imagen recibida
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        # Inferencia
        results = model.predict(image, verbose=False)
        result = results[0]
        
        # Extraemos la clase con mayor probabilidad
        top_class_id = result.probs.top1
        confidence = float(result.probs.top1conf)
        predicted_class_name = result.names[top_class_id].lower()
        
        # Las clases reales de tu modelo son: 'damagedpackages' y 'undamagedpackages'
        is_damaged = predicted_class_name == "damagedpackages"
        
        return {
            "is_damaged": is_damaged,
            "defects": [predicted_class_name] if is_damaged else [],
            "confidence": round(confidence, 2)
        }
        
    except Exception as e:
        print(f"Error procesando la imagen con YOLO: {e}")
        return {
            "is_damaged": False,
            "defects": [],
            "error": str(e)
        }
