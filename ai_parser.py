import json
from openai import OpenAI

client = OpenAI(api_key="SUA_API_KEY_AQUI")

def parse_with_ai(text):

    prompt = f"""
Extraia dados financeiros do texto.

Retorne JSON:

{{
  "estabelecimento": "",
  "valor_total": 0.0,
  "itens": [
    {{
      "nome": "",
      "valor": 0.0,
      "categoria": ""
    }}
  ]
}}

Ignore pagamentos e valores positivos.

Texto:
{text[:6000]}
"""

    try:
        res = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[{"role":"user","content":prompt}],
            temperature=0
        )

        return json.loads(res.choices[0].message.content)

    except:
        return None
