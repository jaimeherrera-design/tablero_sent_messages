from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd


REQUIRED_COLUMNS = {
    "fecha",
    "hora",
    "billed",
    "provider",
    "segments",
    "segment_number",
    "is_unicode",
    "failed",
    "excluded",
    "reason",
    "total_characters",
    "message_type",
    "alias_provider",
    "cuenta",
}

BOOLEAN_COLUMNS = ["billed", "is_unicode", "failed", "excluded"]
NUMERIC_COLUMNS = ["hora", "segments", "segment_number", "total_characters", "cuenta"]


def discover_csv_files(data_dir: Path) -> list[Path]:
    return sorted(path for path in data_dir.glob("*.csv") if path.is_file())


def _normalize_boolean(series: pd.Series) -> pd.Series:
    normalized = series.astype("string").str.strip().str.lower()
    return normalized.map({"true": True, "false": False, "1": True, "0": False}).astype("boolean")


def load_and_consolidate(files: Iterable[Path]) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []

    for source_order, path in enumerate(sorted(files)):
        frame = pd.read_csv(path, low_memory=False)
        missing = REQUIRED_COLUMNS.difference(frame.columns)
        if missing:
            missing_names = ", ".join(sorted(missing))
            raise ValueError(f"{path.name} no contiene las columnas requeridas: {missing_names}")

        frame["fecha"] = pd.to_datetime(frame["fecha"], errors="coerce")
        for column in NUMERIC_COLUMNS:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
        for column in BOOLEAN_COLUMNS:
            frame[column] = _normalize_boolean(frame[column])

        frame = frame.dropna(subset=["fecha", "cuenta"])
        frame["cuenta"] = frame["cuenta"].clip(lower=0)
        frame["_source_order"] = source_order
        frame["_source_file"] = path.name
        frames.append(frame)

    if not frames:
        return pd.DataFrame()

    combined = pd.concat(frames, ignore_index=True)
    source_columns = {"cuenta", "_source_order", "_source_file"}
    dimension_columns = [column for column in combined.columns if column not in source_columns]

    # Aggregate repeated keys inside each export, then let the newest export replace overlaps.
    combined = (
        combined.groupby(dimension_columns + ["_source_order", "_source_file"], dropna=False, as_index=False)[
            "cuenta"
        ]
        .sum()
        .sort_values("_source_order")
        .drop_duplicates(subset=dimension_columns, keep="last")
    )

    combined["hora"] = combined["hora"].fillna(0).astype(int).clip(0, 23)
    combined["mes"] = combined["fecha"].dt.to_period("M").dt.to_timestamp()
    combined["dia"] = combined["fecha"].dt.day
    combined["dia_semana"] = combined["fecha"].dt.day_name(locale="C")
    combined["fecha_hora"] = combined["fecha"] + pd.to_timedelta(combined["hora"], unit="h")
    return combined.sort_values(["fecha", "hora"]).reset_index(drop=True)


def percent_change(current: float, previous: float) -> float | None:
    if previous == 0:
        return None
    return (current - previous) / previous * 100


def current_month_comparison(frame: pd.DataFrame) -> dict[str, float | int | pd.Timestamp | None]:
    if frame.empty:
        return {
            "current": 0.0,
            "previous": 0.0,
            "variation": None,
            "cutoff_day": 0,
            "current_month": None,
            "previous_month": None,
        }

    max_date = frame["fecha"].max()
    current_month = max_date.to_period("M")
    previous_month = current_month - 1
    cutoff_day = int(max_date.day)

    current_mask = frame["fecha"].dt.to_period("M").eq(current_month) & frame["dia"].le(cutoff_day)
    previous_mask = frame["fecha"].dt.to_period("M").eq(previous_month) & frame["dia"].le(cutoff_day)
    current = float(frame.loc[current_mask, "cuenta"].sum())
    previous = float(frame.loc[previous_mask, "cuenta"].sum())

    return {
        "current": current,
        "previous": previous,
        "variation": percent_change(current, previous),
        "cutoff_day": cutoff_day,
        "current_month": current_month.to_timestamp(),
        "previous_month": previous_month.to_timestamp(),
    }


def aggregate_with_variation(frame: pd.DataFrame, period: str) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=[period, "cuenta", "variacion"])

    if period == "mes":
        grouped = frame.groupby("mes", as_index=False)["cuenta"].sum().sort_values("mes")
    elif period == "fecha":
        grouped = frame.groupby("fecha", as_index=False)["cuenta"].sum().sort_values("fecha")
    elif period == "hora":
        grouped = frame.groupby("hora", as_index=False)["cuenta"].sum().sort_values("hora")
    else:
        raise ValueError(f"Periodo no soportado: {period}")

    grouped["variacion"] = grouped["cuenta"].pct_change(fill_method=None) * 100
    return grouped