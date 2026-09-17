"""Pronto Casino UCT - Main Mobile Application with Smartphone Resolution and Login Flow."""

import os
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.label import MDLabel
from kivymd.uix.screenmanager import MDScreenManager

# 1. Configure Smartphone Dimensions (Mobile Resolution: 380x720)
Window.size = (380, 720)
Window.minimum_size = (360, 640)


# 2. Load Kivy Language Stylesheet (CSS equivalent for UCT branding)
styles_file = os.path.join(os.path.dirname(__file__), "punto_casino", "views", "styles.kv")
if os.path.exists(styles_file):
    Builder.load_file(styles_file)

from punto_casino.core.config import config
from punto_casino.models.user import UserRole
from punto_casino.repositories.database import DatabaseManager
from punto_casino.repositories.user_repository import UserRepository
from punto_casino.repositories.product_repository import InMemoryProductRepository
from punto_casino.repositories.order_repository import InMemoryOrderRepository
from punto_casino.services.auth_service import AuthService
from punto_casino.services.order_service import OrderService
from punto_casino.services.cashier_service import CashierService
from punto_casino.views.screens.login_screen import LoginScreen
from punto_casino.views.screens.catalog_screen import CatalogScreen
from punto_casino.views.screens.cashier_screen import CashierScreen
from punto_casino.views.screens.admin_screen import AdminScreen
from punto_casino.views.screens.reservations_screen import ReservationsScreen
from punto_casino.views.components.ui_elements import create_button


