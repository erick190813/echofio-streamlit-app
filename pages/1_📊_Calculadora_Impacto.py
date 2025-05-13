# pages/1_📊_Calculadora_Impacto.py

import streamlit as st
import os # Necessário para verificar a existência do arquivo de logo

# --- Configuração da página (Estas configurações devem estar principalmente no script principal como 'echofio_app.py') ---
# st.set_page_config(page_title="Calculadora", layout="wide") # Removido daqui para evitar conflitos se já definido no echofio_app.py

# --- Verifica se o usuário está logado ---
# Assume que o estado de login está sendo gerenciado em st.session_state no seu script principal (echofio_app.py)
if not st.session_state.get('logged_in', False):
    st.warning("🔒 Por favor, faça login para acessar este módulo.")
    st.stop() # Interrompe a execução desta página se não estiver logado

# --- Layout do cabeçalho (Consistência visual) ---
# Assume que o arquivo da logo está na raiz do seu projeto. Ajuste o caminho se necessário.
LOGO_FILE_NAME = "31121abd-f8d6-4d98-b07a-9de3735ea257.png" # Nome do arquivo da sua logo
# Tenta encontrar o caminho da logo relativo à pasta 'pages' ou na raiz
LOGO_PATH_RELATIVE = os.path.join("..", LOGO_FILE_NAME) # Tenta ../logo.png
LOGO_PATH_ROOT = LOGO_FILE_NAME # Tenta logo.png (se executado da raiz)

col_logo, col_title = st.columns([1, 4])

with col_logo:
    # Verifica qual caminho da logo existe e exibe
    if os.path.exists(LOGO_PATH_RELATIVE):
        st.image(LOGO_PATH_RELATIVE, width=80)
    elif os.path.exists(LOGO_PATH_ROOT):
         st.image(LOGO_PATH_ROOT, width=80)
    else:
        st.header("♻️") # Ícone de fallback se a logo não for encontrada

with col_title:
    st.title("Calculadora de Impacto e Economia") # Novo Título da Página
    st.markdown("### Quantifique os benefícios ambientais e econômicos do ECHOFIO") # Subtítulo

st.markdown("---") # Linha divisória

# --- Seção da Calculadora ---

st.subheader("Calcular Impacto e Economia Estimados")

st.write("Utilize a calculadora abaixo para estimar o impacto positivo e a economia gerada pelo processo e filamentos ECHOFIO.")

# --- Formulário de Input do Usuário ---
with st.form("calculadora_form"):
    st.write("Insira a quantidade de material:")

    quantidade_input = st.number_input(
        "Quantidade:",
        min_value=0.0,
        step=0.1,
        format="%.2f",
        help="Informe a quantidade de resíduo plástico ou filamento ECHOFIO."
    )

    tipo_input = st.radio(
        "Tipo de Material:",
        ('kg de Resíduo Plástico', 'kg de Filamento ECHOFIO Produzido'),
        horizontal=True,
        help="Selecione se a quantidade informada refere-se ao resíduo plástico coletado/processado ou ao filamento ECHOFIO produzido/utilizado."
    )

    calcular_button = st.form_submit_button("Calcular Impacto e Economia")

# --- Valores de Referência do Projeto (CONFIGURE AQUI!) ---
# Importante: Estes valores são exemplos. Você DEVE substituí-los pelos dados reais
# e pesquisados do Projeto ECHOFIO para garantir a precisão da calculadora.

TAXA_CONVERSAO_RESIDUO_FILAMENTO = 0.8 # Exemplo: 0.8 significa que 80% do peso do resíduo vira filamento. Ajuste!
FATOR_CO2_EVITADO_POR_KG_RESIDUO = 2.5 # Exemplo: kg de CO2 evitados por kg de resíduo plástico reciclado. Pesquise este valor para o(s) tipo(s) de plástico que vocês usam!
FATOR_ENERGIA_ECONOMIZADA_POR_KG_RESIDUO = 5.0 # Exemplo: kWh economizados por kg de resíduo plástico reciclado. Pesquise este valor!
CUSTO_ECHOFIO_POR_KG = 100.0 # Exemplo: Preço de venda (ou custo de produção, dependendo do que quer comparar) do filamento ECHOFIO por kg. Ajuste!
CUSTO_VIRGEM_POR_KG = 150.0 # Exemplo: Preço médio de mercado de um filamento virgem similar por kg. Pesquise e ajuste!

