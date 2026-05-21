from __future__ import annotations

import json
import re
import base64
import anthropic
import streamlit as st

FORMATOS = ["Reels", "Carrossel", "Post Feed", "Stories"]

OBJETIVOS = [
    "Engajar",
    "Educar",
    "Inspirar",
    "Vender",
    "Entreter",
    "Viralizar",
    "Construir Autoridade",
    "Bastidores",
]

PILARES = [
    "Educação",
    "Entretenimento",
    "Autoridade",
    "Engajamento",
    "Inspiração",
    "Bastidores",
    "Vendas Orgânicas",
]

CTAS = [
    "Salva esse post!",
    "Comenta aqui embaixo",
    "Manda pra quem precisa ver isso",
    "Segue pra mais conteúdo assim",
    "Clica no link da bio",
    "Me manda uma mensagem",
    "Compartilha nos seus Stories",
    "Marca alguém que precisa ver",
    "Responde aqui nos comentários",
]


def _build_prompt(form: dict) -> str:
    # ── Bloco do cliente / briefing ───────────────────────────────────────────
    if form.get("client_name"):
        client_block = f"""
## CLIENTE
- **Nome:** {form['client_name']}
- **Nicho:** {form.get('nicho', '')} › {form.get('sub_nicho', '')}
- **Público-alvo:** {form.get('publico_alvo', 'Não definido')}
- **Descrição do perfil:** {form.get('client_bio', '')}
"""
        if form.get("tone_of_voice"):
            client_block += f"- **Tom de voz:** {form['tone_of_voice']}\n"
        if form.get("client_handle"):
            client_block += f"- **Handle Instagram:** @{form['client_handle'].lstrip('@')}\n"
        tags = form.get("client_tags", [])
        if tags:
            client_block += f"- **Áreas:** {', '.join(tags)}\n"
    else:
        client_block = f"""
## BRIEFING
- **Nicho:** {form.get('nicho', '')} › {form.get('sub_nicho', '')}
- **Público-alvo:** {form.get('publico_alvo', 'Não definido')}
- **Tom de voz:** {form.get('tone_of_voice', 'Direto e humano')}
"""

    # ── Contexto do criativo ──────────────────────────────────────────────────
    if form.get("criativo_texto"):
        criativo_block = f"""
## TEXTO DO CRIATIVO / ROTEIRO
{form['criativo_texto']}

→ A legenda deve COMPLEMENTAR esse conteúdo — reforçar a mensagem, ampliar o contexto ou criar curiosidade. Não repita o roteiro palavra por palavra.
"""
    elif form.get("has_image"):
        criativo_block = """
## CRIATIVO VISUAL
Analise a imagem anexada. Crie uma legenda que COMPLEMENTE a imagem — não descreva-a, mas amplifique a mensagem que ela transmite. O texto e a imagem juntos devem ser mais poderosos do que separados.
"""
    else:
        criativo_block = ""

    # ── Métricas orgânicas ────────────────────────────────────────────────────
    metrics_block = (
        f"\n## DADOS DE PERFORMANCE DO CLIENTE\n{form['organic_metrics']}\n"
        if form.get("organic_metrics") else ""
    )

    # ── Histórico aprovado ────────────────────────────────────────────────────
    history_block = ""
    approved = form.get("approved_history", [])
    if approved:
        history_block = "\n## LEGENDAS ANTERIORES APROVADAS (referência de voz e estilo)\n"
        for i, h in enumerate(approved[:5], 1):
            history_block += (
                f"\n**Exemplo {i} · {h.get('formato','')} · {h.get('abordagem','')}:**\n"
                f"{str(h.get('legenda_completa',''))[:280]}\n---\n"
            )
        history_block += "→ Mantenha coerência de voz com esses exemplos aprovados.\n"

    # ── Prompt final ──────────────────────────────────────────────────────────
    tom = form.get("tone_of_voice") or "direto, humano e sem exageros"
    handle = form.get("client_handle", "").lstrip("@")
    branded_hint = (
        f"Inclua 1-2 hashtags da marca: #{handle.replace('.','').replace('_','')} se fizer sentido"
        if handle else "Sem hashtag de marca (cliente avulso)"
    )

    prompt = f"""Você é um copywriter sênior especializado em legendas para Instagram no mercado brasileiro. \
Sua especialidade é criar textos que param o scroll na primeira frase, constroem autoridade e geram ação real — nunca genéricos, nunca robotizados.

⚠️ RESTRIÇÃO ABSOLUTA antes de começar:
JAMAIS use o padrão negação + afirmação redefinidora: "Não é X. É Y.", "Não foi sorte. Foi método.", etc. \
Se a segunda frase curta corrige ou redefine a primeira frase curta, é essa estrutura proibida. Não use em nenhuma das 3 variações.
{client_block}
## POST A LEGENDAR
- **Formato:** {form['formato']}
- **Objetivo:** {form['objetivo']}
- **Pilar de conteúdo:** {form['pilar']}
- **Tema:** {form['tema']}
- **CTA desejado:** {form['cta']}
{criativo_block}{metrics_block}{history_block}
## SUA TAREFA

Gere EXATAMENTE 3 variações de legenda, cada uma com abordagem distinta:
1. **Direta** — vai ao ponto imediatamente, sem setup
2. **Narrativa** — abre com uma situação, microhistória ou dado específico
3. **Provocadora** — começa com uma afirmação ousada, contra-intuitiva ou que desafia o senso comum

## REGRAS OBRIGATÓRIAS

**Hook (primeira linha — elemento mais crítico):**
- Máximo 10 palavras
- Sem saudações: "Olá!", "Oi, pessoal!", "Bom dia" — PROIBIDO
- Sem emojis na primeira linha
- Deve funcionar SOZINHO como isca — quem lê o hook deve querer ler mais
- Proibido: "Você sabia que...", "Hoje vou falar sobre...", "Nesse post eu..."
- Proibido: padrão "Não é X. É Y." e variações

**Corpo:**
- Parágrafos curtos (máximo 2-3 linhas cada)
- Use \\n\\n entre parágrafos — espaçamento real
- Tom: {tom}
- Máximo 120 palavras no corpo (sem hook e sem CTA)
- Vá direto — sem introdução, sem "No post de hoje..."

**CTA (última linha):**
- Separado do corpo por \\n\\n
- Variação natural de: "{form['cta']}" — adapte ao contexto de cada variação
- Sem ponto final
- Direto e específico — não genérico

**Emojis:**
- Máximo 3 por legenda total
- Apenas onde agregam contexto real (nunca decorativos)
- Nunca no início de cada parágrafo como bullet
- Nunca na primeira linha (hook)

**Hashtags (12-16 por variação):**
- Nicho/tema: 5-7 hashtags específicas do assunto
- Volume médio: 4-5 hashtags com alcance moderado
- {branded_hint}
- Todas na última linha após o CTA, separadas por espaço

## FORMATO DE RESPOSTA

Retorne EXCLUSIVAMENTE JSON válido — sem texto antes ou depois, sem markdown, sem blocos de código.

{{
  "variacoes": [
    {{
      "id": 1,
      "abordagem": "Direta",
      "hook": "primeira linha exata do post (max 10 palavras)",
      "body": "corpo da legenda sem o hook e sem o CTA",
      "cta": "chamada para ação final",
      "hashtags": ["#tag1", "#tag2", "#tag3"],
      "legenda_completa": "hook\\n\\nbody\\n\\ncta\\n\\n#tag1 #tag2 ...",
      "hook_score": "X/10 — justificativa objetiva de 1 linha sobre a força do hook"
    }},
    {{ "id": 2, "abordagem": "Narrativa", ... }},
    {{ "id": 3, "abordagem": "Provocadora", ... }}
  ]
}}"""

    return prompt


