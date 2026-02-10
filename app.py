import streamlit as st
import pandas as pd
import urllib.parse

# 1. CONFIGURACIÓN GENERAL
st.set_page_config(page_title="Botonera Cordobesa SA", layout="wide")
COLOR_ROJO = "#8d1b1b"

# Estilos visuales forzados para que nada sea invisible
st.markdown(f"""
    <style>
    h1, h2, h3, b {{ color: {COLOR_ROJO} !important; font-family: 'serif'; }}
    .stButton>button {{ background-color: {COLOR_ROJO}; color: white !important; font-weight: bold; border-radius: 10px; }}
    .stTextInput>div>div>input {{ border: 2px solid {COLOR_ROJO} !important; }}
    /* Caja de Total Reforzada */
    .caja-total {{
        background-color: {COLOR_ROJO};
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        margin: 20px 0;
        border: 3px solid #000;
    }}
    .texto-total {{
        color: white !important;
        font-size: 35px !important;
        font-weight: bold !important;
        margin: 0;
    }}
    </style>
""", unsafe_allow_html=True)

# 2. ENCABEZADO INSTITUCIONAL
st.markdown(f"""
    <div style="text-align: center; border-bottom: 3px solid {COLOR_ROJO}; padding-bottom: 10px; margin-bottom: 20px;">
        <h1 style="margin:0; font-size: 2.2em; color: {COLOR_ROJO};">Botonera Cordobesa SA</h1>
        <h1 style="margin:0; font-size: 2.2em; color: {COLOR_ROJO};">Sarquis & Sepag</h1>
        <p style="margin:5px; color: #444; font-size: 1.1em;"><b>Horario:</b> Lunes a Viernes de 8:30 a 17:00 hs</p>
    </div>
""", unsafe_allow_html=True)

# 3. ACCESO SEGURIDAD
if "auth" not in st.session_state: st.session_state["auth"] = False

if not st.session_state["auth"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("🔐 Acceso Clientes")
        u = st.text_input("Usuario", key="u_login")
        p = st.text_input("Contraseña", type="password", key="p_login")
        if st.button("INGRESAR AL SISTEMA", use_container_width=True):
            if u.strip().lower() == "botonera" and p.strip() == "2026":
                st.session_state["auth"] = True
                st.rerun()
            else:
                st.error("Credenciales incorrectas")
    st.stop()

# 4. CARGA DE DATOS (SIN LÍMITES)
if "carrito" not in st.session_state: st.session_state.carrito = []
if "ver_pedido" not in st.session_state: st.session_state.ver_pedido = False

@st.cache_data(ttl=300)
def cargar_base():
    url = "https://docs.google.com/uc?export=download&id=1LTJJ-iXYdcl1gRhcbXaC0jw64J9Khzwo"
    try:
        data = pd.read_csv(url, encoding='latin1', on_bad_lines='skip', sep=None, engine='python')
        data = data.iloc[:, [0, 1, 2]]
        data.columns = ['Cod', 'Desc', 'Precio']
        data['Precio'] = data['Precio'].astype(str).str.replace(',', '.').str.extract(r'(\d+\.?\d*)').astype(float)
        return data
    except: return None

df = cargar_base()

# 5. INTERFAZ DE PEDIDO
if st.session_state.carrito:
    if st.button(f"🛒 REVISAR MI PEDIDO ({len(st.session_state.carrito)} ítems)", use_container_width=True):
        st.session_state.ver_pedido = not st.session_state.ver_pedido
        st.rerun()

st.divider()

if st.session_state.ver_pedido:
    st.markdown("<h2 style='text-align:center;'>Resumen de Pedido</h2>", unsafe_allow_html=True)
    total_gral = 0.0
    
    for i, itm in enumerate(st.session_state.carrito):
        sub = itm['precio'] * itm['cant']
        total_gral += sub
        c1, c2 = st.columns([4, 1])
        c1.write(f"**{itm['cant']}x** {itm['desc']} (Col: {itm['color']}) - ${sub:,.2f}")
        if c2.button("❌", key=f"del_{i}"):
            st.session_state.carrito.pop(i)
            st.rerun()

