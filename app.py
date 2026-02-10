import streamlit as st
import pandas as pd
import urllib.parse

# 1. CONFIGURACIÓN INICIAL
st.set_page_config(page_title="Botonera Cordobesa SA", page_icon="🧵", layout="wide")

COLOR_ROJO = "#8d1b1b"

# --- SISTEMA DE ACCESO ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown(f"<h2 style='text-align:center; color:{COLOR_ROJO};'>Acceso Clientes</h2>", unsafe_allow_html=True)
    user = st.text_input("Usuario")
    clave = st.text_input("Contraseña", type="password")
    if st.button("INGRESAR", use_container_width=True):
        if user.lower() == "botonera" and clave == "2026":
            st.session_state["autenticado"] = True
            st.rerun()
        else:
            st.error("Credenciales incorrectas")
    st.stop()

# 2. ESTILOS VISUALES
st.markdown(f"""
    <style>
    .header {{ text-align: center; color: {COLOR_ROJO}; font-weight: bold; font-size: 20px; border-bottom: 2px solid #ddd; padding-bottom: 10px; }}
    div[data-baseweb="input"] {{ border: 2px solid {COLOR_ROJO} !important; border-radius: 10px !important; }}
    input {{ color: #000 !important; -webkit-text-fill-color: #000 !important; font-weight: bold !important; }}
    .card {{ background: white; padding: 15px; border-radius: 10px; border-left: 6px solid {COLOR_ROJO}; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 10px; }}
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="header">Botonera Cordobesa SA | Sarquis & Sepag</div>', unsafe_allow_html=True)

# 3. CARGA DE DATOS
FILE_ID = "1LTJJ-iXYdcl1gRhcbXaC0jw64J9Khzwo"
SHEET_URL = f"https://docs.google.com/uc?export=download&id={FILE_ID}"

@st.cache_data(ttl=300)
def load_data():
    try:
        df = pd.read_csv(SHEET_URL, encoding='latin1', on_bad_lines='skip', sep=None, engine='python')
        df = df.iloc[:, [0, 1, 2]]
        df.columns = ['Código', 'Descripción', 'Precio']
        return df
    except:
        return pd.DataFrame(columns=['Código', 'Descripción', 'Precio'])

df = load_data()
if 'carrito' not in st.session_state: st.session_state.carrito = []
if 'ver_pedido' not in st.session_state: st.session_state.ver_pedido = False

# 4. LÓGICA DE NAVEGACIÓN (CARRITO O CATÁLOGO)
if st.session_state.ver_pedido:
    st.markdown("### 🛒 Tu Lista de Pedido")
    if not st.session_state.carrito:
        st.write("Tu carrito está vacío.")
    else:
        for idx, item in enumerate(st.session_state.carrito):
            col_a, col_b = st.columns([4, 1])
            col_a.write(f"**{item['cant']}x** {item['desc']} (Col: {item['color']})")
            if col_b.button("❌", key=f"del_{idx}"):
                st.session_state.carrito.pop(idx)
                st.rerun()
    
    if st.button("⬅️ VOLVER AL CATÁLOGO", use_container_width=True):
        st.session_state.ver_pedido = False
        st.rerun()

else:
    # BUSCADOR
    busqueda = st.text_input("BUSCAR PRODUCTO", placeholder="🔍 Escribe nombre o código...").strip().lower()
    
    # PRODUCTOS
    df_filtrado = df[df['Descripción'].str.lower().str.contains(busqueda) | df['Código'].str.lower().str.contains(busqueda)] if busqueda else df.head(15)
