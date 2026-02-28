import streamlit as st
import pandas as pd
import os
import math
import base64

st.set_page_config(page_title="Vortex Investimentos", layout="centered")

st.markdown(
    """
    <style>
    .stApp {
        background-color: #000000;
        color: #FFFFFF;
    }
    h1, h2, h3, h4, h5, h6, p, span, label {
        color: #FFFFFF !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def mostrar_logo_centralizada(caminho, largura=140):
    with open(caminho, "rb") as f:
        dados = base64.b64encode(f.read()).decode()
    st.markdown(
        f"<div style='display:flex; justify-content:center;'>"
        f"<img src='data:image/png;base64,{dados}' width='{largura}'>"
        f"</div>",
        unsafe_allow_html=True
    )

if os.path.exists("logo_vortex.png"):
    mostrar_logo_centralizada("logo_vortex.png", largura=140)

st.markdown(
    """
    <div style="text-align: center;">
        <h1>Vortex Investimentos</h1>
        <h3 style="font-weight: 400;">Vortex Bet Hunter</h3>
    </div>
    """,
    unsafe_allow_html=True
)

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

# =========================
# BACKTEST EXAUSTIVO
# =========================
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
    objetivo = st.number_input("Objetivo final (R$)", min_value=1, step=1, value=1000)
    valor_ur_obj = st.number_input("Valor da UR (R$)", min_value=1, step=1, value=100)
    odd_fixa = st.number_input("Odd fixa", min_value=1.01, step=0.01, value=1.33)

    if st.button("CALCULAR BILHETES NECESSÁRIOS"):
        n = calcular_bilhetes_para_objetivo(valor_ur_obj, odd_fixa, objetivo)
        st.success(f"São necessários **{n} bilhetes vencedores consecutivos**.")

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

ativar_patamar = st.toggle("Ativar retirada de UR (patamar)", value=True)

pat_min, pat_max = st.slider(
    "Faixa de Patamar (multiplicador da UR)",
    min_value=2,
    max_value=5,
    value=(2, 4),
    step=1,
    disabled=not ativar_patamar
)

if st.button("RODAR BACKTEST"):
    # Backtest COM patamar
    df_com = backtest(
        valor_ur, bilhetes,
        odd_min, odd_max,
        pat_min, pat_max,
        ativar_patamar=True
    )

    # Backtest SEM patamar
    df_sem = backtest(
        valor_ur, bilhetes,
        odd_min, odd_max,
        pat_min, pat_max,
        ativar_patamar=False
    )

    st.markdown("## 📊 Comparação Automática")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🔐 Com Proteção (UR)")
        st.metric("Melhor Patrimônio", f"R$ {df_com.iloc[0]['Patrimônio Final']}")
        st.metric("Lucro Máximo", f"R$ {df_com.iloc[0]['Lucro']}")

    with col2:
        st.markdown("### 🔥 Sem Proteção")
        st.metric("Melhor Patrimônio", f"R$ {df_sem.iloc[0]['Patrimônio Final']}")
        st.metric("Lucro Máximo", f"R$ {df_sem.iloc[0]['Lucro']}")

    st.divider()

    st.markdown("## 📋 Resultados COM Patamar")
    st.dataframe(
        df_com[["Odd", "Patamar (×UR)", "URs Criadas", "Lucro", "Patrimônio Final"]],
        use_container_width=True
    )

    st.markdown("## 📋 Resultados SEM Patamar")
    st.dataframe(
        df_sem[["Odd", "URs Criadas", "Lucro", "Patrimônio Final"]],
        use_container_width=True
    )

    st.divider()

    st.markdown("## 📈 Visualizar Cenário (COM Patamar)")

    opcoes = [
        f"Odd {row['Odd']} | Patamar {row['Patamar (×UR)']}× | Lucro {row['Lucro']}"
        for _, row in df_com.iterrows()
    ]

    escolha = st.selectbox(
        "Escolha um cenário",
        range(len(opcoes)),
        format_func=lambda i: opcoes[i]
    )

    df_sel = df_com.iloc[escolha]["Histórico"]

    st.line_chart(df_sel.set_index("Bilhete")["Patrimônio Total"])

    eventos = df_sel[df_sel["Evento"].notna()]
    if not eventos.empty:
        st.markdown("### Pontos de nascimento de URs")
        st.write(eventos[["Bilhete", "Evento"]])
