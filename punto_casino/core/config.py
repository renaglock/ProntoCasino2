"""Application configuration and UCT color constants for Pronto Casino UCT."""

from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class AppConfig:
    """Core configuration settings for Pronto Casino UCT (TEC-UCT)."""

    APP_NAME: str = "PRONTO CASINO UCT"
    LOCATION_SUBTITLE: str = "CASINO CENTRAL UCT"

    # Material Design 3 theme
    PRIMARY_PALETTE: str = "Lightblue"
    ACCENT_PALETTE: str = "Blue"
    THEME_STYLE: str = "Light"

    # UCT Institutional Palette
    UCT_PRIMARY_BLUE: str = "#0A3871"    # Deep UCT Navy Blue
    UCT_ACCENT_BLUE: str = "#0288D1"     # Bright Blue
    UCT_LIGHT_BLUE: str = "#E1F5FE"      # Soft Sky Blue
    UCT_CARD_BG: str = "#FFFFFF"         # Pure White
    UCT_APP_BG: str = "#F5F9FD"          # Very light bluish white
    UCT_TEXT_DARK: str = "#1E293B"       # Slate Dark

    DEFAULT_CURRENCY_SYMBOL: str = "$"
    CURRENCY_CODE: str = "CLP"

    CATEGORIES: List[str] = field(
        default_factory=lambda: [
            "Todos",
            "Menú Normal",
            "Menú Ejecutivo",
            "Menú Hipocalórico",
            "Menú Vegetariano",
            "Comidas Rápidas",
            "Bebidas",
        ]
    )


config = AppConfig()

# Unified Category Color Palette for coherent styling across Admin, Charts, and Menus
CATEGORY_PALETTE = {
    "Menú Normal": {
        "hex": "#0A3871",                          # UCT Navy
        "rgba": [0.04, 0.22, 0.44, 1.0],
        "bg_light": [0.93, 0.95, 0.98, 1.0],       # Soft blue tint
        "icon": "food",
        "label": "Normal",
    },
    "Menú Ejecutivo": {
        "hex": "#0288D1",                          # Bright Blue
        "rgba": [0.01, 0.53, 0.82, 1.0],
        "bg_light": [0.90, 0.96, 1.0, 1.0],        # Soft cyan tint
        "icon": "star",
        "label": "Ejecutivo",
    },
    "Menú Hipocalórico": {
        "hex": "#16A34A",                          # Emerald Green
        "rgba": [0.09, 0.64, 0.29, 1.0],
        "bg_light": [0.92, 0.98, 0.93, 1.0],       # Soft green tint
        "icon": "leaf",
        "label": "Hipocalórico",
    },
    "Menú Vegetariano": {
        "hex": "#059669",                          # Forest Green
        "rgba": [0.02, 0.59, 0.41, 1.0],
        "bg_light": [0.90, 0.97, 0.94, 1.0],       # Soft mint tint
        "icon": "sprout",
        "label": "Vegetariano",
    },
    "Comidas Rápidas": {
        "hex": "#D97706",                          # Warm Amber
        "rgba": [0.85, 0.47, 0.02, 1.0],
        "bg_light": [0.99, 0.96, 0.90, 1.0],       # Soft amber tint
        "icon": "hamburger",
        "label": "Rápidas",
    },
    "Bebidas": {
        "hex": "#0D9488",                          # Deep Teal
        "rgba": [0.05, 0.58, 0.53, 1.0],
        "bg_light": [0.90, 0.97, 0.97, 1.0],       # Soft teal tint
        "icon": "cup",
        "label": "Bebidas",
    },
    "Postres y Snacks": {
        "hex": "#9333EA",                          # Purple
        "rgba": [0.58, 0.20, 0.92, 1.0],
        "bg_light": [0.96, 0.92, 0.99, 1.0],       # Soft purple tint
        "icon": "cake-variant",
        "label": "Postres",
    },
    "Ofertas": {
        "hex": "#2EC76E",                          # Fresh Green
        "rgba": [0.18, 0.78, 0.43, 1.0],
        "bg_light": [0.94, 0.99, 0.96, 1.0],       # Soft mint tint
        "icon": "sale",
        "label": "Ofertas",
    },
    "Todos": {
        "hex": "#0A3871",                          # UCT Navy
        "rgba": [0.04, 0.22, 0.44, 1.0],
        "bg_light": [0.93, 0.95, 0.98, 1.0],       # Soft blue tint
        "icon": "silverware-fork-knife",
        "label": "Todos",
    },
}

DEFAULT_CATEGORY_STYLE = {
    "hex": "#64748B",
    "rgba": [0.39, 0.45, 0.55, 1.0],
    "bg_light": [0.95, 0.96, 0.98, 1.0],
    "icon": "tag-outline",
    "label": "General",
}

# Standardized Color Palette for Admin Accounting and Management Tools
ADMIN_TOOLS_PALETTE = {
    # Headers & Structure
    "tool_title": "#0A3871",                       # UCT Deep Navy
    "tool_subtitle": "#64748B",                    # Slate Gray
    "card_bg": [1.0, 1.0, 1.0, 1.0],              # Crisp Pure White
    "card_border": [0.88, 0.92, 0.96, 1.0],       # Soft Ice-Blue Border (#DFEAF2)
    "kpi_container_bg": [0.96, 0.98, 1.0, 1.0],   # Soft Navy tint
    "track_bg": [0.92, 0.95, 0.98, 1.0],          # M3 Progress track bg

    # Financial & KPI Metrics
    "kpi_collected": "#10B981",                   # Emerald Green - Recaudación Neta
    "kpi_average": "#0288D1",                     # Bright Blue - Ticket Promedio
    "kpi_efficiency": "#10B981",                  # Emerald Green - Tasa de Despacho
    "kpi_dispatched": "#0A3871",                  # UCT Navy - Unidades Despachadas
    "kpi_median": "#0288D1",                      # Bright Blue - Mediana estadística
    "kpi_std_dev": "#D97706",                     # Warm Amber - Desviación Estándar
    "kpi_perf_counter": "#0D9488",                # Deep Teal - Tiempo de cómputo

    # Operational Balance Statuses
    "status_delivered": "#10B981",                # Emerald Green - Entregadas
    "status_delivered_rgba": [0.06, 0.65, 0.45, 1.0],
    "status_pending": "#D97706",                  # Warm Amber - En Cocina / Activas
    "status_pending_rgba": [0.85, 0.47, 0.02, 1.0],
    "status_cancelled": "#DC2626",                # Crimson Red - Canceladas
    "status_cancelled_rgba": [0.86, 0.15, 0.15, 1.0],

    # Ranking Podium Badges
    "rank_gold": "#D97706",                       # #1 Gold/Amber
    "rank_silver": "#64748B",                     # #2 Slate Silver
    "rank_bronze": "#0A3871",                     # #3 UCT Navy
    "rank_neutral": "#94A3B8",                    # #4+ Slate Muted
}


def get_category_style(category: str) -> dict:
    """Return unified styling and color palette for a product category."""
    if not category:
        return DEFAULT_CATEGORY_STYLE
    return CATEGORY_PALETTE.get(category.strip(), DEFAULT_CATEGORY_STYLE)
