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

try:
    headers = st.context.headers
    host = headers.get("Host", "")
    
    if "localhost" in host or "127.0.0.1" in host:
        REDIRECT_URI = "http://localhost:8501/"
    else:
        REDIRECT_URI = "https://make-consulta-xvbe6b9ut9es6i6bbemudm.streamlit.app/"
except Exception:
    REDIRECT_URI = "https://make-consulta-xvbe6b9ut9es6i6bbemudm.streamlit.app/"

# --- CSS PREMIUM GLASSMORPHISM COM EFEITOS ESPECIAIS ---
FUTURISTIC_CSS = """
<style>
    /* --- CORES CORPORATIVAS FIXAS --- */
    :root {
        --bg-app: #030f0a !important;       /* Verde escuro profundo de fundo */
        --bg-sidebar: rgba(2, 11, 8, 0.85) !important; /* Sidebar translúcida */
        --bg-card-glass: rgba(8, 34, 24, 0.65) !important; /* Janelas Flutuantes Translúcidas */
        --border-glass: rgba(0, 168, 84, 0.25) !important;  /* Borda esmeralda sutil */
        --accent: #00a854 !important;       /* Verde oficial da marca */
        --accent-hover: #00c261 !important;
        --text-white: #ffffff !important;   
        --text-secondary: #a3b8b0 !important;
        
        --bg-error-glass: rgba(139, 9, 9, 0.3) !important;
        --border-error: rgba(255, 118, 118, 0.4) !important;
    }

    /* --- ANIMAÇÕES ESPECIAIS --- */
    @keyframes floatWindow {
        0% { transform: translateY(0px); box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3); }
        50% { transform: translateY(-6px); box-shadow: 0 15px 35px 0 rgba(0, 168, 84, 0.15); }
        100% { transform: translateY(0px); box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3); }
    }

    @keyframes glowPulse {
        0% { border-color: rgba(0, 168, 84, 0.2); }
        50% { border-color: rgba(0, 242, 121, 0.5); }
        100% { border-color: rgba(0, 168, 84, 0.2); }
    }

    /* --- UNIFICAÇÃO DO DESIGN DO APLICATIVO --- */
    body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: var(--bg-app) !important;
        background-image: radial-gradient(circle at 50% 0%, rgba(0, 168, 84, 0.12) 0%, transparent 75%) !important;
        color: var(--text-white) !important;
    }

    [data-testid="stHeader"] {
        background-color: transparent !important;
    }

    /* --- SIDEBAR FLUTUANTE TRANSLÚCIDA --- */
    [data-testid="stSidebar"], [data-testid="stSidebar"] section {
        background-color: var(--bg-sidebar) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-right: 1px solid var(--border-glass) !important;
    }
    
    [data-testid="stSidebar"] *, [data-testid="stSidebar"] label, [data-testid="stSidebar"] p {
        color: var(--text-white) !important;
    }

    /* --- JANELAS FLUTUANTES (EFFECT GLASSMORPHISM) --- */
    .notion-card, div[data-testid="stNotification"], .stAlert {
        background: var(--bg-card-glass) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: 14px !important;
        padding: 24px !important;
        margin: 18px 0 !important;
        animation: floatWindow 6s ease-in-out infinite, glowPulse 4s infinite;
    }

    /* --- ABAS (TABS) CUSTOMIZADAS --- */
    button[data-baseweb="tab"] {
        color: var(--text-secondary) !important;
        background-color: transparent !important;
        border: none !important;
        padding: 10px 20px !important;
    }
    
    button[data-baseweb="tab"][aria-selected="true"] {
        color: var(--accent) !important;
        border-bottom: 3px solid var(--accent) !important;
        font-weight: bold !important;
    }

    /* --- BARRA DE PROGRESSO COM BRILHO --- */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--accent), #00ff7f, var(--accent)) !important;
        box-shadow: 0 0 10px var(--accent);
    }

    /* --- BOTÕES NO PADRÃO DA MARCA --- */
    .stButton > button, [data-testid="stDownloadButton"] > button {
        background-color: var(--accent) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        width: 100% !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    .stButton > button:hover, [data-testid="stDownloadButton"] > button:hover {
        background-color: var(--accent-hover) !important;
        transform: scale(1.01) translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(0, 168, 84, 0.4) !important;
    }

    /* CAIXA DE UPLOAD COESA */
    [data-testid="stFileUploaderDropzone"] {
        background-color: rgba(8, 34, 24, 0.4) !important;
        border: 2px dashed var(--border-glass) !important;
        border-radius: 12px !important;
    }

    /* CAIXA DE ERRO PREMIUM GLASS */
    .error-box {
        background: var(--bg-error-glass) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid var(--border-error) !important;
        color: #ff7676 !important;
        padding: 14px;
        border-radius: 10px;
        font-size: 14px;
        margin: 10px 0;
    }

    @media (max-width: 768px) {
        .stColumns { flex-direction: column !important; gap: 12px !important; }
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
            {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": f"NF: {numero_nf}"}}]}},
            {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": f"EMISSAO: {data_emissao}"}}]}},
            {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": f"PARCEIRO: {cod_parceiro}"}}]}},
            {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": f"COD:\n{cod_produto}"}}]}}
        ]
    }
    
    try:
        res = requests.post(url, json=payload, headers=headers)
        return res.status_code == 200
    except requests.RequestException:
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
            if titulo: return titulo[0].get("plain_text", "Sem nome")
        except: pass
        return "Sem nome"

    def _is_database_valido(resultado):
        return resultado.get("object") == "database" and resultado.get("id")

    try:
        payload_busca = {"query": nome_padrao, "filter": {"value": "database", "property": "object"}, "page_size": 10}
        res = requests.post(url, json=payload_busca, headers=headers)
        if res.status_code == 200:
            resultados = [r for r in res.json().get("results", []) if _is_database_valido(r)]
            if resultados: return resultados[0].get("id"), _get_nome_database(resultados[0]), resultados

        payload_geral = {"filter": {"value": "database", "property": "object"}, "page_size": 10}
        res_geral = requests.post(url, json=payload_geral, headers=headers)
        if res_geral.status_code == 200:
            resultados_gerais = [r for r in res_geral.json().get("results", []) if _is_database_valido(r)]
            if resultados_gerais: return resultados_gerais[0].get("id"), _get_nome_database(resultados_gerais[0]), resultados_gerais
    except Exception: pass
    return None, None, []

# --- HEADER ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
        <div style="text-align: center; padding: 40px 0 20px 0;">
            <h1 style="margin: 0; font-size: 28px; letter-spacing: 0.15em; text-transform: uppercase; color: #ffffff;">CONSULTA NF</h1>
            <p style="margin: 12px 0 0 0; font-size: 12px; letter-spacing: 0.08em; color: var(--text-secondary); text-transform: uppercase;">Extração de Notas Fiscais • Make Distribuidora</p>
        </div>
    """, unsafe_allow_html=True)

