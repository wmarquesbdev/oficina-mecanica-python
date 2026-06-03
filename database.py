"""
database.py - Camada de acesso a dados (SQLite) do Sistema Oficina.
Cria o banco oficina.db, as tabelas, o seed inicial e expoe funcoes CRUD.
"""
import sqlite3
import hashlib

DB_NAME = "oficina.db"


def conectar():
    con = sqlite3.connect(DB_NAME)
    con.execute("PRAGMA foreign_keys = ON")
    con.row_factory = sqlite3.Row  # acesso por nome de coluna
    return con


def hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


def criar_tabelas():
    con = conectar()
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id     INTEGER PRIMARY KEY AUTOINCREMENT,
            nome   TEXT NOT NULL,
            login  TEXT NOT NULL UNIQUE,
            senha  TEXT NOT NULL
        )""")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            nome      TEXT NOT NULL,
            cpf       TEXT,
            telefone  TEXT,
            email     TEXT
        )""")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS carros (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id  INTEGER NOT NULL,
            placa       TEXT NOT NULL,
            marca       TEXT,
            modelo      TEXT,
            ano         INTEGER,
            cor         TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )""")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS servicos (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao  TEXT NOT NULL,
            preco      REAL NOT NULL DEFAULT 0
        )""")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS ordens_servico (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id     INTEGER NOT NULL,
            carro_id       INTEGER NOT NULL,
            data_abertura  TEXT NOT NULL,
            status         TEXT NOT NULL DEFAULT 'Aberta',
            observacoes    TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id),
            FOREIGN KEY (carro_id)   REFERENCES carros(id)
        )""")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS os_itens (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            ordem_id    INTEGER NOT NULL,
            servico_id  INTEGER NOT NULL,
            quantidade  INTEGER NOT NULL DEFAULT 1,
            preco_unit  REAL NOT NULL DEFAULT 0,
            FOREIGN KEY (ordem_id)   REFERENCES ordens_servico(id),
            FOREIGN KEY (servico_id) REFERENCES servicos(id)
        )""")

    con.commit()
    con.close()


def seed():
    """Insere dados iniciais apenas se as tabelas estiverem vazias."""
    con = conectar()
    cur = con.cursor()

    if cur.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0] == 0:
        cur.execute("INSERT INTO usuarios (nome, login, senha) VALUES (?,?,?)",
                    ("Administrador", "admin", hash_senha("1234")))

    if cur.execute("SELECT COUNT(*) FROM servicos").fetchone()[0] == 0:
        servicos = [
            ("Troca de oleo", 120.00),
            ("Alinhamento e balanceamento", 90.00),
            ("Troca de pastilha de freio", 180.00),
            ("Revisao geral", 350.00),
            ("Troca de correia dentada", 450.00),
        ]
        cur.executemany("INSERT INTO servicos (descricao, preco) VALUES (?,?)", servicos)

    con.commit()
    con.close()


# ---------- AUTENTICACAO ----------
def autenticar(login: str, senha: str):
    con = conectar()
    row = con.execute(
        "SELECT * FROM usuarios WHERE login = ? AND senha = ?",
        (login, hash_senha(senha)),
    ).fetchone()
    con.close()
    return row


# ---------- CLIENTES ----------
def listar_clientes():
    con = conectar()
    rows = con.execute("SELECT * FROM clientes ORDER BY nome").fetchall()
    con.close()
    return rows


def inserir_cliente(nome, cpf, telefone, email):
    con = conectar()
    con.execute("INSERT INTO clientes (nome, cpf, telefone, email) VALUES (?,?,?,?)",
                (nome, cpf, telefone, email))
    con.commit()
    con.close()


def atualizar_cliente(id_, nome, cpf, telefone, email):
    con = conectar()
    con.execute("UPDATE clientes SET nome=?, cpf=?, telefone=?, email=? WHERE id=?",
                (nome, cpf, telefone, email, id_))
    con.commit()
    con.close()


def excluir_cliente(id_):
    con = conectar()
    con.execute("DELETE FROM clientes WHERE id=?", (id_,))
    con.commit()
    con.close()


# ---------- CARROS ----------
def listar_carros():
    """Lista carros com o nome do cliente (JOIN)."""
    con = conectar()
    rows = con.execute("""
        SELECT carros.id, clientes.nome AS cliente, carros.placa,
               carros.marca, carros.modelo, carros.ano, carros.cor,
               carros.cliente_id
        FROM carros
        JOIN clientes ON carros.cliente_id = clientes.id
        ORDER BY carros.placa
    """).fetchall()
    con.close()
    return rows


def inserir_carro(cliente_id, placa, marca, modelo, ano, cor):
    con = conectar()
    con.execute("""INSERT INTO carros (cliente_id, placa, marca, modelo, ano, cor)
                   VALUES (?,?,?,?,?,?)""",
                (cliente_id, placa, marca, modelo, ano, cor))
    con.commit()
    con.close()


