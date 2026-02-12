import streamlit as st
import pandas as pd
import urllib.parse
import requests

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

# 2. CARGA DE DATOS ANTIBLOQUEO
@st.cache_data(ttl=300)
def cargar_precios():
    # Link directo de descarga forzada
    url = "https://docs.google.com/spreadsheets/d/1LTJJ-iXYdcl1gRhcbXaC0jw64J9Khzwo/export?format=csv&gid=0"
    try:
        # Usamos un agente de usuario para que Google no sepa que es un robot
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            import io
            # Leemos el texto descargado
            df_raw = pd.read_csv(io.StringIO(r.content.decode('latin1')), on_bad_lines='skip', sep=None, engine='python')
            # Forzamos los nombres de las columnas para evitar el KeyError
            df_raw = df_raw.iloc[:, [0, 1, 2]]
            df_raw.columns = ['Cod', 'Desc', 'Precio']
            # Limpiamos los precios
            df_raw['Precio'] = pd.to_numeric(df_raw['Precio'].astype(str).str.replace(',', '.').str.extract(r'(\d+\.?\d*)')[0], errors='coerce').fillna(0)
            return df_raw
    except Exception as e:
        st.error(f"Error técnico: {e}")
    return pd.DataFrame(columns=['Cod', 'Desc', 'Precio'])

df = cargar_precios()

# 3. SESIÓN Y LOGIN
if "carrito" not in st.session_state: st.session_state.carrito = []
if "auth" not in st.session_state: st.session_state.auth = False
if "ver_pedido" not in st.session_state: st.session_state.ver_pedido = False

if not st.session_state.auth:
    st.title("Botonera Cordobesa")
    u = st.text_input("Usuario").lower().strip()
    p = st.text_input("Clave", type="password").strip()
    if st.button("ENTRAR"):
        if u == "botonera" and p == "2026":
            st.session_state.auth = True
            st.rerun()
        else: st.error("Datos incorrectos")
    st.stop()

# 4. ENCABEZADO
st.markdown("<h1 style='text-align:center;'>Botonera Cordobesa SA</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center;'>Sarquis & Sepag</h3>", unsafe_allow_html=True)

# Botones de navegación
c1, c2 = st.columns(2)
if st.session_state.carrito and c1.button(f"🛒 VER PEDIDO ({len(st.session_state.carrito)})"):
    st.session_state.ver_pedido = True
    st.rerun()
if st.session_state.ver_pedido and c2.button("🔍 IR AL CATÁLOGO"):
    st.session_state.ver_pedido = False
    st.rerun()

# --- VISTA: CARRITO ---
if st.session_state.ver_pedido:
    st.subheader("Confirmar Pedido")
    total = 0.0
    resumen = ""
    for i, itm in enumerate(st.session_state.carrito):
        sub = itm['p'] * itm['n']
        total += sub
        st.write(f"**{itm['n']}x** {itm['d']} (Col: {itm['c']}) - **${sub:,.2f}**")
        resumen += f"{itm['n']}x {itm['d']} | Col: {itm['c']} | ${sub:,.2f}\n"
        if st.button("❌", key=f"del_{i}"):
            st.session_state.carrito.pop(i)
            st.rerun()
    
    st.error(f"### TOTAL: ${total:,.2f}")
    
    msg = f"Pedido Botonera:\n{resumen}\nTOTAL: ${total:,.2f}"
    st.link_button("📲 WHATSAPP", f"https://wa.me/5493513698953?text={urllib.parse.quote(msg)}")
    st.link_button("📧 EMAIL A IVAN", f"mailto:ivanrizzi@hotmail.com?subject=Pedido&body={urllib.parse.quote(msg)}")

# --- VISTA: CATÁLOGO ---
else:
    if df.empty:
        st.warning("⚠️ No hay conexión con la lista de precios. Probá refrescar la página.")
        if st.button("REFRESCAR"): st.rerun()
    else:
        sec = st.selectbox("📂 Sección:", ["TODOS", "BOTONES", "AGUJAS", "ELASTICOS", "PUNTILLAS", "CIERRES", "HILOS", "CINTAS", "METALES", "ACCESORIOS"])
        busq = st.text_input("🔍 Buscar nombre o código:")

        # Filtro
        items = df.copy()
        if sec != "TODOS":
            items = items[items['Desc'].str.upper().str.contains(sec[:5], na=False)]
        if busq:
            items = items[items['Desc'].str.contains(busq, case=False, na=False) | items['Cod'].astype(str).str.contains(busq, na=False)]

        items = items.head(50)
        st.caption(f"Productos listos: {len(items)}")

        for idx, r in items.iterrows():
            st.markdown(f"<div class='producto'><b>{r['Desc']}</b><br>Cód: {r['Cod']} | ${r['Precio']:,.2f}</div>", unsafe_allow_html=True)
            ca, cb, cc = st.columns([2, 1, 1])
            col = ca.text_input("Color", key=f"c_{idx}")
            cant = cb.number_input("Cant", 1, 999, 1, key=f"n_{idx}")
            if cc.button("Añadir", key=f"b_{idx}"):
                st.session_state.carrito.append({'d': r['Desc'], 'p': r['Precio'], 'n': cant, 'c': col})
                st.toast("✅ Agregado")
