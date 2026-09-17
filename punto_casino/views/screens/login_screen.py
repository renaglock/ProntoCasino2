"""Dedicated Login Screen for Pronto Casino UCT with pristine, friendly mobile UX and institutional security."""

from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
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
from punto_casino.views.components.ui_elements import create_button


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
            style="elevated",
            md_bg_color=[1.0, 1.0, 1.0, 1],  # Blanco puro
            radius=[dp(18), dp(18), dp(18), dp(18)],
            line_color=[0.88, 0.92, 0.96, 1],
            elevation=1,
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

        # Email input field (No colliding helper text)
        self.email_input = MDTextField(
            MDTextFieldLeadingIcon(icon="email-outline"),
            MDTextFieldHintText(text="Correo institucional"),
            mode="outlined",
            size_hint_y=None,
            height=dp(52),
        )
        self.email_input.text = "renato@uct.cl"
        form_card.add_widget(self.email_input)

        # Password input field (No colliding helper text)
        self.password_input = MDTextField(
            MDTextFieldLeadingIcon(icon="lock-outline"),
            MDTextFieldHintText(text="Contraseña"),
            mode="outlined",
            size_hint_y=None,
            height=dp(52),
        )
        self.password_input.password = True
        self.password_input.text = "Renato2026!"
        form_card.add_widget(self.password_input)

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

