import streamlit as st
import pandas as pd
import urllib.parse

# 1. CONFIGURACIÓN TÉCNICA
st.set_page_config(
    page_title="Botonera Cordobesa SA", 
    page_icon="🧵", 
    layout="wide"
)

COLOR_ROJO = "#8d1b1b"

# --- SISTEMA DE ACCESO ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
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

# 2. ESTILOS CSS (Sin errores de f-string)
st.markdown(f"""
    <style>
    .header-box {{ display: flex; align-items: center; justify-content: center; gap: 10px; padding: 10px; }}
    .txt-logo {{ color: {COLOR_ROJO} !important; font-family: 'serif'; font-size: 1.3em; font-weight: bold; margin: 0; }}
    div[data-baseweb="input"] {{ border: 2px solid {COLOR_ROJO} !important; border-radius: 10px !important; }}
    input {{ color: #000 !important; -webkit-text-fill-color: #000 !important; }}
    .card {{ background: white; padding: 15px; border-radius: 10px; border-left: 6px solid {COLOR_ROJO}; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 10px; }}
    .footer-bar {{ 
        position: fixed; bottom: 0; left: 0; width: 100%; 
        background: white; border-top: 2px solid {COLOR_ROJO}; 
        padding: 10px; z-index: 1000; display: flex; 
        justify-content: space-around; align-items: center; 
        box-shadow: 0 -3px 10px rgba(0,0,0,0.1);
    }}
    </style>
""", unsafe_allow_html=True)

# 3. ENCABEZADO
st.markdown(f'<div class="header-box"><p class="txt-logo">Botonera Cordobesa SA</p><div style="border-left:2px solid #ddd;height:20px;"></div><p class="txt-logo">Sarquis & Sepag</p></div>', unsafe_allow_html=True)

# 4. CARGA DE DATOS
FILE_ID = "1LTJJ-iXYdcl1gRhcbXaC0jw64J9Khzwo"
SHEET_URL = f"https://docs.google.com/uc?export=download&id={FILE_ID}"

@st.cache_data(ttl=300)
def load_data():
    try:
        df = pd.read_csv(SHEET_URL, encoding='latin1', on_bad_lines='skip', sep=None, engine='python')
        df = df.iloc[:, [0, 1, 2]]
        df.columns = ['Código', 'Descripción', 'Precio']
        return df
    except: return pd.DataFrame(columns=['Código', 'Descripción', 'Precio'])

df = load_data()
if 'carrito' not in st.session_state: st.session_state.carrito = []

# 5. BUSCADOR
busqueda = st.text_input("Buscador", placeholder="🔍 Buscar producto...", label_visibility="collapsed").strip().lower()

# 6. MOSTRAR PEDIDO (SI ESTÁ ABIERTO)
if st.session_state.get('ver_pedido', False):
    st.markdown("### 🛒 Tu Lista de Pedido")
    if not st.session_state.carrito:
        st.write("El carrito está vacío.")
        if st.button("Volver al catálogo"):
            st.session_state.ver_pedido = False
            st.rerun()
    else:
        for idx, item in enumerate(st.session_state.carrito):
            col_a, col_b = st.columns([4, 1])
            col_a.write(f"**{item['cant']}x** {item['desc']} ({item['color']})")
            if col_b.button("❌", key=f"del_{idx}"):
                st.session_state.carrito.pop(idx)
                st.rerun()
        
        if st.button("✅ LISTO, VOLVER A BUSCAR"):
            st.session_state.ver_pedido = False
            st.rerun()
    st.divider()

# 7. LISTADO DE PRODUCTOS (Solo si no estamos viendo el pedido)
else:
    df_filtrado = df[df['Descripción'].str.lower().str.contains(busqueda) | df['Código'].str.lower().str.contains(busqueda)] if busqueda else df.head(15)

    for i, row in df_filtrado.iterrows():
        st.markdown(f'<div class="card"><p style="color:#000; font-weight:bold; margin:0;">{row["Descripción"]}</p><p style="color:gray; font-size:0.8em; margin:0;">Cod: {row["Código"]}</p><p style="color:{COLOR_ROJO}; font-weight:bold; margin:0;">${row["Precio"]}</p></div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1: color = st.text_input("Color", key=f"col_{i}", placeholder="Color/Nro")
        with c2: cant = st.number_input("Cant", min_value=1, value=1, key=f"can_{i}")
        with c3:
            st.write("")
            if st.button("➕", key=f"btn_{i}"):
                st.session_state.carrito.append({"desc": row['Descripción'], "cant": cant, "color": color, "precio": row['Precio'], "cod": row['Código']})
                st.toast("Agregado")

st.write("<br><br><br><br>", unsafe_allow_html=True)

# 8. BARRA FIJA INFERIOR
if st.session_
