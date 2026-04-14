import sqlite3
import json
from datetime import datetime

DB_NAME = 'fintrack.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS faturas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            arquivo_origem TEXT,
            estabelecimento TEXT,
            cnpj TEXT,
            data TEXT,
            valor_total REAL,
            forma_pagamento TEXT,
            categoria TEXT,
            itens TEXT,
            data_upload TEXT,
            data_atualizacao TEXT
        )
    ''')
    conn.commit()
    conn.close()

def salvar_fatura(dados):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Se tiver ID, atualiza; senao, insere
    if 'id' in dados and dados['id']:
        cursor.execute('''
            UPDATE faturas SET
                estabelecimento = ?,
                cnpj = ?,
                data = ?,
                valor_total = ?,
                forma_pagamento = ?,
                categoria = ?,
                itens = ?,
                data_atualizacao = ?
            WHERE id = ?
        ''', (
            dados.get('estabelecimento', ''),
            dados.get('cnpj', ''),
            dados.get('data', ''),
            dados.get('valor_total', 0),
            dados.get('forma_pagamento', ''),
            dados.get('categoria', 'Outros'),
            json.dumps(dados.get('itens', [])),
            datetime.now().isoformat(),
            dados['id']
        ))
    else:
        cursor.execute('''
            INSERT INTO faturas (
                arquivo_origem, estabelecimento, cnpj, data, valor_total,
                forma_pagamento, categoria, itens, data_upload, data_atualizacao
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            dados.get('arquivo_origem', ''),
            dados.get('estabelecimento', ''),
            dados.get('cnpj', ''),
            dados.get('data', ''),
            dados.get('valor_total', 0),
            dados.get('forma_pagamento', ''),
            dados.get('categoria', 'Outros'),
            json.dumps(dados.get('itens', [])),
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
    
    conn.commit()
    conn.close()

def listar_faturas():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id, arquivo_origem, estabelecimento, cnpj, data, valor_total, forma_pagamento, categoria, itens, data_upload FROM faturas ORDER BY data DESC')
    rows = cursor.fetchall()
    conn.close()
    
    faturas = []
    for row in rows:
        faturas.append({
            'id': row[0],
            'arquivo_origem': row[1],
            'estabelecimento': row[2],
            'cnpj': row[3],
            'data': row[4],
            'valor_total': row[5],
            'forma_pagamento': row[6],
            'categoria': row[7],
            'itens': json.loads(row[8]) if row[8] else [],
            'data_upload': row[9]
        })
    return faturas

def buscar_fatura_por_id(fatura_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id, arquivo_origem, estabelecimento, cnpj, data, valor_total, forma_pagamento, categoria, itens, data_upload FROM faturas WHERE id = ?', (fatura_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'id': row[0],
            'arquivo_origem': row[1],
            'estabelecimento': row[2],
            'cnpj': row[3],
            'data': row[4],
            'valor_total': row[5],
            'forma_pagamento': row[6],
            'categoria': row[7],
            'itens': json.loads(row[8]) if row[8] else [],
            'data_upload': row[9]
        }
    return None

def deletar_fatura(fatura_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM faturas WHERE id = ?', (fatura_id,))
    conn.commit()
    conn.close()

def atualizar_fatura(fatura_id, dados):
    dados['id'] = fatura_id
    salvar_fatura(dados)

def get_estatisticas():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Total gasto
    cursor.execute('SELECT SUM(valor_total) FROM faturas')
    total_gasto = cursor.fetchone()[0] or 0
    
    # Gasto por categoria
    cursor.execute('SELECT categoria, SUM(valor_total) FROM faturas GROUP BY categoria')
    por_categoria = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Numero de faturas
    cursor.execute('SELECT COUNT(*) FROM faturas')
    total_faturas = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return {
        'total_gasto': total_gasto,
        'por_categoria': por_categoria,
        'total_faturas': total_faturas
    }

# Inicializar banco
init_db()
