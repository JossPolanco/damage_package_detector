# Logistics Package Inspection System

API FastAPI para la inspección de paquetes logísticos, integrando Roboflow (detección de daños) y RapidAPI OCR (lectura de guías).

## Estructura del Proyecto

- `main.py`: Archivo principal con la aplicación FastAPI y los endpoints.
- `services/roboflow_service.py`: Módulo para la integración con el modelo de visión por computadora de Roboflow.
- `services/ocr_service.py`: Módulo para la integración con el servicio OCR de RapidAPI.
- `.env.example`: Plantilla para las variables de entorno.
- `requirements.txt`: Dependencias del proyecto.

## Requisitos Previos

- Python 3.8+

## Instalación y Ejecución

Sigue estos pasos para inicializar el proyecto en tu máquina local:

1. **Crear un entorno virtual:**
   ```bash
   python -m venv venv
   ```

2. **Activar el entorno virtual:**
   - En Windows (Command Prompt o PowerShell):
     ```powershell
     .\venv\Scripts\activate
     ```
   - En Linux/macOS:
     ```bash
     source venv/bin/activate
     ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno:**
   Copia el archivo `.env.example` a un nuevo archivo llamado `.env` y coloca tus API Keys de Roboflow y RapidAPI (si no las tienes aún, la aplicación usará mocks preconfigurados por defecto que simulan un paquete dañado).
   ```bash
   cp .env.example .env
   ```

5. **Ejecutar el servidor en modo desarrollo:**
   ```bash
   uvicorn main:app --reload
   ```

## Uso de la API

Una vez ejecutado el servidor (por defecto en `http://127.0.0.1:8000`), puedes:
- Verificar el estado de la API en el endpoint `GET /`
- Subir una imagen al endpoint `POST /api/v1/inspect-package` mediante form-data con el campo `file`.
- Ver la documentación interactiva Swagger UI en [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

Ejemplo de llamada cURL:
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/api/v1/inspect-package' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@ruta_a_tu_imagen.jpg'
```
