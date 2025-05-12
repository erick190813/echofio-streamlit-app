# pages/1_🔬_Identificação.py

import streamlit as st
import database
import pandas as pd
import random
import time
import math
import os # Para verificar a existência do arquivo de logo

# --- Configuração da página (Remover st.set_page_config se estiver no script principal) ---
# Removendo st.set_page_config daqui.

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
    st.title("Módulo de Identificação") # Título específico da página
    st.markdown("### EchoScan")

st.markdown("---")

# --- Conteúdo da Seção de Upload de Imagem (Módulo EchoScan) ---
st.header("🔬 Identificação de Plásticos (EchoScan)")
st.markdown("Carregue a imagem do resíduo plástico para identificação.")

uploaded_file = st.file_uploader("Escolha uma imagem:", type=["jpg", "jpeg", "png"],
                                 key="echo_scan_uploader", label_visibility="collapsed")

if uploaded_file is not None:
    with st.container(border=True):
        st.image(uploaded_file, caption=f"Imagem carregada: {uploaded_file.name}", use_column_width=True)
        st.info(f"Arquivo '{uploaded_file.name}' carregado com sucesso.")

        if st.button("Analisar Imagem", key="analisar_img_btn"):
            with st.spinner("Analisando imagem... Por favor, aguarde."):
                time.sleep(1.5) # Simula processamento

                filename_lower = uploaded_file.name.lower()
                sugestao_plastico_keyword = None

                if any(keyword in filename_lower for keyword in ["pet", "garrafa", "bottle"]):
                    sugestao_plastico_keyword = "PET"
                elif any(keyword in filename_lower for keyword in ["abs", "lego", "encaixe", "bloco"]):
                    sugestao_plastico_keyword = "ABS"
                elif any(keyword in filename_lower for keyword in ["milho", "amido", "corn"]):
                    sugestao_plastico_keyword = "PLA"
                elif "pla" in filename_lower:
                    if "plástico" not in filename_lower and "plastico" not in filename_lower:
                        sugestao_plastico_keyword = "PLA"

                nomes_disponiveis = st.session_state.get('nomes_materiais', [])
                nomes_validos = [nome for nome in nomes_disponiveis if
                                 isinstance(nome, str) and nome != "Carregando..." and "(Erro DB)" not in nome]

                if not nomes_validos:
                    st.warning("Lista de materiais do banco de dados parece vazia ou inválida. Usando fallback.")
                    nomes_validos = ["PET", "PLA", "ABS"]

                plastico_identificado_final = None
                metodo_identificacao_final = "Aleatório (Simulado)"

                if sugestao_plastico_keyword:
                    for nome_material_db in nomes_validos:
                        if nome_material_db.lower() == sugestao_plastico_keyword.lower():
                            plastico_identificado_final = nome_material_db
                            metodo_identificacao_final = "Nome do Arquivo"
                            break

                if not plastico_identificado_final:
                    if nomes_validos:
                        plastico_identificado_final = random.choice(nomes_validos)
                    else:
                        plastico_identificado_final = "N/A"
                        metodo_identificacao_final = "Falha na Identificação (sem materiais válidos)"

                st.session_state.plastico_identificado_scan = plastico_identificado_final
                st.session_state.metodo_identificacao_scan = metodo_identificacao_final

            if st.session_state.plastico_identificado_scan != "N/A":
                st.success(
                    f"✅ Resultado da Análise (Simulação): Plástico identificado como **{st.session_state.plastico_identificado_scan}** (Método: {st.session_state.metodo_identificacao_scan}).")
                st.info("Este resultado será pré-selecionado no módulo de simulação abaixo.")
            else:
                st.error("❌ Não foi possível identificar o plástico. Tente novamente ou verifique os materiais cadastrados.")

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