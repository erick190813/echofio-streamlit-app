# database.py - Versão CORRIGIDA (Removido '#' da string SQL)

import sqlite3
from passlib.hash import pbkdf2_sha256 # Garante que a senha seja hashed
import os

# --- Configuração do Banco de Dados e Admin Inicial ---
DB_NAME = "materiais.db"
# Obter o caminho absoluto para o arquivo do banco de dados.
# Usar o diretório onde este script database.py está localizado como referência.
DB_PATH = os.path.join(os.path.dirname(__file__), DB_NAME)


ADMIN_USERNAME = "erick19082013"
ADMIN_PASSWORD = "admin1234" # Lembre-se, esta senha será hashed!

# --- Dados dos 4 Materiais Iniciais (Fictícios, BASEADO EM EXEMPLOS COMUNS) ---
# Você DEVE substituir estes dados pelos 4 materiais que você cadastrou com suas propriedades reais.
MATERIAIS_INICIAIS = [
    # (nome, densidade g/cm³, temp_extrusao °C, reciclavel bool, biodegradavel bool, eficiencia %, perda %, consumo_energia kWh/kg)
    ("PETG Reciclado", 1.27, 240.0, 1, 0, 88.0, 7.0, 1.3), # Exemplo 1
    ("PLA Reciclado", 1.24, 210.0, 1, 1, 90.0, 5.0, 1.0),   # Exemplo 2
    ("ABS Reciclado", 1.04, 235.0, 1, 0, 85.0, 9.0, 1.5),   # Exemplo 3
    ("PP Reciclado", 0.90, 220.0, 1, 0, 80.0, 12.0, 1.4),  # Exemplo 4
]
# ---------------------------------------------------------------------------


def conectar_db():
    """Conecta ao banco de dados SQLite e retorna o objeto de conexão e cursor,
       com row_factory configurado para acessar colunas por nome."""
    # --- DEBUG PRINT ---
    print(f"[DEBUG DB] Tentando conectar ao DB em: {DB_PATH}")
    # -----------------
    try:
        # Usa o caminho absoluto baseado na localização do script
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Para acessar colunas pelo nome (permite row['nome_coluna'])
        cursor = conn.cursor()
        # --- DEBUG PRINT ---
        print(f"[DEBUG DB] Conexão bem-sucedida com: {DB_PATH}")
        # -----------------
        return conn, cursor
    except Exception as e:
        # --- DEBUG PRINT ---
        print(f"[DEBUG DB] ERRO ao conectar ao DB em {DB_PATH}: {e}")
        # -----------------
        # Se a conexão falhar, levanta a exceção para que o app principal possa capturá-la
        raise e


# --- Funções de Inicialização do Banco de Dados ---

