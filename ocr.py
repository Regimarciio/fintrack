import os
from PIL import Image
import pytesseract
import pdf2image

def extrair_texto_arquivo(caminho_arquivo):
    extensao = os.path.splitext(caminho_arquivo)[1].lower()
    texto_completo = ""
    
    try:
        if extensao == '.pdf':
            imagens = pdf2image.convert_from_path(caminho_arquivo, dpi=300)
            for i, imagem in enumerate(imagens):
                texto_pagina = pytesseract.image_to_string(imagem, lang='por')
                texto_completo += f"\n--- PAGINA {i+1} ---\n{texto_pagina}"
        elif extensao in ['.png', '.jpg', '.jpeg']:
            imagem = Image.open(caminho_arquivo)
            texto_completo = pytesseract.image_to_string(imagem, lang='por')
        elif extensao == '.txt':
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                texto_completo = f.read()
        else:
            return f"Formato nao suportado: {extensao}"
        
        return texto_completo.strip() if texto_completo else "Nenhum texto encontrado"
    except Exception as e:
        return f"Erro no OCR: {str(e)}"

# Alias para compatibilidade
extract_text = extrair_texto_arquivo
