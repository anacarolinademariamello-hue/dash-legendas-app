from __future__ import annotations

import streamlit as st

from src.styles import (
    get_sidebar_css,
    get_main_css,
    get_page_header_html,
    get_sidebar_welcome_html,
)
from src.clients import load_clients, load_latest_organic_metrics
from src.captions_db import (
    load_history,
    load_approved,
    save_caption,
    update_status,
    delete_caption,
)
from src.caption_gen import (
    generate_caption,
    FORMATOS,
    OBJETIVOS,
    PILARES,
    CTAS,
)

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Gerador de Legendas · Dash Digital",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(f"<style>{get_sidebar_css()}{get_main_css()}</style>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(
        '<div style="text-align:center;padding:8px 0 20px;">'
        '<span style="font-size:1.6rem;">✍️</span>'
        '<div style="font-size:0.7rem;font-weight:700;letter-spacing:0.1em;'
        'text-transform:uppercase;color:rgba(255,255,255,0.45);margin-top:4px;">'
        'Gerador de Legendas</div></div>',
        unsafe_allow_html=True,
    )

    # ── Modo ──────────────────────────────────────────────────────────────────
    modo = st.radio(
        "Modo",
        ["Consulta avulsa", "Cliente cadastrado"],
        horizontal=False,
        key="modo",
        label_visibility="collapsed",
    )

    # Limpa campos ao trocar para avulso
    if st.session_state.get("_last_modo") != modo:
        if modo == "Consulta avulsa":
            for k in ("criativo_texto", "client_observations"):
                if st.session_state.get(k):
                    st.session_state[k] = ""
        st.session_state["_last_modo"] = modo

    selected_client = None

    if modo == "Cliente cadastrado":
        all_clients = load_clients()
        if all_clients:
            names = [c["name"] for c in all_clients]
            chosen = st.selectbox(
                "Cliente",
                names,
                label_visibility="collapsed",
                key="chosen_client",
            )
            selected_client = next((c for c in all_clients if c["name"] == chosen), None)
        else:
            st.info("Nenhum cliente cadastrado.")

    # ── Painel do cliente selecionado ────────────────────────────────────────
    if selected_client:
        has_tov  = bool(selected_client.get("tone_of_voice", "").strip())
        ck       = selected_client.get("key", "")
        metrics  = load_latest_organic_metrics(ck) if ck else ""
        approved = load_approved(ck) if ck else []

        tov_color  = "rgba(16,185,129,0.18)"  if has_tov else "rgba(245,158,11,0.15)"
        tov_text   = "#6ee7b7"               if has_tov else "#fcd34d"
        tov_border = "rgba(16,185,129,0.35)" if has_tov else "rgba(245,158,11,0.3)"
        tov_label  = "Tom de voz ✓" if has_tov else "Sem tom de voz"
        met_color  = "rgba(16,185,129,0.18)"  if metrics else "rgba(245,158,11,0.15)"
        met_text   = "#6ee7b7"               if metrics else "#fcd34d"
        met_border = "rgba(16,185,129,0.35)" if metrics else "rgba(245,158,11,0.3)"
        met_label  = f"Relatório ✓ ({len(approved)} aprovadas)" if metrics else "Sem relatório"

        st.markdown(
            f'<div style="display:flex;gap:6px;flex-wrap:wrap;margin:8px 0 14px;">'
            f'<span style="background:{tov_color};color:{tov_text};border:1px solid {tov_border};'
            f'font-size:.68rem;font-weight:700;padding:3px 10px;border-radius:20px;">{tov_label}</span>'
            f'<span style="background:{met_color};color:{met_text};border:1px solid {met_border};'
            f'font-size:.68rem;font-weight:700;padding:3px 10px;border-radius:20px;">{met_label}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

    # ── Histórico recente na sidebar ─────────────────────────────────────────
    if selected_client:
        ck = selected_client.get("key", "")
        recent = load_history(client_key=ck, limit=5)
    else:
        recent = []

    if recent:
        st.markdown(
            '<div style="font-size:.65rem;font-weight:700;letter-spacing:.1em;'
            'text-transform:uppercase;color:rgba(255,255,255,.4);margin-bottom:10px;">'
            'Histórico recente</div>',
            unsafe_allow_html=True,
        )
        for h in recent[:4]:
            status = h.get("status", "pendente")
            dot = "🟢" if status == "aprovada" else ("🔴" if status == "rejeitada" else "⚪")
            tema = h.get("tema", "")[:30]
            st.markdown(
                f'<div style="font-size:.75rem;color:rgba(255,255,255,.7);'
                f'margin-bottom:6px;line-height:1.3;">'
                f'{dot} {tema}</div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown(get_sidebar_welcome_html(), unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(
        '<div style="font-size:.68rem;font-weight:700;color:rgba(255,255,255,.4);letter-spacing:.08em;margin-bottom:8px;">NAVEGAÇÃO</div>'
        '<a href="https://dash-painel.streamlit.app/" target="_blank" style="display:block;padding:7px 10px;border-radius:8px;text-decoration:none;color:rgba(255,255,255,.8);font-size:.82rem;background:rgba(255,255,255,.06);margin-bottom:4px;">📊 Painel de Clientes</a>'
        '<a href="https://anacarolinademariamello-hue.github.io/hub-dash/" target="_blank" style="display:block;padding:7px 10px;border-radius:8px;text-decoration:none;color:rgba(255,255,255,.8);font-size:.82rem;background:rgba(255,255,255,.06);">🏠 Central de Ferramentas</a>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(get_page_header_html(), unsafe_allow_html=True)

tab_gerar, tab_historico = st.tabs(["✍️ Gerar legenda", "📋 Histórico"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — GERAR
# ══════════════════════════════════════════════════════════════════════════════
with tab_gerar:

    col_form, col_output = st.columns([1, 1], gap="large")

    # ── COLUNA ESQUERDA — Formulário ─────────────────────────────────────────
    with col_form:

        # ── Seção 1: Dados do post ────────────────────────────────────────────
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<div class="form-section-title">📄 Sobre o post</div>', unsafe_allow_html=True)

        tema = st.text_input(
            "Tema / assunto do post *",
            placeholder="Ex: 3 erros que impedem você de emagrecer mesmo fazendo tudo certo",
            key="tema",
        )

        c1, c2 = st.columns(2)
        with c1:
            formato = st.selectbox("Formato", FORMATOS, key="formato")
        with c2:
            objetivo = st.selectbox("Objetivo", OBJETIVOS, key="objetivo")

        pilar = st.selectbox("Pilar de conteúdo", PILARES, key="pilar")

        cta_options = CTAS + ["Outro (digitar)"]
        cta_sel = st.selectbox("CTA desejado", cta_options, key="cta_sel")
        if cta_sel == "Outro (digitar)":
            cta = st.text_input("Digite o CTA", key="cta_custom", placeholder="Ex: Agenda uma consulta pelo link da bio")
        else:
            cta = cta_sel

        st.markdown('</div>', unsafe_allow_html=True)

        # ── Seção 2: Dados do cliente (só no modo avulso) ─────────────────────
        if modo == "Consulta avulsa":
            st.markdown('<div class="form-section">', unsafe_allow_html=True)
            st.markdown('<div class="form-section-title">👤 Sobre o criador</div>', unsafe_allow_html=True)

            av1, av2 = st.columns(2)
            with av1:
                nicho = st.text_input("Nicho", placeholder="Ex: Saúde e bem-estar", key="nicho_avulso")
            with av2:
                sub_nicho = st.text_input("Sub-nicho", placeholder="Ex: Nutrição esportiva", key="sub_nicho_avulso")

            publico_alvo = st.text_input(
                "Público-alvo",
                placeholder="Ex: Mulheres 25-40 anos que praticam musculação",
                key="publico_avulso",
            )
            tone_of_voice = st.text_area(
                "Tom de voz (opcional)",
                placeholder="Ex: Descontraído mas técnico, usa gírias leves, evita termos muito formais",
                height=70,
                key="tov_avulso",
            )
            client_handle = st.text_input(
                "@ do perfil (opcional — para hashtag de marca)",
                placeholder="@seuperfil",
                key="handle_avulso",
            )
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            nicho        = selected_client.get("nicho", "") if selected_client else ""
            sub_nicho    = selected_client.get("sub_nicho", "") if selected_client else ""
            publico_alvo = selected_client.get("publico_alvo", "") if selected_client else ""
            tone_of_voice = selected_client.get("tone_of_voice", "") if selected_client else ""
            client_handle = selected_client.get("handle", "") if selected_client else ""

        # ── Seção 3: Contexto do criativo ────────────────────────────────────
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<div class="form-section-title">🎨 Contexto do criativo</div>', unsafe_allow_html=True)

        tipo_criativo = st.radio(
            "Como você vai fornecer o criativo?",
            ["✏️ Colar texto / roteiro", "🖼️ Upload de imagem", "📝 Sem criativo (só o tema)"],
            horizontal=False,
            key="tipo_criativo",
            label_visibility="collapsed",
        )

        image_bytes      = None
        image_media_type = "image/jpeg"
        criativo_texto   = ""
        has_image        = False

        if tipo_criativo == "✏️ Colar texto / roteiro":
            criativo_texto = st.text_area(
                "Texto do criativo / roteiro / transcrição",
                placeholder=(
                    "Cole aqui o roteiro do vídeo, o texto que vai na imagem, "
                    "a transcrição da fala ou qualquer conteúdo que o criativo vai ter.\n\n"
                    "A legenda vai complementar e reforçar essa mensagem."
                ),
                height=160,
                key="criativo_texto",
            )

        elif tipo_criativo == "🖼️ Upload de imagem":
            st.caption("Suporte: JPG, PNG, WEBP. Máx. 5 MB. A IA analisa a imagem e cria uma legenda que complemente o visual.")
            uploaded = st.file_uploader(
                "Upload do criativo",
                type=["jpg", "jpeg", "png", "webp"],
                key="criativo_upload",
                label_visibility="collapsed",
            )
            if uploaded:
                raw_bytes = uploaded.read()
                if len(raw_bytes) > 5 * 1024 * 1024:
                    st.error("Imagem muito grande. Máximo: 5 MB.")
                else:
                    image_bytes      = raw_bytes
                    image_media_type = uploaded.type or "image/jpeg"
                    has_image        = True
                    st.image(uploaded, caption="Criativo enviado", use_container_width=True)
        else:
            st.caption("A IA vai gerar a legenda com base apenas no tema e nos dados do cliente.")

        st.markdown('</div>', unsafe_allow_html=True)

        # ── Botão gerar ───────────────────────────────────────────────────────
        gerar = st.button("✨ Gerar 3 variações de legenda", use_container_width=True, type="primary")

        if gerar:
            if not tema.strip():
                st.error("Preencha o Tema do post antes de gerar.")
            elif modo == "Consulta avulsa" and not nicho.strip():
                st.error("Preencha o Nicho antes de gerar.")
            else:
                # Monta form_data com todos os contextos
                ck       = selected_client.get("key", "") if selected_client else ""
                metrics  = load_latest_organic_metrics(ck) if ck else ""
                approved = load_approved(ck) if ck else []

                form_data = {
                    # Post
                    "tema":           tema.strip(),
                    "formato":        formato,
                    "objetivo":       objetivo,
                    "pilar":          pilar,
                    "cta":            cta,
                    # Cliente
                    "client_name":    selected_client["name"] if selected_client else "",
                    "client_key":     ck,
                    "client_bio":     selected_client.get("bio", "") if selected_client else "",
                    "client_tags":    selected_client.get("tags", []) if selected_client else [],
                    "client_handle":  client_handle,
                    # Nicho / voz
                    "nicho":          nicho,
                    "sub_nicho":      sub_nicho,
                    "publico_alvo":   publico_alvo,
                    "tone_of_voice":  tone_of_voice,
                    # Criativo
                    "criativo_texto": criativo_texto.strip() if criativo_texto else "",
                    "has_image":      has_image,
                    # IA context
                    "organic_metrics":  metrics,
                    "approved_history": approved,
                }

                with st.spinner("Gerando legendas com IA..."):
                    try:
                        variacoes = generate_caption(
                            form_data,
                            image_bytes=image_bytes,
                            image_media_type=image_media_type,
                        )
                        st.session_state["variacoes"]  = variacoes
                        st.session_state["form_data"]  = form_data
                        # Limpa status da sessão anterior
                        for j in range(1, 4):
                            st.session_state.pop(f"status_var_{j}", None)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao gerar: {e}")

    # ── COLUNA DIREITA — Output ───────────────────────────────────────────────
    with col_output:
        variacoes = st.session_state.get("variacoes", [])
        fd        = st.session_state.get("form_data", {})

        if not variacoes:
            st.markdown(
                '<div style="background:#f8fafc;border:1px dashed #dde3ed;border-radius:16px;'
                'padding:48px 24px;text-align:center;color:#9ca3af;">'
                '<div style="font-size:2rem;margin-bottom:12px;">✍️</div>'
                '<div style="font-size:0.9rem;font-weight:600;">As legendas geradas aparecem aqui</div>'
                '<div style="font-size:0.8rem;margin-top:6px;">Preencha o formulário ao lado e clique em Gerar</div>'
                '</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div style="font-size:.7rem;font-weight:700;text-transform:uppercase;'
                f'letter-spacing:.1em;color:#9ca3af;margin-bottom:16px;">'
                f'3 variações para: {fd.get("tema","")[:60]}</div>',
                unsafe_allow_html=True,
            )

            for v in variacoes:
                vid       = v.get("id", 1)
                abordagem = v.get("abordagem", f"Variação {vid}")
                hook      = v.get("hook", "")
                body      = v.get("body", "")
                cta_text  = v.get("cta", "")
                hashtags  = v.get("hashtags", [])
                legenda   = v.get("legenda_completa", f"{hook}\n\n{body}\n\n{cta_text}\n\n{' '.join(hashtags)}")
                score     = v.get("hook_score", "")
                status_key = f"status_var_{vid}"

                st.markdown(f'<div class="caption-card caption-card-{vid}">', unsafe_allow_html=True)
                st.markdown(f'<div class="caption-abordagem">Variação {vid} — {abordagem}</div>', unsafe_allow_html=True)

                if hook:
                    st.markdown(f'<div class="caption-hook">"{hook}"</div>', unsafe_allow_html=True)
                if score:
                    st.markdown(f'<div class="caption-score">🎯 Hook: {score}</div>', unsafe_allow_html=True)

                # Legenda completa com copy automático via st.code
                st.code(legenda, language=None)

                # Hashtags como chips
                if hashtags:
                    chips_html = '<div class="caption-hashtags">'
                    for tag in hashtags:
                        chips_html += f'<span class="hashtag-chip">{tag}</span>'
                    chips_html += '</div>'
                    st.markdown(chips_html, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # Botões aprovar / rejeitar
                current_status = st.session_state.get(status_key)
                if current_status:
                    badge_class = "badge-aprovada" if current_status == "aprovada" else "badge-rejeitada"
                    label = "APROVADA ✓" if current_status == "aprovada" else "REJEITADA ✗"
                    st.markdown(
                        f'<span class="{badge_class}">{label}</span>',
                        unsafe_allow_html=True,
                    )
                else:
                    ba, br = st.columns(2)
                    with ba:
                        if st.button("✅ Aprovar", key=f"apr_{vid}", use_container_width=True):
                            ok, msg = save_caption(fd, v, status="aprovada")
                            if ok:
                                st.session_state[status_key] = "aprovada"
                                load_history.clear()
                                load_approved.clear()
                                st.rerun()
                            else:
                                st.error(msg)
                    with br:
                        if st.button("❌ Rejeitar", key=f"rej_{vid}", use_container_width=True):
                            ok, msg = save_caption(fd, v, status="rejeitada")
                            if ok:
                                st.session_state[status_key] = "rejeitada"
                                load_history.clear()
                                load_approved.clear()
                                st.rerun()
                            else:
                                st.error(msg)

                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

            # Botão gerar novamente
            if st.button("🔄 Gerar novamente com os mesmos dados", use_container_width=True):
                with st.spinner("Gerando..."):
                    try:
                        variacoes_novas = generate_caption(fd)
                        st.session_state["variacoes"] = variacoes_novas
                        for j in range(1, 4):
                            st.session_state.pop(f"status_var_{j}", None)
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — HISTÓRICO
# ══════════════════════════════════════════════════════════════════════════════
with tab_historico:

    # Filtros
    hf1, hf2, hf3 = st.columns(3)
    with hf1:
        filtro_status = st.selectbox(
            "Status",
            ["Todos", "aprovada", "rejeitada", "pendente"],
            key="hist_status",
        )
    with hf2:
        filtro_formato = st.selectbox(
            "Formato",
            ["Todos"] + FORMATOS,
            key="hist_formato",
        )
    with hf3:
        filtro_cliente = st.text_input("Filtrar por cliente", key="hist_cliente", placeholder="Nome do cliente")

    ck_hist = selected_client.get("key", "") if selected_client else ""
    status_hist = "" if filtro_status == "Todos" else filtro_status
    historico = load_history(client_key=ck_hist, status=status_hist, limit=50)

    # Filtros adicionais client-side
    if filtro_formato != "Todos":
        historico = [h for h in historico if h.get("formato") == filtro_formato]
    if filtro_cliente.strip():
        historico = [h for h in historico if filtro_cliente.lower() in (h.get("client_name") or "").lower()]

    if not historico:
        st.info("Nenhuma legenda encontrada com os filtros selecionados.")
    else:
        aprov  = sum(1 for h in historico if h.get("status") == "aprovada")
        rejeit = sum(1 for h in historico if h.get("status") == "rejeitada")
        st.markdown(
            f'<div style="display:flex;gap:12px;margin-bottom:20px;">'
            f'<span style="background:#d1fae5;color:#065f46;font-size:.75rem;font-weight:700;'
            f'padding:4px 12px;border-radius:20px;">✅ {aprov} aprovadas</span>'
            f'<span style="background:#fee2e2;color:#991b1b;font-size:.75rem;font-weight:700;'
            f'padding:4px 12px;border-radius:20px;">❌ {rejeit} rejeitadas</span>'
            f'<span style="background:#f3f4f6;color:#6b7280;font-size:.75rem;font-weight:700;'
            f'padding:4px 12px;border-radius:20px;">📋 {len(historico)} total</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        for h in historico:
            status   = h.get("status", "pendente")
            tema_h   = h.get("tema", "Sem tema")[:50]
            formato_h = h.get("formato", "")
            abord_h  = h.get("abordagem", "")
            client_h = h.get("client_name", "Avulso")
            data_h   = (h.get("created_at") or "")[:10]
            dot      = "🟢" if status == "aprovada" else ("🔴" if status == "rejeitada" else "⚪")

            with st.expander(
                f"{dot} **{tema_h}** · {formato_h} · {abord_h} · {client_h} · {data_h}",
                expanded=False,
            ):
                legenda_h = h.get("legenda_completa", "")
                if legenda_h:
                    st.code(legenda_h, language=None)

                hook_h = h.get("hook", "")
                score_h = h.get("hook_score", "")
                if hook_h:
                    st.markdown(f'**Hook:** {hook_h}')
                if score_h:
                    st.markdown(f'🎯 {score_h}')

                hashtags_h = h.get("hashtags", "")
                if hashtags_h:
                    chips = "".join(
                        f'<span class="hashtag-chip">{t}</span>'
                        for t in hashtags_h.split()
                    )
                    st.markdown(f'<div class="caption-hashtags">{chips}</div>', unsafe_allow_html=True)

                # Ações
                hid = h.get("id")
                ha1, ha2, ha3 = st.columns(3)
                with ha1:
                    if status != "aprovada":
                        if st.button("✅ Marcar aprovada", key=f"h_apr_{hid}", use_container_width=True):
                            update_status(hid, "aprovada")
                            st.rerun()
                with ha2:
                    if status != "rejeitada":
                        if st.button("❌ Marcar rejeitada", key=f"h_rej_{hid}", use_container_width=True):
                            update_status(hid, "rejeitada")
                            st.rerun()
                with ha3:
                    if st.button("🗑️ Excluir", key=f"h_del_{hid}", use_container_width=True):
                        delete_caption(hid)
                        st.rerun()
