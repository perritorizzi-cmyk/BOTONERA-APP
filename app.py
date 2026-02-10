import streamlit as st
import pandas as pd
import urllib.parse

# 1. CONFIGURACIÓN Y ESTILO
st.set_page_config(page_title="Botonera Cordobesa - Pedidos", page_icon="🧵", layout="wide")

st.markdown("""
    <style>
    .stButton>button { width: 100%; background-color: #008CBA; color: white; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🧵 Botonera Cordobesa SA")
st.subheader("Lista de Precios y Pedidos Mayoristas")

# 2. CONEXIÓN A TU ARCHIVO (Enlace de descarga directa corregido)
FILE_ID = "1LTJJ-iXYdcl1gRhcbXaC0jw64J9Khzwo"
SHEET_URL = f"https://docs.google.com/uc?export=download&id={FILE_ID}"

@st.cache_data(ttl=600)
def load_data():
    # Cargamos el CSV desde tu Google Drive
    df = pd.read_csv(SHEET_URL)
    # Asignamos nombres a tus columnas A, B y C
    df.columns = ['Código', 'Descripción', 'Precio'] + list(df.columns[3:])
    return df

try:
    df = load_data()

    if 'carrito' not in st.session_state:
        st.session_state.carrito = []

    # 3. BUSCADOR
    busqueda = st.text_input("🔍 ¿Qué estás buscando? (Ej: Cierre, Botón, Hilo...)", "").lower()
    
    # Filtrado por descripción o código
    df_filtrado = df[df['Descripción'].astype(str).str.lower().str.contains(busqueda) | 
                     df['Código'].astype(str).str.lower().str.contains(busqueda)]

    # 4. LISTADO DE PRODUCTOS (Limitamos a 50 para rapidez)
    st.write(f"Mostrando {len(df_filtrado)} productos")
    
    for i, row in df_filtrado.head(50).iterrows():
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.markdown(f"**{row['Descripción']}**")
                st.caption(f"Código: {row['Código']}")
            with col2:
                st.markdown(f"**${row['Precio']}**")
                st.caption("+ IVA")
            with col3:
                color = st.text_input("Color", placeholder="Ej: Rojo", key=f"color_{i}")
                cant = st.number_input("Cant.", min_value=1, value=1, key=f"cant_{i}")
                if st.button("🛒 Agregar", key=f"btn_{i}"):
                    st.session_state.carrito.append({
                        "desc": row['Descripción'],
                        "cod": row['Código'],
                        "cant": cant,
                        "color": color,
                        "precio": row['Precio']
                    })
                    st.toast(f"Agregado: {row['Descripción']}")
            st.divider()

    # 5. CARRITO Y ENVÍO POR WHATSAPP
    if st.session_state.carrito:
        st.sidebar.header("🛒 Mi Pedido")
        resumen_wa = "Hola Botonera Cordobesa, este es mi pedido:\n\n"
        total_aprox = 0
        
        for item in st.session_state.carrito:
            st.sidebar.write(f"**{item['cant']}x** {item['desc']}")
            resumen_wa += f"- {item['cant']} x {item['desc']} (Cod: {item['cod']}) | Color: {item['color']}\n"
            total_aprox += float(item['precio']) * item['cant']
        
        st.sidebar.divider()
        st.sidebar.write(f"### Total aprox: ${total_aprox:,.2f}")

        numero_tel = "5493513698953"
        texto_final = urllib.parse.quote(resumen_wa + f"\nTotal aprox: ${total_aprox:,.2f}")
        link_wa = f"https://wa.me/{numero_tel}?text={texto_final}"
        
        st.sidebar.markdown(f'[**✅ ENVIAR PEDIDO POR WHATSAPP**]({link_wa})', unsafe_allow_html=True)
        
        if st.sidebar.button("🗑️ Vaciar carrito"):
            st.session_state.carrito = []
            st.rerun()

except Exception as e:
    st.error(f"Error al cargar los datos: {e}")
    st.info("Asegúrate de que el archivo en Drive tenga los permisos de acceso correctos.")
