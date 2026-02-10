import streamlit as st
import pandas as pd
import urllib.parse

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Botonera Cordobesa SA", layout="wide")
COLOR_ROJO = "#8d1b1b"

# --- APLICACIÓN DE ESTILOS INSTITUCIONALES (CSS) ---
st.markdown(f"""
    <style>
    /* Títulos y Encabezado */
    .stApp {{ background-color: #ffffff; }}
    h2, h3 {{ color: {COLOR_ROJO} !important; font-family: 'serif'; }}
    
    /* Input de búsqueda y formularios */
    div[data-baseweb="input"] {{ 
        border: 2px solid {COLOR_ROJO} !important; 
        border-radius: 10px !important; 
    }}
    
    /* Botones principales */
    .stButton>button {{
        background-color: {COLOR_ROJO};
        color: white;
        border-radius: 8px;
        border: none;
    }}
    
    /* Tarjetas de producto */
    .producto-card {{
        background-color: #fcfcfc;
        padding: 15px;
        border-radius: 10px;
        border-left: 6px solid {COLOR_ROJO};
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }}
    </style>
""", unsafe_allow_html=True)

# --- SISTEMA DE ACCESO ---
if "auth" not in st.session_state:
    st.session_state["auth"] = False

# 2. ENCABEZADO INSTITUCIONAL
st.markdown(f"""
    <div style="text-align: center; padding: 10px; border-bottom: 3px solid {COLOR_ROJO}; margin-bottom: 20px;">
        <h2 style="color: {COLOR_ROJO}; margin-bottom: 5px; font-size: 1.8em; font-weight: bold;">
            Botonera Cordobesa SA
        </h2>
        <h2 style="color: {COLOR_ROJO}; margin-top: 0; font-size: 1.8em; font-weight: bold;">
            Sarquis & Sepag
        </h2>
        <p style="color: #444; font-size: 1em; margin-top: -5px;">
            <b>Horario de atención:</b> Lunes a Viernes de 8:30 a 17:00 hs
        </p>
    </div>
""", unsafe_allow_html=True)

# LÓGICA DE LOGIN
if not st.session_state["auth"]:
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown(f"<h3 style='text-align:center;'>🔐 Acceso Clientes</h3>", unsafe_allow_html=True)
        u = st.text_input("Usuario", key="user_input")
        p = st.text_input("Contraseña", type="password", key="pass_input")
        if st.button("INGRESAR AL CATÁLOGO", use_container_width=True):
            if u.strip().lower() == "botonera" and p.strip() == "2026":
                st.session_state["auth"] = True
                st.rerun()
            else:
                st.error("Usuario o clave incorrectos")
    st.stop()

# --- CONTENIDO POST-LOGIN ---
if "carrito" not in st.session_state:
    st.session_state.carrito = []
if "ver_pedido" not in st.session_state:
    st.session_state.ver_pedido = False

# 3. CARGA DE DATOS
@st.cache_data(ttl=60)
def cargar_csv():
    url = "https://docs.google.com/uc?export=download&id=1LTJJ-iXYdcl1gRhcbXaC0jw64J9Khzwo"
    try:
        data = pd.read_csv(url, encoding='latin1', on_bad_lines='skip', sep=None, engine='python')
        data = data.iloc[:, [0, 1, 2]]
        data.columns = ['Cod', 'Desc', 'Precio']
        data['Precio'] = data['Precio'].astype(str).str.replace(',', '.').str.extract(r'(\d+\.?\d*)').astype(float)
        return data
    except: return None

df = cargar_csv()
if df is None:
    st.warning("Cargando base de datos...")
    st.stop()

# 4. BOTÓN DE CARRITO
if st.session_state.carrito:
    items_count = sum(int(i['cant']) for i in st.session_state.carrito)
    if st.button(f"🛒 REVISAR MI PEDIDO ({items_count} productos)", use_container_width=True):
        st.session_state.ver_pedido = not st.session_state.ver_pedido
        st.rerun()

st.divider()

# 5. VISTA: DETALLE DEL PEDIDO
if st.session_state.ver_pedido:
    st.subheader("📝 Detalle de tu Pedido")
    total_gral = 0.0
    
    for idx, item in enumerate(st.session_state.carrito):
        sub = item['precio'] * item['cant']
        total_gral += sub
        with st.container():
            st.markdown(f"""
                <div style="padding:10px; border-bottom:1px solid #eee;">
                    <b>{item['cant']}x</b> {item['desc']} <br>
                    <small>Color: {item['color']} | Subtotal: ${sub:,.2f}</small>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Eliminar", key=f"del_{idx}"):
                st.session_state.carrito.pop(idx)
                st.rerun()
    
    st.markdown(f"""
        <div style="background-color: {COLOR_ROJO}; padding: 15px; border-radius: 10px; margin-top: 20px;">
            <h2 style="text-align: center; color: white !important; margin: 0;">TOTAL: ${total_gral:,.2f}</h2>
        </div>
    """, unsafe_allow_html=True)
    
    msg = f"Pedido Botonera Cordobesa:\n"
    for x in st.session_state.carrito:
        msg += f"- {x['cant']}x {x['desc']} (Col: {x['color']}) - ${x['precio']*x['cant']:,.2f}\n"
    msg += f"\nTOTAL ESTIMADO: ${total_gral:,.2f}"
    
    wa_link = f"https://wa.me/5493513698953?text={urllib.parse.quote(msg)}"
    st.markdown(f'<a href="{wa_link}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:15px; border-radius:10px; font-weight:bold; cursor:pointer;">📲 ENVIAR POR WHATSAPP</button></a>', unsafe_allow_html=True)
    
    if st.button("⬅️ VOLVER AL CATÁLOGO", use_container_width=True):
        st.session_state.ver_pedido = False
        st.rerun()

# 6. VISTA: BUSCADOR Y CATÁLOGO
else:
    busq = st.text_input("🔍 ¿Qué artículo buscás?", placeholder="Nombre o Código...")
    
    res = df[df['Desc'].str.lower().str.contains(busq.lower(), na=False) | 
             df['Cod'].astype(str).str.contains(busq, na=False)] if busq else df.head(15)

    for i, r in res.iterrows():
        st.markdown(f"""
            <div class="producto-card">
                <p style="margin:0; font-weight:bold; color:#333;">{r['Desc']}</p>
                <p style="margin:0; color:#666; font-size:0.9em;">Cód: {r['Cod']} | Precio: <b>${r['Precio']:,.2f}</b></p>
            </div>
        """, unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([2, 1, 1])
        col_in = c1.text_input("Color", key=f"col_{i}", placeholder="Nro/Color")
        cant_in = c2.number_input("Cant", 1, 1
