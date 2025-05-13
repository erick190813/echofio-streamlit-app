# pages/2_⚙️_Simulação.py - CORRIGIDO (Formatação Eficiência/Perda)

import streamlit as st
import database
import pandas as pd
import random # Mantido caso haja alguma lógica de simulação aleatória
import time # Mantido caso haja delays simulados
import math # Essencial para cálculos de volume/peso
import os # Para verificar a existência do arquivo de logo
import plotly.express as px # Importar Plotly Express para gráficos

# --- Configuração da página (Remover st.set_page_config se estiver no script principal) ---
# Removendo st.set_page_config daqui. A configuração global deve estar em echofio_app.py.

# Constantes do Filamento (Mantidas, certifique-se que o diâmetro está correto para seus filamentos)
DIAMETRO_FILAMENTO_MM = 1.75 # Diâmetro comum para filamento 3D
DIAMETRO_FILAMENTO_M = DIAMETRO_FILAMENTO_MM / 1000 # Convertendo para metros
RAIO_FILAMENTO_M = DIAMETRO_FILAMENTO_M / 2 # Raio em metros
AREA_SECAO_FILAMENTO_M2 = math.pi * (RAIO_FILAMENTO_M ** 2) # Área da seção transversal do filamento em m²

# --- Verifica se o usuário está logado ---
if not st.session_state.get('logged_in', False):
    st.warning("🔒 Por favor, faça login para acessar este módulo.")
    st.stop() # Interrompe a execução desta página se não estiver logado

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
    st.title("⚙️ Módulo de Simulação") # Título específico da página
    st.markdown("### Estime a Produção de Filamento") # Subtítulo

st.markdown("---") # Linha divisória

# --- Formulário de Simulação ---

st.subheader("Dados para Simulação")

# Assume que st.session_state.nomes_materiais está preenchido do echofio_app.py
# Se não estiver (erro na inicialização do DB), buscar agora, mas isso pode ocultar o erro original.
# É melhor depender do st.session_state preenchido pelo app principal.
nomes_materiais_disponiveis = st.session_state.get('nomes_materiais', [])

if not nomes_materiais_disponiveis:
    st.warning("⚠️ Nenhum material encontrado no banco de dados. Por favor, cadastre materiais primeiro.")
    # Mesmo sem materiais, o formulário pode aparecer para input manual, se essa for a intenção.


# Seletor de Material
material_selecionado_nome = st.selectbox(
    "Selecione o Material:",
    ["-- Selecione --"] + nomes_materiais_disponiveis, # Adiciona opção de seleção
    index=0, # Começa com "-- Selecione --"
    help="Selecione o tipo de material plástico a ser simulado."
)

# Se o material selecionado for válido (não "-- Selecione --"), buscar detalhes para simulação
detalhes_material = None
if material_selecionado_nome and material_selecionado_nome != "-- Selecione --":
    detalhes_material = database.buscar_material_por_nome(material_selecionado_nome)

    if detalhes_material:
        st.markdown("#### Dados do Material Selecionado:")
        st.info(f"""
            **Densidade:** {detalhes_material['densidade']:.3f} g/cm³
            **Temp. Extrusão:** {detalhes_material['temp_extrusao']:.1f} °C
            **Eficiência Estimada:** {detalhes_material['eficiencia']:.1f}%  
            **Perda Estimada:** {detalhes_material['perda_percentual']:.1f}% 
            **Consumo de Energia (por kg):** {detalhes_material['consumo_energia_kwh_por_kg']:.3f} kWh/kg
        """)
    else:
         st.warning(f"Detalhes para o material '{material_selecionado_nome}' não encontrados no banco de dados.") # Material selecionado no selectbox mas não encontrado no DB?

# Input da Quantidade
st.markdown("---")
st.subheader("Quantidade de Material")

with st.form("simulacao_quantidade_form"):
    st.write("Insira a quantidade de material plástico que você deseja simular o processamento.")

    quantidade_input = st.number_input(
        "Quantidade:",
        min_value=0.0,
        step=0.1,
        format="%.2f",
        help="Quantidade de material plástico (em kg) a ser processado para virar filamento."
    )

    simular_button = st.form_submit_button("Simular Produção")


# --- Lógica da Simulação ---

# Dicionário para armazenar os resultados da simulação na sessão
if 'simulacao_resultados' not in st.session_state:
    st.session_state.simulacao_resultados = None

