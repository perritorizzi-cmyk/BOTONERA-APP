import streamlit as st
import pandas as pd
import urllib.parse
import requests
from io import StringIO

# 1. CONFIGURACIÓN E ICONO
st.set_page_config(page_title="Botonera Cordobesa", page_icon="🧵", layout="wide")
COLOR = "#8d1b1b"

st.markdown(f"""
    <style>
    .main {{ background-color: #f8f9fa; }}
    h1, h2, h3, b {{ color: {COLOR} !important; }}
    .stButton>button {{ background-color: {COLOR}; color: white !important; border-radius: 8px; font-weight: bold; width: 100%; }}
    .card {{ background: white; padding: 12px; border-radius: 10px; border-left: 6px solid {COLOR}; margin-bottom: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
    </style>
""", unsafe_allow_html=True)

# 2. CARGA DE DATOS ULTRA-SEGURA (Solución al Error 400)
@st.cache_data(ttl=600)
def cargar_datos_v2():
    # Nueva ruta de acceso directo a datos crudos
    csv_url = "https://docs.google.com/spreadsheets/d/1LTJJ-iXYdcl1gRhcbXaC0jw64J9Khzwo/export?format=csv&gid=0"
    try:
        response = requests.get(csv_url)
        if response.status_code == 200:
            # Leemos el contenido del texto descargado
            content = response.content.decode('latin1')
            d = pd.read_csv(StringIO(content), on_bad_lines='skip', sep=None, engine='python')
            d = d.iloc[:, [0, 1, 2]]
            d.columns = ['Cod', 'Desc', 'Precio']
            # Limpieza profesional de precios
            d['Precio'] = pd.to_numeric(d['Precio'].astype(str).str.replace(',', '.').str.extract(r'(\d+\.?\d*)')[0], errors='coerce').fillna(0)
            return d
        else:
            st.error("Error de servidor. Reintentando...")
            return pd.DataFrame()
    except:
        return pd.DataFrame()

df = cargar_datos_v2()

# 3. SESIÓN
if "carrito" not in st.session_state: st.session_state.carrito = []
if "auth" not in st.session_state: st.session_state.auth = False
if "ver_pedido" not in st.session_state: st.session_state.ver_pedido = False

# 4. LOGIN
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>Botonera Cordobesa</h1>", unsafe_allow_html=True)
    u = st.text_input("Usuario").strip().lower()
    p = st.text_input("Contraseña", type="password").strip()
    if st.button("INGRESAR"):
        if u == "botonera" and p == "2026":
            st.session_state.auth = True
            st.rerun()
        else: st.error("Acceso incorrecto")
    st.stop()

# 5. ENCABEZADO (Igual a tu foto 1)
st.markdown("<h1 style='text-align:center; margin-bottom:0;'>Botonera Cordobesa SA</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center; margin-top:0;'>Sarquis & Sepag</h3>", unsafe_allow_html=True)

# 6. NAVEGACIÓN
c1, c2 = st.columns(2)
if st.session_state.carrito:
    if c1.button(f"🛒 VER PEDIDO ({len(st.session_state.carrito)})"):
        st.session_state.ver_pedido = True
        st.rerun()
if st.session_state.ver_pedido:
    if c2.button("🔍 VOLVER AL CATÁLOGO"):
        st.session_state.ver_pedido = False
        st.rerun()

# --- VISTA PEDIDO ---
if st.session_state.ver_pedido:
    st.subheader("Tu Pedido Actual")
    total = 0.0
    resumen = ""
    for i, itm in enumerate(st.session_state.carrito):
        sub = itm['p'] * itm['n']
        total += sub
        st.write(f"**{itm['n']}x** {itm['d']} - ${sub:,.2f}")
        resumen += f"{itm['n']}x {itm['d']} | Col: {itm['c']} | ${sub:,.2f}\n"
        if st.button("Quitar", key=f"del_{i}"):
            st.session_state.carrito.pop(i)
            st.rerun()
    
    st.error(f"## TOTAL: ${total:,.2f}")
    
    msg_wa = f"Pedido Botonera:\n{resumen}\nTOTAL: ${total:,.2f}"
    st.link_button("📲 WHATSAPP", f"https://wa.me/5493513698953?text={urllib.parse.quote(msg_wa)}")
    
    mail = f"mailto:ivanrizzi@hotmail.com?subject=Pedido%20Botonera&body={urllib.parse.quote(resumen + f'\nTOTAL: ${total:,.2f}')}"
    st.link_button("📧 EMAIL A IVAN", mail)

# --- VISTA CATÁLOGO ---
else:
    # Secciones dinámicas (ajustadas a tu Excel)
    secciones = ["TODOS", "Botones", "Agujas", "Elasticos", "Puntillas", "Galones", "Cierres", "Hilos", "Cintas", "Cordones", "Metales"]
    cat_sel = st.selectbox("📂 Seleccione una Sección:", secciones)
    busq = st.text_input("🔍 O busque por nombre o código:")

    # Filtrado que ignora acentos y mayúsculas
    items = df.copy()
    if cat_sel != "TODOS":
        # Filtramos buscando la palabra en la descripción
        items = items[items['Desc'].str.contains(cat_sel.replace("Elasticos", "ELAST"), case=False, na=False)]
    
    if busq:
        items = items[items['Desc'].str.contains(busq, case=False, na=False) | items['Cod'].astype(str).str.contains(busq, na=False)]
    
    items = items.head(50) 
    
    if items.empty:
        st.warning("No se encontraron productos en esta sección. Intente con 'TODOS' o use el buscador.")
    else:
        st.info(f"Productos encontrados: {len(items)}")

    for idx, r in items.iterrows():
        with st.container():
            st.markdown(f"<div class='card'><b>{r['Desc']}</b><br>Cód: {r['Cod']} | ${r['Precio']:,.2f}</div>", unsafe_allow_html=True)
            ca, cb, cc = st.columns([2, 1, 1])
            color = ca.text_input("Color", key=f"c_{idx}")
            cant = cb.number_input("Cant", 1, 1000, 1, key=f"n_{idx}")
            if cc.button("➕", key=f"b_{idx}"):
                st.session_state.carrito.append({'d': r['Desc'], 'p': r['Precio'], 'n': cant, 'c': color})
                st.toast(f"Añadido!")
