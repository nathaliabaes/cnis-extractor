import pdfplumber
import io
import re
from main import *
import requests

url = "https://rigoniadvogados.bitrix24.com.br/rest/203788/rouigospmdym6zt7/download/?token=disk%7CaWQ9MTA5NjY5NiZfPUlQV09MUERTM2htSmdkNXNyYWJ0VDk4SkVwd0FvYVZj%7CImRvd25sb2FkfGRpc2t8YVdROU1UQTVOalk1TmlaZlBVbFFWMDlNVUVSVE0yaHRTbWRrTlhOeVlXSjBWRGs0U2tWd2QwRnZZVlpqfDIwMzc4OHxyb3VpZ29zcG1keW02enQ3Ig%3D%3D.iv0vYqB%2Fx8qXnqT0%2BLq7LpVC2mfXlZlCEvvGBRRnCIs%3D"

response = requests.get(
    url,
    allow_redirects=True,
    headers={
        "User-Agent": "Mozilla/5.0"
    }
)

print("Status:", response.status_code)
print("Content-Type:", response.headers.get("content-type"))

with open("teste.pdf", "wb") as f:
    f.write(response.content)