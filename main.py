import pdfplumber
import io
import re

def extrair_texto(pdf_bytes):
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        texto = "\n".join(page.extract_text() for page in pdf.pages)
    return texto  

def extrair_nome(texto):
    resultado = re.search(r"Nome:\s+([A-ZÀ-Ú ]+)", texto)
    if resultado:
        return resultado.group(1).strip().title()
    return None

def extrair_nit(texto):
    resultado = re.search(r"NIT:\s+([\d.\-]+)", texto)
    if resultado:
        return resultado.group(1).strip()
    return None

def extrair_cpf(texto):  # era extrair_nit duplicado!
    resultado = re.search(r"CPF:\s+([\d.\-]+)", texto)
    if resultado:
        return resultado.group(1).strip()
    return None

def extrair_data_nascimento(texto):
    resultado = re.search(r"Data de nascimento:\s+([\d/]+)", texto)
    if resultado:
        return resultado.group(1).strip()
    return None

def extrair_nb(texto):
    resultado = re.search(r"(\d{10})\s+Benefício", texto)
    if resultado:
        return resultado.group(1).strip()
    return None

def extrair_especie(texto):
    resultado = re.search(r"Benefício\s+(\d+\s+-\s+[^\n]+\n\S+)", texto)  # estava faltando!
    if resultado:
        especie = resultado.group(1).strip()
        especie = re.sub(r'\s+\d{2}/\d{2}/\d{4}.*', '', especie)
        especie = especie.replace("\n", " ").strip()
        return especie.title()
    return None

def extrair_data_inicio(texto):
    resultado = re.search(r"Benefício\s+.+?(\d{2}/\d{2}/\d{4})", texto, re.DOTALL)
    if resultado:
        return resultado.group(1).strip()
    return None

def extrair_data_fim(texto):
    resultado = re.search(r"Benefício\s+.+?\d{2}/\d{2}/\d{4}\s+(\d{2}/\d{2}/\d{4})", texto, re.DOTALL)
    if resultado:
        return resultado.group(1).strip()
    return None

