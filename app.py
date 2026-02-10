import streamlit as st
import pandas as pd
import urllib.parse

# 1. CONFIGURACIÓN Y COLORES
st.set_page_config(page_title="Botonera Cordobesa SA", layout="wide")
COLOR_ROJO = "#8d1b1b"

st.markdown(f"""
    <style>
    h1, h2, h3, b {{ color: {COLOR_ROJO} !important; font-family: 'serif'; }}
    .stButton>button {{ background-color: {COLOR_ROJO}; color: white; border-radius: 10px; }}
    div[data-baseweb="input"] {{ border: 2px solid {COLOR_ROJO} !important; border-radius: 8px !important; }}
    .card {{ border-left: 5px solid {COLOR_ROJO}; background: #fdfdfd; padding: 10px; border-radius: 5px; margin-bottom: 5px; }}
    </style>
""", unsafe_allow_html=True)

# 2. ENCABEZADO UNIFICADO
st.markdown(f"""
    <div style="text-align: center; border-bottom: 3px solid {COLOR_ROJO}; padding-bottom: 10px; margin-bottom: 20px;">
        <h1 style="margin:0; font-size: 2.2em;">Botonera Cordobesa SA</h1>
        <h1 style="margin:0; font-size: 2.2em;">Sarquis & Sepag</h1>
        <p style="margin:5px; color: #555;"><b>Horario:</b> Lunes a Viernes de 8:30 a 17:00 hs</p>
    </div>
""", unsafe_allow_html=True)

# 3. ACCESO
if "auth" not in st.session_state: st.session_state["auth"] = False

if not st.session_state["auth"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("🔐 Acceso Clientes")
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if st.button("INGRESAR", use_container_width=True):
            if u.strip().lower() == "botonera" and p.strip() == "2026":
                st.session_state["auth"] = True
                st.rerun()
            else:
                st.error("Datos incorrectos")
    st.stop()

# 4. CARGA DE DATOS
if "carrito" not in st.session_state: st.session_state.carrito = []
if "ver_pedido" not in st.session_state: st.session_state.ver_pedido = False

@st.cache_data(ttl=60)
def cargar_datos():
    url = "https://docs.google.com/uc?export=download&id=1LTJJ-iXYdcl1gRhcbXaC0jw64J9Khzwo"
    try:
        data = pd.read_csv(url, encoding='latin1', on_bad_lines='skip', sep=None, engine='python')
        data = data.iloc[:, [0, 1, 2]]
        data.columns = ['Cod', 'Desc', 'Precio']
        data['Precio'] = data['Precio'].astype(str).str.replace(',', '.').str.extract(r'(\d+\.?\d*)').astype(float)
        return data
    except: return None

df = cargar_datos()

# 5. LÓGICA DE PANTALLAS
if st.session_state.carrito:
    cant_total = sum(int(x['cant']) for x in st.session_state.carrito)
    if st.button(f"🛒 VER MI PEDIDO ({cant_total} artículos)", use_container_width=True, type="primary"):
        st.session_state.ver_pedido = not st.session_state.ver_pedido
        st.rerun()

st.divider()

if st.session_state.ver_pedido:
    st.subheader("🛒 Tu Pedido")
    total_compra = 0.0
    for i, itm in enumerate(st.session_state.carrito):
        sub = itm['precio'] * itm['cant']
        total_compra += sub
        c_a, c_b = st.columns([4, 1])
        c_a.write(f"**{itm['cant']}x** {itm['desc']} (Col: {itm['color']}) - **${sub:,.2f}**")
        if c_b.button("❌", key=f"del_{i}"):
            st.session_state.carrito.pop(i)
            st.rerun()
    
    st.markdown(f"<div style='background:{COLOR_ROJO}; color:white; padding:15px; border-radius:10px; text-align:center;'><h2>TOTAL: ${total_compra:,.2f}</h2></div>", unsafe_allow_html=True)
    
    # WhatsApp
    msg = "Pedido Botonera Cordobesa:\n"
    for x in st.session_state.carrito: msg += f"- {x['cant']}x {x['desc']} (Col: {x['color']}) - ${x['precio']*x['cant']:,.2f}\n"
    msg += f"\nTOTAL: ${total_compra:,.2f}"
    st.link_button("📲 ENVIAR POR WHATSAPP", f"https://wa.me/5493513698953?text={urllib.parse.quote(msg)}", use_container_width=True)
    
    if st.button("⬅️ VOLVER AL CATÁLOGO", use_container_width=True):
        st.session_state.ver_pedido = False
        st.rerun()

else:
    # BUSCADOR
    busq = st.text_input("🔍 Buscar Producto o Código")
    res = df[df['Desc'].str.lower().str.contains(busq.lower(), na=False) | df['Cod'].astype(str).str.contains(busq, na=False)] if busq else df.head(15)

    for i, r in res.iterrows():
        st.markdown(f"<div class='card'><b>{r['Desc']}</b><br><small>Cód: {r['Cod']} | Precio: ${r['Precio']:,.2f}</small></div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([2, 1, 1])
        color = c1.text_input("Color", key=f"col_{i}", placeholder="Nro")
        cant = c2.number_input("Cant", 1, 1000, 1, key=f"can_{i}")
        if c3.button("➕", key=f"btn_{i}"):
            st.session_state.carrito.append({"desc":r['Desc'], "cant":cant, "color":color, "cod":r['Cod'], "precio":r['Precio']})
            st.toast("Agregado")
        st.divider()