# --- Lógica do Cálculo e Exibição dos Resultados ---
if calcular_button and quantidade_input > 0:
    st.markdown("---")
    st.subheader("Resultados Calculados")

    quantidade_residuo_kg = 0.0
    quantidade_filamento_kg = 0.0

    # Determina as quantidades de resíduo e filamento com base no input
    if tipo_input == 'kg de Resíduo Plástico':
        quantidade_residuo_kg = quantidade_input
        # Garante que a taxa de conversão não é zero para evitar erro
        if TAXA_CONVERSAO_RESIDUO_FILAMENTO > 0:
            quantidade_filamento_kg = quantidade_input * TAXA_CONVERSAO_RESIDUO_FILAMENTO
        else:
             st.error("Erro: A taxa de conversão de resíduo para filamento deve ser maior que zero.")
             quantidade_filamento_kg = 0
             quantidade_residuo_kg = 0 # Zera tudo se a taxa for inválida

    else: # 'kg de Filamento ECHOFIO Produzido'
        quantidade_filamento_kg = quantidade_input
        # Garante que a taxa de conversão não é zero para evitar erro
        if TAXA_CONVERSAO_RESIDUO_FILAMENTO > 0:
            quantidade_residuo_kg = quantidade_input / TAXA_CONVERSAO_RESIDUO_FILAMENTO
        else:
             st.error("Erro: A taxa de conversão de resíduo para filamento deve ser maior que zero.")
             quantidade_filamento_kg = 0
             quantidade_residuo_kg = 0 # Zera tudo se a taxa for inválida


    # Exibe a quantidade de resíduo desviado (diretamente do cálculo acima)
    st.metric(
        label="🗑️ Resíduo Plástico Desviado",
        value=f"{quantidade_residuo_kg:,.2f} kg".replace(',', '.'), # Formatação e substituição para usar ponto como separador decimal
        help="Quantidade de resíduo plástico que deixou de ir para aterros ou o meio ambiente."
    )

    # Exibe a quantidade de filamento produzida/equivalente
    st.metric(
        label="Quantidade de Filamento ECHOFIO",
        value=f"{quantidade_filamento_kg:,.2f} kg".replace(',', '.'), # Formatação e substituição para usar ponto como separador decimal
        help=f"Quantidade estimada de filamento ECHOFIO produzida a partir de {quantidade_residuo_kg:,.2f} kg de resíduo (considerando taxa de conversão de {TAXA_CONVERSAO_RESIDUO_FILAMENTO*100:.1f}%)."
    )


    # --- Estimativa de Impacto Ambiental Evitado ---
    st.subheader("Impacto Ambiental Evitado (Estimativa)")
    # Certifica-se que os fatores estão definidos antes de calcular e exibir
    if FATOR_CO2_EVITADO_POR_KG_RESIDUO is not None and FATOR_ENERGIA_ECONOMIZADA_POR_KG_RESIDUO is not None:
        reducao_co2_estimada = quantidade_residuo_kg * FATOR_CO2_EVITADO_POR_KG_RESIDUO
        economia_energia_estimada = quantidade_residuo_kg * FATOR_ENERGIA_ECONOMIZADA_POR_KG_RESIDUO

        st.metric(
            label="💨 Redução Estimada de CO2",
            value=f"{reducao_co2_estimada:,.2f} kg CO2".replace(',', '.'),
            help=f"Estimativa de emissões de CO2 evitadas pela reciclagem em comparação com a produção de material virgem (baseado em {FATOR_CO2_EVITADO_POR_KG_RESIDUO:,.2f} kg CO2/kg resíduo)."
        )

        st.metric(
             label="💡 Economia Estimada de Energia",
             value=f"{economia_energia_estimada:,.2f} kWh".replace(',', '.'),
             help=f"Estimativa de energia economizada pela reciclagem em comparação com a produção de material virgem (baseado em {FATOR_ENERGIA_ECONOMIZADA_POR_KG_RESIDUO:,.2f} kWh/kg resíduo)."
         )
    else:
        st.info("Fatores de impacto ambiental (CO2, Energia) não configurados. Entre em contato com os administradores.")


    # --- Estimativa de Economia Financeira ---
    st.subheader("Economia Financeira Estimada")
    # Certifica-se que os custos estão definidos e o custo virgem é maior para a economia ser positiva
    if CUSTO_ECHOFIO_POR_KG is not None and CUSTO_VIRGEM_POR_KG is not None:
        if CUSTO_VIRGEM_POR_KG > CUSTO_ECHOFIO_POR_KG:
            economia_financeira_estimada = quantidade_filamento_kg * (CUSTO_VIRGEM_POR_KG - CUSTO_ECHOFIO_POR_KG)
            st.metric(
                label="💰 Economia Financeira Estimada",
                value=f"R$ {economia_financeira_estimada:,.2f}".replace(',', '.'),
                help=f"Estimativa de economia ao utilizar {quantidade_filamento_kg:,.2f} kg de filamento ECHOFIO em vez de filamento virgem (custo ECHOFIO: R${CUSTO_ECHOFIO_POR_KG:,.2f}/kg, custo virgem: R${CUSTO_VIRGEM_POR_KG:,.2f}/kg)."
            )
        elif CUSTO_VIRGEM_POR_KG <= CUSTO_ECHOFIO_POR_KG and quantidade_input > 0:
             st.info("Neste exemplo, o custo do filamento ECHOFIO não é menor que o custo do filamento virgem para gerar economia financeira positiva.")
        else:
             st.info("Dados de custo do filamento não definidos ou configurados incorretamente para calcular a economia financeira.")


    st.markdown("---")
    st.info("""
        **Nota Importante:**
        Os valores apresentados são **estimativas** baseadas em dados de referência e pesquisa.
        A taxa de conversão de resíduo para filamento e os fatores de impacto ambiental/economia podem variar
        dependendo do tipo específico de plástico, do processo de reciclagem e das condições de mercado.
        Consulte a equipe do Projeto ECHOFIO para dados mais precisos e detalhes sobre a metodologia de cálculo.
    """)


