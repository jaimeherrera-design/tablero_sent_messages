from __future__ import annotations

from html import escape
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data_logic import aggregate_with_variation, current_month_comparison, discover_csv_files, load_and_consolidate


DATA_DIR = Path(__file__).resolve().parent
COLORS = {"mint": "#50E3C2", "cyan": "#44B7F7", "amber": "#FFB547", "red": "#FF6376", "violet": "#C38BFA", "grid": "#253047"}
MONTH_SIGNAL_COLORS = {"mint": "#00E676", "amber": "#FFC107", "red": "#FF1744"}
METRIC_LABELS = {
    "cuenta": "Mensajes",
    "facturados": "Facturados",
    "fallidos": "Fallidos",
    "excluidos": "Excluidos",
}
METRIC_COLORS = {"cuenta": COLORS["cyan"], "facturados": COLORS["mint"], "fallidos": COLORS["red"], "excluidos": COLORS["amber"]}
MONTH_NAMES = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}


st.set_page_config(page_title="Mensajes enviados", page_icon="▥", layout="wide")
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
    :root { color-scheme: dark; }
    .stApp { background: #050708; color: #edf3fc; font-family: 'DM Sans', sans-serif; }
    [data-testid="stAppViewContainer"], [data-testid="stMain"] { background: #050708; }
    [data-testid="stMainBlockContainer"] { max-width: 1440px; padding-top: 28px; padding-bottom: 36px; }
    h1, h2, h3 { font-family: 'Space Grotesk', sans-serif !important; letter-spacing: 0 !important; }
    [data-testid="stHeader"] { background: #0c111c; }
    [data-testid="stSidebar"] { background: #101725; border-right: 1px solid #253047; }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"],
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] > p > strong,
    [data-testid="stSidebar"] [data-testid="stMarkdown"] > [data-testid="stMarkdownContainer"] > p {
        color: #ffffff !important;
    }
    [data-testid="stWidgetLabel"],
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] label {
        color: #ffffff !important;
    }
    [data-testid="stSegmentedControl"] label,
    [data-testid="stSegmentedControl"] p {
        color: #ffffff !important;
    }
    [data-testid="stSegmentedControl"], [data-baseweb="segmented-control"] { padding: 4px; border: 1px solid #1f2a35; border-radius: 10px; background: #090c0f; }
    [data-testid="stSegmentedControl"] [aria-checked="true"],
    [data-testid="stSegmentedControl"] [data-selected="true"],
    [data-baseweb="segmented-control"] [aria-checked="true"] {
        border-radius: 7px !important;
        background: #063d34 !important;
        color: #ffffff !important;
        box-shadow: inset 0 0 0 1px #1ac9a8, 0 4px 12px rgba(0,0,0,.25);
    }
    [data-testid="stVerticalBlockBorderWrapper"] { border-color: #1f2a35 !important; border-radius: 14px !important; background: #090c0f !important; box-shadow: inset 0 1px 0 rgba(255,255,255,.025), 0 10px 24px rgba(0,0,0,.16); }
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p { color: #cbd5e1 !important; }
    [data-testid="stSidebarCollapseButton"] button,
    button[data-testid="stExpandSidebarButton"] {
        width: 44px;
        height: 44px;
        border: 1px solid #50e3c2 !important;
        border-radius: 9px !important;
        background: #063d34 !important;
        color: #55f0d0 !important;
        box-shadow: 0 0 0 1px rgba(80,227,194,.08), 0 8px 22px rgba(0,0,0,.3);
        transition: background-color .18s ease, border-color .18s ease, box-shadow .18s ease, transform .18s ease;
    }
    button[data-testid="stExpandSidebarButton"] { position: relative; top: 19px; left: 6px; }
    [data-testid="stSidebarCollapseButton"] button { position: relative; top: 19px; }
    [data-testid="stSidebarCollapseButton"] button:hover,
    button[data-testid="stExpandSidebarButton"]:hover {
        border-color: #7af7dc !important;
        background: #095246 !important;
        box-shadow: 0 0 0 3px rgba(80,227,194,.16), 0 10px 25px rgba(0,0,0,.34);
    }
    [data-testid="stSidebarCollapseButton"] button:focus-visible,
    button[data-testid="stExpandSidebarButton"]:focus-visible {
        outline: 2px solid #edf3fc !important;
        outline-offset: 3px;
    }
    [data-testid="stSidebarCollapseButton"] button [data-testid="stIconMaterial"],
    button[data-testid="stExpandSidebarButton"] [data-testid="stIconMaterial"] {
        color: #55f0d0 !important;
        font-size: 24px !important;
        font-weight: 600;
    }
    .dashboard-banner { position: relative; overflow: hidden; min-height: 220px; margin-bottom: 20px; padding: 34px 38px; border: 1px solid #1f3432; border-radius: 12px; background: radial-gradient(circle at 78% 42%, rgba(20,94,91,.16), transparent 24%), linear-gradient(90deg, #020607 0%, #03090a 58%, #061312 100%); }
    .banner-content { position: relative; z-index: 2; max-width: 76%; }
    .dashboard-banner .eyebrow { color: #25ebc3; font-size: .78rem; font-weight: 700; letter-spacing: .2em; text-transform: uppercase; }
    .dashboard-banner h1 { margin: 13px 0 8px !important; color: #f5fbfa; font-size: 44px !important; font-weight: 700; line-height: 1.05; }
    .dashboard-banner p { margin: 0; color: #c4cccf; font-size: 1rem; line-height: 1.65; }
    .dashboard-banner strong { color: #50e3c2; }
    .banner-network { position: absolute; z-index: 1; inset: 0 0 0 62%; opacity: .9; }
    .banner-node, .banner-edge { position: absolute; display: block; }
    .banner-node { width: 11px; height: 11px; border-radius: 50%; background: #00b995; box-shadow: 0 0 8px #00b995, 0 0 22px rgba(0,185,149,.78); }
    .banner-node.blue { width: 14px; height: 14px; background: #318cab; box-shadow: 0 0 10px #318cab, 0 0 25px rgba(49,140,171,.7); }
    .banner-edge { height: 1px; background: rgba(0,185,149,.48); transform-origin: left center; }
    .banner-edge.faint { background: rgba(77,135,139,.17); }
    .bn1 { left: 8%; top: 12%; } .bn2 { left: 35%; top: 38%; } .bn3 { left: 68%; top: 8%; }
    .bn4 { left: 89%; top: 43%; } .bn5 { left: 57%; top: 73%; } .bn6 { left: 18%; top: 77%; }
    .be1 { left: 9%; top: 15%; width: 31%; transform: rotate(23deg); }
    .be2 { left: 36%; top: 40%; width: 40%; transform: rotate(-28deg); }
    .be3 { left: 69%; top: 11%; width: 29%; transform: rotate(34deg); }
    .be4 { left: 59%; top: 74%; width: 38%; transform: rotate(-35deg); }
    .be5 { left: 19%; top: 78%; width: 43%; transform: rotate(-11deg); }
    .be6 { left: 36%; top: 42%; width: 37%; transform: rotate(49deg); }
    .be7 { left: 9%; top: 15%; width: 68%; transform: rotate(52deg); }
    .kpi-section { margin: 4px 0 26px; padding: 0; border: 0; border-radius: 0; background: transparent; box-shadow: none; }
    .section-kicker { margin: 0 0 12px 3px; color: #8b98a7; font-size: .72rem; font-weight: 700; letter-spacing: .18em; text-transform: uppercase; }
    .kpi-grid { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 10px; margin: 0; }
    .kpi-card { min-width: 0; min-height: 101px; padding: 12px 13px; border: 1px solid #202a33; border-top: 1px solid #202a33; border-radius: 11px; background: linear-gradient(145deg, #11161a, #0b0e11); box-shadow: 0 8px 18px rgba(0,0,0,.2); }
    .kpi-head { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
    .kpi-label { overflow: hidden; color: #8f98a3; font-size: .78rem; font-weight: 700; text-overflow: ellipsis; white-space: nowrap; }
    .kpi-icon { color: var(--accent); font: 600 22px/1 'Space Grotesk'; }
    .kpi-value { margin-top: 11px; color: var(--accent); font: 600 clamp(1.25rem, 1.7vw, 1.85rem)/1 'Space Grotesk'; white-space: nowrap; }
    .kpi-note { margin-top: 7px; color: #8795aa; font-size: .66rem; }
    .kpi-note strong { color: #7d8792; font-weight: 500; }
    .stTabs { margin-top: 8px; }
    .stTabs [data-baseweb="tab-list"], .stTabs [role="tablist"] { display: flex; gap: 4px; width: 100%; margin-bottom: 28px; padding: 6px; border: 1px solid #33414d !important; border-radius: 14px; background: #090c0f !important; box-shadow: inset 0 1px 0 rgba(255,255,255,.035), 0 8px 22px rgba(0,0,0,.2); }
    .stTabs [data-testid="stTab"] { flex: 1 1 0; height: 48px; min-width: 0; border: 1px solid transparent; border-radius: 9px; color: #8e9aa8; font-weight: 600; transition: background-color .18s ease, border-color .18s ease, color .18s ease; }
    .stTabs [data-testid="stTab"]:hover { color: #ffffff !important; background: #13191e !important; }
    .stTabs [data-testid="stTab"][aria-selected="true"] { position: relative; padding-right: 32px; color: #ffffff !important; border: 0 !important; border-radius: 0 !important; background: transparent !important; box-shadow: none !important; }
    .stTabs [data-baseweb="tab-highlight"], .stTabs .react-aria-SelectionIndicator { display: none !important; }
    .stTabs [data-testid="stTab"][aria-selected="true"]::after { content: "✓"; position: absolute; top: 50%; right: 13px; border: 0 !important; background: transparent !important; color: #13d5af; font-size: 17px; font-weight: 700; line-height: 1; transform: translateY(-50%); }
    .stTabs [data-testid="stTab"] p { color: inherit !important; font-size: .9rem; }
    .stTabs [data-baseweb="tab-panel"], .stTabs [role="tabpanel"] { margin-top: 0; padding: 72px 10px 24px !important; border: 1px solid #1f2a35; border-radius: 22px; background: #07090b !important; box-shadow: inset 0 1px 0 rgba(255,255,255,.02), 0 14px 32px rgba(0,0,0,.18); }
    .matrix-shell { overflow: auto; max-height: 430px; border: 1px solid #29364d; border-radius: 8px; }
    table.kpi-matrix { width: 100%; border-collapse: collapse; background: #070b11; font-size: .8rem; }
    table.kpi-matrix th { position: sticky; top: 0; padding: 10px; background: #0d1522 !important; color: #fff !important; text-align: center; }
    table.kpi-matrix td { padding: 9px 10px; border-bottom: 1px solid #1d2939; color: #f4f8ff; text-align: center; }
    .participation-shell { overflow: auto; max-height: 520px; border: 1px solid #29364d; border-radius: 8px; background: #000000; }
    table.participation-table { width: 100%; border-collapse: collapse; background: #000000 !important; font-size: .8rem; }
    table.participation-table th { position: sticky; z-index: 1; top: 0; padding: 11px 10px; border-bottom: 1px solid #334155; background: #05080d !important; color: #ffffff !important; text-align: center; white-space: nowrap; }
    table.participation-table td { padding: 9px 10px; border-bottom: 1px solid #1d2939; background: #000000 !important; color: #ffffff !important; text-align: center; white-space: nowrap; }
    table.participation-table tbody tr:hover td { background: #101725 !important; }
    .percentage-signal { display: inline-flex; align-items: center; gap: 7px; color: #ffffff; font-weight: 700; }
    .percentage-signal-icon { color: var(--signal); font-size: 14px; line-height: 1; }
    .variation-signal { display: inline-flex; align-items: center; justify-content: center; gap: 6px; color: var(--signal); font-weight: 700; white-space: nowrap; }
    .variation-icon { display: inline-grid; width: 20px; height: 20px; place-items: center; border: 1px solid var(--signal); border-radius: 50%; background: color-mix(in srgb, var(--signal) 14%, transparent); font-size: 11px; line-height: 1; }
    .insight-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }
    .insight { min-height: 170px; padding: 16px; border: 1px solid #29364d; border-left: 4px solid var(--signal); border-radius: 8px; background: #101725; }
    .insight-head { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
    .insight-label { color: #d6dfec; font-size: .76rem; font-weight: 700; text-transform: uppercase; }
    .insight-status { color: var(--signal); font-size: .68rem; font-weight: 700; text-transform: uppercase; }
    .insight strong { display: block; margin: 17px 0 8px; color: #f4f8ff; font-family: 'Space Grotesk'; }
    .insight p { margin: 0; color: #aab5c7; font-size: .86rem; line-height: 1.45; }
    @media (max-width: 1180px) { .kpi-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
    @media (max-width: 1000px) { .kpi-grid, .insight-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
    @media (max-width: 600px) { .kpi-section { padding: 13px; border-radius: 12px; } .kpi-grid, .insight-grid { grid-template-columns: 1fr; } .dashboard-banner { min-height: 210px; padding: 24px 20px; } .banner-content { max-width: 100%; } .dashboard-banner h1 { font-size: 28px !important; } .dashboard-banner p { max-width: 88%; font-size: .84rem; line-height: 1.5; } .banner-network { inset: 40% -15% 0 42%; opacity: .32; } }
    </style>
    """,
    unsafe_allow_html=True,
)


def format_number(value: float) -> str:
    return f"{value:,.0f}".replace(",", ".")


def format_pct(value: float | None, signed: bool = False) -> str:
    if value is None or pd.isna(value):
        return "Sin base"
    pattern = "+.2f" if signed else ".2f"
    return f"{value:{pattern}}%".replace(".", ",")


@st.cache_data(show_spinner="Consolidando archivos CSV...")
def load_data(file_signature: tuple[tuple[str, int, int], ...]) -> pd.DataFrame:
    return load_and_consolidate(DATA_DIR / name for name, _, _ in file_signature)


def style_figure(figure: go.Figure, height: int = 390) -> go.Figure:
    figure.update_layout(
        height=height,
        margin=dict(l=12, r=12, t=58, b=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color="#FFFFFF"),
        title_font=dict(family="Space Grotesk", size=17, color="#FFFFFF"),
        legend=dict(font=dict(color="#FFFFFF"), title_font=dict(color="#FFFFFF")),
        legend_title_text="",
        hoverlabel=dict(bgcolor="#101725", font_color="#FFFFFF"),
    )
    figure.update_xaxes(gridcolor=COLORS["grid"], zeroline=False, title_font=dict(color="#FFFFFF"), tickfont=dict(color="#FFFFFF"))
    figure.update_yaxes(gridcolor=COLORS["grid"], zeroline=False, title_font=dict(color="#FFFFFF"), tickfont=dict(color="#FFFFFF"))
    return figure


def rate(frame: pd.DataFrame, metric: str) -> float:
    total = float(frame["cuenta"].sum())
    return float(frame[metric].sum() / total * 100) if total else 0.0


def progress_cell_style(value: float, maximum: float, average: float, high_is_good: bool) -> str:
    if pd.isna(value):
        return ""
    if high_is_good:
        color = COLORS["mint"] if value > average * 1.05 else COLORS["red"] if value < average * 0.95 else COLORS["amber"]
    else:
        color = COLORS["red"] if value > average * 1.05 else COLORS["mint"] if value < average * 0.95 else COLORS["amber"]
    width = min(max(value / maximum * 100, 0), 100) if maximum else 0
    return f"background:linear-gradient(90deg,{color}99 0%,{color}99 {width:.1f}%,transparent {width:.1f}%,transparent 100%) !important;color:#ffffff;font-weight:700"


def format_percentage_signal(value: float, maximum: float, average: float, high_is_good: bool) -> str:
    if pd.isna(value):
        return ""
    if high_is_good:
        color = COLORS["mint"] if value > average * 1.05 else COLORS["red"] if value < average * 0.95 else COLORS["amber"]
    else:
        color = COLORS["red"] if value > average * 1.05 else COLORS["mint"] if value < average * 0.95 else COLORS["amber"]
    return f'<span class="percentage-signal" style="--signal:{color}"><span class="percentage-signal-icon">●</span>{format_pct(value)}</span>'


def format_variation(value: float) -> str:
    if pd.isna(value):
        return ""
    if value > 0:
        color, icon = COLORS["mint"], "▲"
    elif value < 0:
        color, icon = COLORS["red"], "▼"
    else:
        color, icon = COLORS["amber"], "•"
    return f'<span class="variation-signal" style="--signal:{color}"><span class="variation-icon">{icon}</span>{value:+.2f}%</span>'


def build_matrix(frame: pd.DataFrame, period_label: str) -> pd.DataFrame:
    period = {"Mes": "mes", "Día": "fecha", "Hora": "hora"}[period_label]
    matrix = frame.groupby(period, as_index=False)[list(METRIC_LABELS)].sum().sort_values(period)
    if period_label == "Mes":
        matrix["Periodo"] = matrix[period].map(lambda value: f"{MONTH_NAMES[value.month]} {value.year}")
    elif period_label == "Día":
        matrix["Periodo"] = matrix[period].dt.strftime("%d/%m/%Y")
    else:
        matrix["Periodo"] = matrix[period].map(lambda value: f"{int(value):02d}:00")
    matrix["% Facturados"] = matrix["facturados"].div(matrix["cuenta"]).mul(100)
    matrix["% Fallidos"] = matrix["fallidos"].div(matrix["cuenta"]).mul(100)
    matrix["% Excluidos"] = matrix["excluidos"].div(matrix["cuenta"]).mul(100)
    matrix["Variación mensajes"] = matrix["cuenta"].pct_change(fill_method=None).mul(100)
    matrix = matrix.rename(columns=METRIC_LABELS)
    return matrix[["Periodo", "Mensajes", "Variación mensajes", "Facturados", "% Facturados", "Fallidos", "% Fallidos", "Excluidos", "% Excluidos"]]


def build_heatmap(frame: pd.DataFrame, metric: str, as_rate: bool) -> go.Figure:
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_labels = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    values = frame.pivot_table(index="hora", columns="dia_semana", values=metric, aggfunc="sum", fill_value=0).reindex(index=range(24), columns=day_order, fill_value=0)
    if as_rate:
        totals = frame.pivot_table(index="hora", columns="dia_semana", values="cuenta", aggfunc="sum", fill_value=0).reindex(index=range(24), columns=day_order, fill_value=0)
        values = values.div(totals.where(totals.gt(0))).mul(100).fillna(0)
        labels = values.map(lambda value: f"{value:.2f}%")
        title, colorbar, hover = f"Tasa de {METRIC_LABELS[metric].lower()} por día y hora", dict(title=dict(text="Tasa", font=dict(color="#FFFFFF")), tickfont=dict(color="#FFFFFF"), ticksuffix="%"), "%{x} · %{y}:00<br>%{z:.2f}%<extra></extra>"
    else:
        labels = values.map(lambda value: f"{value / 1_000_000:.1f}M" if value >= 1_000_000 else f"{value / 1_000:.0f}K" if value >= 1_000 else f"{value:.0f}")
        title, colorbar, hover = f"Intensidad de {METRIC_LABELS[metric].lower()} por día y hora", dict(title=dict(text=METRIC_LABELS[metric], font=dict(color="#FFFFFF")), tickfont=dict(color="#FFFFFF"), tickformat="~s"), "%{x} · %{y}:00<br>%{z:,.0f}<extra></extra>"
    scale = [[0, "#162132"], [.5, COLORS["amber"]], [1, COLORS["red"] if metric in {"fallidos", "excluidos"} else COLORS["mint"]]]
    figure = go.Figure(go.Heatmap(z=values.values, x=day_labels, y=values.index, text=labels.values, texttemplate="%{text}", textfont=dict(color="#FFFFFF"), colorscale=scale, colorbar=colorbar, xgap=2, ygap=2, hovertemplate=hover))
    figure = style_figure(figure, 455)
    figure.update_layout(title=dict(text=title, font=dict(family="Space Grotesk", size=17, color="#FFFFFF")))
    return figure


def build_insights(frame: pd.DataFrame, comparison_frame: pd.DataFrame) -> list[tuple[str, str, str, str, str]]:
    total = float(frame["cuenta"].sum())
    billed_rate = rate(frame, "facturados")
    failed_rate = rate(frame, "fallidos")
    excluded_rate = rate(frame, "excluidos")
    comparison = current_month_comparison(comparison_frame, "cuenta")
    daily = frame.groupby("fecha", as_index=False)["cuenta"].sum()
    hourly = frame.groupby("hora", as_index=False)["cuenta"].sum()
    providers = frame.groupby("provider", as_index=False)["cuenta"].sum().sort_values("cuenta", ascending=False)
    peak_day, peak_hour, top_provider = daily.loc[daily["cuenta"].idxmax()], hourly.loc[hourly["cuenta"].idxmax()], providers.iloc[0]
    peak_hour_share = float(peak_hour["cuenta"] / total * 100) if total else 0.0
    top_provider_share = float(top_provider["cuenta"] / total * 100) if total else 0.0
    variation = comparison["variation"]
    trend_status = "Sin base" if variation is None else "Al alza" if variation > 5 else "A la baja" if variation < -5 else "Estable"
    trend_color = COLORS["amber"] if variation is None else COLORS["mint"] if variation >= -5 else COLORS["red"]
    failed_status, failed_color = ("Atención", COLORS["red"]) if failed_rate > 1 else ("Controlado", COLORS["mint"])
    return [
        ("Volumen MTD", trend_status, f"Variación {format_pct(variation, True)}", f"{format_number(float(comparison['current']))} mensajes frente a {format_number(float(comparison['previous']))} al mismo corte del mes anterior.", trend_color),
        ("Facturación", "Participación", format_pct(billed_rate), "Porcentaje de mensajes facturados sobre el total del periodo filtrado.", COLORS["mint"]),
        ("Fallidos", failed_status, format_pct(failed_rate), "Tasa de mensajes fallidos. Revise proveedores y franjas con mayor concentración.", failed_color),
        ("Excluidos", "Participación", format_pct(excluded_rate), "Porcentaje de mensajes excluidos sobre el total filtrado.", COLORS["amber"]),
        ("Pico diario", "Volumen", f"{peak_day['fecha']:%d/%m/%Y}", f"El mayor volumen diario fue de {format_number(float(peak_day['cuenta']))} mensajes.", COLORS["amber"]),
        ("Pico horario", "Concentración", f"{int(peak_hour['hora']):02d}:00", f"Esta hora concentra {format_pct(peak_hour_share)} del volumen seleccionado.", COLORS["violet"]),
        ("Proveedor principal", "Participación", escape(str(top_provider["provider"])), f"Concentra {format_pct(top_provider_share)} del total de mensajes filtrados.", COLORS["cyan"]),
    ]


files = discover_csv_files(DATA_DIR)
if not files:
    st.error("No se encontraron archivos CSV en la carpeta del proyecto.")
    st.stop()
signature = tuple((path.name, path.stat().st_mtime_ns, path.stat().st_size) for path in files)
try:
    data = load_data(signature)
except (ValueError, pd.errors.ParserError, UnicodeDecodeError) as error:
    st.error(f"No fue posible consolidar los CSV: {error}")
    st.stop()
if data.empty:
    st.warning("Los archivos no contienen registros válidos.")
    st.stop()

with st.sidebar:
    st.markdown("## Filtros")
    min_date, max_date = data["fecha"].min().date(), data["fecha"].max().date()
    st.markdown("**Periodo de análisis**")
    date_mode = st.segmented_control(
        "Fechas", ["Todas", "Una fecha", "Rango"], default="Todas", key="date_mode"
    ) or "Todas"
    if date_mode == "Una fecha":
        single_date = st.date_input(
            "Fecha", value=max_date, min_value=min_date, max_value=max_date, key="single_date"
        )
        start_date = end_date = pd.Timestamp(single_date)
    elif date_mode == "Rango":
        range_left, range_right = st.columns(2)
        with range_left:
            range_start = st.date_input(
                "Desde", value=min_date, min_value=min_date, max_value=max_date, key="range_start"
            )
        with range_right:
            range_end = st.date_input(
                "Hasta", value=max_date, min_value=min_date, max_value=max_date, key="range_end"
            )
        start_date, end_date = pd.Timestamp(range_start), pd.Timestamp(range_end)
    else:
        start_date, end_date = pd.Timestamp(min_date), pd.Timestamp(max_date)
    available_months = sorted(data["fecha"].dt.to_period("M").unique())
    month_options: dict[str, pd.Period | None] = {"Todos los meses": None}
    month_options.update({f"{MONTH_NAMES[month.month]} {month.year}": month for month in available_months})
    selected_month_label = st.selectbox("Mes", list(month_options))
    selected_month = month_options[selected_month_label]
    selected_providers = st.multiselect("Proveedor", sorted(data["provider"].unique()))
    selected_types = st.multiselect("Tipo de mensaje", sorted(data["message_type"].unique()))
    selected_aliases = st.multiselect("Alias proveedor", sorted(data["alias_provider"].unique()))
    selected_networks = st.multiselect("Red", sorted(data["network_id"].unique()))
    selected_reasons = st.multiselect("Motivo", sorted(data["reason"].unique()))
    st.divider()
    st.caption(f"{len(files)} archivo(s) consolidado(s)")
    st.caption(f"Último registro: {data['fecha_hora'].max():%d/%m/%Y %H:%M}")

dimension_filtered = data.copy()
for column, selected in {"provider": selected_providers, "message_type": selected_types, "alias_provider": selected_aliases, "network_id": selected_networks, "reason": selected_reasons}.items():
    if selected:
        dimension_filtered = dimension_filtered[dimension_filtered[column].isin(selected)]
if start_date > end_date:
    st.sidebar.error("La fecha 'Desde' no puede ser posterior a 'Hasta'.")
    st.stop()
filtered = dimension_filtered[dimension_filtered["fecha"].between(start_date, end_date)].copy()
if selected_month is not None:
    filtered = filtered[filtered["fecha"].dt.to_period("M").eq(selected_month)]
if filtered.empty:
    st.warning("No hay datos para la combinación de filtros seleccionada.")
    st.stop()

st.markdown(
    f"""
    <section class="dashboard-banner">
        <div class="banner-content">
            <span class="eyebrow">▥ &nbsp; Analítica de envíos</span>
            <h1>Mensajes enviados</h1>
            <p>Monitoreo consolidado &nbsp;|&nbsp; Periodo analizado: <strong>{filtered['fecha'].min():%d/%m/%Y} → {filtered['fecha'].max():%d/%m/%Y}</strong> &nbsp;|&nbsp; <strong>{len(files)}</strong> CSV consolidado(s) &nbsp;|&nbsp; Último registro: <strong>{filtered['fecha_hora'].max():%d/%m/%Y %H:%M}</strong></p>
        </div>
        <div class="banner-network" aria-hidden="true">
            <span class="banner-edge be1"></span><span class="banner-edge be2"></span>
            <span class="banner-edge be3 faint"></span><span class="banner-edge be4"></span>
            <span class="banner-edge be5"></span><span class="banner-edge be6 faint"></span>
            <span class="banner-edge be7 faint"></span>
            <span class="banner-node bn1"></span><span class="banner-node blue bn2"></span>
            <span class="banner-node bn3"></span><span class="banner-node bn4"></span>
            <span class="banner-node blue bn5"></span><span class="banner-node bn6"></span>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

totals = {metric: float(filtered[metric].sum()) for metric in METRIC_LABELS}
billed_rate, failed_rate, excluded_rate = (rate(filtered, metric) for metric in ("facturados", "fallidos", "excluidos"))
comparison_data = dimension_filtered[dimension_filtered["fecha"].le(filtered["fecha"].max())]
comparisons = {metric: current_month_comparison(comparison_data, metric) for metric in METRIC_LABELS}
cards = [
    ("Total de mensajes", format_number(totals["cuenta"]), "Σ", COLORS["cyan"], f"MTD vs. mes anterior: {format_pct(comparisons['cuenta']['variation'], True)}"),
    ("Facturados", format_number(totals["facturados"]), "↗", COLORS["mint"], f"MTD vs. mes anterior: {format_pct(comparisons['facturados']['variation'], True)}"),
    ("Fallidos", format_number(totals["fallidos"]), "!", COLORS["red"], f"MTD vs. mes anterior: {format_pct(comparisons['fallidos']['variation'], True)}"),
    ("% facturados", format_pct(billed_rate), "%", COLORS["mint"], "Sobre el total filtrado"),
    ("% fallidos", format_pct(failed_rate), "%", COLORS["red"], "Sobre el total filtrado"),
    ("% excluidos", format_pct(excluded_rate), "%", COLORS["amber"], f"{format_number(totals['excluidos'])} mensajes excluidos"),
]
card_html = "".join(f'<article class="kpi-card" style="--accent:{color}"><div class="kpi-head"><span class="kpi-label">{label}</span><span class="kpi-icon">{icon}</span></div><div class="kpi-value">{value}</div><div class="kpi-note"><strong>{note}</strong></div></article>' for label, value, icon, color, note in cards)
st.markdown(f'<section class="kpi-section"><div class="section-kicker">Indicadores clave de gestión</div><div class="kpi-grid">{card_html}</div></section>', unsafe_allow_html=True)

evolution_tab, participation_tab, heatmap_tab, insights_tab = st.tabs(["📊 Evolución y variaciones", "🏛 Participación", "🧑‍💼 Mapas de calor", "💡 Insights"])
with evolution_tab:
    control_left, control_right = st.columns(2)
    with control_left:
        period_label = st.segmented_control("Granularidad", ["Mes", "Día", "Hora"], default="Mes") or "Mes"
    with control_right:
        selected_metric = st.selectbox("Métrica", list(METRIC_LABELS), format_func=METRIC_LABELS.get)
    period = {"Mes": "mes", "Día": "fecha", "Hora": "hora"}[period_label]
    timeline = aggregate_with_variation(filtered, period, selected_metric)
    if period_label == "Mes":
        timeline["Periodo"] = timeline[period].map(lambda value: f"{MONTH_NAMES[value.month]} {value.year}")
    elif period_label == "Día":
        timeline["Periodo"] = timeline["fecha"]
    elif period_label == "Hora":
        timeline["Periodo"] = timeline[period].map(lambda value: f"{int(value):02d}:00")
    chart_left, chart_right = st.columns([1.6, 1])
    with chart_left:
        if period_label == "Mes":
            volume_chart = px.bar(timeline, x="Periodo", y=selected_metric, text_auto="~s", title=f"{METRIC_LABELS[selected_metric]} por {period_label.lower()}", color_discrete_sequence=[METRIC_COLORS[selected_metric]])
        else:
            volume_chart = px.line(timeline, x="Periodo", y=selected_metric, markers=True, title=f"{METRIC_LABELS[selected_metric]} por {period_label.lower()}")
        if period_label == "Mes":
            monthly_average = float(timeline[selected_metric].mean())
            if selected_metric in {"fallidos", "excluidos"}:
                bar_colors = [
                    MONTH_SIGNAL_COLORS["red"] if value > monthly_average * 1.05
                    else MONTH_SIGNAL_COLORS["mint"] if value < monthly_average * 0.95
                    else MONTH_SIGNAL_COLORS["amber"]
                    for value in timeline[selected_metric]
                ]
            else:
                bar_colors = [
                    MONTH_SIGNAL_COLORS["mint"] if value > monthly_average * 1.05
                    else MONTH_SIGNAL_COLORS["red"] if value < monthly_average * 0.95
                    else MONTH_SIGNAL_COLORS["amber"]
                    for value in timeline[selected_metric]
                ]
            volume_chart.update_traces(marker_color=bar_colors, marker_line_color=bar_colors)
        else:
            period_average = float(timeline[selected_metric].mean())
            if selected_metric in {"fallidos", "excluidos"}:
                signal_colors = [
                    MONTH_SIGNAL_COLORS["red"] if value > period_average * 1.05
                    else MONTH_SIGNAL_COLORS["mint"] if value < period_average * 0.95
                    else MONTH_SIGNAL_COLORS["amber"]
                    for value in timeline[selected_metric]
                ]
            else:
                signal_colors = [
                    MONTH_SIGNAL_COLORS["mint"] if value > period_average * 1.05
                    else MONTH_SIGNAL_COLORS["red"] if value < period_average * 0.95
                    else MONTH_SIGNAL_COLORS["amber"]
                    for value in timeline[selected_metric]
                ]
            volume_chart.update_traces(marker=dict(color=signal_colors, size=8), line=dict(color="#64748B", width=2))
        if period_label == "Mes":
            volume_chart.update_traces(textposition="outside", cliponaxis=False)
        else:
            volume_chart.update_traces(cliponaxis=False)
        if period_label == "Día":
            volume_chart.update_xaxes(
                title_text="Fecha",
                tickformat="%d/%m",
                nticks=12,
            )
        with st.container(border=True):
            st.plotly_chart(style_figure(volume_chart), width="stretch")
    with chart_right:
        variation = timeline.dropna(subset=["variacion"])
        variation_chart = px.bar(variation, x="Periodo", y="variacion", text=[f"{value:+.2f}%" for value in variation["variacion"]], title="Variación vs. periodo anterior", color="variacion", color_continuous_scale=[[0, COLORS["red"]], [.5, COLORS["amber"]], [1, COLORS["mint"]]], color_continuous_midpoint=0)
        if period_label == "Mes":
            variation_colors = [
                MONTH_SIGNAL_COLORS["mint"] if value > 5 else MONTH_SIGNAL_COLORS["red"] if value < -5 else MONTH_SIGNAL_COLORS["amber"]
                for value in variation["variacion"]
            ]
            variation_chart.update_traces(marker_color=variation_colors, marker_line_color=variation_colors)
        variation_chart.update_traces(textposition="outside", cliponaxis=False)
        variation_chart.update_layout(coloraxis_showscale=False)
        variation_chart.update_yaxes(ticksuffix="%")
        if period_label == "Día":
            variation_chart.update_xaxes(
                title_text="Fecha",
                tickformat="%d/%m",
                nticks=12,
            )
        with st.container(border=True):
            st.plotly_chart(style_figure(variation_chart), width="stretch")
    matrix_period = st.segmented_control("Detalle", ["Mes", "Día", "Hora"], default="Mes", key="matrix_period") or "Mes"
    matrix = build_matrix(filtered, matrix_period)
    billed_max = float(matrix["% Facturados"].max())
    billed_average = float(matrix["% Facturados"].mean())
    failed_max = float(matrix["% Fallidos"].max())
    failed_average = float(matrix["% Fallidos"].mean())
    excluded_max = float(matrix["% Excluidos"].max())
    excluded_average = float(matrix["% Excluidos"].mean())
    matrix_percentage_formatters = {
        "% Facturados": lambda value: format_percentage_signal(value, billed_max, billed_average, True),
        "% Fallidos": lambda value: format_percentage_signal(value, failed_max, failed_average, False),
        "% Excluidos": lambda value: format_percentage_signal(value, excluded_max, excluded_average, False),
    }
    matrix_style = (
        matrix.style
        .format({"Mensajes": format_number, "Facturados": format_number, "Fallidos": format_number, "Excluidos": format_number, **matrix_percentage_formatters, "Variación mensajes": format_variation}, escape=None)
        .hide(axis="index")
        .set_table_attributes('class="kpi-matrix"')
    )
    with st.container(border=True):
        st.subheader("Matriz de indicadores")
        st.markdown(f'<div class="matrix-shell">{matrix_style.to_html()}</div>', unsafe_allow_html=True)

with participation_tab:
    participation_control_left, participation_control_right = st.columns(2)
    with participation_control_left:
        dimension_label = st.segmented_control("Dimensión", ["Proveedor", "Tipo", "Alias", "Red", "Motivo"], default="Proveedor") or "Proveedor"
    with participation_control_right:
        y_axis_options = {
            "% fallidos": "% Fallidos",
            "% facturados": "% Facturados",
            "% excluidos": "% Excluidos",
        }
        selected_y_label = st.selectbox("Indicador eje Y", list(y_axis_options))
        selected_y_metric = y_axis_options[selected_y_label]
    dimension = {"Proveedor": "provider", "Tipo": "message_type", "Alias": "alias_provider", "Red": "network_id", "Motivo": "reason"}[dimension_label]
    participation = filtered.groupby(dimension, as_index=False)[list(METRIC_LABELS)].sum()
    participation["Participación"] = participation["cuenta"].div(participation["cuenta"].sum()).mul(100)
    participation["% Facturados"] = participation["facturados"].div(participation["cuenta"]).mul(100)
    participation["% Fallidos"] = participation["fallidos"].div(participation["cuenta"]).mul(100)
    participation["% Excluidos"] = participation["excluidos"].div(participation["cuenta"]).mul(100)
    participation = participation.sort_values("cuenta", ascending=False)
    total_messages = float(participation["cuenta"].sum())
    average_messages = float(participation["cuenta"].mean())
    if selected_y_metric == "% Fallidos":
        global_indicator = float(participation["fallidos"].sum() / total_messages * 100) if total_messages else 0.0
        color_scale = [[0, COLORS["mint"]], [.5, COLORS["amber"]], [1, COLORS["red"]]]
        y_axis_title, y_suffix = "% fallidos", "%"
        global_label = f"Tasa global · {format_pct(global_indicator)}"
    elif selected_y_metric == "% Facturados":
        global_indicator = float(participation["facturados"].sum() / total_messages * 100) if total_messages else 0.0
        color_scale = [[0, COLORS["red"]], [.5, COLORS["amber"]], [1, COLORS["mint"]]]
        y_axis_title, y_suffix = "% facturados", "%"
        global_label = f"Tasa global · {format_pct(global_indicator)}"
    else:
        global_indicator = float(participation["excluidos"].sum() / total_messages * 100) if total_messages else 0.0
        color_scale = [[0, COLORS["mint"]], [.5, COLORS["amber"]], [1, COLORS["red"]]]
        y_axis_title, y_suffix = "% excluidos", "%"
        global_label = f"Tasa global · {format_pct(global_indicator)}"
    participation_chart = px.scatter(
        participation,
        x="cuenta",
        y=selected_y_metric,
        hover_name=dimension,
        color=selected_y_metric,
        color_continuous_scale=color_scale,
        hover_data={
            "cuenta": ":,.0f",
            "% Fallidos": ":.2f",
            "% Facturados": ":.2f",
            "% Excluidos": ":.2f",
            "Participación": ":.2f",
        },
        labels={"cuenta": "Mensajes", selected_y_metric: y_axis_title},
        title=f"Mensajes vs. {selected_y_label.lower()} por {dimension_label.lower()}",
    )
    participation_chart.update_traces(marker=dict(size=11, line=dict(width=1, color="#0C111C")))
    participation_chart.add_vline(
        x=average_messages,
        line_width=2,
        line_dash="dash",
        line_color=COLORS["cyan"],
        annotation_text=f"Promedio mensajes · {format_number(average_messages)}",
        annotation_position="top right",
                annotation_font_color="#FFFFFF",
    )
    participation_chart.add_hline(
        y=global_indicator,
        line_width=2,
        line_dash="dash",
        line_color=COLORS["amber"],
        annotation_text=global_label,
        annotation_position="bottom right",
        annotation_font_color="#FFFFFF",
    )
    participation_chart.update_xaxes(tickformat="~s")
    participation_chart.update_yaxes(ticksuffix=y_suffix)
    participation_chart.update_layout(coloraxis_colorbar=dict(title=dict(text=y_axis_title, font=dict(color="#FFFFFF")), tickfont=dict(color="#FFFFFF"), ticksuffix=y_suffix))
    with st.container(border=True):
        st.plotly_chart(style_figure(participation_chart, 500), width="stretch")
    display_participation = participation.rename(columns={dimension: dimension_label, **METRIC_LABELS})
    display_participation[dimension_label] = display_participation[dimension_label].map(lambda value: escape(str(value)))
    participation_columns = [dimension_label, "Mensajes", "Participación", "Facturados", "% Facturados", "Fallidos", "% Fallidos", "Excluidos", "% Excluidos"]
    participation_percentage_columns = {
        "Participación": True,
        "% Facturados": True,
        "% Fallidos": False,
        "% Excluidos": False,
    }
    participation_percentage_formatters = {
        column: lambda value, column=column, high_is_good=high_is_good: format_percentage_signal(
            value,
            float(display_participation[column].max()),
            float(display_participation[column].mean()),
            high_is_good,
        )
        for column, high_is_good in participation_percentage_columns.items()
    }
    participation_style = (
        display_participation[participation_columns].style
        .format({
            "Mensajes": format_number,
            **participation_percentage_formatters,
            "Facturados": format_number,
            "Fallidos": format_number,
            "Excluidos": format_number,
        }, escape=None)
    )
    participation_style = participation_style.hide(axis="index").set_table_attributes('class="participation-table"')
    with st.container(border=True):
        st.markdown(f'<div class="participation-shell">{participation_style.to_html()}</div>', unsafe_allow_html=True)

with heatmap_tab:
    heatmap_metric = st.selectbox("Métrica de volumen", list(METRIC_LABELS), format_func=METRIC_LABELS.get, key="heatmap_metric")
    with st.container(border=True):
        st.plotly_chart(build_heatmap(filtered, heatmap_metric, False), width="stretch")
    rate_metric = st.segmented_control("Tasa", ["facturados", "fallidos", "excluidos"], default="fallidos", format_func=METRIC_LABELS.get) or "fallidos"
    with st.container(border=True):
        st.plotly_chart(build_heatmap(filtered, rate_metric, True), width="stretch")

with insights_tab:
    with st.container(border=True):
        st.subheader("Señales operativas")
        insight_cards = "".join(f'<article class="insight" style="--signal:{color}"><div class="insight-head"><span class="insight-label">{label}</span><span class="insight-status">{status}</span></div><strong>{title}</strong><p>{description}</p></article>' for label, status, title, description, color in build_insights(filtered, comparison_data))
        st.markdown(f'<section class="insight-grid">{insight_cards}</section>', unsafe_allow_html=True)

st.caption("Los mensajes se suman desde cuenta; facturados, fallidos y excluidos se calculan ponderando sus indicadores por cuenta. Los CSV de la raíz se consolidan automáticamente.")