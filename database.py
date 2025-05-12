# database.py - CORRIGIDO

import sqlite3
from passlib.hash import pbkdf2_sha256

DB_NAME = "materiais.db"

def conectar_db():
    """Conecta ao banco de dados SQLite e retorna o objeto de conexão e cursor."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Para acessar colunas pelo nome
    cursor = conn.cursor()
    return conn, cursor

# --- NOVAS Funções para Usuários (MOVIDAS PARA FORA DE conectar_db) ---

def criar_tabela_usuarios():
    conn = sqlite3.connect(DB_NAME) # Usar DB_NAME consistente
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


def adicionar_usuario(username, password):
    # Hashear a senha antes de armazenar
    hashed_password = pbkdf2_sha256.hash(password)

    conn = sqlite3.connect(DB_NAME) # Usar DB_NAME consistente
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        conn.close()
        return True, "Usuário cadastrado com sucesso!"
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Nome de usuário já existe."
    except Exception as e:
        conn.close()
        return False, f"Erro ao cadastrar usuário: {e}"


def verificar_usuario(username, password):
    conn = sqlite3.connect(DB_NAME) # Usar DB_NAME consistente
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()

    if result:
        stored_password = result[0]
        # Verificar a senha fornecida com a senha hasheada armazenada
        if pbkdf2_sha256.verify(password, stored_password):
            return True  # Login bem-sucedido
    return False  # Usuário ou senha inválidos


def usuario_existe(username):
    conn = sqlite3.connect(DB_NAME) # Usar DB_NAME consistente
    c = conn.cursor()
    c.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    return result is not None

# --- FIM DAS NOVAS Funções para Usuários ---


def inicializar_db():
    """Cria as tabelas (materiais e users) se não existirem e insere dados iniciais."""
    conn, cursor = conectar_db()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS materiais (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT UNIQUE NOT NULL,
        densidade_g_cm3 REAL,
        temp_extrusao_recomendada TEXT,
        reciclavel BOOLEAN,
        biodegradavel BOOLEAN,
        eficiencia_extrusao REAL
    )
    """)

    # Garante que a tabela de usuários também é criada ao inicializar o DB principal
    criar_tabela_usuarios() # <-- Esta chamada agora funciona

    materiais_iniciais = [
        ("PET", 1.38, "230-250°C", True, False, 0.80),
        ("PLA", 1.24, "190-220°C", True, True, 0.85),
        ("ABS", 1.04, "220-250°C", True, False, 0.78),
        ("PP", 0.90, "200-230°C", True, False, 0.82),
        ("PEAD", 0.95, "180-220°C", True, False, 0.88),
        ("PETG", 1.27, "220-250°C", True, False, 0.83),
        ("TPU", 1.21, "210-230°C", False, False, 0.75),
        ("ASA", 1.07, "240-260°C", True, False, 0.79),
        ("HIPS", 1.04, "220-240°C", True, False, 0.80),
        ("PC", 1.20, "260-300°C", True, False, 0.70),
        ("Nylon (PA)", 1.14, "240-270°C", False, False, 0.72)
    ]

    for material in materiais_iniciais:
        try:
            cursor.execute("""
            INSERT INTO materiais (nome, densidade_g_cm3, temp_extrusao_recomendada, reciclavel, biodegradavel, eficiencia_extrusao)
            VALUES (?, ?, ?, ?, ?, ?)
            """, material)
        except sqlite3.IntegrityError:
            pass # Material já existe, ignorar

    conn.commit()
    conn.close()


def buscar_nomes_materiais():
    """Retorna uma lista com os nomes de todos os materiais."""
    conn, cursor = conectar_db()
    cursor.execute("SELECT nome FROM materiais ORDER BY nome ASC")
    nomes = [row["nome"] for row in cursor.fetchall()]
    conn.close()
    return nomes


def buscar_detalhes_material(nome_material):
    """Retorna um dicionário com os detalhes de um material específico."""
    conn, cursor = conectar_db()
    cursor.execute("SELECT * FROM materiais WHERE nome = ?", (nome_material,))
    material_row = cursor.fetchone()
    conn.close()
    return dict(material_row) if material_row else None

# --- FUNÇÕES CRUD EXISTENTES (MANTIDAS) ---

def adicionar_material(nome, densidade_g_cm3, temp_extrusao_recomendada, reciclavel, biodegradavel, eficiencia_extrusao):
    """Adiciona um novo material ao banco de dados."""
    conn, cursor = conectar_db()
    try:
        cursor.execute("""
        INSERT INTO materiais (nome, densidade_g_cm3, temp_extrusao_recomendada, reciclavel, biodegradavel, eficiencia_extrusao)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (nome, densidade_g_cm3, temp_extrusao_recomendada, reciclavel, biodegradavel, eficiencia_extrusao))
        conn.commit()
        return True, "Material adicionado com sucesso!"
    except sqlite3.IntegrityError:
        return False, f"Erro: O material '{nome}' já existe."
    except Exception as e:
        return False, f"Erro ao adicionar material: {e}"
    finally:
        conn.close()

def atualizar_material(id_material, nome, densidade_g_cm3, temp_extrusao_recomendada, reciclavel, biodegradavel, eficiencia_extrusao):
    """Atualiza um material existente no banco de dados."""
    conn, cursor = conectar_db()
    try:
        cursor.execute("""
        UPDATE materiais
        SET nome = ?, densidade_g_cm3 = ?, temp_extrusao_recomendada = ?, reciclavel = ?, biodegradavel = ?, eficiencia_extrusao = ?
        WHERE id = ?
        """, (nome, densidade_g_cm3, temp_extrusao_recomendada, reciclavel, biodegradavel, eficiencia_extrusao, id_material))
        conn.commit()
        if cursor.rowcount == 0:
            return False, "Nenhum material encontrado com o ID fornecido para atualizar."
        return True, "Material atualizado com sucesso!"
    except sqlite3.IntegrityError:
        return False, f"Erro: Já existe um material com o nome '{nome}'."
    except Exception as e:
        return False, f"Erro ao atualizar material: {e}"
    finally:
        conn.close()

def excluir_material(id_material):
    """Exclui um material do banco de dados pelo ID."""
    conn, cursor = conectar_db()
    try:
        cursor.execute("DELETE FROM materiais WHERE id = ?", (id_material,))
        conn.commit()
        if cursor.rowcount == 0:
            return False, "Nenhum material encontrado com o ID fornecido para excluir."
        return True, "Material excluído com sucesso!"
    except Exception as e:
        return False, f"Erro ao excluir material: {e}"
    finally:
        conn.close()

# --- FIM DAS FUNÇÕES CRUD EXISTENTES ---


# Executa a inicialização do DB se o script for rodado diretamente
if __name__ == "__main__":
    inicializar_db()
    print("Banco de dados inicializado via execução direta de database.py.")

    print("\nNomes dos materiais no banco:")
    for nome_db in buscar_nomes_materiais():
        print(nome_db)

    # Testes das funções de usuário (exemplo)
    # print("\nAdicionando usuário 'testeuser':")
    # sucesso_user, msg_user = adicionar_usuario("testeuser", "senha123")
    # print(msg_user)
    # if sucesso_user:
    #     print("\nVerificando usuário 'testeuser':")
    #     if verificar_usuario("testeuser", "senha123"):
    #         print("Login bem-sucedido para 'testeuser'.")
    #     else:
    #         print("Falha no login para 'testeuser'.")
    #     print(f"Usuário 'testeuser' existe? {usuario_existe('testeuser')}")
    # else:
    #      print(f"Usuário 'testeuser' já existe? {usuario_existe('testeuser')}")