def atualizar_carro(id_, cliente_id, placa, marca, modelo, ano, cor):
    con = conectar()
    con.execute("""UPDATE carros SET cliente_id=?, placa=?, marca=?, modelo=?, ano=?, cor=?
                   WHERE id=?""",
                (cliente_id, placa, marca, modelo, ano, cor, id_))
    con.commit()
    con.close()


def excluir_carro(id_):
    con = conectar()
    con.execute("DELETE FROM carros WHERE id=?", (id_,))
    con.commit()
    con.close()


# ---------- SERVICOS ----------
def listar_servicos():
    con = conectar()
    rows = con.execute("SELECT * FROM servicos ORDER BY descricao").fetchall()
    con.close()
    return rows


def inserir_servico(descricao, preco):
    con = conectar()
    con.execute("INSERT INTO servicos (descricao, preco) VALUES (?,?)", (descricao, preco))
    con.commit()
    con.close()


def atualizar_servico(id_, descricao, preco):
    con = conectar()
    con.execute("UPDATE servicos SET descricao=?, preco=? WHERE id=?", (descricao, preco, id_))
    con.commit()
    con.close()


def excluir_servico(id_):
    con = conectar()
    con.execute("DELETE FROM servicos WHERE id=?", (id_,))
    con.commit()
    con.close()


# ---------- CARROS POR CLIENTE (para a tela de OS) ----------
def listar_carros_por_cliente(cliente_id):
    con = conectar()
    rows = con.execute(
        "SELECT * FROM carros WHERE cliente_id=? ORDER BY placa", (cliente_id,)
    ).fetchall()
    con.close()
    return rows


# ---------- ORDENS DE SERVICO ----------
def listar_ordens():
    """Lista as OS com nome do cliente, placa do carro e total calculado."""
    con = conectar()
    rows = con.execute("""
        SELECT o.id, c.nome AS cliente, car.placa, o.data_abertura, o.status,
               o.cliente_id, o.carro_id, o.observacoes,
               (SELECT COALESCE(SUM(quantidade * preco_unit), 0)
                  FROM os_itens WHERE ordem_id = o.id) AS total
        FROM ordens_servico o
        JOIN clientes c   ON o.cliente_id = c.id
        JOIN carros  car  ON o.carro_id   = car.id
        ORDER BY o.id DESC
    """).fetchall()
    con.close()
    return rows


def listar_itens_da_ordem(ordem_id):
    con = conectar()
    rows = con.execute("""
        SELECT i.id, i.servico_id, s.descricao, i.quantidade, i.preco_unit,
               (i.quantidade * i.preco_unit) AS subtotal
        FROM os_itens i
        JOIN servicos s ON i.servico_id = s.id
        WHERE i.ordem_id = ?
    """, (ordem_id,)).fetchall()
    con.close()
    return rows


def inserir_ordem(cliente_id, carro_id, data_abertura, status, observacoes, itens):
    """itens = lista de dicts: {servico_id, quantidade, preco_unit}"""
    con = conectar()
    cur = con.cursor()
    cur.execute("""INSERT INTO ordens_servico
                   (cliente_id, carro_id, data_abertura, status, observacoes)
                   VALUES (?,?,?,?,?)""",
                (cliente_id, carro_id, data_abertura, status, observacoes))
    ordem_id = cur.lastrowid
    for it in itens:
        cur.execute("""INSERT INTO os_itens (ordem_id, servico_id, quantidade, preco_unit)
                       VALUES (?,?,?,?)""",
                    (ordem_id, it["servico_id"], it["quantidade"], it["preco_unit"]))
    con.commit()
    con.close()
    return ordem_id


def atualizar_ordem(ordem_id, cliente_id, carro_id, status, observacoes, itens):
    """Atualiza a OS e regrava os itens (apaga os antigos e insere os novos)."""
    con = conectar()
    cur = con.cursor()
    cur.execute("""UPDATE ordens_servico
                   SET cliente_id=?, carro_id=?, status=?, observacoes=?
                   WHERE id=?""",
                (cliente_id, carro_id, status, observacoes, ordem_id))
    cur.execute("DELETE FROM os_itens WHERE ordem_id=?", (ordem_id,))
    for it in itens:
        cur.execute("""INSERT INTO os_itens (ordem_id, servico_id, quantidade, preco_unit)
                       VALUES (?,?,?,?)""",
                    (ordem_id, it["servico_id"], it["quantidade"], it["preco_unit"]))
    con.commit()
    con.close()


def excluir_ordem(ordem_id):
    con = conectar()
    cur = con.cursor()
    cur.execute("DELETE FROM os_itens WHERE ordem_id=?", (ordem_id,))
    cur.execute("DELETE FROM ordens_servico WHERE id=?", (ordem_id,))
    con.commit()
    con.close()


if __name__ == "__main__":
    # Executar este arquivo cria o banco e popula o seed.
    criar_tabelas()
    seed()
    print(f"Banco '{DB_NAME}' criado/atualizado com sucesso.")
    print("Usuario padrao -> login: admin | senha: 1234")
