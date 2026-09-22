"""Standardized UI components for Pronto Casino UCT ensuring high contrast, zero missing glyphs, and visual symmetry."""

from typing import Any, Callable, Optional
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonIcon, MDButtonText
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel, MDIcon



# Institutional Color Palette
UCT_NAVY = [0.04, 0.22, 0.44, 1.0]       # #0A3871
UCT_ICE_BLUE = [0.90, 0.94, 0.98, 1.0]   # #E5F0FA
UCT_LIGHT_BLUE = [0.01, 0.53, 0.82, 1.0] # #0288D1
LIGHT_GREEN = [0.18, 0.76, 0.42, 1.0]    # #2EC76E (Vibrant fresh light green for offers)
SOFT_MINT = [0.94, 0.99, 0.96, 1.0]      # #F0FDF4 (Soft mint light green background for offer cards)
CRIMSON_RED = [0.86, 0.15, 0.15, 1.0]    # #DC2626
EMERALD_GREEN = [0.06, 0.65, 0.45, 1.0]  # #10B981
WHITE = [1.0, 1.0, 1.0, 1.0]
SLATE_GRAY = [0.39, 0.45, 0.55, 1.0]     # #64748B

# Aliases for offer palette transitions
VIBRANT_ORANGE = LIGHT_GREEN
WARM_PEACH = SOFT_MINT


def create_button(
    text: str,
    icon: Optional[str] = None,
    style: str = "tonal",
    on_release: Optional[Callable] = None,
    size_hint=(None, None),
    height=dp(34),
    width=None,
    icon_size: Optional[Any] = None,
    **kwargs,
) -> MDButton:
    """Build a button with guaranteed contrast, clean typography, and optional Material icon.

    Styles:
        - "filled": UCT Navy background with crisp white text.
        - "tonal": Soft ice-blue background with high-contrast navy text.
        - "outlined": Bordered white button with navy text.
        - "offer": Fresh vibrant light green background with white text.
        - "danger": Crimson red background with white text.
        - "success": Emerald green background with white text.
    """
    children = []

    if style == "filled":
        bg_color = UCT_NAVY
        fg_color = WHITE
        base_style = "filled"
    elif style == "offer":
        bg_color = LIGHT_GREEN
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
        icon_kwargs = {
            "icon": icon,
            "theme_icon_color": "Custom",
            "icon_color": fg_color,
        }
        if icon_size is not None:
            icon_kwargs["size_hint"] = (None, None)
            icon_kwargs["size"] = (icon_size, icon_size)
        children.append(MDButtonIcon(**icon_kwargs))

    children.append(
        MDButtonText(
            text=text,
            theme_text_color="Custom",
            text_color=fg_color,
        )
    )

    has_custom_w = (size_hint and size_hint[0] is not None) or width is not None
    has_custom_h = (size_hint and size_hint[1] is not None) or height is not None

    btn_kwargs = {
        "style": base_style,
        "theme_bg_color": "Custom",
        "md_bg_color": bg_color,
        "theme_width": "Custom" if has_custom_w else "Primary",
        "theme_height": "Custom" if has_custom_h else "Primary",
        "size_hint": size_hint,
        "height": height,
    }
    if width is not None:
        btn_kwargs["width"] = width
    if on_release:
        btn_kwargs["on_release"] = on_release

    btn = MDButton(*children, **btn_kwargs)
    if size_hint is not None:
        btn.size_hint = size_hint
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
        md_bg_color=LIGHT_GREEN,
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


def create_category_pill(category: str) -> MDCard:
    """Create an authentic Material 3 pill badge displaying category name with coherent color branding."""
    from punto_casino.core.config import get_category_style

    cat_style = get_category_style(category)
    badge = MDCard(
        orientation="horizontal",
        size_hint=(None, None),
        height=dp(20),
        padding=[dp(6), dp(1), dp(6), dp(1)],
        spacing=dp(3),
        style="filled",
        theme_bg_color="Custom",
        md_bg_color=cat_style["bg_light"],
        radius=[dp(6), dp(6), dp(6), dp(6)],
        line_color=[*cat_style["rgba"][:3], 0.35],
        elevation=0,
    )
    badge.add_widget(
        MDLabel(
            text=f"[b][color={cat_style['hex']}]{category}[/color][/b]",
            markup=True,
            font_style="Label",
            role="small",
            adaptive_width=True,
        )
    )
    return badge


