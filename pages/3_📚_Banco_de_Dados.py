# pages/3_📚_Banco_de_Dados.py - CORRIGIDO (Input Eficiência/Perda)

import streamlit as st
import database
import pandas as pd
import os # Para verificar a existência do arquivo de logo

# --- Configuração da página (Remover st.set_page_config se estiver no script principal) ---
# Removendo st.set_page_config daqui.

# Função auxiliar para recarregar nomes de materiais e forçar rerun (Mantida)
def recarregar_materiais_e_rerun():
    """Recarrega os nomes dos materiais do banco de dados e reinicia o script do Streamlit."""
    nomes_db = database.buscar_nomes_materiais()
    st.session_state.nomes_materiais = list(nomes_db) if nomes_db else []
    st.rerun()

# --- Verifica se o usuário está logado ---
if not st.session_state.get('logged_in', False):
    st.warning("🔒 Por favor, faça login para acessar este módulo.")
    st.stop() # Interrompe a execução desta página se não estiver logado

# --- Carrega Privilégios do Usuário Logado ---
# Assume que os privilégios foram carregados na sessão durante o login (Login.py)
user_privileges = st.session_state.get('user_privileges', {"can_edit_db": False, "is_admin": False})
pode_editar_db = user_privileges.get("can_edit_db", False)
eh_admin = user_privileges.get("is_admin", False)


# --- Layout do cabeçalho (Consistência visual) ---
# Assume que o arquivo da logo está na raiz do seu projeto. Ajuste o caminho se necessário.
LOGO_FILE_NAME = "31121abd-f8d6-4d98-b07a-9de3735ea257.png" # Nome do arquivo da sua logo
# Tenta encontrar o caminho da logo relativo à pasta 'pages'
LOGO_PATH_RELATIVE = os.path.join("..", LOGO_FILE_NAME) # Tenta ../logo.png

col_logo, col_title = st.columns([1, 4])

with col_logo:
    # Verifica qual caminho da logo existe e exibe
    if os.path.exists(LOGO_PATH_RELATIVE):
        st.image(LOGO_PATH_RELATIVE, width=80)
    else:
        st.header("♻️") # Ícone de fallback se a logo não for encontrada

with col_title:
    st.title("📚 Módulo de Banco de Dados") # Título específico da página
    st.markdown("### Consulta e Gerenciamento de Materiais")

st.markdown("---")


# --- Gerenciamento de Materiais (Permitido APENAS para usuários com 'can_edit_db') ---

