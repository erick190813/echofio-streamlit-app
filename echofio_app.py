# echofio_app.py

import streamlit as st
import database
import os # Importar para verificar a existência do arquivo de logo

# --- Configuração da página (DEVE SER O PRIMEIRO COMANDO STREAMLIT) ---
st.set_page_config(page_title="EchoFio", layout="wide", initial_sidebar_state="expanded")

# --- Inicializar o banco de dados ---
try:
    database.inicializar_db()
    # Também garantir que a tabela de usuários seja criada (se não estiver em inicializar_db)
    database.criar_tabela_usuarios()
    if 'nomes_materiais' not in st.session_state:
        nomes_db = database.buscar_nomes_materiais()
        st.session_state.nomes_materiais = list(nomes_db) if nomes_db else []
    # Inicializar estado de login
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
         st.session_state.username = ""

except Exception as e:
    st.error(f"Erro CRÍTICO ao inicializar o banco de dados: {e}")
    st.warning(
        "A aplicação pode não funcionar corretamente. Verifique o arquivo 'database.py' e se o arquivo 'materiais.db' foi recriado.")
    st.session_state.nomes_materiais = ["PET (Erro DB)", "PLA (Erro DB)", "ABS (Erro DB)"]
    st.session_state.logged_in = False # Garantir que não está logado se houver erro no DB

# --- Função para deslogar ---
def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.success("Você foi desconectado.")
    st.rerun() # Recarrega a página para mostrar a tela de login

# --- Layout do cabeçalho com logo e título ---
col_logo, col_title = st.columns([1, 4])

with col_logo:
    LOGO_PATH = "31121abd-f8d6-4d98-b07a-9de3735ea257.png"
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=100) # Ajuste o width conforme necessário
    else:
        st.warning(f"Arquivo de logo não encontrado: {LOGO_PATH}")
        st.header("♻️") # Fallback icon

with col_title:
    st.title("EchoFio")
    st.markdown("### Inovação Sustentável em Filamentos 3D")

st.markdown("---")

# --- Conteúdo principal baseado no estado de login ---
if st.session_state.logged_in:
    # Se logado, Streamlit exibirá as páginas da pasta 'pages'
    # Não precisamos colocar o conteúdo das páginas aqui, Streamlit faz isso automaticamente
    st.success(f"Bem-vindo, {st.session_state.username}! Use o menu ao lado para navegar.")

    # Adicionar botão de logout na sidebar quando logado
    with st.sidebar:
        st.markdown("---") # Separador visual antes do logout
        st.button("🔒 Logout", on_click=logout)

else:
    # Se não logado, mostre opções de login/cadastro ou redirecione para a página de login
    st.info("Por favor, faça login ou cadastre-se para acessar os recursos.")

    # Você pode adicionar links ou botões para as páginas de Login e Registro aqui
    # ou confiar que o Streamlit listará Login.py e Registro.py na sidebar
    # se eles estiverem na pasta raiz e as páginas estiverem na subpasta 'pages'.
    # Streamlit lista arquivos .py na raiz e na pasta 'pages'.
    # A ordem é alfabética, a menos que você use números prefixados (ex: 01_Login.py).
    # Para garantir que Login/Registro apareçam antes das páginas principais,
    # vamos confiar que eles estarão na raiz e as páginas principais na subpasta 'pages'.
    # O Streamlit listará todos eles, mas o fluxo de lógica no main_app.py
    # garante que o conteúdo das páginas só apareça se logado.

    # Pode-se adicionar um pequeno texto incentivando o cadastro/login:
    st.markdown("""
    Para começar, faça login ou crie uma nova conta utilizando as opções na barra lateral.
    """)

# --- Sidebar (Será preenchida automaticamente pelo Streamlit com base nos arquivos) ---
# O conteúdo manual da sidebar que estava aqui na versão anterior (Navegação)
# será sobrescrito pela navegação automática do Streamlit baseada nos arquivos na pasta 'pages'.
# Mantenha apenas a seção "Sobre o EchoFio AI" e o rodapé de versão.

with st.sidebar:
    # Adicionar o logo na sidebar também (opcional, mas comum)
    # if os.path.exists(LOGO_PATH):
    #     st.image(LOGO_PATH, width=80) # Ajuste o width
    # st.markdown("---") # Separador

    st.header("🌱 Sobre EchoFio AI")
    st.info(
        "EchoFio AI é um protótipo que integra a identificação de plásticos "
        "recicláveis por imagem com a simulação da produção de filamentos para impressão 3D, "
        "promovendo a economia circular e a sustentabilidade."
    )
    st.markdown("---")
    # A navegação (Identificação, Simulação, BD) será adicionada automaticamente aqui pelo Streamlit
    # quando os arquivos estiverem na pasta 'pages'.
    st.caption("EchoFio AI Protótipo v0.8.1") # Incrementar a versão