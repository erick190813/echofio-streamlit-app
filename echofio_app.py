# echofio_app.py - Versão para Debug

import streamlit as st
import database
import os # Importar para verificar a existência do arquivo de logo

# --- Configuração da página (DEVE SER O PRIMEIRO COMANDO STREAMLIT) ---
# Define o título da aba do navegador, layout e estado inicial da sidebar.
# Use um título que represente o aplicativo como um todo.
st.set_page_config(page_title="Projeto ECHOFIO App", layout="wide", initial_sidebar_state="expanded")

# --- Inicializar o banco de dados e o usuário administrador ---
try:
    # A função inicializar_db() em database.py agora chama criar_tabela_usuarios(),
    # criar_tabela_materiais() E criar_usuario_admin_inicial() na ordem correta.
    print("[DEBUG APP] Chamando database.inicializar_db()") # Debug print no app principal
    database.inicializar_db()
    print("[DEBUG APP] database.inicializar_db() concluído.") # Debug print


    # Inicializa o estado da sessão para nomes de materiais, se ainda não existirem.
    # Este é o passo que popula a lista usada na página de Simulação.
    if 'nomes_materiais' not in st.session_state:
        print("[DEBUG APP] 'nomes_materiais' não está na sessão. Buscando nomes do DB...") # Debug
        nomes_db = database.buscar_nomes_materiais() # Chama a função que tem debug prints internos
        st.session_state.nomes_materiais = list(nomes_db) if nomes_db else [] # Converte o resultado para lista
        print(f"[DEBUG APP] st.session_state.nomes_materiais definido como: {st.session_state.nomes_materiais}") # Debug

    # Inicializa estado de login
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        print("[DEBUG APP] 'logged_in' não está na sessão. Definido como False.") # Debug

    if 'username' not in st.session_state:
         st.session_state.username = ""
         print("[DEBUG APP] 'username' não está na sessão. Definido como ''.") # Debug

    # Inicializa user_privileges na sessão.
    # Os privilégios reais só são carregados após o login bem-sucedido em Login.py.
    # Aqui apenas garantimos que a chave existe na sessão com valores padrão False.
    if 'user_privileges' not in st.session_state:
        st.session_state.user_privileges = {"can_edit_db": False, "is_admin": False}
        print("[DEBUG APP] 'user_privileges' não está na sessão. Definido como padrão False/False.") # Debug


except Exception as e:
    # Este bloco captura erros durante a inicialização do DB que ocorrem DENTRO do try
    print(f"[DEBUG APP] ERRO CRÍTICO capturado durante inicialização do APP/DB: {e}") # Debug
    st.error(f"Erro CRÍTICO ao inicializar o banco de dados ou usuário administrador: {e}")
    st.warning(
        "A aplicação pode não funcionar corretamente. Verifique o arquivo 'database.py' e se o arquivo 'materiais.db' foi criado/atualizado corretamente.")
    # Define estados de fallback para que o app não quebre totalmente em caso de erro crítico no DB
    st.session_state.nomes_materiais = [] # Lista vazia em caso de erro no DB
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
         st.session_state.username = ""
    if 'user_privileges' not in st.session_state:
        st.session_state.user_privileges = {"can_edit_db": False, "is_admin": False}

print("[DEBUG APP] Inicialização da sessão e DB concluída.") # Debug print final da inicialização


# --- Layout do cabeçalho (Consistência visual) ---
# Assume que o arquivo da logo está na raiz do seu projeto. Ajuste o caminho se necessário.
LOGO_FILE_NAME = "31121abd-f8d6-4d98-b07a-9de3735ea257.png" # Nome do arquivo da sua logo
# O script principal está na raiz, então o caminho é direto o nome do arquivo.
LOGO_PATH_ROOT = LOGO_FILE_NAME

col_logo, col_title = st.columns([1, 4])

with col_logo:
    # Verifica se o caminho da logo existe e exibe
    if os.path.exists(LOGO_PATH_ROOT):
        st.image(LOGO_PATH_ROOT, width=100) # Logo um pouco maior na página principal
    else:
        st.header("♻️") # Ícone de fallback se a logo não for encontrada

with col_title:
    st.title("Bem-vindo ao Projeto ECHOFIO") # Título Principal da Homepage
    st.markdown("### Inovação Sustentável em Impressão 3D") # Subtítulo/Tagline

st.markdown("---") # Linha divisória

