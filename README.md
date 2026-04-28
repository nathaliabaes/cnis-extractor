# CNIS Extractor API

API Python hospedada no Google Cloud Run que extrai automaticamente dados de PDFs do CNIS (Cadastro Nacional de Informações Sociais) e integra com o Bitrix24 via n8n.

## O que faz

Recebe um PDF do CNIS e retorna os seguintes dados em JSON:

- Nome, CPF, NIT e Data de Nascimento
- Lista de benefícios (NB, Espécie, DIB, DCB)
- Lista de vínculos empregatícios com datas de início e fim

## Tecnologias

- Python 3.11+
- `pdfplumber` — extração de texto do PDF
- `flask` + `functions-framework` — Cloud Function HTTP
- `requests` — download do PDF via URL

## Instalação local

```bash
pip install -r requirements.txt
```

## Rodar localmente

```bash
python -m functions_framework --target processar_cnis
```

A API ficará disponível em `http://localhost:8080`.

## Como usar

### Enviando um arquivo PDF diretamente

```bash
curl -X POST http://localhost:8080 -F "file=@cnis.pdf"
```

### Enviando uma URL para download

```bash
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{"url": "https://url-do-pdf.com/arquivo.pdf"}'
```

## Exemplo de retorno

```json
{
  "nome": "Nathalia Baes de Oliveira",
  "nit": "111.22222.33-4",
  "cpf": "012.345.678-90",
  "data_nascimento": "01/02/2000",
  "beneficios": [
    {
      "nb": "01234567890",
      "especie": "91 - Auxilio Doenca Por Acidente Do Trabalho",
      "data_inicio": "08/09/2023",
      "data_fim": "02/04/2025"
    }
  ],
  "vinculos": [
    {
      "origem": "Nome da empresa",
      "data_inicio": "15/07/2023",
      "data_fim": "03/04/2026"
    }
  ]
}
```

## Observações

- Funciona apenas com PDFs digitais (texto selecionável)
- PDFs escaneados não são suportados
- O modelo simplificado do CNIS (Relações Previdenciárias) retorna aviso para enviar o modelo completo (Extrato Previdenciário)

## Deploy

O projeto está configurado para deploy automático via GitHub → Google Cloud Run. Qualquer `git push` na branch `main` atualiza a API automaticamente.
