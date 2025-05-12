# pages/3_📚_Banco_de_Dados.py

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


# --- Layout do cabeçalho (Consistência visual) ---
col_logo, col_title = st.columns([1, 4])

with col_logo:
    LOGO_PATH = "31121abd-f8d6-4d98-b07a-9de3735ea257.png"
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=80) # Logo um pouco menor nas páginas secundárias
    else:
        st.header("♻️") # Fallback icon

with col_title:
    st.title("Módulo Banco de Dados") # Título específico da página
    st.markdown("### Gerenciamento de Materiais")

st.markdown("---")

# --- Conteúdo da Seção de Banco de Dados de Materiais (Módulo de Materiais) ---
st.header("📚 Banco de Dados de Materiais")
st.markdown("Consulte, adicione, edite ou exclua informações sobre os tipos de plásticos recicláveis.")

# Sub-seção para adicionar novo material
with st.expander("➕ Adicionar Novo Material"):
    with st.form(key="add_material_form"):
        st.subheader("Formulário de Cadastro")
        novo_nome = st.text_input("Nome do Material:", key="add_nome")
        novo_densidade = st.number_input("Densidade (g/cm³):", min_value=0.0, format="%.2f", key="add_densidade")
        novo_temp_extrusao = st.text_input("Temperatura de Extrusão (°C):", placeholder="Ex: 220-250°C", key="add_temp")
        novo_eficiencia = st.number_input("Eficiência de Extrusão (0.0 a 1.0):", min_value=0.0, max_value=1.0,
                                          value=0.80, step=0.01, format="%.2f", key="add_eficiencia")
        col_add1, col_add2 = st.columns(2)
        with col_add1:
            novo_reciclavel = st.checkbox("É Reciclável", key="add_reciclavel")
        with col_add2:
            novo_biodegradavel = st.checkbox("É Biodegradável", key="add_biodegradavel")

        submit_button_add = st.form_submit_button(label="💾 Adicionar Material")

        if submit_button_add:
            if not novo_nome:
                st.error("O nome do material é obrigatório.")
            elif novo_densidade <= 0:
                st.error("A densidade deve ser um valor positivo.")
            elif novo_eficiencia <= 0 or novo_eficiencia > 1:
                st.error("A eficiência de extrusão deve estar entre 0.01 e 1.0.")
            else:
                sucesso, msg = database.adicionar_material(
                    novo_nome, novo_densidade, novo_temp_extrusao,
                    novo_reciclavel, novo_biodegradavel, novo_eficiencia
                )
                if sucesso:
                    st.success(f"✨ {msg}")
                    recarregar_materiais_e_rerun()
                else:
                    st.error(f"❌ {msg}")

nomes_materiais_consulta = st.session_state.get('nomes_materiais', [])
nomes_materiais_consulta_validos = [nome for nome in nomes_materiais_consulta if
                                    isinstance(nome, str) and nome != "Carregando..." and "(Erro DB)" not in nome]

if not nomes_materiais_consulta_validos:
    if not any("(Erro DB)" in nome for nome in nomes_materiais_consulta):
        st.info("Nenhum material disponível para consulta no momento ou falha ao carregar.")

