import sys
from ocr import extract_text
from parser import parse_data
from ai_parser import parse_with_ai
from database import save_to_db

def main(file_path):
    text = extract_text(file_path)

    print("\n=== TEXTO EXTRAÍDO ===\n")
    print(text[:1000])

	ai_data = parse_with_ai(text)

	if ai_data:
	    data = {
	        "estabelecimento": ai_data.get("estabelecimento", "Desconhecido"),
	        "cnpj": ai_data.get("cnpj", ""),
	        "data": ai_data.get("data", ""),
	        "valor_total": ai_data.get("valor_total", 0),
	        "categoria": ai_data.get("categoria", "Outros"),
	        "forma_pagamento": ai_data.get("forma_pagamento", ""),
	        "itens": ai_data.get("itens", []),
	        "arquivo_origem": file_path
	    }
	else:
	    # fallback se IA falhar
	    data = parse_data(text, file_path)
    if ai_data:
        if ai_data.get("valor_total"):
            data["valor_total"] = ai_data["valor_total"]

        if ai_data.get("estabelecimento"):
            data["estabelecimento"] = ai_data["estabelecimento"]

        if ai_data.get("itens"):
            data["itens"] = ai_data["itens"]

    save_to_db(data)

    print("\nRESULTADO FINAL:\n", data)

if __name__ == "__main__":
    main(sys.argv[1])
