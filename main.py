import pdfplumber
import io
import re
import functions_framework
import json
import requests
import calendar


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
        
def extrair_vinculos(texto):
    linhas = re.findall(r"(.+Empregado.+)", texto)

    vinculos = []

    for linha in linhas:
        idx = texto.find(linha)
        trecho = texto[idx:idx+300]
        
        origem = re.search(r"\d{3}\.\d{5}\.\d{2}-\d\s+[\d./-]+\s+((?:(?!Empregado)\S+\s*)+)Empregado", trecho)
        datas_completas = re.findall(r"\d{2}/\d{2}/\d{4}", linha)
        ult_remun = re.search(r"(\d{2}/\d{4})$", linha)

        if not origem:
            continue

        if not datas_completas:
            continue

        nome_origem = origem.group(1).strip()   
        
        nome_origem = re.sub(r'\s+\d{6,}$', '', nome_origem).strip()
        nome_origem = re.sub(r'\s+[A-Za-z]*\d+[A-Za-z0-9]*$', '', nome_origem).strip()
        nome_origem = re.sub(r'\s+FALIDO$', '', nome_origem).strip()
        nome_origem = re.sub(r'\s+\d{3,5}$', '', nome_origem).strip()

        idx = texto.find(linha)
        proximo_trecho = texto[idx + len(linha):idx + len(linha) + 100]
        continuacao = re.match(r"\n([A-ZÀÁÂÃÉÊÍÓÔÕÚÇ .]+)\s+(?:Público|Agente)", proximo_trecho)
        
        if continuacao:
            nome_origem = nome_origem + " " + continuacao.group(1).strip()

        data_inicio = datas_completas[0]

        if len(datas_completas) >= 2:
            data_fim = datas_completas[1]
        elif ult_remun:
            mes, ano = ult_remun.group(1).split('/')
            ultimo_dia = calendar.monthrange(int(ano), int(mes))[1]
            data_fim = f"{ultimo_dia:02d}/{mes}/{ano}"
        else:
            continue

        vinculo = {
            "origem": nome_origem.title(),
            "data_inicio": data_inicio,
            "data_fim": data_fim
        }
        
        vinculos.append(vinculo)
    
    return vinculos

def extrair_dados_cnis(pdf_bytes):
    texto = extrair_texto(pdf_bytes) # extrai o texto do PDF 
    print(f"Tamanho do texto extraído: {len(texto)}")
    print(f"Primeiros 200 chars do texto: {texto[:200]}")
    nome = extrair_nome(texto)
    nit = extrair_nit(texto) 
    cpf = extrair_cpf(texto)
    data_nasc = extrair_data_nascimento(texto)
    beneficios = extrair_dados_beneficio(texto)  # pega os dados do benefício
    vinculos = extrair_vinculos(texto)
    
    dados = {
        "nome": nome or "",
        "nit": nit or "",
        "cpf": cpf or "",
        "data_nascimento": data_nasc or "",
        "beneficios": beneficios,
        "vinculos": vinculos        
    }

    if vinculos is None and nome is not None:
        dados["aviso"] = "CNIS simplificado - solicitar modelo completo"
    
    return dados


# marca essa função como o ponto de entrada da Cloud Function
@functions_framework.http
def processar_cnis(request):
    
    pdf_bytes = None
    url = None

    # 1. Recebe JSON (caso do n8n)
    if request.is_json:
        data = request.get_json(silent=True)
        url = data.get('url')

    # 2. Recebe Form Data (fallback)
    elif 'url' in request.form:
        url = request.form.get('url')

    # 3. Recebe arquivo direto
    elif 'file' in request.files:
        arquivo = request.files['file']
        pdf_bytes = arquivo.read()

    # DEBUG - ver o que está chegando
    print(f"URL recebida: {url}")

    # Se veio URL, tenta baixar o PDF
    if url:
        try:
            response = requests.get(
                url,
                allow_redirects=True,
                headers={
                    "User-Agent": "Mozilla/5.0"
                },
                timeout=30
            )

            print(f"Status: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type')}")

            if response.status_code != 200:
                return json.dumps({
                    "erro": "Erro ao baixar o PDF",
                    "status_code": response.status_code
                }), 400

            pdf_bytes = response.content

        except Exception as e:
            return json.dumps({
                "erro": "Erro ao fazer download",
                "detalhe": str(e)
            }), 500

    # Validação final
    if not pdf_bytes:
        return json.dumps({
            "erro": "Nenhum arquivo ou URL enviado"
        }), 400

    # Processa o CNIS
    try:
        resultado = extrair_dados_cnis(pdf_bytes)

        return json.dumps(resultado, ensure_ascii=False), 200

    except Exception as e:
        return json.dumps({
            "erro": "Erro ao processar PDF",
            "detalhe": str(e)
        }), 500