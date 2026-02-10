import streamlit as st
import pandas as pd
import urllib.parse

# 1. CONFIGURACIÓN TÉCNICA PARA "MODO APP"
st.set_page_config(
    page_title="Botonera Cordobesa SA", 
    page_icon="🧵", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inyectar Meta Tags para que al "Instalar" se vea como App nativa
st.markdown("""
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
""", unsafe_allow_html=True)

COLOR_ROJO = "#8d1b1b"

# --- SISTEMA DE ACCESO (USUARIO: Botonera / CLAVE: 2026) ---
def login():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        st.markdown(f"""
            <style>
            .login-container {{
                background-color: #ffffff;
                padding: 40px 20px;
                border-radius: 20px;
                border-top: 6px solid {COLOR_ROJO};
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                text-align: center;
                margin-top: 50px;
            }}
            .stTextInput>div>div>input {{ text-align: center !important; font-size: 1.2em !important; }}
            </style>
        """, unsafe_allow_html=True)
        
        _, col, _ = st.columns([1, 3, 1])
        with col:
            st.markdown('<div class="login-container">', unsafe_allow_html=True)
            st.markdown(f"<h2 style='color:{COLOR_ROJO}; margin-bottom:0;'>BIENVENIDO</h2>", unsafe_allow_html=True)
            st.markdown("<p style='color:gray;'>Acceso Exclusivo Mayorista</p>", unsafe_allow_html=True)
            
            user = st.text_input("Usuario", placeholder="Ej: Botonera")
            clave = st.text_input("Contraseña", type="password", placeholder="****")
            
            if st.button("INGRESAR AL SISTEMA", use_container_width=True):
                if user.lower() == "botonera" and clave == "2026":
                    st.session_state["autenticado"] = True
                    st.rerun()
                else:
                    st.error("Credenciales inválidas")
            st.markdown('</div>', unsafe_allow_html=True)
        return False
    return True

if login():
    # 2. ESTILOS VISUALES DEL CATÁLOGO
    st.markdown(f"""
        <style>
        /* Encabezado */
        .header-box {{ display: flex; align-items: center; justify-content: center; gap: 10px; padding: 10px; }}
        .txt-logo {{ color: {COLOR_ROJO} !important; font-family: 'serif'; font-size: 1.4em; font-weight: bold; margin: 0; }}
        
        /* Buscador Robusto */
        div[data-baseweb="input"] {{ border: 3px solid {COLOR_ROJO} !important; border-radius: 12px !important; background: white !important; }}
        input {{ color: #000 !important; -webkit-text-fill-color: #000 !important; font-weight: bold !important; }}
        
        /* Tarjetas */
        .card {{ background: white; padding: 15px; border-radius: 12px; border-left: 6px solid {COLOR_ROJO}; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 10px; }}
        .card-tit {{ color: #111; font-weight: bold; margin:0; font-size: 1em; line-height: 1.2; }}
        .card-pre {{ color: {COLOR_ROJO}; font-weight: bold; margin:0; font-size: 1.2em; }}
        
        /* Barra Flotante */
        .sticky-bar {{ 
            position: fixed; bottom: 0; left: 0; width: 100%; 
            background: #fff; border-top: 2px solid {COLOR_ROJO}; 
            padding: 10px; z-index: 999; display: flex; 
            justify-content: space-around; align-items: center; 
            box-shadow: 0 -4px 10px rgba(0,0,0,0.1);
        }}
        </style>
    """, unsafe_allow_html=True)

    # 3. CABECERA E INSTITUCIONAL
    st.markdown(f'<div class="header-box"><p class="txt-logo">Botonera Cordobesa SA</p><div style="border-left:2px solid #ddd;height:25px;"></div><p class="txt-logo">Sarquis & Sepag</p></div>', unsafe_allow_html=True)
    
    col_top1, col_top2 = st.columns([5, 1])
    with col_top2:
        if st.button("Cerrar Sesión"):
            st.session_state["autenticado"] = False
            st.rerun()

    # 4. CARGA DE DATOS
    FILE_ID = "1LTJJ-iXYdcl1gRhcbXaC0jw64J9Khzwo"
    SHEET_URL = f"https://docs.google.com/uc?export=download&id={FILE_ID}"

    @st.cache_data(ttl=300)
    def load_data():
        try:
            df = pd.read_csv(SHEET_URL, encoding='latin1', on_bad_lines='skip', sep=None, engine='python')
            df = df.iloc[:, [0, 1, 2]]
            df.columns = ['Código', 'Descripción', 'Precio']
            return df
        except: return pd.DataFrame(columns=['Código', 'Descripción', 'Precio'])

    df = load_data()
    if 'carrito' not in st.session_state: st.session_state.carrito = []

    # 5. BUSCADOR
    st.write("")
    busqueda = st.text_input("BUSCADOR", placeholder="🔍 Escribe nombre o código del producto...", label_visibility="collapsed").strip().lower()

    # 6. RESULTADOS
    df_filtrado = df[df['Descripción'].str.lower().str.contains(busqueda) | df['Código'].str.lower().str.contains(busqueda)] if busqueda else df.head(20)

    for i, row in df_filtrado.iterrows():
        st.markdown(f"""
            <div class="card">
                <p class="card-tit">{row['Descripción']}</p>
                <p style="color:gray; font-size:0.8em; margin:0;">Código: {row['Código']}</p>
                <p class="card-pre">${row['Precio']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1: color = st.text_input("Color", key=f"col_{i}", placeholder="Color/Nro")
        with c2: cant = st.number_input("Cant", min_value=1, value=1, key=f"can_{i}")
        with c3:
            st.write("")
            if st.button("➕", key=f"btn_{i}"):
                st.session_state.carrito.append({"desc": row['Descripción'], "cant": cant, "color": color, "precio": row['Precio'], "cod": row['Código']})
                st.toast(f"✅ Agregado!")

    st.write("<br><br><br><br><br>", unsafe_allow_html=True)

    # 7. CARRITO FLOTANTE
    if st.session_state.carrito:
        n_items = sum(item['cant'] for item in st.session_state.carrito)
        st.markdown(f'<div class="sticky-bar"><span style="color:#111; font-weight:bold;">🛒 {n_items} artículos</span></div>', unsafe_allow_html=True)
        
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            if st.button("📝 REVISAR PEDIDO", use_container_width=True):
                st.session_state.ver_pedido = not st.session_state.get('ver_pedido', False)
        with f_col2:
            mensaje = "Hola Botonera Cordobesa, envío mi pedido:\n\n"
            for itm in st.session_state.carrito:
                mensaje += f"- {itm['cant']}x {itm['desc']} (Cod: {itm['cod']}) | Color: {itm['color']}\n"
            wa_url = f"https://wa.me/5493513698953?text={urllib.parse.quote(mensaje)}"
            st.markdown(f'<a href="{wa_url}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:10px; border-radius:8px; font-weight:bold; height:45px; cursor:pointer; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">📲 ENVIAR PEDIDO</button></a>', unsafe_allow_html=True)

        if st.session_state.get('ver_pedido', False):
            with st.expander("TU LISTA (Toca para cerrar)", expanded=True):
                for idx, itm in enumerate(st.session_state.carrito):
                    ca, cb = st.columns([4, 1])
                    ca.write(f"**{itm['cant']}** - {itm['desc']} (Col: {itm['color']})")
                    if cb.button("❌", key=f"del_{idx}"):
                        st.session_state.carrito.pop(idx)
                        st.rerun()
                if st.button("VACIAR TODO EL CARRITO"):
                    st.session_state.carrito = []
                    st.rerun()