def criar_tabela_usuarios():
    """Cria a tabela de usuários se ela não existir, incluindo colunas de privilégio."""
    conn, cursor = conectar_db() # Conecta para executar esta função
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                can_edit_db INTEGER DEFAULT 0, -- 0 para False, 1 para True: Permite editar materiais
                is_admin INTEGER DEFAULT 0     -- 0 para False, 1 para True: Permite gerenciar permissões de outros
            )
        ''')
        conn.commit()
        print("[DEBUG DB] Tabela 'users' verificada/criada.")
    except Exception as e:
        print(f"[DEBUG DB] ERRO ao criar tabela de usuários: {e}")
    finally:
        conn.close() # Fecha a conexão ao terminar


def criar_usuario_admin_inicial():
    """Cria o usuário administrador inicial (erick19082013) se ele não existir."""
    conn, cursor = conectar_db() # Conecta para executar esta função
    try:
        # Verifica se o usuário admin já existe
        cursor.execute("SELECT id FROM users WHERE username = ?", (ADMIN_USERNAME,))
        user_exists = cursor.fetchone()

        # Se o usuário admin NÃO existir, cria ele
        if not user_exists:
            hashed_password = pbkdf2_sha256.hash(ADMIN_PASSWORD) # Hashea a senha
            cursor.execute(
                "INSERT INTO users (username, password, can_edit_db, is_admin) VALUES (?, ?, ?, ?)",
                (ADMIN_USERNAME, hashed_password, 1, 1) # Admin inicial tem ambos os privilégios (editar DB e ser admin)
            )
            conn.commit()
            print(f"[DEBUG DB] Usuário administrador inicial '{ADMIN_USERNAME}' criado com sucesso.")
        # else: print(f"[DEBUG DB] Usuário administrador '{ADMIN_USERNAME}' já existe.") # Debug opcional
    except Exception as e:
        print(f"[DEBUG DB] ERRO ao criar usuário administrador inicial: {e}")
    finally:
        conn.close() # Fecha a conexão ao terminar


def criar_tabela_materiais():
    """Cria a tabela de materiais se ela não existir."""
    conn, cursor = conectar_db() # Conecta para executar esta função
    try:
        # --- DEBUG PRINT ADICIONAL ---
        print("[DEBUG DB] Iniciando função criar_tabela_materiais()...")
        print("[DEBUG DB] Executando CREATE TABLE IF NOT EXISTS materiais...")
        # -----------------------------
        # --- CORREÇÃO: Removidos comentários # dentro da string SQL ---
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS materiais (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE NOT NULL,
                densidade REAL, -- g/cm³ (Agora é comentário SQL --)
                temp_extrusao REAL, -- °C
                reciclavel BOOLEAN, -- 0 ou 1
                biodegradavel BOOLEAN, -- 0 ou 1
                eficiencia REAL, -- % (Ex: 85.5)
                perda_percentual REAL, -- % (Ex: 10.0)
                consumo_energia_kwh_por_kg REAL -- kWh/kg do material de entrada
            )
        ''')
        # -------------------------------------------------------------
        # --- DEBUG PRINT ADICIONAL ---
        print("[DEBUG DB] Execução do CREATE TABLE IF NOT EXISTS materiais concluída.")
        print("[DEBUG DB] Tentando commit da criação da tabela materiais...")
        # -----------------------------
        conn.commit()
        print("[DEBUG DB] Commit da criação da tabela materiais bem-sucedido.")
        print("[DEBUG DB] Tabela 'materiais' verificada/criada.")
    except Exception as e:
        # --- DEBUG PRINT ADICIONAL ---
        print(f"[DEBUG DB] ERRO CAPTURADO ao criar tabela de materiais: {e}")
        # -----------------------------
    finally:
        conn.close() # Fecha a conexão ao terminar


