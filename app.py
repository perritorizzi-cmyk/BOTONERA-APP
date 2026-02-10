import streamlit as st
import pandas as pd
import urllib.parse

# 1. AJUSTES DE PÁGINA
st.set_page_config(page_title="Botonera Cordobesa", page_icon="🧵", layout="wide")

# --- LOGIN ---
if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    st.title("🔐 Acceso Mayorista")
    u = st.text_input("Usuario")
    p = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        if u.lower() == "botonera" and p == "2026":
            st.session_state["auth"] = True
            st.rerun()
        else:
            st.error("Datos incorrectos")
    st.stop()

# --- APP PRINCIPAL ---
if "carrito" not in st.session_state:
    st.session_state.carrito = []
if "ver_pedido" not in st.session_state:
    st.session_state.ver_pedido = False

# Encabezado simple para evitar errores de diseño
st.markdown("<h1 style='text-align:center; color:#8d1b1b;'>Botonera Cordobesa SA</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Sarquis & Sepag</p>", unsafe_allow_html=True)

# 2. CARGA DE DATOS
@st.cache_data(ttl=300)
def cargar_base():
    url = "https://docs.google.com/uc?export=download&id=1LTJJ-iXYdcl1gRhcbXaC0jw64J9Khzwo"
    try:
        df = pd.read_csv(url, encoding='latin1', on_bad_lines='skip', sep=None, engine='python')
        df = df.iloc[:, [0, 1, 2]]
        df.columns = ['Cod', 'Desc', 'Precio']
        return df
    except:
        return pd.DataFrame(columns=['Cod', 'Desc', 'Precio'])

df = cargar_base()

# 3. INTERFAZ: ¿VER PEDIDO O VER CATÁLOGO?
if st.session_state.ver_pedido:
    st.header("🛒 Tu Pedido Actual")
    if not st.session_state.carrito:
        st.warning("El carrito está vacío")
    else:
        for i, item in enumerate(st.session_state.carrito):
            c1, c2 = st.columns([4, 1])
            c1.write(f"**{item['cant']}x** {item['desc']} (Color: {item['color']})")
            if c2.button("❌", key=f"del_{i}"):
                st.session_state.carrito.pop(i)
                st.rerun()
        
        # WhatsApp Link
        txt = "Pedido Botonera:\n\n"
        for itm in st.session_state.carrito:
            txt += f"- {itm['cant']}x {itm['desc']} (Cod: {itm['cod']}) Col: {itm['color']}\n"
        link = f"https://wa.me/5493513698953?text={urllib.parse.quote(txt)}"
        st.markdown(f'<a href="{link}" target="_blank"><button style="width:100%; background:#25D366; color:white; border:none; padding:15px; border-radius:10px; font-weight:bold;">📲 ENVIAR POR WHATSAPP</button></a>', unsafe_allow_html=True)

    if st.button("⬅️ VOLVER A BUSCAR PRODUCTOS", use_container_width=True):
        st.session_state.ver_pedido = False
        st.rerun()

else:
    # BUSCADOR
    busq = st.text_input("🔍 ¿Qué estás buscando?", placeholder="Escribe nombre o código...").strip().lower()
    
    filtro = df[df['Desc'].str.lower().str.contains(busq) | df['Cod'].str.lower().str.contains(busq)] if busq else df.head(12)

    for i, r in filtro.iterrows():
        with st.container():
            st.markdown(f"**{r['Desc']}** \n*Cod: {r['Cod']}* - **${r['Precio']}**")
            col_a, col_b, col_c = st.columns([2, 1, 1])
            color = col_a.text_input("Color/Nro", key=f"col_{i}")
            cant = col_b.number_input("Cant", min_value=1, value=1, key=f"can_{i}")
            if col_c.button("➕", key=f"btn_{i}"):
                st.session_state.carrito.append({"desc": r['Desc'], "cant": cant, "color": color, "cod": r['Cod']})
                st.toast("¡Agregado!")
            st.divider()

    # BOTÓN FLOTANTE DE REVISIÓN
    if st.session_state.carrito:
        total_items = sum(int(x['cant']) for x in st.session_state.carrito)
        if st.button(f"🛒 REVISAR MI PEDIDO ({total_items} ítems)", use_container_width=True, type="primary"):
            st.session_state.ver_pedido = True
            st.rerun()
