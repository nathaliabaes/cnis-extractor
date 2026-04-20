import pdfplumber
import io
import re
from main import *

# Testa os 4 CNIS
for arquivo in ["cnis.pdf", "cnis2.pdf", "cnis3.pdf", "cnis4.pdf"]:
    print(f"\n{'='*40}")
    print(f"Arquivo: {arquivo}")
    print('='*40)
    
    with open(arquivo, "rb") as f:
        pdf_bytes = f.read()
    
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        texto = "\n".join(page.extract_text() for page in pdf.pages)
    
    beneficio = extrair_dados_beneficio(texto)
    
    print("Nome:", extrair_nome(texto))
    print("NIT:", extrair_nit(texto))
    print("CPF:", extrair_cpf(texto))
    print("Data nasc:", extrair_data_nascimento(texto))
    print("NB:", beneficio["nb"])
    print("Especie:", beneficio["especie"])
    print("Data inicio:", beneficio["data_inicio"])
    print("Data fim:", beneficio["data_fim"])
    print("Origem:", extrair_origem_vinculo(texto))

