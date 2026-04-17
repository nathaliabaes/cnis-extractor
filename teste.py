import pdfplumber
import io

with open("cnis.pdf", "rb") as f:
    pdf_bytes = f.read()

print("tamanho do pdf:", len(pdf_bytes))

with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
    print("numero de paginas:", len(pdf.pages))
    texto = "\n".join(page.extract_text() for page in pdf.pages)

print(texto)