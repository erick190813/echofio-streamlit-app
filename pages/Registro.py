# Registro.py

import streamlit as st
import database
import os # Para verificar a existência do arquivo de logo

# --- Configuração da página (Novamente, remover st.set_page_config se estiver no script principal) ---
# Removendo st.set_page_config daqui.

# --- Layout do cabeçalho (Opcional, mas bom para consistência visual) ---
col_logo, col_title = st.columns([1, 4])

with col_logo:
    LOGO_PATH = "../31121abd-f8d6-4d98-b07a-9de3735ea257.png"
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=80) # Logo um pouco menor nas páginas secundárias
    else:
        st.header("♻️") # Fallback icon

with col_title:
    st.title("Cadastro") # Título específico da página
    st.markdown("### Crie sua conta EchoFio AI")

st.markdown("---")

# --- Formulário de Cadastro ---
st.subheader("📝 Criar Nova Conta")

# Verificar se o usuário já está logado. Se sim, mostrar mensagem.
if st.session_state.get('logged_in', False):
    st.info(f"Você já está logado como {st.session_state.username}.")
    st.markdown("Você pode navegar usando o menu ao lado.")
else:
    # Exibir o formulário de registro apenas se não estiver logado
    with st.form("registro_form"):
        novo_username = st.text_input("Nome de Usuário (único)")
        nova_password = st.text_input("Senha", type="password")
        confirm_password = st.text_input("Confirmar Senha", type="password")

        submit_button = st.form_submit_button("Cadastrar")

        if submit_button:
            if not novo_username or not nova_password or not confirm_password:
                 st.warning("Por favor, preencha todos os campos.")
            elif nova_password != confirm_password:
                st.error("As senhas não coincidem.")
            elif database.usuario_existe(novo_username):
                 st.error("Este nome de usuário já está em uso.")
            else:
                sucesso, msg = database.adicionar_usuario(novo_username, nova_password)
                if sucesso:
                    st.success(f"✅ {msg} Agora você pode fazer login.")
                    # Opcional: Redirecionar para a página de login
                    # st.session_state.page = 'Login' # Esta abordagem requer lógica extra no main_app.py
                    # st.experimental_rerun()
                else:
                    st.error(f"❌ {msg}")

    st.markdown("---")


# --- Sidebar (Apenas a parte 'Sobre') ---
# A navegação principal é gerada pelo Streamlit a partir da pasta 'pages'.
# Aqui, mantemos apenas as informações 'Sobre' e o rodapé.
with st.sidebar:
     st.header("🌱 Sobre EchoFio AI")
     st.info(
         "EchoFio AI é um protótipo que integra a identificação de plásticos "
         "recicl\u00E1veis por imagem com a simula\u00E7\u00E3o da produ\u00E7\u00E3o de filamentos para impress\u00E3o 3D, "
         "promovendo a economia circular e a sustentabilidade."
     )
     st.markdown("---")
     st.caption("EchoFio AI Protótipo v0.8.4") # Manter a versão consistente