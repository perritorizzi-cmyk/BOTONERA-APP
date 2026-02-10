import streamlit as st
import pandas as pd
import urllib.parse

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Botonera Cordobesa SA", page_icon="🧵", layout="wide")

COLOR_BORDEAUX = "#8d1b1b"
COLOR_GRIS_TEXTO = "#444444"

# 2. ESTILO CSS: TIPOGRAFÍA, ENCABEZADO Y BUSCADOR
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Roboto:wght@400;700&display=swap');

    /* Encabezado Institucional */
    .header-container {{
        text-align: center;
        padding: 20px;
        margin-bottom: 10px;
    }}
    .nombre-empresa {{
        font-family: 'Playfair Display', serif;
        color: {COLOR_BORDEAUX};
        font-size: 2.8em;
        font-weight: 700;
        display: inline-block;
        margin: 0 20px;
        line-height: 1.1;
    }}
    .divisor {{
        border-left: 3px solid #ccc;
        height: 60px;
        display: inline-block;
        vertical-align: middle;
    }}
    .subtitulo-header {{
        color: {COLOR_GRIS_TEXTO};
        font-family: 'Roboto', sans-serif;
        font-size: 1.1em;
        letter-spacing: 2px;
        margin-top: 10px;
    }}

    /* BUSCADOR ULTRA DESTACADO */
    div[data-baseweb="input"] {{
        border: 5px solid {COLOR_BORDEAUX} !important;
        border-radius: 20px !important;
        padding: 10px !important;
        box-shadow: 0 10px 25px rgba(141, 27, 27, 0.25) !important;
        background-color: white !important;
    }}
    input {{
        font-size: 1.6em !important;
        font-weight: bold !important;
        text-align: center !important;
    }}

    /* Tarjetas de productos */
    .producto-card {{ 
        background-color: #ffffff !important; 
        padding: 20px; 
        border-radius: 12px; 
        border-left: 10px solid {COLOR_BORDEAUX}; 
        box-shadow: 2px 5px 15px rgba(0,0,0,0.08); 
        margin-bottom: 15px;
    }}
    .titulo-prod {{ color: #1a1a1a !important; font-weight: bold; font-size: 1.25em; display: block; }}
    .precio-prod {{ color: {COLOR_BORDEAUX} !important; font-weight: bold; font-size: 1.5em; }}
    
    /* Botones */
    .stButton>button {{
        background-color: {COLOR_BORDEAUX} !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        height: 3.5em !important;
        font-size: 1em !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# 3. ENCABEZADO DE TEXTO INSTITUCIONAL (Reemplaza al logo que fallaba)
st.markdown(f"""
    <div class="header-container">
        <div class="nombre-empresa">Botonera Cordobesa SA</div>
        <div class="divisor"></div>
        <div class="nombre-empresa">Sarquis & Sepag</div>
        <div class="subtitulo-header">CATÁLOGO DE PEDIDOS MAYORISTAS ONLINE</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")
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

# 5. SECCIÓN DE BÚSQUEDA DESTACADA
st.markdown(f"<h2 style='color:{COLOR_BORDEAUX}; text-align:center; font-family:sans-serif;'>🔍 ¿QUÉ ARTÍCULO BUSCÁS?</h2>", unsafe_allow_html=True)
busqueda = st.text_input("", placeholder="Ingresá nombre o código aquí...", label_visibility="collapsed").strip().lower()

# Filtrado
if busqueda:
    df_filtrado = df[df['Descripción'].str.lower().str.contains(busqueda) | df['Código'].str.lower().str.contains(busqueda)]
else:
    df_filtrado = df.head(12)

# 6. LISTADO
if not df_filtrado.empty:
    for i, row in df_filtrado.iterrows():
        st.markdown(f"""
        <div class="producto-card">
            <span class="titulo-prod">{row['Descripción']}</span>
            <span style="color:gray; font-size:0.9em;">Código: {row['Código']}</span><br>
            <span class="precio-prod">${row['Precio']} <small style="font-size:0.6em; color:gray;">+ IVA</small></span>
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1: color = st.text_input("Color o número", key=f"col_{i}", placeholder="Ej: Rojo / 102")
        with c2: cant = st.number_input("Cantidad", min_value=1, value=1, key=f"can_{i}")
        with c3:
            st.write(" ")
            if st.button("AÑADIR", key=f"btn_{i}"):
                st.session_state.carrito.append({
                    "desc": row['Descripción'], "cant": cant, 
                    "color": color, "precio": row['Precio'], "cod": row['Código']
                })
                st.toast("✅ Agregado")
        st.write("---")

# 7. CARRITO (Sidebar)
if st.session_state.carrito:
    st.sidebar.header("🛒 Tu Pedido")
    mensaje_wa = "Hola Botonera Cordobesa, envío mi pedido:\n\n"
    total = 0
    for item in st.session_state.carrito:
        st.sidebar.write(f"• **{item['cant']}x** {item['desc']}")
        mensaje_wa += f"- {item['cant']}x {item['desc']} (Cod: {item['cod']}) | Color/Nro: {item['color']}\n"
        try: 
            p = float(str(item['precio']).replace(',', '.'))
            total += p * item['cant']
        except: pass
    
    st.sidebar.divider()
    st.sidebar.write(f"### Total aprox: ${total:,.2f}")
    link_wa = f"https://wa.me/5493513698953?text={urllib.parse.quote(mensaje_wa)}"
    st.sidebar.markdown(f'<a href="{link_wa}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:15px; border-radius:10px; font-weight:bold; cursor:pointer;">📲 ENVIAR POR WHATSAPP</button></a>', unsafe_allow_html=True)
