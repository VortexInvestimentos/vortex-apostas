import streamlit as st
import os
import math
import base64

# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================
st.set_page_config(page_title="Vortex Bet", layout="centered")

# =========================================================
# CSS – TIPOGRAFIA E ESPAÇAMENTOS
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@200;300;400&display=swap');

.stApp {
    background-color: #000000;
    color: #FFFFFF;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.header-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    margin-top: 40px;
}

.header-title {
    font-size: 30px;
    font-weight: 200;
    margin: 0;
}

.header-subtitle {
    font-size: 15px;
    font-weight: 300;
    color: #9A9A9A;
    margin-top: 6px;
}

.section-spacing {
    margin-top: 48px;
}

.calc-title {
    font-size: 20px;
    font-weight: 300;
    margin-bottom: 12px;
}

.soft-validation {
    margin-top: 8px;
    font-size: 13px;
    color: #9A9A9A;
}

.compare-box {
    margin-top: 14px;
    padding: 10px;
    border: 1px solid #222222;
    border-radius: 8px;
    background-color: #0E0E0E;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# LOGO
# =========================================================
def mostrar_logo_centralizada(caminho, largura=140):
    with open(caminho, "rb") as f:
        dados = base64.b64encode(f.read()).decode()
    st.markdown(
        f"<div style='display:flex;justify-content:center;'>"
        f"<img src='data:image/png;base64,{dados}' width='{largura}'>"
        f"</div>",
        unsafe_allow_html=True
    )

if os.path.exists("logo_vortex.png"):
    mostrar_logo_centralizada("logo_vortex.png")

# =========================================================
# TÍTULO
# =========================================================
st.markdown("""
<div class="header-wrapper">
    <div class="header-title">Vortex Bet</div>
    <div class="header-subtitle">Vortex Bet Hunter</div>
</div>
""", unsafe_allow_html=True)

# =========================================================
# CÁLCULO DO OBJETIVO
# =========================================================
st.markdown('<div class="section-spacing"></div>', unsafe_allow_html=True)
st.markdown("<div class='calc-title'>🎯 Cálculo do Objetivo</div>", unsafe_allow_html=True)

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
    objetivo = st.number_input("Objetivo (R$)", min_value=1, value=1000)

if modo != "Bilhetes":
    bilhetes = st.number_input("Quantidade de Bilhetes", min_value=1, value=10)

# =========================================================
# PATAMAR – COMPARAÇÃO
# =========================================================
ativar_patamar = st.checkbox("Ativar geração de UR filhote (patamar)")

comparar_patamares = False
patamar_a = patamar_b = None

if ativar_patamar:
    comparar_patamares = st.checkbox("Comparar dois patamares")

    if comparar_patamares:
        col_a, col_b = st.columns(2)
        with col_a:
            patamar_a = st.number_input("Patamar A (×UR)", min_value=1, step=1, value=3)
        with col_b:
            patamar_b = st.number_input("Patamar B (×UR)", min_value=1, step=1, value=5)
    else:
        patamar_a = st.number_input("Patamar (×UR)", min_value=1, step=1, value=3)

# =========================================================
# CÁLCULO
# =========================================================
if st.button("Calcular"):

    # ---------- resultado bruto ----------
    if modo == "Bilhetes":
        n = math.log(objetivo / valor_ur) / math.log(odd)
        bil = math.ceil(n)
        resultado_bruto = valor_ur * (odd ** bil)
        st.success(f"Bilhetes necessários: **{bil}**")

    elif modo == "Valor da UR":
        resultado_bruto = objetivo
        ur = objetivo / (odd ** bilhetes)
        st.success(f"Valor da UR necessário: **R$ {ur:.2f}**")

    elif modo == "Odd":
        resultado_bruto = objetivo
        o = (objetivo / valor_ur) ** (1 / bilhetes)
        st.success(f"Odd necessária: **{o:.4f}**")

    elif modo == "Objetivo Final":
        resultado_bruto = valor_ur * (odd ** bilhetes)
        st.success(f"Resultado bruto: **R$ {resultado_bruto:.2f}**")

    # ---------- função de leitura de patamar ----------
    def leitura_patamar(multiplicador):
        valor_patamar = valor_ur * multiplicador
        urs = int(resultado_bruto // valor_patamar)
        protegido = urs * valor_ur
        em_risco = resultado_bruto - protegido
        pct = (protegido / resultado_bruto) * 100 if resultado_bruto > 0 else 0
        return urs, protegido, em_risco, pct

    # ---------- exibição ----------
    if ativar_patamar:

        if comparar_patamares:
            col1, col2 = st.columns(2)

            for col, label, pat in [(col1, "Patamar A", patamar_a),
                                     (col2, "Patamar B", patamar_b)]:
                urs, prot, risco, pct = leitura_patamar(pat)
                with col:
                    st.markdown(f"<div class='compare-box'>"
                                f"<strong>{label} — {pat}× UR</strong><br>"
                                f"URs filhotes: <strong>{urs}</strong><br>"
                                f"Capital protegido: <strong>R$ {prot:.2f}</strong><br>"
                                f"Em risco: <strong>R$ {risco:.2f}</strong><br>"
                                f"% protegido: <strong>{pct:.1f}%</strong>"
                                f"</div>", unsafe_allow_html=True)

        else:
            urs, prot, risco, pct = leitura_patamar(patamar_a)
            st.markdown(
                f"<div class='soft-validation'>"
                f"URs filhotes: <strong>{urs}</strong><br>"
                f"Capital protegido: <strong>R$ {prot:.2f}</strong><br>"
                f"Em risco: <strong>R$ {risco:.2f}</strong><br>"
                f"% protegido: <strong>{pct:.1f}%</strong>"
                f"</div>",
                unsafe_allow_html=True
            )