st.divider()

if not PDFPLUMBER_AVAILABLE:
    st.error("⚠️ **AVISO CRÍTICO** - Execute `pip install pdfplumber` para ativar a extração de PDF.")
    st.stop()

# ============================================================================
# FUNÇÕES DE EXTRAÇÃO
# ============================================================================

def limpar_texto(valor):
    return re.sub(r'\s+', ' ', (valor or '')).strip()

def extrair_nf(texto, linhas_pdf):
    padroes_nf = [r'\bN\.?\s*(\d{1,3}(?:\.\d{3})*|\d{3,})\b', r'\bNF[-\s]*e?\s*(?:n[ºo]\.?|n[úu]mero)?\s*[:\-]?\s*(\d{3,})\b']
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
                if ('CÓD' in cabecalho and 'PROD' in cabecalho) or ('DESCRIÇÃO' in cabecalho and 'PRODUTO' in cabecalho): continue
                for indice, celula in enumerate(valores):
                    if re.fullmatch(r'\d{3,}', celula):
                        if indice + 1 < len(valores) and not any(item == celula for item in itens): itens.append(celula)
                        break
    if not itens and texto_completo:
        for linha in texto_completo.splitlines():
            linha_limpa = limpar_texto(linha)
            if re.search(r'\b(5101|5102|5405|5403|6101|6102)\b', linha_limpa):
                match_codigo = re.match(r'^["\']?(\d+)\b', linha_limpa)
                if match_codigo:
                    codigo = match_codigo.group(1)
                    if codigo not in itens and 3 <= len(codigo) <= 7: itens.append(codigo)
    return itens

def extrair_codigo_parceiro(texto, linhas_pdf):
    texto_normalizado = re.sub(r'\s+', ' ', texto)
    match_canhoto = re.search(r'INDICADA\s+A[DQ]\s+LADO\s+(\d{3,8})', texto_normalizado, re.IGNORECASE)
    if match_canhoto: return match_canhoto.group(1)

    for indice, linha in enumerate(linhas_pdf):
        if re.search(r'NOME/RAZ[ÃA]O SOCIAL', linha, re.IGNORECASE):
            janela = ' '.join(linhas_pdf[indice:indice + 6])
            match = re.search(r'NOME/RAZ[ÃA]O SOCIAL\s+(.+?)\s+(\d{3,8})\b', janela, re.IGNORECASE)
            if match and "." not in match.group(2) and "-" not in match.group(2): return match.group(2)
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

            dados = {"NF": extrair_nf(texto_completo, lines_pdf=linhas), "Data de emissão": "N/A", "Código do produto": "N/A", "Código do parceiro": "N/A"}
            match_data = re.search(r'EMISS[ÃA]O\D{0,20}(\d{2}/\d{2}/\d{4})', texto_completo, re.IGNORECASE)
            if not match_data: match_data = re.search(r'(\d{2}/\d{2}/\d{4})', texto_completo)
            if match_data: dados["Data de emissão"] = match_data.group(1)

            codigos_produtos = extrair_itens_produtos(pdf, texto_completo=texto_completo)
            dados["Código do produto"] = "\n".join(codigos_produtos) if codigos_produtos else "N/A"
            dados["Código do parceiro"] = extrair_codigo_parceiro(texto_completo, linhas)
            return dados
    except Exception as e:
        return {"NF": "Erro", "Data de emissão": str(e), "Código do produto": "Erro", "Código do parceiro": "Erro"}

