import os
import torch
from ultralytics import YOLO

if __name__ == "__main__":
    dataset_path = os.path.abspath("dataset")
    print(f"--- Iniciando entrenamiento con dataset: {dataset_path} ---")

    # Detectar si hay GPU NVIDIA con CUDA disponible
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        device = 0
        print(f"🚀 [GPU DETECTADA]: Entrenando con {gpu_name} (device=0)")
    else:
        device = "cpu"
        print("⚠️ [CPU DETECTADA]: No se detectó CUDA/GPU activa en PyTorch. Se entrenará en CPU.")

    # 1. Cargar el modelo base preentrenado de clasificación
    model = YOLO("yolov8n-cls.pt")

    # 2. Entrenar el modelo con tu dataset
    results = model.train(
        data=dataset_path,
        epochs=10,
        imgsz=224,
        batch=16,
        workers=2,
        device=device,
        project="runs/classify",
        name="train",
        exist_ok=True
    )
 
    print("\n===========================================")
    print("¡Entrenamiento completado con éxito!")
    print("Tu modelo está guardado en: runs/classify/train/weights/best.pt")
    print("===========================================")

