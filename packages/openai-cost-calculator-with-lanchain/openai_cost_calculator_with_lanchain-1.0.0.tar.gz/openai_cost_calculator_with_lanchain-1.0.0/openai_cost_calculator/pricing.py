"""
Remote CSV → in-memory dict  (with a tiny 24-hour cache).
The CSV **no longer** has a Token-Type column – every row is Text.
"""

from __future__ import annotations

import csv
import io
import time
import threading
from typing import Dict, Tuple, Iterable, Mapping, Optional
import requests

_PRICING_CSV_URL = (
    "https://raw.githubusercontent.com/orkunkinay/openai_cost_calculator/refs/heads/main/data/gpt_pricing_data.csv"
)

# Existing cache for remote CSV
_CACHE: Dict[Tuple[str, str], dict] | None = None
_CACHE_TS = 0
_TTL = 60 * 60 * 24  # 24h

# local, in-process overrides
# Keys match your finder: (model_name, model_date) with YYYY-MM-DD dates.
_LOCAL_OVERRIDES: Dict[Tuple[str, str], dict] = {}
_LOCK = threading.RLock()
_OFFLINE_ONLY = False  # if True, never fetch remote CSV

def _validate_date_str(date: str) -> None:
    # very lightweight guard
    if not isinstance(date, str) or len(date) != 10:
        raise ValueError("model_date must be 'YYYY-MM-DD'")
    y, m, d = date.split("-")
    if not (y.isdigit() and m.isdigit() and d.isdigit()):
        raise ValueError("model_date must be 'YYYY-MM-DD'")

def _normalize_row(input_price: float, output_price: float, cached_input_price: Optional[float]) -> dict:
    if input_price < 0 or output_price < 0:
        raise ValueError("Prices must be non-negative")
    row = {
        "input_price": float(input_price),
        "output_price": float(output_price),
        "cached_input_price": float(cached_input_price) if cached_input_price not in (None, 0) else None,
    }
    return row

def add_pricing_entry(
    model_name: str,
    model_date: str,
    *,
    input_price: float,
    output_price: float,
    cached_input_price: Optional[float] = None,
    replace: bool = True,
) -> None:
    """
    Register or override a single pricing row that will be used by `load_pricing()`.
    Users call this at process start, before they estimate costs.

    Example:
        add_pricing_entry(
            "gpt-4o-mini", "2025-08-01",
            input_price=0.20, output_price=0.60, cached_input_price=0.04
        )
    """
    if not model_name or not isinstance(model_name, str):
        raise ValueError("model_name must be a non-empty string")
    _validate_date_str(model_date)
    row = _normalize_row(input_price, output_price, cached_input_price)

    with _LOCK:
        key = (model_name, model_date)
        if not replace and key in _LOCAL_OVERRIDES:
            raise KeyError(f"Pricing already exists for {key}; set replace=True to override.")
        _LOCAL_OVERRIDES[key] = row

def add_pricing_entries(
    entries: Iterable[Tuple[str, str, float, float, Optional[float]]],
    *,
    replace: bool = True,
) -> None:
    """
    Bulk add: each tuple is (model_name, model_date, input_price, output_price, cached_input_price).
    """
    with _LOCK:
        for model_name, model_date, ip, op, cip in entries:
            _validate_date_str(model_date)
            row = _normalize_row(ip, op, cip)
            key = (model_name, model_date)
            if not replace and key in _LOCAL_OVERRIDES:
                raise KeyError(f"Pricing already exists for {key}; set replace=True to override.")
            _LOCAL_OVERRIDES[key] = row

def clear_local_pricing() -> None:
    """Remove all user-added overrides (remote CSV remains unaffected)."""
    with _LOCK:
        _LOCAL_OVERRIDES.clear()

def set_offline_mode(offline: bool = True) -> None:
    """
    If True, `load_pricing()` will NEVER fetch remote CSV—only local overrides are used.
    Useful for air-gapped or pinned environments.
    """
    global _OFFLINE_ONLY
    with _LOCK:
        _OFFLINE_ONLY = bool(offline)

# remote fetch
def _fetch_csv() -> Dict[Tuple[str, str], dict]:
    resp = requests.get(_PRICING_CSV_URL, timeout=5)
    resp.raise_for_status()
    reader = csv.DictReader(io.StringIO(resp.text))
    data = {}
    for row in reader:
        key = (row["Model Name"], row["Model Date"])
        data[key] = {
            "input_price": float(row["Input Price"]),
            "cached_input_price": float(row["Cached Input Price"] or 0) or None,
            "output_price": float(row["Output Price"]),
        }
    return data

def load_pricing() -> Dict[Tuple[str, str], dict]:
    """
    Returns the authoritative pricing map:
        - Remote CSV (cached ~24h) unless offline mode is enabled.
        - PLUS user overrides, which always win on key collisions.
    """
    global _CACHE, _CACHE_TS
    base: Dict[Tuple[str, str], dict] = {}

    if not _OFFLINE_ONLY:
        now = time.time()
        if _CACHE is None or (now - _CACHE_TS) > _TTL:
            _CACHE = _fetch_csv()
            _CACHE_TS = now
        base.update(_CACHE)

    with _LOCK:
        base.update(_LOCAL_OVERRIDES)  # local entries always take precedence

    return base

def refresh_pricing() -> None:
    """
    Refresh remote CSV cache immediately. Local overrides are preserved.
    In offline mode this is a no-op for the remote side.
    """
    global _CACHE, _CACHE_TS
    if _OFFLINE_ONLY:
        return
    _CACHE = _fetch_csv()
    _CACHE_TS = time.time()
