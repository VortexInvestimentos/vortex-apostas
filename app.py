import streamlit as st
import pandas as pd
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
st.markdown(
    """
    <style>
    .stApp {
        background-color: #000000;
        color: #FFFFFF;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# FUNÇÃO PARA LOGO CENTRALIZADA
# =========================================================
def mostrar_logo_centralizada(caminho, largura=140):
    with open(caminho, "rb") as f:
        dados = base64.b64encode(f.read()).decode()

    html = f"""
    <div style="display: flex; justify-content: center;">
        <img src="data:image/png;base64,{dados}" width="{largura}">
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================
if os.path.exists("logo_vortex.png"):
    mostrar_logo_centralizada("logo_vortex.png", largura=140)

st.markdown("## Vortex Bet Hunter")

# =========================================================
# FUNÇÃO – OBJETIVO FINAL (RESTAURADA, INTACTA)
# =========================================================
def calcular_bilhetes_para_objetivo(valor_ur, odd, objetivo):
    if odd <= 1 or objetivo <= valor_ur:
        return 0
    n = math.log(objetivo / valor_ur) / math.log(odd)
    return math.ceil(n)

# =========================================================
# SEÇÃO – OBJETIVO FINAL (RESTAURADA, INTACTA)
# =========================================================
st.markdown("### 🎯 Cálculo de Objetivo Final")

ativar_objetivo = st.toggle("Ativar cálculo de objetivo final")

if ativar_objetivo:
    objetivo = st.number_input("Objetivo final (R$)", min_value=1, step=1, value=1000)
    valor_ur_obj = st.number_input("Valor da UR (R$)", min_value=1, step=1, value=100)
    odd_fixa = st.number_input("Odd fixa", min_value=1.01, step=0.01, value=1.33)

    if st.button("Calcular bilhetes necessários"):
        n = calcular_bilhetes_para_objetivo(valor_ur_obj, odd_fixa, objetivo)
        st.success(f"São necessários **{n} bilhetes vencedores consecutivos**.")

# =========================================================
# CORE ENGINE (INALTERADO NA LÓGICA)
# =========================================================
def rodar_cenario(valor_ur, odd, bilhetes, patamar, ativar_patamar):
    saldo = valor_ur
    urs = 0
    limite = valor_ur * patamar

    for _ in range(bilhetes):
        saldo *= odd
        if ativar_patamar and saldo >= limite:
            saldo -= valor_ur
            urs += 1

    return round(saldo + urs * valor_ur, 2)

def frange(start, stop, step):
    while start <= stop + 1e-9:
        yield round(start, 2)
        start += step

# =========================================================
# FUNÇÕES DE SCORE (NOVAS – BACKTEST)
# =========================================================
def score_fragilidade(patrimonio, ur, bilhetes, odd):
    fragilidade = ur * bilhetes * (odd - 1)
    return patrimonio / fragilidade if fragilidade > 0 else 0

def score_retorno_risco(patrimonio, ur, bilhetes):
    capital_exposto = ur * bilhetes
    return patrimonio / capital_exposto if capital_exposto > 0 else 0

def score_utilidade_log(patrimonio, ur, bilhetes):
    capital_exposto = ur * bilhetes
    if capital_exposto <= 0 or patrimonio <= 0:
        return -999
    return math.log(patrimonio / capital_exposto)

# =========================================================
# BACKTEST EVOLUÍDO
# =========================================================
st.markdown("### 🔍 Backtest Paramétrico Inteligente")

criterio = st.selectbox(
    "Critério de Avaliação do Backtest",
    [
        "Fragilidade",
        "Retorno / Risco Implícito",
        "Utilidade Logarítmica"
    ]
)

ur_min, ur_max = st.slider("Faixa de UR", 10, 1000, (100, 300), step=10)
bil_min, bil_max = st.slider("Faixa de Bilhetes", 5, 300, (20, 60), step=1)
odd_min, odd_max = st.slider("Faixa de Odds", 1.01, 3.00, (1.30, 1.40), step=0.01)

ativar_patamar = st.toggle("Ativar Patamar", True)

pat_min, pat_max = st.slider(
    "Faixa de Patamar (×UR)",
    2, 6, (2, 4),
    step=1,
    disabled=not ativar_patamar
)

if st.button("Rodar Backtest"):
    top10 = []

    for ur in range(ur_min, ur_max + 1, 10):
        for bil in range(bil_min, bil_max + 1):
            for odd in frange(odd_min, odd_max, 0.01):
                for pat in range(pat_min, pat_max + 1):
                    patrimonio = rodar_cenario(ur, odd, bil, pat, ativar_patamar)

                    if criterio == "Fragilidade":
                        score = score_fragilidade(patrimonio, ur, bil, odd)
                    elif criterio == "Retorno / Risco Implícito":
                        score = score_retorno_risco(patrimonio, ur, bil)
                    else:
                        score = score_utilidade_log(patrimonio, ur, bil)

                    registro = {
                        "Score": round(score, 6),
                        "Patrimônio Final (R$)": patrimonio,
                        "UR": ur,
                        "Bilhetes": bil,
                        "Odd": odd,
                        "Patamar": pat if ativar_patamar else "—"
                    }

                    top10.append(registro)
                    top10 = sorted(top10, key=lambda x: x["Score"], reverse=True)[:10]

    df = pd.DataFrame(top10)
    df.index = range(1, len(df) + 1)
    st.dataframe(df)
