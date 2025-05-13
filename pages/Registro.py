# Registro.py - Versão CORRIGIDA (Limpeza de Inputs com Chave)

import streamlit as st
import database
import os # Para verificar a existência do arquivo de logo
import re # Importar módulo de expressões regulares para validação de senha

# --- Configuração da página (Remover st.set_page_config se estiver no script principal) ---
# Removendo st.set_page_config daqui.

# --- Layout do cabeçalho (Opcional, mas bom para consistência visual) ---
# Assume que o arquivo da logo está na raiz do seu projeto. Ajuste o caminho se necessário.
LOGO_FILE_NAME = "31121abd-f8d6-4d98-b07a-9de3735ea257.png" # Nome do arquivo da sua logo
# Assumindo que Registro.py ESTÁ NA PASTA 'pages'.
LOGO_PATH_RELATIVE = os.path.join("..", LOGO_FILE_NAME) # Caminho relativo para a raiz

col_logo, col_title = st.columns([1, 4])

with col_logo:
    # Verifica se o caminho da logo existe e exibe
    if os.path.exists(LOGO_PATH_RELATIVE):
        st.image(LOGO_PATH_RELATIVE, width=80) # Logo um pouco menor nas páginas secundárias
    elif os.path.exists(LOGO_FILE_NAME): # Fallback se o script for executado da raiz inesperadamente
         st.image(LOGO_FILE_NAME, width=80)
    else:
        st.header("♻️") # Fallback icon


with col_title:
    st.title("Cadastro") # Título específico da página
    st.markdown("### Crie sua conta ECHOFIO") # Subtítulo atualizado

st.markdown("---")

# --- Funções Auxiliares para Validação Individual da Senha ---
def has_min_length(password, min_len=8):
    return len(password) >= min_len

def has_uppercase(password):
    return bool(re.search(r'[A-Z]', password))

def has_lowercase(password):
    return bool(re.search(r'[a-z]', password))

def has_digit(password):
    return bool(re.search(r'[0-9]', password))

def has_special_char(password):
    # Regex para encontrar qualquer caractere que NÃO seja letra (a-z, A-Z) ou número (0-9) ou underscore (_).
    return bool(re.search(r'[\W_]', password))


# --- Função de Validação de Senha Segura (para o submit final) ---
# Mantemos esta função para a validação final ao submeter o formulário.
def validar_senha_segura(password):
    """Verifica se a senha atende a TODOS os critérios de segurança."""
    if not has_min_length(password):
        return False, f"A senha deve ter no mínimo 8 caracteres (atual: {len(password)})."
    if not has_uppercase(password):
        return False, "A senha deve conter pelo menos uma letra maiúscula."
    if not has_lowercase(password):
        return False, "A senha deve conter pelo menos uma letra minúscula."
    if not has_digit(password):
        return False, "A senha deve conter pelo menos um número."
    if not has_special_char(password):
        return False, "A senha deve conter pelo menos um caractere especial."
    return True, "Senha válida."

# --- Formulário de Cadastro ---
st.subheader("📝 Criar Nova Conta")

# Verificar se o usuário já está logado. Se sim, mostrar mensagem.
if st.session_state.get('logged_in', False):
    st.info(f"Você já está logado como **{st.session_state.username}**.")
    st.markdown("Você pode navegar usando o menu ao lado.")