# --- PAINEL LATERAL ---
st.sidebar.markdown('<div style="padding: 10px 0;"><h2 style="text-align: center; margin: 0; font-size: 14px; letter-spacing: 0.08em; text-transform: uppercase;">Painel de Controle</h2></div>', unsafe_allow_html=True)
st.sidebar.divider()
st.sidebar.subheader("📁 Selecione seus arquivos PDF")
uploaded_files = st.sidebar.file_uploader("Arraste os arquivos para cá", type="pdf", accept_multiple_files=True)

if uploaded_files:
    total_files = len(uploaded_files)
    lista_resultados = []
    progress_bar = st.progress(0)

    for idx, file in enumerate(uploaded_files):
        dados = extrair_dados_nf(file.read(), file.name)
        dados['Arquivo'] = file.name
        lista_resultados.append(dados)
        progress_bar.progress((idx + 1) / total_files)

    df = pd.DataFrame(lista_resultados)
    df = df[['Arquivo', 'NF', 'Data de emissão', 'Código do produto', 'Código do parceiro']]

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
            with st.spinner("Validando credenciais..."):
                resposta_oauth = obter_access_token(codigo_retorno)
                if resposta_oauth:
                    st.session_state["token_notion_usuario"] = resposta_oauth["access_token"]
                    st.toast("Conectado com sucesso ao Notion!", icon="🦖")
                    st.query_params.clear()
                else:
                    st.markdown('<div class="error-box">Falha ao autenticar com o Notion. Tente novamente.</div>', unsafe_allow_html=True)

        if "token_notion_usuario" not in st.session_state:
            url_notion_auth = gerar_link_notion()
            st.link_button("🔑 CONECTAR MEU NOTION", url_notion_auth)
        else:
            if "id_notion_automatico" not in st.session_state:
                with st.spinner("Localizando suas páginas..."):
                    token_atual = st.session_state["token_notion_usuario"]
                    id_encontrado, nome_encontrado, todos_resultados = buscar_id_da_pagina_por_nome(token_atual, "Notes")
                    if id_encontrado:
                        st.session_state["id_notion_automatico"] = id_encontrado
                        st.session_state["nome_notion_automatico"] = nome_encontrado or "Página Conectada"
                        st.session_state["opcoes_notion"] = [(r.get("title", [{}])[0].get("plain_text", "Sem nome") if r.get("title") else "Sem nome", r.get("id")) for r in todos_resultados]
                    else:
                        st.session_state["id_notion_automatico"] = None
                        st.session_state["opcoes_notion"] = []

            id_final_tabela = st.session_state.get("id_notion_automatico")
            nome_pagina_detectada = st.session_state.get("nome_notion_automatico", "Notas")
            opcoes_disponiveis = st.session_state.get("opcoes_notion", [])

            if id_final_tabela:
                st.markdown(f'<div class="notion-card" style="border-left: 4px solid var(--accent); padding: 12px 20px;">Sessão ativa com o Notion corporativo: <b>{nome_pagina_detectada}</b></div>', unsafe_allow_html=True)
                if len(opcoes_disponiveis) > 1:
                    nomes_opcoes = [f"{nome}" for nome, _ in opcoes_disponiveis]
                    escolha = st.selectbox("Escolher outra página (opcional):", nomes_opcoes, index=0)
                    id_final_tabela = opcoes_disponiveis[nomes_opcoes.index(escolha)][1]

                if st.button("🚀 TRANSMITIR REGISTROS PARA O MEU NOTION"):
                    barra_envio = st.progress(0)
                    sucessos = 0
                    total_envio = len(df)
                    
                    for i, (_, row_envio) in enumerate(df.iterrows()):
                        if enviar_linha_para_notion(st.session_state["token_notion_usuario"], id_final_tabela, row_envio.to_dict()):
                            sucessos += 1
                        barra_envio.progress((i + 1) / total_envio)
                    
                    # --- COMPONENTE FIXO DE SUCESSO COM O DINOSSAURO ---
                    st.toast(f"Sucesso! {sucessos} notas integradas.", icon="🦖")
                    st.markdown(f"""
                        <div class="notion-card" style="border: 1px solid var(--accent); background: rgba(0, 168, 84, 0.15); margin-top: 15px;">
                            <span style="color: #00ff7f; font-weight: bold;">🦖 [Ref: S1126F-HPA]</span> 
                            Transmissão efetuada com sucesso no ambiente corporativo da Distribuidora.
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown('<div class="error-box">Nenhuma lista compatível foi encontrada no seu Notion. Verifique as permissões.</div>', unsafe_allow_html=True)

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
        st.info("Como Usar:\n1. Acesse o painel lateral\n2. Selecione seus arquivos PDF\n3. O sistema processa automaticamente")

st.markdown("---")
st.markdown("<div style='text-align: center; padding: 20px 0;'><p style='font-size: 11px; color: var(--text-secondary);'>Make Distribuidora • ConsultaNF • 2.0</p></div>", unsafe_allow_html=True)