def adicionar_materiais_iniciais_se_vazio():
    """Adiciona materiais iniciais à tabela 'materiais' APENAS se ela estiver vazia."""
    conn, cursor = conectar_db() # Conecta para executar esta função
    try:
        # Verifica se a tabela materiais está vazia
        cursor.execute("SELECT COUNT(*) FROM materiais")
        count = cursor.fetchone()[0] # Obtém o número de linhas

        if count == 0:
            print("[DEBUG DB] Tabela 'materiais' está vazia. Adicionando materiais iniciais...")
            # Insere cada material da lista MATERIAIS_INICIAIS
            cursor.executemany(
                """
                INSERT INTO materiais (nome, densidade, temp_extrusao, reciclavel, biodegradavel, eficiencia, perda_percentual, consumo_energia_kwh_por_kg)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                MATERIAIS_INICIAIS
            )
            conn.commit()
            print(f"[DEBUG DB] {len(MATERIAIS_INICIAIS)} materiais iniciais adicionados com sucesso.")
        # else: print(f"[DEBUG DB] Tabela 'materiais' já contém {count} registros. Não adicionando materiais iniciais.") # Debug opcional

    except Exception as e:
        print(f"[DEBUG DB] ERRO ao adicionar materiais iniciais: {e}")
    finally:
        conn.close() # Fecha a conexão ao terminar


def inicializar_db():
    """Inicializa o banco de dados, cria tabelas (usuarios, materiais), admin inicial e materiais iniciais (se vazio)."""
    # A ordem é importante
    criar_tabela_usuarios()   # Garante que a tabela 'users' exista primeiro
    criar_tabela_materiais()  # Garante que a tabela 'materiais' exista
    criar_usuario_admin_inicial() # Garante que o admin inicial exista
    adicionar_materiais_iniciais_se_vazio() # Adiciona materiais iniciais se a tabela estiver vazia


# --- Funções para Usuários (Atualizadas com Privilégios) ---

def adicionar_usuario(username, password):
    """Adiciona um novo usuário ao banco de dados com privilégios padrão (nenhum)."""
    conn, cursor = conectar_db()
    try:
        hashed_password = pbkdf2_sha256.hash(password) # Hashea a senha
        # Novos usuários não têm privilégios (0 para ambos) por padrão
        cursor.execute(
            "INSERT INTO users (username, password, can_edit_db, is_admin) VALUES (?, ?, ?, ?)",
            (username, hashed_password, 0, 0)
        )
        conn.commit()
        print(f"[DEBUG DB] Usuário '{username}' adicionado com privilégios padrão.")
        return True, "Usuário registrado com sucesso! Faça login para continuar."
    except sqlite3.IntegrityError:
        print(f"[DEBUG DB] Erro ao adicionar usuário '{username}': Nome já existe (IntegrityError).")
        return False, "Nome de usuário já existe."
    except Exception as e:
        print(f"[DEBUG DB] ERRO ao adicionar usuário '{username}': {e}")
        return False, f"Erro ao registrar usuário: {e}"
    finally:
        conn.close()


def verificar_usuario(username, password):
    """Verifica as credenciais do usuário."""
    conn, cursor = conectar_db()
    try:
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        result = cursor.fetchone() # result é um objeto Row ou None
        if result:
            hashed_password = result['password'] # Acessa a coluna 'password'
            if pbkdf2_sha256.verify(password, hashed_password): # Verifica a senha hasheada
                print(f"[DEBUG DB] Verificação de credenciais para '{username}': SUCESSO.")
                return True # Credenciais corretas
        print(f"[DEBUG DB] Verificação de credenciais para '{username}': FALHA (usuário não encontrado ou senha incorreta).")
        return False # Usuário não encontrado ou senha incorreta
    except Exception as e:
        print(f"[DEBUG DB] ERRO ao verificar usuário '{username}': {e}")
        return False # Erro durante a verificação
    finally:
        conn.close()


def buscar_privilegios_usuario(username):
    """Busca os privilégios (can_edit_db, is_admin) de um usuário pelo nome."""
    conn, cursor = conectar_db()
    try:
        # --- DEBUG PRINT ---
        print(f"[DEBUG DB] Buscando privilégios para usuário: '{username}'...")
        # -----------------
        cursor.execute("SELECT can_edit_db, is_admin FROM users WHERE username = ?", (username,))
        result = cursor.fetchone() # result é um objeto Row ou None
        if result:
            # Retorna um dicionário com os status dos privilégios (converte 1/0 para True/False)
            privileges = {"can_edit_db": bool(result['can_edit_db']), "is_admin": bool(result['is_admin'])}
            print(f"[DEBUG DB] Privilégios para '{username}' encontrados: {privileges}")
            return privileges
        print(f"[DEBUG DB] Privilégios para '{username}': Usuário não encontrado.")
        return {"can_edit_db": False, "is_admin": False} # Usuário não encontrado ou sem privilégios
    except Exception as e:
        print(f"[DEBUG DB] ERRO ao buscar privilégios do usuário '{username}': {e}")
        return {"can_edit_db": False, "is_admin": False} # Erro durante a busca
    finally:
        conn.close()


def buscar_todos_usuarios_basico():
    """Busca ID, username, can_edit_db e is_admin de todos os usuários (para gerenciamento de permissões)."""
    conn, cursor = conectar_db()
    try:
        # Seleciona todas as colunas exceto a senha
        cursor.execute("SELECT id, username, can_edit_db, is_admin FROM users ORDER BY username")
        users_list = [dict(row) for row in cursor.fetchall()] # Converte linhas para dicionários
        print(f"[DEBUG DB] Buscar todos usuários (básico) retornou {len(users_list)} usuários.")
        return users_list
    except Exception as e:
        print(f"[DEBUG DB] ERRO ao buscar todos os usuários (básico): {e}")
        return []
    finally:
        conn.close()


def atualizar_privilegio_edicao_db(user_id, can_edit_status):
    """Atualiza o privilégio can_edit_db para um usuário específico pelo ID."""
    conn, cursor = conectar_db()
    try:
        # Certifica-se que o status é 0 (False) ou 1 (True)
        status_int = 1 if can_edit_status else 0
        cursor.execute(
            "UPDATE users SET can_edit_db = ? WHERE id = ?",
            (status_int, user_id)
        )
        conn.commit()
        print(f"[DEBUG DB] Privilégio de edição atualizado para user_id {user_id} para status: {status_int}.")
        return True, "Privilégio de edição do banco de dados atualizado com sucesso."
    except Exception as e:
        print(f"[DEBUG DB] ERRO ao atualizar privilégio de edição para user_id {user_id}: {e}")
        conn.rollback() # Desfaz a operação em caso de erro
        return False, f"Erro ao atualizar privilégio: {e}"
    finally:
        conn.close()

# Opcional: Função para verificar se um usuário existe pelo nome (útil para o registro)
def usuario_existe(username):
     conn, cursor = conectar_db()
     try:
         cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
         result = cursor.fetchone()
         return result is not None
     except Exception as e:
         print(f"[DEBUG DB] ERRO ao verificar se usuário '{username}' existe: {e}")
         return False
     finally:
         conn.close()


# --- Funções para Materiais ---

def adicionar_material(nome, densidade, temp_extrusao, reciclavel, biodegradavel, eficiencia, perda_percentual, consumo_energia_kwh_por_kg):
    """Adiciona um novo material ao banco de dados."""
    conn, cursor = conectar_db()
    try:
        # Converte booleanos Python para 1/0 para SQLite
        reciclavel_db = 1 if reciclavel else 0
        biodegradavel_db = 1 if biodegradavel else 0

        cursor.execute(
            """
            INSERT INTO materiais (nome, densidade, temp_extrusao, reciclavel, biodegradavel, eficiencia, perda_percentual, consumo_energia_kwh_por_kg)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (nome, densidade, temp_extrusao, reciclavel_db, biodegradavel_db, eficiencia, perda_percentual, consumo_energia_kwh_por_kg)
        )
        conn.commit()
        print(f"[DEBUG DB] Material '{nome}' adicionado com sucesso.")
        return True, "Material adicionado com sucesso!"
    except sqlite3.IntegrityError:
        print(f"[DEBUG DB] Erro ao adicionar material '{nome}': Nome já existe (IntegrityError).")
        return False, "Material com este nome já existe."
    except Exception as e:
        print(f"[DEBUG DB] ERRO geral ao adicionar material '{nome}': {e}")
        return False, f"Erro ao adicionar material: {e}"
    finally:
        conn.close()