else:
    # Exibir o formulário de cadastro apenas se não estiver logado

    # --- Lógica para Limpar Formulário na Próxima Execução ---
    # Verifica se a flag de limpeza está ativa (setada após sucesso no submit anterior)
    if st.session_state.get('clear_registro_form', False):
        # Limpa os valores na session state ANTES dos inputs serem instanciados nesta execução
        st.session_state.registro_username_input = ""
        st.session_state.registro_nova_password_input = ""
        st.session_state.registro_confirm_password_input = ""
        st.session_state.clear_registro_form = False # Desativa a flag para não limpar em reruns futuros
        print("[DEBUG REGISTRO] Campos do formulário de registro limpos via session state.") # Debug
    # --- Fim Lógica de Limpeza ---


    # --- Campos FORA do Formulário (para feedback em tempo real) ---
    # Campo de Nome de Usuário (fora do form, precisa de key)
    # Inicializa a chave se não existir.
    if 'registro_username_input' not in st.session_state:
         st.session_state.registro_username_input = "" # Inicializa o valor na sessão

    novo_username_valor = st.text_input(
        "Nome de Usuário",
        help="Escolha um nome de usuário único.",
        key='registro_username_input' # Chave para o campo Nome de Usuário
    )


    # Campo de Senha (FORA do formulário para acionar rerun e feedback em tempo real)
    # Inicializa a chave se não existir.
    if 'registro_nova_password_input' not in st.session_state:
        st.session_state.registro_nova_password_input = "" # Inicializa o valor na sessão

    nova_password_valor = st.text_input(
        "Senha",
        type="password",
        help="Crie uma senha segura (mínimo 8 caracteres, maiúscula, minúscula, número, especial).",
        key='registro_nova_password_input' # Chave única para este widget
    )
    # O valor digitado agora está automaticamente em st.session_state.registro_nova_password_input


    # --- NOVO: DEBUG PRINT PARA A SENHA (Agora fora do form) ---
    # Este print mostrará no terminal o valor que o script está lendo do input a cada rerun.
    # Usamos st.session_state para garantir que pegamos o valor mais recente
    print(f"[DEBUG REGISTRO] Valor da Senha lido do input (via key): '{st.session_state.registro_nova_password_input}' (Length: {len(st.session_state.registro_nova_password_input)})")
    # -----------------------------------


    # --- Feedback Visual de Requisitos (Fora do formulário, usa o valor do input de fora) ---
    st.markdown("##### Requisitos da Senha:")

    # Verifica cada requisito usando o valor da senha do input FORA do formulário
    password_atual = st.session_state.registro_nova_password_input # Usa o valor da senha do input externo

    if has_min_length(password_atual):
        st.markdown("✅ Mínimo de 8 caracteres.")
    else:
        st.markdown("❌ Mínimo de 8 caracteres.")

    if has_uppercase(password_atual):
        st.markdown("✅ Pelo menos uma letra maiúscula.")
    else:
        st.markdown("❌ Pelo menos uma letra maiúscula.")

    if has_lowercase(password_atual):
        st.markdown("✅ Pelo menos uma letra minúscula.")
    else:
        st.markdown("❌ Pelo menos uma letra minúscula.")

    if has_digit(password_atual):
        st.markdown("✅ Pelo menos um número.")
    else:
        st.markdown("❌ Pelo menos um número.")

    if has_special_char(password_atual):
        st.markdown("✅ Pelo menos um caractere especial.")
    else:
        st.markdown("❌ Mínimo de 8 caracteres.") # CORRIGIDO: Mensagem do requisito especial
    # --- Fim Feedback Visual ---


    # --- Campos DENTRO do Formulário (Processados apenas ao submeter) ---
    # O campo Confirmar Senha e o botão continuam dentro do formulário.
    with st.form("registro_form"):
        # Adicionar chave para o campo Confirmar Senha também para consistência
        # Inicializa a chave se não existir.
        if 'registro_confirm_password_input' not in st.session_state:
            st.session_state.registro_confirm_password_input = "" # Inicializa o valor na sessão

        confirm_password_valor = st.text_input(
            "Confirmar Senha",
            type="password",
            help="Digite a senha novamente para confirmar.",
            key='registro_confirm_password_input' # Chave para o campo Confirmar Senha
        )
        # O valor digitado estará automaticamente em st.session_state.registro_confirm_password_input


        submit_button = st.form_submit_button("Registrar")

        if submit_button:
            # --- Validações FINAIS ao submeter o formulário ---
            # Acessa os valores finais dos inputs (sejam de fora ou de dentro do form)
            # Já estão disponíveis via session state por causa das keys
            final_username = st.session_state.registro_username_input.strip() # Pega do input de fora (via key)
            final_password = st.session_state.registro_nova_password_input # Pega do input de fora (via key)
            final_confirm_password = st.session_state.registro_confirm_password_input # Pega do input de dentro (via key)

            if not final_username or not final_password or not final_confirm_password:
                 st.warning("Por favor, preencha todos os campos.")
            elif final_password != final_confirm_password:
                st.error("As senhas não coincidem.")
            else:
                # --- Validar a complexidade da senha usando a função completa ---
                # Usa a senha do input que está FORA do formulário
                senha_valida_final, mensagem_validacao_final = validar_senha_segura(final_password)

                if not senha_valida_final:
                    st.error(f"❌ Erro na senha: {mensagem_validacao_final}") # Exibe o erro sumário
                # --- FIM Validação de Senha Final ---
                elif database.usuario_existe(final_username): # Verifica se o username já existe
                     st.error("Este nome de usuário já está em uso.")
                else:
                    # Se todas as validações passarem, adiciona o usuário ao banco de dados
                    sucesso, msg = database.adicionar_usuario(final_username, final_password) # Adiciona o usuário
                    if sucesso:
                        st.success(f"✅ {msg}")
                        st.info("Agora você pode fazer login usando seu nome de usuário e senha.")
                        # --- NOVO: Sinaliza para Limpar campos na próxima execução ---
                        st.session_state.clear_registro_form = True # Seta a flag para limpar na próxima execução
                        st.rerun() # Força um rerun
                        # A limpeza real acontece no início do script na próxima execução
                        # -------------------------------------------------------------

                    else:
                        # Caso de erro ao adicionar (ex: erro no DB)
                        st.error(f"❌ Erro ao registrar usuário: {msg}")

    st.markdown("---")

# --- Sidebar (Conteúdo fixo para todas as páginas) ---
with st.sidebar:
     # Adicionar o logo na sidebar também (opcional, mas comum)
     # Usa o mesmo tratamento de caminho da logo do cabeçalho principal (na raiz)
     # Assumindo que este script está em 'pages/' e a logo na raiz
     LOGO_FILE_NAME = "31121abd-f8d6-4d98-b07a-9de3735ea257.png" # Nome do arquivo da sua logo
     LOGO_PATH_ROOT_SIDEBAR = os.path.join("..", LOGO_FILE_NAME) # Tenta ../logo.png

     if os.path.exists(LOGO_PATH_ROOT_SIDEBAR):
         st.image(LOGO_PATH_ROOT_SIDEBAR, width=80) # Logo menor na sidebar
     elif os.path.exists(LOGO_FILE_NAME): # Tenta na raiz se o script for executado de lá por algum motivo
         st.image(LOGO_FILE_NAME, width=80)
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
     st.write("Versão: 1.0") # Exemplo de versão