"""Admin screen with spacious CRUD, near-expiry discounts, and sales order history."""

from typing import Optional
from kivy.metrics import dp
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

from punto_casino.models.order import OrderStatus, ORDER_STATUS_LABELS, ORDER_STATUS_COLORS
from punto_casino.models.product import Product
from punto_casino.repositories.product_repository import InMemoryProductRepository
from punto_casino.services.order_service import OrderService
from punto_casino.utils.formatters import format_currency
from punto_casino.views.components.ui_elements import (
    create_button,
    create_offer_badge,
    VIBRANT_ORANGE,
    UCT_ICE_BLUE,
    UCT_NAVY,
    WHITE,
)


class AdminScreen(MDScreen):
    """Admin dashboard with full spacious CRUD, near-expiry discounts, and sales order history."""

    def __init__(
        self,
        product_repo: InMemoryProductRepository,
        on_navigate,
        order_service: Optional[OrderService] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.product_repo = product_repo
        self.order_service = order_service
        self.on_navigate = on_navigate

        self.current_tab = "crud"  # "crud" or "history"
        self._editing_product_id: Optional[str] = None
        self._is_offer_active = False

        self.root_layout = None
        self.status_label = None
        self.confirm_modal = None

        # Form widgets
        self.input_id = None
        self.input_name = None
        self.input_cat = None
        self.input_price = None
        self.input_stock = None
        self.input_ingredients = None
        self.input_offer_price = None
        self.input_offer_label = None
        self.toggle_offer_btn = None
        self.toggle_offer_text = None
        self.offer_card = None
        self.offer_fields_layout = None

        self.root_layout = MDBoxLayout(orientation="vertical")
        self.add_widget(self.root_layout)
        self._show_list_view()

    def on_enter(self):
        """Called when admin screen is visited."""
        self._show_list_view()

    # =========================================================================
    # 1. MAIN LIST VIEW (CRUD & HISTORY)
    # =========================================================================

    def _show_list_view(self):
        """Render the main catalog list and tabbed view without cramming."""
        self.root_layout.clear_widgets()

        container = MDBoxLayout(
            orientation="vertical",
            padding=[dp(14), dp(10), dp(14), dp(10)],
            spacing=dp(8),
        )

        # Header with Title and '+ Nuevo Plato' Button
        title_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(36),
            spacing=dp(8),
        )
        title_lbl = MDLabel(
            text="[b][color=#0A3871]Administración Casino UCT[/color][/b]",
            markup=True,
            font_style="Title",
            role="medium",
        )
        self.new_dish_btn = create_button(
            text="+ Nuevo Plato",
            icon="plus",
            style="filled",
            size_hint=(None, None),
            height=dp(34),
            width=dp(140),
            on_release=lambda x: self._open_create_form(),
        )
        title_row.add_widget(title_lbl)
        title_row.add_widget(self.new_dish_btn)
        container.add_widget(title_row)

        # Tab Switcher: [Platos (CRUD)] vs [Historial y Ventas]
        tabs_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(36),
            spacing=dp(8),
        )
        self.btn_tab_crud = create_button(
            text="Platos (CRUD)",
            icon="silverware-fork-knife",
            style="filled" if self.current_tab == "crud" else "tonal",
            size_hint=(0.5, None),
            height=dp(34),
            on_release=lambda x: self._switch_tab("crud"),
        )
        self.btn_tab_history = create_button(
            text="Historial y Ventas",
            icon="chart-bar",
            style="filled" if self.current_tab == "history" else "tonal",
            size_hint=(0.5, None),
            height=dp(34),
            on_release=lambda x: self._switch_tab("history"),
        )
        tabs_row.add_widget(self.btn_tab_crud)
        tabs_row.add_widget(self.btn_tab_history)
        container.add_widget(tabs_row)

        # Status feedback label
        status_text = (
            "Catálogo de platos activo. Pulsa '+ Nuevo Plato' o 'Editar' para gestionar ofertas."
            if self.current_tab == "crud"
            else "Historial de ventas y métricas contables del casino."
        )
        self.status_label = MDLabel(
            text=status_text,
            font_style="Body",
            role="small",
            size_hint_y=None,
            height=dp(18),
            markup=True,
        )
        container.add_widget(self.status_label)

        # Scrollable Content
        scroll = ScrollView(size_hint=(1, 1))
        self.content_container = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
        )
        self.content_container.bind(minimum_height=self.content_container.setter("height"))
        scroll.add_widget(self.content_container)
        container.add_widget(scroll)

        self.root_layout.add_widget(container)

        if self.current_tab == "crud":
            self._render_crud_items()
        else:
            self._render_history_items()

    def _switch_tab(self, tab_name: str):
        self.current_tab = tab_name
        self._show_list_view()

    # --- CRUD Products List ---

    def _render_crud_items(self):
        self.content_container.clear_widgets()
        products = self.product_repo.get_all(include_inactive=True)

        for prod in products:
            card_h = dp(156) if prod.is_offer else dp(132)
            card = MDCard(
                orientation="vertical",
                size_hint_y=None,
                height=card_h,
                padding=[dp(14), dp(10), dp(14), dp(10)],
                spacing=dp(5),
                style="elevated",
                md_bg_color=[1.0, 1.0, 1.0, 1.0],
                radius=[dp(12), dp(12), dp(12), dp(12)],
                line_color=[0.88, 0.92, 0.96, 1.0],
                elevation=1,
            )

            # Row 1: Code badge + Title + Price
            row1 = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(24), spacing=dp(6))
            id_lbl = MDLabel(
                text=f"[color=#0A3871][b][{prod.id_producto}][/b][/color]",
                markup=True,
                font_style="Label",
                role="medium",
                size_hint_x=None,
                width=dp(80),
            )
            name_lbl = MDLabel(
                text=f"[b][color=#1E293B]{prod.name}[/color][/b]",
                markup=True,
                font_style="Title",
                role="small",
                shorten=True,
                shorten_from="right",
            )
            price_text = format_currency(prod.price)
            price_lbl = MDLabel(
                text=f"[b][color=#0288D1]{price_text}[/color][/b]",
                markup=True,
                halign="right",
                font_style="Title",
                role="small",
                size_hint_x=None,
                width=dp(80),
            )
            row1.add_widget(id_lbl)
            row1.add_widget(name_lbl)
            row1.add_widget(price_lbl)
            card.add_widget(row1)

            # Row 1.5: Offer Badge (if near-expiry)
            if prod.is_offer:
                offer_msg = prod.offer_label or "Por vencer hoy"
                card.add_widget(create_offer_badge(offer_msg))

            # Row 2: Category & Stock Pill
            row2 = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(20))
            cat_lbl = MDLabel(
                text=f"[color=#64748B]{prod.category}[/color]",
                markup=True,
                font_style="Body",
                role="small",
            )
            stock_color = "#10B981" if prod.stock > 0 else "#EF4444"
            stock_msg = f"{prod.stock} disp." if prod.stock > 0 else "Agotado"
            stock_lbl = MDLabel(
                text=f"[color={stock_color}][b]{stock_msg}[/b][/color]",
                markup=True,
                halign="right",
                font_style="Label",
                role="small",
            )
            row2.add_widget(cat_lbl)
            row2.add_widget(stock_lbl)
            card.add_widget(row2)

            # Row 3: Ingredients / Description
            display_ing = prod.ingredients or prod.description or "Sin detalles"
            ing_lbl = MDLabel(
                text=f"[color=#64748B]{display_ing}[/color]",
                markup=True,
                font_style="Body",
                role="small",
                size_hint_y=None,
                height=dp(18),
                shorten=True,
                shorten_from="right",
            )
            card.add_widget(ing_lbl)

            # Row 4: Action Buttons (Responsive 50/50 proportion)
            actions_row = MDBoxLayout(
                orientation="horizontal",
                spacing=dp(8),
                size_hint_y=None,
                height=dp(34),
            )
            edit_btn = create_button(
                text="Editar / Oferta",
                icon="pencil",
                style="tonal",
                size_hint=(0.5, None),
                height=dp(32),
                on_release=lambda x, p=prod: self._open_edit_form(p),
            )
            del_btn = create_button(
                text="Eliminar",
                icon="delete-outline",
                style="danger",
                size_hint=(0.5, None),
                height=dp(32),
                on_release=lambda x, p=prod: self._ask_delete_confirmation(p),
            )
            actions_row.add_widget(edit_btn)
            actions_row.add_widget(del_btn)
            card.add_widget(actions_row)

            self.content_container.add_widget(card)

    # --- Sales and Order History List ---

    def _render_history_items(self):
        self.content_container.clear_widgets()

        if not self.order_service:
            empty_lbl = MDLabel(
                text="[color=#64748B]Servicio de órdenes no inicializado.[/color]",
                markup=True,
                halign="center",
            )
            self.content_container.add_widget(empty_lbl)
            return

        metrics = self.order_service.get_sales_metrics()

        # Metrics Summary Card
        metrics_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(96),
            padding=[dp(14), dp(10), dp(14), dp(10)],
            spacing=dp(4),
            style="elevated",
            md_bg_color=[0.96, 0.98, 1.0, 1.0],
            radius=[dp(12), dp(12), dp(12), dp(12)],
            line_color=[0.02, 0.53, 0.82, 0.3],
            elevation=1,
        )
        m_title = MDLabel(
            text="[b][color=#0A3871]Resumen Contable del Casino[/color][/b]",
            markup=True,
            font_style="Title",
            role="small",
            size_hint_y=None,
            height=dp(20),
        )
        total_rec_text = format_currency(metrics["total_collected"])
        m_total = MDLabel(
            text=f"[b][color=#10B981]Total Recaudado: {total_rec_text}[/color][/b]",
            markup=True,
            font_style="Headline",
            role="small",
            size_hint_y=None,
            height=dp(26),
        )
        m_stats = MDLabel(
            text=(
                f"Comandas totales: [b]{metrics['total_orders']}[/b]  |  "
                f"Entregadas: [b]{metrics['delivered_count']}[/b]  |  "
                f"Pendientes: [b]{metrics['pending_count']}[/b]  |  "
                f"Canceladas: [b]{metrics['cancelled_count']}[/b]"
            ),
            markup=True,
            font_style="Body",
            role="small",
            size_hint_y=None,
            height=dp(20),
        )
        metrics_card.add_widget(m_title)
        metrics_card.add_widget(m_total)
        metrics_card.add_widget(m_stats)
        self.content_container.add_widget(metrics_card)

        # Chronological Orders
        all_orders = self.order_service.order_repo.get_all()
        if not all_orders:
            no_orders = MDCard(
                size_hint_y=None,
                height=dp(50),
                padding=dp(10),
                style="outlined",
            )
            no_orders.add_widget(
                MDLabel(
                    text="[color=#64748B]Aún no hay comandas registradas.[/color]",
                    markup=True,
                    halign="center",
                )
            )
            self.content_container.add_widget(no_orders)
            return

        for order in all_orders:
            st_text = ORDER_STATUS_LABELS.get(order.status, order.status.value)
            st_color = ORDER_STATUS_COLORS.get(order.status, "#64748B")

            o_card = MDCard(
                orientation="vertical",
                size_hint_y=None,
                height=dp(86),
                padding=[dp(12), dp(8), dp(12), dp(8)],
                spacing=dp(4),
                style="elevated",
                md_bg_color=[1.0, 1.0, 1.0, 1.0],
                radius=[dp(10), dp(10), dp(10), dp(10)],
                line_color=[0.88, 0.92, 0.96, 1.0],
            )
            o_row1 = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(22))
            o_row1.add_widget(
                MDLabel(
                    text=f"[b][color=#0A3871]Comanda #{order.comanda_number}[/color][/b] [color=#64748B]({order.id_pedido})[/color]",
                    markup=True,
                    font_style="Title",
                    role="small",
                )
            )
            o_row1.add_widget(
                MDLabel(
                    text=f"[b]{format_currency(order.total)}[/b]",
                    markup=True,
                    halign="right",
                    font_style="Title",
                    role="small",
                )
            )

            o_row2 = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(18))
            o_row2.add_widget(
                MDLabel(
                    text=f"Cliente: {order.customer_name} • {order.created_at.strftime('%H:%M')}",
                    font_style="Body",
                    role="small",
                )
            )
            o_row2.add_widget(
                MDLabel(
                    text=f"[color={st_color}][b]{st_text}[/b][/color]",
                    markup=True,
                    halign="right",
                    font_style="Label",
                    role="small",
                )
            )

            items_str = ", ".join(f"{i.quantity}x {i.name}" for i in order.items)
            o_row3 = MDLabel(
                text=f"[color=#64748B]Platos: {items_str}[/color]",
                markup=True,
                font_style="Body",
                role="small",
                shorten=True,
                shorten_from="right",
                size_hint_y=None,
                height=dp(18),
            )

            o_card.add_widget(o_row1)
            o_card.add_widget(o_row2)
            o_card.add_widget(o_row3)
            self.content_container.add_widget(o_card)

    # =========================================================================
    # 2. SPACIOUS FULL-SCREEN FORM VIEW (ZERO SQUISHING, 100% RESPONSIVE)
    # =========================================================================

    def _open_create_form(self):
        new_id = f"MENU-0{len(self.product_repo.get_all(True)) + 1}"
        self._editing_product_id = None
        self._is_offer_active = False
        self._render_form_view(
            form_title="Nuevo Plato en Catálogo",
            pid=new_id,
            name="",
            cat="Menú Normal",
            price="4800",
            stock="20",
            ingredients="",
            is_offer=False,
            offer_price="2400",
            offer_label="Por vencer hoy - 50% OFF",
            id_editable=True,
        )

    def _open_edit_form(self, prod: Product):
        self._editing_product_id = prod.id_producto
        self._is_offer_active = prod.is_offer
        normal_price = prod.original_price if prod.is_offer and prod.original_price else prod.price
        off_price = prod.price if prod.is_offer else int(prod.price * 0.5)

        self._render_form_view(
            form_title=f"Editar Plato: {prod.name}",
            pid=prod.id_producto,
            name=prod.name,
            cat=prod.category,
            price=str(normal_price),
            stock=str(prod.stock),
            ingredients=prod.ingredients,
            is_offer=prod.is_offer,
            offer_price=str(off_price),
            offer_label=prod.offer_label or "Por vencer hoy - 50% OFF",
            id_editable=False,
        )

    def _render_form_view(
        self,
        form_title,
        pid,
        name,
        cat,
        price,
        stock,
        ingredients,
        is_offer,
        offer_price,
        offer_label,
        id_editable,
    ):
        """Builds a dedicated, fully-scrollable, comfortable form view without overlapping."""
        self.root_layout.clear_widgets()

        main_box = MDBoxLayout(
            orientation="vertical",
            padding=[dp(14), dp(8), dp(14), dp(8)],
            spacing=dp(8),
        )

        # Form Top Bar
        top_bar = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(40),
            spacing=dp(8),
        )
        back_btn = create_button(
            text="Volver",
            icon="arrow-left",
            style="tonal",
            size_hint=(None, None),
            height=dp(34),
            width=dp(100),
            on_release=lambda x: self._show_list_view(),
        )
        title_lbl = MDLabel(
            text=f"[b][color=#0A3871]{form_title}[/color][/b]",
            markup=True,
            font_style="Title",
            role="medium",
        )
        top_bar.add_widget(back_btn)
        top_bar.add_widget(title_lbl)
        main_box.add_widget(top_bar)

        # Status / Error banner
        self.form_error_lbl = MDLabel(
            text="Completa los datos del plato y activa la oferta si corresponde.",
            font_style="Body",
            role="small",
            size_hint_y=None,
            height=dp(18),
            markup=True,
        )
        main_box.add_widget(self.form_error_lbl)

        # Full-Screen ScrollView for Form inputs
        scroll = ScrollView(size_hint=(1, 1))
        fields_box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(14),
            padding=[dp(4), dp(8), dp(4), dp(24)],
            size_hint_y=None,
        )
        fields_box.bind(minimum_height=fields_box.setter("height"))

        # 1. ID Input
        self.input_id = MDTextField(
            MDTextFieldLeadingIcon(icon="barcode"),
            MDTextFieldHintText(text="ID Producto (ej: MENU-09)"),
            mode="outlined",
            size_hint_y=None,
            height=dp(52),
        )
        self.input_id.text = pid
        self.input_id.disabled = not id_editable
        fields_box.add_widget(self.input_id)

        # 2. Name Input
        self.input_name = MDTextField(
            MDTextFieldLeadingIcon(icon="silverware-fork-knife"),
            MDTextFieldHintText(text="Nombre del Plato"),
            mode="outlined",
            size_hint_y=None,
            height=dp(52),
        )
        self.input_name.text = name
        fields_box.add_widget(self.input_name)

        # 3. Category Input
        self.input_cat = MDTextField(
            MDTextFieldLeadingIcon(icon="tag-outline"),
            MDTextFieldHintText(text="Categoría (Menú Normal, Comidas Rápidas, Bebidas...)"),
            mode="outlined",
            size_hint_y=None,
            height=dp(52),
        )
        self.input_cat.text = cat
        fields_box.add_widget(self.input_cat)

        # 4. Price & Stock Row
        row_ps = MDBoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(52))
        self.input_price = MDTextField(
            MDTextFieldLeadingIcon(icon="currency-usd"),
            MDTextFieldHintText(text="Precio Normal CLP"),
            mode="outlined",
            size_hint=(0.5, None),
            height=dp(52),
        )
        self.input_price.text = price
        self.input_stock = MDTextField(
            MDTextFieldLeadingIcon(icon="package-variant"),
            MDTextFieldHintText(text="Stock Disponible"),
            mode="outlined",
            size_hint=(0.5, None),
            height=dp(52),
        )
        self.input_stock.text = stock
        row_ps.add_widget(self.input_price)
        row_ps.add_widget(self.input_stock)
        fields_box.add_widget(row_ps)

        # 5. Ingredients Input
        self.input_ingredients = MDTextField(
            MDTextFieldLeadingIcon(icon="food-apple-outline"),
            MDTextFieldHintText(text="Ingredientes y Acompañamientos"),
            mode="outlined",
            size_hint_y=None,
            height=dp(52),
        )
        self.input_ingredients.text = ingredients
        fields_box.add_widget(self.input_ingredients)

        # 6. DEDICATED NEAR-EXPIRY / DISCOUNT SECTION (ZERO CRASH, DIRECT TEXT REFERENCE)
        self._is_offer_active = is_offer
        self.offer_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(175) if self._is_offer_active else dp(68),
            padding=[dp(14), dp(10), dp(14), dp(10)],
            spacing=dp(8),
            style="elevated",
            md_bg_color=[0.99, 0.96, 0.91, 1.0],  # Cálido ámbar
            radius=[dp(14), dp(14), dp(14), dp(14)],
            line_color=[0.85, 0.60, 0.20, 1.0],
            elevation=1,
        )

        self.toggle_offer_text = MDButtonText(
            text="Oferta / Por Vencer: ACTIVA" if self._is_offer_active else "Activar Precio Rebajado por Vencer",
            theme_text_color="Custom",
            text_color=WHITE if self._is_offer_active else UCT_NAVY,
        )
        self.toggle_offer_icon = MDButtonIcon(
            icon="sale" if self._is_offer_active else "tag-outline",
            theme_icon_color="Custom",
            icon_color=WHITE if self._is_offer_active else UCT_NAVY,
        )
        self.toggle_offer_btn = MDButton(
            self.toggle_offer_icon,
            self.toggle_offer_text,
            style="filled" if self._is_offer_active else "tonal",
            theme_bg_color="Custom",
            md_bg_color=VIBRANT_ORANGE if self._is_offer_active else UCT_ICE_BLUE,
            size_hint=(1, None),
            height=dp(38),
            on_release=lambda x: self._toggle_offer_state(),
        )
        self.offer_card.add_widget(self.toggle_offer_btn)

        self.offer_fields_layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(110) if self._is_offer_active else dp(0),
            opacity=1 if self._is_offer_active else 0,
            disabled=not self._is_offer_active,
        )

        self.input_offer_price = MDTextField(
            MDTextFieldLeadingIcon(icon="sale"),
            MDTextFieldHintText(text="Precio Rebajado en Oferta (CLP)"),
            mode="outlined",
            size_hint_y=None,
            height=dp(48),
        )
        self.input_offer_price.text = offer_price

        self.input_offer_label = MDTextField(
            MDTextFieldLeadingIcon(icon="clock-alert-outline"),
            MDTextFieldHintText(text="Motivo (ej: Por vencer hoy - 50% OFF)"),
            mode="outlined",
            size_hint_y=None,
            height=dp(48),
        )
        self.input_offer_label.text = offer_label

        self.offer_fields_layout.add_widget(self.input_offer_price)
        self.offer_fields_layout.add_widget(self.input_offer_label)
        self.offer_card.add_widget(self.offer_fields_layout)
        fields_box.add_widget(self.offer_card)

        # 7. Bottom Action Buttons (Spacious, full width, high contrast)
        save_btn = create_button(
            text="Guardar en Catálogo",
            icon="check",
            style="filled",
            size_hint=(1, None),
            height=dp(44),
            on_release=lambda x: self._save_product(),
        )
        cancel_btn = create_button(
            text="Cancelar y Volver",
            style="outlined",
            size_hint=(1, None),
            height=dp(40),
            on_release=lambda x: self._show_list_view(),
        )
        fields_box.add_widget(save_btn)
        fields_box.add_widget(cancel_btn)

        scroll.add_widget(fields_box)
        main_box.add_widget(scroll)
        self.root_layout.add_widget(main_box)

    def _toggle_offer_state(self):
        """Safe toggle without traversing children, with responsive card height update and high contrast."""
        self._is_offer_active = not self._is_offer_active
        if self._is_offer_active:
            self.toggle_offer_btn.style = "filled"
            self.toggle_offer_btn.md_bg_color = VIBRANT_ORANGE
            self.toggle_offer_text.text = "Oferta / Por Vencer: ACTIVA"
            self.toggle_offer_text.text_color = WHITE
            self.toggle_offer_icon.icon = "sale"
            self.toggle_offer_icon.icon_color = WHITE
            self.offer_fields_layout.opacity = 1
            self.offer_fields_layout.disabled = False
            self.offer_fields_layout.height = dp(110)
            self.offer_card.height = dp(175)
        else:
            self.toggle_offer_btn.style = "tonal"
            self.toggle_offer_btn.md_bg_color = UCT_ICE_BLUE
            self.toggle_offer_text.text = "Activar Precio Rebajado por Vencer"
            self.toggle_offer_text.text_color = UCT_NAVY
            self.toggle_offer_icon.icon = "tag-outline"
            self.toggle_offer_icon.icon_color = UCT_NAVY
            self.offer_fields_layout.opacity = 0
            self.offer_fields_layout.disabled = True
            self.offer_fields_layout.height = dp(0)
            self.offer_card.height = dp(68)

    def _save_product(self):
        pid = self.input_id.text.strip()
        name = self.input_name.text.strip()
        cat = self.input_cat.text.strip() or "Menú Normal"
        try:
            price = int(self.input_price.text.strip())
            stock = int(self.input_stock.text.strip())
        except ValueError:
            self.form_error_lbl.text = "[color=#EF4444]Error: Precio y Stock deben ser números enteros.[/color]"
            return

        if not pid or not name:
            self.form_error_lbl.text = "[color=#EF4444]Error: ID y Nombre son obligatorios.[/color]"
            return

        ingredients = self.input_ingredients.text.strip()

        is_offer = self._is_offer_active
        original_price = 0
        final_price = price
        offer_label = ""

        if is_offer:
            try:
                discounted = int(self.input_offer_price.text.strip())
                if discounted <= 0 or discounted >= price:
                    self.form_error_lbl.text = "[color=#EF4444]El precio rebajado debe ser menor al precio normal.[/color]"
                    return
                original_price = price
                final_price = discounted
                offer_label = self.input_offer_label.text.strip() or "Por vencer hoy"
            except ValueError:
                self.form_error_lbl.text = "[color=#EF4444]Precio de oferta inválido.[/color]"
                return

        prod = Product(
            id_producto=pid,
            name=name,
            price=final_price,
            stock=stock,
            category=cat,
            ingredients=ingredients,
            is_offer=is_offer,
            original_price=original_price,
            offer_label=offer_label,
        )

        if self._editing_product_id:
            self.product_repo.update(prod)
        else:
            self.product_repo.create(prod)

        self._show_list_view()

    # --- Deletion modal confirmation ---

    def _ask_delete_confirmation(self, prod: Product):
        self._hide_confirm_modal()

        self.confirm_modal = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(130),
            padding=[dp(14), dp(12), dp(14), dp(12)],
            spacing=dp(8),
            style="elevated",
            md_bg_color=[1.0, 1.0, 1.0, 1.0],
            radius=[dp(14), dp(14), dp(14), dp(14)],
            line_color=[0.9, 0.2, 0.2, 0.4],
            elevation=3,
        )
        title = MDLabel(
            text="[b][color=#EF4444]Confirmar Eliminación[/color][/b]",
            markup=True,
            font_style="Title",
            role="small",
            size_hint_y=None,
            height=dp(22),
        )
        msg = MDLabel(
            text=f"¿Eliminar '{prod.name}' ({prod.id_producto}) del casino?",
            font_style="Body",
            role="small",
            size_hint_y=None,
            height=dp(24),
        )
        btns = MDBoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(36))
        cancel_btn = create_button(
            text="Cancelar",
            style="tonal",
            size_hint=(0.5, None),
            height=dp(34),
            on_release=lambda x: self._hide_confirm_modal(),
        )
        del_btn = create_button(
            text="Sí, Eliminar",
            icon="delete-outline",
            style="danger",
            size_hint=(0.5, None),
            height=dp(34),
            on_release=lambda x: self._execute_delete(prod.id_producto, prod.name),
        )
        btns.add_widget(cancel_btn)
        btns.add_widget(del_btn)

        self.confirm_modal.add_widget(title)
        self.confirm_modal.add_widget(msg)
        self.confirm_modal.add_widget(btns)
        self.root_layout.add_widget(self.confirm_modal, index=1)

    def _execute_delete(self, pid: str, name: str):
        self._hide_confirm_modal()
        self.product_repo.delete(pid)
        self._show_list_view()

    def _hide_confirm_modal(self):
        if self.confirm_modal and self.confirm_modal in self.root_layout.children:
            self.root_layout.remove_widget(self.confirm_modal)
            self.confirm_modal = None
