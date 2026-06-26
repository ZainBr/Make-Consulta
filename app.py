import streamlit as st 
import pandas as pd
import io
import re
import requests
import urllib.parse

# --- CONFIGURAÇÃO DA INTERFACE ---
st.set_page_config(
    page_title="Make Distribuidora - ConsultaNF", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CREDENCIAIS DA SUA INTEGRAÇÃO PÚBLICA (NOTION OAUTH) ---
CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]

# DETECÇÃO AUTOMÁTICA DE AMBIENTE:
try:
    headers = st.context.headers
    host = headers.get("Host", "")
    
    if "localhost" in host or "127.0.0.1" in host:
        REDIRECT_URI = "http://localhost:8501/"
    else:
        REDIRECT_URI = "https://make-consulta-xvbe6b9ut9es6i6bbemudm.streamlit.app/"
except Exception:
    REDIRECT_URI = "https://make-consulta-xvbe6b9ut9es6i6bbemudm.streamlit.app/"

# --- CSS PREMIUM INSPIRADO NA MAKE DISTRIBUIDORA ---
FUTURISTIC_CSS = """
<style>
    /* --- VARIÁVEIS DE COR CORPORATIVAS (MUDANÇA DINÂMICA) --- */
    :root {
        --bg-app: #04140e; /* Verde escuro idêntico à imagem de referência */
        --bg-card: #082218; 
        --border-line: #123a2b;
        --accent: #00a854; /* Verde vibrante do botão "Entrar" */
        --accent-hover: #00c261;
        --text-white: #ffffff;
        --text-secondary: #a3b8b0;
        
        /* Alertas baseados no erro da imagem */
        --bg-error: rgba(139, 9, 9, 0.25);
        --border-error: #8b0909;
        --text-error: #ff7676;
    }

    /* Suporte automático a Tema Claro do Sistema */
    @media (prefers-color-scheme: light) {
        :root {
            --bg-app: #f4f7f5;
            --bg-card: #ffffff;
            --border-line: #d1e0db;
            --accent: #00a854;
            --accent-hover: #008f47;
            --text-white: #0f1f18;
            --text-secondary: #50695f;
            --bg-error: #fdf2f2;
            --border-error: #f8b4b4;
            --text-error: #9b1c1c;
        }
    }
    
    /* --- ESTRUTURA GLOBAL --- */
    body, .stApp, [data-testid="stAppViewContainer"] {
        background: var(--bg-app) !important;
        color: var(--text-white) !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    h1, h2, h3, h4, h5, h6, p, span, label {
        color: var(--text-white) !important;
    }
    
    /* --- RESPONSIVIDADE MOBILE --- */
    @media (max-width: 768px) {
        .stColumns {
            flex-direction: column !important;
            gap: 12px !important;
        }
        .stButton > button, [data-testid="stDownloadButton"] > button {
            width: 100% !important;
        }
        .notion-card {
            padding: 16px !important;
        }
    }
    
    /* --- CARDS PERSONALIZADOS (ESTILO DA MARCA) --- */
    .notion-card {
        background: var(--bg-card);
        border: 1px solid var(--border-line);
        border-radius: 10px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* --- BOTÕES NO ESTILO "ENTRAR" DA MAKE --- */
    .stButton > button, [data-testid="stDownloadButton"] > button {
        background-color: var(--accent) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stButton > button:hover, [data-testid="stDownloadButton"] > button:hover {
        background-color: var(--accent-hover) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,168,84,0.3);
    }
    
    /* --- NOTIFICAÇÕES E ALERTAS ESTILIZADOS --- */
    div[data-testid="stNotification"] {
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border-line) !important;
        border-radius: 8px !important;
    }
    
    /* Estilo customizado para mensagens de erro/aviso idênticas à imagem */
    .error-box {
        background-color: var(--bg-error);
        border: 1px solid var(--border-error);
        color: var(--text-error) !important;
        padding: 14px;
        border-radius: 8px;
        font-size: 14px;
        margin: 10px 0;
    }
</style>
"""

