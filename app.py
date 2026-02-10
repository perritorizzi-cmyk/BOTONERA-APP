import streamlit as st
import pandas as pd
import urllib.parse

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Botonera Cordobesa SA", page_icon="🧵", layout="wide")

COLOR_BORDEAUX = "#8d1b1b"

# 2. ESTILO CSS (Buscador destacado y Tarjetas)
st.markdown(f"""
    <style>
    /* Buscador Ultra Destacado */
    div[data-baseweb="input"] {{
        border: 4px solid {COLOR_BORDEAUX} !important;
        border-radius: 15px !important;
        padding: 5px !important;
        box-shadow: 0 4px 15px rgba(141, 27, 27, 0.3) !important;
    }}
    input {{
        font-size: 1.4em !important;
        font-weight: bold !important;
    }}
    /* Tarjetas de productos */
    .producto-card {{ 
        background-color: #ffffff !important; 
        padding: 20px; 
        border-radius: 12px; 
        border-left: 8px solid {COLOR_BORDEAUX}; 
        box-shadow: 2px 4px 12px rgba(0,0,0,0.1); 
        margin-bottom: 15px;
    }}
    .titulo-prod {{ color: #1a1a1a !important; font-weight: bold; font-size: 1.2em; display: block; }}
    .precio-prod {{ color: {COLOR_BORDEAUX} !important; font-weight: bold; font-size: 1.4em; }}
    </style>
    """, unsafe_allow_html=True)

# 3. ENCABEZADO INSTITUCIONAL (Logo Doble)
# Usamos una estructura simple para evitar errores de corte de código
st.image("https://static.wixstatic.com/media/893674_2f7f985a113d42f582a85710a309f488~mv2.png", use_container_width=True)
st.markdown("<h4 style='text-align: center; color: gray;'>Catálogo de Pedidos Mayoristas Online</h4>", unsafe_allow_html=True)

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

# 5. SECCIÓN DE BÚSQUEDA (MÁS DESTACADA)
st.markdown(f"<h2 style='color:{COLOR_BORDEAUX}; text-align:center;'>🔍 BUSCAR PRODUCTO</h2>", unsafe_allow_html=True)
busqueda = st.text_input("", placeholder="Escriba aquí el nombre o el código...").strip().lower()

# Filtrado
if busqueda:
    df_filtrado = df[df['Descripción'].str.lower().str.contains(busqueda) | df['Código'].str.lower().str.contains(busqueda)]
else:
    df_filtrado = df.head(15)

# 6. LISTADO
if not df_filtrado.empty:
    for i, row in df_filtrado.iterrows():
        st.markdown(f"""
        <div class="producto-card">
            <span class="titulo-prod">{row['Descripción']}</span>
            <span style="color:gray;">Código: {row['Código']}</span><br>
            <span class="precio-prod">${row['Precio']}</span> <small>+ IVA</small>
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1: color = st.text_input("Color o número", key=f"col_{i}", placeholder="Ej: Rojo / 102")
        with c2: cant = st.number_input("Cantidad", min_value=1, value=1, key=f"can_{i}")
        with c3:
            st.write(" ")
            if st.button("AÑADIR", key=f"btn_{i}"):
                st.session_state.carrito.append({"desc": row['Descripción'], "cant": cant, "color": color, "precio": row['Precio'], "cod": row['Código']})
                st.toast("✅ ¡Sumado!")
        st.write("---")

# 7. CARRITO (SIDEBAR)
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
    link_wa = f"https://wa.me/5493513698953?text={urllib.parse.quote(mensaje_wa)}"
    st.sidebar.markdown(f'<a href="{link_wa}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:15px; border-radius:10px; font-weight:bold; cursor:pointer;">📲 ENVIAR POR WHATSAPP</button></a>', unsafe_allow_html=True)
