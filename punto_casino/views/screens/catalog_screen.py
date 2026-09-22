"""Responsive product catalog matching PRONTO CASINO UCT wireframe with clean layout, vibrant offers, and high contrast."""

from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButtonIcon
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen

from punto_casino.core.config import config, get_category_style
from punto_casino.models.user import UserRole
from punto_casino.services.order_service import OrderService
from punto_casino.services.auth_service import AuthService
from punto_casino.utils.formatters import format_currency
from punto_casino.views.components.ui_elements import (
    create_button,
    create_offer_badge,
    LIGHT_GREEN,
    SOFT_MINT,
    UCT_NAVY,
    WHITE,
)


class CatalogScreen(MDScreen):
    """Product catalog with responsive card layout, category filtering, vibrant offer cards, and student/guest balance."""

    def __init__(self, order_service: OrderService, auth_service: AuthService, **kwargs):
        super().__init__(**kwargs)
        self.order_service = order_service
        self.auth_service = auth_service
        self.selected_category = "Todos"
        self._loaded_category = None
        self._is_dirty = True

        self.root_layout = None
        self.balance_label = None
        self.cart_label = None
        self.status_label = None
        self.products_container = None
        self.cat_box = None
        self.confirm_modal = None
        self.desc_label = None

        self._build_ui()

    def _build_ui(self):
        self.root_layout = MDBoxLayout(
            orientation="vertical",
            padding=[dp(14), dp(10), dp(14), dp(10)],
            spacing=dp(8),
            theme_bg_color="Custom",
            md_bg_color=[0.96, 0.97, 0.99, 1.0],
        )

        # 1. Location & User Role Banner (Symmetrical & High Contrast)
        banner = MDCard(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(38),
            padding=[dp(14), dp(6), dp(14), dp(6)],
            style="outlined",
            theme_bg_color="Custom",
            md_bg_color=[1, 1, 1, 1],
            radius=[dp(10), dp(10), dp(10), dp(10)],
            line_color=[0.88, 0.92, 0.96, 1],
            elevation=0,
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

        # 2. Category Tabs Horizontal Scroll (With crisp icons and no square glyphs)
        cat_scroll = ScrollView(size_hint=(1, None), height=dp(42), do_scroll_x=True, do_scroll_y=False)
        self.cat_box = MDBoxLayout(orientation="horizontal", spacing=dp(6), size_hint_x=None)
        self.cat_box.bind(minimum_width=self.cat_box.setter("width"))

        self._rebuild_category_tabs()
        cat_scroll.add_widget(self.cat_box)
        self.root_layout.add_widget(cat_scroll)

        # 4. Products List (Scrollable)
        scroll = ScrollView(size_hint=(1, 1))
        self.products_container = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
        )
        self.products_container.bind(minimum_height=self.products_container.setter("height"))
        scroll.add_widget(self.products_container)
        self.root_layout.add_widget(scroll)

        # 5. Cart Summary & Action Footer (High Contrast)
        footer = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(92),
            padding=[dp(12), dp(8), dp(12), dp(8)],
            spacing=dp(4),
            style="outlined",
            theme_bg_color="Custom",
            md_bg_color=[1, 1, 1, 1],
            radius=[dp(14), dp(14), dp(14), dp(14)],
            line_color=[0.88, 0.92, 0.96, 1],
            elevation=0,
        )
        self.cart_label = MDLabel(
            text="Carrito vacío",
            bold=True,
            markup=True,
            size_hint_y=None,
            height=dp(20),
            font_style="Title",
            role="small",
        )
        self.status_label = MDLabel(
            text="",
            markup=True,
            size_hint_y=None,
            height=dp(20),
            font_style="Label",
            role="small",
        )

        actions_box = MDBoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(34))
        clear_btn = create_button(
            text="Vaciar",
            icon="trash-can-outline",
            style="outlined",
            size_hint=(0.35, None),
            height=dp(34),
            on_release=lambda x: self._on_clear_cart(),
        )
        order_btn = create_button(
            text="Reservar Comanda",
            icon="cart-check",
            style="filled",
            size_hint=(0.65, None),
            height=dp(34),
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

    def _rebuild_category_tabs(self):
        """Build category filter buttons with crisp vector icons and active highlights."""
        self.cat_box.clear_widgets()

        categories = [
            ("Todos", "Todos", "silverware"),
            ("Ofertas", "Ofertas", "sale"),
            ("Menú Normal", "Normal", "food"),
            ("Menú Ejecutivo", "Ejecutivo", "star"),
            ("Menú Hipocalórico", "Hipocalórico", "leaf"),
            ("Menú Vegetariano", "Vegetariano", "sprout"),
            ("Comidas Rápidas", "Rápidas", "hamburger"),
            ("Bebidas", "Bebidas", "cup"),
        ]

        for full_cat, display_name, icon_name in categories:
            is_active = (self.selected_category == full_cat) or (
                full_cat == "Ofertas" and "oferta" in self.selected_category.lower()
            )

            if is_active:
                btn_style = "offer" if "oferta" in full_cat.lower() else "filled"
            else:
                btn_style = "tonal"

            btn = create_button(
                text=display_name,
                icon=icon_name,
                style=btn_style,
                size_hint=(None, None),
                height=dp(34),
                on_release=lambda x, c=full_cat: self._on_select_category(c),
            )
            self.cat_box.add_widget(btn)

    def on_enter(self):
        """Update balance and cart on screen enter; only rebuild catalog if dirty or category changed."""
        user = self.auth_service.current_user
        if user:
            if user.role == UserRole.CLIENT:
                self.balance_label.text = "[color=#0288D1][b]Estudiante UCT[/b][/color]"
            elif user.role == UserRole.GUEST:
                self.balance_label.text = "[color=#EA580C][b]Invitado UCT[/b][/color]"
            else:
                self.balance_label.text = f"[color=#64748B][b]{user.role.value}[/b][/color]"
        self._update_cart_label()

        if self._is_dirty or self._loaded_category != self.selected_category:
            self.refresh_catalog()

    def refresh_catalog(self):
        self._loaded_category = self.selected_category
        self._is_dirty = False

        user = self.auth_service.current_user
        if user:
            if user.role == UserRole.CLIENT:
                self.balance_label.text = "[color=#0288D1][b]Estudiante UCT[/b][/color]"
            elif user.role == UserRole.GUEST:
                self.balance_label.text = "[color=#EA580C][b]Invitado UCT[/b][/color]"
            else:
                self.balance_label.text = f"[color=#64748B][b]{user.role.value}[/b][/color]"

        self.products_container.clear_widgets()

        # Human-readable scrollable description that scrolls up with dish cards
        self.desc_label = MDLabel(
            text="[color=#64748B]Selecciona tus platos de hoy y retira en casino sin hacer filas.[/color]",
            font_style="Body",
            role="small",
            size_hint_y=None,
            height=dp(30),
            markup=True,
            padding=[dp(4), dp(2), dp(4), dp(6)],
        )
        self.products_container.add_widget(self.desc_label)

        products = self.order_service.product_repo.get_by_category(self.selected_category)

        # Empty state handling
        if not products:
            empty_card = MDCard(
                orientation="vertical",
                size_hint_y=None,
                height=dp(110),
                padding=[dp(16), dp(14), dp(16), dp(14)],
                spacing=dp(6),
                style="outlined",
                theme_bg_color="Custom",
                md_bg_color=[1, 1, 1, 1],
                radius=[dp(12), dp(12), dp(12), dp(12)],
                line_color=[0.88, 0.92, 0.96, 1],
                elevation=0,
            )
            empty_card.add_widget(
                MDLabel(
                    text="[b][color=#0A3871]No hay productos disponibles[/color][/b]",
                    markup=True,
                    font_style="Title",
                    role="small",
                    halign="center",
                    size_hint_y=None,
                    height=dp(22),
                )
            )
            empty_card.add_widget(
                MDLabel(
                    text="No se encontraron platos activos para esta categoría en este momento.\nPrueba seleccionando 'Todos' o consulta en caja.",
                    markup=True,
                    font_style="Body",
                    role="small",
                    halign="center",
                    size_hint_y=None,
                    height=dp(38),
                )
            )
            self.products_container.add_widget(empty_card)
            self._update_cart_label()
            return

        for prod in products:
            card_h = dp(154) if prod.is_offer else dp(128)
            card_bg = SOFT_MINT if prod.is_offer else WHITE
            card_border = LIGHT_GREEN if prod.is_offer else [0.88, 0.92, 0.96, 1]

            card = MDCard(
                orientation="vertical",
                size_hint_y=None,
                height=card_h,
                padding=[dp(14), dp(8), dp(14), dp(8)],
                spacing=dp(4),
                style="outlined",
                theme_bg_color="Custom",
                md_bg_color=card_bg,
                radius=[dp(12), dp(12), dp(12), dp(12)],
                line_color=card_border,
                elevation=0,
            )

            # Row 1: Title and Price (Symmetrical and high contrast)
            top_line = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(24), spacing=dp(4))

            # Small offer icon indicating discount on the product card
            if prod.is_offer:
                top_line.add_widget(
                    MDButtonIcon(
                        icon="sale",
                        theme_icon_color="Custom",
                        icon_color=LIGHT_GREEN,
                        size_hint=(None, None),
                        size=(dp(18), dp(18)),
                    )
                )

            top_line.add_widget(
                MDLabel(
                    text=f"[b][color=#0A3871]{prod.name}[/color][/b]",
                    markup=True,
                    font_style="Title",
                    role="small",
                    shorten=True,
                    shorten_from="right",
                )
            )

            if prod.is_offer and prod.original_price:
                price_markup = (
                    f"[s][color=#94A3B8]{format_currency(prod.original_price)}[/color][/s]  "
                    f"[b][color=#DC2626]{format_currency(prod.price)}[/color][/b]"
                )
            else:
                price_markup = f"[b][color=#0288D1]{format_currency(prod.price)}[/color][/b]"

            top_line.add_widget(
                MDLabel(
                    text=price_markup,
                    markup=True,
                    halign="right",
                    font_style="Title",
                    role="small",
                    size_hint_x=None,
                    width=dp(130),
                )
            )
            card.add_widget(top_line)

            # Row 1.5: Vibrant Offer Badge (if product is discounted/near-expiry)
            if prod.is_offer:
                card.add_widget(create_offer_badge(prod.offer_label or "Precio Rebajado"))

            # Row 2: Category and Stock Badges
            badge_line = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(18))
            cat_style = get_category_style(prod.category)
            badge_line.add_widget(
                MDLabel(
                    text=f"[b][color={cat_style['hex']}]{prod.category}[/color][/b]",
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
            card.add_widget(badge_line)

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
            card.add_widget(ing_label)

            # Row 4: Action Button with High Contrast
            bottom_line = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(30))
            bottom_line.add_widget(MDBoxLayout())  # spacer
            add_btn = create_button(
                text="Agregar",
                icon="plus",
                style="offer" if prod.is_offer else "tonal",
                size_hint=(None, None),
                height=dp(28),
                on_release=lambda x, p=prod.id_producto: self._on_add_product(p),
            )
            bottom_line.add_widget(add_btn)
            card.add_widget(bottom_line)

            self.products_container.add_widget(card)

        self._update_cart_label()

    def _on_select_category(self, category: str):
        self.selected_category = category
        self.status_label.text = f"Filtrando: {category}"
        self._rebuild_category_tabs()
        self.refresh_catalog()

    def _on_add_product(self, product_id: str):
        try:
            self.order_service.add_to_cart(product_id, 1)
            self.status_label.text = "[color=#10B981]Plato agregado al carrito.[/color]"
            self._update_cart_label()
        except ValueError as e:
            self.status_label.text = f"[color=#EF4444]Error: {str(e)}[/color]"

    def _on_clear_cart(self):
        self.order_service.clear_cart()
        self.status_label.text = "[color=#64748B]Carrito vaciado.[/color]"
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
            self.status_label.text = "[color=#EF4444]El carrito está vacío. Agrega platos antes de reservar.[/color]"
            return

        total = self.order_service.get_cart_total()
        user = self.auth_service.current_user

        self._hide_modal()

        self.confirm_modal = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(140),
            padding=[dp(14), dp(12), dp(14), dp(12)],
            spacing=dp(6),
            style="outlined",
            theme_bg_color="Custom",
            md_bg_color=[1, 1, 1, 1],
            radius=[dp(14), dp(14), dp(14), dp(14)],
            line_color=[0.04, 0.22, 0.44, 0.4],
            elevation=0,
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
        modal_btns = MDBoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(36))

        cancel_btn = create_button(
            text="Cancelar",
            style="tonal",
            size_hint=(0.5, None),
            height=dp(34),
            on_release=lambda x: self._hide_modal(),
        )
        confirm_btn = create_button(
            text="Confirmar",
            icon="check",
            style="filled",
            size_hint=(0.5, None),
            height=dp(34),
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
            self.status_label.text = f"[color=#10B981]¡Éxito! Comanda #{order.comanda_number} reservada.[/color]"
            self.refresh_catalog()
        except ValueError as e:
            self.status_label.text = f"[color=#EF4444]Error: {str(e)}[/color]"
