import streamlit as st
import pandas as pd
import urllib.parse

# 1. CONFIGURACIÓN Y ESTILO CORPORATIVO
st.set_page_config(page_title="Botonera Cordobesa SA", page_icon="🧵", layout="wide")

COLOR_MARCA = "#8d1b1b" # Bordeaux oficial

st.markdown(f"""
    <style>
    .stButton>button {{
        background-color: {COLOR_MARCA};
        color: white;
        border-radius: 5px;
        font-weight: bold;
        border: none;
        height: 3em;
    }}
    .producto-card {{
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid {COLOR_MARCA};
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }}
    </style>
    """, unsafe_allow_html=True)

# 2. CABECERA CON TU LOGO
col1, col2 = st.columns([1, 4])
with col1:
    # URL del logo de tu sitio web
    st.image("https://static.wixstatic.com/media/893674_2f7f985a113d42f582a85710a309f488~mv2.png", width=140)
with col2:
    st.title("Botonera Cordobesa SA")
    st.subheader("Pedidos Mayoristas Online")

st.divider()

# 3. CARGA DE DATOS DESDE DRIVE
FILE_ID = "1LTJJ-iXYdcl1gRhcbXaC0jw64J9Khzwo"
SHEET_URL = f"https://docs.google.com/uc?export=download&id={FILE_ID}"

@st.cache_data(ttl=600)
def load_data():
    # Cargamos el archivo con las correcciones de errores que ya probamos
    df = pd.read_csv(SHEET_URL, encoding='latin1', on_bad_lines='skip', sep=None, engine='python')
    df = df.iloc[:, [0, 1, 2]]
    df.columns = ['Código', 'Descripción', 'Precio']
    return df

try:
    df = load_data()
    if 'carrito' not in st.session_state: st.session_state.carrito = []

    # Buscador
    busqueda = st.text_input("🔍 ¿Qué estás buscando? (Nombre o código)", "").lower()
    
    df_filtrado = df.dropna(subset=['Descripción'])
    df_filtrado = df_filtrado[
        df_filtrado['Descripción'].astype(str).str.lower().str.contains(busqueda) | 
        df_filtrado['Código'].astype(str).str.lower().str.contains(busqueda)
    ]

    # 4. LISTADO DE PRODUCTOS
    for i, row in df_filtrado.head(60).iterrows():
        st.markdown(f"""
        <div class="producto-card">
            <span style="color:{COLOR_MARCA}; font-weight:bold;">{row['Descripción']}</span><br>
            <small>Cod: {row['Código']}</small> | <b>${row['Precio']}</b> <small>+ IVA</small>
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            color = st.text_input("Color", placeholder="Ej: Blanco", key=f"col_{i}")
        with c2:
            cant = st.number_input("Cant.", min_value=1, value=1, key=f"can_{i}")
        with c3:
            st.write(" ")
            if st.button("AÑADIR", key=f"btn_{i}"):
                st.session_state.carrito.append({
                    "desc": row['Descripción'], "cod": row['Código'],
                    "cant": cant, "color": color, "precio": row['Precio']
                })
                st.toast("¡Añadido!")
        st.write("---")

    # 5. CARRITO Y WHATSAPP (Barra Lateral)
    if st.session_state.carrito:
        st.sidebar.header("🛒 Tu Pedido")
        mensaje_wa = "Hola Botonera Cordobesa, envío mi pedido:\n\n"
        total = 0
        for item in st.session_state.carrito:
            st.sidebar.write(f"• {item['cant']}x {item['desc']}")
            mensaje_wa += f"- {item['cant']} x {item['desc']} (Cod: {item['cod']}) | Col: {item['color']}\n"
            try: total += float(str(item['precio']).replace(',', '.')) * item['cant']
            except: pass
        
        st.sidebar.divider()
        st.sidebar.write(f"### Total aprox: ${total:,.2f}")
        
        link_wa = f"https://wa.me/5493513698953?text={urllib.parse.quote(mensaje_wa + f'\\nTotal: ${total:,.2f}')}"
        
        st.sidebar.markdown(f"""
            <a href="{link_wa}" target="_blank">
                <button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; border-radius:8px; font-weight:bold; cursor:pointer;">
                    ✅ ENVIAR PEDIDO POR WHATSAPP
                </button>
            </a>
            """, unsafe_allow_html=True)
        
        if st.sidebar.button("🗑️ Vaciar Carrito"):
            st.session_state.carrito = []
            st.rerun()

except Exception as e:
    st.error("Error al conectar con la base de datos.")
