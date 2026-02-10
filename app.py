import streamlit as st
import pandas as pd
import urllib.parse

# 1. CONFIGURACION BASICA
st.set_page_config(page_title="Botonera", layout="wide")
ROJO = "#8d1b1b"

# Estilos simples y efectivos
st.markdown(f"""
    <style>
    h1, h2, h3, b {{ color: {ROJO} !important; }}
    .stButton>button {{ background-color: {ROJO}; color: white !important; width: 100%; border-radius: 10px; }}
    .stTextInput>div>div>input {{ border: 2px solid {ROJO} !important; }}
    </style>
""", unsafe_allow_html=True)

# 2. ENCABEZADO (Mismo tamaño para ambos)
st.markdown(f"<h1 style='text-align:center; margin:0;'>Botonera Cordobesa SA</h1>", unsafe_allow_html=True)
st.markdown(f"<h1 style='text-align:center; margin:0;'>Sarquis & Sepag</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Horario: Lunes a Viernes 8:30 a 17:00 hs</p>", unsafe_allow_html=True)
st.markdown("---")

# 3. SESION Y DATOS
if "auth" not in st.session_state: st.session_state["auth"] = False
if "carrito" not in st.session_state: st.session_state.carrito = []
if "ver_pedido" not in st.session_state: st.session_state.ver_pedido = False

@st.cache_data(ttl=300)
def traer_datos():
    url = "https://docs.google.com/uc?export=download&id=1LTJJ-iXYdcl1gRhcbXaC0jw64J9Khzwo"
    try:
        d = pd.read_csv(url, encoding='latin1', on_bad_lines='skip', sep=None, engine='python')
        d = d.iloc[:, [0, 1, 2]]
        d.columns = ['Cod', 'Desc', 'Precio']
        d['Precio'] = d['Precio'].astype(str).str.replace(',', '.').str.extract(r'(\d+\.?\d*)').astype(float)
        return d
    except: return None

df = traer_datos()

# 4. LOGIN
if not st.session_state["auth"]:
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        st.subheader("🔐 Acceso")
        user = st.text_input("Usuario")
        pas = st.text_input("Clave", type="password")
        if st.button("ENTRAR"):
            if user.lower() == "botonera" and pas == "2026":
                st.session_state["auth"] = True
                st.rerun()
            else: st.error("Error de datos")
    st.stop()

# 5. BOTON DE CARRITO
if st.session_state.carrito:
    if st.button(f"🛒 VER MI PEDIDO ({len(st.session_state.carrito)} ARTICULOS)"):
        st.session_state.ver_pedido = not st.session_state.ver_pedido
        st.rerun()

# 6. PANTALLA: CARRITO Y TOTAL
if st.session_state.ver_pedido:
    st.header("Tu Pedido")
    suma = 0.0
    for i, art in enumerate(st.session_state.carrito):
        subt = art['precio'] * art['cant']
        suma += subt
        c1, c2 = st.columns([4, 1])
        c1.write(f"**{art['cant']}x** {art['desc']} (Col: {art['color']}) - **${subt:,.2f}**")
        if c2.button("Eliminar", key=f"del_{i}"):
            st.session_state.carrito.pop(i)
            st.rerun()
    
    st.markdown("---")
    # TOTAL VISIBLE (Usamos h1 puro de Streamlit para que no falle)
    st.error(f"VALOR TOTAL DEL PEDIDO: ${suma:,.2f}")
    
    txt = f"Pedido Botonera:\n"
    for x in st.session_state.carrito: txt += f"- {x['cant']}x {x['desc']} (Col: {x['color']})\n"
    txt += f"\nTOTAL: ${suma:,.2f}"
    
    st.link_button("📲 ENVIAR POR WHATSAPP", f"https://wa.me/5493513698953?text={urllib.parse.quote(txt)}")
    if st.button("⬅️ VOLVER AL CATALOGO"):
        st.session_state.ver_pedido = False
        st.rerun()

# 7. PANTALLA: CATALOGO COMPLETO
else:
    busq = st.text_input("🔍 Buscar producto...", placeholder="Nombre o codigo")
    
    if busq:
        datos = df[df['Desc'].str.lower().str.contains(busq.lower(), na=False) | df['Cod'].astype(str).str.contains(busq, na=False)]
    else:
        datos = df # Muestra TODA la lista sin limites
    
    st.write(f"Viendo {len(datos)} articulos")
    
    for i, r in datos.iterrows():
        with st.container():
            st.write(f"**{r['Desc']}**")
            st.write(f"Cód: {r['Cod']} | Precio: ${r['Precio']:,.2f}")
            ca, cb, cc = st.columns([2, 1, 1])
            col = ca.text_input("Color", key=f"c{i}")
            cnt = cb.number_input("Cant", 1, 5000, 1, key=f"n{i}")
            if cc.button("Añadir", key=f"b{i}"):
                st.session_state.carrito.append({"desc":r['Desc'], "cant":cnt, "color":col, "precio":r['Precio']})
                st.toast("Añadido")
            st.divider()
