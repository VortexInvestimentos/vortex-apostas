import streamlit as st
import pandas as pd
import os
import math

# =========================
# HEADER
# =========================
st.set_page_config(page_title="Vortex Investimentos", layout="centered")

if os.path.exists("logo_vortex.png"):
    st.image("logo_vortex.png", width=200)

st.title("Vortex Investimentos")
st.subheader("Método Vortex ARC – Engenharia de Risco")

# =========================
# FUNÇÃO OBJETIVO FINAL
# =========================
def calcular_bilhetes_para_objetivo(valor_ur, odd, objetivo):
    if odd <= 1 or objetivo <= valor_ur:
        return 0
    n = math.log(objetivo / valor_ur) / math.log(odd)
    return math.ceil(n)

# =========================
# CORE ENGINE (CENÁRIO FIXO)
# =========================
def rodar_cenario(valor_ur, odd, bilhetes, multiplicador):
    saldo = valor_ur
    urs = 0
    historico = []

    patamar = valor_ur * multiplicador

    for i in range(1, bilhetes + 1):
        saldo *= odd
        evento = None

        if saldo >= patamar:
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

# =========================
# BACKTEST EXAUSTIVO
# =========================
def backtest(valor_ur, bilhetes, odd_min, odd_max, pat_min, pat_max):
    resultados = []

    odds = [round(o, 2) for o in frange(odd_min, odd_max, 0.01)]
    patamares = list(range(pat_min, pat_max + 1))

    for odd in odds:
        for pat in patamares:
            df, urs = rodar_cenario(valor_ur, odd, bilhetes, pat)
            final = df.iloc[-1]["Patrimônio Total"]

            resultados.append({
                "Odd": odd,
                "Patamar (×UR)": pat,
                "URs Criadas": urs,
                "Patrimônio Final": final,
                "Lucro": round(final - valor_ur, 2),
                "Histórico": df
            })

    df_resultados = pd.DataFrame(resultados)
    df_resultados = df_resultados.sort_values(by="Lucro", ascending=False)

    return df_resultados

def frange(start, stop, step):
    while start <= stop + 1e-9:
        yield start
        start += step

# =========================
# UI — OBJETIVO FINAL
# =========================
st.markdown("## 🎯 Cálculo de Objetivo Final")

ativar_objetivo = st.toggle("Ativar cálculo de objetivo final")

if ativar_objetivo:
    objetivo = st.number_input(
        "Objetivo final (R$)",
        min_value=1,
        step=1,
        value=1000
    )

    valor_ur_obj = st.number_input(
        "Valor da UR (R$)",
        min_value=1,
        step=1,
        value=100
    )

    odd_fixa = st.number_input(
        "Odd fixa",
        min_value=1.01,
        step=0.01,
        value=1.33
    )

    if st.button("CALCULAR BILHETES NECESSÁRIOS"):
        n = calcular_bilhetes_para_objetivo(valor_ur_obj, odd_fixa, objetivo)

        st.success(
            f"São necessários **{n} bilhetes vencedores consecutivos** "
            f"para alcançar ou superar R$ {objetivo}."
        )

st.divider()

# =========================
# UI — BACKTEST
# =========================
st.markdown("## 🔍 Backtest Paramétrico")

valor_ur = st.number_input("Valor da UR", 10, 1000, 100, step=10)
bilhetes = st.number_input("Quantidade de bilhetes", 10, 1000, 50, step=1)

odd_min, odd_max = st.slider(
    "Faixa de Odds (fixas por cenário)",
    1.01, 2.00, (1.30, 1.33), step=0.01
)

pat_min, pat_max = st.slider(
    "Faixa de Patamar (multiplicador da UR)",
    min_value=2,
    max_value=5,
    value=(2, 4),
    step=1
)

if st.button("RODAR BACKTEST"):
    df_bt = backtest(valor_ur, bilhetes, odd_min, odd_max, pat_min, pat_max)

    st.markdown("### Resultados (ordenados por maior lucro)")
    st.dataframe(
        df_bt[["Odd", "Patamar (×UR)", "URs Criadas", "Lucro", "Patrimônio Final"]],
        use_container_width=True
    )

    st.markdown("### Selecionar cenário para visualizar")

    opcoes = [
        f"Odd {row['Odd']} | Patamar {row['Patamar (×UR)']}× | Lucro {row['Lucro']}"
        for _, row in df_bt.iterrows()
    ]

    escolha = st.selectbox(
        "Escolha um cenário",
        range(len(opcoes)),
        format_func=lambda i: opcoes[i]
    )

    df_sel = df_bt.iloc[escolha]["Histórico"]

    st.markdown("### Gráfico do cenário selecionado")
    st.line_chart(df_sel.set_index("Bilhete")["Patrimônio Total"])

    eventos = df_sel[df_sel["Evento"].notna()]
    if not eventos.empty:
        st.markdown("### Pontos de nascimento de URs")
        st.write(eventos[["Bilhete", "Evento"]])
