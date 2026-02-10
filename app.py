import streamlit as st
import pandas as pd
import urllib.parse

# 1. CONFIGURACIÓN DE PÁGINA E ICONO PARA INSTALACIÓN
st.set_page_config(
    page_title="Botonera Cordobesa SA", 
    page_icon="🧵", 
    layout="wide"
)

COLOR_ROJO = "#8d1b1b"

# --- SISTEMA DE ACCESO ---
def login():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        # Estilo para la pantalla de login
        st.markdown(f"""
            <style>
            .login-box {{
                background-color: #ffffff;
                padding: 30px;
                border-radius: 15px;
                border-top: 5px
