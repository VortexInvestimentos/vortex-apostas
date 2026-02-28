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
# CSS GLOBAL (FONTE + FUNDO + CORES)
# =========================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500&display=swap');

    .stApp {
        background-color: #000000;
        color: #FFFFFF;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    h1, h2, h3, h4, h5, h6, p, span, label, div {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        color: #FFFFFF;
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

# Espaço entre logo e título
st.markdown("<div style='height: 22px;'></div>", unsafe_allow_html=True)

st.markdown(
    """
    <div style="text-align: center;">
        <h1 style="font-size: 32px; font-weight: 400; margin-bottom: 6px;">
            Vortex Investimentos
        </h1>
        <h3 style="font-size: 18px; font-weight: 300; margin-top: 0;">
            Vortex Bet Hunter
        </h3>
    </div>
    """,
    unsafe_allow_html=True
)

# Espaço entre subtítulo e primeira seção
st.markdown("<div style='height: 36px;'></div>", unsafe_allow_html=True)

# =========================================================
# FUNÇÃO – OBJETIVO FINAL
# =========================================================
def calcular_bilhetes_para_objetivo(valor_ur, odd, objetivo):
    if odd <= 1 or objetivo <= valor_ur:
        return 0
    n = math.log(objetivo / valor_ur) / math.log(odd)
    return math.ceil(n)

# =========================================================
# TÍTULO – OBJETIVO FINAL
# =========================================================
st.markdown(
    "<h2 style='font-size: 22px; font-weight: 400;'>🎯 Cálculo de Objetivo Final</h2>",
    unsafe_allow_html=True
)

ativar_objetivo = st.toggle("Ativar cálculo de objetivo final")

if ativar_objetivo:
    objetivo = st.number_input("Objetivo final (R$)", min_value=1, step=1, value=1000)
    valor_ur_obj = st.number_input("Valor da UR (R$)", min_value=1, step=1, value=100)
    odd_fixa = st.number_input("Odd fixa", min_value=1.01, step=0.01, value=1.33)

    if st.button("Calcular bilhetes necessários"):
        n = calcular_bilhetes_para_objetivo(valor_ur_obj, odd_fixa, objetivo)
        st.success(f"São necessários **{n} bilhetes vencedores consecutivos**.")

st.markdown("<div style='height: 36px;'></div>", unsafe_allow_html=True)

# =========================================================
# CORE ENGINE – CENÁRIO FIXO
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

# =========================================================
# BACKTEST EXAUSTIVO
# =========================================================
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

# =========================================================
# TÍTULO – BACKTEST
# =========================================================
st.markdown(
    "<h2 style='font-size: 22px; font-weight: 400;'>🔍 Backtest Paramétrico</h2>",
    unsafe_allow_html=True
)

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
    df_com = backtest(
        valor_ur, bilhetes,
        odd_min, odd_max,
        pat_min, pat_max,
        ativar_patamar=True
    )

    df_sem = backtest(
        valor_ur, bilhetes,
        odd_min, odd_max,
        pat_min, pat_max,
        ativar_patamar=False
    )

    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)

    st.markdown("### Comparação Automática")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Com proteção (UR)**")
        st.metric("Melhor Patrimônio", f"R$ {df_com.iloc[0]['Patrimônio Final']}")
        st.metric("Lucro Máximo", f"R$ {df_com.iloc[0]['Lucro']}")

    with col2:
        st.markdown("**Sem proteção**")
        st.metric("Melhor Patrimônio", f"R$ {df_sem.iloc[0]['Patrimônio Final']}")
        st.metric("Lucro Máximo", f"R$ {df_sem.iloc[0]['Lucro']}")

    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)

    st.markdown("### Resultados com Patamar")
    st.dataframe(
        df_com[["Odd", "Patamar (×UR)", "URs Criadas", "Lucro", "Patrimônio Final"]],
        use_container_width=True
    )

    st.markdown("### Resultados sem Patamar")
    st.dataframe(
        df_sem[["Odd", "URs Criadas", "Lucro", "Patrimônio Final"]],
        use_container_width=True
    )

    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)

    st.markdown("### Visualizar Cenário (com patamar)")

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
        st.markdown("**Pontos de nascimento de URs**")
        st.write(eventos[["Bilhete", "Evento"]])