def _parse_response(raw: str) -> list[dict]:
    clean = re.sub(r"```(?:json)?", "", raw).strip().strip("`").strip()
    try:
        data = json.loads(clean)
        return data.get("variacoes", [])
    except Exception:
        pass
    match = re.search(r'\{.*\}', clean, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(0))
            return data.get("variacoes", [])
        except Exception:
            pass
    return []


def generate_caption(
    form: dict,
    image_bytes: bytes | None = None,
    image_media_type: str = "image/jpeg",
) -> list[dict]:
    """
    Chama o Claude para gerar 3 variações de legenda.
    Se image_bytes fornecido, usa visão multimodal.
    Retorna lista de variações ou lança ValueError.
    """
    try:
        api_key = st.secrets.get("ANTHROPIC_API_KEY") or st.secrets.get("anthropic_api_key")
    except Exception:
        api_key = None

    if not api_key:
        raise ValueError("Chave ANTHROPIC_API_KEY não encontrada em .streamlit/secrets.toml.")

    claude = anthropic.Anthropic(api_key=api_key)
    prompt_text = _build_prompt(form)

    if image_bytes:
        img_b64 = base64.standard_b64encode(image_bytes).decode("utf-8")
        message = claude.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=3500,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type":       "base64",
                            "media_type": image_media_type,
                            "data":       img_b64,
                        },
                    },
                    {"type": "text", "text": prompt_text},
                ],
            }],
        )
    else:
        message = claude.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=3500,
            messages=[{"role": "user", "content": prompt_text}],
        )

    raw = message.content[0].text.strip()
    variacoes = _parse_response(raw)

    if not variacoes:
        raise ValueError(f"Não foi possível interpretar a resposta da IA.\n\nTrecho:\n{raw[:400]}")

    return variacoes
