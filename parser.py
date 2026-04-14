import re
from datetime import datetime

def clean_text(text):
    text = re.sub(r'(?<=\w)\s(?=\w)', '', text)
    text = re.sub(r'(\d)\s+(\d)', r'\1\2', text)
    text = re.sub(r'(\d)\s+\.', r'\1.', text)
    text = re.sub(r'\.\s+(\d)', r'.\1', text)
    text = re.sub(r'(\d)\s+,', r'\1,', text)
    text = re.sub(r',\s+(\d)', r',\1', text)
    text = re.sub(r'R\s*\$\s*', 'R$', text)
    return text

def parse_data(text, file_path):
    text = clean_text(text)

    valores = re.findall(r"R\$\s*([\d\.]+,\d{2})", text)

    valor = 0.0
    if valores:
        valores_float = [float(v.replace(".", "").replace(",", ".")) for v in valores]
        valores_filtrados = [v for v in valores_float if v < 3000]
        valor = max(valores_filtrados) if valores_filtrados else max(valores_float)

    data_match = re.search(r"(\d{2}/\d{2}/\d{4})", text)

    return {
        "estabelecimento": "Banco Inter" if "inter" in text.lower() else "Desconhecido",
        "cnpj": "",
        "data": data_match.group(1) if data_match else str(datetime.now().date()),
        "valor_total": valor,
        "categoria": "Financeiro",
        "forma_pagamento": "Fatura",
        "itens": [],
        "arquivo_origem": file_path
    }
