import json
from datetime import datetime
from ocr import extract_text
from parser_inteligente import parse_with_rules

def testar_extraicao(arquivo):
    print(f"Testando: {arquivo}")
    texto = extract_text(arquivo)
    resultado = parse_with_rules(texto)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
    return resultado

if __name__ == "__main__":
    testar_extraicao('uploads/fatura-inter-2025-11.pdf')
