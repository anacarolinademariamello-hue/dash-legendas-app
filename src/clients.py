from __future__ import annotations

import json
import requests
import streamlit as st


def _creds() -> tuple[str, str]:
    try:
        url = st.secrets.get("supabase_url", "") or ""
        key = st.secrets.get("supabase_service_key", "") or ""
        return url, key
    except Exception:
        return "", ""


def _configured() -> bool:
    u, k = _creds()
    return bool(u and k)


def _headers() -> dict:
    _, key = _creds()
    return {
        "apikey":        key,
        "Authorization": f"Bearer {key}",
        "Content-Type":  "application/json",
        "Prefer":        "return=representation",
    }


@st.cache_data(ttl=120)
def load_clients() -> list[dict]:
    """Carrega clientes ativos do Supabase."""
    if not _configured():
        return []
    url, _ = _creds()
    try:
        resp = requests.get(
            f"{url}/rest/v1/clients",
            headers=_headers(),
            params={"active": "eq.true", "order": "name.asc", "select": "*"},
            timeout=10,
        )
        resp.raise_for_status()
        return [
            {
                "name":               r["name"],
                "key":                r.get("key") or "",
                "handle":             r.get("handle") or "",
                "tone_of_voice":      r.get("tone_of_voice") or "",
                "bio":                r.get("bio") or "",
                "tags":               r.get("tags") or [],
                "nicho":              r.get("nicho") or "",
                "sub_nicho":          r.get("sub_nicho") or "",
                "publico_alvo":       r.get("publico_alvo") or "",
                "observations":       r.get("observations") or "",
            }
            for r in resp.json()
        ]
    except Exception:
        return []


@st.cache_data(ttl=60)
def load_latest_organic_metrics(client_key: str) -> str:
    """Retorna texto formatado das métricas do último relatório orgânico."""
    if not _configured() or not client_key:
        return ""
    url, key = _creds()
    try:
        r = requests.get(
            f"{url}/rest/v1/report_history",
            headers={"apikey": key, "Authorization": f"Bearer {key}"},
            params={
                "client_key": f"eq.{client_key}",
                "order":      "generated_at.desc",
                "limit":      "1",
                "select":     "date_from,date_to,metrics",
            },
            timeout=10,
        )
        r.raise_for_status()
        rows = r.json()
        if not rows:
            return ""
        row = rows[0]
        m = row.get("metrics", {})
        if isinstance(m, str):
            try:
                m = json.loads(m)
            except Exception:
                return ""

        period = f"{row.get('date_from','')[:10]} → {row.get('date_to','')[:10]}"
        lines = [f"Relatório orgânico ({period}):"]

        if m.get("org_eng_rate"):
            lines.append(f"- Taxa de engajamento: {float(m['org_eng_rate']):.2f}%")
        if m.get("org_reach"):
            lines.append(f"- Alcance orgânico: {int(m['org_reach']):,}".replace(",", "."))
        if m.get("followers_gained"):
            lines.append(f"- Seguidores ganhos: +{int(m['followers_gained'])}")

        # Performance por formato
        formats = m.get("content_formats", [])
        best_format = m.get("best_format", "")
        if formats:
            lines.append("Formatos com melhor desempenho:")
            for f in formats:
                lines.append(
                    f"  • {f.get('type','')}: alcance médio {float(f.get('avg_reach',0)):.0f} | "
                    f"engaj. {float(f.get('avg_eng_rate',0)):.2f}%"
                )
            if best_format:
                lines.append(f"  → Melhor formato: {best_format}")

        # Top posts
        top_posts = m.get("top_posts", [])
        if top_posts:
            lines.append("Temas que mais performaram:")
            for i, post in enumerate(top_posts[:5], 1):
                topic = post.get("caption_preview", post.get("topic", ""))
                reach = post.get("reach", 0)
                lines.append(f"  {i}. Alcance {int(reach):,} — {str(topic)[:80]}".replace(",", "."))

        return "\n".join(lines)
    except Exception:
        return ""
