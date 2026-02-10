import streamlit as st
import pandas as pd
import urllib.parse

# 1. CONFIGURACIÓN BÁSICA
st.set_page_config(page_title="Botonera Cordobesa", layout="wide")

# --- SISTEMA DE LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.title("🔐 Acceso Clientes")
    usuario = st.text_input("Usuario")
    clave = st.text_input("Contraseña", type="password")
    if st.button("INGRESAR"):
        if usuario.lower() == "botonera" and clave == "2026":
            st.session_state["autenticado"] = True
            st.rerun()
        else:
            st.error("Usuario o clave incorrectos")
    st.stop()

# --- INICIALIZACIÓN DE VARIABLES ---
if "carrito" not in st.session_state:
    st.session_state.carrito = []
if "ver_pedido" not in st.session_state:
    st.session_state.ver_pedido = False

# 2. ENCABEZADO
st.header("Botonera Cordobesa SA")
st.subheader("Catálogo de Pedidos Mayoristas")

# 3. CARGA DE DATOS (Link directo a tu Google Sheets)
@st.cache_data(ttl=300)
def cargar_datos():
    url = "https://docs.google.com/uc?export=download&id=1LTJJ-iXYdcl1gRhcbXaC0jw64J9Khzwo"
    try:
        df = pd.read_csv(url, encoding='latin1', on_bad_lines='skip', sep=None, engine='python')
        df = df.iloc[:, [0, 1, 2]]
        df.columns = ['Codigo', 'Descripcion', 'Precio']
        return df
    except:
        return pd.DataFrame(columns=['Codigo', 'Descripcion', 'Precio'])

df = cargar_datos()

# 4. LÓGICA DE NAVEGACIÓN
# Botón para cambiar entre el Catálogo y el Carrito
if st.session_state.carrito:
    total_items = sum(int(item['cant']) for item in st.session_state.carrito)
    if st.button(f"🛒 REVISAR MI PEDIDO ({total_items} artículos)", use_container_width=True, type="primary"):
        st.session_state.ver_pedido = not st.session_state.ver_pedido
        st.rerun()

st.divider()

# VISTA DEL CARRITO
if st.session_state.ver_pedido:
    st.title("Tu Lista de Pedido")
    if not st.session_state.carrito:
        st.write("No has agregado nada aún.")
    else:
        for i, item in enumerate(st.session_state.carrito):
            col_a, col_b = st.columns([4, 1])
            col_a.write(f"**{item['cant']}x** {item['desc']} (Color: {item['color']})")
            if col_b.button("Eliminar", key=f"del_{i}"):
                st.session_state.carrito.pop(i)
                st.rerun()
        
        # Botón para enviar a WhatsApp
        mensaje = "Hola Botonera Cordobesa, envío mi pedido:\n\n"
        for itm in st.session_state.carrito:
            mensaje += f"- {itm['cant']}x {itm['desc']} (Cod: {itm['cod']}) | Color: {itm['color']}\n"
        
        wa_url = f"https://wa.me/5493513698953?text={urllib.parse.quote(mensaje)}"
        st.link_button("📲 ENVIAR PEDIDO POR WHATSAPP", wa_url, use_container_width=True)

    if st.button("⬅️ VOLVER AL CATÁLOGO"):
        st.session_state.ver_pedido = False
        st.rerun()

# VISTA DEL CATÁLOGO
else:
    busqueda = st.text_input("🔍 BUSCAR PRODUCTO (Nombre o Código)", "").strip().lower()
    
    # Filtrar datos
    df_f = df[df['Descripcion'].str.lower().str.contains(busqueda) | df['Codigo'].str.lower().str.contains(busqueda)] if busqueda else df.head(15)

    for i, row in df_f.iterrows():
        with st.container():
            st.write(f"### {row['Descripcion']}")
            st.write(f"**Código:** {row['Codigo']} | **Precio:** ${row['Precio']}")
            
            c1, c2, c3 = st.columns([2, 1, 1])
            color = c1.text_input("Color/Nro", key=f"col_{i}", placeholder="Color")
            cantidad = c2.number_input("Cant", min_value=1, value=1, key=f"can_{i}")
            if c3.button("➕", key=f"btn_{i}"):
                st.session_state.carrito.append({
                    "desc": row['Descripcion'], 
                    "cant": cantidad, 
                    "color": color, 
                    "cod": row['Codigo']
                })
                st.toast(f"Agregado: {row['Descripcion']}")
            st.divider()
