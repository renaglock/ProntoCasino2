from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButtonIcon
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField, MDTextFieldLeadingIcon

from punto_casino.core.config import config, get_category_style
from punto_casino.models.order import (
    PaymentMethod,
    PAYMENT_METHOD_LABELS,
    PAYMENT_METHOD_ICONS,
)
from punto_casino.models.user import UserRole
from punto_casino.services.order_service import OrderService
from punto_casino.services.auth_service import AuthService
from punto_casino.services.analytics_service import variante_ab
from punto_casino.utils.formatters import format_currency
from punto_casino.views.components.ui_elements import (
    ICON_OK, ICON_WARN,
    create_button,
    create_offer_badge,
    create_category_pill,
    create_category_title_header,
    LIGHT_GREEN,
    SOFT_MINT,
    UCT_NAVY,
    WHITE,
)


class CatalogScreen(MDScreen):
    """Product catalog with responsive card layout, category filtering, vibrant offer cards, and student/guest balance."""

    def __init__(self, order_service: OrderService, auth_service: AuthService, on_navigate=None, **kwargs):
        super().__init__(**kwargs)
        self.order_service = order_service
        self.auth_service = auth_service
        self.on_navigate = on_navigate
        self.selected_category = "Todos"
        self.search_text = ""
        self.selected_payment_method = PaymentMethod.EFECTIVO_POS.value
        self._show_online_methods = False  # pasarela: False = reservar sin pagar, True = medios en línea
        self._loaded_category = None
        self._is_dirty = True

        self.root_layout = None
        self.balance_label = None
        self.cart_label = None
        self.status_label = None
        self.products_container = None
        self.cat_box = None
        self.confirm_modal = None
        self.payment_modal = None
        self.bottom_spacer = None
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

        # Search bar, fixed above the scroll
        search_field = MDTextField(
            MDTextFieldLeadingIcon(icon="magnify"),
            mode="outlined",
            multiline=False,
            height=dp(44),  # KivyMD fija 56dp; igualamos al contenedor para no chocar con el banner
        )
        search_field.bind(text=self._on_search_text_changed)
        # Placeholder fijo encima del campo: se oculta al hacer clic, sin animación flotante
        placeholder = MDLabel(
            text="Buscar plato o ingrediente...",
            theme_text_color="Custom",
            text_color=[0.45, 0.5, 0.55, 1],
            pos=(dp(52), 0),
            size_hint=(1, 1),
        )

        def _toggle_placeholder(*_):
            placeholder.opacity = 0 if (search_field.focus or search_field.text) else 1

        search_field.bind(focus=_toggle_placeholder, text=_toggle_placeholder)
        search_box = RelativeLayout(size_hint_y=None, height=dp(44))
        search_box.add_widget(search_field)
        search_box.add_widget(placeholder)
        self.root_layout.add_widget(search_box)

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
            if is_active:
                cat_st = get_category_style(full_cat)
                btn.md_bg_color = cat_st["rgba"]
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

        repo = self.order_service.product_repo
        products = repo.get_by_category(self.selected_category)
        if self.search_text.strip():
            found = {p.id_producto for p in repo.search(self.search_text)}
            products = [p for p in products if p.id_producto in found]

        # Standardized Category Title Header
        self.products_container.add_widget(
            create_category_title_header(self.selected_category, count=len(products))
        )

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

            # Row 2: Category Pill & Stock Pill (Standardized M3 Pill Component)
            badge_line = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(20), spacing=dp(6))
            cat_pill = create_category_pill(prod.category)
            stock_color = "#10B981" if prod.stock > 0 else "#EF4444"
            stock_msg = f"{prod.stock} disp." if prod.stock > 0 else "Agotado"
            stock_lbl = MDLabel(
                text=f"[color={stock_color}][b]{stock_msg}[/b][/color]",
                markup=True,
                halign="right",
                font_style="Label",
                role="small",
            )
            badge_line.add_widget(cat_pill)
            badge_line.add_widget(stock_lbl)
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

    def _on_search_text_changed(self, instance, text: str):
        self.search_text = text
        self.refresh_catalog()

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
        """Display cart confirmation dialog with 'Pagar' button leading to payment gateway."""
        items = self.order_service.get_cart_items()
        if not items:
            self.status_label.text = "[color=#EF4444]El carrito está vacío. Agrega platos antes de pagar.[/color]"
            return

        total = self.order_service.get_cart_total()
        user = self.auth_service.current_user

        self._hide_modal()

        self.confirm_modal = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(150),
            padding=[dp(16), dp(12), dp(16), dp(12)],
            spacing=dp(8),
            style="outlined",
            theme_bg_color="Custom",
            md_bg_color=[1, 1, 1, 1],
            radius=[dp(14), dp(14), dp(14), dp(14)],
            line_color=[0.04, 0.22, 0.44, 0.4],
            elevation=0,
        )
        modal_title = MDLabel(
            text="[color=#0A3871][b]Confirmar Carrito de Comanda[/b][/color]",
            markup=True,
            font_style="Title",
            role="small",
            size_hint_y=None,
            height=dp(22),
            halign="center",
        )
        modal_msg = MDLabel(
            text=f"Total: [b]{format_currency(total)}[/b] | Titular: [b]{user.name}[/b]\nPaga ahora para preparar en cocina y retirar sin hacer filas.",
            size_hint_y=None,
            height=dp(38),
            font_style="Body",
            role="small",
            markup=True,
            halign="center",
        )
        modal_btns = MDBoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(36))

        cancel_btn = create_button(
            text="Cancelar",
            style="tonal",
            size_hint=(0.48, None),
            height=dp(34),
            on_release=lambda x: self._hide_modal(),
        )
        pay_btn = create_button(
            text="Continuar",
            icon="arrow-right",
            style="offer",
            size_hint=(0.52, None),
            height=dp(34),
            # A/B (data/remote_config.json): B abre la pasarela directo en los medios en línea
            on_release=lambda x: self._set_gateway_view(
                online=variante_ab(self.auth_service.current_user.id_usuario) == "B"
            ),
        )
        modal_btns.add_widget(cancel_btn)
        modal_btns.add_widget(pay_btn)

        self.confirm_modal.add_widget(modal_title)
        self.confirm_modal.add_widget(modal_msg)
        self.confirm_modal.add_widget(modal_btns)

        self.root_layout.add_widget(self.confirm_modal, index=2)

    def _show_payment_gateway_modal(self):
        """Display Chilean higher-ed payment gateway conforming to Punto 4 of Plan de Expansión."""
        self._hide_modal()

        items = self.order_service.get_cart_items()
        if not items:
            self.status_label.text = "[color=#EF4444]El carrito está vacío.[/color]"
            return

        total = self.order_service.get_cart_total()

        # Temporarily hide scroll to cleanly anchor payment modal at top with bottom spacer
        if hasattr(self, "scroll") and self.scroll:
            self.scroll.opacity = 0
            self.scroll.size_hint_y = None
            self.scroll.height = 0
            self.scroll.disabled = True

        if not hasattr(self, "bottom_spacer") or not self.bottom_spacer:
            self.bottom_spacer = Widget(size_hint_y=1)
        if self.bottom_spacer not in self.root_layout.children:
            self.root_layout.add_widget(self.bottom_spacer, index=0)

        online = self._show_online_methods
        reservation = None if online else self.order_service.get_active_reservation()
        too_many = self.order_service.get_cart_count() > 1
        can_reserve = reservation is None and not too_many
        if online:
            options = [
                (PaymentMethod.WEBPAY_PLUS.value, "Webpay Plus", "Transbank: débito, crédito y CuentaRUT", "credit-card", True),
                (PaymentMethod.BAES_JUNAEB.value, "Beca BAES", "No disponible por ahora", "school", False),
                (PaymentMethod.FINTOC_KHIPU.value, "Transferencia Bancaria", "No disponible por ahora", "bank-transfer", False),
                (PaymentMethod.BECA_INTERNA.value, "Beca DAE", "No disponible por ahora", "card-account-details-star", False),
            ]
        else:
            if reservation:
                reserve_desc = f"Ya tienes la reserva #{reservation.comanda_number} activa"
            elif too_many:
                reserve_desc = "Solo 1 plato por reserva sin pago"
            else:
                reserve_desc = "Pagas al retirar en caja"
            options = [
                (PaymentMethod.EFECTIVO_POS.value, "Reservar sin pagar", reserve_desc, "cash-register", can_reserve),
            ]
        options_h = len(options) * dp(46) + (len(options) - 1) * dp(5)
        # padding 24 + título 24 + monto 20 + subtítulo 18 + acciones 36 = 122; spacing 6 entre hijos
        modal_h = dp(122) + options_h + (dp(24) if online else dp(84) + dp(36))

        self.payment_modal = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=modal_h,
            padding=[dp(16), dp(12), dp(16), dp(12)],
            spacing=dp(6),
            style="outlined",
            theme_bg_color="Custom",
            md_bg_color=[1.0, 1.0, 1.0, 1.0],
            radius=[dp(16), dp(16), dp(16), dp(16)],
            line_color=[0.04, 0.22, 0.44, 0.4],
            elevation=0,
        )

        # 1. Header
        p_title = MDLabel(
            text="[b][color=#0A3871]Pasarela de Pago Seguro UCT[/color][/b]",
            markup=True,
            halign="center",
            font_style="Title",
            role="medium",
            size_hint_y=None,
            height=dp(24),
        )
        p_amount = MDLabel(
            text=f"Total a pagar: [b][color=#0288D1]{format_currency(total)}[/color][/b]",
            markup=True,
            halign="center",
            font_style="Title",
            role="small",
            size_hint_y=None,
            height=dp(20),
        )
        p_subtitle = MDLabel(
            text=f"[color=#64748B]{'Medios de pago en línea:' if online else 'Medio de pago oficial:'}[/color]",
            markup=True,
            halign="center",
            font_style="Body",
            role="small",
            size_hint_y=None,
            height=dp(18),
        )
        self.payment_modal.add_widget(p_title)
        self.payment_modal.add_widget(p_amount)
        self.payment_modal.add_widget(p_subtitle)

        # 2. Options List
        self.options_container = MDBoxLayout(
            orientation="vertical",
            spacing=dp(5),
            size_hint_y=None,
            height=options_h,
        )

        for method_val, name, desc, icon_name, enabled in options:
            is_active = enabled and self.selected_payment_method == method_val
            card_opt = self._build_payment_option_card(method_val, name, desc, icon_name, is_active, enabled)
            self.options_container.add_widget(card_opt)

        self.payment_modal.add_widget(self.options_container)

        if not online:
            alert_lbl = MDLabel(
                text=(
                    f"[color=#D97706]{ICON_WARN} Tienes [b]1 hora[/b] para retirar y pagar en caja; si no, la reserva se pierde. "
                    "Máximo [b]1 reserva sin pago de 1 plato[/b]: para más, paga por adelantado.[/color]"
                ),
                markup=True,
                font_style="Body",
                role="small",
                size_hint_y=None,
                height=dp(48),
            )
            self.payment_modal.add_widget(alert_lbl)
            self.payment_modal.add_widget(
                create_button(
                    text="Ver medios de pago",
                    icon="credit-card-outline",
                    style="outlined",
                    size_hint=(1, None),
                    height=dp(36),
                    on_release=lambda x: self._set_gateway_view(online=True),
                )
            )

        # 3. Actions Row
        actions_row = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(36),
        )
        btn_back = create_button(
            text="Atrás" if online else "Volver",
            style="tonal",
            size_hint=(0.35, None),
            height=dp(36),
            on_release=(lambda x: self._set_gateway_view(online=False)) if online else (lambda x: self._hide_modal()),
        )
        btn_pay = create_button(
            text=f"Pagar {format_currency(total)}" if online else "Reservar Comanda",
            icon="credit-card-check" if online else "calendar-check",
            style="offer",
            size_hint=(0.65, None),
            height=dp(36),
            on_release=lambda x: self._execute_payment(),
        )
        btn_pay.disabled = not online and not can_reserve
        actions_row.add_widget(btn_back)
        actions_row.add_widget(btn_pay)
        self.payment_modal.add_widget(actions_row)

        self.root_layout.add_widget(self.payment_modal, index=1)

    def _build_payment_option_card(
        self, method_val: str, name: str, desc: str, icon_name: str, is_active: bool, enabled: bool = True
    ) -> MDCard:
        bg_col = [0.90, 0.94, 0.98, 1.0] if is_active else [1.0, 1.0, 1.0, 1.0]
        border_col = [0.04, 0.22, 0.44, 0.9] if is_active else [0.88, 0.92, 0.96, 1.0]
        extra = {"on_release": lambda x, m=method_val: self._select_payment_method(m)} if enabled else {}

        card = MDCard(
            orientation="horizontal",
            size_hint=(1, None),
            height=dp(46),
            padding=[dp(10), dp(4), dp(10), dp(4)],
            spacing=dp(8),
            style="outlined",
            theme_bg_color="Custom",
            md_bg_color=bg_col,
            radius=[dp(10), dp(10), dp(10), dp(10)],
            line_color=border_col,
            elevation=0,
            opacity=1 if enabled else 0.45,  # medios deshabilitados: visibles pero no seleccionables
            **extra,
        )

        icon_box = MDBoxLayout(size_hint=(None, 1), width=dp(28))
        icon = MDIcon(
            icon=icon_name,
            theme_icon_color="Custom",
            icon_color=[0.04, 0.22, 0.44, 1.0] if is_active else [0.39, 0.45, 0.55, 1.0],
            size_hint=(None, None),
            size=(dp(20), dp(20)),
            pos_hint={"center_y": 0.5},
        )
        icon_box.add_widget(icon)

        text_box = MDBoxLayout(orientation="vertical", size_hint=(1, 1), spacing=dp(1))
        title_lbl = MDLabel(
            text=f"[b][color=#0A3871]{name}[/color][/b]" if is_active else f"[color=#1E293B]{name}[/color]",
            markup=True,
            font_style="Label",
            role="large",
            shorten=True,
            shorten_from="right",
            size_hint_y=None,
            height=dp(18),
        )
        desc_lbl = MDLabel(
            text=f"[color=#64748B]{desc}[/color]",
            markup=True,
            font_style="Body",
            role="small",
            shorten=True,
            shorten_from="right",
            size_hint_y=None,
            height=dp(14),
        )
        text_box.add_widget(title_lbl)
        text_box.add_widget(desc_lbl)

        check_box = MDBoxLayout(size_hint=(None, 1), width=dp(24))
        if is_active:
            check_icon = MDIcon(
                icon="check-circle",
                theme_icon_color="Custom",
                icon_color=[0.06, 0.65, 0.45, 1.0],
                size_hint=(None, None),
                size=(dp(18), dp(18)),
                pos_hint={"center_y": 0.5},
            )
            check_box.add_widget(check_icon)

        card.add_widget(icon_box)
        card.add_widget(text_box)
        card.add_widget(check_box)
        return card

    def _select_payment_method(self, method_val: str):
        self.selected_payment_method = method_val
        self._show_payment_gateway_modal()

    def _set_gateway_view(self, online: bool):
        """Alterna la pasarela entre 'Reservar sin pagar' y la lista de medios en línea."""
        self._show_online_methods = online
        self.selected_payment_method = (
            PaymentMethod.WEBPAY_PLUS.value if online else PaymentMethod.EFECTIVO_POS.value
        )
        self._show_payment_gateway_modal()

    def _execute_payment(self):
        self._hide_modal()
        try:
            pay_method = self.selected_payment_method
            pay_label = PAYMENT_METHOD_LABELS.get(pay_method, pay_method)
            is_paid = pay_method != PaymentMethod.EFECTIVO_POS.value
            order = self.order_service.checkout(
                payment_method=pay_method,
                is_paid=is_paid,
            )
            if is_paid:
                self.status_label.text = (
                    f"[color=#10B981]{ICON_OK} ¡Pago exitoso con {pay_label}! "
                    f"Comanda #{order.comanda_number} en preparación. Retira con tu QR.[/color]"
                )
            else:
                self.status_label.text = (
                    f"[color=#10B981]{ICON_OK} Comanda #{order.comanda_number} reservada ({order.id_pedido}). "
                    f"Tienes 1 hora para retirar y pagar en caja.[/color]"
                )
            self.refresh_catalog()
            if self.on_navigate:
                Clock.schedule_once(lambda dt: self.on_navigate("reservations"), 0.5)
        except ValueError as e:
            self.status_label.text = f"[color=#EF4444]Error: {str(e)}[/color]"

    def _hide_modal(self):
        if hasattr(self, "bottom_spacer") and self.bottom_spacer:
            if self.bottom_spacer in self.root_layout.children:
                self.root_layout.remove_widget(self.bottom_spacer)
            self.bottom_spacer = None
        if hasattr(self, "scroll") and self.scroll:
            self.scroll.opacity = 1
            self.scroll.size_hint_y = 1
            self.scroll.disabled = False
        if self.confirm_modal and self.confirm_modal in self.root_layout.children:
            self.root_layout.remove_widget(self.confirm_modal)
            self.confirm_modal = None
        if self.payment_modal and self.payment_modal in self.root_layout.children:
            self.root_layout.remove_widget(self.payment_modal)
            self.payment_modal = None
