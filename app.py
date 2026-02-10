import streamlit as st
import pandas as pd
import urllib.parse

# 1. CONFIGURACIÓN MÓVIL Y ESCRITORIO
st.set_page_config(page_title="Botonera Cordobesa SA", page_icon="🧵", layout="wide")

COLOR_BORDEAUX = "#8d1b1b"

st.markdown(f"""
    <style>
    .stButton>button {{ background-color: {COLOR_BORDEAUX}; color: white; border-radius: 8px; font-weight: bold; border: none; width: 100%; }}
    .producto-card {{ background-color: #ffffff; padding: 12px; border-radius: 10px; border-left: 5px solid {COLOR_BORDEAUX}; box-shadow: 2px 2px 8px rgba(0,0,0,0.1); margin-bottom: 8px; }}
    /* Ajuste para que en celular no se vea todo apretado */
    @media (max-width: 600px) {{
        .stMarkdown {{ font-size: 14px; }}
    }}
    </style>
    """, unsafe_allow_html=True)

# 2. CABECERA
col1, col2 = st.columns([1, 4])
with col1:
    st.image("https://static.wixstatic.com/media/893674_2f7f985a113d42f582a85710a309f488~mv2.png", width=120)
with col2:
    st.markdown(f"<h2 style='color:{COLOR_BORDEAUX}; margin:0;'>Botonera Cordobesa SA</h2>", unsafe_allow_html=True)
    st.write("Catálogo Mayorista")

st.divider()

# 3. CARGA DE DATOS
FILE_ID = "1LTJJ-iXYdcl1gRhcbXaC0jw64J9Khzwo"
SHEET_URL = f"https://docs.google.com/uc?export=download&id={FILE_ID}"

@st.cache_data(ttl=300) # Bajamos el caché a 5 min para que refresque rápido en celular
def load_data():
    try:
        df = pd.read_csv(SHEET_URL, encoding='latin1', on_bad_lines='skip', sep=None, engine='python')
        df = df.iloc[:, [0, 1, 2]]
        df.columns = ['Código', 'Descripción', 'Precio']
        # Limpiamos espacios en blanco que a veces molestan en móviles
        df['Descripción'] = df['Descripción'].fillna('').astype(str)
        df['Código'] = df['Código'].fillna('').astype(str)
        return df
    except:
        return pd.DataFrame(columns=['Código', 'Descripción', 'Precio'])

df = load_data()

if 'carrito' not in st.session_state: 
    st.session_state.carrito = []

# 4. BUSCADOR MEJORADO PARA MÓVIL
busqueda = st.text_input("🔍 Buscar producto o código", value="", placeholder="Ej: Cierre, Boton...").strip().lower()

# Filtrado
if busqueda:
    df_filtrado = df[df['Descripción'].str.lower().str.contains(busqueda) | 
                     df['Código'].str.lower().str.contains(busqueda)]
else:
    # Si no hay búsqueda, mostramos los primeros 30 por defecto (esto arregla el error del celular)
    df_filtrado = df.head(30)

if not df_filtrado.empty:
    st.write(f"Mostrando {len(df_filtrado)} artículos")
    
    for i, row in df_filtrado.iterrows():
        st.markdown(f"""
        <div class="producto-card">
            <b>{row['Descripción']}</b><br>
            <small>Cod: {row['Código']}</small> | <b style="color:{COLOR_BORDEAUX};">${row['Precio']}</b>
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1: color = st.text_input("Color", key=f"col_{i}", placeholder="Color")
        with c2: cant = st.number_input("Cant", min_value=1, value=1, key=f"can_{i}")
        with c3:
            st.write(" ")
            if st.button("➕", key=f"btn_{i}"):
                st.session_state.carrito.append({"desc": row['Descripción'], "cant": cant, "color": color, "precio": row['Precio'], "cod": row['Código']})
                st.toast("¡Agregado!")
        st.divider()
else:
    st.warning("No se encontraron artículos con esa búsqueda.")

# 5. CARRITO EN BARRA LATERAL (En celular aparece arriba como una flechita)
if st.session_state.carrito:
    st.sidebar.header("🛒 Tu Pedido")
    mensaje_wa = "Hola Botonera Cordobesa, este es mi pedido:\n\n"
    total = 0
    for item in st.session_state.carrito:
        st.sidebar.write(f"• {item['cant']}x {item['desc']}")
        mensaje_wa += f"- {item['cant']}x {item['desc']} (Cod: {item['cod']}) | Col: {item['color']}\n"
        try: total += float(str(item['precio']).replace(',', '.')) * item['cant']
        except: pass
    
    st.sidebar.write(f"### Total aprox: ${total:,.2f}")
    link_wa = f"https://wa.me/5493513698953?text={urllib.parse.quote(mensaje_wa)}"
    st.sidebar.markdown(f'<a href="{link_wa}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; border-radius:8px; font-weight:bold; cursor:pointer;">📲 ENVIAR POR WHATSAPP</button></a>', unsafe_allow_html=True)
    if st.sidebar.button("Vaciar"):
        st.session_state.carrito = []
        st.rerun()

