import streamlit as st
import pandas as pd
import urllib.parse

# 1. CONFIGURACIÓN DE PÁGINA E IDENTIDAD VISUAL
st.set_page_config(page_title="Botonera Cordobesa SA - Pedidos", page_icon="🧵", layout="wide")

# Colores extraídos de botoneracordobesa.com.ar
COLOR_BORDEAUX = "#8d1b1b"
COLOR_GRIS_FONDO = "#f8f9fa"

st.markdown(f"""
    <style>
    /* Estilo General y Tipografía */
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
    html, body, [class*="css"] {{
        font-family: 'Montserrat', sans-serif;
    }}
    
    /* Botones con el rojo de la marca */
    .stButton>button {{
        width: 100%;
        background-color: {COLOR_BORDEAUX};
        color: white;
        border-radius: 5px;
        font-weight: 700;
        border: none;
        height: 3em;
        transition: 0.3s;
    }}
    .stButton>button:hover {{
        background-color: #6d1515;
        color: white;
    }}
    
    /* Tarjetas de productos */
    .producto-card {{
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-top: 4px solid {COLOR_BORDEAUX};
        margin-bottom: 15px;
    }}
    </style>
    """, unsafe_allow_html=True)

# 2. CABECERA CON LOGO OFICIAL
col1, col2 = st.columns([1, 4])
with col1:
    # Logo oficial extraído de tu web
    st.image("https://static.wixstatic.com/media/893674_2f7f985a113d42f582a85710a309f488~mv2.png", width=150)
with col2:
    st.title("Botonera Cordobesa SA")
    st.subheader("Catálogo Interactivo de Pedidos Mayoristas")

st.divider()

# 3. CARGA DE DATOS (Tu archivo de Drive)
FILE_ID = "1LTJJ-iXYdcl1gRhcbXaC0jw64J9Khzwo"
SHEET_URL = f"https://docs.google.com/uc?export=download&id={FILE_ID}"

@st.cache_data(ttl=600)
def load_data():
    # Cargamos ignorando líneas erróneas y con la codificación correcta
    df = pd.read_csv(SHEET_URL, encoding='latin1', on_bad_lines='skip', sep=None, engine='python')
    df = df.iloc[:, [0, 1, 2]]
    df.columns = ['Código', 'Descripción', 'Precio']
    return df

try:
    df = load_data()
    if 'carrito' not in st.session_state: st.session_state.carrito = []

    # Buscador principal
    busqueda = st.text_input("🔍 Buscar por nombre de artículo o código (ej: Cierre, Botón, 1234)...", "").lower()
    
    df_filtrado = df.dropna(subset=['Descripción'])
    df_filtrado = df_filtrado[
        df_filtrado['Descripción'].astype(str).str.lower().str.contains(busqueda) | 
        df_filtrado['Código'].astype(str).str.lower().str.contains(busqueda)
    ]

    st.write(f"Mostrando {len(df_filtrado)} productos disponibles")

    # 4. GRILLA DE PRODUCTOS
    for i, row in df_filtrado.head(50).iterrows():
        with st.container():
            # Diseño de tarjeta para cada producto
            st.markdown(f"""
            <div class="producto-card">
                <span style="color: {COLOR_BORDEAUX}; font-weight: bold; font-size: 1.1em;">{row['Descripción']}</span><br>
                <small>Código de artículo: {row['Código']}</small><br>
                <b style="font-size: 1.3em;">${row['Precio']}</b> <small>+ IVA</small>
            </div>
            """, unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns([2, 2, 1])
            with c1:
                color = st.text_input("Color deseado", placeholder="Ej: Rojo 02", key=f"col_{i}")
            with c2:
                cant = st.number_input("Cantidad", min_value=1, value=1, key=f"can_{i}")
            with c3:
                st.write(" ") # Espacio estético
                if st.button("AGREGAR", key=f"btn_{i}"):
                    st.session_state.carrito.append({
                        "desc": row['Descripción'], "cod": row['Código'],
                        "cant": cant, "color": color, "precio": row['Precio']
                    })
                    st.toast(f"✅ Sumado al carrito")
            st.write(" ")

    # 5. BARRA LATERAL (EL CARRITO)
    if st.session_state.carrito:
        st.sidebar.header("🛒 Tu Pedido Actual")
        mensaje_wa = "Hola Botonera Cordobesa, envío mi pedido:\n\n"
        total_aprox = 0
        
        for item in st.session_state.carrito:
            st.sidebar.markdown(f"**{item['cant']}x** {item['desc']}")
            if item['color']: st.sidebar.caption(f"Color: {item['color']}")
            
            mensaje_wa += f"- {item['cant']} x {item['desc']} (Cod: {item['cod']})"
            if item['color']: mensaje_wa += f" | Color: {item['color']}"
            mensaje_wa += "\n"
            
            try:
                total_aprox += float(str(item['precio']).replace(',', '.')) * item['cant']
            except: pass
        
        st.sidebar.divider()
        st.sidebar.write(f"### Total Estimado: ${total_aprox:,.2f}")
        st.sidebar.caption("Los precios finales serán confirmados por el vendedor (+IVA)")

        # Botón de WhatsApp con el color verde oficial de la red
        link_wa = f"https://wa.me/5493513698953?text={urllib.parse.quote(mensaje_wa + f'\\nTotal aprox: ${total_aprox:,.2f}')}"
        st.sidebar.markdown(f"""
            <a href="{link_wa}" target="_blank">
                <button style="width:100%; background-color:#25D366; color:white
