import streamlit as st
import pandas as pd
import urllib.parse

# 1. CONFIGURACIÓN Y ESTILOS
st.set_page_config(page_title="Botonera Cordobesa SA", layout="wide")
COLOR_ROJO = "#8d1b1b"

st.markdown(f"""
    <style>
    h1, h2, h3, b {{ color: {COLOR_ROJO} !important; font-family: 'serif'; }}
    .stButton>button {{ background-color: {COLOR_ROJO}; color: white !important; border-radius: 10px; font-weight: bold; }}
    .stTextInput>div>div>input {{ border: 2px solid {COLOR_ROJO} !important; }}
    .total-box {{
        background-color: {COLOR_ROJO};
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        color: white !important;
        margin: 20px 0;
    }}
    .paginacion-info {{ text-align: center; color: #666; margin: 10px 0; }}
    </style>
""", unsafe_allow_html=True)

# 2. ENCABEZADO UNIFICADO
st.markdown(f"""
    <div style="text-align: center; border-bottom: 3px solid {COLOR_ROJO}; padding-bottom: 10px; margin-bottom: 20px;">
        <h1 style="margin:0; font-size: 2.2em; color: {COLOR_ROJO};">Botonera Cordobesa SA</h1>
        <h1 style="margin:0; font-size: 2.2em; color: {COLOR_ROJO};">Sarquis & Sepag</h1>
        <p style="margin:5px; color: #555; font-size: 1.1em;">
            <b>Horario de atención:</b> Lunes a Viernes de 8:30 a 17:00 hs
        </p>
    </div>
""", unsafe_allow_html=True)

# 3. ACCESO
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

# 4. CARGA DE DATOS Y ESTADOS
if "carrito" not in st.session_state: st.session_state.carrito = []
if "ver_pedido" not in st.session_state: st.session_state.ver_pedido = False
if "pagina_actual" not in st.session_state: st.session_state.pagina_actual = 0

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

# 5. BOTÓN SUPERIOR DE PEDIDO
if st.session_state.carrito:
    cant_total = sum(int(x['cant']) for x in st.session_state.carrito)
    if st.button(f"🛒 VER MI PEDIDO ({cant_total} artículos)", use_container_width=True):
        st.session_state.ver_pedido = not st.session_state.ver_pedido
        st.rerun()

st.divider()

# 6. VISTA: CARRITO
if st.session_state.ver_pedido:
    st.markdown("<h2 style='text-align:center;'>Tu Pedido</h2>", unsafe_allow_html=True)
    total_compra = 0.0
    
    for i, itm in enumerate(st.session_state.carrito):
        sub = itm['precio'] * itm['cant']
        total_compra += sub
        c_a, c_b = st.columns([4, 1])
        c_a.write(f"**{itm['cant']}x** {itm['desc']} (Col: {itm['color']}) - **${sub:,.2f}**")
        if c_b.button("❌", key=f"del_{i}"):
            st.session_state.carrito.pop(i)
            st.rerun()
    
    # TOTAL EN BLANCO SOBRE ROJO
    st.markdown(f'<div class="total-box"><h1 style="color: white !important; margin: 0;">TOTAL: ${total_compra:,.2f}</h1></div>', unsafe_allow_html=True)
    
    wa_url = f"https://wa.me/5493513698953?text={urllib.parse.quote('Pedido Botonera Cordobesa...')}"
    st.link_button("📲 ENVIAR PEDIDO POR WHATSAPP", wa_url, use_container_width=True)
    
    if st.button("⬅️ VOLVER AL CATÁLOGO", use_container_width=True):
        st.session_state.ver_pedido = False
        st.rerun()

# 7. VISTA: CATÁLOGO CON PAGINACIÓN
else:
    busq = st.text_input("🔍 Buscar por Nombre o Código", placeholder="Escribe aquí...")
    
    if busq:
        resultado = df[df['Desc'].str.lower().str.contains(busq.lower(), na=False) | 
                       df['Cod'].astype(str).str.contains(busq, na=False)]
        items_por_pagina = len(resultado) # Si busca, mostramos todo lo encontrado
        inicio = 0
        fin = len(resultado)
    else:
        resultado = df
        items_por_pagina = 25
        num_paginas = (len(resultado) // items_por_pagina) + 1
        
        # Controles de página arriba
        c_pag1, c_pag2, c_pag3 = st.columns([1, 2, 1])
        with c_pag1:
            if st.button("⬅️ Anterior") and st.session_state.pagina_actual > 0:
                st.session_state.pagina_actual -= 1
                st.rerun()
        with c_pag2:
            st.markdown(f"<p class='paginacion-info'>Página {st.session_state.pagina_actual + 1} de {num_paginas}</p>", unsafe_allow_html=True)
        with c_pag3:
            if st.button("

