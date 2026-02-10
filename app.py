import streamlit as st
import pandas as pd
import urllib.parse

# 1. CONFIGURACIÓN Y ESTILOS
st.set_page_config(page_title="Botonera Cordobesa SA", layout="wide")
COLOR_ROJO = "#8d1b1b"

st.markdown(f"""
    <style>
    /* Estilos globales */
    h1, h2, h3, b {{ color: {COLOR_ROJO} !important; font-family: 'serif'; }}
    .stButton>button {{ background-color: {COLOR_ROJO}; color: white; border-radius: 10px; font-weight: bold; }}
    div[data-baseweb="input"] {{ border: 2px solid {COLOR_ROJO} !important; border-radius: 8px !important; }}
    
    /* Tarjeta de producto en catálogo */
    .card {{ 
        border-left: 5px solid {COLOR_ROJO}; 
        background: #fdfdfd; 
        padding: 15px; 
        border-radius: 8px; 
        margin-bottom: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }}
    </style>
""", unsafe_allow_html=True)

# 2. ENCABEZADO UNIFICADO (Mismo tamaño para ambas casas)
st.markdown(f"""
    <div style="text-align: center; border-bottom: 3px solid {COLOR_ROJO}; padding-bottom: 10px; margin-bottom: 20px;">
        <h1 style="margin:0; font-size: 2.2em; color: {COLOR_ROJO};">Botonera Cordobesa SA</h1>
        <h1 style="margin:0; font-size: 2.2em; color: {COLOR_ROJO};">Sarquis & Sepag</h1>
        <p style="margin:5px; color: #555; font-size: 1.1em;">
            <b>Horario de atención:</b> Lunes a Viernes de 8:30 a 17:00 hs
        </p>
    </div>
""", unsafe_allow_html=True)

# 3. SISTEMA DE ACCESO
if "auth" not in st.session_state: st.session_state["auth"] = False

if not st.session_state["auth"]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h3 style='text-align:center;'>🔐 Acceso Clientes</h3>", unsafe_allow_html=True)
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type="password")
        if st.button("INGRESAR AL CATÁLOGO", use_container_width=True):
            if u.strip().lower() == "botonera" and p.strip() == "2026":
                st.session_state["auth"] = True
                st.rerun()
            else:
                st.error("Usuario o clave incorrectos")
    st.stop()

# 4. CARGA DE DATOS Y VARIABLES
if "carrito" not in st.session_state: st.session_state.carrito = []
if "ver_pedido" not in st.session_state: st.session_state.ver_pedido = False

@st.cache_data(ttl=60)
def cargar_datos():
    url = "https://docs.google.com/uc?export=download&id=1LTJJ-iXYdcl1gRhcbXaC0jw64J9Khzwo"
    try:
        data = pd.read_csv(url, encoding='latin1', on_bad_lines='skip', sep=None, engine='python')
        data = data.iloc[:, [0, 1, 2]]
        data.columns = ['Cod', 'Desc', 'Precio']
        # Limpieza de precios
        data['Precio'] = data['Precio'].astype(str).str.replace(',', '.').str.extract(r'(\d+\.?\d*)').astype(float)
        return data
    except: return None

df = cargar_datos()

# 5. BOTÓN FLOTANTE / SUPERIOR DE CARRITO
if st.session_state.carrito:
    cant_total = sum(int(x['cant']) for x in st.session_state.carrito)
    if st.button(f"🛒 REVISAR MI PEDIDO ({cant_total} artículos)", use_container_width=True):
        st.session_state.ver_pedido = not st.session_state.ver_pedido
        st.rerun()

st.divider()

# 6. VISTA: DETALLE DEL PEDIDO (CARRITO)
if st.session_state.ver_pedido:
    st.markdown(f"<h2 style='text-align:center;'>🛒 Tu Pedido</h2>", unsafe_allow_html=True)
    total_compra = 0.0
    
    for i, itm in enumerate(st.session_state.carrito):
        sub = itm['precio'] * itm['cant']
        total_compra += sub
        with st.container():
            c_a, c_b = st.columns([4, 1])
            c_a.markdown(f"**{itm['cant']}x** {itm['desc']}<br><small>Color: {itm['color']} | Subtotal: **${sub:,.2f}**</small>", unsafe_allow_html=True)
            if c_b.button("🗑️", key=f"del_{i}"):
                st.session_state.carrito.pop(i)
                st.rerun()
    
    # RECUADRO DE TOTAL CORREGIDO
    st.markdown(f"""
        <div style="background-color: {COLOR_ROJO}; padding: 20px; border-radius: 15px; text-align: center; margin: 20px 0;">
            <h1 style="color: white !important; margin: 0; font-size: 2.5em;">TOTAL: ${total_compra:,.2f}</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # WhatsApp
    msg = f"Pedido Botonera Cordobesa:\n"
    for x in st.session_state.carrito:
        msg += f"- {x['cant']}x {x['desc']} (Col: {x['color']}) - ${x['precio']*x['cant']:,.2f}\n"
    msg += f"\nTOTAL ESTIMADO: ${total_compra:,.2f}"
    
    wa_url = f"https://wa.me/5493513698953?text={urllib.parse.quote(msg)}"
    st.markdown(f'<a href="{wa_url}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:15px; border-radius:10px; font-weight:bold; font-size:1.2em; cursor:pointer;">📲 ENVIAR PEDIDO POR WHATSAPP</button></a>', unsafe_allow_html=True)
    
    if st.button("⬅️ VOLVER AL CATÁLOGO", use_container_width=True):
        st.session_state.ver_pedido = False
        st.rerun()

# 7. VISTA: BUSCADOR Y CATÁLOGO
else:
    busq = st.text_input("🔍 ¿Qué estás buscando? (Nombre o Código)", placeholder="Ej: Cierre, Botón, 100068...")
    
    res = df[df['Desc'].str.lower().str.contains(busq.lower(), na=False) | 
             df['Cod'].astype(str).str.contains(busq, na=False)] if busq else df.head(15)

    for i, r in res.iterrows():
        st.markdown(f"""
            <div class="card">
                <b style="font-size:1.1em;">{r['Desc']}</b><br>
                <span style="color:#666;">Cód: {r['Cod']} | Precio: <b>${r['Precio']:,.2f}</b></span>
            </div>
        """, unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([2, 1, 1])
        color = c1.text_input("Color/Nro", key=f"col_{i}", placeholder="Color")
        cant = c2.number_input("Cant", 1, 1000, 1, key=f"can_{i}")
        if c3.button("AÑADIR ➕", key=f"btn_{i}"):
            st.session_state.carrito.append({
                "desc": r['Desc'], "cant": cant, "color": color, 
                "cod": r['Cod'], "precio": r['Precio']
            })
            st.toast(f"✅ Agregado: {r['Desc']}")
        st.divider()

