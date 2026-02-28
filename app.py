import streamlit as st
import random
import statistics

# =========================
# ENGINE (DETERMINÍSTICO)
# =========================
def simulador_vortex(
    valor_ur,
    odd_min,
    odd_max,
    bilhetes,
    patamar,
    retirada_ur,
):
    saldo = valor_ur
    urs_filhotes = 0
    urs_totais = 1
    proximo_patamar = patamar

    for _ in range(bilhetes):
        odd = round(random.uniform(odd_min, odd_max), 2)

        # WIN sempre (modelo sem ruína)
        saldo *= odd

        # Nascimento de UR (uma por patamar)
        if saldo >= proximo_patamar:
            saldo -= retirada_ur
            urs_filhotes += 1
            urs_totais += 1
            proximo_patamar += patamar

    return {
        "saldo_final": round(saldo, 2),
        "urs_filhotes": urs_filhotes,
        "capital_protegido": urs_filhotes * retirada_ur,
        "patrimonio_total": round(saldo + urs_filhotes * retirada_ur, 2),
    }


def monte_carlo(config, n=5000):
    resultados = []

    for _ in range(n):
        r = simulador_vortex(**config)
        resultados.append(r["patrimonio_total"])

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

st.title("📱 Vortex ARC – Engenharia de Risco")

st.markdown("### Parâmetros")

valor_ur = st.number_input(
    "💵 Valor da UR",
    min_value=10,
    max_value=1000,
    value=100,
    step=10
)

odd_min, odd_max = st.slider(
    "🎯 Faixa de Odds",
    min_value=1.01,
    max_value=2.00,
    value=(1.30, 1.33),
    step=0.01
)

bilhetes = st.slider(
    "📆 Quantidade de bilhetes",
    min_value=10,
    max_value=1000,
    value=30,
    step=1
)

modo_mc = st.toggle("🔁 Ativar Monte Carlo (dispersão de resultados)")

config = {
    "valor_ur": valor_ur,
    "odd_min": odd_min,
    "odd_max": odd_max,
    "bilhetes": bilhetes,
    "patamar": 300,
    "retirada_ur": valor_ur
}

if st.button("▶️ SIMULAR"):
    r = simulador_vortex(**config)

    st.markdown("## 📊 Resultado")

    col1, col2 = st.columns(2)
    col1.metric("💰 Patrimônio Total", f"R$ {r['patrimonio_total']}")
    col2.metric("🔐 URs Protegidas", r["urs_filhotes"])

    col3, col4 = st.columns(2)
    col3.metric("🔥 Capital em Operação", f"R$ {r['saldo_final']}")
    col4.metric("📦 Capital Protegido", f"R$ {r['capital_protegido']}")

    if modo_mc:
        st.markdown("## 🔁 Monte Carlo (5.000 simulações)")
        mc = monte_carlo(config)

        st.metric("📈 Patrimônio Médio", f"R$ {mc['media']}")
        st.metric("⚖️ Mediana", f"R$ {mc['mediana']}")
        st.metric("🔝 Máximo", f"R$ {mc['maximo']}")
        st.metric("🔻 Mínimo", f"R$ {mc['minimo']}")
