import pdfplumber
import io
import re

def extrair_texto(pdf_bytes):
    # pdf_bytes é o PDF em formato de bytes (como vem da internet)
    # io.BytesIO transforma esses bytes em algo que o pdfplumber consegue abrir
    # "abre esse arquivo e chama ele de pdf aqui dentro"
    with pdfplumber.open(io.bytesIO(pdf_bytes)) as pdf:
        #O PDF pode ter várias páginas, então percorremos todas
        # e juntamos o texto com quebra de linha entre elas
        texto = "\n".join(page.extract_text() for page in pdf.pages)
        #"Para cada página do PDF, extrai o texto, e junta tudo numa string só separada por quebra de linha"


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

def extrair_nit(texto):
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
    resultado = re.search(r"(\d{10})\s+\d+\s+-\s+[A-ZÀ-Ú ]+(?<!Não Informado)", texto)
    
    if resultado:
        return resultado.group(1).strip()
    
    return None

def extrair_especie(texto):
    resultado = re.search(r"\d{10}\s+(\d+\s+-\s+[A-ZÀ-Ú ]+?)(?:\s+Não Informado|\n)", texto)
    
    if resultado:
        # Verifica se não é Não Informado
        especie = resultado.group(1).strip()
        if "Não Informado" not in especie:
            return especie.title()
    
    return None