if simular_button:
    if quantidade_input <= 0:
        st.warning("Por favor, insira uma quantidade de material maior que zero para simular.")
        st.session_state.simulacao_resultados = None # Limpa resultados anteriores se input for inválido
    elif not detalhes_material:
         st.warning("Por favor, selecione um material válido do banco de dados para simular.")
         st.session_state.simulacao_resultados = None # Limpa resultados anteriores
    else:
        # Recupera os detalhes do material selecionado
        densidade = detalhes_material['densidade']
        eficiencia_percentual = detalhes_material['eficiencia'] # Vem em % (0-100)
        perda_percentual = detalhes_material['perda_percentual'] # Vem em % (0-100)
        consumo_energia_por_kg = detalhes_material['consumo_energia_kwh_por_kg'] # kWh por kg de input

        # Converte eficiência para fator decimal (0-1)
        # Aqui, consideramos a 'eficiência' do DB como o fator de conversão LÍQUIDO (já considerando perdas típicas).
        eficiencia_fator = eficiencia_percentual / 100.0

        # Cálculo da quantidade de filamento produzido
        quantidade_filamento_produzido_kg = quantidade_input * eficiencia_fator # Ex: 10kg * 0.8 = 8kg


        # Cálculo do comprimento do filamento
        # Volume total do filamento (m³) = Massa (kg) / Densidade (kg/m³)
        # Densidade está em g/cm³, converter para kg/m³: Densidade (g/cm³) * 1000
        densidade_kg_m3 = densidade * 1000
        # Garante que a densidade não é zero para evitar divisão por zero
        volume_filamento_m3 = 0
        comprimento_filamento_m = 0
        if densidade_kg_m3 > 0:
            volume_filamento_m3 = quantidade_filamento_produzido_kg / densidade_kg_m3
            # Comprimento (m) = Volume (m³) / Área da Seção Transversal (m²)
            # Garante que a área da seção não é zero
            if AREA_SECAO_FILAMENTO_M2 > 0:
                 comprimento_filamento_m = volume_filamento_m3 / AREA_SECAO_FILAMENTO_M2
            else:
                 st.warning(f"Área da seção do filamento calculada como zero. Verifique o diâmetro do filamento ({DIAMETRO_FILAMENTO_MM} mm).")


        comprimento_filamento_km = comprimento_filamento_m / 1000 # Comprimento em km


        # Cálculo do consumo de energia total
        # Assume que o consumo_energia_kwh_por_kg é baseado na quantidade_input_kg
        consumo_energia_total_kwh = quantidade_input * consumo_energia_por_kg


        # Armazenar resultados na session state
        st.session_state.simulacao_resultados = {
            "quantidade_input_kg": quantidade_input,
            "material_simulado": material_selecionado_nome,
            "quantidade_filamento_produzido_kg": quantidade_filamento_produzido_kg,
            "comprimento_filamento_km": comprimento_filamento_km,
            "consumo_energia_total_kwh": consumo_energia_total_kwh,
            "densidade_gcm3": densidade, # Incluir para exibição
            "eficiencia_perc": eficiencia_percentual, # Incluir para exibição
            "perda_perc": perda_percentual, # Incluir para exibição
            "energia_por_kg": consumo_energia_por_kg # Incluir para exibição
        }
        st.rerun() # Força o rerun para exibir os resultados na seção abaixo

# --- Exibição dos Resultados da Simulação ---

st.markdown("---")
st.subheader("Resultados da Simulação")

if st.session_state.simulacao_resultados:
    resultados = st.session_state.simulacao_resultados

    st.info(f"""
        Simulação realizada para **{resultados['quantidade_input_kg']:.2f} kg** do material **{resultados['material_simulado']}**.
        (Densidade: {resultados['densidade_gcm3']:.3f} g/cm³, Eficiência: {resultados['eficiencia_perc']:.2f}%, Perda: {resultados['perda_perc']:.2f}%, Consumo Energia/kg: {resultados['energia_por_kg']:.3f} kWh/kg)
        **Nota:** A quantidade de filamento produzido é calculada como `Quantidade de Entrada * (Eficiência Estimada / 100)`.
    """)

    # Usando st.metric para os resultados principais
    st.metric(
        label="filament Filamento Produzido",
        value=f"{resultados['quantidade_filamento_produzido_kg']:,.2f} kg".replace(',', '.'), # Formatação e substituição
        help="Quantidade estimada de filamento produzida a partir da quantidade de material informada, considerando a eficiência do processo para este material."
    )

    st.metric(
        label="📏 Comprimento Estimado do Filamento",
        value=f"{resultados['comprimento_filamento_km']:,.2f} km".replace(',', '.'), # Formatação e substituição
        help=f"Comprimento estimado do filamento produzido (considerando diâmetro de {DIAMETRO_FILAMENTO_MM} mm e a densidade do material)."
    )

    st.metric(
        label="⚡ Consumo Total de Energia no Processo",
        value=f"{resultados['consumo_energia_total_kwh']:,.2f} kWh".replace(',', '.'),
        help="Consumo total estimado de energia elétrica para processar a quantidade de material informada, com base no consumo por kg do material."
    )

    # --- Visualizações (Gráficos) ---
    st.markdown("#### Visualização dos Resultados")

    # 1. Gráfico de Quantidade (Input vs Produzido)
    quantidade_data = pd.DataFrame({
        "Métrica": ["Material Plástico (Input)", "Filamento Produzido"],
        "Quantidade (kg)": [resultados['quantidade_input_kg'], resultados['quantidade_filamento_produzido_kg']]
    })

    fig_quantidade = px.bar(
        quantidade_data,
        x="Métrica",
        y="Quantidade (kg)",
        title="Comparativo Quantidade (Input vs Produção)",
        labels={"Quantidade (kg)": "Quantidade (kg)", "Métrica": "Tipo de Material"},
        template="plotly_white",
        color="Métrica" # Cores diferentes para as barras
    )
    fig_quantidade.update_layout(yaxis_title="Quantidade (kg)") # Garante título do eixo Y
    st.plotly_chart(fig_quantidade, use_container_width=True)


    # 2. Gráfico de Consumo de Energia
    energia_data = pd.DataFrame({
         "Métrica": ["Consumo de Energia Total"],
         "Valor (kWh)": [resultados['consumo_energia_total_kwh']]
    })

    fig_energia = px.bar(
        energia_data,
        x="Métrica",
        y="Valor (kWh)",
        title="Consumo de Energia Estimado",
        labels={"Valor (kWh)": "Energia (kWh)", "Métrica": ""}, # Eixo X vazio
        template="plotly_white",
        color="Métrica" # Cor na barra
    )
    fig_energia.update_layout(showlegend=False, yaxis_title="Energia (kWh)") # Sem legenda e título do eixo Y
    st.plotly_chart(fig_energia, use_container_width=True)


else:
    st.info("Preencha os dados à esquerda e clique em 'Simular Produção' para ver os resultados e gráficos.")


st.markdown("---") # Linha divisória


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