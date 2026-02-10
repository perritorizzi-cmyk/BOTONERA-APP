import streamlit as st
import pandas as pd
import urllib.parse

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Botonera Cordobesa SA", page_icon="🧵", layout="wide")

COLOR_ROJO = "#8d1b1b"

# 2. ESTILO CSS: ENCABEZADO Y BUSCADOR MEJORADO
st.markdown(f"""
    <style>
    /* Estilo para los nombres en la misma línea (PC y Celular) */
    .header-container {{
        display: flex;
        align-items: center;
        justify-content: center;
        flex-wrap: wrap;
        text-align: center;
        gap: 15px;
        padding: 10px;
    }}
    .nombre-header {{
        color: {COLOR_ROJO};
        font-family: 'Times New Roman', serif;
        font-size: 1.8em;
        font-weight: bold;
        margin: 0;
    }}
    .divisor-header {{
        border-left: 2px solid #ccc;
        height: 40px;
    }}
    
    /* BUSCADOR DESTACADO SIN BARRAS NEGRAS */
    div[data-baseweb="input"] {{
        border: 4px solid {COLOR_ROJO} !important;
        border-radius: 12px !important;
        background-color: white !important;
    }}
    input {{
        color: #333 !important;
        font-size: 1.2em !important;
    }}

    /* Tarjetas de productos siempre legibles */
    .producto-card {{ 
        background-color: #ffffff !important; 
        padding: 15px; 
        border-radius: 10px; 
        border-left: 8px solid {COLOR_ROJO}; 
        box-shadow: 2px 4px 10px rgba(0,0,0,0.1); 
        margin-bottom: 10px;
    }}
    .titulo-prod {{ color: #1a1a1a !important; font-weight: bold; font-size: 1.1em; }}
    .precio-prod {{ color: {COLOR_ROJO} !important; font-weight: bold; font-size: 1.3em; }}
    
    /* Etiquetas de color y cantidad en blanco para que se vean en modo oscuro */
    label {{ color: white !important; font-weight: bold !important; }}
    </style>
    """, unsafe_allow_html=True)

# 3. ENCABEZADO TIPO LOGO (Botonera | Sarquis)
st.markdown(f"""
    <div class="header-container">
        <p class="nombre-header">Botonera Cordobesa SA</p>
        <div class="divisor-header"></div>
        <p class="nombre-header">Sarquis & Sepag</p>
    </div>
    <p style='text-align: center; color: gray; margin-top: -10px;'>Catálogo de Pedidos Mayoristas Online</p>
    """, unsafe_allow_html=True)

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

# 5. BUSCADOR DESTACADO
st.markdown(f"<h3 style='color:{COLOR_ROJO}; text-align:center;'>🔍 ¿QUÉ ARTÍCULO BUSCÁS?</h3>", unsafe_allow_html=True)
busqueda = st.text_input("Buscador", placeholder="Ingresá nombre o código aquí...", label_visibility="collapsed").strip().lower()

# Filtrado
if busqueda:
    df_filtrado = df[df['Descripción'].str.lower().str.contains(busqueda) | df['Código'].str.lower().str.contains(busqueda)]
else:
    df_filtrado = df.head(10)

# 6. LISTADO DE RESULTADOS
if not df_filtrado.empty:
    for i, row in df_filtrado.iterrows():
        st.markdown(f"""
        <div class="producto-card">
            <span class="titulo-prod">{row['Descripción']}</span><br>
            <span style="color:gray; font-size:0.9em;">Código: {row['Código']}</span><br>
            <span class="precio-prod">${row['Precio']}</span> <small style="color:gray;">+ IVA</small>
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1: color = st.text_input("Color o número", key=f"col_{i}", placeholder="Ej: Blanco")
        with c2: cant = st.number_input("Cant", min_value=1, value=1, key=f"can_{i}")
        with c3:
            st.write(" ")
            if st.button("AÑADIR", key=f"btn_{i}"):
                st.session_state.carrito.append({"desc": row['Descripción'], "cant": cant, "color": color, "precio": row['Precio'], "cod": row['Código']})
                st.toast("✅ Agregado")
        st.write("---")

# 7. CARRITO (SIDEBAR)
if st.session_state.carrito:
    st.sidebar.header("🛒 Mi Pedido")
    mensaje_wa = "Hola Botonera Cordobesa, envío mi pedido:\n\n"
    for item in st.session_state.carrito:
        st.sidebar.write(f"• **{item['cant']}x** {item['desc']}")
        mensaje_wa += f"- {item['cant']}x {item['desc']} (Cod: {item['cod']}) | Col: {item['color']}\n"
    
    link_wa = f"https://wa.me/5493513698953?text={urllib.parse.quote(mensaje_wa)}"
    st.sidebar.markdown(f'<a href="{link_wa}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:15px; border-radius:10px; font-weight:bold; cursor:pointer;">📲 ENVIAR POR WHATSAPP</button></a>', unsafe_allow_html=True)
    if st.sidebar.button("Vaciar Carrito"):
        st.session_state.carrito = []
        st.rerun()
