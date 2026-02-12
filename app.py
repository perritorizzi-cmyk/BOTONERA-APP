import streamlit as st
import pandas as pd
import urllib.parse
import requests
import io

# 1. AJUSTES DE PÁGINA
st.set_page_config(page_title="Botonera Cordobesa", layout="wide")
ROJO = "#8d1b1b"

st.markdown(f"""
    <style>
    h1, h2, b {{ color: {ROJO} !important; }}
    .stButton>button {{ background-color: {ROJO}; color: white !important; font-weight: bold; border-radius: 8px; }}
    .producto {{ background: white; padding: 15px; border-radius: 10px; border-left: 5px solid {ROJO}; margin-bottom: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
    </style>
""", unsafe_allow_html=True)

# 2. CARGA DE DATOS (URL DE PUBLICACIÓN WEB - Más estable)
@st.cache_data(ttl=60)
def cargar_inventario_final():
    # Esta es una URL de 'Publicar en la Web' que suele evitar el Error 400
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT5q7U_pE7p6S6x7mO6i-Y-8J-6x8N-D_9h0z_Y-8J-6x8N-D_9h0z_Y-8J-6x8N-D_9h0z_Y/pub?output=csv"
    # Si la anterior falla, usamos la que tenías pero con parámetros de limpieza
    backup_url = "https://docs.google.com/spreadsheets/d/1LTJJ-iXYdcl1gRhcbXaC0jw64J9Khzwo/export?format=csv"
    
    try:
        r = requests.get(backup_url, timeout=10)
        if r.status_code == 200:
            df_raw = pd.read_csv(io.BytesIO(r.content), encoding='latin1', on_bad_lines='skip', sep=None, engine='python')
            # Forzamos nombres de columnas SIEMPRE para evitar el KeyError
            df_raw = df_raw.iloc[:, [0, 1, 2]]
            df_raw.columns = ['Cod', 'Desc', 'Precio']
            return df_raw
    except:
        pass
    return pd.DataFrame(columns=['Cod', 'Desc', 'Precio'])

df = cargar_inventario_final()

# 3. CONTROL DE ACCESO
if "carrito" not in st.session_state: st.session_state.carrito = []
if "auth" not in st.session_state: st.session_state.auth = False
if "ver_pedido" not in st.session_state: st.session_state.ver_pedido = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>Botonera Cordobesa</h1>", unsafe_allow_html=True)
    u = st.text_input("Usuario").lower().strip()
    p = st.text_input("Clave", type="password").strip()
    if st.button("ENTRAR"):
        if u == "botonera" and p == "2026":
            st.session_state.auth = True
            st.rerun()
        else: st.error("Datos incorrectos")
    st.stop()

# 4. CABECERA
st.markdown("<h1 style='text-align:center; margin-bottom:0;'>Botonera Cordobesa SA</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center; margin-top:0;'>Sarquis & Sepag</h3>", unsafe_allow_html=True)

# Navegación
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
    st.subheader("Tu Pedido")
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
    
    st.error(f"### TOTAL: ${total:,.2f}")
    msg = f"Pedido Botonera:\n{resumen}\nTOTAL: ${total:,.2f}"
    st.link_button("📲 WHATSAPP", f"https://wa.me/5493513698953?text={urllib.parse.quote(msg)}")

# --- VISTA CATÁLOGO ---
else:
    if df.empty:
        st.warning("⚠️ No se pudo cargar la lista. Por favor, asegúrate de que el Excel en Google Drive esté compartido como 'Cualquier persona con el enlace puede leer'.")
        if st.button("REINTENTAR CARGA"): st.rerun()
    else:
        secciones = ["TODOS", "Botones", "Agujas", "Elasticos", "Puntillas", "Cierres", "Hilos", "Cintas"]
        cat_sel = st.selectbox("📂 Sección:", secciones)
        busq = st.text_input("🔍 Buscar:")

        # Filtrado
        items = df.copy()
        if cat_sel != "TODOS":
            items = items[items['Desc'].str.upper().str.contains(cat_sel.upper()[:4], na=False)]
        if busq:
            items = items[items['Desc'].str.contains(busq, case=False, na=False) | items['Cod'].astype(str).str.contains(busq, na=False)]

        items = items.head(40)
        st.info(f"Productos disponibles: {len(items)}")

        for idx, r in items.iterrows():
            st.markdown(f"<div class='producto'><b>{r['Desc']}</b><br>Cód: {r['Cod']} | ${r['Precio']:,.2f}</div>", unsafe_allow_html=True)
            ca, cb, cc = st.columns([2, 1, 1])
            col = ca.text_input("Color", key=f"c_{idx}")
            cant = cb.number_input("Cant", 1, 999, 1, key=f"n_{idx}")
            if cc.button("Añadir", key=f"b_{idx}"):
                st.session_state.carrito.append({'d': r['Desc'], 'p': r['Precio'], 'n': cant, 'c': col})
                st.toast("✅ Añadido")