class M3NavItem(ButtonBehavior, MDBoxLayout):
    """Authentic, high-end mobile navigation tab.
    Full-width touchable surface across icon, label, and container.
    Zero toggle-switch artifacts, zero touch-blocking sub-widgets."""

    def __init__(self, text: str, icon: str, on_release: Optional[Callable] = None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint = (1, 1)
        self.spacing = dp(2)
        self.padding = [dp(2), dp(2), dp(2), dp(4)]
        self.theme_bg_color = "Custom"
        self.md_bg_color = [1.0, 1.0, 1.0, 1.0]  # Solid white
        self.nav_text = text
        self._on_release_cb = on_release

        # 1. Top active accent indicator (sleek corporate bar)
        self.top_indicator = MDBoxLayout(
            size_hint=(None, None),
            size=(dp(36), dp(3)),
            pos_hint={"center_x": 0.5},
            radius=[dp(2), dp(2), dp(2), dp(2)],
            theme_bg_color="Custom",
            md_bg_color=[1.0, 1.0, 1.0, 0.0],  # Transparent when inactive
        )

        # 2. Centered prominent icon
        self.icon_box = MDBoxLayout(
            orientation="vertical",
            size_hint=(1, None),
            height=dp(26),
            pos_hint={"center_x": 0.5},
        )
        self.icon_w = MDIcon(
            icon=icon,
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            theme_icon_color="Custom",
            icon_color=[0.39, 0.45, 0.55, 1.0],  # Slate Gray
        )
        self.icon_box.add_widget(self.icon_w)

        # 3. Centered typography label
        self.lbl = MDLabel(
            text=f"[color=#64748B]{text}[/color]",
            markup=True,
            halign="center",
            font_style="Label",
            role="small",
            size_hint_y=None,
            height=dp(16),
        )

        self.add_widget(self.top_indicator)
        self.add_widget(self.icon_box)
        self.add_widget(self.lbl)

        if on_release:
            self.bind(on_release=on_release)

    def on_touch_down(self, touch):
        """Intercept touches anywhere inside the tab bounding box."""
        if self.collide_point(*touch.pos):
            touch.grab(self)
            return True
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        """Trigger navigation whenever a touch releases inside the tab."""
        if touch.grab_current is self:
            touch.ungrab(self)
            if self.collide_point(*touch.pos):
                self.dispatch("on_release")
                if self._on_release_cb:
                    self._on_release_cb(self)
            return True
        return super().on_touch_up(touch)

    def set_active(self, is_active: bool):
        """Update visual state with pristine contrast and zero switch appearance."""
        if is_active:
            # Active: Vibrant UCT Navy (#0A3871) top accent + icon + bold label
            self.top_indicator.md_bg_color = [0.04, 0.22, 0.44, 1.0]
            self.icon_w.icon_color = [0.04, 0.22, 0.44, 1.0]
            self.lbl.text = f"[b][color=#0A3871]{self.nav_text}[/color][/b]"
        else:
            # Inactive: Transparent accent + Slate Gray (#64748B) icon + regular label
            self.top_indicator.md_bg_color = [1.0, 1.0, 1.0, 0.0]
            self.icon_w.icon_color = [0.39, 0.45, 0.55, 1.0]
            self.lbl.text = f"[color=#64748B]{self.nav_text}[/color]"


def create_nav_item(text: str, icon: str, on_release: Optional[Callable] = None) -> M3NavItem:
    """Builds an authentic, responsive navigation tab with full-area touch capture."""
    return M3NavItem(text=text, icon=icon, on_release=on_release)

