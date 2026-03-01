import streamlit as st
import os
import math
import base64

# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================
st.set_page_config(page_title="Vortex Bet", layout="centered")

# =========================================================
# CSS – LAYOUT & TIPOGRAFIA
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@200;300;400&display=swap');

:root {
    --space-sm: 18px;
    --space-md: 32px;
    --space-lg: 44px; /* +10% */
}

.stApp {
    background-color: #000000;
    color: #FFFFFF;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.header-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    margin-top: calc(var(--space-md) * 1.1); /* +10% da distância da logo */
}

.header-title {
    font-size: 30px;
    font-weight: 200; /* mais fina e estreita */
    margin: 0;
}

.header-subtitle {
    font-size: 16px;
    font-weight: 300;
    color: #9A9A9A;
    margin-top: 6px;
}

.section-spacing {
    margin-top: calc(var(--space-lg) * 1.1); /* +10% entre subtítulo e cálculo */
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# LOGO (INALTERADA)
# =========================================================
def mostrar_logo_centralizada(caminho, largura=140):
    with open(caminho, "rb") as f:
        dados = base64.b64encode(f.read()).decode()
    st.markdown(
        f"<div style='display:flex;justify-content:center;'>"
        f"<img src='data:image/png;base64,{dados}' width='{largura}'>"
        f"</div>",
        unsafe_allow_html=True
    )

if os.path.exists("logo_vortex.png"):
    mostrar_logo_centralizada("logo_vortex.png")

# =========================================================
# TÍTULO + SUBTÍTULO (NOVO DESIGN)
# =========================================================
st.markdown("""
<div class="header-wrapper">
    <div class="header-title">Vortex Bet</div>
    <div class="header-subtitle">Vortex Bet Hunter</div>
</div>
""", unsafe_allow_html=True)

# =========================================================
# CÁLCULO DO OBJETIVO
# =========================================================
st.markdown('<div class="section-spacing"></div>', unsafe_allow_html=True)
st.markdown("### 🎯 Cálculo do Objetivo")

modo = st.selectbox(
    "Qual variável deseja calcular?",
    ["Bilhetes", "Valor da UR", "Odd", "Objetivo Final"]
)

valor_ur = odd = objetivo = bilhetes = None

if modo != "Valor da UR":
    valor_ur = st.number_input("Valor da UR (R$)", min_value=1, value=100)

if modo != "Odd":
    odd = st.number_input("Odd", min_value=1.01, step=0.01, value=1.33)

if modo != "Objetivo Final":
    objetivo = st.number_input("Objetivo (R$)", min_value=1, value=1000)

if modo != "Bilhetes":
    bilhetes = st.number_input("Quantidade de Bilhetes", min_value=1, value=10)

if st.button("Calcular"):
    if modo == "Bilhetes":
        n = math.log(objetivo / valor_ur) / math.log(odd)
        st.success(f"Bilhetes necessários: **{math.ceil(n)}**")

    elif modo == "Valor da UR":
        ur = objetivo / (odd ** bilhetes)
        st.success(f"Valor da UR necessário: **R$ {ur:.2f}**")

    elif modo == "Odd":
        o = (objetivo / valor_ur) ** (1 / bilhetes)
        st.success(f"Odd necessária: **{o:.4f}**")

    elif modo == "Objetivo Final":
        obj = valor_ur * (odd ** bilhetes)
        st.success(f"Objetivo atingido: **R$ {obj:.2f}**")
