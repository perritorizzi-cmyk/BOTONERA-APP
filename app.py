import streamlit as st
import pandas as pd
import urllib.parse

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Botonera Cordobesa", layout="wide")
COLOR_ROJO = "#8d1b1b"

st.markdown(f"""
    <style>
    h1, h2, b {{ color: {COLOR_ROJO} !important; }}
    .stButton>button {{ background-color: {COLOR_ROJO}; color: white !important; border-radius: 8px; font-weight: bold; }}
    .producto-card {{
        background: white; padding: 12px; border-radius: 8px;
        border-left: 5px solid {COLOR_ROJO}; margin-bottom: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }}
    </style>
""", unsafe_allow_html=True)

# 2. ENCABEZADO
st.markdown("<h1 style='text-align:center; margin:0;'>Botonera Cordobesa SA</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align:center; margin:0;'>Sarquis & Sepag</h2>", unsafe_allow_html=True)
st.markdown("---")

# 3. SESIÓN Y DATOS
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

# 4. LOGIN
if not st.session_state.auth:
    _, col_b, _ = st.columns([1, 4, 1])
    with col_b:
        u = st.text_input("Usuario").strip().lower()
        p = st.text_input("Clave", type="password").strip()
        if st.button("INGRESAR"):
            if u == "botonera" and p == "2026":
                st.session_state.auth = True
                st.rerun()
            else: st.error("Clave incorrecta")
    st.stop()

# 5. NAVEGACIÓN
c1, c2 = st.columns(2)
if st.session_state.carrito:
    if c1.button(f"🛒 VER PEDIDO ({len(st.session_state.carrito)})"):
        st.session_state.ver_pedido = True
        st.rerun()
if st.session_state.ver_pedido:
    if c2.button("🔍 VOLVER AL CATÁLOGO"):
        st.session_state.ver_pedido = False
        st.rerun()

# --- VISTA: CARRITO ---
if st.session_state.ver_pedido:
    st.subheader("Resumen para enviar")
    total = 0.0
    txt_resumen = ""
    for i, item in enumerate(st.session_state.carrito):
        sub = item['p'] * item['n']
        total += sub
        st.write(f"**{item['n']}x** {item['d']} - Col: {item['c']} - ${sub:,.2f}")
        txt_resumen += f"{item['n']}x {item['d']} (Col: {item['c']}) - ${sub:,.2f}\n"
        if st.button("Quitar", key=f"rm_{i}"):
            st.session_state.carrito.pop(i)
            st.rerun()
    
    st.error(f"### TOTAL: ${total:,.2f}")
    
    # WhatsApp y Email
    msg_wa = f"Pedido Botonera:\n{txt_resumen}\nTOTAL: ${total:,.2f}"
    st.link_button("📲 WHATSAPP", f"https://wa.me/5493513698953?text={urllib.parse.quote(msg_wa)}")
    
    mail_url = f"mailto:ivanrizzi@hotmail.com?subject=Pedido%20Botonera&body={urllib.parse.quote(txt_resumen + f'TOTAL: ${total:,.2f}')}"
    st.link_button("📧 EMAIL (Para Imprimir)", mail_url)

# --- VISTA: CATÁLOGO POR SECCIONES ---
else:
    # Selector de Categorías
    categorias = [
        "TODOS", "Botones", "Agujas y Alfileres", "Elásticos", 
        "Puntillas, Broderies y Festones", "Galones", "Aplicaciones", 
        "Cierres", "Hilos", "Cintas", "Cuerdas y Cordones", 
        "Pinturas y Anilinas", "Metales", "Accesorios", "Otros"
    ]
    seccion = st.selectbox("📂 Seleccione una Sección:", categorias)
    
    busq = st.text_input("🔍 O busque por nombre/código directo:")

    # Filtrado dinámico
    res = df.copy()
    if seccion != "TODOS":
        res = res[res['Desc'].str.contains(seccion, case=False, na=False)]
    if busq:
        res = res[res['Desc'].str.contains(busq, case=False, na=False) | res['Cod'].astype(str).str.contains(busq, na=False)]
    
    # Mostrar resultados (máximo 100 para agilidad)
    res = res.head(100)
    st.caption(f"Mostrando {len(res)} productos de esta sección")

    for idx, r in res.iterrows():
        st.markdown(f"<div class='producto-card'><b>{r['Desc']}</b><br>Cód: {r['Cod']} - ${r['Precio']:,.2f}</div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([2, 1, 1])
        color = col1.text_input("Color", key=f"col_{idx}")
        cant = col2.number_input("Cant", 1, 1000, 1, key=f"can_{idx}")
        if col3.button("➕", key=f"add_{idx}"):
            st.session_state.carrito.append({'d': r['Desc'], 'n': cant, 'c': color, 'p': r['Precio']})
            st.toast("Agregado")
