import streamlit as st
import pandas as pd
import urllib.parse
import base64
import requests

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Botonera Cordobesa SA", page_icon="🧵", layout="wide")

COLOR_BORDEAUX = "#8d1b1b"

# ESTILO PARA MÓVILES Y VISIBILIDAD
st.markdown(f"""
    <style>
    .producto-card {{ 
        background-color: #ffffff !important; 
        padding: 15px; 
        border-radius: 10px; 
        border-left: 5px solid {COLOR_BORDEAUX}; 
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1); 
        margin-bottom: 10px;
    }}
    .titulo-prod {{ color: #1a1a1a !important; font-weight: bold; font-size: 1.1em; display: block; }}
    .subtitulo-prod {{ color: #444444 !important; font-size: 0.8em; }}
    .precio-prod {{ color: {COLOR_BORDEAUX} !important; font-weight: bold; font-size: 1.2em; }}
    .stButton>button {{ background-color: {COLOR_BORDEAUX}; color: white !important; border-radius: 8px; font-weight: bold; }}
    </style>
    """, unsafe_allow_html=True)

# 2. FUNCIÓN PARA CARGAR LOGO
def get_base64_logo(url):
    try:
        response = requests.get(url)
        return base64.b64encode(response.content).decode()
    except:
        return None

# 3. CABECERA
logo_url = "https://static.wixstatic.com/media/893674_2f7f985a113d42f582a85710a309f488~mv2.png"
logo_base64 = get_base64_logo(logo_url)

col1, col2 = st.columns([1, 3])
with col1:
    if logo_base64:
        st.markdown(f'<img src="data:image/png;base64,{logo_base64}" width="160">', unsafe_allow_html=True)
    else:
        st.write("🧵")
with col2:
    st.markdown(f"<h1 style='color:{COLOR_BORDEAUX}; margin-bottom:0;'>Botonera Cordobesa SA</h1>", unsafe_allow_html=True)
    st.write("Pedidos Mayoristas Online")

st.divider()

# 4. CARGA DE DATOS
FILE_ID = "1LTJJ-iXYdcl1gRhcbXaC0jw64J9Khzwo"
SHEET_URL = f"https://docs.google.com/uc?export=download&id={FILE_ID}"

@st.cache_data(ttl=300)
def load_data():
    try:
        df = pd.read_csv(SHEET_URL, encoding='latin1', on_bad_lines='skip', sep=None, engine='python')
        df = df.iloc[:, [0, 1, 2]]
        df.columns = ['Código', 'Descripción', 'Precio']
        df['Descripción'] = df['Descripción'].fillna('').astype(str)
        df['Código'] = df['Código'].fillna('').astype(str)
        return df
    except:
        return pd.DataFrame(columns=['Código', 'Descripción', 'Precio'])

df = load_data()
if 'carrito' not in st.session_state: st.session_state.carrito = []

# 5. BUSCADOR Y LISTADO
busqueda = st.text_input("🔍 ¿Qué producto buscás?", value="", placeholder="Ej: Cierre, Boton...").strip().lower()

df_filtrado = df[df['Descripción'].str.lower().str.contains(busqueda) | df['Código'].str.lower().str.contains(busqueda)] if busqueda else df.head(20)

if not df_filtrado.empty:
    for i, row in df_filtrado.iterrows():
        st.markdown(f"""
        <div class="producto-card">
            <span class="titulo-prod">{row['Descripción']}</span>
            <span class="subtitulo-prod">Código: {row['Código']}</span><br>
            <span class="precio-prod">${row['Precio']}</span>
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1: 
            # CAMBIO SOLICITADO AQUÍ:
            color = st.text_input("Color o número", key=f"col_{i}", placeholder="Ej: Rojo o 102")
        with c2: 
            cant = st.number_input("Cant", min_value=1, value=1, key=f"can_{i}")
        with c3:
            st.write(" ")
            if st.button("➕", key=f"btn_{i}"):
                st.session_state.carrito.append({"desc": row['Descripción'], "cant": cant, "color": color, "precio": row['Precio'], "cod": row['Código']})
                st.toast("✅ ¡Agregado!")
        st.write("---")

# 6. CARRITO (SIDEBAR)
if st.session_state.carrito:
    st.sidebar.header("🛒 Mi Pedido")
    mensaje_wa = "Hola Botonera Cordobesa, envío mi pedido:\n\n"
    total = 0
    for item in st.session_state.carrito:
        st.sidebar.write(f"• **{item['cant']}x** {item['desc']}")
        mensaje_wa += f"- {item['cant']}x {item['desc']} (Cod: {item['cod']}) | Color/Nro: {item['color']}\n"
        try: total += float(str(item['precio']).replace(',', '.')) * item['cant']
        except: pass
    
    st.sidebar.write(f"### Total aprox: ${total:,.2f}")
    link_wa = f"https://wa.me/5493513698953?text={urllib.parse.quote(mensaje_wa + f'\\nTotal: ${total:,.2f}')}"
    st.sidebar.markdown(f'<a href="{link_wa}" target="_blank"><button style="width:100%; background-color:#25D366; color:white !important; border:none; padding:12px; border-radius:8px; font-weight:bold; cursor:pointer;">📲 ENVIAR POR WHATSAPP</button></a>', unsafe_allow_html=True)
    if st.sidebar.button("Vaciar Carrito"):
        st.session_state.carrito = []
        st.rerun()