# Verifica se o usuário logado tem permissão para editar o BD
if pode_editar_db:
    st.subheader("Gerenciar Materiais no Banco de Dados")

    tab1, tab2, tab3 = st.tabs(["Adicionar Material", "Consultar/Editar Material", "Excluir Material"])

    with tab1:
        st.subheader("➕ Adicionar Novo Material")
        with st.form("adicionar_material_form"):
            nome = st.text_input("Nome do Material", help="Nome único para identificar o material (Ex: PET, PP, ABS).")
            densidade = st.number_input("Densidade (g/cm³)", min_value=0.0, format="%.3f", help="Densidade do material em gramas por centímetro cúbico.")
            temp_extrusao = st.number_input("Temperatura de Extrusão (°C)", min_value=0.0, format="%.1f", help="Temperatura recomendada para extrusão do filamento deste material.")
            col_bool1, col_bool2 = st.columns(2)
            with col_bool1:
                 reciclavel = st.checkbox("Reciclável?", value=True, help="Marque se este material é comumente reciclável no processo ECHOFIO.")
            with col_bool2:
                 biodegradavel = st.checkbox("Biodegradável?", value=False, help="Marque se este material é biodegradável.")

            # --- MUDANÇA AQUI: Removido max_value=100.0 ---
            eficiencia = st.number_input("Eficiência de Processo (%)", min_value=0.0, format="%.2f", help="Eficiência estimada na conversão deste material para filamento (Ex: 85.5 para 85.5%).")
            perda_percentual = st.number_input("Perda no Processo (%)", min_value=0.0, format="%.2f", help="Perda percentual esperada durante o processo (Ex: 10.0 para 10.0%).")
            # --------------------------------------------

            consumo_energia_kwh_por_kg = st.number_input("Consumo de Energia (kWh/kg)", min_value=0.0, format="%.3f", help="Consumo médio de energia em kWh para processar 1 kg deste material.")

            adicionar_button = st.form_submit_button("Adicionar Material")

            if adicionar_button:
                # Validação básica (mantida a validação de >= 0)
                if not nome or densidade <= 0 or temp_extrusao <= 0 or eficiencia < 0 or perda_percentual < 0 or consumo_energia_kwh_por_kg < 0:
                    st.error("Por favor, preencha todos os campos obrigatórios com valores válidos.")
                else:
                    # Converte booleanos de Streamlit (True/False) para 1/0 para o SQLite
                    reciclavel_db = 1 if reciclavel else 0
                    biodegradavel_db = 1 if biodegradavel else 0

                    sucesso, msg = database.adicionar_material(
                        nome.strip(), densidade, temp_extrusao, reciclavel_db, biodegradavel_db,
                        eficiencia, perda_percentual, consumo_energia_kwh_por_kg
                    )
                    if sucesso:
                        st.success(f"✅ {msg}")
                        recarregar_materiais_e_rerun() # Recarrega a lista na sessão e força o rerun
                    else:
                        st.error(f"❌ {msg}")

    with tab2:
        st.subheader("✏️ Consultar ou Editar Material Existente")
        # Assume que st.session_state.nomes_materiais está preenchido do echofio_app.py
        nomes_materiais_disponiveis = ["-- Selecione --"] + st.session_state.nomes_materiais

        material_selecionado_nome = st.selectbox(
            "Selecione o Material para Consultar/Editar:",
            nomes_materiais_disponiveis,
            key='material_selecionado_consulta' # Chave para manter o estado
        )

        material_para_editar = None
        if material_selecionado_nome and material_selecionado_nome != "-- Selecione --":
            material_para_editar = database.buscar_material_por_nome(material_selecionado_nome)

            if material_para_editar:
                st.markdown("#### Dados Atuais:")
                # Exibir dados atuais (somente leitura ou em campos desabilitados visualmente)
                # ou pré-preencher o formulário de edição abaixo
                # Vamos usar um formulário pré-preenchido

                st.markdown("#### Editar Dados:")
                with st.form("editar_material_form"):
                    # Pré-preenche os campos com os dados do material selecionado
                    edit_nome = st.text_input("Nome do Material", value=material_para_editar['nome'], key='edit_nome')
                    edit_densidade = st.number_input("Densidade (g/cm³)", min_value=0.0, format="%.3f", value=material_para_editar['densidade'], key='edit_densidade')
                    edit_temp_extrusao = st.number_input("Temperatura de Extrusão (°C)", min_value=0.0, format="%.1f", value=material_para_editar['temp_extrusao'], key='edit_temp_extrusao')
                    col_edit_bool1, col_edit_bool2 = st.columns(2)
                    with col_edit_bool1:
                         edit_reciclavel = st.checkbox("Reciclável?", value=bool(material_para_editar['reciclavel']), key='edit_reciclavel') # Converte 1/0 para True/False
                    with col_edit_bool2:
                         edit_biodegradavel = st.checkbox("Biodegradável?", value=bool(material_para_editar['biodegradavel']), key='edit_biodegradavel') # Converte 1/0 para True/False

                    # --- MUDANÇA AQUI: Removido max_value=100.0 ---
                    edit_eficiencia = st.number_input("Eficiência de Processo (%)", min_value=0.0, format="%.2f", value=material_para_editar['eficiencia'], key='edit_eficiencia')
                    edit_perda_percentual = st.number_input("Perda no Processo (%)", min_value=0.0, format="%.2f", value=material_para_editar['perda_percentual'], key='edit_perda_percentual')
                    # --------------------------------------------

                    edit_consumo_energia_kwh_por_kg = st.number_input("Consumo de Energia (kWh/kg)", min_value=0.0, format="%.3f", value=material_para_editar['consumo_energia_kwh_por_kg'], key='edit_consumo_energia_kwh_por_kg')

                    editar_button = st.form_submit_button("Salvar Alterações")

                    if editar_button:
                        # Validação básica (mantida a validação de >= 0)
                         if not edit_nome or edit_densidade <= 0 or edit_temp_extrusao <= 0 or edit_eficiencia < 0 or edit_perda_percentual < 0 or edit_consumo_energia_kwh_por_kg < 0:
                             st.error("Por favor, preencha todos os campos obrigatórios com valores válidos.")
                         else:
                            # Converte booleanos de Streamlit (True/False) para 1/0 para o SQLite
                            edit_reciclavel_db = 1 if edit_reciclavel else 0
                            edit_biodegradavel_db = 1 if edit_biodegradavel else 0

                            sucesso, msg = database.atualizar_material(
                                material_para_editar['id'], edit_nome.strip(), edit_densidade, edit_temp_extrusao,
                                edit_reciclavel_db, edit_biodegradavel_db, edit_eficiencia, edit_perda_percentual,
                                edit_consumo_energia_kwh_por_kg
                            )
                            if sucesso:
                                st.success(f"✅ {msg}")
                                # Recarrega a lista de nomes caso o nome tenha mudado
                                recarregar_materiais_e_rerun()
                            else:
                                st.error(f"❌ {msg}")
            else:
                 st.warning("Material não encontrado no banco de dados.") # Caso raro, mas possível
        elif material_selecionado_nome == "-- Selecione --":
             st.info("Selecione um material acima para ver ou editar seus detalhes.")

    with tab3:
        st.subheader("🗑️ Excluir Material Existente")
        # Assume que st.session_state.nomes_materiais está preenchido
        nomes_materiais_excluir = ["-- Selecione --"] + st.session_state.nomes_materiais

        material_selecionado_excluir_nome = st.selectbox(
            "Selecione o Material para Excluir:",
            nomes_materiais_excluir,
            key='material_selecionado_excluir' # Chave para manter o estado
        )

        material_para_excluir = None
        if material_selecionado_excluir_nome and material_selecionado_excluir_nome != "-- Selecione --":
            material_para_excluir = database.buscar_material_por_nome(material_selecionado_excluir_nome)

            if material_para_excluir:
                st.warning(f"Tem certeza que deseja excluir o material: **{material_para_excluir['nome']}**?")
                if st.button(f"Confirmar Exclusão de {material_para_excluir['nome']}", key='confirmar_exclusao'):
                    sucesso, msg = database.excluir_material(material_para_excluir['id'])
                    if sucesso:
                        st.success(f"✅ {msg}")
                        # Limpa a seleção e recarrega a lista de nomes
                        st.session_state.material_selecionado_excluir = "-- Selecione --" # Reseta o selectbox
                        recarregar_materiais_e_rerun() # Recarrega lista e força rerun
                    else:
                        st.error(f"❌ {msg}")
            elif material_selecionado_excluir_nome != "-- Selecione --":
                 st.warning("Material não encontrado no banco de dados para exclusão.")
        elif material_selecionado_excluir_nome == "-- Selecione --":
             st.info("Selecione um material acima para excluí-lo.")

