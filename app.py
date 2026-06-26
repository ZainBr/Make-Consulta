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
    
    .stButton > button {
        background: transparent !important;
        border: 1px solid var(--border-line) !important;
        color: var(--text-secondary) !important;
        border-radius: 4px;
        padding: 10px 24px;
        font-weight: 500;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .stButton > button:hover {
        background: var(--accent-soft) !important;
        border-color: var(--accent) !important;
        color: var(--text-white) !important;
        transform: scale(1.02) translateY(-2px);
        box-shadow: 0 8px 24px rgba(62, 207, 158, 0.16);
    }
    
    [data-testid="stDownloadButton"] > button {
        background: transparent !important;
        border: 1px solid var(--border-line) !important;
        color: var(--text-secondary) !important;
        border-radius: 4px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    [data-testid="stDownloadButton"] > button:hover {
        background: var(--accent-soft) !important;
        border-color: var(--accent) !important;
        color: var(--text-white) !important;
        transform: scale(1.02) translateY(-2px);
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
    base_url =