# --- Conteúdo da Homepage (Mostrado quando NÃO logado - Mais Detalhado) ---
if not st.session_state.get('logged_in', False):
    st.subheader("Dando Uma Nova Vida ao Plástico Descartado")

    st.write(
        """
        O **Projeto ECHOFIO** é uma iniciativa dedicada a revolucionar a impressão 3D através da sustentabilidade.
        Nossa missão é dar uma **nova vida** a resíduos plásticos que seriam descartados,
        transformando-os em **filamentos de alta qualidade** para impressoras 3D.
        """
    )

    st.markdown("#### Nossa Proposta de Valor se Baseia em Pilares Fortes:")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### 🌱 Sustentabilidade e Economia Circular")
        st.write(
            """
            Acreditamos em um futuro onde o "lixo" não existe, apenas recursos fora do lugar.
            O ECHOFIO implementa a **economia circular** na prática, desviando toneladas de resíduos plásticos de aterros
            e oceanos, e reintegrando-os na cadeia produtiva como matéria-prima para filamentos.
            Reduzimos significativamente o impacto ambiental associado à produção de filamentos a partir de plástico virgem.
            """
        )

        st.markdown("##### 💡 Inovação Tecnológica")
        st.write(
            """
            Nosso processo envolve etapas cuidadosas de coleta, triagem, limpeza, trituração e, crucialmente, a **extrusão**
            controlada para garantir a qualidade e uniformidade do filamento. Aplicamos **controle de qualidade rigoroso**
            para assegurar que o filamento ECHOFIO atenda aos padrões necessários para uma impressão 3D confiável e de sucesso.
            """
        )

    with col2:
        st.markdown("##### 💰 Baixo Custo e Acessibilidade")
        st.write(
            """
            Ao utilizar resíduos como matéria-prima, conseguimos reduzir consideravelmente os custos de produção
            em comparação com filamentos tradicionais. Isso torna o filamento ECHOFIO uma **alternativa mais acessível**
            e economicamente viável para makers, empresas e instituições que buscam reduzir gastos sem comprometer a qualidade
            ou o compromisso ambiental.
            """
        )

        st.markdown("##### 📚 Educação e Conscientização")
        st.write(
            """
            Vamos além da produção. O ECHOFIO também se dedica a **disseminar conhecimento** sobre a importância da reciclagem,
            os princípios da economia circular e as possibilidades da manufatura aditiva sustentável. Colaboramos com
            instituições de ensino e parceiros para inspirar e capacitar a próxima geração de inovadores conscientes.
            """
        )

    st.markdown("---")

    st.subheader("Nosso Processo em Resumo:")
    st.write(
        """
        De forma simplificada, transformamos o resíduo através das seguintes etapas:
        **Coleta & Triagem** → **Limpeza & Trituração** → **Extrusão & Filamentação** → **Controle de Qualidade** → **Prototipagem & Otimização** → **Distribuição Sustentável**.
        Cada passo é otimizado para garantir a eficiência do ciclo e a qualidade do filamento final.
        """
    )

    st.markdown("---")

    st.subheader("Quem Apoiamos e Quem Busca o ECHOFIO:")
    st.write(
        """
        Nosso projeto atende a diversos segmentos, todos unidos pelo interesse em inovação, sustentabilidade e eficiência:
        **Comunidade Maker**, **Empresas e Startups** que usam impressão 3D, **Setor Industrial**, **Instituições Educacionais e de Pesquisa**,
        e **Organizações com Foco em Impacto Social e Ambiental**.
        Contamos com parceiros estratégicos como o **SENAI Nova Lima** e a **AML EDITORA** para fortalecer nossa atuação e alcance.
        """
    )

    st.markdown("---")


    st.subheader("Explore Nossas Ferramentas!")
    st.write(
        """
        Crie uma conta ou faça login para ter acesso total às nossas ferramentas,
        como a **Calculadora de Impacto e Economia** (quantifique os benefícios da reciclagem)
        e o **Módulo de Simulação** (planeje sua produção de filamento com diferentes materiais).
        """
    )

    st.info("Para começar, utilize as opções 'Login' ou 'Registro' na barra lateral.")


else:
    # --- Conteúdo Mostrado Quando Logado ---
    st.success(f"Bem-vindo(a), {st.session_state.username}! Você está logado.")
    st.write("Explore os módulos disponíveis na barra lateral à esquerda:")

    st.markdown("""
    - 📊 **Calculadora de Impacto e Economia:** Calcule o impacto ambiental e a economia do ECHOFIO.
    - ⚙️ **Simulação:** Simule a produção de filamento com base em diferentes materiais.
    - 📚 **Banco de Dados:** Consulte e (se permitido) gerencie as propriedades dos materiais reciclados.
    """)

st.markdown("---") # Linha divisória

# --- Sidebar (Conteúdo fixo para todas as páginas) ---
with st.sidebar:
    # Adicionar o logo na sidebar também (opcional, mas comum)
    # Usa o mesmo tratamento de caminho da logo do cabeçalho principal (na raiz)
    if os.path.exists(LOGO_PATH_ROOT):
        st.image(LOGO_PATH_ROOT, width=80) # Logo menor na sidebar
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