else:
    # Mensagem mostrada se o usuário NÃO tiver permissão de edição
    st.warning("Você não tem permissão para modificar o banco de dados de materiais.")
    st.info("Por favor, entre em contato com um administrador caso precise solicitar permissão de edição.")


st.markdown("---")

# --- Consulta Geral de Materiais (Disponível para todos os usuários logados) ---
st.subheader("📋 Lista de Todos os Materiais Cadastrados")

todos_materiais = database.buscar_todos_materiais()

if todos_materiais:
    # Converte a lista de Row objects para DataFrame do Pandas para exibição fácil
    df_materiais = pd.DataFrame(todos_materiais)
    # Opcional: Ocultar colunas de ID se não forem relevantes para exibição geral
    # if 'id' in df_materiais.columns:
    #     df_materiais = df_materiais.drop(columns=['id'])
    # Converte 1/0 para Sim/Não ou True/False para melhor leitura
    if 'reciclavel' in df_materiais.columns:
        df_materiais['reciclável'] = df_materiais['reciclavel'].apply(lambda x: 'Sim' if x else 'Não')
        df_materiais = df_materiais.drop(columns=['reciclavel']) # Oculta a coluna original
    if 'biodegradavel' in df_materiais.columns:
        df_materiais['biodegradável'] = df_materiais['biodegradavel'].apply(lambda x: 'Sim' if x else 'Não')
        df_materiais = df_materiais.drop(columns=['biodegradavel']) # Oculta a coluna original

    st.dataframe(df_materiais, use_container_width=True)
