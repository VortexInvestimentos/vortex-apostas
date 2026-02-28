import streamlit as st
import pandas as pd
import os
import math
import base64

# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================
st.set_page_config(page_title="Vortex Investimentos", layout="centered")

# =========================================================
# CSS GLOBAL (FONTE, FUNDO, CORES, ESPAÇAMENTOS)
# =========================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500&display=swap');

    :root {
        --space-xs: 8px;
        --space-sm: 16px;
        --space-md: 28px;
        --space-lg: 40px;
    }

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
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        width: 100%;
    }

    .header-title {
        font-size: 32px;
        font-weight: 400;
        margin: 0;
    }

    .header-subtitle {
        font-size: 18px;
        font-weight: 300;
        margin-top: 6px;
        color: #B0B0B0;
    }

    .divider {
        width: 60%;
        height: 1px;
        background-color: #222222;
        margin: var(--space-lg) auto;
    }

    .section-title {
        font-size: 22px;
        font-weight: 400;
        margin-bottom: var(--space-sm);
    }

    .section {
        margin-bottom: var(--space-lg);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# FUNÇÃO PARA LOGO CENTRALIZADA (BASE64)
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
# HEADER (LOGO + TÍTULO + SUBTÍTULO)
# =========================================================
if os.path.exists("logo_vortex.png"):
    mostrar_logo_centralizada("logo_vortex.png", largura=140)

st.markdown("<div style='height: var(--space-md);'></div>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="header-wrapper">
        <h1 class="header-title">Vortex Investimentos</h1>
        <div class="header-subtitle">Vortex Bet Hunter</div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# =========================================================
# FUNÇÃO – OBJETIVO FINAL
# =========================================================
def calcular_bilhetes_para_objetivo(valor_ur, odd, objetivo):
    if odd <= 1 or objetivo <= valor_ur:
        return 0
    n = math.log(objetivo / valor_ur) / math.log(odd)
    return math.ceil(n)

# =========================================================
# SEÇÃO – OBJETIVO FINAL
# =========================================================
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>🎯 Cálculo de Objetivo Final</div>", unsafe_allow_html=True)

ativar_objetivo = st.toggle("Ativar cálculo de objetivo final")

if ativar_objetivo:
    objetivo = st.number_input("Objetivo final (R$)", min_value=1, step=1, value=1000)
    valor_ur_obj = st.number_input("Valor da UR (R$)", min_value=1, step=1, value=100)
    odd_fixa = st.number_input("Odd fixa", min_value=1.01, step=0.01, value=1.33)

    if st.button("Calcular bilhetes necessários"):
        n = calcular_bilhetes_para_objetivo(valor_ur_obj, odd_fixa, objetivo)
        st.success(f"São necessários **{n} bilhetes vencedores consecutivos**.")

st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# CORE ENGINE
# =========================================================
def rodar_cenario(valor_ur, odd, bilhetes, multiplicador, ativar_patamar):
    saldo = valor_ur
    urs = 0
    historico = []

    patamar = valor_ur * multiplicador

    for i in range(1, bilhetes + 1):
        saldo *= odd
        evento = None

        if ativar_patamar and saldo >= patamar:
            saldo -= valor_ur
            urs += 1
            evento = f"UR ({multiplicador}×)"

        patrimonio = saldo + urs * valor_ur

        historico.append({
            "Bilhete": i,
            "Patrimônio Total": round(patrimonio, 2),
            "Evento": evento
        })

    return pd.DataFrame(historico), urs

def frange(start, stop, step):
    while start <= stop + 1e-9:
        yield start
        start += step

def backtest(valor_ur, bilhetes, odd_min, odd_max, pat_min, pat_max, ativar_patamar):
    resultados = []
    odds = [round(o, 2) for o in frange(odd_min, odd_max, 0.01)]
    patamares = list(range(pat_min, pat_max + 1))

    for odd in odds:
        for pat in patamares:
            df, urs = rodar_cenario(valor_ur, odd, bilhetes, pat, ativar_patamar)
            final = df.iloc[-1]["Patrimônio Total"]

            resultados.append({
                "Odd": odd,
                "Patamar (×UR)": pat if ativar_patamar else "—",
                "URs Criadas": urs,
                "Patrimônio Final": final,
                "Lucro": round(final - valor_ur, 2),
                "Histórico": df
            })

    return pd.DataFrame(resultados).sort_values(by="Lucro", ascending=False)

# =========================================================
# SEÇÃO – BACKTEST
# =========================================================
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>🔍 Backtest Paramétrico</div>", unsafe_allow_html=True)

valor_ur = st.number_input("Valor da UR", 10, 1000, 100, step=10)
bilhetes = st.number_input("Quantidade de bilhetes", 10, 1000, 50, step=1)

odd_min, odd_max = st.slider(
    "Faixa de Odds (fixas por cenário)",
    1.01, 2.00, (1.30, 1.33), step=0.01
)

ativar_patamar = st.toggle("Ativar retirada de UR (patamar)", value=True)

pat_min, pat_max = st.slider(
    "Faixa de Patamar (multiplicador da UR)",
    min_value=2,
    max_value=5,
    value=(2, 4),
    step=1,
    disabled=not ativar_patamar
)

if st.button("Rodar Backtest"):
    df_com = backtest(valor_ur, bilhetes, odd_min, odd_max, pat_min, pat_max, True)
    df_sem = backtest(valor_ur, bilhetes, odd_min, odd_max, pat_min, pat_max, False)

    st.markdown("### Comparação Automática")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Melhor Patrimônio (com proteção)", f"R$ {df_com.iloc[0]['Patrimônio Final']}")
    with col2:
        st.metric("Melhor Patrimônio (sem proteção)", f"R$ {df_sem.iloc[0]['Patrimônio Final']}")

st.markdown("</div>", unsafe_allow_html=True)
