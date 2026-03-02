import streamlit as st
import os
import math
import base64

# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================
st.set_page_config(page_title="Vortex Bet", layout="centered")

# =========================================================
# CSS
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@200;300;400;600&display=swap');

.stApp {
    background-color: #000;
    color: #FFF;
    font-family: 'Inter', sans-serif;
}

.header-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 40px;
    text-align: center;
}

.header-title {
    font-size: 30px;
    font-weight: 200;
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
    font-weight: 600;
    margin-bottom: 12px;
}

.soft-validation {
    font-size: 12px;
    color: #9A9A9A;
    margin-top: 4px;
}

.patamar-container {
    display: flex;
    gap: 14px;
    margin-top: 12px;
}

.patamar-box {
    flex: 1;
    padding: 12px;
    border: 1px solid #222;
    border-radius: 8px;
    background-color: #0E0E0E;
    font-size: 12px;
    color: #B0B0B0;
    margin-bottom: 12px;
}
.valor {
    color: #FFFFFF;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# LOGO
# =========================================================
def mostrar_logo(caminho, largura=140):
    with open(caminho, "rb") as f:
        img = base64.b64encode(f.read()).decode()
    st.markdown(
        f"<div style='display:flex;justify-content:center;'>"
        f"<img src='data:image/png;base64,{img}' width='{largura}'>"
        f"</div>",
        unsafe_allow_html=True
    )

if os.path.exists("logo_vortex.png"):
    mostrar_logo("logo_vortex.png")

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
# NÚCLEO MATEMÁTICO (EXTRAÇÃO – PONTO 3)
# =========================================================
def calc_bilhetes(valor_ur, odd, objetivo):
    n = math.log(objetivo / valor_ur) / math.log(odd)
    bil = math.ceil(n)
    resultado = valor_ur * (odd ** bil)
    return bil, resultado, "Número de repetições necessárias para atingir o objetivo."

def calc_ur(odd, bilhetes, objetivo):
    ur = objetivo / (odd ** bilhetes)
    return ur, objetivo, "Valor unitário necessário por tentativa."

def calc_odd(valor_ur, bilhetes, objetivo):
    o = (objetivo / valor_ur) ** (1 / bilhetes)
    return o, objetivo, "Dificuldade mínima do evento para alcançar o objetivo."

def calc_resultado(valor_ur, odd, bilhetes):
    resultado = valor_ur * (odd ** bilhetes)
    return resultado, "Resultado total antes de qualquer proteção."

# =========================================================
# NOVO MOTOR DE PATAMAR (MODELO B - DINÂMICO POR ESTÁGIOS)
# =========================================================
def simular_patamar_modelo_b(valor_ur_base, odd, bilhetes, patamar):
    """
    MODELO B (conforme sua operação real):
    - All-in por bilhete (WIN => saldo *= odd; LOSS => saldo = 0). Aqui é PROJEÇÃO: assume WIN em todos os bilhetes.
    - Patamar fixo (2x, 3x, 4x ou 5x): define de quantas em quantas vezes a UR_base ocorre uma retirada.
    - Estágios / níveis do patamar:
        step = patamar * UR_base
        níveis em: step, 2*step, 3*step, ...
      Cada vez que o saldo bruto cruza um novo nível ainda não executado, retira 1*UR_base (UMA VEZ POR NÍVEL).
    """
    saldo = float(valor_ur_base)
    ur_base = float(valor_ur_base)
    odd = float(odd)
    bilhetes = int(bilhetes)
    patamar = int(patamar)

    step = patamar * ur_base
    nivel_atual = 0  # quantos níveis (k) já foram "executados"
    total_sacado = 0.0
    total_saques_eventos = 0  # número de saques (quantos níveis novos executados ao longo dos bilhetes)

    # Histórico opcional (útil caso queira expandir UI depois)
    historico = []

    for i in range(1, bilhetes + 1):
        saldo_inicial = saldo

        # Projeção assume WIN (resultado total por bilhete)
        saldo_bruto = saldo_inicial * odd

        # Quantos níveis (k) o saldo bruto atinge?
        k_max = int(saldo_bruto // step) if step > 0 else 0

        # Níveis novos atingidos desde o último estado
        novos = max(0, k_max - nivel_atual)

        # Saque deste bilhete
        valor_sacado = novos * ur_base

        # Aplica saque (não deixa negativo)
        saldo_final = max(0.0, saldo_bruto - valor_sacado)

        # Atualiza acumuladores
        total_sacado += valor_sacado
        total_saques_eventos += novos
        nivel_atual += novos
        saldo = saldo_final

        historico.append({
            "Bilhete": i,
            "Saldo Inicial": saldo_inicial,
            "Odd": odd,
            "Saldo Bruto": saldo_bruto,
            "Novos Níveis": novos,
            "Saque": valor_sacado,
            "Saldo Final": saldo_final,
            "Nível Atual": nivel_atual
        })

        # Se zerar (em projeção isso não ocorre, pois sempre WIN), mas mantemos a lógica robusta
        if saldo <= 0:
            break

    return saldo, total_sacado, total_saques_eventos, nivel_atual, historico

def calc_patamares(valor_ur, odd, bilhetes, pat_min, pat_max):
    """
    Substitui a lógica anterior (estática) por MODELO B (dinâmico por estágios).
    Retorna, para cada patamar dentro do intervalo, um resumo compatível com a UI existente:
    - pat
    - urs (aqui: número total de retiradas / "URs filhotes" executadas)
    - protegido (total sacado)
    - risco (saldo final projetado após todas as retiradas)
    - pct (percentual protegido vs total final = (sacado + saldo final))
    - comentario
    """
    patamares = []
    for pat in range(pat_min, pat_max + 1):
        saldo_final, total_sacado, total_saques_eventos, nivel_atual, _hist = simular_patamar_modelo_b(
            valor_ur_base=valor_ur,
            odd=odd,
            bilhetes=bilhetes,
            patamar=pat
        )

        protegido = total_sacado
        risco = saldo_final
        total = protegido + risco
        pct = (protegido / total) * 100 if total else 0

        if pat == pat_min:
            comentario = "Proteção mais frequente (retira a cada menos múltiplos da UR)."
        elif pat == pat_max:
            comentario = "Proteção mais espaçada (prioriza crescimento antes de retirar)."
        else:
            comentario = "Equilíbrio intermediário entre proteção e crescimento."

        # 'urs' na UI original era "URs filhotes". No MODELO B, isso vira:
        # quantidade de retiradas executadas (cada retirada = 1 UR_base).
        urs = int(total_saques_eventos)

        patamares.append((pat, urs, protegido, risco, pct, comentario))

    return patamares

# =========================================================
# UI – CÁLCULO
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

ativar_patamar = False
pat_min = pat_max = None

if modo != "Valor da UR":
    ativar_patamar = st.checkbox("Ativar geração de UR filhote (patamar)")
    if ativar_patamar:
        pat_min, pat_max = st.slider(
            "Intervalo de patamar (×UR)",
            min_value=2,
            max_value=5,
            value=(3, 3),
            step=1
        )

if st.button("Calcular"):

    # Guardas para usar os valores "efetivos" (principalmente no modo Odd, onde odd é calculada)
    odd_efetiva = odd
    valor_ur_efetiva = valor_ur
    bilhetes_efetivo = bilhetes

    if modo == "Bilhetes":
        bil, resultado, comentario = calc_bilhetes(valor_ur, odd, objetivo)
        st.success(f"Bilhetes necessários: **{bil}**")
        bilhetes_efetivo = bil  # para usar no patamar dinâmico (MODELO B)

    elif modo == "Valor da UR":
        ur, resultado, comentario = calc_ur(odd, bilhetes, objetivo)
        st.success(f"Valor da UR necessário: **R$ {ur:.2f}**")
        # patamar não aparece neste modo (mantido como no original)

    elif modo == "Odd":
        o, resultado, comentario = calc_odd(valor_ur, bilhetes, objetivo)
        st.success(f"Odd necessária: **{o:.4f}**")
        odd_efetiva = o  # importante: odd "efetiva" para o patamar dinâmico

    else:
        resultado, comentario = calc_resultado(valor_ur, odd, bilhetes)
        st.success(f"Resultado bruto: **R$ {resultado:.2f}**")

    st.markdown(f"<div class='soft-validation'>{comentario}</div>", unsafe_allow_html=True)

    # =========================================================
    # PATAMAR (MODELO B) - usa odd_efetiva e bilhetes_efetivo
    # =========================================================
    if ativar_patamar:
        # Para o MODELO B, precisamos simular bilhete a bilhete.
        # Isso exige: valor_ur (UR_base), odd (efetiva), bilhetes (efetivo).
        # Se algo estiver None por causa do modo, não calcula (fallback robusto).
        if valor_ur_efetiva is None or odd_efetiva is None or bilhetes_efetivo is None:
            st.warning("Não foi possível calcular o patamar com os valores atuais.")
        else:
            st.markdown("<div class='patamar-container'>", unsafe_allow_html=True)
            for pat, urs, protegido, risco, pct, comentario_pat in calc_patamares(
                valor_ur_efetiva, odd_efetiva, bilhetes_efetivo, pat_min, pat_max
            ):
                st.markdown(
                    f"<div class='patamar-box'>"
                    f"<strong>Patamar {pat}× UR</strong><br>"
                    f"URs filhotes (retiradas): <span class='valor'>{urs}</span><br>"
                    f"Capital protegido (sacado): <span class='valor'>R$ {protegido:.2f}</span><br>"
                    f"Saldo final em risco: <span class='valor'>R$ {risco:.2f}</span><br>"
                    f"% protegido (sacado / (sacado + saldo)): <span class='valor'>{pct:.1f}%</span><br>"
                    f"<span class='soft-validation'>{comentario_pat}</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )
            st.markdown("</div>", unsafe_allow_html=True)
