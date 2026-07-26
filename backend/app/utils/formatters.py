from typing import Any, Optional
import json
from datetime import datetime


def format_tonnes(value: Optional[float], unit: str = "t") -> str:
    if value is None:
        return "N/A"
    if abs(value) >= 1e6:
        return f"{value/1e6:.2f} M{unit}"
    elif abs(value) >= 1e3:
        return f"{value/1e3:.2f} k{unit}"
    return f"{value:.2f} {unit}"


def format_percentage(value: Optional[float]) -> str:
    if value is None:
        return "N/A"
    return f"{value:.2f}%"


def format_ppm(value: Optional[float]) -> str:
    if value is None:
        return "N/A"
    if value >= 1000:
        return f"{value/1000:.2f} wt%"
    return f"{value:.1f} ppm"


def format_currency(value: Optional[float], currency: str = "USD") -> str:
    if value is None:
        return "N/A"
    symbols = {"USD": "$", "EUR": "\u20ac", "GBP": "\u00a3", "CNY": "\u00a5"}
    symbol = symbols.get(currency, currency + " ")
    if abs(value) >= 1e9:
        return f"{symbol}{value/1e9:.2f}B"
    elif abs(value) >= 1e6:
        return f"{symbol}{value/1e6:.2f}M"
    elif abs(value) >= 1e3:
        return f"{symbol}{value/1e3:.2f}K"
    return f"{symbol}{value:.2f}"


def format_date(dt: Optional[datetime], fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    if dt is None:
        return "N/A"
    return dt.strftime(fmt)


def safe_json_dumps(obj: Any) -> str:
    try:
        return json.dumps(obj, default=str)
    except (TypeError, ValueError):
        return "{}"


def truncate_string(s: str, max_length: int = 100) -> str:
    if len(s) <= max_length:
        return s
    return s[:max_length - 3] + "..."
