import streamlit as st
import os
import math
import base64
import json

CONFIG_FILE = "configs.json"

# =========================================================
# CONFIGURAÇÕES SALVAS
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
# CONFIGURAÇÃO DA PÁGINA
# =========================================================
st.set_page_config(page_title="Vortex Bet", layout="centered")

# =========================================================
# CSS
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@200;300;400&display=swap');
.stApp {
    background-color: #000;
    color: #fff;
    font-family: 'Inter', sans-serif;
}
.soft { color:#9A9A9A; font-size:13px; }
.box { border:1px solid #222; padding:12px; border-radius:8px; background:#0E0E0E; margin-top:10px; }
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

st.markdown("<h2 style='text-align:center;font-weight:200'>Vortex Bet</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#9A9A9A'>Vortex Bet Hunter</p>", unsafe_allow_html=True)

# =========================================================
# CONFIGURAÇÕES (PRESETS + FAVORITOS)
# =========================================================
st.markdown("### ⚙️ Configurações")

opcoes = (
    ["Preset: Conservador", "Preset: Moderado", "Preset: Agressivo"]
    + [f"Favorito: {k}" for k in configs["favoritos"].keys()]
)

selecionado = st.selectbox("Carregar configuração", ["—"] + opcoes)

if selecionado != "—":
    tipo, nome = selecionado.split(": ", 1)
    origem = "presets" if tipo == "Preset" else "favoritos"
    dados = configs[origem].get(nome, {})
    for k, v in dados.items():
        st.session_state[k] = v

# =========================================================
# CÁLCULO DO OBJETIVO
# =========================================================
st.markdown("### 🎯 Cálculo do Objetivo")

modo = st.selectbox(
    "Qual variável deseja calcular?",
    ["Bilhetes", "Valor da UR", "Odd", "Objetivo Final"],
    key="modo"
)

valor_ur = st.number_input("Valor da UR (R$)", min_value=1, value=st.session_state.get("valor_ur", 100))
odd = st.number_input("Odd", min_value=1.01, step=0.01, value=st.session_state.get("odd", 1.25))
objetivo = st.number_input("Objetivo (R$)", min_value=1, value=st.session_state.get("objetivo", 1000))
bilhetes = st.number_input("Quantidade de Bilhetes", min_value=1, value=st.session_state.get("bilhetes", 10))

# =========================================================
# PATAMAR
# =========================================================
ativar_patamar = st.checkbox("Ativar geração de UR filhote", value=st.session_state.get("ativar_patamar", False))

if ativar_patamar:
    pat_min, pat_max = st.slider(
        "Intervalo de patamar (×UR)",
        2, 5,
        st.session_state.get("patamar", (3, 3))
    )

# =========================================================
# SALVAR FAVORITO
# =========================================================
with st.expander("💾 Salvar configuração"):
    nome_fav = st.text_input("Nome do favorito")
    if st.button("Salvar"):
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
        st.success("Favorito salvo")

# =========================================================
# CÁLCULO
# =========================================================
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
        st.success(f"Objetivo atingido: R$ {obj:.2f}")
