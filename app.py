import streamlit as st
import os
import math
import base64

# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================
st.set_page_config(page_title="Vortex Bet", layout="centered")

# =========================================================
# CSS GLOBAL
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@200;300;400;600&display=swap');

.stApp {
    background-color: #000;
    color: #FFF;
    font-family: 'Inter', sans-serif;
}

.header-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 40px;
    text-align: center;
}

.header-title {
    font-size: 30px;
    font-weight: 200;
}

.header-subtitle {
    font-size: 15px;
    font-weight: 300;
    color: #9A9A9A;
    margin-top: 6px;
}

.section-spacing {
    margin-top: 48px;
}

.calc-title {
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 12px;
}

.soft-validation {
    font-size: 12px;
    color: #9A9A9A;
    margin-top: 4px;
}

.patamar-container {
    display: flex;
    gap: 14px;
    margin-top: 12px;
}

.patamar-box {
    flex: 1;
    padding: 12px;
    border: 1px solid #222;
    border-radius: 8px;
    background-color: #0E0E0E;
    font-size: 12px;
    color: #B0B0B0;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# LOGO
# =========================================================
def mostrar_logo(caminho, largura=140):
    with open(caminho, "rb") as f:
        img = base64.b64encode(f.read()).decode()
    st.markdown(
        f"<div style='display:flex;justify-content:center;'>"
        f"<img src='data:image/png;base64,{img}' width='{largura}'>"
        f"</div>",
        unsafe_allow_html=True
    )

if os.path.exists("logo_vortex.png"):
    mostrar_logo("logo_vortex.png")

# =========================================================
# TÍTULO
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
st.markdown("<div class='calc-title'>🎯 Cálculo do Objetivo</div>", unsafe_allow_html=True)

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

# =========================================================
# PATAMAR
# =========================================================
ativar_patamar = False
pat_min = pat_max = None

if modo != "Valor da UR":
    ativar_patamar = st.checkbox("Ativar geração de UR filhote (patamar)")

    if ativar_patamar:
        pat_min, pat_max = st.slider(
            "Intervalo de patamar (×UR)",
            min_value=2,
            max_value=5,
            value=(3, 3),
            step=1
        )

# =========================================================
# CÁLCULO
# =========================================================
if st.button("Calcular"):

    if modo == "Bilhetes":
        bil = math.ceil(math.log(objetivo / valor_ur) / math.log(odd))
        resultado = valor_ur * (odd ** bil)
        st.success(f"Bilhetes necessários: **{bil}**")
        comentario = "Número de repetições necessárias para atingir o objetivo."

    elif modo == "Valor da UR":
        ur = objetivo / (odd ** bilhetes)
        resultado = objetivo
        st.success(f"Valor da UR necessário: **R$ {ur:.2f}**")
        comentario = "Valor unitário necessário por tentativa."

    elif modo == "Odd":
        o = (objetivo / valor_ur) ** (1 / bilhetes)
        resultado = objetivo
        st.success(f"Odd necessária: **{o:.4f}**")
        comentario = "Dificuldade mínima do evento para alcançar o objetivo."

    else:
        resultado = valor_ur * (odd ** bilhetes)
        st.success(f"Resultado bruto: **R$ {resultado:.2f}**")
        comentario = "Resultado total antes de qualquer proteção."

    st.markdown(f"<div class='soft-validation'>{comentario}</div>", unsafe_allow_html=True)

    if ativar_patamar:
        st.markdown("<div class='patamar-container'>", unsafe_allow_html=True)

        for pat in range(pat_min, pat_max + 1):
            valor_pat = valor_ur * pat
            urs = int(resultado // valor_pat)
            protegido = urs * valor_ur
            risco = resultado - protegido
            pct = (protegido / resultado) * 100 if resultado else 0

            st.markdown(
                f"<div class='patamar-box'>"
                f"<strong>Patamar {pat}× UR</strong><br>"
                f"URs filhotes: <strong>{urs}</strong><br>"
                f"Capital protegido: <strong>R$ {protegido:.2f}</strong><br>"
                f"Resultado em risco: <strong>R$ {risco:.2f}</strong><br>"
                f"% protegido: <strong>{pct:.1f}%</strong>"
                f"</div>",
                unsafe_allow_html=True
            )

        st.markdown("</div>", unsafe_allow_html=True)
