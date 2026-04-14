import sqlite3

def init_db():
    conn = sqlite3.connect("data/gastos.db")
    c = conn.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS gastos (id INTEGER PRIMARY KEY, data TEXT, estabelecimento TEXT, valor REAL, categoria TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS itens (id INTEGER PRIMARY KEY, gasto_id INTEGER, nome TEXT, valor REAL, categoria TEXT)")

    conn.commit()
    conn.close()

def save_to_db(data):
    init_db()

    conn = sqlite3.connect("data/gastos.db")
    c = conn.cursor()

    c.execute("INSERT INTO gastos (data, estabelecimento, valor, categoria) VALUES (?,?,?,?)",
              (data["data"], data["estabelecimento"], data["valor_total"], data["categoria"]))

    gid = c.lastrowid

    for item in data.get("itens", []):
        c.execute("INSERT INTO itens (gasto_id, nome, valor, categoria) VALUES (?,?,?,?)",
                  (gid, item.get("nome"), item.get("valor"), item.get("categoria")))

    conn.commit()
    conn.close()
