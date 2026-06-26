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

# --- CSS MINIMALISTA PREMIUM (COSMOS/LAYERS AESTHETIC) ---
FUTURISTIC_CSS = """
<style>
    :root {
        --bg-app: #09090b;
        --bg-sidebar: #09090b;
        --bg-card: #141416;
        --border-line: #222226;
        --accent: #3ecf9e;
        --accent-soft: rgba(62, 207, 158, 0.15);
        --text-white: #f4f4f5;
        --text-secondary: #a3a3a8;
    }
    
    @keyframes fadeInSlide {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes auroraAmbient {
        0% { background-position: 0% 50%; background-size: 200% 200%; }
        50% { background-position: 100% 50%; background-size: 200% 200%; }
        100% { background-position: 0% 50%; background-size: 200% 200%; }
    }
    
    @keyframes shimmerSwipe {
        0% { background-position: -1200px 0; }
        100% { background-position: 1200px 0; }
    }
    
    @keyframes shimmerText {
        0% { background-position: -2000px 0; }
        100% { background-position: 2000px 0; }
    }
    
    @keyframes breathingPulse {
        0%, 100% { box-shadow: inset 0 0 0 1px rgba(62, 207, 158, 0.2), 0 0 8px rgba(62, 207, 158, 0.08); }
        50% { box-shadow: inset 0 0 0 1px rgba(62, 207, 158, 0.4), 0 0 16px rgba(62, 207, 158, 0.16); }
    }
    
    @keyframes elasticPulse {
        0%, 100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(62, 207, 158, 0.08), inset 0 0 0 1px rgba(62, 207, 158, 0.15); }
        50% { transform: scale(1.03); box-shadow: 0 0 24px 4px rgba(62, 207, 158, 0.12), inset 0 0 0 2px rgba(62, 207, 158, 0.25); }
    }
    
    @keyframes rippleWave {
        0% { background-color: var(--bg-card); box-shadow: inset 0 0 0 0 rgba(62, 207, 158, 0); }
        50% { box-shadow: inset 0 0 0 4px rgba(62, 207, 158, 0.06); }
        100% { background-color: #1c1c1f; box-shadow: inset 0 0 0 0 rgba(62, 207, 158, 0); }
    }
    
    body, .stApp, [data-testid="stAppViewContainer"] {
        background: var(--bg-app) !important;
        background-image: 
            radial-gradient(circle at 20% 50%, rgba(62, 207, 158, 0.05) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(62, 207, 158, 0.03) 0%, transparent 60%) !important;
        animation: auroraAmbient 16s ease-in-out infinite !important;
        color: var(--text-white) !important;
    }
    
    * { color: var(--text-white); }
    
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-white) !important;
        font-weight: 500;
        letter-spacing: 0.05em;
        animation: fadeInSlide 0.7s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }
    
    [data-testid="stSidebar"] {
        background: rgba(9, 9, 11, 0.75) !important;
        backdrop-filter: blur(16px);
        border-right: 1px solid var(--border-line);
        -webkit-backdrop-filter: blur(16px);
    }
    
    /* Customização global para botões normais e link_buttons do Streamlit */
    .stButton > button, data-testid="stLinkButton" a, .stDownloadButton > button, [data-testid="stBaseLinkButton"] {
        background: transparent !important;
        border: 1px solid var(--border-line) !important;
        color: var(--text-secondary) !important;
        border-radius: 4px !important;
        padding: 10px 24px !important;
        font-weight: 500 !important;
        text-decoration: none !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    .stButton > button:hover, data-testid="stLinkButton" a:hover, .stDownloadButton > button:hover, [data-testid="stBaseLinkButton"]:hover {
        background: var(--accent-soft) !important;
        border-color: var(--accent) !important;
        color: var(--text-white) !important;
        transform: scale(1.02) translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(62, 207, 158, 0.16) !important;
    }
    
    .stTextInput > div > div > input {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-line) !important;
        color: var(--text-white) !important;
        border-radius: 4px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--accent) !important;
    }
    
    .stTable tbody tr:hover {
        animation: rippleWave 0.5s cubic-bezier(0.4, 0, 0.2, 1) forwards;
    }
    
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--accent) 0%, rgba(62, 207, 158, 0.5) 50%, var(--accent) 100%) !important;
        background-size: 1000px 100%;
        animation: shimmerSwipe 2s infinite !important;
        height: 2px !important;
    }
    
    .stFileUploader > div {
        background: var(--bg-card) !important;
        border: 2px dashed var(--border-line) !important;
        border-radius: 8px;
        animation: elasticPulse 3s ease-in-out infinite;
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
    
    payload_busca = {
        "query": nome_padrao,
        "filter": {"value": "database", "property": "object"},
        "page_size": 1
    }
    
    try:
        res = requests.post(url, json=payload_busca, headers=headers)
        if res.status_code == 200:
            resultados = res.json().get("results", [])
            if resultados:
                return resultados[0].get("id")
        
        payload_geral = {
            "filter": {"value": "database", "property": "object"},
            "page_size": 1
        }
        res_geral = requests.post(url, json=payload_geral, headers=headers)
        if res_geral.status_code == 200:
            resultados_gerais = res_geral.json().get("results", [])
            if resultados_gerais:
                return resultados_gerais[0].get("id")
                
        return None
    except Exception:
        return None

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

    if not itens and texto_completo:
        for linha in texto_completo.splitlines():
            linha_limpa = limpar_texto(linha)
            if re.search(r'\b(5101|5102|5405|5403|6101|6102)\b', linha_limpa):
                match_codigo = re.match(r'^["\']?(\d+)\b', linha_limpa)
                if match_codigo:
                    codigo = match_codigo.group(1)
                    if codigo not in itens and len(codigo) >= 3 and len(codigo) <= 7:
                        itens.append(codigo)
                        
    return itens

def extrair_codigo_parceiro(texto, linhas_pdf):
    texto_normalizado = re.sub(r'\s+', ' ', texto)

    match_canhoto = re.search(r'INDICADA\s+A[DQ]\s+LADO\s+(\d{3,8})', texto_normalizado, re.IGNORECASE)
    if match_canhoto:
        return match_canhoto.group(1)

    for indice, linha in enumerate(linhas_pdf):
        if re.search(r'NOME/RAZ[ÃA]O SOCIAL', linha, re.IGNORECASE):
            janela = ' '.join(linhas_pdf[indice:indice + 6])
            match = re.search(r'NOME/RAZ[ÃA]O SOCIAL\s+(.+?)\s+(\d{3,8})\b', janela, re.IGNORECASE)
            if match:
                codigo_candidato = match.group(2)
                if "." not in codigo_candidato and "-" not in codigo_candidato:
                    return codigo_candidato

    match_antes_cnpj = re.search(r'\b(\d{3,8})\s+\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}', texto_normalizado)
    if match_antes_cnpj:
        return match_antes_cnpj.group(1)
        
    match_antes_cpf = re.search(r'\b(\d{3,8})\s+\d{3}\.\d{3}\.\d{3}-\d{2}', texto_normalizado)
    if match_antes_cpf:
        return match_antes_cpf.group(1)

    match_generico = re.search(r'NOME/RAZ[ÃA]O SOCIAL.*?\b(\d{3,8})\b', texto_normalizado, re.IGNORECASE)
    if match_generico:
        codigo_candidato = match_generico.group(1)
        if codigo_candidato != "12228198":
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
                "NF": extrair_nf(texto_completo, lines:=linhas),
                "Data de emissão": "N/A",
                "Código do produto": "N/A",
                "Código do parceiro": "N/A"
            }

            match_data = re.search(
                r'EMISS[ÃA]O\D{0,20}(\d{2}/\d{2}/\d{4})',
                texto_completo,
                re.IGNORECASE
            )
            if not match_data:
                match_data = re.search(r'(\d{2}/\d{2}/\d{4})', texto_completo)
            if match_data:
                dados["Data de emissão"] = match_data.group(1)

            codigos_produtos = extrair_itens_produtos(pdf, texto_completo=texto_completo)
            dados["Código do produto"] = "\n".join(codigos_produtos) if codigos_produtos else "N/A"
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
            with st.spinner("Validando credenciais corporativas no Notion..."):
                resposta_oauth = obter_access_token(codigo_retorno)
                if resposta_oauth:
                    st.session_state["token_notion_usuario"] = resposta_oauth["access_token"]
                    if "duplicated_template_id" in resposta_oauth:
                        st.session_state["id_tabela_usuario"] = resposta_oauth["duplicated_template_id"]
                    st.toast("🔒 Conectado com sucesso ao Notion!", icon="✅")
                    st.query_params.clear()
                else:
                    st.error("Falha ao autenticar com o Notion. Entre em contato com o Diego ou tente novamente.")

        if "token_notion_usuario" not in st.session_state:
            url_notion_auth = gerar_link_notion()
            
            # Botão em HTML Puro estruturado para abrir na mesma guia (_top) sem bugar o clique
            st.markdown(f"""
                <a href="{url_notion_auth}" target="_top" style="
                    text-decoration: none; 
                    display: block; 
                    width: 100%;
                ">
                    <button style="
                        width: 100%;
                        background-color: transparent;
                        border: 1px solid var(--border-line);
                        color: var(--text-secondary);
                        border-radius: 4px;
                        padding: 10px 24px;
                        font-weight: 500;
                        font-size: 16px;
                        text-align: center;
                        cursor: pointer;
                        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                    " onmouseover="this.style.backgroundColor='var(--accent-soft)'; this.style.borderColor='var(--accent)'; this.style.color='var(--text-white)'; this.style.transform='scale(1.01) translateY(-2px)'; this.style.boxShadow='0 8px 24px rgba(62, 207, 158, 0.16)';" 
                       onmouseout="this.style.backgroundColor='transparent'; this.style.borderColor='var(--border-line)'; this.style.color='var(--text-secondary)'; this.style.transform='none'; this.style.boxShadow='none';">
                        🔑 CONECTAR MEU NOTION
                    </button>
                </a>
            """, unsafe_allow_html=True)
            
            st.caption("Cada colaborador precisa se autenticar uma vez por sessão para enviar os dados para seu respectivo espaço de trabalho.")
        else:
            st.success("✅ Você está conectado no Notion.")
            
            if "id_notion_automatico" not in st.session_state or not st.session_state["id_notion_automatico"]:
                with st.spinner("Localizando sua página de destino no Notion..."):
                    token_atual = st.session_state["token_notion_usuario"]
                    
                    url_busca = "https://api.notion.com/v1/search"
                    headers_busca = {"Authorization": f"Bearer {token_atual}", "Notion-Version": "2022-06-28"}
                    
                    id_encontrado = buscar_id_da_pagina_por_nome(token_atual, "Notes")
                    
                    if id_encontrado:
                        st.session_state["id_notion_automatico"] = id_encontrado
                        
                        try:
                            res_nome = requests.get(f"https://api.notion.com/v1/databases/{id_encontrado}", headers=headers_busca)
                            nome_real = res_nome.json().get("title", [{}])[0].get("plain_text", "Minha Lista")
                            st.session_state["nome_notion_automatico"] = nome_real
                        except:
                            st.session_state["nome_notion_automatico"] = "Página Conectada"
                    else:
                        st.session_state["id_notion_automatico"] = None

            id_final_tabela = st.session_state.get("id_notion_automatico")
            nome_pagina_detectada = st.session_state.get("nome_notion_automatico", "Notas")

            if id_final_tabela:
                if st.button("🚀 TRANSMITIR REGISTROS PARA O MEU NOTION"):
                    barra_envio = st.progress(0)
                    sucessos, falhas = 0, 0
                    total_envio = len(df)
                    
                    with st.spinner("Enviando linhas..."):
                        for i, (_, row_envio) in enumerate(df.iterrows()):
                            if enviar_linha_para_notion(st.session_state["token_notion_usuario"], id_final_tabela, row_envio.to_dict()):
                                sucessos += 1
                            else:
                                falhas += 1
                            barra_envio.progress((i + 1) / total_envio)
                    
                    if falhas == 0:
                        st.success(f"✨ Pronto! {sucessos} notas fiscais geradas com sucesso na sua página")
                    else:
                        st.error(f"🔴 Erro no envio: {falhas} falhas detectadas. Verifique a estrutura das suas notas.")
            else:
                st.error("❌ Nenhuma página ou lista de notas foi encontrada no seu Notion.")
                st.warning("Certifique-se de que você selecionou e marcou a caixinha de pelo menos uma página ao clicar no botão 'Conectar meu Notion'.")

        st.markdown("---")
        st.markdown("#### 📥 Exportação Local Tradicional")
        col_export1, col_export2, col_export3 = st.columns(3, gap="medium")

        texto_txt = "".join(f"Arquivo: {r['Arquivo']}\nNF: {r['NF']}\nData: {r['Data de emissão']}\nProdutos: {r['Código do produto']}\nParceiro: {r['Código do parceiro']}\n{'-'*40}\n\n" for _, r in df.iterrows())
        csv_data = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        buffer_bytes = io.BytesIO()
        with pd.ExcelWriter(buffer_bytes, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='NFs')
        
        col_export1.download_button(label=" TXT", data=texto_txt, file_name='dados_extraidos.txt', mime='text/plain', use_container_width=True)
        col_export2.download_button(label=" CSV", data=csv_data, file_name='dados_extraidos.csv', mime='text/csv', use_container_width=True)
        col_export3.download_button(label=" EXCEL", data=buffer_bytes.getvalue(), file_name='dados_extraidos.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', use_container_width=True)
else:
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("Como Usar:\n1. Acesse o painel lateral\n2. Selecione seus arquivos PDF\n3. O sistema processa automaticamente\n4. Exporte em TXT, CSV, Excel ou Notion")
        st.success("Dica: Você pode fazer upload de múltiplos PDFs simultaneamente.")

st.markdown("---")
st.markdown("<div style='text-align: center; padding: 20px 0;'><p style='font-size: 11px; color: var(--text-secondary);'>Make Distribuidora • ConsultaNF • 2.0</p></div>", unsafe_allow_html=True)
