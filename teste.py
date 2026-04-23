import pdfplumber
import io
import re
from main import *

for arquivo in ["cnis.pdf", "cnis2.pdf", "cnis3.pdf", "cnis4.pdf"]:
    print(f"\n{'='*40}")
    print(f"Arquivo: {arquivo}")
    print('='*40)
    
    with open(arquivo, "rb") as f:
        pdf_bytes = f.read()
    
    resultado = extrair_dados_cnis(pdf_bytes)
    print(resultado)