import streamlit as st
import random
import statistics
import pandas as pd
import os

# =========================
# HEADER
# =========================
st.set_page_config(page_title="Vortex Investimentos", layout="centered")

if os.path.exists("logo_vortex.png"):
    st.image("logo_vortex.png", width=200)

st.title("Vortex Investimentos")
st.subheader("Método Vortex ARC – Engenharia de Risco")

# =========================
# ENGINE
# =========================
def simulador_vortex(
    valor_ur,
    odd_min,
    odd_max,
    bilhetes,
    patamar_min,
    patamar_max,
):
    saldo = valor_ur
    urs_filhotes = 0

    historico = []
    eventos_ur = []

    for i in range(1, bilhetes + 1):
        odd = round(random.uniform(odd_min, odd_max), 2)
        multiplicador = random.uniform(patamar_min, patamar_max)

        patamar = valor_ur * multiplicador

        saldo *= odd
        evento = None

        if saldo >= patamar:
            saldo -= valor_ur
            urs_filhotes += 1
            evento = "UR"
            eventos_ur.append(i)

        patrimonio = saldo + urs_filhotes * valor_ur

        historico.append({
            "Bilhete": i,
            "Patrimônio Total": round(patrimonio, 2),
            "Odd": odd,
            "Patamar (×UR)": round(multiplicador, 2),
            "Evento": evento
        })

    return pd.DataFrame(historico), eventos_ur


def monte_carlo(config, n=1000):
    resultados = []

    for _ in range(n):
        df, _ = simulador_vortex(**config)
        final = df.iloc[-1]

        resultados.append({
            "Patrimônio Final": final["Patrimônio Total"],
            "Odd Média": round(df["Odd"].mean(), 2),
            "Patamar Médio (×UR)": round(df["Patamar (×UR)"].mean(), 2),
        })

    df_mc = pd.DataFrame(resultados)
    df_mc["Lucro"] = df_mc["Patrimônio Final"] - config["valor_ur"]
    df_mc = df_mc.sort_values(by="Lucro", ascending=False)

    return df_mc

# =========================
# UI – PARÂMETROS
# =========================
st.markdown("### Parâmetros")

valor_ur = st.number_input("Valor da UR", 10, 1000, 100, step=10)
bilhetes = st.number_input("Quantidade de bilhetes", 10, 1000, 50, step=1)

odd_min, odd_max = st.slider(
    "Faixa de Odds",
    1.01, 2.00, (1.30, 1.33), step=0.01
)

patamar_min, patamar_max = st.slider(
    "Patamar (multiplicador da UR)",
    1.5, 5.0, (3.0, 3.0), step=0.1
)

modo_mc = st.toggle("Ativar Monte Carlo")

# =========================
# SIMULAÇÃO
# =========================
if st.button("SIMULAR"):
    config = {
        "valor_ur": valor_ur,
        "odd_min": odd_min,
        "odd_max": odd_max,
        "bilhetes": bilhetes,
        "patamar_min": patamar_min,
        "patamar_max": patamar_max
    }

    df, eventos_ur = simulador_vortex(**config)

    st.markdown("## Resultado Final")
    st.metric("Patrimônio Total", f"R$ {df.iloc[-1]['Patrimônio Total']}")
    st.metric("URs Criadas", len(eventos_ur))

    st.markdown("## Crescimento do Patrimônio")
    st.line_chart(df.set_index("Bilhete")["Patrimônio Total"])

    if eventos_ur:
        st.caption(f"URs nasceram nos bilhetes: {eventos_ur}")

    if modo_mc:
        st.markdown("## Monte Carlo – Resultados Ordenados")
        df_mc = monte_carlo(config)
        st.dataframe(df_mc)
