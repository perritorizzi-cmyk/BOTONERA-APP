import streamlit as st
import pandas as pd
import urllib.parse

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Botonera Cordobesa", layout="wide")

COLOR_ROJO = "#8d1b1b"

# --- LOGIN ---
if "acceso" not in st.session_state:
    st.session_state["acceso"] = False

if not st.session_state["acceso"]:
    st.title("Acceso Clientes")
    usr = st.text_input("Usuario")
    psw = st.text_input("Contraseña", type="password")
    if st.button("INGRESAR"):
        if usr.strip().lower() == "botonera" and psw.strip() == "2026":
            st.session_state["acceso"] = True
            st.rerun()
        else:
            st.error("Usuario o clave incorrectos")
    st.stop()

# --- INICIALIZACIÓN ---
if "carrito" not in st.session_state:
    st.session_state.carrito = []
if "ver_pedido" not in st.session_state:
    st.session_state.ver_pedido = False

# 2. CARGA DE DATOS
@st.cache_data(ttl=60)
def cargar_precios():
    url = "https://docs.google.com/uc?export=download&id=1LTJJ-iXYdcl1gRhcbXaC0jw64J9Khzwo"
    try:
        data = pd.read_csv(url, encoding='latin1', on_bad_lines='skip', sep=None, engine='python')
        data = data.iloc[:, [0, 1, 2]]
        data.columns = ['Cod', 'Desc', 'Precio']
        # Limpiar precios
        data['Precio'] = data['Precio'].astype(str).str.replace(',', '.').str.extract(r'(\d+\.?\d*)').astype(float)
        return data
    except:
        return None

df = cargar_precios()
if df is None:
    st.error("Error al cargar datos. Refresca la página.")
    st.stop()

# 3. ENCABEZADO PERSONALIZADO
st.markdown(f"""
    <div style="text-align: center; padding: 10px;">
        <h2 style="color: {COLOR_ROJO}; font-family: 'Times New Roman', serif; margin-bottom: 0;">
            Botonera Cordobesa SA
        </h2>
        <h3 style="color: {COLOR_ROJO}; font-family: 'Times New Roman', serif; margin-top: 0; font-weight: normal;">
            Sarquis & Sepag
        </h3>
        <p style="color: #666; font-size: 0.9em; margin-top: -10px;">
            Horario de atención: Lunes a Viernes de 8:30 a 17:00 hs
        </p>
    </div>
""", unsafe_allow_html=True)

# Botón de Carrito (Solo si hay productos)
if st.session_state.carrito:
    n = len(st.session_state.carrito)
    if st.button(f"🛒 REVISAR MI PEDIDO ({n} productos)", use_container_width=True, type="primary"):
        st.session_state.ver_pedido = not st.session_state.ver_pedido
        st.rerun()

st.divider()

# 4. VISTA DEL PEDIDO (CARRITO)
if st.session_state.ver_pedido:
    st.subheader("Tu Lista de Pedido")
    total_general = 0.0
    
    for i, itm in enumerate(st.session_state.carrito):
        subtotal = it

