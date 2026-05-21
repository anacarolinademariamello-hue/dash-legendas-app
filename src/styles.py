from __future__ import annotations


def get_sidebar_css() -> str:
    return """
    /* ── Sidebar dark ── */
    [data-testid="stSidebar"] {
        background: #0d2137 !important;
    }
    [data-testid="stSidebar"] * {
        color: rgba(255,255,255,0.88) !important;
    }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] .stTextInput label {
        color: rgba(255,255,255,0.6) !important;
        font-size: 0.72rem !important;
        text-transform: uppercase;
        letter-spacing: 0.07em;
    }
    [data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, #f8b940, #d99a20) !important;
        color: #0d2137 !important;
        border: none !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        padding: 10px 0 !important;
        width: 100% !important;
        transition: all 0.2s !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: linear-gradient(135deg, #ffd06a, #f8b940) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 14px rgba(248,185,64,0.35) !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.1) !important;
    }
    [data-testid="stSidebar"] .stRadio > div {
        gap: 4px !important;
    }
    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        background: rgba(255,255,255,0.07) !important;
        border-color: rgba(255,255,255,0.15) !important;
        border-radius: 10px !important;
    }
    """


def get_main_css() -> str:
    return """
    /* ── Page header ── */
    .page-header {
        background: linear-gradient(135deg, #0d2137 0%, #1a5a9a 100%);
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 28px;
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .page-header-icon {
        font-size: 2rem;
        line-height: 1;
    }
    .page-header h1 {
        font-size: 1.5rem;
        font-weight: 800;
        color: #fff;
        margin: 0 0 4px;
    }
    .page-header p {
        font-size: 0.85rem;
        color: rgba(255,255,255,0.65);
        margin: 0;
    }

    /* ── Form sections ── */
    .form-section {
        background: #fff;
        border: 1px solid #e8ecf4;
        border-radius: 14px;
        padding: 22px 24px;
        margin-bottom: 18px;
    }
    .form-section-title {
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #9ca3af;
        margin-bottom: 16px;
    }

    /* ── Caption cards ── */
    .caption-card {
        background: #fff;
        border: 1px solid #e8ecf4;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        position: relative;
        overflow: hidden;
    }
    .caption-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
    }
    .caption-card-1::before { background: linear-gradient(90deg, #3b82f6, #8b5cf6); }
    .caption-card-2::before { background: linear-gradient(90deg, #10b981, #3b82f6); }
    .caption-card-3::before { background: linear-gradient(90deg, #f59e0b, #ef4444); }

    .caption-abordagem {
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #9ca3af;
        margin-bottom: 10px;
    }
    .caption-hook {
        font-size: 1.05rem;
        font-weight: 700;
        color: #0d2137;
        background: #f0f3f8;
        border-left: 3px solid #f8b940;
        padding: 10px 14px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 14px;
        line-height: 1.4;
    }
    .caption-score {
        display: inline-block;
        font-size: 0.7rem;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 20px;
        background: #fef3c7;
        color: #92400e;
        margin-bottom: 14px;
    }
    .caption-hashtags {
        display: flex;
        flex-wrap: wrap;
        gap: 5px;
        margin-top: 12px;
    }
    .hashtag-chip {
        font-size: 0.72rem;
        font-weight: 600;
        padding: 3px 9px;
        border-radius: 20px;
        background: #eff6ff;
        color: #1a5a9a;
        cursor: default;
    }

    /* ── Status badges ── */
    .badge-aprovada {
        background: #d1fae5; color: #065f46;
        font-size: 0.72rem; font-weight: 700;
        padding: 3px 10px; border-radius: 20px;
    }
    .badge-rejeitada {
        background: #fee2e2; color: #991b1b;
        font-size: 0.72rem; font-weight: 700;
        padding: 3px 10px; border-radius: 20px;
    }

    /* ── Divider ── */
    .sb-divider { border: none; border-top: 1px solid rgba(255,255,255,0.1); margin: 14px 0; }

    /* ── Info box ── */
    .info-box {
        background: rgba(248,185,64,0.12);
        border: 1px solid rgba(248,185,64,0.3);
        border-radius: 10px;
        padding: 10px 14px;
        font-size: 0.8rem;
        color: rgba(255,255,255,0.85);
        margin-bottom: 12px;
    }
    .info-box strong { color: #f8b940; }

    /* ── Approve/Reject buttons ── */
    .stButton [data-testid="baseButton-secondary"] {
        border-radius: 8px !important;
    }
    """


def get_page_header_html() -> str:
    return """
    <div class="page-header">
        <div class="page-header-icon">✍️</div>
        <div>
            <h1>Gerador de Legendas</h1>
            <p>Crie legendas para posts orgânicos com IA — alimentada pelos relatórios e histórico de cada cliente</p>
        </div>
    </div>
    """


def get_sidebar_welcome_html() -> str:
    return """
    <div style="text-align:center;padding:20px 0;color:rgba(255,255,255,0.35);font-size:0.8rem;">
        Gere legendas para ver<br>as opções aqui
    </div>
    """