elif calcular_button and quantidade_input == 0:
     st.warning("Por favor, insira uma quantidade maior que zero para realizar o cálculo.")

# --- Rodapé da página (Opcional, para consistência) ---
# st.markdown("---")
# st.write("Projeto ECHOFIO - Inovação Sustentável") # Exemplo de rodapé


# --- Sidebar (Atualizar a descrição do projeto e incluir logo) ---
with st.sidebar:
     # Adicionar o logo na sidebar também (opcional, mas comum)
     # Use o mesmo tratamento de caminho da logo do cabeçalho principal
     if os.path.exists(LOGO_PATH_RELATIVE):
         st.image(LOGO_PATH_RELATIVE, width=80)
     elif os.path.exists(LOGO_PATH_ROOT):
          st.image(LOGO_PATH_ROOT, width=80)
     else:
          st.header("♻️") # Ícone de fallback


     st.markdown("---") # Separador visual

     st.header("🌱 Sobre o Projeto ECHOFIO") # Nome do projeto atualizado
     st.info(
         "O Projeto ECHOFIO transforma resíduos plásticos descartados em filamentos "
         "sustentáveis de alta qualidade para impressão 3D. Nosso objetivo é promover a "
         "economia circular, reduzir o impacto ambiental e oferecer uma alternativa "
         "inovadora e de baixo custo no mercado de manufatura aditiva." # Descrição atualizada, sem menção a IA
     )
     st.markdown("---")
     st.write("Desenvolvido por Equipe ECHOFIO") # Créditos