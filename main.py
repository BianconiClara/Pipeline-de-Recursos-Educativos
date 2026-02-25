from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import shutil
import os

from pipeline import ejecutar_pipeline


app = FastAPI()

# Archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")





# Templates HTML
templates = Jinja2Templates(directory="templates")

# -------------------------
# Middleware
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en producción: restringir
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Directorios
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
RESULTADOS_DIR = os.path.join(BASE_DIR, "resultados")

os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(RESULTADOS_DIR, exist_ok=True)

# -------------------------
# Templates (HTML)
# -------------------------
templates = Jinja2Templates(directory="templates")

# -------------------------
# Archivos estáticos (resultados)
# -------------------------
app.mount(
    "/resultados",
    StaticFiles(directory=RESULTADOS_DIR),
    name="resultados"
)

# -------------------------
# Rutas
# -------------------------

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    """
    Página principal con el formulario
    """
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


@app.post("/upload")
async def subir_archivo(file: UploadFile = File(...)):
    """
    Recibe PDF o video, ejecuta el pipeline
    y devuelve los archivos generados
    """
    nombre = file.filename
    extension = nombre.split(".")[-1].lower()

    if extension not in ["mp4", "mov", "avi", "mkv", "pdf"]:
        raise HTTPException(status_code=400, detail="Formato no soportado")

    ruta_archivo = os.path.join(UPLOADS_DIR, nombre)

    # Guardar archivo subido
    with open(ruta_archivo, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        resultados = ejecutar_pipeline(ruta_archivo)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return JSONResponse({
        "status": "ok",
        "resultados": resultados
    })
