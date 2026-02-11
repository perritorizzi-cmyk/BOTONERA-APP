import streamlit as st
import pandas as pd
import urllib.parse

# 1. CONFIGURACIÓN Y ESTILO DIRECTO
st.set_page_config(page_title="Botonera Cordobesa", layout="wide")
COLOR_INST = "#8d1b1b"

st.markdown(f"""
    <style>
    h1, h2, h3, b {{ color: {COLOR_INST} !important; }}
    .stButton>button {{ background-color: {COLOR_INST}; color: white !important; border-radius: 10px; width: 100%; }}
    .stTextInput>div>div>input {{ border: 2px solid {COLOR_INST} !important; }}
    </style>
""", unsafe_allow_html=True)

# 2. ENCABEZADO UNIFICADO
st.markdown(f"<h1 style='text-align:center; margin-bottom:0;'>Botonera Cordobesa SA</h1>", unsafe_allow_html=True)
st.markdown(f"<h1 style='text-align:center; margin-top:0;'>Sarquis & Sepag</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'><b>Horario:</b> Lunes a Viernes 8:30 a 17:00 hs</p>", unsafe_allow_html=True)
st.markdown("---")

# 3. MANEJO DE ESTADO
if "auth" not in st.session_state: st.session_state["auth"] = False
if "carrito" not in st.session_state: st.session_state.carrito = []
if "ver_pedido" not in st.session_state: st.session_state.ver_pedido = False

# 4. CARGA DE BASE DE DATOS
@st.cache_data(ttl=600)
def cargar_catalogo():
    url = "https://docs.google.com/uc?export=download&id=1LTJJ-iXYdcl1gRhcbXaC0jw64J9Khzwo"
    try:
        d = pd.read_csv(url, encoding='latin1', on_bad_lines='skip', sep=None, engine='python')
        d = d.iloc[:, [0, 1, 2]]
        d.columns = ['Cod', 'Desc', 'Precio']
        d['Precio'] = d['Precio'].astype(str).str.replace(',', '.').str.extract(r'(\d+\.?\d*)').astype(float)
        return d
    except: return None

df = cargar_catalogo()

# 5. LOGIN (Optimizado para celular)
if not st.session_state["auth"]:
    _, col_login, _ = st.columns([1, 4, 1])
    with col_login:
        st.subheader("🔐 Acceso Clientes")
        usuario_ingresado = st.text_input("Usuario")
        clave_ingresada = st.text_input("Contraseña", type="password")
        if st.button("INGRESAR"):
            # Limpiamos espacios por si el autocorrector del celular agrega uno
            if usuario_ingresado.strip().lower() == "botonera" and clave_ingresada.strip() == "2026":
                st.session_state["auth"] = True
                st.rerun()
            else:
                st.error("Usuario o clave incorrectos")
    st.stop()

# 6. INTERFAZ POST-LOGIN
if st.session_state.carrito:
    if st.button(f"🛒 REVISAR MI PEDIDO ({len(st.session_state.carrito)} ítems)"):
        st.session_state.ver_pedido = not st.session_state.ver_pedido
        st.rerun()

# --- VISTA CARRITO ---
if st.session_state.ver_pedido:
    st.header("📝 Resumen de Pedido")
    total = 0.0
    for i, itm in enumerate(st.session_state.carrito):
        sub = itm['precio'] * itm['cant']
        total += sub
        c1, c2 = st.columns([4, 1])
        c1.write(f"**{itm['cant']}x** {itm['desc']} (Col: {itm['color']}) - ${sub:,.2f}")
        if c2.button("❌", key=f"del_{i}"):
            st.session_state.carrito.pop(i)
            st.rerun()
    
    st.markdown("---")
    # TOTAL EN BARRA ROJA (Garantizado que se vea)
    st.error(f"### IMPORTE TOTAL: ${total:,.2f}")
    
    # Preparar mensaje WhatsApp
    msg = f"Pedido Botonera Cordobesa:\n"
    for x in st.session_state.carrito:
        msg += f"- {x['cant']}x {x['desc']} (Col: {x['color']}) - ${x['precio']*x['cant']:,.2f}\n"
    msg += f"\nTOTAL: ${total:,.2f}"
    
    st.link_button("📲 ENVIAR PEDIDO POR WHATSAPP", f"https://wa.me/5493513698953?text={urllib.parse.quote(msg)}")
    
    if st.button("⬅️ VOLVER AL CATÁLOGO"):
        st.session_state.ver_pedido = False
        st.rerun()

# --- VISTA CATÁLOGO ---
else:
    busqueda = st.text_input("🔍 Buscar artículo o código...")
    
    if busqueda:
        items = df[df['Desc'].str.lower().str.contains(busqueda.lower(), na=False) | 
                   df['Cod'].astype(str).str.contains(busqueda, na=False)]
    else:
        items = df # Muestra toda la lista

    st.info(f"Mostrando {len(items)} productos")

    for idx, row in items.iterrows():
        with st.container():
            st.markdown(f"**{row['Desc']}**")
            st.write(f"Código: {row['Cod']} | Precio: ${row['Precio']:,.2f}")
            col_a, col_b, col_c = st.columns([2, 1, 1])
            color_sel = col_a.text_input("Color", key=f"color_{idx}")
            cant_sel = col_b.number_input("Cant", 1, 5000, 1, key=f"cant_{idx}")
            if col_c.button("Añadir", key=f"btn_{idx}"):
                st.session_state.carrito.append({
                    "desc": row['Desc'], "cant": cant_sel, "color": color_sel, 
                    "precio": row['Precio'], "cod": row['Cod']
                })
                st.toast("Añadido al pedido")
            st.divider()