if nomes_materiais_consulta_validos:
    material_selecionado_consulta = st.selectbox(
        "🔍 Selecione um material para ver/gerenciar detalhes:",
        options=nomes_materiais_consulta_validos,
        key="consulta_material_select",
        disabled=not bool(nomes_materiais_consulta_validos)
    )
    if material_selecionado_consulta and "(Erro DB)" not in material_selecionado_consulta:
        detalhes = database.buscar_detalhes_material(material_selecionado_consulta)
        if detalhes:
            st.subheader(f"Detalhes de **{detalhes.get('nome', 'N/A')}**:")

            col_db1, col_db2 = st.columns(2)
            with col_db1:
                densidade_val = detalhes.get('densidade_g_cm3', 'N/A')
                st.text(f"ID: {detalhes.get('id', 'N/A')}")
                st.text(f"Densidade: {densidade_val if densidade_val is not None else 'N/A'} g/cm³")
                st.text(
                    f"Temp. Extrusão: {detalhes.get('temp_extrusao_recomendada', 'N/A')} ")
            with col_db2:
                st.text(f"Reciclável: {'✅ Sim' if detalhes.get('reciclavel') else '❌ Não'}")
                st.text(f"Biodegradável: {'✅ Sim' if detalhes.get('biodegradavel') else '❌ Não'}")

            eficiencia_val = detalhes.get('eficiencia_extrusao', None)
            st.text(
                f"Eficiência de Extrusão Estimada: {eficiencia_val * 100:.0f}%" if eficiencia_val is not None else "N/A")

            # --- Seção de Edição e Exclusão ---
            st.markdown("---")
            st.subheader("Gerenciar Material Selecionado")

            with st.container():
                if st.button(f"🗑️ Excluir Material '{detalhes.get('nome')}'", key=f"delete_btn_{detalhes.get('id')}"):
                    st.session_state.material_para_excluir_id = detalhes.get('id')
                    st.session_state.material_para_excluir_nome = detalhes.get('nome')

                if 'material_para_excluir_id' in st.session_state and st.session_state.material_para_excluir_id == detalhes.get(
                        'id'):
                    st.warning(
                        f"⚠️ Tem certeza que deseja excluir o material **{st.session_state.material_para_excluir_nome}** (ID: {st.session_state.material_para_excluir_id})? Esta ação não pode ser desfeita.")
                    col_confirm_del1, col_confirm_del2, _ = st.columns([1, 1, 3])
                    with col_confirm_del1:
                        if st.button("👍 Confirmar Exclusão", key="confirm_delete"):
                            sucesso, msg = database.excluir_material(st.session_state.material_para_excluir_id)
                            if sucesso:
                                st.success(f"✅ {msg}")
                                del st.session_state.material_para_excluir_id
                                if 'material_para_excluir_nome' in st.session_state: del st.session_state.material_para_excluir_nome
                                recarregar_materiais_e_rerun()
                            else:
                                st.error(f"❌ {msg}")
                    with col_confirm_del2:
                        if st.button("👎 Cancelar", key="cancel_delete"):
                            del st.session_state.material_para_excluir_id
                            if 'material_para_excluir_nome' in st.session_state: del st.session_state.material_para_excluir_nome
                            st.rerun()

            with st.expander(f"✏️ Editar Material '{detalhes.get('nome')}'"):
                with st.form(key=f"edit_material_form_{detalhes.get('id')}"):
                    st.subheader("Formulário de Edição")
                    edit_nome = st.text_input("Nome do Material:", value=detalhes.get('nome'),
                                              key=f"edit_nome_{detalhes.get('id')}")
                    edit_densidade = st.number_input("Densidade (g/cm³):",
                                                     value=float(detalhes.get('densidade_g_cm3', 0.0)), min_value=0.0,
                                                     format="%.2f", key=f"edit_densidade_{detalhes.get('id')}")
                    edit_temp_extrusao = st.text_input("Temperatura de Extrusão (°C):",
                                                       value=detalhes.get('temp_extrusao_recomendada', ''),
                                                       placeholder="Ex: 220-250°C",
                                                       key=f"edit_temp_{detalhes.get('id')}")
                    edit_eficiencia = st.number_input("Eficiência de Extrusão (0.0 a 1.0):",
                                                      value=float(detalhes.get('eficiencia_extrusao', 0.0)),
                                                      min_value=0.0, max_value=1.0, step=0.01, format="%.2f",
                                                      key=f"edit_eficiencia_{detalhes.get('id')}")

                    col_edit1, col_edit2 = st.columns(2)
                    with col_edit1:
                        edit_reciclavel = st.checkbox("É Reciclável", value=bool(detalhes.get('reciclavel')),
                                                      key=f"edit_reciclavel_{detalhes.get('id')}")
                    with col_edit2:
                        edit_biodegradavel = st.checkbox("É Biodegradável", value=bool(detalhes.get('biodegradavel')),
                                                         key=f"edit_biodegradavel_{detalhes.get('id')}")

                    submit_button_edit = st.form_submit_button(label="💾 Salvar Alterações")

                    if submit_button_edit:
                        if not edit_nome:
                            st.error("O nome do material é obrigatório.")
                        elif edit_densidade <= 0:
                            st.error("A densidade deve ser um valor positivo.")
                        elif edit_eficiencia <= 0 or edit_eficiencia > 1:
                            st.error("A eficiência de extrusão deve estar entre 0.01 e 1.0.")
                        else:
                            sucesso, msg = database.atualizar_material(
                                detalhes.get('id'), edit_nome, edit_densidade, edit_temp_extrusao,
                                edit_reciclavel, edit_biodegradavel, edit_eficiencia
                            )
                            if sucesso:
                                st.success(f"✨ {msg}")
                                recarregar_materiais_e_rerun()
                            else:
                                st.error(f"❌ {msg}")
        else:
            st.warning(f"Detalhes não encontrados para {material_selecionado_consulta}.")

st.markdown("---")

# --- Sidebar (Apenas a parte 'Sobre') ---
with st.sidebar:
     st.header("🌱 Sobre EchoFio AI")
     st.info(
         "EchoFio AI é um protótipo que integra a identificação de plásticos "
         "recicl\u00E1veis por imagem com a simula\u00E7\u00E3o da produ\u00E7\u00E3o de filamentos para impress\u00E3o 3D, "
         "promovendo a economia circular e a sustentabilidade."
     )
     st.markdown("---")
     st.caption("EchoFio AI Protótipo v0.8.1")