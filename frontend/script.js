const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const loader = document.getElementById('loader');
const resultsPanel = document.getElementById('results');
const previewImg = document.getElementById('preview-img');
const statusBadge = document.getElementById('status-badge');
const actionText = document.getElementById('action-text');
const defectsText = document.getElementById('defects-text');
const trackingGroup = document.getElementById('tracking-group');
const trackingText = document.getElementById('tracking-text');
const downloadBtn = document.getElementById('download-pdf');
const resetBtn = document.getElementById('reset-btn');

let currentApiResult = null;
let currentImageUrl = null;

// Drag & Drop Listeners
dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) {
        handleFile(e.dataTransfer.files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
});

function handleFile(file) {
    if (!file.type.startsWith('image/')) {
        alert('Por favor, selecciona una imagen.');
        return;
    }

    // Mostrar preview
    currentImageUrl = URL.createObjectURL(file);
    previewImg.src = currentImageUrl;

    // Cambiar UI a loading
    dropZone.classList.add('hidden');
    resultsPanel.classList.add('hidden');
    loader.classList.remove('hidden');

    // Enviar a la API
    const formData = new FormData();
    formData.append('file', file);

    fetch('http://127.0.0.1:8000/api/v1/inspect-package', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        currentApiResult = data;
        displayResults(data);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Ocurrió un error al procesar el paquete. Verifica que el servidor esté corriendo.');
        resetUI();
    });
}

function displayResults(data) {
    loader.classList.add('hidden');
    resultsPanel.classList.remove('hidden');

    const isDamaged = data.package_status === "DAMAGED";
    
    // Status Badge
    statusBadge.textContent = isDamaged ? '❌ PAQUETE DAÑADO' : '✅ PAQUETE EN BUEN ESTADO';
    statusBadge.className = 'status-badge ' + (isDamaged ? 'status-damaged' : 'status-ok');

    // Action Text User Friendly
    let actionFriendly = data.logistics_action;
    if (data.logistics_action === "BLOCK_DELIVERY") {
        actionFriendly = "Bloquear Entrega y Devolver a Almacén 🛑";
    } else if (data.logistics_action === "PROCEED_TO_ROUTE") {
        actionFriendly = "Aprobado para Ruta de Entrega 🚚";
    }

    actionText.textContent = actionFriendly;
    actionText.style.color = isDamaged ? 'var(--danger)' : 'var(--success)';

    // Defects
    defectsText.textContent = data.detected_defects.length > 0 
        ? data.detected_defects.join(', ') 
        : 'Ninguno detectado';

    // Tracking Info (Hide if OK)
    if (!isDamaged) {
        trackingGroup.classList.add('hidden');
    } else {
        trackingGroup.classList.remove('hidden');
        const tracking = data.label_extracted_data?.tracking_number;
        trackingText.textContent = tracking ? tracking : 'No se pudo extraer la guía de rastreo';
    }
}

// Lógica del botón de analizar otro
resetBtn.addEventListener('click', () => {
    resetUI();
    // Limpiar input file para permitir subir el mismo archivo si se desea
    fileInput.value = '';
});

function resetUI() {
    loader.classList.add('hidden');
    resultsPanel.classList.add('hidden');
    dropZone.classList.remove('hidden');
}

// Generación de PDF usando jsPDF
downloadBtn.addEventListener('click', () => {
    if (!currentApiResult) return;

    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    const data = currentApiResult;
    const isDamaged = data.package_status === "DAMAGED";

    // Set document properties
    doc.setFont("helvetica");

    // Título
    doc.setFontSize(22);
    doc.setTextColor(40, 40, 40);
    doc.text("Reporte de Inspección Logística", 105, 20, null, null, "center");

    // Línea separadora
    doc.setLineWidth(0.5);
    doc.line(20, 25, 190, 25);

    // Información básica
    doc.setFontSize(12);
    doc.setTextColor(60, 60, 60);
    doc.text(`Fecha del Reporte: ${new Date(data.timestamp).toLocaleString()}`, 20, 40);
    doc.text(`Estado del Paquete: ${data.package_status === "DAMAGED" ? "DAÑADO" : "BUEN ESTADO"}`, 20, 50);
    
    let actionFriendly = data.logistics_action === "BLOCK_DELIVERY" ? "Bloquear Entrega y Devolver a Almacén" : "Aprobado para Ruta de Entrega";
    doc.text(`Acción Logística: ${actionFriendly}`, 20, 60);
    
    let currentY = 70;
    
    // Número de Guía solo si está dañado
    const tracking = data.label_extracted_data?.tracking_number || "Desconocido";
    if (isDamaged) {
        doc.setFont("helvetica", "bold");
        doc.text(`Número de Guía (Tracking): ${tracking}`, 20, currentY);
        doc.setFont("helvetica", "normal");
        currentY += 10;
    }

    // Defectos
    doc.text(`Defectos Detectados: ${data.detected_defects.length > 0 ? data.detected_defects.join(', ') : 'Ninguno'}`, 20, currentY);
    currentY += 15;

    // Texto extraído en bruto solo si está dañado
    if (isDamaged) {
        doc.text("Texto completo de la etiqueta OCR:", 20, currentY);
        currentY += 10;
        doc.setFontSize(10);
        doc.setTextColor(100, 100, 100);
        const rawText = data.label_extracted_data?.raw_text || "No hay texto disponible";
        const splitText = doc.splitTextToSize(rawText, 170);
        doc.text(splitText, 20, currentY);
    }

    // Agregar la Marca de Agua (Watermark)
    doc.setFontSize(60);
    doc.setFont("helvetica", "bold");
    
    if (isDamaged) {
        doc.setTextColor(255, 0, 0, 0.3); // Rojo con opacidad simulada
        // doc.text(text, x, y, options, transform, angle)
        doc.text("NO VALIDO", 105, 180, null, null, "center");
    } else {
        doc.setTextColor(0, 150, 0, 0.3); // Verde con opacidad
        doc.text("VALIDADO", 105, 180, null, null, "center");
    }

    // Agregar imagen al final si está disponible
    if (currentImageUrl) {
        try {
            // Convierte la imagen a un tamaño razonable en el PDF
            doc.addImage(previewImg, 'JPEG', 55, 200, 100, 75);
        } catch(e) {
            console.log("No se pudo insertar la imagen en el PDF", e);
        }
    }

    // Descargar
    doc.save(`Reporte_${tracking}.pdf`);
});
