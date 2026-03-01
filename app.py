import streamlit as st
import os
import math
import base64
import json

CONFIG_FILE = "configs.json"

# =========================================================
# CONFIGS (PRESETS + FAVORITOS)
# =========================================================
def carregar_configs():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {
        "presets": {
            "Conservador": {},
            "Moderado": {},
            "Agressivo": {}
        },
        "favoritos": {}
    }

def salvar_configs(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)

configs = carregar_configs()

# =========================================================
# PÁGINA
# =========================================================
st.set_page_config(page_title="Vortex Bet", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@200;300;400&display=swap');
.stApp { background:#000; color:#fff; font-family:Inter; }
.header { text-align:center; margin-top:40px; }
.header h1 { font-weight:200; margin:0; }
.header p { color:#9A9A9A; margin-top:6px; }
.section { margin-top:48px; }
.calc-title { font-size:20px; font-weight:300; margin-bottom:12px; }
.pat-box {
  margin-top:14px; padding:12px;
  border:1px solid #222; border-radius:8px; background:#0E0E0E;
}
.soft { font-size:13px; color:#9A9A9A; margin-top:6px; }
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

st.markdown("""
<div class="header">
  <h1>Vortex Bet</h1>
  <p>Vortex Bet Hunter</p>
</div>
""", unsafe_allow_html=True)

# =========================================================
# CONFIGURAÇÕES (PRESETS / FAVORITOS)
# =========================================================
st.markdown("### ⚙️ Configurações")

opcoes = (
    ["Preset: Conservador", "Preset: Moderado", "Preset: Agressivo"]
    + [f"Favorito: {k}" for k in configs["favoritos"]]
)

sel = st.selectbox("Carregar configuração", ["—"] + opcoes)

if sel != "—":
    tipo, nome = sel.split(": ", 1)
    origem = "presets" if tipo == "Preset" else "favoritos"
    for k, v in configs[origem].get(nome, {}).items():
        st.session_state[k] = v

# =========================================================
# CÁLCULO DO OBJETIVO
# =========================================================
st.markdown('<div class="section-spacing"></div>', unsafe_allow_html=True)
st.markdown("<div class='calc-title'>🎯 Cálculo do Objetivo</div>", unsafe_allow_html=True)

modo = st.selectbox(
    "Qual variável deseja calcular?",
    ["Bilhetes", "Valor da UR", "Odd", "Objetivo Final"],
    key="modo"
)

valor_ur = odd = objetivo = bilhetes = None

if modo != "Valor da UR":
    valor_ur = st.number_input("Valor da UR (R$)", min_value=1, value=100, key="valor_ur")

if modo != "Odd":
    odd = st.number_input("Odd", min_value=1.01, step=0.01, value=1.33, key="odd")

if modo != "Objetivo Final":
    objetivo = st.number_input("Objetivo (R$)", min_value=1, value=1000, key="objetivo")

if modo != "Bilhetes":
    bilhetes = st.number_input("Quantidade de Bilhetes", min_value=1, value=10, key="bilhetes")

# =========================================================
# PATAMAR (somente quando faz sentido)
# =========================================================
ativar_patamar = False
pat_min = pat_max = None

if modo != "Valor da UR":
    ativar_patamar = st.checkbox(
        "Ativar geração de UR filhote (patamar)",
        key="ativar_patamar"
    )

    if ativar_patamar:
        pat_min, pat_max = st.slider(
            "Intervalo de patamar (×UR)",
            min_value=2,
            max_value=5,
            value=(3, 3),
            step=1,
            key="patamar_intervalo"
        )

# =========================================================
# CÁLCULO
# =========================================================
calculado = False

if st.button("Calcular", key="btn_calcular"):

    calculado = True

    # ---------------- RESULTADO BASE ----------------
    if modo == "Bilhetes":
        n = math.log(objetivo / valor_ur) / math.log(odd)
        bil = math.ceil(n)
        resultado_bruto = valor_ur * (odd ** bil)

        st.success(f"Bilhetes necessários: **{bil}**")
        comentario_base = "Número de repetições necessárias para atingir o objetivo."

    elif modo == "Valor da UR":
        ur = objetivo / (odd ** bilhetes)
        resultado_bruto = objetivo

        st.success(f"Valor da UR necessário: **R$ {ur:.2f}**")
        comentario_base = "Valor unitário necessário por tentativa."

    elif modo == "Odd":
        o = (objetivo / valor_ur) ** (1 / bilhetes)
        resultado_bruto = objetivo

        st.success(f"Odd necessária: **{o:.4f}**")
        comentario_base = "Dificuldade mínima do evento para alcançar o objetivo."

    elif modo == "Objetivo Final":
        resultado_bruto = valor_ur * (odd ** bilhetes)

        st.success(f"Resultado bruto: **R$ {resultado_bruto:.2f}**")
        comentario_base = "Resultado total antes de qualquer proteção."

    st.markdown(
        f"<div class='soft-validation'>{comentario_base}</div>",
        unsafe_allow_html=True
    )

    # ---------------- PATAMARES ----------------
    if ativar_patamar:
        st.markdown("")

        for pat in range(pat_min, pat_max + 1):
            valor_patamar = valor_ur * pat
            urs = int(resultado_bruto // valor_patamar)
            protegido = urs * valor_ur
            em_risco = resultado_bruto - protegido
            pct = (protegido / resultado_bruto) * 100 if resultado_bruto > 0 else 0

            if pat == pat_min:
                comentario = "Proteção mais frequente, com menor capital exposto."
            elif pat == pat_max:
                comentario = "Proteção mais espaçada, priorizando crescimento."
            else:
                comentario = "Equilíbrio intermediário entre proteção e crescimento."

            st.markdown(
                f"<div class='patamar-box'>"
                f"<strong>Patamar {pat}× UR</strong><br>"
                f"URs filhotes: <strong>{urs}</strong><br>"
                f"Capital protegido: <strong>R$ {protegido:.2f}</strong><br>"
                f"Resultado em risco: <strong>R$ {em_risco:.2f}</strong><br>"
                f"% protegido: <strong>{pct:.1f}%</strong><br>"
                f"<span class='soft-validation'>{comentario}</span>"
                f"</div>",
                unsafe_allow_html=True
            )

# =========================================================
# SALVAR CONFIGURAÇÃO (APENAS APÓS RESULTADOS)
# =========================================================
if calculado:

    st.markdown("")
    st.markdown("### 💾 Salvar configuração")

    nome_fav = st.text_input("Nome da configuração", key="nome_favorito")

    if st.button("Salvar configuração", key="btn_salvar"):

        configs["favoritos"][nome_fav] = {
            "modo": modo,
            "valor_ur": valor_ur,
            "odd": odd,
            "objetivo": objetivo,
            "bilhetes": bilhetes,
            "ativar_patamar": ativar_patamar,
            "patamar": (pat_min, pat_max) if ativar_patamar else None
        }

        salvar_configs(configs)
        st.success("Configuração salva com sucesso.")
# 
