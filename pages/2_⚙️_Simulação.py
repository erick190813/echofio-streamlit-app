# pages/2_⚙️_Simulação.py

import streamlit as st
import database
import pandas as pd
import random
import time
import math
import os # Para verificar a existência do arquivo de logo

# --- Configuração da página (Remover st.set_page_config se estiver no script principal) ---
# Removendo st.set_page_config daqui.

# Constantes (Manter se usadas apenas nesta página ou mover para um arquivo de constantes global se usadas em várias)
DIAMETRO_FILAMENTO_MM = 1.75
DIAMETRO_FILAMENTO_M = DIAMETRO_FILAMENTO_MM / 1000
RAIO_FILAMENTO_M = DIAMETRO_FILAMENTO_M / 2
AREA_SECAO_FILAMENTO_M2 = math.pi * (RAIO_FILAMENTO_M ** 2)


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
    st.title("Módulo de Simulação") # Título específico da página
    st.markdown("### Simulação de Produção")

st.markdown("---")


# --- Conteúdo da Seção de Simulação de Produção (Módulo de Simulação) ---
st.header("⚙️ Simulação de Produção de Filamento")
st.markdown("Estime a quantidade de filamento 3D que pode ser produzida a partir de uma dada quantidade de matéria-prima plástica.")

col1_sim, col2_sim = st.columns(2)

with col1_sim:
    st.subheader("Entrada de Dados")

    nomes_materiais_db_list = st.session_state.get('nomes_materiais', [])
    nomes_materiais_db_list_validos = [nome for nome in nomes_materiais_db_list if
                                       isinstance(nome, str) and nome != "Carregando..." and "(Erro DB)" not in nome]
    if not nomes_materiais_db_list_validos:
        nomes_materiais_db_list_validos = ["PET", "PLA", "ABS"] # Fallback

    index_selecionado = 0
    plastico_pre_selecionado = st.session_state.get('plastico_identificado_scan')

    if plastico_pre_selecionado and plastico_pre_selecionado != "N/A" and plastico_pre_selecionado in nomes_materiais_db_list_validos:
        try:
            index_selecionado = nomes_materiais_db_list_validos.index(plastico_pre_selecionado)
        except ValueError:
            index_selecionado = 0

    tipo_plastico_sim = st.selectbox(
        "Selecione o tipo de plástico:",
        options=nomes_materiais_db_list_validos,
        key="sim_plastico",
        index=index_selecionado,
        disabled=not bool(nomes_materiais_db_list_validos) or any(
            "(Erro DB)" in opt for opt in nomes_materiais_db_list_validos)
    )
    materia_prima_kg = st.number_input("Quantidade de matéria-prima (kg):", min_value=0.1, value=1.0, step=0.1,
                                       key="sim_materia_prima")

    with st.container():
         if st.button("✨ Simular Produção de Filamento", key="sim_botao",
                      disabled=not tipo_plastico_sim or "(Erro DB)" in tipo_plastico_sim):
             if tipo_plastico_sim and tipo_plastico_sim != "Carregando..." and "(Erro DB)" not in tipo_plastico_sim:
                 detalhes_material_sim = database.buscar_detalhes_material(tipo_plastico_sim)

                 detalhes_validos = False
                 if not detalhes_material_sim:
                     st.error(f"Não foi possível buscar detalhes para '{tipo_plastico_sim}' no banco de dados.")
                 elif 'eficiencia_extrusao' not in detalhes_material_sim or detalhes_material_sim[
                     'eficiencia_extrusao'] is None:
                     st.warning(f"Eficiência de extrusão não encontrada para '{tipo_plastico_sim}'. Verifique o BD.")
                 elif 'densidade_g_cm3' not in detalhes_material_sim or detalhes_material_sim['densidade_g_cm3'] is None:
                     st.warning(f"Densidade não encontrada para '{tipo_plastico_sim}'. Verifique o BD.")
                 else:
                     detalhes_validos = True

                 if detalhes_validos:
                     eficiencia = detalhes_material_sim['eficiencia_extrusao']
                     densidade_g_cm3 = detalhes_material_sim['densidade_g_cm3']

                     filamento_produzido_kg = materia_prima_kg * eficiencia

                     comprimento_filamento_m = 0
                     if densidade_g_cm3 > 0:
                         densidade_kg_m3 = densidade_g_cm3 * 1000
                         volume_filamento_m3 = filamento_produzido_kg / densidade_kg_m3
                         if AREA_SECAO_FILAMENTO_M2 > 0:
                             comprimento_filamento_m = volume_filamento_m3 / AREA_SECAO_FILAMENTO_M2
                     else:
                         st.warning(
                             f"Densidade inválida (n\u00E3o positiva) para {tipo_plastico_sim} no banco de dados. Comprimento n\u00E3o calculado.")

                     st.session_state.filamento_produzido = filamento_produzido_kg
                     st.session_state.comprimento_filamento = comprimento_filamento_m
                     st.session_state.plastico_simulado = tipo_plastico_sim
                     st.session_state.eficiencia_usada = eficiencia
                     st.session_state.materia_prima_usada = materia_prima_kg
                 else:
                     st.error(
                         f"Simulação não pôde ser concluída devido a dados ausentes ou inválidos para {tipo_plastico_sim}. Verifique o banco de dados.")
                     st.session_state.filamento_produzido = 0
                     st.session_state.comprimento_filamento = 0
                     st.session_state.plastico_simulado = tipo_plastico_sim
                     if 'eficiencia_usada' in st.session_state: del st.session_state.eficiencia_usada
                     if 'materia_prima_usada' in st.session_state: del st.session_state.materia_prima_usada
             else:
                  st.warning("Selecione um tipo de plástico válido para simular.")


