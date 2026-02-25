import os
import time
import requests
import logging

logger = logging.getLogger(__name__)

# ==============================
# Configuración
# ==============================

PICTORY_API_KEY = os.getenv("PICTORY_API_KEY")
USE_MOCK = os.getenv("USE_MOCK_APIS", "false").lower() == "true"

BASE_URL = "https://api.pictory.ai/v1"

HEADERS = {
    "Authorization": f"Bearer {PICTORY_API_KEY}",
    "Content-Type": "application/json"
}

# ==============================
# API pública
# ==============================

def crear_video_desde_texto(
    texto: str,
    timeout: int = 600
) -> str:
    """
    Crea un video en Pictory a partir de texto.
    Devuelve una URL (real) o un identificador mock.
    """

    # -------- MOCK --------
    if USE_MOCK:
        logger.info("[MOCK] Pictory: creando video simulado")
        time.sleep(2)
        return "mock://video_pictory"

    # -------- REAL --------
    if not PICTORY_API_KEY:
        raise RuntimeError("PICTORY_API_KEY no configurada")
   

    payload = {
        "videoName": "Video educativo automático",
        "videoType": "script",
        "script": texto,
        "aspectRatio": "16:9",
        "language": "es",
        "voiceOver": {
            "enabled": True,
            "voice": "es-ES-AlvaroNeural"
        },
        "autoHighlights": True,
        "autoBranding": True
    }

    logger.info("Creando video en Pictory...")
    r = requests.post(
        f"{BASE_URL}/video/create",
        headers=HEADERS,
        json=payload,
        timeout=30
    )
    r.raise_for_status()

    job_id = r.json()["jobId"]
    logger.info("Job Pictory creado: %s", job_id)

    return _esperar_video(job_id, timeout)


def descargar_video(url: str, destino: str):
    """
    Descarga el MP4 final desde Pictory (real o mock)
    """

    # -------- MOCK --------
    if USE_MOCK:
        logger.info("[MOCK] Pictory: generando archivo MP4 falso")

        # Archivo dummy válido para el pipeline
        with open(destino, "wb") as f:
            f.write(b"FAKE MP4 CONTENT - PICTORY MOCK")

        return

    # -------- REAL --------
    if not PICTORY_API_KEY:
        raise RuntimeError("PICTORY_API_KEY no configurada")

    logger.info("Descargando video final desde Pictory...")
    r = requests.get(url, stream=True, timeout=60)
    r.raise_for_status()

    with open(destino, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)

    logger.info("Video guardado en %s", destino)


# ==============================
# Funciones internas
# ==============================

def _esperar_video(job_id: str, timeout: int) -> str:
    inicio = time.time()

    while True:
        r = requests.get(
            f"{BASE_URL}/video/status/{job_id}",
            headers=HEADERS,
            timeout=30
        )
        r.raise_for_status()

        data = r.json()
        estado = data.get("status")

        if estado == "completed":
            return data["videoUrl"]

        if estado == "failed":
            raise RuntimeError(f"Error en Pictory: {data}")

        if time.time() - inicio > timeout:
            raise TimeoutError("Timeout esperando video de Pictory")

        time.sleep(10)
