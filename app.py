import streamlit as st
import time
import random
from PIL import Image

def check_package_damage(image):
    """
    Simula la detección de daños en el paquete.
    # AQUÍ VA EL REQUEST A ROBOFLOW
    """
    time.sleep(1.5)  # Simulando la latencia de red
    return random.choice(["ok", "damaged"])

def extract_label_ocr(image):
    """
    Simula la extracción de texto (OCR) de la etiqueta de envío.
    # AQUÍ VA EL REQUEST A RAPIDAPI
    """
    time.sleep(1.0)  # Simulando la latencia de red
    tracking_numbers = ["1Z9999999999999999", "JD000222333444555", "TBA123456789000"]
    return random.choice(tracking_numbers)

def main():
    st.set_page_config(page_title="Escáner Logístico", page_icon="📦", layout="wide")

    # Interfaz Principal
    st.title("📦 Escáner de Triage Logístico")
    st.markdown("Sistema inteligente para la detección automática de daños en paquetes y la extracción rápida de los datos de la etiqueta de envío mediante visión computacional.")
    
    st.divider()

    # Opciones para cargar la imagen
    input_col1, input_col2 = st.columns(2)
    
    with input_col1:
        uploaded_file = st.file_uploader("Arrastra o selecciona una imagen del paquete", type=["jpg", "jpeg", "png"])
        
    with input_col2:
        camera_picture = st.camera_input("O toma una foto directamente con la cámara")

    # Lógica y Estados de Carga
    image_data = uploaded_file if uploaded_file else camera_picture

    if image_data:
        st.divider()
        
        # Columnas para mostrar la imagen y los resultados
        res_col1, res_col2 = st.columns([1, 1])
        
        with res_col1:
            st.image(image_data, caption="Imagen del paquete bajo revisión", use_container_width=True)
            
        with res_col2:
            st.subheader("Resultados de Inspección")
            
            with st.spinner('Analizando integridad del paquete y leyendo etiqueta de envío...'):
                # Simulamos la lectura de la imagen (usualmente convertiríamos a bytes o base64 para la API)
                img = Image.open(image_data)
                
                # Invocamos las funciones mock
                status = check_package_damage(img)
                ocr_data = extract_label_ocr(img)
                
            # Renderizado Condicional de Resultados
            if status == "ok":
                st.success("✅ PAQUETE ÓPTIMO PARA ENVÍO. Listo para ruta.")
            else:
                st.error("🚨 ALERTA: PAQUETE DAÑADO. Detener envío.")
                # Sección destacada si el paquete está dañado
                st.warning(f"**Datos de etiqueta extraídos:** Tracking `{ocr_data}`")

if __name__ == "__main__":
    main()
