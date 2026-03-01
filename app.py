import streamlit as st
import os
import math
import base64

# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================
st.set_page_config(page_title="Vortex Bet", layout="centered")

# =========================================================
# CSS – TIPOGRAFIA E ESPAÇAMENTOS
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@200;300;400&display=swap');

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
    margin-top: 40px;
}

.header-title {
    font-size: 30px;
    font-weight: 200;
    margin: 0;
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
    font-weight: 300;
    margin-bottom: 12px;
}

.soft-validation {
    margin-top: 6px;
    font-size: 13px;
    color: #9A9A9A;
}

.patamar-box {
    margin-top: 14px;
    padding: 12px;
    border: 1px solid #222222;
    border-radius: 8px;
    background-color: #0E0E0E;
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
# PATAMAR – APENAS QUANDO FAZ SENTIDO
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

    # ---------- resultado bruto ----------
    if modo == "Bilhetes":
        n = math.log(objetivo / valor_ur) / math.log(odd)
        bil = math.ceil(n)
        resultado_bruto = valor_ur * (odd ** bil)
        st.success(f"Bilhetes necessários: **{bil}**")

    elif modo == "Valor da UR":
        resultado_bruto = objetivo
        ur = objetivo / (odd ** bilhetes)
        st.success(f"Valor da UR necessário: **R$ {ur:.2f}**")

    elif modo == "Odd":
        resultado_bruto = objetivo
        o = (objetivo / valor_ur) ** (1 / bilhetes)
        st.success(f"Odd necessária: **{o:.4f}**")

    elif modo == "Objetivo Final":
        resultado_bruto = valor_ur * (odd ** bilhetes)
        st.success(f"Resultado bruto: **R$ {resultado_bruto:.2f}**")

    # ---------- patamares ----------
    if ativar_patamar:
        for pat in range(pat_min, pat_max + 1):
            valor_patamar = valor_ur * pat
            urs = int(resultado_bruto // valor_patamar)
            protegido = urs * valor_ur
            em_risco = resultado_bruto - protegido
            pct = (protegido / resultado_bruto) * 100 if resultado_bruto > 0 else 0

            if pat == pat_min:
                comentario = "Proteção mais frequente, com menor capital exposto."
            elif pat == pat_max:
                comentario = "Proteção mais espaçada, priorizando crescimento."
            else:
                comentario = "Equilíbrio intermediário entre proteção e crescimento."

            st.markdown(
                f"<div class='patamar-box'>"
                f"<strong>Patamar {pat}× UR</strong><br>"
                f"URs filhotes: <strong>{urs}</strong><br>"
                f"Capital protegido: <strong>R$ {protegido:.2f}</strong><br>"
                f"Resultado em risco: <strong>R$ {em_risco:.2f}</strong><br>"
                f"% protegido: <strong>{pct:.1f}%</strong><br>"
                f"<span class='soft-validation'>{comentario}</span>"
                f"</div>",
                unsafe_allow_html=True
            )
