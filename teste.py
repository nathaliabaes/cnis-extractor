import pdfplumber
import io
import re
import calendar
from main import *

with open("6. CNIS.pdf", "rb") as f:
    pdf_bytes = f.read()

with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
    texto = "\n".join(page.extract_text() for page in pdf.pages)

vinculos = extrair_vinculos(texto)
for v in vinculos:
    print(v)