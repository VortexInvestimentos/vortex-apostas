import streamlit as st
import random
import statistics
import pandas as pd

# =========================
# CONFIGURAÇÕES DE MODOS
# =========================
MODOS = {
    "Personalizado": None,
    "Conservador": {
        "odd_min": 1.05,
        "odd_max": 1.20,
        "multiplicador_patamar": 4
    },
    "Normal": {
        "odd_min": 1.25,
        "odd_max": 1.35,
        "multiplicador_patamar": 3
    },
    "Agressivo": {
        "odd_min": 1.40,
        "odd_max": 1.60,
        "multiplicador_patamar": 2
    }
}

# =========================
# ENGINE
# =========================
def simulador_vortex(
    valor_ur,
    odd_min,
    odd_max,
    bilhetes,
    multiplicador_patamar,
):
    saldo = valor_ur
    urs_filhotes = 0

    patamar = valor_ur * multiplicador_patamar
    proximo_patamar = patamar

    historico = []

    for i in range(1, bilhetes + 1):
        odd = round(random.uniform(odd_min, odd_max), 2)
        saldo *= odd

        evento = "WIN"

        if saldo >= proximo_patamar:
            saldo -= valor_ur
            urs_filhotes += 1
            proximo_patamar += patamar
            evento = "UR FILHOTE"

        patrimonio = saldo + urs_filhotes * valor_ur

        historico.append({
            "Bilhete": i,
            "Odd": odd,
            "Saldo Operando": round(saldo, 2),
            "URs Protegidas": urs_filhotes,
            "Patrimônio Total": round(patrimonio, 2),
            "Evento": evento
        })

    return pd.DataFrame(historico)


def monte_carlo(config, n=3000):
    resultados = []

    for _ in range(n):
        df = simulador_vortex(**config)
        resultados.append(df.iloc[-1]["Patrimônio Total"])

    return {
        "media": round(statistics.mean(resultados), 2),
        "mediana": round(statistics.median(resultados), 2),
        "maximo": round(max(resultados), 2),
        "minimo": round(min(resultados), 2),
    }

# =========================
# UI – MOBILE FIRST
# =========================
st.set_page_config(page_title="Vortex ARC – Apostas", layout="centered")

st.title("🌪️ Vortex Investimentos")
st.subheader("Método Vortex ARC – Engenharia de Risco em Apostas")

st.markdown("### 🎛️ Modo de Operação")

modo = st.selectbox("Escolha o modo", list(MODOS.keys()))

# Valores padrão
odd_min = 1.30
odd_max = 1.33
multiplicador_patamar = 3

if modo != "Personalizado":
    odd_min = MODOS[modo]["odd_min"]
    odd_max = MODOS[modo]["odd_max"]
    multiplicador_patamar = MODOS[modo]["multiplicador_patamar"]

st.markdown("### ⚙️ Parâmetros")

valor_ur = st.number_input(
    "💵 Valor da UR",
    min_value=10,
    max_value=1000,
    value=100,
    step=10
)

bilhetes = st.number_input(
    "📆 Quantidade de bilhetes",
    min_value=10,
    max_value=1000,
    value=50,
    step=1
)

odd_min, odd_max = st.slider(
    "🎯 Faixa de Odds",
    min_value=1.01,
    max_value=2.00,
    value=(odd_min, odd_max),
    step=0.01
)

multiplicador_patamar = st.slider(
    "📦 Patamar (× UR)",
    min_value=2,
    max_value=5,
    value=multiplicador_patamar,
    step=1
)

modo_mc = st.toggle("🔁 Ativar Monte Carlo")

if st.button("▶️ SIMULAR"):
    config = {
        "valor_ur": valor_ur,
        "odd_min": odd_min,
        "odd_max": odd_max,
        "bilhetes": bilhetes,
        "multiplicador_patamar": multiplicador_patamar
    }

    df = simulador_vortex(**config)

    st.markdown("## 📊 Resultado Final")

    col1, col2 = st.columns(2)
    col1.metric("💰 Patrimônio Total", f"R$ {df.iloc[-1]['Patrimônio Total']}")
    col2.metric("🔐 URs Protegidas", int(df.iloc[-1]["URs Protegidas"]))

    st.markdown("## 📈 Gráfico de Crescimento")
    st.line_chart(df.set_index("Bilhete")["Patrimônio Total"])

    if modo_mc:
        st.markdown("## 🔁 Monte Carlo")
        mc = monte_carlo(config)

        st.metric("📈 Patrimônio Médio", f"R$ {mc['media']}")
        st.metric("⚖️ Mediana", f"R$ {mc['mediana']}")
        st.metric("🔝 Máximo", f"R$ {mc['maximo']}")
        st.metric("🔻 Mínimo", f"R$ {mc['minimo']}")
