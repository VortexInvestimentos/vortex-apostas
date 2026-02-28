import streamlit as st
import pandas as pd
import os
import math
import base64
from itertools import product

# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================
st.set_page_config(page_title="Vortex Bet", layout="centered")

# =========================================================
# CSS GLOBAL
# =========================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500&display=swap');

    .stApp {
        background-color: #000000;
        color: #FFFFFF;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    h1, h2, h3, h4, h5, h6, p, span, label, div {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        color: #FFFFFF;
    }

    .header-wrapper {
        text-align: center;
    }

    .header-title {
        font-size: 28px;
        font-weight: 300;
        margin: 0;
    }

    .header-subtitle {
        font-size: 22px;
        font-weight: 300;
        margin-top: 6px;
        color: #B0B0B0;
    }

    .divider {
        width: 60%;
        height: 1px;
        background-color: #222;
        margin: 32px auto;
    }

    .section-title {
        font-size: 22px;
        font-weight: 300;
        margin-bottom: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# LOGO CENTRALIZADA (BASE64)
# =========================================================
def mostrar_logo(caminho, largura=140):
    with open(caminho, "rb") as f:
        img = base64.b64encode(f.read()).decode()
    st.markdown(
        f"<div style='display:flex; justify-content:center;'>"
        f"<img src='data:image/png;base64,{img}' width='{largura}'></div>",
        unsafe_allow_html=True
    )

if os.path.exists("logo_vortex.png"):
    mostrar_logo("logo_vortex.png", 140)

st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="header-wrapper">
        <h1 class="header-title">Vortex Bet</h1>
        <div class="header-subtitle">Vortex Bet Hunter</div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# =========================================================
# ========= FUNÇÕES MATEMÁTICAS =========
# =========================================================
def patrimonio_final(valor_ur, odd, bilhetes, patamar=None):
    saldo = valor_ur
    urs = 0

    for _ in range(bilhetes):
        saldo *= odd
        if patamar and saldo >= valor_ur * patamar:
            saldo -= valor_ur
            urs += 1

    return saldo + urs * valor_ur

# =========================================================
# ========= OBJETIVO FINAL =========
# =========================================================
st.markdown("<div class='section-title'>🎯 Cálculo de Objetivo Final</div>", unsafe_allow_html=True)

modo = st.selectbox(
    "O que você quer calcular?",
    [
        "Bilhetes necessários",
        "Odd necessária",
        "Valor da UR necessário",
        "Objetivo final alcançado"
    ]
)

valor_ur = st.number_input("Valor da UR (R$)", min_value=1, value=100)
odd = st.number_input("Odd fixa", min_value=1.01, value=1.33, step=0.01)
bilhetes = st.number_input("Quantidade de bilhetes", min_value=1, value=30)
objetivo = st.number_input("Objetivo final (R$)", min_value=1, value=1000)

if st.button("Calcular"):
    if modo == "Bilhetes necessários":
        n = math.log(objetivo / valor_ur) / math.log(odd)
        st.success(f"Bilhetes necessários: **{math.ceil(n)}**")

    elif modo == "Odd necessária":
        odd_req = (objetivo / valor_ur) ** (1 / bilhetes)
        st.success(f"Odd necessária: **{round(odd_req, 3)}**")

    elif modo == "Valor da UR necessário":
        ur_req = objetivo / (odd ** bilhetes)
        st.success(f"Valor da UR necessário: **R$ {round(ur_req, 2)}**")

    elif modo == "Objetivo final alcançado":
        final = valor_ur * (odd ** bilhetes)
        st.success(f"Objetivo alcançado: **R$ {round(final, 2)}**")

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# =========================================================
# ========= BACKTEST PARAMÉTRICO =========
# =========================================================
st.markdown("<div class='section-title'>🔍 Backtest Paramétrico (Top 10)</div>", unsafe_allow_html=True)

ur_min, ur_max = st.slider("Faixa Valor da UR", 10, 1000, (100, 300), step=10)
b_min, b_max = st.slider("Faixa de Bilhetes", 5, 500, (20, 100))
odd_min, odd_max = st.slider("Faixa de Odds", 1.01, 2.00, (1.30, 1.40), step=0.01)
pat_min, pat_max = st.slider("Faixa de Patamar (× UR)", 2, 5, (2, 4))

ativar_patamar = st.toggle("Ativar retirada de UR", value=True)

if st.button("Rodar Backtest"):
    resultados = []

    for ur, b, o, p in product(
        range(ur_min, ur_max + 1, 10),
        range(b_min, b_max + 1),
        [round(x, 2) for x in frange(odd_min, odd_max, 0.01)],
        range(pat_min, pat_max + 1)
    ):
        final = patrimonio_final(
            ur, o, b, p if ativar_patamar else None
        )

        resultados.append({
            "Patrimônio Final": round(final, 2),
            "Valor UR": ur,
            "Bilhetes": b,
            "Odd": o,
            "Patamar": p if ativar_patamar else "—"
        })

    df = pd.DataFrame(resultados)
    df = df.sort_values(by="Patrimônio Final", ascending=False).head(10)
    df.insert(0, "Posição", range(1, len(df) + 1))

    st.dataframe(df, use_container_width=True)