st.markdown(FUTURISTIC_CSS, unsafe_allow_html=True)

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    pdfplumber = None
    PDFPLUMBER_AVAILABLE = False

# ============================================================================
# LOGICA AUXILIAR DE INTEGRAÇÃO MULTI-USUÁRIO (NOTION OAUTH)
# ============================================================================

def gerar_link_notion():
    base_url = "https://api.notion.com/v1/oauth/authorize"
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "owner": "user",
        "redirect_uri": REDIRECT_URI
    }
    return f"{base_url}?{urllib.parse.urlencode(params)}"

def obter_access_token(auth_code):
    url = "https://api.notion.com/v1/oauth/token"
    try:
        response = requests.post(
            url,
            auth=(CLIENT_ID, CLIENT_SECRET),
            json={
                "grant_type": "authorization_code",
                "code": auth_code,
                "redirect_uri": REDIRECT_URI
            },
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            return response.json()
        return None
    except requests.RequestException as e:
        st.error(f"Erro de rede ao autenticar com o Notion: {e}")
        return None

def enviar_linha_para_notion(token, database_id, dados):
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    nome_arquivo = str(dados.get("Arquivo", dados.get("arquivo", "N/A")))
    numero_nf = str(dados.get("NF", dados.get("nf", "N/A")))
    data_emissao = str(dados.get("Data de emissão", dados.get("data", "N/A")))
    cod_produto = str(dados.get("Código do produto", dados.get("produto", "N/A")))
    cod_parceiro = str(dados.get("Código do parceiro", dados.get("parceiro", "N/A")))

    # Estrutura para criar uma página DENTRO da base de dados da foto
    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "title": [
                {
                    "type": "text",
                    "text": {"content": nome_arquivo}
                }
            ]
        },
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": f"NF: {numero_nf}"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": f"EMISSAO: {data_emissao}"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": f"PARCEIRO: {cod_parceiro}"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": f"COD:\n{cod_produto}"}}]
                }
            }
        ]
    }
    
    try:
        res = requests.post(url, json=payload, headers=headers)
        if res.status_code == 200:
            return True
        else:
            st.error(f"🔴 Erro na API do Notion ({res.status_code}): {res.text}")
            return False
    except requests.RequestException as e:
        st.error(f"🔴 Falha crítica de rede: {e}")
        return False
def buscar_id_da_pagina_por_nome(token, nome_padrao="Notes"):
    url = "https://api.notion.com/v1/search"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    def _get_nome_database(resultado):
        try:
            titulo = resultado.get("title", [])
            if titulo:
                return titulo[0].get("plain_text", "Sem nome")
        except:
            pass
        return "Sem nome"

    def _is_database_valido(resultado):
        return resultado.get("object") == "database" and resultado.get("id")

    try:
        # Tentativa 1: Buscar pelo nome padrao
        payload_busca = {
            "query": nome_padrao,
            "filter": {"value": "database", "property": "object"},
            "page_size": 10
        }
        res = requests.post(url, json=payload_busca, headers=headers)
        if res.status_code == 200:
            resultados = [r for r in res.json().get("results", []) if _is_database_valido(r)]
            if resultados:
                return resultados[0].get("id"), _get_nome_database(resultados[0]), resultados

        # Tentativa 2: Busca geral, qualquer database liberado
        payload_geral = {
            "filter": {"value": "database", "property": "object"},
            "page_size": 10
        }
        res_geral = requests.post(url, json=payload_geral, headers=headers)
        if res_geral.status_code == 200:
            resultados_gerais = [r for r in res_geral.json().get("results", []) if _is_database_valido(r)]
            if resultados_gerais:
                return resultados_gerais[0].get("id"), _get_nome_database(resultados_gerais[0]), resultados_gerais

    except Exception:
        pass

    return None, None, []
