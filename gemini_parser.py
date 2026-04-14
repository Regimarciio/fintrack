import google.generativeai as genai
import json
import re

# Configure sua chave gratuita em: https://aistudio.google.com/app/apikey
genai.configure(api_key="SUA_CHAVE_GEMINI_AQUI")

def parse_with_gemini(texto):
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Extraia do texto abaixo: estabelecimento, CNPJ, data, valor_total, itens.
    Responda APENAS JSON.
    
    Texto: {texto[:3000]}
    """
    
    response = model.generate_content(prompt)
    return json.loads(re.sub(r'```json\n?|```\n?', '', response.text))
