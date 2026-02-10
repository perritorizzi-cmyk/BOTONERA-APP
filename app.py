import streamlit as st
import pandas as pd
import urllib.parse

# 1. CONFIGURACIÓN Y ESTILO
st.set_page_config(page_title="Botonera Cordobesa SA", page_icon="🧵", layout="wide")

COLOR_BORDEAUX = "#8d1b1b"

st.markdown(f"""
    <style>
    .stButton>button {{ background-color: {COLOR_BORDEAUX}; color: white; border-radius: 8px; font-weight: bold; border: none; }}
    .producto-card {{ background-color: #ffffff; padding: 15px; border-radius: 10px; border-left: 5px solid {COLOR_BORDEAUX}; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); margin-bottom: 10px; }}
    </style>
    """, unsafe_allow_html=True)

# 2. CABECERA (Logo y Título)
col1, col2 = st.columns([1, 4])
with col1:
    # Usamos el logo oficial directamente
    st.image("https://static.wixstatic.com/media/893674_2f7f985a113d42f582a85710a309f488~mv2.png", width=140)
with col2:
    st.markdown(f"<h1 style='color:{COLOR_BORDEAUX};'>Botonera Cordobesa SA</h1>", unsafe_allow_html=True)
    st.write("Catálogo de Pedidos Mayoristas Online")

st.divider()

# 3. CARGA DE DATOS
FILE_ID = "1LTJJ-iXYdcl1gRhcbXaC0jw64J9Khzwo"
SHEET_URL = f"https://docs.google.com/uc?export=download&id={FILE_ID}"

@st.cache_data(ttl=600)
def load_data():
    df = pd.read_csv(SHEET_URL, encoding='latin1', on_bad_lines='skip', sep=None, engine='python')
    df = df.iloc[:, [0, 1, 2]]
    df.columns = ['Código', 'Descripción', 'Precio']
    return df

try:
    df = load_data()
    if 'carrito' not in st.session_state: st.session_state.carrito = []

    busqueda = st.text_input("🔍 ¿Qué buscas? (Nombre o código)", "")
    
    df_filtrado = df.dropna(subset=['Descripción'])
    df_filtrado = df_filtrado[df_filtrado['Descripción'].astype(str).str.contains(busqueda, case=False) | df_filtrado['Código'].astype(str).str.contains(busqueda, case=False)]

    for i, row in df_filtrado.head(50).iterrows():
        st.markdown(f'<div class="producto-card"><b>{row["Descripción"]}</b><br><small>Cod: {row["Código"]}</small> | <b>${row["Precio"]}</b></div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1: color = st.text_input("Color", key=f"col_{i}")
        with c2: cant = st.number_input("Cant", min_value=1, value=1, key=f"can_{i}")
        with c3:
            st.write(" ")
            if st.button("AÑADIR", key=f"btn_{i}"):
                st.session_state.carrito.append({"desc": row['Descripción'], "cant": cant, "color": color, "precio": row['Precio'], "cod": row['Código']})
                st.toast("¡Sumado!")
        st.write("---")

    # BARRA LATERAL (CARRITO)
    if st.session_state.carrito:
        st.sidebar.header("🛒 Mi Pedido")
        mensaje_wa = "Hola Botonera Cordobesa, este es mi pedido:\n\n"
        total = 0
        for item in st.session_state.carrito:
            st.sidebar.write(f"• {item['cant']}x {item['desc']}")
            mensaje_wa += f"- {item['cant']}x {item['desc']} (Cod: {item['cod']}) | Col: {item['color']}\n"
            try: total += float(str(item['precio']).replace(',', '.')) * item['cant']
            except: pass
        
        st.sidebar.write(f"### Total: ${total:,.2f}")
        link_wa = f"https://wa.me/5493513698953?text={urllib.parse.quote(mensaje_wa)}"
        st.sidebar.markdown(f'<a href="{link_wa}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; border-radius:8px; font-weight:bold;">📲 ENVIAR PEDIDO</button></a>', unsafe_allow_html=True)
        if st.sidebar.button("Vaciar"):
            st.session_state.carrito = []
            st.rerun()

except Exception as e:
    st.error("Error al conectar con la base de datos.")