class ProntoCasinoApp(MDApp):
    """Main mobile application orchestrator with role-based navigation and UCT styling."""

    def build(self):
        self.title = config.APP_NAME
        self.theme_cls.primary_palette = config.PRIMARY_PALETTE
        self.theme_cls.theme_style = config.THEME_STYLE

        # 1. Database and Persistence Layer (SQLite WAL mode & OWASP Security)
        self.db_manager = DatabaseManager()
        self.user_repo = UserRepository(self.db_manager)
        self.product_repo = InMemoryProductRepository()
        self.order_repo = InMemoryOrderRepository()

        # 2. Domain & Application Services
        self.auth_service = AuthService(self.user_repo)
        self.order_service = OrderService(self.product_repo, self.order_repo, self.auth_service)
        self.cashier_service = CashierService(self.product_repo, self.order_repo, self.auth_service)

        # Root Mobile Layout
        self.master_layout = MDBoxLayout(orientation="vertical")

        # 1. Top Bar (Pristine White & UCT Navy Blue)
        self.top_bar = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(52),
            padding=[dp(14), dp(8), dp(14), dp(8)],
            spacing=dp(8),
            md_bg_color=[0.04, 0.22, 0.44, 1],  # Azul UCT #0A3871
        )
        self.app_title_lbl = MDLabel(
            text="[b][color=#FFFFFF]PRONTO CASINO UCT[/color][/b]",
            markup=True,
            font_style="Title",
            role="medium",
        )
        self.user_chip_lbl = MDLabel(
            text="",
            markup=True,
            halign="right",
            font_style="Label",
            role="medium",
            size_hint_x=None,
            width=dp(130),
        )
        self.logout_btn = create_button(
            text="Salir",
            icon="logout",
            style="tonal",
            size_hint=(None, None),
            height=dp(34),
            width=dp(90),
            on_release=lambda x: self._on_logout(),
        )

        self.top_bar.add_widget(self.app_title_lbl)
        self.top_bar.add_widget(self.user_chip_lbl)
        self.top_bar.add_widget(self.logout_btn)

        # 2. Screen Manager
        self.sm = MDScreenManager()

        self.login_screen = LoginScreen(
            auth_service=self.auth_service,
            on_login_success=self._on_login_success,
            name="login",
        )
        self.catalog_screen = CatalogScreen(
            order_service=self.order_service,
            auth_service=self.auth_service,
            name="catalog",
        )
        self.reservations_screen = ReservationsScreen(
            order_service=self.order_service,
            auth_service=self.auth_service,
            on_navigate=self.navigate_to,
            name="reservations",
        )
        self.cashier_screen = CashierScreen(
            cashier_service=self.cashier_service,
            on_navigate=self.navigate_to,
            name="cashier",
        )
        self.admin_screen = AdminScreen(
            product_repo=self.product_repo,
            order_service=self.order_service,
            on_navigate=self.navigate_to,
            name="admin",
        )

        self.sm.add_widget(self.login_screen)
        self.sm.add_widget(self.catalog_screen)
        self.sm.add_widget(self.reservations_screen)
        self.sm.add_widget(self.cashier_screen)
        self.sm.add_widget(self.admin_screen)

        # 3. Bottom Navigation Bar (Dynamic per role, high contrast)
        self.bottom_nav = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(54),
            padding=[dp(8), dp(4), dp(8), dp(4)],
            spacing=dp(6),
            md_bg_color=[1.0, 1.0, 1.0, 1],  # Blanco
        )

        self.master_layout.add_widget(self.top_bar)
        self.master_layout.add_widget(self.sm)
        self.master_layout.add_widget(self.bottom_nav)

        # Initial state: in Login screen (hide top bar & bottom nav)
        self._set_bars_visible(False)
        self.sm.current = "login"
        return self.master_layout

    def _set_bars_visible(self, visible: bool):
        if visible:
            self.top_bar.height = dp(52)
            self.top_bar.opacity = 1
            self.top_bar.disabled = False
            self.bottom_nav.height = dp(54)
            self.bottom_nav.opacity = 1
            self.bottom_nav.disabled = False
        else:
            self.top_bar.height = dp(0)
            self.top_bar.opacity = 0
            self.top_bar.disabled = True
            self.bottom_nav.height = dp(0)
            self.bottom_nav.opacity = 0
            self.bottom_nav.disabled = True

    def _on_login_success(self, user_key: str, target_screen: str):
        user = self.auth_service.current_user
        first_name = "Invitado" if user.role == UserRole.GUEST else user.name.split()[0]
        self.user_chip_lbl.text = f"[b][color=#E1F5FE]{first_name}[/color][/b]"
        self._set_bars_visible(True)
        self._rebuild_bottom_nav_for_role(user.role)
        self.navigate_to(target_screen)

    def _on_logout(self):
        self.order_service.clear_cart()
        self._set_bars_visible(False)
        self.navigate_to("login")

    def _go_to_offers(self):
        """Navigate directly to the Catalog filtered by active discounts/offers."""
        self.catalog_screen.selected_category = "Ofertas"
        self.navigate_to("catalog")
        if hasattr(self.catalog_screen, "_rebuild_category_tabs"):
            self.catalog_screen._rebuild_category_tabs()
        self.catalog_screen.refresh_catalog()

    def _rebuild_bottom_nav_for_role(self, role: UserRole):
        """Reconstruct bottom navigation buttons tailored to the logged-in role with high contrast."""
        self.bottom_nav.clear_widgets()

        btn_menus = create_button(
            text="Menús",
            icon="silverware-fork-knife",
            style="tonal",
            on_release=lambda x: self._go_to_all_menus(),
        )
        btn_reservas = create_button(
            text="Reservas",
            icon="receipt",
            style="tonal",
            on_release=lambda x: self.navigate_to("reservations"),
        )
        self.bottom_nav.add_widget(btn_menus)
        self.bottom_nav.add_widget(btn_reservas)

        if role == UserRole.CASHIER or role == UserRole.ADMIN:
            btn_caja = create_button(
                text="Caja",
                icon="cash-register",
                style="tonal",
                on_release=lambda x: self.navigate_to("cashier"),
            )
            self.bottom_nav.add_widget(btn_caja)

        if role == UserRole.ADMIN:
            btn_admin = create_button(
                text="Admin",
                icon="shield-account",
                style="tonal",
                on_release=lambda x: self.navigate_to("admin"),
            )
            self.bottom_nav.add_widget(btn_admin)

    def _go_to_all_menus(self):
        self.catalog_screen.selected_category = "Todos"
        self.navigate_to("catalog")
        if hasattr(self.catalog_screen, "_rebuild_category_tabs"):
            self.catalog_screen._rebuild_category_tabs()
        self.catalog_screen.refresh_catalog()

    def navigate_to(self, screen_name: str):
        if screen_name in self.sm.screen_names:
            self.sm.current = screen_name
            target = self.sm.get_screen(screen_name)
            if hasattr(target, "on_enter"):
                target.on_enter()


if __name__ == "__main__":
    ProntoCasinoApp().run()