# --- HEADER MINIMALISTA ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
        <div style="text-align: center; padding: 40px 0 20px 0;">
            <h1 style="
                margin: 0;
                font-size: 28px;
                letter-spacing: 0.15em;
                text-transform: uppercase;
                color: var(--text-white);
                background: linear-gradient(90deg, var(--accent), #ffffff, var(--accent));
                background-size: 200% 100%;
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                animation: shimmerText 4s linear infinite;
            ">CONSULTA NF</h1>
            <p style="
                margin: 12px 0 0 0;
                font-size: 12px;
                letter-spacing: 0.08em;
                color: var(--text-secondary);
                text-transform: uppercase;
            ">Extração de Notas Fiscais</p>
        </div>
    """, unsafe_allow_html=True)

st.divider()

if not PDFPLUMBER_AVAILABLE:
    st.error("⚠️ **AVISO CRÍTICO** - Execute `pip install pdfplumber` para ativar a extração de PDF.")
    st.stop()

# ============================================================================
# FUNÇÕES DE EXTRAÇÃO CORRIGIDAS
# ============================================================================

def limpar_texto(valor):
    return re.sub(r'\s+', ' ', (valor or '')).strip()

def extrair_nf(texto, linhas_pdf):
    padroes_nf = [
        r'\bN\.?\s*(\d{1,3}(?:\.\d{3})*|\d{3,})\b',
        r'\bNF[-\s]*e?\s*(?:n[ºo]\.?|n[úu]mero)?\s*[:\-]?\s*(\d{3,})\b',
        r'\bN[ºo]\.?\s*(\d{3,})\b'
    ]
    for padrao in padroes_nf:
        match = re.search(padrao, texto, re.IGNORECASE)
        if match: return match.group(1).replace('.', '')
    return "N/A"

def extrair_itens_produtos(pdf_obj, texto_completo=""):
    itens = []
    
    # 1ª tentativa: Baseado em tabela estruturada
    for page in pdf_obj.pages:
        for tabela in (page.extract_tables() or []):
            for linha in tabela:
                if not linha: continue
                valores = [limpar_texto(celula) for celula in linha if limpar_texto(celula)]
                if not valores: continue
                cabecalho = " ".join(valores).upper()
                if ('CÓD' in cabecalho and 'PROD' in cabecalho) or ('DESCRIÇÃO' in cabecalho and 'PRODUTO' in cabecalho):
                    continue
                for indice, celula in enumerate(valores):
                    if re.fullmatch(r'\d{3,}', celula):
                        if indice + 1 < len(valores) and not any(item == celula for item in itens):
                            itens.append(celula)
                        break

    # Fallback Robusto: Se a extração de tabelas falhar ou vier vazia, varre o texto puro linha por linha
    if not itens and texto_completo:
        for linha in texto_completo.splitlines():
            linha_limpa = limpar_texto(linha)
            # Procura por padrões de CFOP de saída/venda comuns (Ex: 5405, 5102, 6102) na linha
            if re.search(r'\b(5101|5102|5405|5403|6101|6102)\b', linha_limpa):
                # O código do produto na DANFE é o primeiro grupo de dígitos isolados no início da linha da tabela
                match_codigo = re.match(r'^["\']?(\d+)\b', linha_limpa)
                if match_codigo:
                    codigo = match_codigo.group(1)
                    # Ignora se por acaso bater com a própria NF ou ano
                    if codigo not in itens and len(codigo) >= 3 and len(codigo) <= 7:
                        itens.append(codigo)
                        
    return itens

def extrair_codigo_parceiro(texto, linhas_pdf):
    """Extrai o código do parceiro/cliente da DANFE de forma precisa."""
    texto_normalizado = re.sub(r'\s+', ' ', texto)

    # --- ESTRATÉGIA 1: Canhoto Superior (A mais segura para este layout específico) ---
    # Procura pela frase fixa do canhoto que contém o código puro: "INDICADA AD LADO XXXXXX"
    match_canhoto = re.search(r'INDICADA\s+A[DQ]\s+LADO\s+(\d{3,8})', texto_normalizado, re.IGNORECASE)
    if match_canhoto:
        return match_canhoto.group(1)

    # --- ESTRATÉGIA 2: Sua lógica original baseada na Janela do Nome/Razão Social ---
    for indice, linha in enumerate(linhas_pdf):
        if re.search(r'NOME/RAZ[ÃA]O SOCIAL', linha, re.IGNORECASE):
            janela = ' '.join(linhas_pdf[indice:indice + 6])
            match = re.search(r'NOME/RAZ[ÃA]O SOCIAL\s+(.+?)\s+(\d{3,8})\b', janela, re.IGNORECASE)
            if match:
                # Evita capturar fragmentos comuns de início de CNPJ como "25.065.929"
                codigo_candidato = match.group(2)
                if "." not in codigo_candidato and "-" not in codigo_candidato:
                    return codigo_candidato

    # --- ESTRATÉGIA 3: Fallback por proximidade antes do CNPJ/CPF Destinatário ---
    # Captura o número limpo de 3 a 8 dígitos que antecede a máscara do CNPJ/CPF
    match_antes_cnpj = re.search(r'\b(\d{3,8})\s+\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}', texto_normalizado)
    if match_antes_cnpj:
        return match_antes_cnpj.group(1)
        
    match_antes_cpf = re.search(r'\b(\d{3,8})\s+\d{3}\.\d{3}\.\d{3}-\d{2}', texto_normalizado)
    if match_antes_cpf:
        return match_antes_cpf.group(1)

    # --- ESTRATÉGIA 4: Bloqueio de segurança contra Inscrição Estadual ---
    # Se ainda tentar buscar por "NOME/RAZÃO SOCIAL" genérico, garantimos que não pegue a IE (12228198)
    match_generico = re.search(r'NOME/RAZ[ÃA]O SOCIAL.*?\b(\d{3,8})\b', texto_normalizado, re.IGNORECASE)
    if match_generico:
        codigo_candidato = match_generico.group(1)
        if codigo_candidato != "12228198": # Ignora a IE da distribuidora
            return codigo_candidato

    return "N/A"

@st.cache_data(show_spinner=False)
def extrair_dados_nf(pdf_bytes, nome_arquivo):
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            texto_completo = ""
            linhas = []
            for page in pdf.pages:
                pagina_texto = page.extract_text() or ""
                texto_completo += pagina_texto + "\n"
                linhas.extend([l.strip() for l in pagina_texto.splitlines() if l.strip()])

            dados = {
                "NF": extrair_nf(texto_completo, linhas),
                "Data de emissão": "N/A",
                "Código do produto": "N/A",
                "Código do parceiro": "N/A"
            }

            # Busca a data de emissão
            match_data = re.search(
                r'EMISS[ÃA]O\D{0,20}(\d{2}/\d{2}/\d{4})',
                texto_completo,
                re.IGNORECASE
            )
            if not match_data:
                match_data = re.search(r'(\d{2}/\d{2}/\d{4})', texto_completo)
            if match_data:
                dados["Data de emissão"] = match_data.group(1)

            # Extração dos códigos mapeando fallback textual
            codigos_produtos = extrair_itens_produtos(pdf, texto_completo=texto_completo)
            dados["Código do produto"] = "\n".join(codigos_produtos) if codigos_produtos else "N/A"
            
            # Código do parceiro dinâmico ajustado
            dados["Código do parceiro"] = extrair_codigo_parceiro(texto_completo, linhas)
            
            return dados
    except Exception as e:
        return {"NF": "Erro", "Data de emissão": str(e), "Código do produto": "Erro", "Código do parceiro": "Erro"}

# --- SIDEBAR CONTROL PANEL ---
st.sidebar.markdown("""
    <div style="padding: 20px 0;">
        <h2 style="text-align: center; margin: 0; font-size: 14px; letter-spacing: 0.08em; text-transform: uppercase;">Painel de Controle</h2>
    </div>
""", unsafe_allow_html=True)
st.sidebar.divider()

st.sidebar.subheader("📁 Selecione seus arquivos PDF")
uploaded_files = st.sidebar.file_uploader("Arraste os arquivos para cá", type="pdf", accept_multiple_files=True)

# --- PROCESSAMENTO ---
if uploaded_files:
    total_files = len(uploaded_files)
    lista_resultados = []
    progress_bar = st.progress(0)

    with st.spinner("🔄 Processando arquivos..."):
        for idx, file in enumerate(uploaded_files):
            dados = extrair_dados_nf(file.read(), file.name)
            dados['Arquivo'] = file.name
            lista_resultados.append(dados)
            progress_bar.progress((idx + 1) / total_files)

    df = pd.DataFrame(lista_resultados)
    df = df[['Arquivo', 'NF', 'Data de emissão', 'Código do produto', 'Código do parceiro']]

    st.markdown("---")
    tab1, tab2, tab3 = st.tabs([" VISÃO GERAL", " ESTATÍSTICAS", " EXPORTAR / NOTION"])

    with tab1:
        st.markdown(f"<p style='font-size:14px;'>✓ <strong>{total_files} arquivo(s) processado(s)</strong></p>", unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True, hide_index=True)

    with tab2:
        cols = st.columns(4)
        cols[0].metric("ARQUIVOS", len(df))
        cols[1].metric("NFS", len(df[df['NF'] != 'N/A']))
        cols[2].metric("PRODUTOS", sum(len(str(p).split('\n')) for p in df['Código do produto'] if p != 'N/A'))
        cols[3].metric("PARCEIROS", len(df[df['Código do parceiro'] != 'N/A']))

    with tab3:
        st.markdown("### 🌐 Integração Corporativa Cloud")
        
        parametros_url = st.query_params
        if "code" in parametros_url and "token_notion_usuario" not in st.session_state:
            codigo_retorno = parametros_url["code"]
            with st.spinner("Conectando ao ambiente de trabalho..."):
                resposta_oauth = obter_access_token(codigo_retorno)
                if resposta_oauth:
                    st.session_state["token_notion_usuario"] = resposta_oauth["access_token"]
                    if "duplicated_template_id" in resposta_oauth:
                        st.session_state["id_tabela_usuario"] = resposta_oauth["duplicated_template_id"]
                    st.toast("Conectado com sucesso à Make Distribuidora no Notion!", icon="✅")
                    st.query_params.clear()
                else:
                    st.markdown('<div class="error-box">Falha ao autenticar com o Notion. Por favor, tente novamente.</div>', unsafe_allow_html=True)

        # --- CONTAINER SE DESCONECTADO ---
        if "token_notion_usuario" not in st.session_state:
            st.markdown("""
                <div class="notion-card">
                    <h4 style="margin: 0 0 8px 0; font-weight: 600;">Sincronização com o Notion</h4>
                    <p style="margin: 0; font-size: 14px; color: var(--text-secondary); line-height: 1.5;">
                        Vincule seu painel corporativo para exportar os dados das Notas Fiscais extraídas de forma direta para a base do seu setor.
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            url_notion_auth = gerar_link_notion()
            st.link_button("🔑 CONECTAR MEU NOTION", url_notion_auth, use_container_width=True)
            
        # --- CONTAINER SE CONECTADO ---
        else:
            if "id_notion_automatico" not in st.session_state:
                with st.spinner("Mapeando tabelas integradas..."):
                    token_atual = st.session_state["token_notion_usuario"]
                    id_encontrado, nome_encontrado, todos_resultados = buscar_id_da_pagina_por_nome(token_atual, "Notes")

                    if id_encontrado:
                        st.session_state["id_notion_automatico"] = id_encontrado
                        st.session_state["nome_notion_automatico"] = nome_encontrado or "Página Conectada"
                        opcoes = [(r.get("title", [{}])[0].get("plain_text", "Sem nome") if r.get("title") else "Sem nome", r.get("id")) for r in todos_resultados]
                        st.session_state["opcoes_notion"] = opcoes
                    else:
                        st.session_state["id_notion_automatico"] = None
                        st.session_state["opcoes_notion"] = []

            id_final_tabela = st.session_state.get("id_notion_automatico")
            nome_pagina_detectada = st.session_state.get("nome_notion_automatico", "Notas")
            opcoes_disponiveis = st.session_state.get("opcoes_notion", [])

            st.markdown(f"""
                <div class="notion-card" style="border-left: 4px solid var(--accent);">
                    <p style="margin: 0; font-size: 14px; font-weight: 500;">Sessão ativa com o Notion corporativo.</p>
                </div>
            """, unsafe_allow_html=True)

            if id_final_tabela:
                if len(opcoes_disponiveis) > 1:
                    nomes_opcoes = [f"{nome}" for nome, _ in opcoes_disponiveis]
                    escolha = st.selectbox("Selecione a página de destino:", nomes_opcoes, index=0)
                    idx_escolhido = nomes_opcoes.index(escolha)
                    id_final_tabela = opcoes_disponiveis[idx_escolhido][1]
                else:
                    st.info(f"Página conectada atual: **{nome_pagina_detectada}**")

                if st.button("🚀 TRANSMITIR REGISTROS PARA O MEU NOTION", use_container_width=True):
                    barra_envio = st.progress(0)
                    sucessos, falhas = 0, 0
                    total_envio = len(df)
                    
                    for i, (_, row_envio) in enumerate(df.iterrows()):
                        if enviar_linha_para_notion(st.session_state["token_notion_usuario"], id_final_tabela, row_envio.to_dict()):
                            sucessos += 1
                        else:
                            falhas += 1
                        barra_envio.progress((i + 1) / total_envio)
                    
                    if falhas == 0:
                        st.toast(f"Sucesso! {sucessos} notas fiscais integradas.", icon="✨")
                    else:
                        st.markdown(f'<div class="error-box">Erro no envio: {falhas} falhas detectadas. Verifique a estrutura das notas compartilhadas.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="error-box">Nenhuma lista compatível foi encontrada no espaço Notion selecionado. Certifique-se de marcar a página ao autorizar.</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### 📥 Exportação Local Tradicional")
        col_export1, col_export2, col_export3 = st.columns(3, gap="medium")

        texto_txt = "".join(f"Arquivo: {r['Arquivo']}\nNF: {r['NF']}\nData: {r['Data de emissão']}\nProdutos: {r['Código do produto']}\nParceiro: {r['Código do parceiro']}\n{'-'*40}\n\n" for _, r in df.iterrows())
        csv_data = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        buffer_bytes = io.BytesIO()
        with pd.ExcelWriter(buffer_bytes, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='NFs')
        
        col_export1.download_button(label="TXT", data=texto_txt, file_name='dados_extraidos.txt', mime='text/plain', use_container_width=True)
        col_export2.download_button(label="CSV", data=csv_data, file_name='dados_extraidos.csv', mime='text/csv', use_container_width=True)
        col_export3.download_button(label="EXCEL", data=buffer_bytes.getvalue(), file_name='dados_extraidos.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', use_container_width=True)
else:
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("Como Usar:\n1. Acesse o painel lateral\n2. Selecione seus arquivos PDF\n3. O sistema processa automaticamente\n4. Exporte em TXT, CSV, Excel ou Notion")
        st.success("Dica: Você pode fazer upload de múltiplos PDFs simultaneamente.")

st.markdown("---")
st.markdown("<div style='text-align: center; padding: 20px 0;'><p style='font-size: 11px; color: var(--text-secondary);'>Make Distribuidora • ConsultaNF • 2.0</p></div>", unsafe_allow_html=True)
