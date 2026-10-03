import os
import io
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY")
ROBOFLOW_WORKSPACE_NAME = os.getenv("ROBOFLOW_WORKSPACE_NAME", "josue-angel-perez-polanco")
ROBOFLOW_WORKFLOW_ID = os.getenv("ROBOFLOW_WORKFLOW_ID", "damaged-box-detection-a77lo")

def get_client():
    if not ROBOFLOW_API_KEY or ROBOFLOW_API_KEY in ["your_roboflow_api_key_here", ""]:
        return None
    try:
        from inference_sdk import InferenceHTTPClient, InferenceConfiguration
        client = InferenceHTTPClient(
            api_url="https://serverless.roboflow.com",
            api_key=ROBOFLOW_API_KEY
        ).configure(InferenceConfiguration(
            api_key_transport="header"
        ))
        return client
    except Exception as e:
        print(f"Error initializing InferenceHTTPClient: {e}")
        return None

def extract_predictions_from_workflow_result(result) -> list:
    """
    Recursively extracts all detection predictions from a Roboflow workflow response.
    """
    predictions = []

    def _search(obj):
        if isinstance(obj, dict):
            # Check if this dictionary represents a detection prediction
            if "class" in obj or "class_name" in obj:
                predictions.append(obj)
                return
            for v in obj.values():
                _search(v)
        elif isinstance(obj, list):
            for item in obj:
                _search(item)

    _search(result)
    return predictions

def detect_damage(image_bytes: bytes) -> dict:
    """
    Detects package damage using Roboflow Workflow Inference.
    Falls back to mock if API key is not configured or in case of error.
    """
    client = get_client()
    if not client:
        # Fallback Mock
        return {
            "is_damaged": True,
            "defects": ["dented_box", "torn_label"],
            "confidence": 0.95,
            "predictions": []
        }

    try:
        # Load image with PIL and convert to RGB
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # Run Roboflow Workflow
        result = client.run_workflow(
            workspace_name=ROBOFLOW_WORKSPACE_NAME,
            workflow_id=ROBOFLOW_WORKFLOW_ID,
            images={"image": image},
            use_cache=True
        )

        print(f"[ROBOFLOW DEBUG] Raw workflow result: {result}")

        # Check if result is empty
        if not result or result == [{}] or result == {}:
            print("[ROBOFLOW WARNING] Workflow returned empty response [{}]! Check if a model version is trained.")

        defects = []
        confidences = []
        is_damaged = False

        # Support 1: Classification models (top class)
        # Often returns: {"top": "damagedpackages", "confidence": 0.95} or {"predictions": [...]}
        def check_classification_dict(d):
            nonlocal is_damaged
            top_class = str(d.get("top") or d.get("prediction") or d.get("class") or "").lower()
            conf = float(d.get("confidence") or 0.0)
            if top_class:
                if any(kw in top_class for kw in ["damage", "defect", "broken", "tear", "crush", "hole"]):
                    is_damaged = True
                    defects.append(top_class)
                    confidences.append(conf)

        if isinstance(result, list):
            for item in result:
                if isinstance(item, dict):
                    check_classification_dict(item)
                    for k, v in item.items():
                        if isinstance(v, dict):
                            check_classification_dict(v)
        elif isinstance(result, dict):
            check_classification_dict(result)

        # Support 2: Object Detection bounding boxes
        predictions = extract_predictions_from_workflow_result(result)
        for p in predictions:
            cls_name = str(p.get("class") or p.get("class_name") or "").lower()
            conf = float(p.get("confidence") or 0.0)
            if cls_name:
                # If class contains damage/defect, or in binary classification if damagedpackages
                if any(kw in cls_name for kw in ["damage", "defect", "broken", "tear", "crush", "hole", "dent"]):
                    is_damaged = True
                    defects.append(cls_name)
                    confidences.append(conf)
                elif "undamaged" not in cls_name and "ok" not in cls_name:
                    # Generic defect class
                    is_damaged = True
                    defects.append(cls_name)
                    confidences.append(conf)

        top_confidence = max(confidences) if confidences else (0.90 if is_damaged else 0.0)

        return {
            "is_damaged": is_damaged,
            "defects": list(set(defects)),
            "confidence": round(float(top_confidence), 2),
            "predictions": predictions,
            "raw_result": result
        }

    except Exception as e:
        print(f"Error calling Roboflow workflow: {e}")
        return {
            "is_damaged": False,
            "defects": [],
            "confidence": 0.0,
            "error": str(e)
        }
