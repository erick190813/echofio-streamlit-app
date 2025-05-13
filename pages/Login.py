# Login.py - Versão Atualizada para Carregar Privilégios

import streamlit as st
import database
import os # Para verificar a existência do arquivo de logo

# --- Configuração da página (Remover st.set_page_config se estiver no script principal) ---
# Removendo st.set_page_config daqui. A configuração global deve estar em echofio_app.py.

# --- Layout do cabeçalho (Consistência visual) ---
# Assume que o arquivo da logo está na raiz do seu projeto. Ajuste o caminho se necessário.
LOGO_FILE_NAME = "31121abd-f8d6-4d98-b07a-9de3735ea257.png" # Nome do arquivo da sua logo
# Tenta encontrar o caminho da logo relativo à pasta 'pages' (se Login.py estiver em pages/) ou na raiz
# Se Login.py estiver na raiz, use apenas LOGO_FILE_NAME.
# Se Login.py estiver em pages/, use "../" + LOGO_FILE_NAME
# Vamos assumir que Login.py ESTÁ NA RAIZ do projeto, ao lado de echofio_app.py
LOGO_PATH = LOGO_FILE_NAME


col_logo, col_title = st.columns([1, 4])

with col_logo:
     # Verifica se o caminho da logo existe e exibe
     if os.path.exists(LOGO_PATH):
         st.image(LOGO_PATH, width=80) # Logo um pouco menor nas páginas secundárias
     else:
         st.header("♻️") # Ícone de fallback se a logo não for encontrada


with col_title:
    st.title("Login") # Título específico da página
    st.markdown("### Acesse sua conta ECHOFIO") # Subtítulo atualizado

st.markdown("---")

# --- Formulário de Login ---
st.subheader("🔒 Entrar")

# Verificar se o usuário já está logado. Se sim, mostrar mensagem.
if st.session_state.get('logged_in', False):
    st.info(f"Você já está logado como **{st.session_state.username}**.")
    # Opcional: Adicionar botão de logout aqui também, ou link para outra página.
    # if st.button("Sair"):
    #     st.session_state.logged_in = False
    #     st.session_state.username = ""
    #     if 'user_privileges' in st.session_state: # Remover privilégios ao deslogar
    #          del st.session_state['user_privileges']
    #     st.rerun() # Recarrega a página
    st.markdown("Você pode navegar usando o menu ao lado.")

else:
    # Exibir o formulário de login apenas se não estiver logado
    with st.form("login_form"):
        username_input = st.text_input("Nome de Usuário")
        password_input = st.text_input("Senha", type="password")

        submit_button = st.form_submit_button("Entrar")

        if submit_button:
            if database.verificar_usuario(username_input, password_input):
                st.session_state.logged_in = True
                st.session_state.username = username_input

                # --- NOVO: Carregar privilégios do usuário ao logar ---
                st.session_state.user_privileges = database.buscar_privilegios_usuario(username_input)
                # -----------------------------------------------------

                st.success(f"Login bem-sucedido! Bem-vindo(a), {username_input}!")
                st.info("Agora você pode acessar os módulos na barra lateral.")
                st.rerun() # Recarrega a página para ativar a navegação das páginas logadas

            else:
                st.error("Nome de usuário ou senha inválidos.")

    st.markdown("---")


# --- Sidebar (Atualizar a descrição do projeto e incluir logo) ---
with st.sidebar:
     # Adicionar o logo na sidebar também (opcional, mas comum)
     # Use o mesmo tratamento de caminho da logo do cabeçalho principal
     if os.path.exists(LOGO_PATH):
         st.image(LOGO_PATH, width=80) # Logo menor na sidebar
     else:
         st.header("♻️") # Ícone de fallback

     st.markdown("---") # Separador visual

     st.header("🌱 Sobre o Projeto ECHOFIO") # Nome do projeto atualizado
     st.info(
         "O **Projeto ECHOFIO** transforma resíduos plásticos em filamentos "
         "sustentáveis de alta qualidade para impressão 3D, promovendo a "
         "economia circular e reduzindo o impacto ambiental." # Descrição atualizada, concisa e sem menção a IA
     )
     st.markdown("---")
     st.write("Desenvolvido por Equipe ECHOFIO") # Créditos