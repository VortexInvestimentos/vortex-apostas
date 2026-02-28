import streamlit as st
import pandas as pd
import os
import math
import base64
import heapq

# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================
st.set_page_config(page_title="Vortex Bet", layout="centered")

# =========================================================
# CSS GLOBAL
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500&display=swap');

.stApp {
    background-color: #000000;
    color: #FFFFFF;
    font-family: 'Inter', sans-serif;
}

.header-wrapper {
    text-align: center;
}

.header-title {
    font-size: 28px;
    font-weight: 300;
}

.header-subtitle {
    font-size: 26px;
    font-weight: 200;
    color: #B0B0B0;
}

.divider {
    width: 60%;
    height: 1px;
    background-color: #222;
    margin: 40px auto;
}

.section-title {
    font-size: 26px;
    font-weight: 300;
    margin-bottom: 16px;
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
        f"<div style='text-align:center;'><img src='data:image/png;base64,{dados}' width='{largura}'></div>",
        unsafe_allow_html=True
    )

if os.path.exists("logo_vortex.png"):
    mostrar_logo_centralizada("logo_vortex.png")

st.markdown("""
<div class="header-wrapper">
    <h1 class="header-title">Vortex Bet</h1>
    <div class="header-subtitle">Vortex Bet Hunter</div>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)

# =========================================================
# FUNÇÃO OBJETIVO FINAL (GENÉRICA)
# =========================================================
def calcular_variavel(alvo, objetivo, ur, odd, bilhetes):
    if alvo == "Bilhetes":
        return math.ceil(math.log(objetivo / ur) / math.log(odd))
    if alvo == "Objetivo":
        return round(ur * (odd ** bilhetes), 2)
    if alvo == "UR":
        return round(objetivo / (odd ** bilhetes), 2)
    if alvo == "Odd":
        return round((objetivo / ur) ** (1 / bilhetes), 4)

# =========================================================
# SEÇÃO OBJETIVO FINAL
# =========================================================
st.markdown("<div class='section-title'>🎯 Cálculo de Objetivo Final</div>", unsafe_allow_html=True)

alvo = st.selectbox(
    "Qual variável deseja calcular?",
    ["Bilhetes", "Objetivo", "UR", "Odd"]
)

objetivo = st.number_input("Objetivo final (R$)", value=1000.0)
ur = st.number_input("Valor da UR (R$)", value=100.0)
odd = st.number_input("Odd fixa", value=1.33)
bilhetes = st.number_input("Quantidade de bilhetes", value=10)

if st.button("Calcular"):
    resultado = calcular_variavel(alvo, objetivo, ur, odd, bilhetes)
    st.success(f"{alvo} calculado: **{resultado}**")

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# =========================================================
# CORE ENGINE (SEM HISTÓRICO, ULTRA LEVE)
# =========================================================
def simular(valor_ur, odd, bilhetes, patamar, ativar_patamar):
    saldo = valor_ur
    urs = 0
    limite = valor_ur * patamar if ativar_patamar else None

    for _ in range(bilhetes):
        saldo *= odd
        if ativar_patamar and saldo >= limite:
            saldo -= valor_ur
            urs += 1

    return round(saldo + urs * valor_ur, 2)

# =========================================================
# BACKTEST OTIMIZADO (TOP 10)
# =========================================================
def backtest_otimizado(ur_range, bilhetes_range, odd_range, pat_range, ativar_patamar):
    top10 = []

    for ur in ur_range:
        for b in bilhetes_range:
            for odd in odd_range:
                for pat in pat_range:
                    final = simular(ur, odd, b, pat, ativar_patamar)

                    registro = (
                        final,
                        {
                            "UR": ur,
                            "Bilhetes": b,
                            "Odd": odd,
                            "Patamar": pat if ativar_patamar else "—"
                        }
                    )

                    if len(top10) < 10:
                        heapq.heappush(top10, registro)
                    else:
                        heapq.heappushpop(top10, registro)

    return sorted(top10, key=lambda x: x[0], reverse=True)

# =========================================================
# SEÇÃO BACKTEST
# =========================================================
st.markdown("<div class='section-title'>🔍 Backtest Paramétrico</div>", unsafe_allow_html=True)

ur_min, ur_max, ur_step = st.number_input("UR mín", 10), st.number_input("UR máx", 500), st.number_input("UR step", 10)
b_min, b_max, b_step = st.number_input("Bilhetes mín", 5), st.number_input("Bilhetes máx", 100), st.number_input("Bilhetes step", 5)

odd_min, odd_max = st.slider("Faixa de Odds", 1.01, 2.0, (1.30, 1.35), step=0.01)

ativar_patamar = st.toggle("Ativar patamar", value=True)
pat_min, pat_max = st.slider("Faixa de Patamar", 2, 6, (2, 4), disabled=not ativar_patamar)

if st.button("Rodar Backtest"):
    ur_range = range(int(ur_min), int(ur_max + 1), int(ur_step))
    bilhetes_range = range(int(b_min), int(b_max + 1), int(b_step))
    odd_range = [round(o, 2) for o in frange := [odd_min + i*0.01 for i in range(int((odd_max-odd_min)/0.01)+1)]]
    pat_range = range(pat_min, pat_max + 1)

    resultados = backtest_otimizado(
        ur_range, bilhetes_range, odd_range, pat_range, ativar_patamar
    )

    st.markdown("### 🏆 Top 10 Resultados")
    for i, (valor, cfg) in enumerate(resultados, 1):
        st.write(
            f"**#{i}** | R$ {valor} | UR: {cfg['UR']} | "
            f"Bilhetes: {cfg['Bilhetes']} | Odd: {cfg['Odd']} | Patamar: {cfg['Patamar']}"
        )
