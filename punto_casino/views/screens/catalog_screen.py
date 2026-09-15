"""Responsive product catalog matching PRONTO CASINO UCT wireframe with clean layout."""

from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen

from punto_casino.core.config import config
from punto_casino.models.user import UserRole
from punto_casino.services.order_service import OrderService
from punto_casino.services.auth_service import AuthService
from punto_casino.utils.formatters import format_currency


class CatalogScreen(MDScreen):
    """Product catalog with responsive card layout, category filtering, and student balance."""

    def __init__(self, order_service: OrderService, auth_service: AuthService, **kwargs):
        super().__init__(**kwargs)
        self.order_service = order_service
        self.auth_service = auth_service
        self.selected_category = "Todos"

        self.root_layout = None
        self.balance_label = None
        self.cart_label = None
        self.status_label = None
        self.products_container = None
        self.confirm_modal = None

        self._build_ui()

    def _build_ui(self):
        self.root_layout = MDBoxLayout(
            orientation="vertical",
            padding=[dp(14), dp(10), dp(14), dp(10)],
            spacing=dp(8),
        )

        # 1. Location & Subtitle Banner
        banner = MDCard(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(36),
            padding=[dp(12), dp(4), dp(12), dp(4)],
            style="elevated",
            md_bg_color=[1, 1, 1, 1],
            radius=[dp(10), dp(10), dp(10), dp(10)],
        )
        location_label = MDLabel(
            text=f"[color=#0A3871][b]{config.LOCATION_SUBTITLE}[/b][/color]",
            markup=True,
            font_style="Label",
            role="medium",
        )
        self.balance_label = MDLabel(
            text="",
            markup=True,
            halign="right",
            font_style="Label",
            role="medium",
            bold=True,
        )
        banner.add_widget(location_label)
        banner.add_widget(self.balance_label)
        self.root_layout.add_widget(banner)

        # 2. Category Tabs Horizontal Scroll
        cat_scroll = ScrollView(size_hint=(1, None), height=dp(38), do_scroll_x=True, do_scroll_y=False)
        cat_box = MDBoxLayout(orientation="horizontal", spacing=dp(6), size_hint_x=None)
        cat_box.bind(minimum_width=cat_box.setter("width"))

        category_aliases = [
            ("Todos", "Todos"),
            ("Menú Normal", "Normal"),
            ("Menú Ejecutivo", "Ejecutivo"),
            ("Menú Hipocalórico", "Hipocalórico"),
            ("Menú Vegetariano", "Vegetariano"),
            ("Comidas Rápidas", "Rápidas"),
            ("Bebidas", "Bebidas"),
        ]

        for full_cat, display_name in category_aliases:
            btn = MDButton(
                MDButtonText(text=display_name),
                style="tonal",
                size_hint_y=None,
                height=dp(34),
                on_release=lambda x, c=full_cat: self._on_select_category(c),
            )
            cat_box.add_widget(btn)

        cat_scroll.add_widget(cat_box)
        self.root_layout.add_widget(cat_scroll)

        # 3. Products List (Scrollable)
        scroll = ScrollView(size_hint=(1, 1))
        self.products_container = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
        )
        self.products_container.bind(minimum_height=self.products_container.setter("height"))
        scroll.add_widget(self.products_container)
        self.root_layout.add_widget(scroll)

        # 4. Cart Summary & Action Footer
        footer = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(88),
            padding=[dp(12), dp(8), dp(12), dp(8)],
            spacing=dp(4),
            style="elevated",
            md_bg_color=[1, 1, 1, 1],
            radius=[dp(14), dp(14), dp(14), dp(14)],
        )
        self.cart_label = MDLabel(text="Carrito vacío", bold=True, size_hint_y=None, height=dp(20))
        self.status_label = MDLabel(text="", size_hint_y=None, height=dp(16), font_style="Label", role="small")

        actions_box = MDBoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(34))
        clear_btn = MDButton(
            MDButtonText(text="Vaciar"),
            style="outlined",
            on_release=lambda x: self._on_clear_cart(),
        )
        order_btn = MDButton(
            MDButtonText(text="Reservar Comanda"),
            style="filled",
            on_release=lambda x: self._ask_reservation_confirmation(),
        )
        actions_box.add_widget(clear_btn)
        actions_box.add_widget(order_btn)

        footer.add_widget(self.cart_label)
        footer.add_widget(self.status_label)
        footer.add_widget(actions_box)
        self.root_layout.add_widget(footer)

        self.add_widget(self.root_layout)
        self.refresh_catalog()

    def on_enter(self):
        """Update balance and products on screen enter."""
        self.refresh_catalog()

    def refresh_catalog(self):
        user = self.auth_service.current_user
        if user.role == UserRole.CLIENT:
            self.balance_label.text = "[color=#0288D1][b]Estudiante UCT[/b][/color]"
        else:
            self.balance_label.text = f"[color=#64748B]{user.role.value}[/color]"

        self.products_container.clear_widgets()
        products = self.order_service.product_repo.get_by_category(self.selected_category)

        for prod in products:
            card = MDCard(
                orientation="vertical",
                size_hint_y=None,
                height=dp(112),
                padding=[dp(12), dp(8), dp(12), dp(8)],
                spacing=dp(3),
                style="elevated",
                md_bg_color=[1, 1, 1, 1],
                radius=[dp(12), dp(12), dp(12), dp(12)],
            )

            # Row 1: Title and Price (Clean contrast)
            top_line = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(22))
            top_line.add_widget(
                MDLabel(
                    text=f"[b][color=#0A3871]{prod.name}[/color][/b]",
                    markup=True,
                    font_style="Title",
                    role="small",
                )
            )
            top_line.add_widget(
                MDLabel(
                    text=f"[b][color=#0288D1]{format_currency(prod.price)}[/color][/b]",
                    markup=True,
                    halign="right",
                    font_style="Title",
                    role="small",
                )
            )

            # Row 2: Badges (Category & Stock)
            badge_line = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(18))
            badge_line.add_widget(
                MDLabel(
                    text=f"[color=#64748B]{prod.category}[/color]",
                    markup=True,
                    font_style="Label",
                    role="small",
                )
            )
            badge_line.add_widget(
                MDLabel(
                    text=f"[color=#10B981]{prod.stock} disp.[/color]" if prod.stock > 0 else "[color=#EF4444]Agotado[/color]",
                    markup=True,
                    halign="right",
                    font_style="Label",
                    role="small",
                )
            )

            # Row 3: Ingredients (Shortened cleanly with ellipsis)
            display_ingredients = prod.ingredients or prod.description or "Plato del día"
            ing_label = MDLabel(
                text=f"[color=#64748B]{display_ingredients}[/color]",
                markup=True,
                font_style="Body",
                role="small",
                size_hint_y=None,
                height=dp(18),
                shorten=True,
                shorten_from="right",
            )

            # Row 4: Action Button
            bottom_line = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(28))
            bottom_line.add_widget(MDBoxLayout())  # spacer
            add_btn = MDButton(
                MDButtonText(text="+ Agregar"),
                style="tonal",
                size_hint_y=None,
                height=dp(28),
                on_release=lambda x, p=prod.id_producto: self._on_add_product(p),
            )
            bottom_line.add_widget(add_btn)

            card.add_widget(top_line)
            card.add_widget(badge_line)
            card.add_widget(ing_label)
            card.add_widget(bottom_line)
            self.products_container.add_widget(card)

        self._update_cart_label()

    def _on_select_category(self, category: str):
        self.selected_category = category
        self.status_label.text = f"Filtrando: {category}"
        self.refresh_catalog()

    def _on_add_product(self, product_id: str):
        try:
            self.order_service.add_to_cart(product_id, 1)
            self.status_label.text = "Plato agregado al carrito."
            self._update_cart_label()
        except ValueError as e:
            self.status_label.text = f"Error: {str(e)}"

    def _on_clear_cart(self):
        self.order_service.clear_cart()
        self.status_label.text = "Carrito vaciado."
        self._update_cart_label()

    def _update_cart_label(self):
        items = self.order_service.get_cart_items()
        total = self.order_service.get_cart_total()
        count = sum(i.quantity for i in items)
        if count == 0:
            self.cart_label.text = "Carrito vacío"
        else:
            self.cart_label.text = f"Carrito: {count} ítem(s) - Total: {format_currency(total)}"

    def _ask_reservation_confirmation(self):
        """Display action confirmation dialog."""
        items = self.order_service.get_cart_items()
        if not items:
            self.status_label.text = "El carrito está vacío. Agrega platos antes de reservar."
            return

        total = self.order_service.get_cart_total()
        user = self.auth_service.current_user

        self._hide_modal()

        self.confirm_modal = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(135),
            padding=[dp(12), dp(10), dp(12), dp(10)],
            spacing=dp(6),
            style="elevated",
            md_bg_color=[1, 1, 1, 1],
            radius=[dp(14), dp(14), dp(14), dp(14)],
        )
        modal_title = MDLabel(
            text="[color=#0A3871][b]Confirmar Reserva de Comanda[/b][/color]",
            markup=True,
            font_style="Title",
            role="small",
            size_hint_y=None,
            height=dp(22),
        )
        modal_msg = MDLabel(
            text=f"Total: {format_currency(total)} | Titular: {user.name}\n¿Confirmar y enviar a cocina en caja?",
            size_hint_y=None,
            height=dp(36),
            font_style="Body",
            role="small",
        )
        modal_btns = MDBoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(34))

        cancel_btn = MDButton(
            MDButtonText(text="Cancelar"),
            style="tonal",
            on_release=lambda x: self._hide_modal(),
        )
        confirm_btn = MDButton(
            MDButtonText(text="Sí, Confirmar"),
            style="filled",
            on_release=lambda x: self._execute_reservation(),
        )
        modal_btns.add_widget(cancel_btn)
        modal_btns.add_widget(confirm_btn)

        self.confirm_modal.add_widget(modal_title)
        self.confirm_modal.add_widget(modal_msg)
        self.confirm_modal.add_widget(modal_btns)

        self.root_layout.add_widget(self.confirm_modal, index=2)

    def _hide_modal(self):
        if self.confirm_modal and self.confirm_modal in self.root_layout.children:
            self.root_layout.remove_widget(self.confirm_modal)
            self.confirm_modal = None

    def _execute_reservation(self):
        self._hide_modal()
        try:
            order = self.order_service.checkout()
            self.status_label.text = f"¡Éxito! Comanda #{order.comanda_number} reservada."
            self.refresh_catalog()
        except ValueError as e:
            self.status_label.text = f"Error: {str(e)}"
