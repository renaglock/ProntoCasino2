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
}

DEFAULT_CATEGORY_STYLE = {
    "hex": "#64748B",
    "rgba": [0.39, 0.45, 0.55, 1.0],
    "bg_light": [0.95, 0.96, 0.98, 1.0],
    "icon": "tag-outline",
    "label": "General",
}


def get_category_style(category: str) -> dict:
    """Return unified styling and color palette for a product category."""
    if not category:
        return DEFAULT_CATEGORY_STYLE
    return CATEGORY_PALETTE.get(category.strip(), DEFAULT_CATEGORY_STYLE)
