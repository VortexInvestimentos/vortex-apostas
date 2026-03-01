import streamlit as st
import os
import math
import base64

# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================
st.set_page_config(page_title="Vortex Bet", layout="centered")

# =========================================================
# CSS
# =========================================================
st.markdown("""
<style>
.stApp {
    background-color: #000000;
    color: #FFFFFF;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# LOGO
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

st.markdown("## Vortex Bet Hunter")

# =========================================================
# CÁLCULO DO OBJETIVO (renomeado, lógica intacta)
# =========================================================
st.markdown("### 🎯 Cálculo do Objetivo")

modo = st.selectbox(
    "Qual variável deseja calcular?",
    ["Bilhetes", "Valor da UR", "Odd", "Objetivo Final"]
)

valor_ur = odd = objetivo = bilhetes = None

if modo != "Valor da UR":
    valor_ur = st.number_input(
        "Valor da UR (R$)",
        min_value=1,
        value=100
    )

if modo != "Odd":
    odd = st.number_input(
        "Odd",
        min_value=1.01,
        step=0.01,
        value=1.33
    )

if modo != "Objetivo Final":
    objetivo = st.number_input(
        "Objetivo (R$)",
        min_value=1,
        value=1000
    )

if modo != "Bilhetes":
    bilhetes = st.number_input(
        "Quantidade de Bilhetes",
        min_value=1,
        value=10
    )

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
