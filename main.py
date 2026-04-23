import pdfplumber
import io
import re
import functions_framework
import json

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

def extrair_dados_beneficio(texto):
    # Pega todas as linhas que contém "Benefício"
    linhas = re.findall(r"(.+Benefício.+)", texto)
    
    beneficios = []
    nbs_vistos = set()  # para evitar duplicatas

    for linha in linhas:
        # Junta a linha com a próxima para pegar "TRABALHO" que pode quebrar
        idx = texto.find(linha)
        trecho = texto[idx:idx+300]  # pega um trecho maior a partir da linha
        # Pega as duas datas da linha
        datas = re.findall(r"\d{2}/\d{2}/\d{4}", linha)
        
        if len(datas) < 2:
            continue  # pula se não tiver as duas datas

        if len(datas) < 2:
            continue
        
        nb = re.search(r"(\d{10})\s+Benefício", linha)  # estava faltando!
        if not nb:
            continue
            
        nb_valor = nb.group(1).strip()
        
        nb_valor = nb.group(1).strip()

        # Pula se já processou esse NB
        if nb_valor in nbs_vistos:
            continue
        nbs_vistos.add(nb_valor)

        especie = re.search(r"Benefício\s+(\d+\s+-\s+[^\n]+?)\s+\d{2}/\d{2}/\d{4}.+\n(\S+)", trecho)
        esp = ""
        if especie:
            parte1 = especie.group(1).strip()
            parte2 = especie.group(2).strip()
            if re.match(r'^[A-ZÀÁÂÃÉÊÍÓÔÕÚÇ]+$', parte2) and len(parte2) > 2:
                esp = f"{parte1} {parte2}"
            else:
                esp = parte1
        
        beneficios.append({
            "nb": nb_valor,
            "especie": esp.title() if esp else "",
            "data_inicio": datas[0],
            "data_fim": datas[1]
        })
    
    return beneficios           
        
        
def extrair_origem_vinculo(texto):
    linhas = re.findall(r"(.+Empregado.+)", texto)
    
    melhor_data = 0
    melhor_origem = None
    
    for linha in linhas:
        #"Encontra o NIT, pula o Código Emp., captura tudo até a matrícula, pula a matrícula e para em Empregado"
        ult_remun = re.search(r"(\d{2}/\d{4})$", linha)
        origem = re.search(r"\d{3}\.\d{5}\.\d{2}-\d\s+[\d./-]+\s+(.+?)\s+\w+\s+Empregado", linha)
        
        if ult_remun and origem:
            mes, ano = ult_remun.group(1).split("/")
            numero = int(ano) * 100 + int(mes)
            
            if numero > melhor_data:
                melhor_data = numero
                nome_origem = origem.group(1).strip()  # guarda sem .title() ainda
                
                # Verifica se o nome continua na linha seguinte
                idx = texto.find(linha)
                proximo_trecho = texto[idx + len(linha):idx + len(linha) + 100]
                continuacao = re.match(r"\n([A-ZÀÁÂÃÉÊÍÓÔÕÚÇ ]+)\s+Público", proximo_trecho)
                
                if continuacao:
                    nome_origem = nome_origem + " " + continuacao.group(1).strip()
                
            melhor_origem = nome_origem.title()  # aplica .title() só no final  
        
    return melhor_origem

def extrair_dados_cnis(pdf_bytes):
    texto = extrair_texto(pdf_bytes) # extrai o texto do PDF 
    nome = extrair_nome(texto)
    nit = extrair_nit(texto) 
    cpf = extrair_cpf(texto)
    data_nasc = extrair_data_nascimento(texto)
    beneficios = extrair_dados_beneficio(texto)  # pega os dados do benefício
    origem = extrair_origem_vinculo(texto)

    dados = {
        "nome": nome or "",
        "nit": nit or "",
        "cpf": cpf or "",
        "data_nascimento": data_nasc or "",
        "beneficios": beneficios,
        "origem": origem or ""
    }

    if origem is None and nome is not None:
        dados["aviso"] = "CNIS simplificado - solicitar modelo completo"
    
    return dados

@functions_framework.http # marca essa função como o ponto de entrada da Cloud Function
def processar_cnis(request):
    # Verifica se veio um arquivo na requisição
    if 'file' not in request.files:
        return json.dumps({"erro": "Nenhum arquivo enviado"}), 400
    
    # Pega o arquivo enviado
    arquivo = request.files['file']
    pdf_bytes = arquivo.read()
    
    # Extrai os dados
    resultado = extrair_dados_cnis(pdf_bytes)
    
    # Devolve o resultado em JSON
    return json.dumps(resultado, ensure_ascii=False), 200