def buscar_todos_materiais():
    """Busca todos os materiais no banco de dados."""
    conn, cursor = conectar_db()
    try:
        cursor.execute("SELECT * FROM materiais ORDER BY nome") # Adicionado ORDER BY para consistência
        materiais = cursor.fetchall() # Retorna lista de objetos Row
        print(f"[DEBUG DB] Buscar todos materiais retornou {len(materiais)} materiais.")
        return materiais
    except Exception as e:
        print(f"[DEBUG DB] ERRO ao buscar todos os materiais: {e}")
        return []
    finally:
        conn.close()

def buscar_material_por_nome(nome):
    """Busca um material específico pelo nome."""
    conn, cursor = conectar_db()
    try:
        cursor.execute("SELECT * FROM materiais WHERE nome = ?", (nome,))
        material = cursor.fetchone() # Retorna um objeto Row ou None
        print(f"[DEBUG DB] Buscar material por nome '{nome}' retornou: {'Encontrado' if material else 'Não encontrado'}")
        return material
    except Exception as e:
        print(f"[DEBUG DB] ERRO ao buscar material por nome '{nome}': {e}")
        return None
    finally:
        conn.close()

def buscar_nomes_materiais():
    """Busca apenas os nomes de todos os materiais, ordenados por nome."""
    conn, cursor = conectar_db()
    try:
        # --- DEBUG PRINT ---
        print("[DEBUG DB] Executando SELECT nome FROM materiais...")
        # -----------------
        cursor.execute("SELECT nome FROM materiais ORDER BY nome")
        raw_results = cursor.fetchall() # Retorna lista de objetos Row
        # --- DEBUG PRINT ---
        print(f"[DEBUG DB] SELECT nome FROM materiais retornou (raw): {raw_results}")
        # -----------------
        # Extrai os nomes dos objetos Row
        nomes_list = [row['nome'] for row in raw_results]
        # --- DEBUG PRINT ---
        print(f"[DEBUG DB] buscar_nomes_materiais() retornando lista: {nomes_list}")
        # -----------------
        return nomes_list
    except Exception as e:
        # --- DEBUG PRINT ---
        print(f"[DEBUG DB] ERRO ao buscar nomes dos materiais: {e}")
        # -----------------
        return [] # Retorna lista vazia em caso de erro
    finally:
        conn.close()

