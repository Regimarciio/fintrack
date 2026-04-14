import json
import re

class ParserInteligente:
    def __init__(self, config_file='config_extracao.json'):
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
    
    def extrair(self, texto):
        linhas = texto.split('\n')
        resultado = {}
        
        for campo, config in self.config['campos'].items():
            valor = self._extrair_campo(texto, linhas, campo, config)
            resultado[campo] = valor
        
        # Força extração do maior valor (prioridade para VALOR COBRADO)
        maior_valor = self._extrair_maior_valor(texto, linhas)
        if maior_valor > 0:
            resultado['valor_total'] = maior_valor
        
        # Classificar categoria
        estabelecimento = resultado.get('estabelecimento', '').upper()
        resultado['categoria'] = self._classificar_categoria(estabelecimento)
        
        if not resultado.get('itens'):
            resultado['itens'] = []
        
        return resultado
    
    def _extrair_maior_valor(self, texto, linhas):
        """Extrai o maior valor encontrado no documento"""
        
        # Primeiro: procura por VALOR COBRADO
        for i, linha in enumerate(linhas):
            if 'VALOR COBRADO' in linha:
                nums = re.findall(r'(\d{1,6},\d{2})', linha)
                if not nums and i+1 < len(linhas):
                    nums = re.findall(r'(\d{1,6},\d{2})', linhas[i+1])
                if nums:
                    valor = float(nums[0].replace(',', '.'))
                    if valor > 100:  # Ignora valores pequenos como 177,80
                        return valor
        
        # Segundo: procura por R$
        r_matches = re.findall(r'R?\$?\s*(\d{1,6},\d{2})', texto)
        if r_matches:
            valores = [float(v.replace(',', '.')) for v in r_matches]
            # Pega o maior valor, ignorando valores muito pequenos (pagamento mínimo)
            maiores = [v for v in valores if v > 100]
            if maiores:
                return max(maiores)
            return max(valores)
        
        # Terceiro: qualquer número com vírgula (maior deles)
        todos = re.findall(r'(\d{1,6},\d{2})', texto)
        if todos:
            valores = [float(v.replace(',', '.')) for v in todos]
            maiores = [v for v in valores if v > 100]
            if maiores:
                return max(maiores)
            return max(valores)
        
        return 0.0
    
    def _extrair_campo(self, texto, linhas, campo, config):
        for padrao in config['padroes']:
            valor = None
            
            if padrao['tipo'] == 'palavra_chave':
                valor = self._buscar_por_palavra_chave(linhas, padrao['valor'])
            elif padrao['tipo'] == 'regex':
                valor = self._buscar_por_regex(texto, padrao['valor'])
            elif padrao['tipo'] == 'prefixo':
                valor = self._buscar_por_prefixo(linhas, padrao['valor'])
            elif padrao['tipo'] == 'proximo_a':
                valor = self._buscar_proximo_a(linhas, padrao['valor'])
            
            if valor and valor not in ['', None]:
                return self._limpar_valor(campo, valor)
        
        return self._valor_padrao(campo)
    
    def _buscar_por_palavra_chave(self, linhas, palavras):
        for linha in linhas:
            for palavra in palavras:
                if palavra.upper() in linha.upper():
                    if len(linha.strip()) < 100:
                        return linha.strip()
        return None
    
    def _buscar_por_regex(self, texto, padrao):
        matches = re.findall(padrao, texto)
        if matches:
            return matches[0]
        return None
    
    def _buscar_por_prefixo(self, linhas, prefixos):
        for i, linha in enumerate(linhas):
            for prefixo in prefixos:
                if prefixo in linha.upper():
                    nums = re.findall(r'(\d{1,6},\d{2})', linha)
                    if nums:
                        return nums[0]
                    if i+1 < len(linhas):
                        nums = re.findall(r'(\d{1,6},\d{2})', linhas[i+1])
                        if nums:
                            return nums[0]
        return None
    
    def _buscar_proximo_a(self, linhas, referencia):
        for i, linha in enumerate(linhas):
            if referencia in linha:
                for j in range(i+1, min(i+6, len(linhas))):
                    datas = re.findall(r'(\d{2}[/-]\d{2}[/-]\d{4})', linhas[j])
                    if datas:
                        return datas[0]
        return None
    
    def _limpar_valor(self, campo, valor):
        if campo == 'cnpj':
            return re.sub(r'\D', '', valor) if valor else ''
        elif campo == 'data':
            if valor and '/' in valor:
                partes = valor.split('/')
                if len(partes) == 3:
                    ano = partes[2] if len(partes[2]) == 4 else f"20{partes[2]}"
                    return f"{ano}-{partes[1]}-{partes[0]}"
        return valor if valor else ''
    
    def _valor_padrao(self, campo):
        padroes = {
            'estabelecimento': 'Nao identificado',
            'cnpj': '',
            'data': '',
            'valor_total': 0.0,
            'forma_pagamento': '',
            'itens': []
        }
        return padroes.get(campo, '')
    
    def _classificar_categoria(self, estabelecimento):
        for categoria, palavras in self.config['categorias'].items():
            for palavra in palavras:
                if palavra in estabelecimento:
                    return categoria
        return 'Outros'

def parse_with_rules(texto):
    parser = ParserInteligente()
    return parser.extrair(texto)
