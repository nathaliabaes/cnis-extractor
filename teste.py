import pdfplumber
import io
import re
from main import *

with open("cnis.pdf", "rb") as f:
    pdf_bytes = f.read()

with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
    texto = "\n".join(page.extract_text() for page in pdf.pages)

print("Nome:", extrair_nome(texto))
print("NIT:", extrair_nit(texto))
print("CPF:", extrair_cpf(texto))
print("Data nasc:", extrair_data_nascimento(texto))
print("NB:", extrair_nb(texto))
print("Especie:", extrair_especie(texto))
print("Data inicio:", extrair_data_inicio(texto))
print("Data fim:", extrair_data_fim(texto))

for linha in texto.split("\n"):
    if "Empregado" in linha or "Agente" in linha:
        print(repr(linha))

for linha in texto.split("\n"):
    if "Empregado" in linha or "Agente" in linha:
        print(repr(linha))
               