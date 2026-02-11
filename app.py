import streamlit as st
import pandas as pd
import urllib.parse

# 1. CONFIGURACIÓN DE ALTO RENDIMIENTO
st.set_page_config(page_title="Botonera Cordobesa", layout="wide")

# Estilos CSS simplificados para máxima velocidad en celulares
st.markdown("""
    <style>
    .main { background-color: #fafafa; }
    h1, h2, b { color: #8d1b1b !important; }
    .stButton>button { 
        background-color: #8d1b1b; color: white !important; 
        border-radius: 8px; width: 100%; height: 45px; font-weight: bold;
    }
    .producto-card {
        background: white; padding: 10px; border-radius: 8px;
        border-left: 5px solid #8d1b1b; margin-bottom: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    /* Barra de total fija y visible */
    .total-footer {
        background-color: #8d1b1b; color: white;
        padding: 15px; border-radius: 10px; text-align: center;
        font-size: 20px; font-weight: bold; margin: 15px 0;
    }
    </style>
""", unsafe_allow_html=True)

# 2. ENCABEZADO
st.markdown("<h1 style='text-align:center; margin:0;'>Botonera Cordobesa SA</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align:center; margin:0;'>Sarquis & Sepag</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:14px;'>Lun a Vie 8:30 a 17:00 hs</p>", unsafe_allow_html=True)

# 3. GESTIÓN DE DATOS (Cache de larga duración)
if "carrito" not in st.session_state: st.session_state.carrito = []
if "auth" not in st.session_state: st.session_state.auth = False
if "ver_pedido" not in st.session_state: st.session_state.ver_pedido = False

@st.cache_data(ttl=3600)
def get_data():
    url = "https://docs.google.com/uc?export=download&id=1LTJJ-iXYdcl1gRhcbXaC0jw64J9Khzwo"
    try:
        d = pd.read_csv(url, encoding='latin1', on_bad_lines='skip', sep=None, engine='python')
        d = d.iloc[:, [0, 1, 2]]
        d.columns = ['Cod', 'Desc', 'Precio']
        d['Precio'] = pd.to_numeric(d['Precio'].astype(str).str.replace(',', '.').str.extract(r'(\d+\.?\d*)')[0], errors='coerce').fillna(0)
        return d
    except: return pd.DataFrame(columns=['Cod', 'Desc', 'Precio'])

df = get_data()

# 4. ACCESO
if not st.session_state.auth:
    col_a, col_b, col_c = st.columns([1, 4, 1])
    with col_b:
        u = st.text_input("Usuario").strip().lower()
        p = st.text_input("Clave", type="password").strip()
        if st.button("INGRESAR"):
            if u == "botonera" and p == "2026":
                st.session_state.auth = True
                st.rerun()
            else: st.error("Clave incorrecta")
    st.stop()

# 5. NAVEGACIÓN RÁPIDA
c_nav1, c_nav2 = st.columns(2)
if st.session_state.carrito:
    if c_nav1.button(f"🛒 PEDIDO ({len(st.session_state.carrito)})"):
        st.session_state.ver_pedido = True
        st.rerun()
if st.session_state.ver_pedido:
    if c_nav2.button("🔍 VOLVER AL CATÁLOGO"):
        st.session_state.ver_pedido = False
        st.rerun()

# 6. VISTA: CARRITO E IMPRESIÓN
if st.session_state.ver_pedido:
    st.subheader("Detalle del Pedido")
    total = 0.0
    resumen_texto = "CANT | ARTICULO | COLOR | SUBT\n"
    
    for i, item in enumerate(st.session_state.carrito):
        sub = item['p'] * item['n']
        total += sub
        st.markdown(f"**{item['n']}x** {item['d']} (Col: {item['c']}) - **${sub:,.2f}**")
        resumen_texto += f"{item['n']} x {item['d']} | {item['c']} | ${sub:,.2f}\n"
        if st.button("Quitar", key=f"rm_{i}"):
            st.session_state.carrito.pop(i)
            st.rerun()
    
    st.markdown(f"<div class='total-footer'>TOTAL: ${total:,.2f}</div>", unsafe_allow_html=True)
    
    # WhatsApp y Email
    msg_wa = f"Pedido Botonera:\n{resumen_texto}\nTOTAL: ${total:,.2f}"
    st.link_button("📲 WHATSAPP", f"https://wa.me/5493513698953?text={urllib.parse.quote(msg_wa)}")
    
    mail_url = f"mailto:ivanrizzi@hotmail.com?subject=Pedido%20Botonera&body={urllib.parse.quote(resumen_texto + f'TOTAL: ${total:,.2f}')}"
    st.link_button("📧 ENVIAR A IVAN (Para Imprimir)", mail_url)

# 7. VISTA: CATÁLOGO AGILIZADO
else:
    busq = st.text_input("🔍 Buscar producto...", placeholder="Escribe nombre o código...")
    
    # Filtrado ultra-rápido
    if busq:
        res = df[df['Desc'].str.contains(busq, case=False, na=False) | df['Cod'].astype(str).str.contains(busq, na=False)]
    else:
        res = df.head(50) # Carga inicial de 50 para no tildar el celu, el buscador encuentra el resto.

    for idx, r in res.iterrows():
        st.markdown(f"""<div class='producto-card'><b>{r['Desc']}</b><br>Cód: {r['Cod']} - Price: ${r['Precio']:,.2f}</div>""", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([2, 1, 1])
        color = col1.text_input("Color", key=f"col_{idx}")
        cant = col2.number_input("Cant", 1, 1000, 1, key=f"can_{idx}")
        if col3.button("➕", key=f"add_{idx}"):
            st.session_state.carrito.append({'d': r['Desc'], 'n': cant, 'c': color, 'p': r['Precio']})
            st.toast("Agregado")

