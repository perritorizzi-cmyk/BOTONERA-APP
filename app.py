import streamlit as st
import pandas as pd
import urllib.parse

# 1. CONFIGURACIÓN DE PÁGINA Y ESTILO PROFESIONAL
st.set_page_config(page_title="Botonera Cordobesa - Pedidos", page_icon="🧵", layout="wide")

st.markdown("""
    <style>
    .stButton>button { width: 100%; background-color: #008CBA; color: white; border-radius: 8px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🧵 Botonera Cordobesa SA")
st.subheader("Consulta de Precios y Pedidos")

# 2. CONEXIÓN A TU ARCHIVO DE GOOGLE DRIVE
FILE_ID = "1LTJJ-iXYdcl1gRhcbXaC0jw64J9Khzwo"
SHEET_URL = f"https://docs.google.com/uc?export=download&id={FILE_ID}"

@st.cache_data(ttl=600)
def load_data():
    # on_bad_lines='skip' ignora las filas que causaban el error ParserError
    df = pd.read_csv(SHEET_URL, encoding='latin1', on_bad_lines='skip', sep=None, engine='python')
    # Nos aseguramos de tomar las primeras 3 columnas (Código, Descripción, Precio)
    df = df.iloc[:, [0, 1, 2]]
    df.columns = ['Código', 'Descripción', 'Precio']
    return df

# 3. LÓGICA DE LA APLICACIÓN
try:
    df = load_data()

    if 'carrito' not in st.session_state:
        st.session_state.carrito = []

    # Buscador
    busqueda = st.text_input("🔍 ¿Qué producto buscas? (Escribe nombre o código)", "").lower()
    
    # Filtrar datos limpiando valores vacíos
    df_filtrado = df.dropna(subset=['Descripción'])
    df_filtrado = df_filtrado[
        df_filtrado['Descripción'].astype(str).str.lower().str.contains(busqueda) | 
        df_filtrado['Código'].astype(str).str.lower().str.contains(busqueda)
    ]

    st.write(f"Se encontraron {len(df_filtrado)} artículos")
    st.divider()

    # 4. LISTADO DE PRODUCTOS
    for i, row in df_filtrado.head(100).iterrows():
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.markdown(f"**{row['Descripción']}**")
                st.caption(f"Código: {row['Código']}")
            with col2:
                st.markdown(f"**${row['Precio']}**")
                st.caption("+ IVA")
            with col3:
                color = st.text_input("Color", placeholder="Ej: Blanco", key=f"color_{i}")
                cant = st.number_input("Cantidad", min_value=1, value=1, key=f"cant_{i}")
                if st.button("➕ Agregar", key=f"btn_{i}"):
                    st.session_state.carrito.append({
                        "desc": row['Descripción'],
                        "cod": row['Código'],
                        "cant": cant,
                        "color": color,
                        "precio": row['Precio']
                    })
                    st.toast(f"✅ Sumado: {row['Descripción']}")
            st.divider()

    # 5. PANEL DEL PEDIDO (BARRA LATERAL)
    if st.session_state.carrito:
        st.sidebar.header("🛒 Mi Pedido")
        mensaje_wa = "Hola Botonera Cordobesa, quiero hacer este pedido:\n\n"
        total_aprox = 0
        
        for item in st.session_state.carrito:
            st.sidebar.write(f"**{item['cant']}x** {item['desc']}")
            mensaje_wa += f"- {item['cant']} x {item['desc']} (Cod: {item['cod']})"
            if item['color']:
                mensaje_wa += f" | Color: {item['color']}"
            mensaje_wa += "\n"
            try:
                total_aprox += float(str(item['precio']).replace(',', '.')) * item['cant']
            except:
                pass
        
        st.sidebar.divider()
        st.sidebar.write(f"### Total aprox: ${total_aprox:,.2f}")

        numero_vendedor = "5493513698953"
        texto_final = urllib.parse.quote(mensaje_wa + f"\nTotal aprox: ${total_aprox:,.2f}")
        link_wa = f"https://wa.me/{numero_vendedor}?text={texto_final}"
        
        st.sidebar.markdown(f'<a href="{link_wa}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; border-radius:8px; font-weight:bold; cursor:pointer;">📲 ENVIAR POR WHATSAPP</button></a>', unsafe_allow_html=True)
        
        if st.sidebar.button("🗑️ Vaciar Carrito"):
            st.session_state.carrito = []
            st.rerun()

except Exception as e:
    st.error(f"Error al cargar la base de datos.")
    st.write("Asegúrate de que el archivo CSV esté ordenado por columnas.")
