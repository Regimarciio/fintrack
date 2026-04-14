import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv
from parser_inteligente import parse_with_rules

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

def parse_with_ai(texto_extraido):
    # Sempre usa o parser por regras primeiro (mais rapido e confiavel)
    resultado_regras = parse_with_rules(texto_extraido)
    
    # Se achou estabelecimento e valor, retorna direto
    if resultado_regras['estabelecimento'] != 'Nao identificado' and resultado_regras['valor_total'] > 0:
        print("Usando parser por regras (confiavel)")
        return resultado_regras
    
    # Se nao, tenta OpenAI como fallback
    if client:
        try:
            print("Tentando OpenAI...")
            prompt = f"Extraia JSON com estabelecimento, valor_total, data. Texto: {texto_extraido[:2000]}"
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            resultado_ia = json.loads(response.choices[0].message.content)
            return resultado_ia
        except Exception as e:
            print(f"Erro OpenAI: {e}")
    
    return resultado_regras

def fallback_parser(texto):
    return parse_with_rules(texto)