with col2_sim:
    st.subheader("Resultados")
    if 'filamento_produzido' in st.session_state and 'plastico_simulado' in st.session_state:
        plastico_simulado_nome = st.session_state.plastico_simulado

        if st.session_state.filamento_produzido > 0 or ('materia_prima_usada' in st.session_state):
            st.metric(
                label=f"Filamento de {plastico_simulado_nome} estimado",
                value=f"{st.session_state.filamento_produzido:.2f} kg"
            )
            if 'comprimento_filamento' in st.session_state and st.session_state.comprimento_filamento > 0:
                st.metric(
                    label=f"Comprimento estimado (Ø{DIAMETRO_FILAMENTO_MM}mm)",
                    value=f"{st.session_state.comprimento_filamento:.2f} metros"
                )
            elif 'comprimento_filamento' in st.session_state and st.session_state.comprimento_filamento == 0 and st.session_state.filamento_produzido > 0:
                st.info(
                    f"Comprimento do filamento não pôde ser calculado (verifique a densidade do material {plastico_simulado_nome} no BD).")

            if 'eficiencia_usada' in st.session_state:
                st.caption(f"Eficiência de extrusão considerada: {st.session_state.eficiencia_usada * 100:.0f}%")

            st.success("👍 Simulação concluída com sucesso!")

            if 'materia_prima_usada' in st.session_state and st.session_state.filamento_produzido >= 0:
                try:
                    chart_data = pd.DataFrame(
                        {
                            "Etapa": ["Matéria-prima", "Filamento Estimado"],
                            "Quantidade (kg)": [st.session_state.materia_prima_usada,
                                                st.session_state.filamento_produzido]
                        }
                    )
                    st.bar_chart(chart_data.set_index("Etapa"))
                except Exception as e:
                    st.warning(f"Não foi possível gerar o gráfico dos resultados: {e}")
        elif 'plastico_simulado' in st.session_state and st.session_state.filamento_produzido == 0 and not (
                'materia_prima_usada' in st.session_state):
            st.warning(
                f"Simulação para {plastico_simulado_nome} resultou em 0kg de filamento ou falhou devido a dados ausentes. Verifique as entradas e o banco de dados.")
    else:
        st.info("Preencha os dados à esquerda e clique em 'Simular Produção' para ver os resultados.")

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