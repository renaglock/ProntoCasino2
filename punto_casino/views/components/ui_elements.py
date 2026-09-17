"""Standardized UI components for Pronto Casino UCT ensuring high contrast, zero missing glyphs, and visual symmetry."""

from typing import Callable, Optional
from kivy.metrics import dp
from kivymd.uix.button import MDButton, MDButtonIcon, MDButtonText
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel


# Institutional Color Palette
UCT_NAVY = [0.04, 0.22, 0.44, 1.0]       # #0A3871
UCT_ICE_BLUE = [0.90, 0.94, 0.98, 1.0]   # #E5F0FA
UCT_LIGHT_BLUE = [0.01, 0.53, 0.82, 1.0] # #0288D1
VIBRANT_ORANGE = [0.95, 0.35, 0.08, 1.0] # #F25A14 (Vibrant fiery offer accent)
WARM_PEACH = [1.0, 0.96, 0.92, 1.0]      # Soft background for offer cards
CRIMSON_RED = [0.86, 0.15, 0.15, 1.0]    # #DC2626
EMERALD_GREEN = [0.06, 0.65, 0.45, 1.0]  # #10B981
WHITE = [1.0, 1.0, 1.0, 1.0]
SLATE_GRAY = [0.39, 0.45, 0.55, 1.0]     # #64748B


def create_button(
    text: str,
    icon: Optional[str] = None,
    style: str = "tonal",
    on_release: Optional[Callable] = None,
    size_hint=(None, None),
    height=dp(34),
    width=None,
    **kwargs,
) -> MDButton:
    """Build a button with guaranteed contrast, clean typography, and optional Material icon.

    Styles:
        - "filled": UCT Navy background with crisp white text.
        - "tonal": Soft ice-blue background with high-contrast navy text.
        - "outlined": Bordered white button with navy text.
        - "offer": Vibrant fiery orange background with white text.
        - "danger": Crimson red background with white text.
        - "success": Emerald green background with white text.
    """
    children = []

    if style == "filled":
        bg_color = UCT_NAVY
        fg_color = WHITE
        base_style = "filled"
    elif style == "offer":
        bg_color = VIBRANT_ORANGE
        fg_color = WHITE
        base_style = "filled"
    elif style == "danger":
        bg_color = CRIMSON_RED
        fg_color = WHITE
        base_style = "filled"
    elif style == "success":
        bg_color = EMERALD_GREEN
        fg_color = WHITE
        base_style = "filled"
    elif style == "outlined":
        bg_color = WHITE
        fg_color = UCT_NAVY
        base_style = "outlined"
    else:  # "tonal" default
        bg_color = UCT_ICE_BLUE
        fg_color = UCT_NAVY
        base_style = "tonal"

    if icon:
        children.append(
            MDButtonIcon(
                icon=icon,
                theme_icon_color="Custom",
                icon_color=fg_color,
            )
        )

    children.append(
        MDButtonText(
            text=text,
            theme_text_color="Custom",
            text_color=fg_color,
        )
    )

    btn_kwargs = {
        "style": base_style,
        "theme_bg_color": "Custom",
        "md_bg_color": bg_color,
        "size_hint": size_hint,
        "height": height,
    }
    if width is not None:
        btn_kwargs["width"] = width
    if on_release:
        btn_kwargs["on_release"] = on_release

    btn = MDButton(*children, **btn_kwargs)
    return btn


def create_offer_badge(offer_label: str) -> MDCard:
    """Create a vibrant pill badge for discounted and near-expiry items with guaranteed high contrast."""
    badge = MDCard(
        orientation="horizontal",
        size_hint=(1, None),
        height=dp(26),
        padding=[dp(8), dp(3), dp(10), dp(3)],
        spacing=dp(6),
        style="filled",
        theme_bg_color="Custom",
        md_bg_color=VIBRANT_ORANGE,
        radius=[dp(8), dp(8), dp(8), dp(8)],
        elevation=0,
    )
    badge.add_widget(
        MDButtonIcon(
            icon="sale",
            theme_icon_color="Custom",
            icon_color=WHITE,
            size_hint=(None, None),
            size=(dp(16), dp(16)),
        )
    )
    badge.add_widget(
        MDLabel(
            text=f"[b][color=#FFFFFF]OFERTA: {offer_label}[/color][/b]",
            markup=True,
            font_style="Label",
            role="small",
            theme_text_color="Custom",
            text_color=WHITE,
            size_hint_y=None,
            height=dp(20),
        )
    )
    return badge

