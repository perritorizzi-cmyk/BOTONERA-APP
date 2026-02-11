import streamlit as st
import pandas as pd
import urllib.parse

# 1. CONFIGURACIÓN E ICONO
st.set_page_config(page_title="Botonera Cordobesa", page_icon="logo.png", layout="wide")
COLOR_ROJO = "#8d1b1b"

st.markdown(f"""
    <style>
    h1, h2, h3, b {{ color: {COLOR_ROJO} !important; font-family: 'serif'; }}
    .stButton>button {{ background-color: {COLOR_ROJO}; color: white !important; border-radius: 10px; width: 100%; font-weight: bold; }}
    .stTextInput>div>div>input {{ border: 2px solid {COLOR_ROJO} !important; }}
    .stAlert {{ border: 2px solid {COLOR_ROJO} !important; background-color: #fff1f1 !important; }}
    </style>
""", unsafe_allow_html=True)

# 2. ENCABEZADO
st.markdown(f"<h1 style='text-align:center; margin-bottom:0;'>Botonera Cordobesa SA</h1>", unsafe_allow_html=True)
st.markdown(f"<h1 style='text-align:center; margin-top:0;'>Sarquis & Sepag</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'><b>Horario:</b> Lunes a Viernes 8:30 a 17:00 hs</p>", unsafe_allow_html=True)
st.markdown("---")

# 3. ESTADOS
if "auth" not in st.session_state: st.session_state["auth"] = False
if "carrito" not in st.session_state: st.session_state.carrito = []
if "ver_pedido" not in st.session_state: st.session_state.ver_pedido = False

# 4. CARGA DE DATOS
@st.cache_data(ttl=600)
def cargar_excel():
    url = "https://docs.google.com/uc?export=download&id=1LTJJ-iXYdcl1gRhcbXaC0jw64J9Khzwo"
    try:
        d = pd.read_csv(url, encoding='latin1', on_bad_lines='skip', sep=None, engine='python')
        d = d.iloc[:, [0, 1, 2]]
        d.columns = ['Cod', 'Desc', 'Precio']
        d['Precio'] = d['Precio'].astype(str).str.replace(',', '.').str.extract(r'(\d+\.?\d*)').astype(float)
        return d
    except: return None

df = cargar_excel()

# 5. LOGIN
if not st.session_state["auth"]:
    _, col_log, _ = st.columns([1, 4, 1])
    with col_log:
        st.subheader("🔐 Acceso Clientes")
        u_ing = st.text_input("Usuario")
        p_ing = st.text_input("Contraseña", type="password")
        if st.button("INGRESAR"):
            if u_ing.strip().lower() == "botonera" and p_ing.strip() == "2026":
                st.session_state["auth"] = True
                st.rerun()
            else: st.error("Datos incorrectos")
    st.stop()

# 6. CARRITO
if st.session_state.carrito:
    if st.button(f"🛒 REVISAR MI PEDIDO ({len(st.session_state.carrito)} ítems)"):
        st.session_state.ver_pedido = not st.session_state.ver_pedido
        st.rerun()

# --- VISTA PEDIDO (CON OPCIÓN EMAIL) ---
if st.session_state.ver_pedido:
    st.header("Tu Pedido")
    suma_total = 0.0
    
    # Listado para visualización
    for i, itm in enumerate(st.session_state.carrito):
        sub = itm['precio'] * itm['cant']
        suma_total += sub
        c1, c2 = st.columns([4, 1])
        c1.write(f"**{itm['cant']}x** {itm['desc']} (Col: {itm['color']}) - ${sub:,.2f}")
        if c2.button("❌", key=f"del_{i}"):
            st.session_state.carrito.pop(i)
            st.rerun()
    
    st.error(f"### TOTAL A PAGAR: ${suma_total:,.2f}")
    
    # FORMATEO PARA WHATSAPP
    msg_wa = f"Pedido Botonera Cordobesa:\n"
    for x in st.session_state.carrito:
        msg_wa += f"- {x['cant']}x {x['desc']} (Col: {x['color']}) - ${x['precio']*x['cant']:,.2f}\n"
    msg_wa += f"\nTOTAL: ${suma_total:,.2f}"
    
    # FORMATEO PARA EMAIL (Imprimible)
    destinatario = "ivanrizzi@hotmail.com"
    asunto = "NUEVO PEDIDO - BOTONERA CORDOBESA"
    cuerpo_mail = "DETALLE DEL PEDIDO:\n\n"
    cuerpo_mail += "CANT | DESCRIPCION | COLOR | SUBTOT\n"
    cuerpo_mail += "---------------------------------------\n"
    for x in st.session_state.carrito:
        cuerpo_mail += f"{x['cant']} x {x['desc']} | Col: {x['color']} | ${x['precio']*x['cant']:,.2f}\n"
    cuerpo_mail += "---------------------------------------\n"
    cuerpo_mail += f"TOTAL GENERAL: ${suma_total:,.2f}"
    
    # BOTONES DE ENVÍO
    st.link_button("📲 ENVIAR POR WHATSAPP", f"https://wa.me/5493513698953?text={urllib.parse.quote(msg_wa)}")
    
    st.link_button("📧 ENVIAR POR EMAIL (Para imprimir)", 
                   f"mailto:{destinatario}?subject={urllib.parse.quote(asunto)}&body={urllib.parse.quote(cuerpo_mail)}")
    
    if st.button("⬅️ VOLVER AL CATÁLOGO"):
        st.session_state.ver_pedido = False
        st.rerun()

# --- VISTA CATÁLOGO ---
else:
    busq = st.text_input("🔍 Buscar artículo o código...")
    mostrables = df[df['Desc'].str.lower().str.contains(busq.lower(), na=False) | 
                    df['Cod'].astype(str).str.contains(busq, na=False)] if busq else df

    st.info(f"Mostrando {len(mostrables)} artículos")

    for idx, fila in mostrables.iterrows():
        with st.container():
            st.markdown(f"**{fila['Desc']}**")
            st.write(f"Cód: {fila['Cod']} | Precio: ${fila['Precio']:,.2f}")
            ca, cb, cc = st.columns([2, 1, 1])
            col_sel = ca.text_input("Color", key=f"c_{idx}")
            can_sel = cb.number_input("Cant", 1, 5000, 1, key=f"n_{idx}")
            if cc.button("Añadir", key=f"b_{idx}"):
                st.session_state.carrito.append({
                    "desc": fila['Desc'], "cant": can_sel, "color": col_sel, 
                    "precio": fila['Precio'], "cod": fila['Cod']
                })
                st.toast("✅ Agregado")
            st.divider()
