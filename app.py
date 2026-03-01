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