else:
    st.info("Nenhum material cadastrado no banco de dados ainda.")


st.markdown("---")


# --- Gerenciamento de Permissões de Usuários (Permitido APENAS para usuários com 'is_admin') ---
# Esta seção é para o usuário administrador gerenciar quem pode editar o BD de materiais.

if eh_admin:
    st.subheader("👑 Gerenciar Permissões de Edição do Banco de Dados")
    st.info("Como administrador, você pode conceder ou remover a permissão de edição do banco de dados de materiais para outros usuários.")

    todos_usuarios = database.buscar_todos_usuarios_basico()

    if todos_usuarios:
        st.write("Usuários Registrados:")

        # Usar um formulário para agrupar as atualizações de permissão
        with st.form("gerenciar_permissoes_form"):
             st.write("Marque a caixa 'Permite Editar BD' para conceder ou desmarque para remover a permissão.")

             updates = {} # Dicionário para armazenar as alterações (user_id: novo_status)

             # Exibe cada usuário e um checkbox para a permissão
             for user in todos_usuarios:
                 # Não permite alterar a permissão do próprio usuário administrador principal (erick19082013) por segurança
                 if user['username'] == database.ADMIN_USERNAME:
                      st.write(f"**{user['username']}** (Administrador Principal - Permissão de Edição Sempre Ativa)")
                      # Não coloca checkbox para o admin principal
                 else:
                     # Cria um checkbox para cada usuário
                     novo_status_edicao = st.checkbox(
                         f"Usuário: **{user['username']}**",
                         value=bool(user['can_edit_db']), # Valor inicial do checkbox
                         key=f"checkbox_edit_{user['id']}", # Chave única para o estado do checkbox
                         help=f"Conceder ou remover permissão para editar o banco de dados de materiais para '{user['username']}'."
                     )

                     # Se o novo status for diferente do status original, armazena para atualização
                     if novo_status_edicao != bool(user['can_edit_db']):
                         updates[user['id']] = novo_status_edicao # Armazena a alteração pendente

             salvar_permissoes_button = st.form_submit_button("Salvar Alterações nas Permissões")

             if salvar_permissoes_button:
                 if updates:
                     st.write("Aplicando alterações...")
                     total_sucesso = 0
                     total_falha = 0
                     mensagens_falha = []

                     for user_id, novo_status in updates.items():
                         sucesso_update, msg_update = database.atualizar_privilegio_edicao_db(user_id, novo_status)
                         if sucesso_update:
                             total_sucesso += 1
                         else:
                             total_falha += 1
                             mensagens_falha.append(f"Falha para usuário ID {user_id}: {msg_update}")

                     if total_sucesso > 0:
                         st.success(f"✅ {total_sucesso} permissão(ões) atualizada(s) com sucesso.")
                     if total_falha > 0:
                         st.error(f"❌ {total_falha} permissão(ões) falhou(ram) ao atualizar:")
                         for msg_falha in mensagens_falha:
                             st.write(f"- {msg_falha}")

                     # Força o rerun para recarregar a lista de usuários com os status atualizados
                     # E garante que o próprio admin logado tenha seus privilégios atualizados na sessão (caso mude a si mesmo, embora o checkbox dele não apareça aqui)
                     st.session_state.user_privileges = database.buscar_privilegios_usuario(st.session_state.username) # Recarrega os privilégios do admin
                     st.rerun() # Recarrega a página para exibir os novos status


                 else:
                     st.info("Nenhuma alteração de permissão pendente para salvar.")

        if not todos_usuarios:
             st.info("Nenhum usuário registrado ainda, exceto o administrador principal.")

else:
    # Mensagem mostrada se o usuário NÃO for administrador principal
    st.info("Você não tem permissão para gerenciar as permissões de outros usuários.")


st.markdown("---")


# --- Sidebar (Conteúdo fixo para todas as páginas) ---
with st.sidebar:
     # Adicionar o logo na sidebar também (opcional, mas comum)
     # Usa o mesmo tratamento de caminho da logo do cabeçalho principal (na raiz)
     # Assumindo que este script está em 'pages/' e a logo na raiz
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