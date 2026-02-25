import os
import subprocess
import whisper
import logging


from pictory_client import crear_video_desde_texto, descargar_video
from ppt_ai_client import crear_presentacion_desde_texto
from pdf_utils import texto_a_pdf, pdf_a_texto

#condicionales de API keys
PICTORY_API_KEY = os.getenv("PICTORY_API_KEY")
PPT_AI_API_KEY = os.getenv("PPT_AI_API_KEY")

HAY_PICTORY = bool(PICTORY_API_KEY)
HAY_PPT_AI = bool(PPT_AI_API_KEY)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
MOCK_EXTERNAL_APIS = True

# =============================
# RUTAS
# =============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTADOS = os.path.join(BASE_DIR, "resultados")
os.makedirs(RESULTADOS, exist_ok=True)

VIDEO_EDITADO = os.path.join(RESULTADOS, "video_editado.mp4")
VIDEO_PICTORY = os.path.join(RESULTADOS, "video_pictory.mp4")
TRANSCRIPCION_PDF = os.path.join(RESULTADOS, "transcripcion.pdf")
PRESENTACION = os.path.join(RESULTADOS, "presentacion.pptx")

# =============================
# MODELO WHISPER
# =============================
MODEL = whisper.load_model("small")

# =============================
# HELPERS DE TIPO DE ARCHIVO
# =============================
def es_video(path: str) -> bool:
    return path.lower().endswith((".mp4", ".mov", ".avi", ".mkv"))

def es_pdf(path: str) -> bool:
    return path.lower().endswith(".pdf")

# =============================
# FUNCIONES BASE
# =============================
def editar_video(entrada: str, salida: str):
    """
    Ejemplo simple de edición usando ffmpeg
    """
    logger.info("Editando video...")
    subprocess.run([
        "ffmpeg", "-y",
        "-i", entrada,
        "-vf", "scale=1280:720",
        salida
    ], check=True)

def transcribir_video(video_path: str) -> str:
    logger.info("Transcribiendo video...")
    result = MODEL.transcribe(video_path)
    return result["text"]

# =============================
# PIPELINE VIDEO
# =============================
def pipeline_video(video_path: str):
    logger.info("Entrada detectada: VIDEO")

    resultados = {}

    # 1. Editar video
    editar_video(video_path, VIDEO_EDITADO)
    resultados["video_editado"] = VIDEO_EDITADO

    # 2. Transcribir
    texto = transcribir_video(VIDEO_EDITADO)

    # 3. Crear PDF de la transcripción
    texto_a_pdf(texto, TRANSCRIPCION_PDF)
    resultados["pdf_transcripcion"] = TRANSCRIPCION_PDF

    # 4. Video externo SOLO si NO hay API key
    if HAY_PICTORY:
        logger.info("API de Pictory detectada → ejecutando Pictory")
        video_url = crear_video_desde_texto(texto)
        descargar_video(video_url, VIDEO_PICTORY)
        resultados["video_pictory"] = VIDEO_PICTORY
    else:
        logger.info("No hay API de Pictory → se omite creación de video")
        resultados["video_pictory"] = None


    # 5. Presentación 
    if HAY_PPT_AI:
        crear_presentacion_desde_texto(texto, PRESENTACION)
        resultados["presentacion"] = PRESENTACION
    else:
        logger.info("No hay API de ppt.ai → se omite presentación")
        resultados["presentacion"] = None
        
    resultados["video_pictory"] = "video_pictory.mp4"
    resultados["video_editado"] = "video_editado.mp4"
    resultados["pdf_transcripcion"] = "transcripcion.pdf"
    resultados["presentacion"] = "presentacion.pptx"


    return resultados

# =============================
# PIPELINE PDF
# =============================
def pipeline_pdf(pdf_path: str):
    logger.info("Entrada detectada: PDF")

    texto = pdf_a_texto(pdf_path)

    resultados = {
        "pdf_entrada": os.path.abspath(pdf_path)
    }

    

    if PICTORY_API_KEY:
        logger.info("PICTORY_API_KEY detectada → ejecutando Pictory")
        video_url = crear_video_desde_texto(texto)
        descargar_video(video_url, VIDEO_PICTORY)
        resultados["video_pictory"] = VIDEO_PICTORY
    else:
        logger.warning("PICTORY_API_KEY no configurada → se omite Pictory")
        resultados["video_pictory"] = None
   
   
    if PPT_AI_API_KEY:
        logger.info("PPT_AI_API_KEY detectada → ejecutando ppt.ai")
        crear_presentacion_desde_texto(texto, PRESENTACION)
        resultados["presentacion"] = PRESENTACION
    else:
        logger.warning("PICTORY_API_KEY no configurada → se omite Pictory")
        resultados["presentacion"] = None

   
    resultados["video_pictory"] = "video_pictory.mp4"
    resultados["presentacion"] = "presentacion.pptx"
   
    return resultados

# =============================
# ENTRYPOINT
# =============================
def ejecutar_pipeline(entrada: str):
    if es_video(entrada):
        return pipeline_video(entrada)

    if es_pdf(entrada):
        return pipeline_pdf(entrada)

    raise ValueError("Formato de entrada no soportado")
