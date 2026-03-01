import streamlit as st
import pandas as pd
import os
import math
import base64
from math import comb
from scipy.stats import binom

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
        f"<div style='display:flex;justify-content:center;'><img src='data:image/png;base64,{dados}' width='{largura}'></div>",
        unsafe_allow_html=True
    )

if os.path.exists("logo_vortex.png"):
    mostrar_logo_centralizada("logo_vortex.png")

st.markdown("## Vortex Bet Hunter")

# =========================================================
# OBJETIVO FINAL – FLEXÍVEL (INTACTO)
# =========================================================
st.markdown("### 🎯 Objetivo Final")

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
    objetivo = st.number_input("Objetivo Final (R$)", min_value=1, value=1000)

if modo != "Bilhetes":
    bilhetes = st.number_input("Quantidade de Bilhetes", min_value=1, value=10)

if st.button("Calcular"):
    if modo == "Bilhetes":
        n = math.log(objetivo / valor_ur) / math.log(odd)
        st.success(f"Bilhetes necessários: {math.ceil(n)}")

    elif modo == "Valor da UR":
        ur = objetivo / (odd ** bilhetes)
        st.success(f"Valor da UR necessário: R$ {ur:.2f}")

    elif modo == "Odd":
        o = (objetivo / valor_ur) ** (1 / bilhetes)
        st.success(f"Odd necessária: {o:.4f}")

    elif modo == "Objetivo Final":
        obj = valor_ur * (odd ** bilhetes)
        st.success(f"Objetivo final atingido: R$ {obj:.2f}")

# =====================================================================
# A PARTIR DAQUI: NOVOS MÓDULOS ESTATÍSTICOS (BACKTEST REMOVIDO)
# =====================================================================

st.markdown("---")
st.markdown("## 📊 Análise Estatística para Apostas All-In")

# =========================================================
# MÓDULO 1 — ESPERANÇA MATEMÁTICA (EV)
# =========================================================
st.markdown("### 1️⃣ Esperança Matemática (EV)")

odd_ev = st.number_input("Odd da aposta", min_value=1.01, value=1.60, key="ev1")
p_estimada = st.slider("Probabilidade estimada de acerto (%)", 1, 99, 60, key="ev2") / 100

ganho = odd_ev - 1
ev = p_estimada * ganho - (1 - p_estimada)

st.write(f"**EV:** {ev:.4f}")
st.write("EV > 0 → aposta teoricamente vantajosa")

# =========================================================
# MÓDULO 2 — EDGE NECESSÁRIO
# =========================================================
st.markdown("### 2️⃣ Edge Necessário")

odd_edge = st.number_input("Odd", min_value=1.01, value=1.60, key="edge1")
p_min = 1 / odd_edge

st.write(f"Probabilidade mínima necessária: **{p_min*100:.2f}%**")
st.write("Se sua taxa real for menor que isso, a aposta é negativa.")

# =========================================================
# MÓDULO 3 — VALIDAÇÃO ESTATÍSTICA (BINOMIAL)
# =========================================================
st.markdown("### 3️⃣ Validação Estatística de Resultados")

n_apostas = st.number_input("Número de apostas", min_value=1, value=100)
vitorias = st.number_input("Número de acertos", min_value=0, max_value=n_apostas, value=60)
odd_media = st.number_input("Odd média", min_value=1.01, value=1.60)

p_mercado = 1 / odd_media

# p-value (probabilidade de obter >= vitórias assumindo p_mercado)
p_value = 1 - binom.cdf(vitorias - 1, n_apostas, p_mercado)

st.write(f"Probabilidade do mercado (implícita): **{p_mercado*100:.2f}%**")
st.write(f"**p-value:** {p_value:.6f}")

if p_value < 0.05:
    st.success("Resultado estatisticamente significativo (possível edge).")
else:
    st.warning("Resultado compatível com sorte / variância.")

# =========================================================
# MÓDULO 4 — CRITÉRIO DE KELLY
# =========================================================
st.markdown("### 4️⃣ Critério de Kelly")

bankroll = st.number_input("Bankroll total (R$)", min_value=1.0, value=1000.0)
odd_kelly = st.number_input("Odd", min_value=1.01, value=1.60, key="kelly1")
p_kelly = st.slider("Probabilidade estimada de acerto (%)", 1, 99, 60, key="kelly2") / 100

f_kelly = (p_kelly * odd_kelly - 1) / (odd_kelly - 1)

if f_kelly <= 0:
    st.error("Kelly ≤ 0 → Não apostar (EV negativo).")
else:
    aposta_otima = bankroll * f_kelly
    st.success(f"Fração de Kelly: **{f_kelly:.2%}**")
    st.write(f"Aposta teórica ótima: **R$ {aposta_otima:.2f}**")
