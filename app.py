import streamlit as st
import pandas as pd
import urllib.parse

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Botonera Cordobesa SA", page_icon="🧵", layout="wide")

# 2. ESTILO PERSONALIZADO (CSS)
COLOR_MARCA = "#8d1b1b"

st.markdown(f"""
    <style>
    .stButton>button {{
        background-color: {COLOR_MARCA};
        color: white;
        border-radius: 8px;
        font-weight: bold;
        border: none;
        height: 3em;
        transition: 0.3s;
    }}
    .stButton>button:hover {{
        background-color: #5a0000;
        border: 1px solid white;
    }}
    .producto-card {{
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid {COLOR_MARCA};
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }}
    </style>
    """, unsafe_allow_html=True)

# 3. CABECERA CON LOGOTIPO
col1, col2 = st.columns([1, 4])
with col1:
    # Logo oficial de tu sitio web
    logo_url = "https://static.wixstatic.com/media/893674_2f7f985a113d42f582a85710a309f488~mv2.png"
    st.image(logo_url, width=150)
with col2:
    st.markdown(f"<h1 style='color:{COLOR_MARCA}; margin-bottom:0;'>Botonera Cordobesa SA</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:1.2em; margin-top:0;'>Catálogo de Pedidos Mayoristas</p>", unsafe_allow_html=True)

st.divider()

# 4. CARGA DE DATOS (GOOGLE DRIVE)
FILE_ID = "1LTJJ-iXYdcl1gRhcbXaC0jw64J9Khzwo"
SHEET_URL = f"https://docs.google.com/uc?export=download&id={FILE_ID}"

@st.cache_data(ttl=600)
def load_data():
    # Cargamos el archivo ignorando errores de filas y con codificación latina
    df = pd.read_csv(SHEET_URL, encoding='latin1', on_bad_lines='skip', sep=None, engine='python')
    df = df.iloc[:, [0, 1, 2]] # Columnas A, B y C
    df.columns = ['Código', 'Descripción', 'Precio']
    return df

try:
    df = load_data()
    if 'carrito' not in st.session_state:
        st.session_state.carrito = []

    # Buscador principal
    busqueda = st.text_input("🔍 ¿Qué producto buscás? (E