def actualizar_material(id, nome, densidade, temp_extrusao, reciclavel, biodegradavel, eficiencia, perda_percentual, consumo_energia_kwh_por_kg):
    """Atualiza os dados de um material existente pelo ID."""
    conn, cursor = conectar_db()
    try:
        # Converte booleanos Python para 1/0 para SQLite
        reciclavel_db = 1 if reciclavel else 0
        biodegradavel_db = 1 if biodegradavel else 0

        cursor.execute(
            """
            UPDATE materiais SET nome=?, densidade=?, temp_extrusao=?, reciclavel=?, biodegradavel=?, eficiencia=?, perda_percentual=?, consumo_energia_kwh_por_kg=?
            WHERE id=?
            """,
            (nome, densidade, temp_extrusao, reciclavel_db, biodegradavel_db, eficiencia, perda_percentual, consumo_energia_kwh_por_kg, id)
        )
        conn.commit()
        print(f"[DEBUG DB] Material ID {id} atualizado com sucesso.")
        return True, "Material atualizado com sucesso!"
    except sqlite3.IntegrityError:
         print(f"[DEBUG DB] Erro ao atualizar material ID {id}: Nome '{nome}' já existe.")
         return False, "Não foi possível atualizar: Material com este nome já existe."
    except Exception as e:
        print(f"[DEBUG DB] ERRO geral ao atualizar material com ID {id}: {e}")
        return False, f"Erro ao atualizar material: {e}"
    finally:
        conn.close()

def excluir_material(id):
    """Exclui um material do banco de dados pelo ID."""
    conn, cursor = conectar_db()
    try:
        cursor.execute("DELETE FROM materiais WHERE id = ?", (id,))
        conn.commit()
        # Verifica se alguma linha foi realmente excluída
        if cursor.rowcount > 0:
             print(f"[DEBUG DB] Material ID {id} excluído com sucesso.")
             return True, "Material excluído com sucesso!"
        else:
             print(f"[DEBUG DB] Excluir material ID {id}: Material não encontrado (nenhuma linha afetada).")
             return False, "Material não encontrado." # Ou True, se considerar sucesso o ID não existir
    except Exception as e:
        print(f"[DEBUG DB] ERRO ao excluir material com ID {id}: {e}")
        return False, f"Erro ao excluir material: {e}"
    finally:
        conn.close()

# --- Código de Debug Opcional (Ignorar ou remover em produção) ---
# Este bloco só executa se você rodar este script database.py diretamente.
# É útil para testar as funções do banco de dados isoladamente.
# if __name__ == "__main__":
#     print("--- Testando Funções do Database ---")
#     # Rode este arquivo standalone: python database.py
#     # Certifique-se de que o arquivo materiais.db está no mesmo diretório.
#     # Se você deletou o materias.db antes de rodar este script diretamente, ele criará um novo.
#     inicializar_db() # Garante que tabelas, admin e materiais iniciais existam
#
#     print("\nBuscando todos os nomes de materiais após inicialização:")
#     nomes_apos_init = buscar_nomes_materiais()
#     print(f"Nomes encontrados: {nomes_apos_init}")
#
#     print("\nBuscando todos os materiais após inicialização:")
#     todos_materiais = buscar_todos_materiais()
#     if todos_materiais:
#         for mat in todos_materiais:
#             print(dict(mat)) # Imprimir cada material como dicionário
#     else:
#         print("Nenhum material encontrado na tabela materiais após inicialização.")
#
#     print("\nVerificando credenciais de erick19082013...")
#     print(f"Resultado: {verificar_usuario('erick19082013', 'admin1234')}") # Deve ser True
#
#     print("\nBuscando privilégios de erick19082013:")
#     print(buscar_privilegios_usuario("erick19082013")) # Deve ter can_edit_db=True, is_admin=True
#
#     print("\nBuscando todos os usuários (básico):")
#     todos_users = buscar_todos_usuarios_basico()
#     for user in todos_users:
#         print(user) # Imprime como dicionário
#
#     # Exemplo de teste de adição de material (se a tabela estava vazia antes)
#     # print("\nTentando adicionar um material extra (PP - extra):")
#     # sucesso_add, msg_add = adicionar_material("PP - Extra", 0.91, 225.0, True, False, 78.0, 15.0, 1.6)
#     # print(f"Resultado: {msg_add} (Sucesso: {sucesso_add})")
#
#     # Testar verificação de usuário (admin inicial)
#     # print("\nVerificando credenciais de erick19082013...")
#     # print(f"Resultado: {verificar_usuario('erick19082013', 'admin1234')}") # Deve ser True