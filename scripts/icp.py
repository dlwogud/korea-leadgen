"""ICP (Ideal Customer Profile) — the single source of truth.

Loads config/icp.json and turns it into the criteria that drive BOTH:
  - sourcing  (which keywords to search)        → source_saramin.py
  - scoring   (how well a company fits a service) → enrich.py, score_leads.py

Edit config/icp.json (not code) when the team/mentor confirm the real ICP.
"""
from __future__ import annotations

import json
from pathlib import Path

_CONFIG = Path(__file__).resolve().parent.parent / "config" / "icp.json"
_DATA = json.loads(_CONFIG.read_text(encoding="utf-8"))
_SERVICES = _DATA["services"]


def services() -> list[str]:
    return list(_SERVICES.keys())


def label(service: str) -> str:
    return _SERVICES[service].get("label", service)


def target_industries(service: str) -> list[str]:
    return _SERVICES.get(service, {}).get("target_industries", [])


def keywords(service: str) -> list[str]:
    return _SERVICES.get(service, {}).get("keywords", [])


def all_keywords() -> list[str]:
    seen, out = set(), []
    for svc in _SERVICES.values():
        for kw in svc.get("keywords", []):
            if kw not in seen:
                seen.add(kw); out.append(kw)
    return out


def tech_terms() -> list[str]:
    return _DATA.get("tech_terms", [])


def _contains_any(text: str, terms: list[str]) -> bool:
    low = (text or "").lower()
    return any(t.lower() in low for t in terms)


def fit(row: dict, service: str) -> float:
    """0–100 fit of a company row for one service, per config/icp.json.

    row needs: industry, sample_titles, tech_stack, locations, hiring_count.
    """
    cfg = _SERVICES[service]
    industry = row.get("industry", "")
    signal_blob = f"{row.get('sample_titles','')} {row.get('tech_stack','')}"
    locations = row.get("locations", "")
    hiring = int(row.get("hiring_count") or 0)

    industry_match = _contains_any(industry, cfg.get("target_industries", []))
    signal_match = _contains_any(signal_blob, cfg.get("signal_terms", []))
    signal_fit = 1.0 if (industry_match or signal_match) else 0.3

    intent = min(1.0, hiring / 5)

    regions = cfg.get("target_regions", [])
    region_fit = 1.0 if (not regions or any(r in locations for r in regions)) else 0.5

    w = cfg["weights"]
    return 100 * (w["signal"] * signal_fit + w["intent"] * intent + w["region"] * region_fit)


def best_fit(row: dict) -> tuple[str, float]:
    """Return (best_service, its_fit) for a company row."""
    scored = {svc: fit(row, svc) for svc in services()}
    best = max(scored, key=scored.get)
    return best, scored[best]
