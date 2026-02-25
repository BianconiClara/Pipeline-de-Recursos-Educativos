from fpdf import FPDF
from PyPDF2 import PdfReader

def texto_a_pdf(texto: str, salida_pdf: str):#funcion para convertir texto a pdf
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for linea in texto.split("\n"):
        pdf.multi_cell(0, 8, linea)

    pdf.output(salida_pdf)

def pdf_a_texto(pdf_path: str) -> str:#funcion para convertir pdf a texto
    reader = PdfReader(pdf_path)
    texto = []

    for page in reader.pages:
        texto.append(page.extract_text() or "")

    return "\n".join(texto)
