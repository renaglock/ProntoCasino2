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
