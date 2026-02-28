import streamlit as st
import random
import statistics

# =========================
# ENGINE
# =========================
def simulador_vortex(
    valor_ur,
    odd_min,
    odd_max,
    dias,
    patamar,
    retirada_ur,
    prob_acerto,
):
    saldo = valor_ur
    urs_filhotes = 0
    urs_totais = 1
    proximo_patamar = patamar

    for _ in range(dias):
        odd = round(random.uniform(odd_min, odd_max), 2)

        # Ruína
        if random.random() > prob_acerto:
            return {
                "saldo_final": 0,
                "urs_filhotes": urs_filhotes,
                "capital_protegido": urs_filhotes * retirada_ur,
                "patrimonio_total": urs_filhotes * retirada_ur,
                "ruina": True
            }

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
        "ruina": False
    }


def monte_carlo(config, n=5000):
    resultados = []
    ruinas = 0

    for _ in range(n):
        r = simulador_vortex(**config)
        resultados.append(r["patrimonio_total"])
        if r["ruina"]:
            ruinas += 1

    return {
        "media": round(statistics.mean(resultados), 2),
        "mediana": round(statistics.median(resultados), 2),
        "maximo": round(max(resultados), 2),
        "minimo": round(min(resultados), 2),
        "risco_ruina": round(ruinas / n * 100, 2)
    }


# =========================
# UI – MOBILE FIRST
# =========================
st.set_page_config(page_title="Vortex ARC – Apostas", layout="centered")

st.title("📱 Vortex ARC – Engenharia de Risco")

st.markdown("### Parâmetros do Bilhete")

valor_ur = st.number_input("💵 Valor da UR", 50, 1000, 100, step=50)

odd_min, odd_max = st.slider(
    "🎯 Faixa de Odds",
    1.10, 2.00, (1.30, 1.36),
    step=0.01
)

dias = st.slider("📆 Quantidade de bilhetes", 1, 120, 30)

prob_acerto = st.slider(
    "✅ Probabilidade estimada de acerto",
    0.50, 1.00, 0.78,
    step=0.01
)

modo_mc = st.toggle("🔁 Ativar Monte Carlo (análise de risco)")

config = {
    "valor_ur": valor_ur,
    "odd_min": odd_min,
    "odd_max": odd_max,
    "dias": dias,
    "patamar": 300,
    "retirada_ur": valor_ur,
    "prob_acerto": prob_acerto
}

if st.button("▶️ SIMULAR"):
    r = simulador_vortex(**config)

    st.markdown("## 📊 Resultado")

    col1, col2 = st.columns(2)
    col1.metric("💰 Patrimônio Total", f"R$ {r['patrimonio_total']}")
    col2.metric("🔐 URs Protegidas", r["urs_filhotes"])

    col3, col4 = st.columns(2)
    col3.metric("🔥 Capital em Risco", f"R$ {r['saldo_final']}")
    col4.metric("⚠️ Ruína", "SIM" if r["ruina"] else "NÃO")

    if modo_mc:
        st.markdown("## 🔁 Monte Carlo (5.000 simulações)")
        mc = monte_carlo(config)

        st.metric("📉 Risco de Ruína", f"{mc['risco_ruina']} %")
        st.metric("📈 Patrimônio Médio", f"R$ {mc['media']}")
        st.metric("🔝 Máximo", f"R$ {mc['maximo']}")
        st.metric("🔻 Mínimo", f"R$ {mc['minimo']}")
