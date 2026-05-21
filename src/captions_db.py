"""
captions_db.py — Persistência do histórico de legendas no Supabase.

Tabela: caption_history

SQL para criar:

create table caption_history (
  id               serial primary key,
  client_key       text    default '',
  client_name      text    default '',
  formato          text    default '',
  objetivo         text    default '',
  pilar            text    default '',
  tema             text    default '',
  nicho            text    default '',
  abordagem        text    default '',
  hook             text    default '',
  body             text    default '',
  cta_text         text    default '',
  hashtags         text    default '',
  legenda_completa text    default '',
  hook_score       text    default '',
  criativo_texto   text    default '',
  status           text    default 'pendente',
  observacoes      text    default '',
  created_at       timestamptz default now()
);
create index on caption_history (client_key, status);
create index on caption_history (status, created_at desc);
"""
from __future__ import annotations

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


def _headers(prefer: str = "return=minimal") -> dict:
    _, key = _creds()
    return {
        "apikey":        key,
        "Authorization": f"Bearer {key}",
        "Content-Type":  "application/json",
        "Prefer":        prefer,
    }


def _rest() -> str:
    url, _ = _creds()
    return f"{url}/rest/v1/caption_history"


# ── Carregar histórico ────────────────────────────────────────────────────────

@st.cache_data(ttl=30)
def load_history(client_key: str = "", status: str = "", limit: int = 30) -> list[dict]:
    """Carrega histórico de legendas. Filtra por cliente e/ou status se fornecidos."""
    if not _configured():
        return []
    params: dict = {
        "order":  "created_at.desc",
        "limit":  str(limit),
        "select": "id,client_key,client_name,formato,objetivo,pilar,tema,abordagem,hook,legenda_completa,hashtags,hook_score,status,observacoes,created_at",
    }
    if client_key:
        params["client_key"] = f"eq.{client_key}"
    if status:
        params["status"] = f"eq.{status}"
    try:
        r = requests.get(_rest(), headers=_headers("return=representation"), params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception:
        return []


@st.cache_data(ttl=30)
def load_approved(client_key: str, limit: int = 10) -> list[dict]:
    """Carrega legendas aprovadas de um cliente para alimentar a IA."""
    if not _configured() or not client_key:
        return []
    params = {
        "client_key": f"eq.{client_key}",
        "status":     "eq.aprovada",
        "order":      "created_at.desc",
        "limit":      str(limit),
        "select":     "formato,objetivo,pilar,tema,legenda_completa,hook,abordagem",
    }
    try:
        r = requests.get(_rest(), headers=_headers("return=representation"), params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception:
        return []


# ── Salvar legenda ────────────────────────────────────────────────────────────

def save_caption(
    form: dict,
    variacao: dict,
    status: str = "pendente",
    observacoes: str = "",
) -> tuple[bool, str]:
    """Salva uma variação de legenda no histórico."""
    if not _configured():
        return False, "Supabase não configurado."

    hashtags_str = " ".join(variacao.get("hashtags", []))
    payload = {
        "client_key":       form.get("client_key", ""),
        "client_name":      form.get("client_name", ""),
        "formato":          form.get("formato", ""),
        "objetivo":         form.get("objetivo", ""),
        "pilar":            form.get("pilar", ""),
        "tema":             form.get("tema", ""),
        "nicho":            form.get("nicho", ""),
        "abordagem":        variacao.get("abordagem", ""),
        "hook":             variacao.get("hook", ""),
        "body":             variacao.get("body", ""),
        "cta_text":         variacao.get("cta", ""),
        "hashtags":         hashtags_str,
        "legenda_completa": variacao.get("legenda_completa", ""),
        "hook_score":       variacao.get("hook_score", ""),
        "criativo_texto":   form.get("criativo_texto", ""),
        "status":           status,
        "observacoes":      observacoes,
    }
    try:
        r = requests.post(_rest(), headers=_headers(), json=payload, timeout=10)
        if r.status_code in (200, 201):
            load_history.clear()
            load_approved.clear()
            return True, "Salvo com sucesso."
        return False, f"Erro {r.status_code}: {r.text}"
    except Exception as e:
        return False, f"Erro: {e}"


# ── Atualizar status ──────────────────────────────────────────────────────────

def update_status(record_id: int, status: str, observacoes: str = "") -> bool:
    if not _configured():
        return False
    try:
        payload: dict = {"status": status}
        if observacoes:
            payload["observacoes"] = observacoes
        r = requests.patch(
            _rest(),
            headers=_headers(),
            params={"id": f"eq.{record_id}"},
            json=payload,
            timeout=10,
        )
        load_history.clear()
        load_approved.clear()
        return r.status_code in (200, 204)
    except Exception:
        return False


# ── Deletar ───────────────────────────────────────────────────────────────────

def delete_caption(record_id: int) -> bool:
    if not _configured():
        return False
    try:
        r = requests.delete(
            _rest(),
            headers=_headers(),
            params={"id": f"eq.{record_id}"},
            timeout=10,
        )
        load_history.clear()
        load_approved.clear()
        return r.status_code in (200, 204)
    except Exception:
        return False
