# Pipeline-de-Recursos-Educativos
Es un pipeline para la elaboración de recursos educativos para el ámbito de clases a distancia. Este es solo un modelo; no posee las keys necesarias para su implementación. 
## Pipeline en Python que permite:

- Editar videos (ffmpeg)
- Transcribir audio/video con Whisper
- Convertir transcripción en PDF
- Crear un video a partir del texto (Pictory API)
- Crear una presentación PPTX desde texto (ppt.ai API)
  
## Funcionalidades

- Video → edición + transcripción
- PDF → generación de video + presentación
- Integración con APIs externas (opcional)
- Pipeline automatizada

## Entradas y Salidas
### PDF
En el caso de que la entrada sea un PDF, pasar por una determinada pipeline cuya salida es la siguiente:
- Video creado con el contenido de la entrada
- Presentación creado con el contenido de entrada
### MP4
En el caso de que la entrada sea un video, pasar por una determinada pipeline cuya salida es la siguiente:
- Video editado
- Transcripción del video en PDF
- Video en base al PDF de transcripción
## Esquema
![Esquema del Pipeline](img/PIPELINE.png)

## Requisitos

- Python 3.10+
- ffmpeg instalado
- API Keys (opcional):
  - PICTORY_API_KEY
  - PPT_AI_API_KEY

