import streamlit as st
import pandas as pd
import urllib.parse

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Botonera Cordobesa SA", page_icon="🧵", layout="wide")

# 2. COLORES Y ESTILO OFICIAL
COLOR_MARCA = "#8d1b1b"

st.markdown(f"""
    <style>
    .stButton>button {{
        background-color: {COLOR_MARCA};
        color: white;
        border-radius: 8px;
        font-weight: bold;
        border: none;
        height: 3em;
    }}
    .producto-card {{
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid {COLOR_MARCA};
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }}
    </style>
    """, unsafe_allow_html=True)

# 3. CABECERA CON LOGOTIPO
col1, col2 = st.columns([1, 4])
with col1:
    # Logo oficial (con proxy para asegurar carga)
    logo_url = "https://static.wixstatic.com/media/893674_2f7f985a113d42f582a85710a309f488~mv2.png"
    st.image(logo_url, width=150)
with col2:
    st.markdown(f"<h1 style='color:{COLOR_MARCA}; margin-bottom:0;'>Botonera Cordobesa SA</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:1.2em; margin-top:0;'>Catálogo de Pedidos Mayoristas</p>", unsafe_allow_html=True)

st.divider()

# 4. CARGA DE DATOS
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
    if 'carrito' not in st.session_state:
        st.session_state.carrito = []

    # Buscador
    busqueda = st.text_input("🔍 ¿Qué producto buscás? (Escribí nombre o código)", "").lower()
    
    df_filtrado = df.dropna(subset=['Descripción'])
    df_filtrado = df_filtrado[
        df_filtrado['Descripción'].astype(str).str.lower().str.contains(busqueda) | 
        df_filtrado['Código'].astype(str).str.lower().str.contains(busqueda)
    ]

    st.write(f"Se encontraron {len(df_filtrado)} artículos")

    # 5. LISTADO DE PRODUCTOS
    for i, row in df_filtrado.head(50).iterrows():
        st.markdown(f"""
        <div class="producto-card">
            <span style="color:{COLOR_MARCA}; font-weight:bold;">{row['Descripción']}</span><br>
            <small>Código: {row['Código']}</small> | <b>${row['Precio']}</b> <small>+ IVA</small>
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            color = st.text_input("Color", placeholder="Ej: Blanco", key=f"col_{i}")
        with c2:
            cant = st.number_input("Cantidad", min_value=1, value=1, key=f"can_{i}")
        with c3:
            st.write(" ")
            if st.button("AÑADIR", key=f"btn_{i}"):
                st.session_state.carrito.append({
                    "desc": row['Descripción'], "cod": row['Código'],
                    "cant": cant, "color": color, "precio": row['Precio']
                })
                st.toast(f"✅ Añadido!")
        st.write("---")

    # 6. CARRITO Y WHATSAPP (BARRA LATERAL)
    if st.session_state.carrito:
        st.sidebar.header("🛒 Mi Pedido")
        mensaje_wa = "Hola Botonera Cordobesa, envío mi pedido:\n\n"
        total_aprox = 0
        
        for item in st.session_state.carrito:
            st.sidebar.write(f"• **{item['cant']}x** {item['desc']}")
            mensaje_wa += f"- {item['cant']} x {item['desc']} (Cod: {item['cod']})"
            if item['color']: mensaje_wa += f" | Color: {item['color']}"
            mensaje_wa += "\n"
            try:
                p = float(str(item['precio']).replace(',', '.'))
                total_aprox += p * item['cant']
            except: pass
        
        st
