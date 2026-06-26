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

# --- CSS MINIMALISTA PREMIUM ---
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
    
    body, .stApp, [data-testid="stAppViewContainer"] {
        background: var(--bg-app) !important;
        color: var(--text-white) !important;
    }
    
    * { color: var(--text-white); }
    
    [data-testid="stSidebar"] {
        background: rgba(9, 9, 11, 0.75) !important;
        backdrop-filter: blur(16px);
        border-right: 1px solid var(--border-line);
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
# LÓGICA AUXILIAR DE INTEGRAÇÃO MULTI-USUÁRIO (NOTION OAUTH)
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
    except requests.RequestException:
        return None

def listar_databases_disponiveis(token):
    url = "https://api.notion.com/v1/search"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    payload = {
        "filter": {"value": "database", "property": "object"},
        "page_size": 50
    }
    try:
        res = requests.post(url, json=payload, headers=headers)
        if res.status_code == 200:
            resultados = res.json().get("results", [])
            lista_final = []
            for db in resultados:
                db_id = db.get("id")
                titulos = db.get("title", [])
                nome_db = titulos[0].get("plain_text", "Sem título") if titulos else "Tabela sem nome"
                lista_final.append({"id": db_id, "title": nome_db})
            return lista_final
        return []
    except Exception:
        return []

def enviar_linha_para_notion(token, database_id, dados):
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    nome_arquivo = str(dados.get("Arquivo", "N/A"))
    numero_nf = str(dados.get("NF", "N/A"))
    data_emissao = str(dados.get("Data de emissão", "N/A"))
    cod_produto = str(dados.get("Código do produto", "N/A"))
    cod_parceiro = str(dados.get("Código do parceiro", "N/A"))

    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "title": [{"type": "text", "text": {"content": nome_arquivo}}]
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
    except Exception:
        return False

# ============================================================================
# FUNÇÕES DE EXTRAÇÃO
# ============================================================================
def limpar_texto(valor):
    return re.sub(r'\s+', ' ', (valor or '')).strip()

def extrair_nf(texto, linhas_pdf):
    padroes_nf = [
        r'\bN\.?\s*(\d{1,3}(?:\.\d{3})*|\d{3,})\b',
        r'\bNF[-\s]*e?\s*(?:n[ºo]\.?|n[úu]mero)?\s*[:\-]?\s*(\d{3,})\b'
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
                for celula in valores:
                    if re.fullmatch(r'\d{3,}', celula) and celula not in itens:
                        itens.append(celula)
                        break
    return itens

def extrair_codigo_parceiro(texto, linhas_pdf):
    texto_normalizado = re.sub(r'\s+', ' ', texto)
    match_canhoto = re.search(r'INDICADA\s+A[DQ]\s+LADO\s+(\d{3,8})', texto_normalizado, re.IGNORECASE)
    if match_canhoto: return match_canhoto.group(1)
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
                "Código do parceiro": extrair_codigo_parceiro(texto_completo, linhas)
            }
            match_data = re.search(r'(\d{2}/\d{2}/\d{4})', texto_completo)
            if match_data: dados["Data de emissão"] = match_data.group(1)
            
            codigos = extrair_itens_produtos(pdf, texto_completo)
            dados["Código do produto"] = "\n".join(codigos) if codigos else "N/A"
            return dados
    except Exception as e:
        return {"NF": "Erro", "Data de emissão": str(e), "Código do produto": "Erro", "Código do parceiro": "Erro"}

# --- HEADER ---
st.markdown("<h1 style='text-align: center;'>CONSULTA NF</h1>", unsafe_allow_html=True)
st.divider()

# --- SIDEBAR CONTROL PANEL ---
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
        st.dataframe(df, use_container_width=True, hide_index=True)

    with tab2:
        st.metric("ARQUIVOS PROCESSADOS", len(df))

    with tab3:
        st.markdown("### 🌐 Integração Corporativa Cloud")
        
        parametros_url = st.query_params
        if "code" in parametros_url and "token_notion_usuario" not in st.session_state:
            codigo_retorno = parametros_url["code"]
            resposta_oauth = obter_access_token(codigo_retorno)
            if resposta_oauth:
                st.session_state["token_notion_usuario"] = resposta_oauth["access_token"]
                st.session_state["databases_disponiveis"] = None 
                st.toast("🔒 Conectado ao Notion!", icon="✅")
                st.query_params.clear()

        if "token_notion_usuario" not in st.session_state:
            url_notion_auth = gerar_link_notion()
            
            # --- CORREÇÃO DEFINITIVA USANDO JAVASCRIPT EM ONCLICK ---
            # O window.top.location.href força o navegador pai a ir para o link sem sofrer bloqueio do sandbox
            st.markdown(f"""
                <div style="text-align: center; width: 100%;">
                    <button onclick="window.top.location.href='{url_notion_auth}'" style="
                        display: block;
                        width: 100%;
                        background-color: transparent;
                        border: 1px solid #222226;
                        color: #3ecf9e;
                        border-radius: 4px;
                        padding: 12px 24px;
                        font-weight: 600;
                        font-size: 14px;
                        letter-spacing: 0.05em;
                        cursor: pointer;
                        box-sizing: border-box;
                        transition: all 0.3s ease;
                    " onmouseover="this.style.backgroundColor='rgba(62, 207, 158, 0.15)'; this.style.borderColor='#3ecf9e'; this.style.color='#f4f4f5';" 
                       onmouseout="this.style.backgroundColor='transparent'; this.style.borderColor='#222226'; this.style.color='#3ecf9e';">
                        🔑 CONECTAR MEU NOTION
                    </button>
                </div>
            """, unsafe_allow_html=True)
            st.caption("Cada colaborador precisa se autenticar uma vez por sessão.")
        else:
            st.success("✅ Você está conectado ao Notion.")
            token_atual = st.session_state["token_notion_usuario"]
            
            if "databases_disponiveis" not in st.session_state or not st.session_state["databases_disponiveis"]:
                st.session_state["databases_disponiveis"] = listar_databases_disponiveis(token_atual)

            lista_dbs = st.session_state.get("databases_disponiveis", [])

            if lista_dbs:
                opcoes_tela = [f"📊 {item['title']} ({item['id'][:8]}...)" for item in lista_dbs]
                selecao = st.selectbox("Selecione qual tabela do seu Notion deseja usar:", opciones_tela)
                
                indice_selecionado = opciones_tela.index(selecao)
                id_final_tabela = lista_dbs[indice_selecionado]["id"]
                
                if st.button("🚀 TRANSMITIR REGISTROS PARA O MEU NOTION"):
                    barra_envio = st.progress(0)
                    sucessos, total_envio = 0, len(df)
                    
                    for i, (_, row_envio) in enumerate(df.iterrows()):
                        if enviar_linha_para_notion(token_atual, id_final_tabela, row_envio.to_dict()):
                            sucessos += 1
                        barra_envio.progress((i + 1) / total_envio)
                    st.success(f"✨ Concluído! {sucessos} notas fiscais integradas.")
            else:
                st.error("❌ Nenhuma tabela encontrada. Verifique se você deu permissão às páginas ao logar.")
