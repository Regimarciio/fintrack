import requests
import json

def parse_with_local(texto):
    response = requests.post('http://localhost:11434/api/generate', 
        json={
            "model": "llama3.2:3b",
            "prompt": f"Extraia JSON com estabelecimento, valor_total, data deste texto: {texto[:2000]}",
            "stream": False
        })
    return json.loads(response.json()['response'])
