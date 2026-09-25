from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data_logic import aggregate_with_variation, current_month_comparison, discover_csv_files, load_and_consolidate, percent_change


DATA_DIR = Path(__file__).resolve().parent
COLORS = {
    "mint": "#50E3C2",
    "cyan": "#44B7F7",
    "amber": "#FFB547",
    "red": "#FF6376",
    "muted": "#8491A8",
    "grid": "#253047",
}
DIMENSION_LABELS = {
    "provider": "Proveedor",
    "alias_provider": "Alias proveedor",
    "message_type": "Tipo de mensaje",
    "reason": "Motivo",
    "network_id": "Red",
    "segments": "Segmentos",
    "segment_number": "Número de segmento",
    "is_unicode": "Unicode",
    "billed": "Facturado",
    "failed": "Fallido",
    "excluded": "Excluido",
    "total_characters": "Caracteres",
}


st.set_page_config(page_title="Sent Messages", page_icon="▥", layout="wide", initial_sidebar_state="expanded")
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Material+Symbols+Rounded:FILL@0..1&family=Space+Grotesk:wght@500;600&display=swap');
    :root { color-scheme: dark; }
    .stApp {
        background: #020a0d;
        color: #edf3fc;
        font-family: 'DM Sans', sans-serif;
    }
    [data-testid="stHeader"] { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }
    .main .block-container {
        padding-top: 0 !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
        max-width: 100% !important;
    }
    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif !important; letter-spacing: 0 !important; }
    h1 { font-size: 2rem !important; margin-bottom: .15rem !important; }
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] p { color: #c8d2e2 !important; }
    button[data-testid="stExpandSidebarButton"],
    button[data-testid="stSidebarCollapsedControl"],
    button[data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapsedControl"] button,
    [data-testid="stSidebarCollapseButton"] button,
    [data-testid="stHeader"] button[aria-label*="sidebar" i],
    [data-testid="stHeader"] button[aria-label*="barra lateral" i] {
        width: 44px !important;
        height: 44px !important;
        min-width: 44px !important;
        border: 1px solid #65efd6 !important;
        border-radius: 14px !important;
        background: #0b4542 !important;
        box-shadow: 0 0 0 1px rgba(101, 239, 214, .12), 0 8px 20px rgba(0, 0, 0, .3) !important;
        color: #79f4da !important;
    }
    button[data-testid="stExpandSidebarButton"] [data-testid="stIconMaterial"],
    button[data-testid="stSidebarCollapsedControl"] svg,
    button[data-testid="stSidebarCollapseButton"] svg,
    [data-testid="stSidebarCollapsedControl"] button svg,
    [data-testid="stSidebarCollapseButton"] button svg,
    [data-testid="stHeader"] button[aria-label*="sidebar" i] svg,
    [data-testid="stHeader"] button[aria-label*="barra lateral" i] svg {
        color: #79f4da !important;
        fill: none !important;
        stroke: #79f4da !important;
        width: 21px !important;
        height: 21px !important;
        font-size: 21px !important;
    }
    button[data-testid="stExpandSidebarButton"]:hover,
    button[data-testid="stSidebarCollapsedControl"]:hover,
    button[data-testid="stSidebarCollapseButton"]:hover,
    [data-testid="stSidebarCollapsedControl"] button:hover,
    [data-testid="stSidebarCollapseButton"] button:hover,
    [data-testid="stHeader"] button[aria-label*="sidebar" i]:hover,
    [data-testid="stHeader"] button[aria-label*="barra lateral" i]:hover {
        border-color: #a5ffe9 !important;
        background: #126058 !important;
        color: #a5ffe9 !important;
    }
    button[data-testid="stExpandSidebarButton"]:focus-visible,
    button[data-testid="stSidebarCollapsedControl"]:focus-visible,
    button[data-testid="stSidebarCollapseButton"]:focus-visible,
    [data-testid="stSidebarCollapsedControl"] button:focus-visible,
    [data-testid="stSidebarCollapseButton"] button:focus-visible,
    [data-testid="stHeader"] button[aria-label*="sidebar" i]:focus-visible,
    [data-testid="stHeader"] button[aria-label*="barra lateral" i]:focus-visible {
        outline: 3px solid #ffb547;
        outline-offset: 2px;
    }
    [data-testid="stMetric"] {
        background: #131c2c;
        border: 1px solid #29364d;
        border-top: 3px solid #50e3c2;
        border-radius: 6px;
        padding: 14px 16px;
        min-height: 122px;
    }
    [data-testid="stMetricLabel"] p { color: #aebbd0 !important; }
    [data-testid="stMetricValue"] { color: #edf3fc !important; font-family: 'Space Grotesk', sans-serif; }
    [data-testid="stMetricValue"] > div { color: #edf3fc !important; }
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(7, minmax(0, 1fr));
        gap: 14px;
        margin: 0 0 32px;
    }
    .kpi-card {
        position: relative;
        min-width: 0;
        min-height: 136px;
        padding: 14px 15px 12px;
        border: 1px solid rgba(82, 104, 128, 0.72);
        border-radius: 14px;
        background: linear-gradient(180deg, rgba(14, 20, 27, 0.96), rgba(10, 15, 20, 0.96));
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.04), 0 12px 18px rgba(0,0,0,0.14);
    }
    .kpi-card::before {
        content: "";
        position: absolute;
        inset: 0 0 auto 0;
        height: 1px;
        background: rgba(255,255,255,0.05);
    }
    .kpi-head {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 10px;
        min-height: 26px;
    }
    .kpi-label {
        overflow: hidden;
        color: #a9b9cc;
        font-size: .72rem;
        font-weight: 600;
        line-height: 1.2;
        text-transform: none;
        text-overflow: ellipsis;
        white-space: nowrap;
        letter-spacing: .01em;
    }
    .kpi-icon {
        display: grid;
        place-items: center;
        width: 28px;
        height: 28px;
        border-radius: 8px;
        background: rgba(85, 232, 202, 0.08);
        border: 1px solid rgba(85, 232, 202, 0.20);
        color: var(--accent);
        font-family: 'Material Symbols Rounded';
        font-size: 15px;
        font-variation-settings: 'FILL' 0, 'wght' 550, 'GRAD' 0, 'opsz' 24;
        box-shadow: inset 0 0 0 1px rgba(255,255,255,0.02);
    }
    .kpi-card[data-tone="mint"] { --accent: #4de0c3; }
    .kpi-card[data-tone="cyan"] { --accent: #4abaf7; }
    .kpi-card[data-tone="amber"] { --accent: #ffb75d; }
    .kpi-card[data-tone="red"] { --accent: #ff6d85; }
    .kpi-card[data-tone="pink"] { --accent: #ff7b9d; }
    .kpi-card[data-tone="purple"] { --accent: #c59af9; }
    .kpi-card[data-tone="teal"] { --accent: #4de0c3; }
    .kpi-value {
        width: 100%;
        margin-top: 18px;
        overflow: hidden;
        color: #edf3fc;
        font-family: 'Space Grotesk', sans-serif;
        font-size: clamp(1.38rem, 0.9vw + 1.05rem, 2.05rem);
        font-weight: 600;
        line-height: 1.1;
        white-space: nowrap;
        letter-spacing: -0.04em;
        text-shadow: 0 0 12px rgba(80, 227, 194, 0.08);
    }
    @media (max-width: 1200px) { .kpi-grid { grid-template-columns: repeat(4, minmax(0, 1fr)); } }
    @media (max-width: 820px) { .kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
    @media (max-width: 560px) { .kpi-grid { grid-template-columns: 1fr; } }
    .quality-kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 12px;
        margin: 2px 0 24px;
    }
    .quality-kpi-card {
        position: relative;
        overflow: hidden;
        min-width: 0;
        min-height: 156px;
        padding: 17px;
        border: 1px solid color-mix(in srgb, var(--signal) 40%, #29364d);
        border-radius: 8px;
        background: linear-gradient(145deg, rgba(22, 33, 50, .98), rgba(15, 23, 37, .98));
        box-shadow: inset 0 2px 0 var(--signal), 0 10px 26px rgba(0, 0, 0, .16);
    }
    .quality-kpi-head { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
    .quality-kpi-label { color: #b8c3d5; font-size: .82rem; font-weight: 700; }
    .quality-kpi-icon {
        display: grid;
        flex: 0 0 36px;
        width: 36px;
        height: 36px;
        place-items: center;
        border: 1px solid color-mix(in srgb, var(--signal) 48%, transparent);
        border-radius: 8px;
        background: color-mix(in srgb, var(--signal) 13%, transparent);
        color: var(--signal);
        font-family: 'DM Sans', sans-serif;
        font-size: 18px;
        font-weight: 700;
    }
    .quality-kpi-value {
        margin-top: 17px;
        color: #f4f8ff;
        font-family: 'Space Grotesk', sans-serif;
        font-size: clamp(1.6rem, 2vw, 2.15rem);
        font-weight: 600;
        line-height: 1;
    }
    .quality-kpi-benchmark { margin-top: 12px; color: #93a1b7; font-size: .74rem; }
    .quality-kpi-status { color: var(--signal); font-weight: 700; }
    @media (max-width: 1000px) { .quality-kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
    @media (max-width: 560px) { .quality-kpi-grid { grid-template-columns: 1fr; } }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; border-bottom: 1px solid #29364d; }
    .stTabs [data-baseweb="tab"] { height: 48px; color: #9ba8bd; background: transparent; }
    .stTabs [aria-selected="true"] { color: #edf3fc !important; border-bottom: 2px solid #50e3c2; }
    .insight {
        min-height: 138px;
        background: #131c2c;
        border: 1px solid #29364d;
        border-left: 5px solid var(--signal);
        border-radius: 6px;
        padding: 15px 16px;
        margin-bottom: 12px;
    }
    .insight-top { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
    .insight-meta { display: flex; align-items: center; gap: 8px; }
    .insight-icon {
        display: grid;
        width: 30px;
        height: 30px;
        place-items: center;
        border: 1px solid color-mix(in srgb, var(--signal) 52%, transparent);
        border-radius: 7px;
        background: color-mix(in srgb, var(--signal) 12%, transparent);
        color: var(--signal);
        font-family: 'DM Sans', sans-serif;
        font-size: 16px;
        font-weight: 700;
    }
    .insight .signal { color: var(--signal); font-size: .72rem; font-weight: 700; text-transform: uppercase; }
    .insight-horizon {
        color: #9eabc0;
        font-size: .68rem;
        font-weight: 700;
        text-transform: uppercase;
    }
    .insight strong { display: block; font-family: 'Space Grotesk'; margin: 7px 0 5px; }
    .insight p { color: #aab5c7; font-size: .88rem; line-height: 1.4; margin: 0; }
    .dashboard-banner {
        position: relative;
        overflow: hidden;
        min-height: 260px;
        margin: 0 0 28px;
        padding: 26px 32px 24px;
        border: 1px solid rgba(18, 56, 51, 0.95);
        border-radius: 18px;
        background:
            radial-gradient(circle at 70% 20%, rgba(33, 116, 100, 0.18), transparent 26%),
            radial-gradient(circle at 84% 68%, rgba(22, 146, 126, 0.12), transparent 20%),
            linear-gradient(90deg, rgba(3, 8, 10, 0.96) 0%, rgba(4, 12, 14, 0.98) 54%, rgba(3, 19, 21, 0.94) 100%);
    }
    .dashboard-banner::before {
        content: "";
        position: absolute;
        inset: 0;
        pointer-events: none;
        background-image:
            linear-gradient(rgba(80,227,194,0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(80,227,194,0.02) 1px, transparent 1px);
        background-size: 82px 82px;
    }
    .banner-content { position: relative; z-index: 2; max-width: 72%; }
    .dashboard-banner h1 {
        margin: 16px 0 12px !important;
        color: #f2f5f9;
        font-size: clamp(3rem, 4.2vw, 6rem) !important;
        font-weight: 700;
        line-height: .95;
        letter-spacing: -0.055em;
    }
    .dashboard-banner p {
        margin: 0;
        color: #dfe8f3;
        font-size: 1.05rem;
        line-height: 1.5;
    }
    .dashboard-banner p strong { color: #50e3c2; font-weight: 700; }
    .dashboard-banner .eyebrow {
        display: block;
        color: #48e3c5;
        font-size: .72rem;
        font-weight: 700;
        letter-spacing: .18em;
        text-transform: uppercase;
    }
    .banner-network {
        position: absolute;
        z-index: 1;
        inset: -8% -4% 0 57%;
        opacity: 0.9;
    }
    .banner-network .node,
    .banner-network .edge { position: absolute; display: block; }
    .banner-network .node {
        width: 14px;
        height: 14px;
        border-radius: 50%;
        background: #52e8ca;
        box-shadow: 0 0 12px rgba(82, 232, 202, 0.8), 0 0 24px rgba(82, 232, 202, 0.4);
    }
    .banner-network .node.blue {
        width: 16px;
        height: 16px;
        background: #54b8f8;
        box-shadow: 0 0 12px rgba(84, 184, 248, 0.8), 0 0 28px rgba(84, 184, 248, 0.45);
    }
    .banner-network .edge {
        height: 2px;
        background: rgba(85, 232, 202, 0.8);
        transform-origin: left center;
        box-shadow: 0 0 8px rgba(85, 232, 202, 0.5);
    }
    .banner-network .edge.faint { background: rgba(126, 154, 178, 0.18); }
    .n1 { left: 16%; top: 12%; }
    .n2 { left: 31%; top: 42%; }
    .n3 { left: 61%; top: 23%; }
    .n4 { left: 75%; top: 52%; }
    .n5 { left: 44%; top: 70%; }
    .n6 { left: 80%; top: 80%; }
    .e1 { left: 17%; top: 14%; width: 27%; transform: rotate(20deg); }
    .e2 { left: 31%; top: 44%; width: 36%; transform: rotate(-18deg); }
    .e3 { left: 61%; top: 25%; width: 18%; transform: rotate(-18deg); }
    .e4 { left: 44%; top: 72%; width: 39%; transform: rotate(-22deg); }
    .e5 { left: 16%; top: 12%; width: 61%; transform: rotate(38deg); }
    .e6 { left: 29%; top: 42%; width: 36%; transform: rotate(40deg); }
    .e7 { left: 58%; top: 28%; width: 22%; transform: rotate(34deg); }
    @media (max-width: 640px) {
        .dashboard-banner { min-height: 220px; padding: 22px 18px; border-radius: 14px; }
        .banner-content { max-width: 100%; }
        .dashboard-banner h1 { font-size: 2.4rem !important; }
        .dashboard-banner p { font-size: .84rem; line-height: 1.4; }
        .banner-network { inset: 18% -6% 0 45%; opacity: .35; }
    }
    .matrix-shell {
        overflow: hidden;
        border: 1px solid #29364d;
        border-radius: 8px;
        background: #070b11;
    }
    .matrix-shell.scrollable { overflow-y: auto; }
    table.kpi-matrix { width: 100%; border-collapse: collapse; background: #070b11; font-size: .8rem; }
    table.kpi-matrix th {
        position: sticky;
        z-index: 2;
        top: 0;
        padding: 11px 10px;
        border-bottom: 1px solid #334155;
        background: #0d1522 !important;
        color: #ffffff !important;
        font-weight: 700;
        text-align: right;
        white-space: nowrap;
    }
    table.kpi-matrix td {
        padding: 9px 10px;
        border-bottom: 1px solid #1d2939;
        color: #f4f8ff;
        text-align: right;
        white-space: nowrap;
    }
    table.kpi-matrix th:first-child, table.kpi-matrix td:first-child { text-align: left; }
    table.kpi-matrix tbody tr:last-child td { border-bottom: 0; }
    table.kpi-matrix tbody tr:hover td { filter: brightness(1.15); }
    </style>
    """,
    unsafe_allow_html=True,
)


def format_number(value: float) -> str:
    return f"{value:,.0f}".replace(",", ".")


def format_compact(value: float) -> str:
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if abs(value) >= 1_000:
        return f"{value / 1_000:.0f}K"
    return f"{value:.0f}"


def format_pct(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "Sin base"
    return f"{value:+.1f}%".replace(".", ",")


@st.cache_data(show_spinner="Consolidando archivos CSV...")
def load_data(file_signature: tuple[tuple[str, int, int], ...]) -> pd.DataFrame:
    files = [DATA_DIR / name for name, _, _ in file_signature]
    return load_and_consolidate(files)


def style_figure(figure: go.Figure, height: int = 390) -> go.Figure:
    figure.update_layout(
        height=height,
        margin=dict(l=12, r=12, t=48, b=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(19,28,44,.76)",
        font=dict(family="DM Sans", color="#ffffff"),
        title_font=dict(family="Space Grotesk", size=17, color="#ffffff"),
        legend=dict(font=dict(color="#ffffff"), title_font=dict(color="#ffffff")),
        legend_title_text="",
        hoverlabel=dict(bgcolor="#101725", font_color="#edf3fc"),
    )
    figure.update_xaxes(gridcolor=COLORS["grid"], zeroline=False)
    figure.update_yaxes(gridcolor=COLORS["grid"], zeroline=False)
    return figure


def top_breakdown(frame: pd.DataFrame, dimension: str, limit: int = 12) -> pd.DataFrame:
    values = frame.copy()
    values[dimension] = values[dimension].astype("string").fillna("Sin dato").replace("", "Sin dato")
    return (
        values.groupby(dimension, as_index=False, dropna=False)["cuenta"]
        .sum()
        .nlargest(limit, "cuenta")
        .sort_values("cuenta")
    )


def weighted_rate(frame: pd.DataFrame, column: str) -> float:
    total = frame["cuenta"].sum()
    if total == 0:
        return 0.0
    mask = frame[column].fillna(False).astype(bool)
    return float(frame.loc[mask, "cuenta"].sum() / total * 100)


def average_monthly_rate(frame: pd.DataFrame, column: str) -> float:
    working = frame[["mes", "cuenta", column]].copy()
    working["ponderado"] = working["cuenta"] * working[column].fillna(False).astype(bool)
    monthly = working.groupby("mes", as_index=False).agg(total=("cuenta", "sum"), ponderado=("ponderado", "sum"))
    valid = monthly[monthly["total"].gt(0)]
    if valid.empty:
        return 0.0
    return float((valid["ponderado"] / valid["total"] * 100).mean())


def benchmark_signal(value: float, benchmark: float, high_is_good: bool) -> tuple[str, str]:
    tolerance = max(abs(benchmark) * 0.05, 0.01)
    difference = value - benchmark
    if abs(difference) <= tolerance:
        return COLORS["amber"], "En promedio"
    is_favorable = difference > 0 if high_is_good else difference < 0
    return (COLORS["mint"], "Mejor que promedio") if is_favorable else (COLORS["red"], "Peor que promedio")


def build_kpi_matrix(frame: pd.DataFrame, period: str) -> tuple[pd.DataFrame, str]:
    working = frame.copy()
    working["_fallidos"] = working["cuenta"] * working["failed"].fillna(False).astype(bool)
    working["_excluidos"] = working["cuenta"] * working["excluded"].fillna(False).astype(bool)
    working["_facturados"] = working["cuenta"] * working["billed"].fillna(False).astype(bool)

    period_map = {"Month": "mes", "Day": "fecha", "Hour": "hora"}
    period_column = period_map.get(period, "mes")
    matrix = (
        working.groupby(period_column, as_index=False)
        .agg(
            Mensajes=("cuenta", "sum"),
            Fallidos=("_fallidos", "sum"),
            Excluidos=("_excluidos", "sum"),
            Facturados=("_facturados", "sum"),
        )
        .sort_values(period_column)
    )

    if period == "Month":
        averages = working.groupby(["mes", "fecha"])["cuenta"].sum().groupby("mes").mean()
        matrix["Promedio operativo"] = matrix[period_column].map(averages)
        average_label = "Promedio diario"
        matrix["Periodo"] = matrix[period_column].map(lambda value: month_names_es(value.month))
    elif period == "Day":
        averages = working.groupby(["fecha", "hora"])["cuenta"].sum().groupby("fecha").mean()
        matrix["Promedio operativo"] = matrix[period_column].map(averages)
        average_label = "Promedio por hora"
        matrix["Periodo"] = matrix[period_column].dt.strftime("%d/%m/%Y")
    else:
        averages = working.groupby(["hora", "fecha"])["cuenta"].sum().groupby("hora").mean()
        matrix["Promedio operativo"] = matrix[period_column].map(averages)
        average_label = "Promedio diario"
        matrix["Periodo"] = matrix[period_column].map(lambda value: f"{int(value):02d}:00")

    total = matrix["Mensajes"].sum()
    matrix["Participación"] = matrix["Mensajes"] / total * 100 if total else 0.0
    matrix["Variación"] = matrix["Mensajes"].pct_change(fill_method=None) * 100
    matrix["Tasa de fallos"] = matrix["Fallidos"] / matrix["Mensajes"] * 100
    matrix["Tasa de exclusión"] = matrix["Excluidos"] / matrix["Mensajes"] * 100
    matrix["Facturación"] = matrix["Facturados"] / matrix["Mensajes"] * 100
    matrix = matrix.rename(columns={"Promedio operativo": average_label})
    return matrix[["Periodo", "Mensajes", average_label, "Participación", "Variación", "Tasa de fallos", "Tasa de exclusión", "Facturación"]], average_label


def build_dimension_kpi_matrix(frame: pd.DataFrame, dimension: str) -> pd.DataFrame:
    working = frame.copy()
    dimension_label = DIMENSION_LABELS[dimension]
    working["_fallidos"] = working["cuenta"] * working["failed"].fillna(False).astype(bool)
    working["_excluidos"] = working["cuenta"] * working["excluded"].fillna(False).astype(bool)
    working["_facturados"] = working["cuenta"] * working["billed"].fillna(False).astype(bool)
    if dimension in {"billed", "failed"}:
        working[dimension] = working[dimension].map({True: "Sí", False: "No"}).fillna("Sin dato")
    else:
        working[dimension] = working[dimension].astype("string").fillna("Sin dato").replace("", "Sin dato")
    matrix = (
        working.groupby(dimension, as_index=False, dropna=False)
        .agg(
            Mensajes=("cuenta", "sum"),
            Fallidos=("_fallidos", "sum"),
            Excluidos=("_excluidos", "sum"),
            Facturados=("_facturados", "sum"),
        )
        .sort_values("Mensajes", ascending=False)
    )

    daily_average = working.groupby([dimension, "fecha"])["cuenta"].sum().groupby(dimension).mean()
    matrix["Promedio diario"] = matrix[dimension].map(daily_average)
    total = matrix["Mensajes"].sum()
    matrix["Participación"] = matrix["Mensajes"] / total * 100 if total else 0.0
    matrix["Tasa de fallos"] = matrix["Fallidos"] / matrix["Mensajes"] * 100
    matrix["Tasa de exclusión"] = matrix["Excluidos"] / matrix["Mensajes"] * 100
    matrix["Facturación"] = matrix["Facturados"] / matrix["Mensajes"] * 100

    max_date = working["fecha"].max()
    current_month = max_date.to_period("M")
    previous_month = current_month - 1
    current_values = (
        working.loc[working["fecha"].dt.to_period("M").eq(current_month)]
        .groupby(dimension)["cuenta"]
        .sum()
    )
    previous_values = (
        working.loc[
            working["fecha"].dt.to_period("M").eq(previous_month) & working["fecha"].dt.day.le(max_date.day)
        ]
        .groupby(dimension)["cuenta"]
        .sum()
    )
    matrix["Variación MTD"] = matrix[dimension].map(
        lambda value: percent_change(float(current_values.get(value, 0)), float(previous_values.get(value, 0)))
    )
    return matrix.rename(columns={dimension: dimension_label})[
        [dimension_label, "Mensajes", "Promedio diario", "Participación", "Variación MTD", "Tasa de fallos", "Tasa de exclusión", "Facturación"]
    ]


def month_names_es(month: int) -> str:
    return {
        1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
        7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December",
    }[month]


def build_insights(frame: pd.DataFrame) -> list[tuple[str, str, str, str, str, str]]:
    if frame.empty:
        return [("ALERT", "Short term", "!", "No data to analyze", "Widen the filters to generate alerts.", COLORS["red"])] * 6

    comparison = current_month_comparison(frame)
    variation = comparison["variation"]
    if variation is None:
        trend_level, trend_color = "ATTENTION", COLORS["amber"]
    elif abs(variation) >= 15:
        trend_level, trend_color = "ALERT", COLORS["red"]
    elif abs(variation) >= 5:
        trend_level, trend_color = "ATTENTION", COLORS["amber"]
    else:
        trend_level, trend_color = "STABLE", COLORS["mint"]

    providers = top_breakdown(frame, "provider", 2).sort_values("cuenta", ascending=False)
    leading_provider = str(providers.iloc[0]["provider"])
    concentration = float(providers.iloc[0]["cuenta"] / frame["cuenta"].sum() * 100)
    if concentration >= 50:
        concentration_level, concentration_color = "ALERT", COLORS["red"]
    elif concentration >= 30:
        concentration_level, concentration_color = "ATTENTION", COLORS["amber"]
    else:
        concentration_level, concentration_color = "STABLE", COLORS["mint"]

    daily = frame.groupby("fecha", as_index=False)["cuenta"].sum()
    peak_day = daily.loc[daily["cuenta"].idxmax()]
    hourly = frame.groupby("hora", as_index=False)["cuenta"].sum()
    peak_hour = hourly.loc[hourly["cuenta"].idxmax()]
    peak_hour_share = float(peak_hour["cuenta"] / hourly["cuenta"].sum() * 100)
    peak_day_ratio = float(peak_day["cuenta"] / daily["cuenta"].mean())
    if peak_day_ratio >= 1.5:
        peak_level, peak_color = "ALERTA", COLORS["red"]
    elif peak_day_ratio >= 1.2:
        peak_level, peak_color = "ATENCIÓN", COLORS["amber"]
    else:
        peak_level, peak_color = "ESTABLE", COLORS["mint"]

    failed_rate = weighted_rate(frame, "failed")
    failed_benchmark = average_monthly_rate(frame, "failed")
    failed_color, failed_status = benchmark_signal(failed_rate, failed_benchmark, high_is_good=False)
    failed_level = "ALERTA" if failed_color == COLORS["red"] else "ATENCIÓN" if failed_color == COLORS["amber"] else "ESTABLE"

    provider_risk = frame.copy()
    provider_risk["provider"] = provider_risk["provider"].astype("string").fillna("Sin dato").replace("", "Sin dato")
    provider_risk["fallidos"] = provider_risk["cuenta"] * provider_risk["failed"].fillna(False).astype(bool)
    provider_risk = provider_risk.groupby("provider", as_index=False).agg(Mensajes=("cuenta", "sum"), Fallidos=("fallidos", "sum"))
    provider_risk["Tasa"] = provider_risk["Fallidos"] / provider_risk["Mensajes"] * 100
    worst_provider = provider_risk.sort_values("Fallidos", ascending=False).iloc[0]
    worst_share = float(worst_provider["Fallidos"] / max(provider_risk["Fallidos"].sum(), 1) * 100)
    if worst_share >= 40:
        provider_level, provider_color = "ALERTA", COLORS["red"]
    elif worst_share >= 20:
        provider_level, provider_color = "ATENCIÓN", COLORS["amber"]
    else:
        provider_level, provider_color = "ESTABLE", COLORS["mint"]

    billed_rate = weighted_rate(frame, "billed")
    billed_benchmark = average_monthly_rate(frame, "billed")
    billed_color, billed_status = benchmark_signal(billed_rate, billed_benchmark, high_is_good=True)
    billed_level = "ALERTA" if billed_color == COLORS["red"] else "ATENCIÓN" if billed_color == COLORS["amber"] else "ESTABLE"
    unbilled_messages = float(frame["cuenta"].sum() * (100 - billed_rate) / 100)

    return [
        (
            trend_level,
            "Corto plazo · 7 días",
            "↗",
            f"El volumen cambió {format_pct(variation)}",
            f"Al día {comparison['cutoff_day']} van {format_number(comparison['current'])} mensajes frente a {format_number(comparison['previous'])} el mes pasado. Acción: ajuste capacidad y previsión de envíos para la próxima semana.",
            trend_color,
        ),
        (
            failed_level,
            "Corto plazo · 24 horas",
            "!",
            f"Fallan {failed_rate:.1f} de cada 100 mensajes",
            f"El promedio mensual es {failed_benchmark:.2f}% ({failed_status.lower()}). Acción: revise hoy los códigos de error y los proveedores con más fallos.",
            failed_color,
        ),
        (
            provider_level,
            "Corto plazo · 48 horas",
            "◆",
            f"{worst_provider['provider']} aporta más fallos",
            f"Genera {worst_share:.1f}% de todos los mensajes fallidos y falla en {worst_provider['Tasa']:.2f}% de sus envíos. Acción: valide su ruta y acuerde un plan de corrección.",
            provider_color,
        ),
        (
            concentration_level,
            "Mediano plazo · 30 días",
            "◎",
            f"{leading_provider} mueve {concentration:.1f}% del tráfico",
            "Una alta dependencia puede afectar la continuidad si ese proveedor falla. Acción: defina capacidad de respaldo y límites de distribución por proveedor.",
            concentration_color,
        ),
        (
            peak_level,
            "Corto plazo · 7 días",
            "◷",
            f"La mayor carga ocurre a las {int(peak_hour['hora']):02d}:00",
            f"Esa hora concentra {peak_hour_share:.1f}% del volumen. El día pico fue {peak_day['fecha']:%d/%m/%Y}. Acción: reserve capacidad y monitoreo reforzado en esa franja.",
            peak_color,
        ),
        (
            billed_level,
            "Mediano plazo · 30 días",
            "✓",
            f"Hay {format_number(unbilled_messages)} mensajes no facturados",
            f"La facturación está en {billed_rate:.2f}% y su promedio mensual es {billed_benchmark:.2f}% ({billed_status.lower()}). Acción: concilie proveedores y tipos de mensaje antes del cierre.",
            billed_color,
        ),
    ]


files = discover_csv_files(DATA_DIR)
if not files:
    st.error("No CSV files were found in the project folder.")
    st.stop()

signature = tuple((path.name, path.stat().st_mtime_ns, path.stat().st_size) for path in files)
try:
    data = load_data(signature)
except (ValueError, pd.errors.ParserError) as error:
    st.error(f"It was not possible to consolidate the CSV files: {error}")
    st.stop()

if data.empty:
    st.warning("The files do not contain valid records.")
    st.stop()

latest_record = data["fecha_hora"].max()

with st.sidebar:
    st.markdown("## Filters")
    min_date = data["fecha"].min().date()
    max_date = data["fecha"].max().date()
    available_months = sorted(data["fecha"].dt.to_period("M").unique(), reverse=True)
    month_options = {"All months": None}
    month_options.update({f"{month_names_es(period.month)} {period.year}": period for period in available_months})
    date_filter_mode = st.segmented_control(
        "Dates",
        options=["All", "One date", "Range"],
        default="All",
        selection_mode="single",
    )
    if date_filter_mode == "One date":
        selected_date = st.date_input("Date", value=max_date, min_value=min_date, max_value=max_date)
        start_date = end_date = pd.Timestamp(selected_date)
    elif date_filter_mode == "Range":
        date_range = st.date_input(
            "Date range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
        else:
            start_date = end_date = pd.Timestamp(date_range)
    else:
        start_date, end_date = pd.Timestamp(min_date), pd.Timestamp(max_date)
    selected_month = month_options[st.selectbox("Month", month_options)]
    selected_provider = st.multiselect("Provider", sorted(data["provider"].dropna().astype(str).unique()))
    selected_type = st.multiselect("Message type", sorted(data["message_type"].dropna().astype(str).unique()))
    status = st.selectbox("Status", ["All", "Successful", "Failed", "Excluded"])
    st.divider()
    st.caption(f"{len(files)} consolidated files")
    st.caption(f"Last data: {max_date:%d/%m/%Y}")
dimension_filtered = data.copy()
if selected_month is not None:
    dimension_filtered = dimension_filtered[dimension_filtered["fecha"].dt.to_period("M").eq(selected_month)]
if selected_provider:
    dimension_filtered = dimension_filtered[dimension_filtered["provider"].astype(str).isin(selected_provider)]
if selected_type:
    dimension_filtered = dimension_filtered[dimension_filtered["message_type"].astype(str).isin(selected_type)]
if status == "Successful":
    dimension_filtered = dimension_filtered[~dimension_filtered["failed"].fillna(False) & ~dimension_filtered["excluded"].fillna(False)]
elif status == "Failed":
    dimension_filtered = dimension_filtered[dimension_filtered["failed"].fillna(False)]
elif status == "Excluded":
    dimension_filtered = dimension_filtered[dimension_filtered["excluded"].fillna(False)]

filtered = dimension_filtered[dimension_filtered["fecha"].between(start_date, end_date)]

st.markdown(
    f"""
    <section class="dashboard-banner">
        <div class="banner-content">
            <span class="eyebrow">MESSAGING ANALYTICS · AI</span>
            <h1>Sent Messages</h1>
            <p>Consolidated monitoring &nbsp;|&nbsp; Period analyzed: <strong>{start_date:%d/%m/%Y} → {end_date:%d/%m/%Y}</strong> &nbsp;|&nbsp; <strong>{len(files)}</strong> CSV consolidated &nbsp;|&nbsp; Last record: <strong>{latest_record:%d/%m/%Y %H:%M}</strong></p>
        </div>
        <div class="banner-network" aria-hidden="true">
            <span class="edge e1"></span><span class="edge e2"></span><span class="edge e3 faint"></span>
            <span class="edge e4"></span><span class="edge e5"></span><span class="edge e6 faint"></span><span class="edge e7 faint"></span>
            <span class="node n1"></span><span class="node blue n2"></span><span class="node n3"></span>
            <span class="node n4"></span><span class="node blue n5"></span><span class="node n6"></span>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

if filtered.empty:
    st.warning("No data for the selected filter combination.")
    st.stop()

comparison = current_month_comparison(dimension_filtered)
total = float(filtered["cuenta"].sum())
failed_rate = weighted_rate(filtered, "failed")
excluded_rate = weighted_rate(filtered, "excluded")
average_daily = float(filtered.groupby("fecha")["cuenta"].sum().mean())

st.markdown(
    f"""
    <section class="kpi-grid" aria-label="Indicadores principales">
        <article class="kpi-card" data-tone="mint">
            <div class="kpi-head"><span class="kpi-label">Messages sent</span><span class="kpi-icon">➤</span></div>
            <div class="kpi-value">{format_number(total)}</div>
        </article>
        <article class="kpi-card" data-tone="cyan">
            <div class="kpi-head"><span class="kpi-label">Messages read</span><span class="kpi-icon">✓</span></div>
            <div class="kpi-value">{format_number(total * (1 - failed_rate / 100))}</div>
        </article>
        <article class="kpi-card" data-tone="amber">
            <div class="kpi-head"><span class="kpi-label">Failed messages</span><span class="kpi-icon">×</span></div>
            <div class="kpi-value">{format_number(total * failed_rate / 100)}</div>
        </article>
        <article class="kpi-card" data-tone="red">
            <div class="kpi-head"><span class="kpi-label">Billed messages</span><span class="kpi-icon">$</span></div>
            <div class="kpi-value">{format_number(total * (1 - excluded_rate / 100))}</div>
        </article>
        <article class="kpi-card" data-tone="teal">
            <div class="kpi-head"><span class="kpi-label">% read</span><span class="kpi-icon">✓</span></div>
            <div class="kpi-value">{(100 - failed_rate):.2f}%</div>
        </article>
        <article class="kpi-card" data-tone="red">
            <div class="kpi-head"><span class="kpi-label">% failed</span><span class="kpi-icon">!</span></div>
            <div class="kpi-value">{failed_rate:.2f}%</div>
        </article>
        <article class="kpi-card" data-tone="pink">
            <div class="kpi-head"><span class="kpi-label">% billable</span><span class="kpi-icon">$</span></div>
            <div class="kpi-value">{(100 - excluded_rate):.2f}%</div>
        </article>
    </section>
    """,
    unsafe_allow_html=True,
)

timeline_tab, mix_tab, quality_tab, insights_tab = st.tabs(
    ["Volume trend", "Mix & providers", "Operational quality", "Insights"]
)

with timeline_tab:
    st.subheader("Volume trend")
    period_label = st.segmented_control("Granularity", ["Month", "Day", "Hour"], default="Month")
    period_map = {"Month": "mes", "Day": "fecha", "Hour": "hora"}
    period = period_map[period_label]
    timeline = aggregate_with_variation(filtered, period)
    if period == "fecha":
        timeline = filtered.groupby("dia", as_index=False)["cuenta"].sum().sort_values("dia")
        timeline["variacion"] = timeline["cuenta"].pct_change(fill_method=None) * 100
        timeline["fecha"] = timeline["dia"]
    month_names = {
        1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
        7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December",
    }
    month_ticks = pd.Series(dtype="datetime64[ns]")
    month_labels: list[str] = []
    month_axis_range: list[pd.Timestamp] = []
    day_ticks: list[int] = []
    if period == "mes":
        month_ticks = filtered["mes"].drop_duplicates().sort_values()
        month_labels = [month_names[month.month] for month in month_ticks]
        axis_padding = pd.Timedelta(days=15)
        month_axis_range = [timeline[period].min() - axis_padding, timeline[period].max() + axis_padding]
    elif period == "fecha":
        day_ticks = list(range(1, 32))
    left, right = st.columns([1.65, 1])
    with left:
        if period == "mes":
            monthly_values = timeline["cuenta"]
            low_threshold = monthly_values.quantile(1 / 3)
            high_threshold = monthly_values.quantile(2 / 3)
            if low_threshold == high_threshold:
                bar_colors = [COLORS["amber"]] * len(monthly_values)
            else:
                bar_colors = [
                    COLORS["red"] if value <= low_threshold else COLORS["mint"] if value >= high_threshold else COLORS["amber"]
                    for value in monthly_values
                ]
            monthly_average = float(monthly_values.mean())
            volume_chart = px.bar(
                timeline,
                x=period,
                y="cuenta",
                text=[format_number(value) for value in timeline["cuenta"]],
                title="Messages by month",
                color_discrete_sequence=[COLORS["cyan"]],
            )
            volume_chart.update_traces(
                marker_color=bar_colors,
                opacity=.9,
                textposition="outside",
                textfont=dict(color="#edf3fc", size=12),
                cliponaxis=False,
                hovertemplate="%{x|%B %Y}<br>%{y:,.0f} messages<extra></extra>",
            )
            volume_chart.add_hline(
                y=monthly_average,
                line_color=COLORS["amber"],
                line_dash="dash",
                line_width=2,
                annotation_text=f"Average: {format_number(monthly_average)}",
                annotation_position="top left",
                annotation_font_color="#ffffff",
            )
        else:
            volume_chart = px.line(
                timeline,
                x=period,
                y="cuenta",
                title=f"Messages by {period_label.lower()}",
                markers=True,
                color_discrete_sequence=[COLORS["cyan"]],
            )
            if period == "fecha":
                daily_average = float(timeline["cuenta"].mean())
                daily_marker_colors = [
                    COLORS["mint"] if value > daily_average else COLORS["red"] if value < daily_average else COLORS["amber"]
                    for value in timeline["cuenta"]
                ]
                volume_chart.add_hline(
                    y=daily_average,
                    line_color=COLORS["amber"],
                    line_dash="dash",
                    line_width=2,
                    annotation_text=f"Average: {format_number(daily_average)}",
                    annotation_position="top left",
                    annotation_font_color="#ffffff",
                )
            else:
                daily_marker_colors = COLORS["mint"]
            volume_chart.update_traces(
                line_width=2.5,
                marker=dict(size=7, color=daily_marker_colors, line=dict(width=1.5, color="#0c111c")),
            )
        if period == "mes":
            volume_chart.update_xaxes(
                tickmode="array", tickvals=month_ticks, ticktext=month_labels, title_text="Month", range=month_axis_range
            )
        elif period == "fecha":
            volume_chart.update_xaxes(
                tickmode="array", tickvals=day_ticks, ticktext=[str(day) for day in day_ticks],
                title_text="Day of month", range=[0.5, 31.5]
            )
        styled_volume_chart = style_figure(volume_chart)
        if period == "mes":
            styled_volume_chart.update_layout(
                title_font=dict(color="#ffffff", family="Space Grotesk", size=17),
            )
        st.plotly_chart(styled_volume_chart, use_container_width=True)
    with right:
        variation_data = timeline.dropna(subset=["variacion"])
        variation_chart = px.bar(
            variation_data,
            x=period,
            y="variacion",
            title="Variation vs previous period (%)",
            color="variacion",
            color_continuous_scale=[[0, COLORS["red"]], [0.5, COLORS["amber"]], [1, COLORS["mint"]]],
            color_continuous_midpoint=0,
        )
        variation_chart.update_layout(coloraxis_showscale=False)
        variation_chart.update_traces(hovertemplate="%{x}<br>%{y:.2f}%<extra></extra>")
        variation_chart.update_yaxes(ticksuffix="%", tickformat=".2f")
        if period == "mes":
            variation_chart.update_traces(
                text=[f"{value:+.2f}%" for value in variation_data["variacion"]],
                texttemplate="%{text}",
                textposition="outside",
                textfont=dict(color="#edf3fc", size=12),
                cliponaxis=False,
            )
        if period == "mes":
            variation_chart.update_xaxes(
                tickmode="array", tickvals=month_ticks, ticktext=month_labels, title_text="Month", range=month_axis_range
            )
        elif period == "fecha":
            variation_chart.update_xaxes(
                tickmode="array", tickvals=day_ticks, ticktext=[str(day) for day in day_ticks],
                title_text="Day of month", range=[0.5, 31.5]
            )
        variation_chart.update_xaxes(tickfont=dict(size=10))
        st.plotly_chart(style_figure(variation_chart), use_container_width=True)

    heatmap_data = filtered.pivot_table(index="hora", columns="dia_semana", values="cuenta", aggfunc="sum", fill_value=0)
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_labels = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    heatmap_data = heatmap_data.reindex(columns=day_order, fill_value=0)
    heatmap_labels = heatmap_data.map(
        lambda value: f"{value / 1_000_000:.1f}M" if value >= 1_000_000 else f"{value / 1_000:.0f}K"
    )
    heatmap = go.Figure(
        go.Heatmap(
            z=heatmap_data.values,
            x=day_labels,
            y=heatmap_data.index,
            text=heatmap_labels.values,
            texttemplate="%{text}",
            textfont=dict(color="#07110f", size=10),
            colorscale=[[0, "#e05260"], [.5, "#f2c94c"], [1, "#22c55e"]],
            colorbar=dict(title="Messages", tickformat="~s"),
            xgap=2,
            ygap=2,
            hovertemplate="%{x} · %{y}:00<br>%{z:,.0f} messages<extra></extra>",
        )
    )
    heatmap = style_figure(heatmap, 430)
    heatmap.update_layout(
        title=dict(
            text="Intensity map by day and hour",
            font=dict(color="#ffffff", size=20, family="Space Grotesk"),
            x=0.02,
            xanchor="left",
        )
    )
    st.plotly_chart(heatmap, use_container_width=True)

    st.subheader("Indicator matrix")
    matrix_period = st.segmented_control(
        "Matrix detail", ["Month", "Day", "Hour"], default="Month", key="matrix_period"
    )
    matrix_period = matrix_period or "Month"
    kpi_matrix, average_column = build_kpi_matrix(filtered, matrix_period)
    base_cell_style = "background-color:#070b11;color:#f4f8ff;border-color:#1d2939;"
    green_style = "background-color:#123d2d;color:#7ef0b2;font-weight:700;"
    yellow_style = "background-color:#473817;color:#ffd66b;font-weight:700;"
    red_style = "background-color:#48202a;color:#ff91a0;font-weight:700;"

    def signal_column(series: pd.Series, high_is_good: bool) -> list[str]:
        valid = series.dropna()
        if valid.empty:
            return [base_cell_style] * len(series)

        low = float(valid.quantile(1 / 3))
        high = float(valid.quantile(2 / 3))
        if low == high:
            return [base_cell_style if pd.isna(value) else yellow_style for value in series]

        styles: list[str] = []
        for value in series:
            if pd.isna(value):
                styles.append(base_cell_style)
            elif high_is_good and value >= high or not high_is_good and value <= low:
                styles.append(green_style)
            elif high_is_good and value <= low or not high_is_good and value >= high:
                styles.append(red_style)
            else:
                styles.append(yellow_style)
        return styles

    matrix_style = (
        kpi_matrix.style
        .format(
            {
                "Mensajes": lambda value: format_number(value),
                average_column: lambda value: format_number(value),
                "Participación": "{:.2f}%",
                "Variación": lambda value: "—" if pd.isna(value) else f"{value:+.2f}%",
                "Tasa de fallos": "{:.2f}%",
                "Tasa de exclusión": "{:.2f}%",
                "Facturación": "{:.2f}%",
            }
        )
        .set_properties(**{"background-color": "#070b11", "color": "#f4f8ff", "border-color": "#1d2939"})
        .apply(signal_column, high_is_good=True, subset=["Participación"])
        .apply(signal_column, high_is_good=True, subset=["Variación"])
        .apply(signal_column, high_is_good=False, subset=["Tasa de fallos"])
        .apply(signal_column, high_is_good=False, subset=["Tasa de exclusión"])
        .apply(signal_column, high_is_good=True, subset=["Facturación"])
        .set_table_styles(
            [
                {"selector": "th", "props": [("background-color", "#0d1522"), ("color", "#ffffff"), ("font-weight", "700")]},
                {"selector": "td", "props": [("border-color", "#1d2939")]},
            ]
        )
        .hide(axis="index")
        .set_table_attributes('class="kpi-matrix"')
    )
    matrix_height = min(420, 42 + len(kpi_matrix) * 37)
    scroll_class = " scrollable" if len(kpi_matrix) > 10 else ""
    st.markdown(
        f'<div class="matrix-shell{scroll_class}" style="max-height:{matrix_height}px">{matrix_style.to_html()}</div>',
        unsafe_allow_html=True,
    )

with mix_tab:
    provider_scatter = filtered.copy()
    provider_scatter["provider"] = provider_scatter["provider"].astype("string").fillna("Sin dato").replace("", "Sin dato")
    provider_scatter["mensajes_fallidos"] = (
        provider_scatter["cuenta"] * provider_scatter["failed"].fillna(False).astype(bool)
    )
    provider_scatter = (
        provider_scatter.groupby("provider", as_index=False)
        .agg(Volumen=("cuenta", "sum"), Mensajes_fallidos=("mensajes_fallidos", "sum"))
        .query("Volumen > 0")
    )
    provider_scatter["Tasa de fallos"] = provider_scatter["Mensajes_fallidos"] / provider_scatter["Volumen"] * 100
    provider_scatter["Etiqueta"] = ""
    top_provider_indexes = provider_scatter.nlargest(10, "Volumen").index
    provider_scatter.loc[top_provider_indexes, "Etiqueta"] = provider_scatter.loc[top_provider_indexes, "provider"]

    average_volume = float(provider_scatter["Volumen"].mean())
    average_failure = float(provider_scatter["Tasa de fallos"].mean())
    provider_scatter_chart = px.scatter(
        provider_scatter,
        x="Volumen",
        y="Tasa de fallos",
        size="Volumen",
        color="Tasa de fallos",
        text="Etiqueta",
        hover_name="provider",
        hover_data={"Volumen": ":,.0f", "Tasa de fallos": ":.2f", "Mensajes_fallidos": ":,.0f", "Etiqueta": False},
        size_max=38,
        title="Volumen de SMS vs. tasa de fallos por proveedor",
        color_continuous_scale=[[0, "#22c55e"], [.5, "#f2c94c"], [1, "#e05260"]],
    )
    provider_scatter_chart.update_traces(
        textposition="top center",
        textfont=dict(color="#ffffff", size=10),
        marker=dict(line=dict(color="rgba(255,255,255,.65)", width=1), opacity=.82),
    )
    provider_scatter_chart.add_vline(
        x=average_volume,
        line_width=1.5,
        line_dash="dash",
        line_color="#ffffff",
        annotation_text=f"Volumen promedio · {format_compact(average_volume)}",
        annotation_position="top left",
        annotation_font_color="#ffffff",
    )
    provider_scatter_chart.add_hline(
        y=average_failure,
        line_width=1.5,
        line_dash="dash",
        line_color="#ffffff",
        annotation_text=f"Fallo promedio · {average_failure:.2f}%",
        annotation_position="bottom right",
        annotation_font_color="#ffffff",
    )
    provider_scatter_chart.update_xaxes(title_text="Volumen de SMS", tickformat="~s", type="log")
    provider_scatter_chart.update_yaxes(title_text="Tasa de fallos", ticksuffix="%", tickformat=".2f")
    provider_scatter_chart.update_layout(coloraxis_colorbar=dict(title="Fallos %", ticksuffix="%"))
    st.plotly_chart(style_figure(provider_scatter_chart, 520), use_container_width=True)

    st.subheader("Traffic mix")
    traffic_dimensions = ["provider", "message_type", "billed", "failed"]
    dimension = st.selectbox("Analysis variable", traffic_dimensions, format_func=DIMENSION_LABELS.get)
    breakdown = top_breakdown(filtered, dimension)
    category_chart = px.bar(
        breakdown,
        x="cuenta",
        y=dimension,
        text=[format_compact(value) for value in breakdown["cuenta"]],
        orientation="h",
        title=f"Top 12 · {DIMENSION_LABELS[dimension]}",
        color="cuenta",
        color_continuous_scale=[[0, "#17698e"], [1, COLORS["mint"]]],
    )
    category_chart.update_traces(
        textposition="outside",
        textfont=dict(color="#ffffff", size=12),
        cliponaxis=False,
        hovertemplate=f"%{{y}}<br>%{{x:,.0f}} messages<extra></extra>",
    )
    category_chart.update_layout(coloraxis_showscale=False, margin=dict(l=12, r=82, t=48, b=12))
    st.plotly_chart(style_figure(category_chart, 480), use_container_width=True)

    st.subheader(f"Indicator matrix by {DIMENSION_LABELS[dimension].lower()}")
    dimension_matrix = build_dimension_kpi_matrix(filtered, dimension)
    dimension_matrix_style = (
        dimension_matrix.style
        .format(
            {
                "Mensajes": lambda value: format_number(value),
                "Promedio diario": lambda value: format_number(value),
                "Participación": "{:.2f}%",
                "Variación MTD": lambda value: "—" if pd.isna(value) else f"{value:+.2f}%",
                "Tasa de fallos": "{:.2f}%",
                "Tasa de exclusión": "{:.2f}%",
                "Facturación": "{:.2f}%",
            }
        )
        .set_properties(**{"background-color": "#070b11", "color": "#f4f8ff", "border-color": "#1d2939"})
        .apply(signal_column, high_is_good=True, subset=["Participación"])
        .apply(signal_column, high_is_good=True, subset=["Variación MTD"])
        .apply(signal_column, high_is_good=False, subset=["Tasa de fallos"])
        .apply(signal_column, high_is_good=False, subset=["Tasa de exclusión"])
        .apply(signal_column, high_is_good=True, subset=["Facturación"])
        .set_table_styles(
            [
                {"selector": "th", "props": [("background-color", "#0d1522"), ("color", "#ffffff"), ("font-weight", "700")]},
                {"selector": "td", "props": [("border-color", "#1d2939")]},
            ]
        )
        .hide(axis="index")
        .set_table_attributes('class="kpi-matrix"')
    )
    dimension_matrix_height = min(420, 42 + len(dimension_matrix) * 37)
    dimension_scroll_class = " scrollable" if len(dimension_matrix) > 10 else ""
    st.markdown(
        f'<div class="matrix-shell{dimension_scroll_class}" style="max-height:{dimension_matrix_height}px">{dimension_matrix_style.to_html()}</div>',
        unsafe_allow_html=True,
    )

with quality_tab:
    st.subheader("Quality and delivery")
    quality_kpis = [
        ("Billed", "billed", "✓", True),
        ("Failed", "failed", "!", False),
        ("Excluded", "excluded", "×", False),
        ("Unicode", "is_unicode", "U+", False),
    ]
    quality_cards: list[str] = []
    for label, column, icon, high_is_good in quality_kpis:
        value = weighted_rate(filtered, column)
        benchmark = average_monthly_rate(filtered, column)
        signal_color, signal_label = benchmark_signal(value, benchmark, high_is_good)
        quality_cards.append(
            f'<article class="quality-kpi-card" style="--signal:{signal_color}">'
            f'<div class="quality-kpi-head"><span class="quality-kpi-label">{label}</span>'
            f'<span class="quality-kpi-icon" aria-label="{label}">{icon}</span></div>'
            f'<div class="quality-kpi-value">{value:.2f}%</div>'
            f'<div class="quality-kpi-benchmark">Monthly average · {benchmark:.2f}% · '
            f'<span class="quality-kpi-status">{signal_label}</span></div></article>'
        )
    st.markdown(f'<section class="quality-kpi-grid">{"".join(quality_cards)}</section>', unsafe_allow_html=True)

    quality_left, quality_right = st.columns(2)
    with quality_left:
        reason_chart = px.bar(
            top_breakdown(filtered, "reason", 10),
            x="cuenta",
            y="reason",
            orientation="h",
            title="Main reported reasons",
            color_discrete_sequence=[COLORS["red"]],
        )
        st.plotly_chart(style_figure(reason_chart), use_container_width=True)
    with quality_right:
        segment_chart = px.histogram(
            filtered,
            x="segments",
            y="cuenta",
            histfunc="sum",
            title="Messages by segment count",
            color_discrete_sequence=[COLORS["amber"]],
        )
        st.plotly_chart(style_figure(segment_chart), use_container_width=True)

    failed_heatmap_data = (
        filtered.loc[filtered["failed"].fillna(False)]
        .pivot_table(index="hora", columns="dia_semana", values="cuenta", aggfunc="sum", fill_value=0)
    )
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_labels = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    failed_heatmap_data = failed_heatmap_data.reindex(index=range(24), columns=day_order, fill_value=0)
    failed_heatmap_labels = failed_heatmap_data.map(
        lambda value: f"{value / 1_000_000:.1f}M" if value >= 1_000_000 else f"{value / 1_000:.0f}K"
    )
    failed_heatmap = go.Figure(
        go.Heatmap(
            z=failed_heatmap_data.values,
            x=day_labels,
            y=failed_heatmap_data.index,
            text=failed_heatmap_labels.values,
            texttemplate="%{text}",
            textfont=dict(color="#07110f", size=10),
            colorscale=[[0, "#142b3d"], [.5, "#f2c94c"], [1, "#e05260"]],
            colorbar=dict(title="Failed", tickformat="~s"),
            xgap=2,
            ygap=2,
            hovertemplate="%{x} · %{y}:00<br>%{z:,.0f} failed<extra></extra>",
        )
    )
    failed_heatmap = style_figure(failed_heatmap, 430)
    failed_heatmap.update_layout(
        title=dict(
            text="Failed by day and hour",
            font=dict(color="#ffffff", size=20, family="Space Grotesk"),
            x=0.02,
            xanchor="left",
        )
    )
    st.plotly_chart(failed_heatmap, use_container_width=True)

    character_data = filtered.groupby("total_characters", as_index=False)["cuenta"].sum().sort_values("total_characters")
    character_chart = px.line(
        character_data,
        x="total_characters",
        y="cuenta",
        title="Message length distribution",
        color_discrete_sequence=[COLORS["cyan"]],
    )
    st.plotly_chart(style_figure(character_chart), use_container_width=True)

with insights_tab:
    st.subheader("6 alerts to decide")
    insight_columns = st.columns(3)
    for index, (level, horizon, icon, title, description, color) in enumerate(build_insights(filtered)):
        with insight_columns[index % 3]:
            st.markdown(
                f'<div class="insight" style="--signal:{color}">'
                f'<div class="insight-top"><div class="insight-meta"><span class="insight-icon">{icon}</span>'
                f'<span class="signal">{level}</span></div><span class="insight-horizon">{horizon}</span></div>'
                f'<strong>{title}</strong><p>{description}</p></div>',
                unsafe_allow_html=True,
            )

st.caption("Los indicadores se calculan con SUM(cuenta). Los nuevos CSV se incorporan al recargar la aplicación.")