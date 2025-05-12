# Login.py

import streamlit as st
import database
import os # Para verificar a existência do arquivo de logo

# --- Configuração da página (Necessário em cada script de página/app) ---
# NOTA: st.set_page_config só deve ser chamado UMA VEZ, idealmente no script principal.
# Se você chamar em múltiplos arquivos, pode ter warnings. Para apps multi-página,
# é melhor definí-lo apenas no script principal (echofio_app.py neste caso).
# Removendo st.set_page_config daqui.

# --- Layout do cabeçalho (Opcional, mas bom para consistência visual) ---
# Você pode replicar o cabeçalho do echofio_app.py aqui ou ter um cabeçalho mais simples.
# Vamos replicar para manter a identidade visual.
col_logo, col_title = st.columns([1, 4])

with col_logo:
    LOGO_PATH = "../31121abd-f8d6-4d98-b07a-9de3735ea257.png"
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=80) # Logo um pouco menor nas páginas secundárias
    else:
        st.header("♻️") # Fallback icon

with col_title:
    st.title("Login") # Título específico da página
    st.markdown("### Acesse sua conta EchoFio AI")

st.markdown("---")

# --- Formulário de Login ---
st.subheader("🔑 Entrar")

# Verificar se o usuário já está logado. Se sim, redirecionar ou mostrar mensagem.
if st.session_state.get('logged_in', False):
    st.info(f"Você já está logado como {st.session_state.username}.")
    st.markdown("Você pode navegar usando o menu ao lado") # Link genérico
    # O Streamlit lida com a navegação via sidebar automaticamente para páginas logadas.
else:
    # Exibir o formulário de login apenas se não estiver logado
    with st.form("login_form"):
        username = st.text_input("Nome de Usuário")
        password = st.text_input("Senha", type="password")

        submit_button = st.form_submit_button("Entrar")

        if submit_button:
            if database.verificar_usuario(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Login bem-sucedido! Bem-vindo(a), {username}!")
                st.info("Agora você pode acessar os módulos na barra lateral.")
                st.rerun() # Recarrega a página para ativar a navegação das páginas
            else:
                st.error("Nome de usuário ou senha inválidos.")

    st.markdown("---")

# --- Sidebar (Apenas a parte 'Sobre') ---
# A navegação principal é gerada pelo Streamlit a partir da pasta 'pages'.
# Aqui, mantemos apenas as informações 'Sobre' e o rodapé.
with st.sidebar:
     st.header("🌱 Sobre EchoFio AI")
     st.info(
         "EchoFio AI é um protótipo que integra a identificação de plásticos "
         "recicláveis por imagem com a simulação da produção de filamentos para impressão 3D, "
         "promovendo a economia circular e a sustentabilidade."
     )
     st.markdown("---")
     st.caption("EchoFio AI Protótipo v0.8.4") # Manter a versão consistente