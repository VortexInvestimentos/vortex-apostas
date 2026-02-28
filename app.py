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
        font-size: 28px;    
        font-weight: 300;    
        margin: 0;    
    }    
    
    .header-subtitle {    
        font-size: 26px;    
        font-weight: 200;    
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
        font-size: 26px;    
        font-weight: 300;    
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
        <h1 class="header-title">Vortex Bet</h1>    
        <div class="header-subtitle">Vortex Bet Hunter</div>    
    </div>    
    """,    
    unsafe_allow_html=True    
)    
    
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# =========================================================
# OBJETIVO FINAL – FLEXÍVEL
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

# =========================================================
# CORE ENGINE
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
# BACKTEST OTIMIZADO
# =========================================================
st.markdown("### 🔍 Backtest Paramétrico (Top 10)")

ur_min, ur_max = st.slider("Faixa UR", 10, 1000, (100, 300), step=10)
bil_min, bil_max = st.slider("Faixa Bilhetes", 5, 200, (20, 60), step=1)

odd_min, odd_max = st.slider("Faixa Odds", 1.01, 3.00, (1.30, 1.40), step=0.01)

ativar_patamar = st.toggle("Ativar Patamar", True)
pat_min, pat_max = st.slider("Faixa Patamar (×UR)", 2, 6, (2, 4), step=1, disabled=not ativar_patamar)

if st.button("Rodar Backtest"):
    top10 = []

    for ur in range(ur_min, ur_max + 1, 10):
        for bil in range(bil_min, bil_max + 1):
            for odd in frange(odd_min, odd_max, 0.01):
                for pat in range(pat_min, pat_max + 1):
                    final = rodar_cenario(ur, odd, bil, pat, ativar_patamar)

                    registro = {
                        "Patrimônio Final": final,
                        "UR": ur,
                        "Bilhetes": bil,
                        "Odd": odd,
                        "Patamar": pat if ativar_patamar else "—"
                    }

                    top10.append(registro)
                    top10 = sorted(top10, key=lambda x: x["Patrimônio Final"], reverse=True)[:10]

    df = pd.DataFrame(top10)
    df.index = range(1, len(df) + 1)
    st.dataframe(df)
