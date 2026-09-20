"""Dedicated Login Screen for Pronto Casino UCT with pristine, friendly mobile UX and institutional security."""

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonIcon, MDButtonText
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import (
    MDTextField,
    MDTextFieldHintText,
    MDTextFieldLeadingIcon,
)

from punto_casino.models.user import UserRole
from punto_casino.services.auth_service import AuthService
from punto_casino.views.components.ui_elements import create_button, UCT_NAVY, SLATE_GRAY


class LoginScreen(MDScreen):
    """Clean, friendly login screen with institutional authentication."""

    def __init__(self, auth_service: AuthService, on_login_success, **kwargs):
        super().__init__(**kwargs)
        self.auth_service = auth_service
        self.on_login_success = on_login_success

        self.email_input = None
        self.password_input = None
        self.error_label = None

        self._build_ui()

    def _build_ui(self):
        scroll = ScrollView(size_hint=(1, 1))

        content_box = MDBoxLayout(
            orientation="vertical",
            padding=[dp(20), dp(24), dp(20), dp(24)],
            spacing=dp(18),
            size_hint_y=None,
        )
        content_box.bind(minimum_height=content_box.setter("height"))

        # 1. Header Banner (Clean, comfortable, non-card, high contrast)
        header_box = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(105),
            padding=[dp(8), dp(4), dp(8), dp(4)],
            spacing=dp(4),
        )
        title = MDLabel(
            text="[b][color=#0A3871]PRONTO CASINO UCT[/color][/b]",
            markup=True,
            font_style="Headline",
            role="medium",
            halign="center",
            size_hint_y=None,
            height=dp(38),
        )
        sub = MDLabel(
            text="[b][color=#0288D1]Universidad Católica de Temuco[/color][/b]",
            markup=True,
            font_style="Title",
            role="small",
            halign="center",
            size_hint_y=None,
            height=dp(22),
        )
        tagline = MDLabel(
            text="[color=#64748B]Casino Central • Campus San Juan Pablo II\nPedidos y Comandas sin Filas[/color]",
            markup=True,
            font_style="Body",
            role="small",
            halign="center",
            size_hint_y=None,
            height=dp(36),
        )
        header_box.add_widget(title)
        header_box.add_widget(sub)
        header_box.add_widget(tagline)
        content_box.add_widget(header_box)

        # 2. Authentication Form Card (Spacious, elegant, responsive, no overlapping text)
        form_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(360),
            padding=[dp(22), dp(18), dp(22), dp(18)],
            spacing=dp(10),
            style="outlined",
            theme_bg_color="Custom",
            md_bg_color=[1.0, 1.0, 1.0, 1],  # Blanco puro
            radius=[dp(18), dp(18), dp(18), dp(18)],
            line_color=[0.88, 0.92, 0.96, 1],
            elevation=0,
        )

        form_title = MDLabel(
            text="[b][color=#0A3871]Ingreso al Sistema[/color][/b]",
            markup=True,
            font_style="Title",
            role="medium",
            size_hint_y=None,
            height=dp(26),
        )
        form_sub = MDLabel(
            text="[color=#64748B]Ingresa tu correo institucional y contraseña[/color]",
            markup=True,
            font_style="Body",
            role="small",
            size_hint_y=None,
            height=dp(20),
        )
        form_card.add_widget(form_title)
        form_card.add_widget(form_sub)

        # Email input field (Clean, responsive, keyboard-friendly)
        self.email_input = MDTextField(
            MDTextFieldLeadingIcon(icon="email-outline"),
            MDTextFieldHintText(text="Correo institucional"),
            mode="outlined",
            size_hint_y=None,
            height=dp(52),
            multiline=False,
            write_tab=False,
        )
        self.email_input.text = "renato@uct.cl"
        self.email_input.bind(on_text_validate=lambda x: self._focus_password())
        form_card.add_widget(self.email_input)

        # Password input container with interactive reveal/conceal toggle button
        password_container = RelativeLayout(
            size_hint_y=None,
            height=dp(52),
        )
        self.password_input = MDTextField(
            MDTextFieldLeadingIcon(icon="lock-outline"),
            MDTextFieldHintText(text="Contraseña"),
            mode="outlined",
            size_hint=(1, 1),
            multiline=False,
            write_tab=False,
        )
        self.password_input.password = True
        self.password_input.text = "Renato2026!"
        self.password_input.bind(on_text_validate=lambda x: self._on_credentials_submit())

        self.password_toggle_icon = MDButtonIcon(
            icon="eye-off",
            theme_icon_color="Custom",
            icon_color=SLATE_GRAY,
            size_hint=(None, None),
            size=(dp(22), dp(22)),
        )
        self.password_toggle_btn = MDButton(
            self.password_toggle_icon,
            style="text",
            theme_bg_color="Custom",
            md_bg_color=[0, 0, 0, 0],
            size_hint=(None, None),
            size=(dp(44), dp(44)),
            pos_hint={"right": 0.98, "center_y": 0.5},
            on_release=self._toggle_password_visibility,
        )
        password_container.add_widget(self.password_input)
        password_container.add_widget(self.password_toggle_btn)
        form_card.add_widget(password_container)

        # Keyboard focus navigation chain
        self.email_input.focus_next = self.password_input
        self.password_input.focus_previous = self.email_input

        # Error / Status Feedback Label
        self.error_label = MDLabel(
            text="",
            markup=True,
            font_style="Label",
            role="small",
            halign="center",
            size_hint_y=None,
            height=dp(18),
        )
        form_card.add_widget(self.error_label)

        # Submit Button (Comfortable tap target, UCT styling)
        btn_submit = create_button(
            text="Iniciar Sesión Institucional",
            icon="login",
            style="filled",
            size_hint=(1, None),
            height=dp(44),
            on_release=lambda x: self._on_credentials_submit(),
        )
        form_card.add_widget(btn_submit)

        # Guest One-Tap Access Button (Section 2 & 6 MVP with high contrast and no square emoji glyph)
        btn_guest = create_button(
            text="Continuar como Invitado (Sin Registro)",
            icon="account-outline",
            style="tonal",
            size_hint=(1, None),
            height=dp(42),
            on_release=lambda x: self._on_guest_access(),
        )
        form_card.add_widget(btn_guest)
        content_box.add_widget(form_card)

        # 3. Institutional Security Notice (Reassuring, clean, no square unprinted glyphs)
        security_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(56),
            padding=[dp(14), dp(8), dp(14), dp(8)],
            spacing=dp(2),
            style="outlined",
            md_bg_color=[0.96, 0.98, 1.0, 1],
            radius=[dp(14), dp(14), dp(14), dp(14)],
            line_color=[0.85, 0.91, 0.97, 1],
        )
        sec_title = MDLabel(
            text="[color=#0A3871][b]Conexión Institucional Segura[/b][/color]",
            markup=True,
            font_style="Label",
            role="small",
            halign="center",
            size_hint_y=None,
            height=dp(18),
        )
        sec_desc = MDLabel(
            text="[color=#64748B]Acceso protegido por la plataforma central de la UCT[/color]",
            markup=True,
            font_style="Label",
            role="small",
            halign="center",
            size_hint_y=None,
            height=dp(16),
        )
        security_card.add_widget(sec_title)
        security_card.add_widget(sec_desc)
        content_box.add_widget(security_card)

        scroll.add_widget(content_box)
        self.add_widget(scroll)

    def _toggle_password_visibility(self, *args):
        """Toggle password concealment on and off with immediate visual icon update."""
        if not self.password_input:
            return
        self.password_input.password = not self.password_input.password
        if self.password_toggle_icon:
            if self.password_input.password:
                self.password_toggle_icon.icon = "eye-off"
                self.password_toggle_icon.icon_color = SLATE_GRAY
            else:
                self.password_toggle_icon.icon = "eye"
                self.password_toggle_icon.icon_color = UCT_NAVY

    def _focus_password(self):
        """Move focus to password input field."""
        if self.email_input:
            self.email_input.focus = False
        if self.password_input:
            self.password_input.focus = True

    def _focus_email(self):
        """Move focus to email input field."""
        if self.password_input:
            self.password_input.focus = False
        if self.email_input:
            self.email_input.focus = True

    def on_enter(self):
        """Screen entered: bind keyboard shortcuts and autofocus email input."""
        if self.error_label:
            self.error_label.text = ""
        # Auto-focus email field with a gentle tick so Kivy window state settles
        Clock.schedule_once(lambda dt: setattr(self.email_input, "focus", True), 0.1)
        # Bind global hardware keyboard events for Tab, Enter, and Arrow navigation
        Window.bind(on_key_down=self._on_window_key_down)

    def on_leave(self):
        """Screen left: clean up keyboard listener."""
        Window.unbind(on_key_down=self._on_window_key_down)

    def _on_window_key_down(self, window, key, scancode, codepoint, modifiers) -> bool:
        """Handle Tab, Shift+Tab, Enter, and Up/Down arrows seamlessly."""
        # 1. Tab navigation (Key code 9)
        if key == 9:
            if self.email_input and self.email_input.focus:
                self._focus_password()
                return True
            elif self.password_input and self.password_input.focus:
                if "shift" in modifiers:
                    self._focus_email()
                else:
                    self._focus_email()
                return True

        # 2. Enter / Return key (Key codes 13 and 271 for keypad)
        elif key in (13, 271):
            if self.email_input and self.email_input.focus:
                self._focus_password()
                return True
            elif self.password_input and self.password_input.focus:
                self._on_credentials_submit()
                return True

        # 3. Up Arrow (Key code 273)
        elif key == 273:
            if self.password_input and self.password_input.focus:
                self._focus_email()
                return True

        # 4. Down Arrow (Key code 274)
        elif key == 274:
            if self.email_input and self.email_input.focus:
                self._focus_password()
                return True

        return False

    def _on_credentials_submit(self):
        """Authenticate user strictly using the email and password inputs against the database."""
        email = self.email_input.text.strip()
        password = self.password_input.text

        if not email or not password:
            self.error_label.text = "[color=#EF4444]Por favor ingresa correo y contraseña[/color]"
            return

        user = self.auth_service.authenticate_credentials(email, password)
        if user:
            self.error_label.text = "[color=#10B981]Acceso concedido. Iniciando sesión...[/color]"
            target_screen = "catalog"
            if user.role == UserRole.CASHIER:
                target_screen = "cashier"
            elif user.role == UserRole.ADMIN:
                target_screen = "admin"

            self.on_login_success(user, target_screen)
        else:
            self.error_label.text = "[color=#EF4444]Credenciales incorrectas o usuario no encontrado[/color]"

    def _on_guest_access(self):
        """Allow unauthenticated walk-in guests to browse catalog and order immediately."""
        user = self.auth_service.quick_login("invitado")
        if user:
            self.on_login_success(user, "catalog")


