import streamlit as st
import pandas as pd
import urllib.parse
import base64
import requests

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Botonera Cordobesa SA", page_icon="🧵", layout="wide")

COLOR_BORDEAUX = "#8d1b1b"

# ESTILO CSS PARA DESTACAR EL BUSCADOR Y TARJETAS
st.markdown(f"""
    <style>
    /* --- BUSCADOR ULTRA DESTACADO --- */
    .stTextInput > div > div > input {{
        border: 4px solid {COLOR_BORDEAUX} !important;
        border-radius: 15px !important;
        padding: 20px !important;
        font-size: 1.3em !important;
        background-color: #fdfdfd !important;
        box-shadow: 0 8px 16px rgba(141, 27, 27, 0.15) !important;
        color: #333 !important;
    }}
    
    /* Etiquetas de los campos (Color o número) */
    label {{
        color: #333 !important;
        font-weight: bold !important;
    }}

    /* Tarjetas de productos */
    .producto-card {{ 
        background-color: #ffffff !important; 
        padding: 15px; 
        border-radius: 12px; 
        border-left: 6px solid {COLOR_BORDEAUX}; 
        box-shadow: 2px 4px 10px rgba(0,0,0,0.1); 
        margin-bottom: 12px;
    }}
    .titulo-prod {{ color: #1a1a1a !important; font-weight: bold; font-size: 1.15em; display: block; }}
    .subtitulo-prod {{ color: #555555 !important; font-size: 0.85em; }}
    .precio-prod {{ color: {COLOR_BORDEAUX} !important; font-weight: bold; font-size: 1.3em; margin-top: 5px; display: block; }}
    
    /* Botones */
    .stButton>button {{ 
        background-color: {COLOR_BORDEAUX}; 
        color: white !important; 
        border-radius: 10px; 
        font-weight: bold; 
        height: 3.5em;
        width: 100%;
    }}
    </style>
    """, unsafe_allow_html=True)

# 2. FUNCIÓN PARA CARGAR EL LOGO (S&S Y BOTONERA)
def get_base64_logo(url):
    try:
        response = requests.get(url)
        return base64.b64encode(response.content).decode()
    except:
        return None

# 3. ENCABEZADO (Logo Combinado)
logo_url = "https://static.wixstatic.com/media/893674_2f7f985a113d42f582a85710a309f488~mv2.png"
logo_base64 = get_base64_logo(logo_url)

if logo_base64:
    st.markdown(
        f'<div style="text-align
