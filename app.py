import streamlit as st
import pandas as pd
import urllib.parse

# 1. CONFIGURACION
st.set_page_config(page_title="Botonera", layout="wide")

# --- LOGIN ---
if "acceso" not in st.session_state:
    st.session_state["acceso"] = False

if not st.session_state["acceso"]:
    st.title("Acceso Clientes")
    usr = st.text_input("Usuario")
    psw = st.text_input("Contraseña", type="password")
    if st.button("INGRESAR"):
        # Usamos .strip() para evitar errores si hay un espacio de más
        if usr.strip().lower() == "botonera" and psw.strip() == "2026":
            st.session_state["acceso"] = True
            st.rerun()
        else:
            st.error("Usuario o clave incorrectos")
    st.stop()

# --- APP PRINCIPAL ---
if "carrito" not in st.session_state:
    st.session_state.carrito = []
if "ver_pedido" not in st.session_state:
    st.session_state.ver_pedido = False

# 2. CARGA DE DATOS
@st.cache_data(ttl=60)
def cargar_precios():
    url = "https://docs.google.com/uc?export=download&id=1LTJJ-iXYdcl1gRhcbXaC0jw64J9Khzwo"
    try:
        data = pd.read_csv(url, encoding='latin1', on_bad_lines='skip', sep=None, engine='python')
        data = data.iloc[:, [0, 1, 2]]
        data.columns = ['Cod', 'Desc', 'Precio']
        return data
    except:
        return None

df = cargar_precios()

if df is None:
    st.error("Error al cargar datos. Refresca la página.")
    st.stop()

# 3. INTERFAZ
st.header("🧵 Botonera Cordobesa SA")

# Boton de Carrito
if st.session_state.carrito:
    n = len(st.session_state.carrito)
    if st.button(f"🛒 REVISAR MI PEDIDO ({n} productos)", use_container_width=True):
        st.session_state.ver_pedido = not st.session_state.ver_pedido
        st.rerun()

st.divider()

if st.session_state.ver_pedido:
    st.subheader("Tu Lista")
    for i, itm in enumerate(st.session_state.carrito):
        col_a, col_b = st.columns([4, 1])
        col_a.write(f"{itm['cant']}x {itm['desc']} - {itm['color']}")
        if col_b.button("Borrar", key=f"del_{i}"):
            st.session_state.carrito.pop(i)
            st.rerun()
    
    # Enviar WhatsApp
    msg = "Pedido:\n"
    for x in st.session_state.carrito:
        msg += f"- {x['cant']}x {x['desc']} (Col: {x['color']})\n"
    link = f"https://wa.me/5493513698953?text={urllib.parse.quote(msg)}"
    st.link_button("📲 ENVIAR POR WHATSAPP", link, use_container_width=True)
    
    if st.button("⬅️ VOLVER AL CATALOGO"):
        st.session_state.ver_pedido = False
        st.rerun()

else:
    busq = st.text_input("🔍 Buscar por nombre o código")
    
    res = df[df['Desc'].str.lower().str.contains(busq.lower(), na=False) | 
             df['Cod'].astype(str).str.contains(busq, na=False)] if busq else df.head(10)

    for i, r in res.iterrows():
        st.write(f"**{r['Desc']}**")
        st.write(f"Cod: {r['Cod']} | Precio: ${r['Precio']}")
        c1, c2, c3 = st.columns([2, 1, 1])
        color = c1.text_input("Color", key=f"c_{i}")
        cant = c2.number_input("Cant", 1, 100, 1, key=f"n_{i}")
        if c3.button("Añadir", key=f"b_{i}"):
            st.session_state.carrito.append({"desc":r['Desc'], "cant":cant, "color":color, "cod":r['Cod']})
            st.toast("Añadido")
        st.divider()
