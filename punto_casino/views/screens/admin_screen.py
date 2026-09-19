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

from punto_casino.models.order import Order, OrderStatus, ORDER_STATUS_LABELS, ORDER_STATUS_COLORS
from punto_casino.models.product import Product
from punto_casino.repositories.product_repository import InMemoryProductRepository
from punto_casino.services.order_service import OrderService
from punto_casino.utils.formatters import format_currency
from punto_casino.views.components.ui_elements import (
    create_button,
    create_offer_badge,
    LIGHT_GREEN,
    SOFT_MINT,
    UCT_ICE_BLUE,
    UCT_NAVY,
    UCT_LIGHT_BLUE,
    EMERALD_GREEN,
    CRIMSON_RED,
    WHITE,
)


class AdminScreen(MDScreen):
    """Admin dashboard with dish management, offers, visual accounting analytics, and robust order history."""

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

        self.current_tab = "crud"  # "crud" (platos) or "history"
        self._editing_product_id: Optional[str] = None
        self._is_offer_active = False

        self.root_layout = None
        self.status_label = None
        self.confirm_modal = None
        self.category_modal = None
        self.audit_modal = None

        # Order history audit & filter state
        self.history_filter = "ALL"  # "ALL", "DELIVERED", "ACTIVE", "CANCELLED"
        self.history_search = ""

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
            text="Nuevo Plato",
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

        # Tab Switcher: [Platos] vs [Historial y Ventas]
        tabs_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(36),
            spacing=dp(8),
        )
        self.btn_tab_crud = create_button(
            text="Platos",
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
            "Catálogo de platos activo. Pulsa '+ Nuevo Plato' o 'Editar / Oferta' para gestionar."
            if self.current_tab == "crud"
            else "Historial contable, auditoría de comandas y métricas financieras."
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

    # =========================================================================
    # 2. HERRAMIENTAS GRÁFICAS DE CONTABILIDAD E HISTORIAL DE AUDITORÍA
    # =========================================================================

    def _render_history_items(self):
        """Render executive accounting tools, visual charts, and filtered order history."""
        self.content_container.clear_widgets()

        if not self.order_service:
            empty_lbl = MDLabel(
                text="[color=#64748B]Servicio de órdenes no inicializado.[/color]",
                markup=True,
                halign="center",
                size_hint_y=None,
                height=dp(40),
            )
            self.content_container.add_widget(empty_lbl)
            return

        report = self.order_service.get_accounting_report()
        all_orders = self.order_service.order_repo.get_all()

        # 1. Herramienta Gráfica: Resumen Ejecutivo de Contabilidad
        self.content_container.add_widget(self._build_kpi_summary_card(report))

        # 2. Herramienta Gráfica: Distribución de Ingresos por Categoría
        self.content_container.add_widget(self._build_category_distribution_card(report))

        # 3. Herramienta Gráfica: Balance Operativo de Pedidos
        self.content_container.add_widget(self._build_operational_balance_card(report))

        # 4. Herramienta Gráfica: Ranking de Platos Más Vendidos
        self.content_container.add_widget(self._build_top_dishes_card(report))

        # 5. Sección de Historial Robusto con Filtros y Buscador Reactivo
        self._build_order_history_section(all_orders)

    def _build_kpi_summary_card(self, report: dict) -> MDCard:
        card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(142),
            padding=[dp(14), dp(10), dp(14), dp(10)],
            spacing=dp(6),
            style="elevated",
            md_bg_color=[0.96, 0.98, 1.0, 1.0],
            radius=[dp(12), dp(12), dp(12), dp(12)],
            line_color=[0.02, 0.53, 0.82, 0.3],
            elevation=2,
        )

        title_box = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(22))
        title_lbl = MDLabel(
            text="[b][color=#0A3871]Resumen Contable del Casino[/color][/b]",
            markup=True,
            font_style="Title",
            role="small",
        )
        delivered_lbl = MDLabel(
            text=f"[color=#10B981][b]{report['delivered_count']} cobrados[/b][/color]",
            markup=True,
            halign="right",
            font_style="Label",
            role="medium",
        )
        title_box.add_widget(title_lbl)
        title_box.add_widget(delivered_lbl)
        card.add_widget(title_box)

        # Big Total Collected
        tot_box = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(34), spacing=dp(8))
        total_lbl = MDLabel(
            text=f"[b][color=#10B981]{format_currency(report['total_collected'])}[/color][/b]",
            markup=True,
            font_style="Headline",
            role="small",
            size_hint_x=0.6,
        )
        tot_sub = MDLabel(
            text="[color=#64748B]Recaudación Neta\nen Turno Activo[/color]",
            markup=True,
            halign="right",
            font_style="Body",
            role="small",
            size_hint_x=0.4,
        )
        tot_box.add_widget(total_lbl)
        tot_box.add_widget(tot_sub)
        card.add_widget(tot_box)

        # 3 KPI Stats Row
        kpi_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(48), spacing=dp(6))
        p1 = self._build_mini_kpi_pill("Ticket Prom.", format_currency(report["average_ticket"]), "#0288D1")
        p2 = self._build_mini_kpi_pill("Efectividad", f"{report['delivery_rate']}%", "#10B981")
        p3 = self._build_mini_kpi_pill("Despachados", f"{report['total_items_sold']} un.", "#0A3871")

        kpi_row.add_widget(p1)
        kpi_row.add_widget(p2)
        kpi_row.add_widget(p3)
        card.add_widget(kpi_row)

        return card

    def _build_mini_kpi_pill(self, label: str, val: str, color_hex: str) -> MDCard:
        pill = MDCard(
            orientation="vertical",
            size_hint=(0.333, 1),
            padding=[dp(6), dp(4), dp(6), dp(4)],
            spacing=dp(1),
            style="filled",
            theme_bg_color="Custom",
            md_bg_color=[1.0, 1.0, 1.0, 0.9],
            radius=[dp(8), dp(8), dp(8), dp(8)],
            line_color=[0.85, 0.90, 0.95, 1.0],
        )
        lbl1 = MDLabel(
            text=f"[color=#64748B]{label}[/color]",
            markup=True,
            halign="center",
            font_style="Label",
            role="small",
            size_hint_y=0.4,
        )
        lbl2 = MDLabel(
            text=f"[b][color={color_hex}]{val}[/color][/b]",
            markup=True,
            halign="center",
            font_style="Title",
            role="small",
            size_hint_y=0.6,
        )
        pill.add_widget(lbl1)
        pill.add_widget(lbl2)
        return pill

    def _build_category_distribution_card(self, report: dict) -> MDCard:
        categories = report.get("category_sales", [])
        card_h = dp(70) + max(len(categories), 1) * dp(38)

        card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=card_h,
            padding=[dp(14), dp(10), dp(14), dp(10)],
            spacing=dp(6),
            style="elevated",
            md_bg_color=[1.0, 1.0, 1.0, 1.0],
            radius=[dp(12), dp(12), dp(12), dp(12)],
            line_color=[0.88, 0.92, 0.96, 1.0],
            elevation=1,
        )

        head_box = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(22))
        head_title = MDLabel(
            text="[b][color=#0A3871]Distribución de Ventas por Categoría[/color][/b]",
            markup=True,
            font_style="Title",
            role="small",
        )
        head_box.add_widget(head_title)
        card.add_widget(head_box)

        cat_colors = {
            "Menú Normal": [0.04, 0.22, 0.44, 1.0],       # Azul UCT
            "Menú Ejecutivo": [0.01, 0.53, 0.82, 1.0],    # Celeste UCT
            "Menú Hipocalórico": [0.18, 0.76, 0.42, 1.0], # Verde Claro
            "Menú Vegetariano": [0.06, 0.65, 0.45, 1.0],  # Verde Esmeralda
            "Comidas Rápidas": [0.85, 0.47, 0.02, 1.0],   # Ámbar
            "Bebidas": [0.05, 0.58, 0.53, 1.0],           # Teal
            "Postres y Snacks": [0.60, 0.25, 0.70, 1.0],  # Morado
        }

        if not categories:
            empty_msg = MDLabel(
                text="[color=#64748B]Aún no hay comandas cobradas para clasificar ventas.[/color]",
                markup=True,
                font_style="Body",
                role="small",
                size_hint_y=None,
                height=dp(26),
            )
            card.add_widget(empty_msg)
            return card

        for cat in categories:
            c_name = cat["category"]
            c_color = cat_colors.get(c_name, [0.39, 0.45, 0.55, 1.0])
            c_rev = format_currency(cat["revenue"])
            c_pct = cat["percentage"]

            row_box = MDBoxLayout(orientation="vertical", size_hint_y=None, height=dp(32), spacing=dp(3))
            
            label_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(18))
            cat_name_lbl = MDLabel(
                text=f"[b][color=#0A3871]{c_name}[/color][/b] [color=#64748B]({cat['quantity']} un.)[/color]",
                markup=True,
                font_style="Body",
                role="small",
                size_hint_x=0.6,
                shorten=True,
                shorten_from="right",
            )
            cat_val_lbl = MDLabel(
                text=f"[b]{c_rev}[/b] [color=#64748B]({c_pct}%)[/color]",
                markup=True,
                halign="right",
                font_style="Body",
                role="small",
                size_hint_x=0.4,
            )
            label_row.add_widget(cat_name_lbl)
            label_row.add_widget(cat_val_lbl)

            # Proportional bar
            track = MDCard(
                size_hint=(1, None),
                height=dp(8),
                style="filled",
                theme_bg_color="Custom",
                md_bg_color=[0.92, 0.95, 0.98, 1.0],
                radius=[dp(4), dp(4), dp(4), dp(4)],
                elevation=0,
            )
            ratio = max(min(c_pct / 100.0, 1.0), 0.04)
            fill_bar = MDCard(
                size_hint=(ratio, 1),
                style="filled",
                theme_bg_color="Custom",
                md_bg_color=c_color,
                radius=[dp(4), dp(4), dp(4), dp(4)],
                elevation=0,
            )
            track.add_widget(fill_bar)

            row_box.add_widget(label_row)
            row_box.add_widget(track)
            card.add_widget(row_box)

        return card

    def _build_operational_balance_card(self, report: dict) -> MDCard:
        card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(108),
            padding=[dp(14), dp(10), dp(14), dp(10)],
            spacing=dp(6),
            style="elevated",
            md_bg_color=[1.0, 1.0, 1.0, 1.0],
            radius=[dp(12), dp(12), dp(12), dp(12)],
            line_color=[0.88, 0.92, 0.96, 1.0],
            elevation=1,
        )

        title = MDLabel(
            text="[b][color=#0A3871]Balance Operativo de Comandas[/color][/b]",
            markup=True,
            font_style="Title",
            role="small",
            size_hint_y=None,
            height=dp(20),
        )
        card.add_widget(title)

        total_orders = max(report["total_orders"], 1)
        del_count = report["delivered_count"]
        pen_count = report["pending_count"]
        can_count = report["cancelled_count"]

        del_pct = round(del_count / total_orders * 100, 1)
        pen_pct = round(pen_count / total_orders * 100, 1)
        can_pct = round(can_count / total_orders * 100, 1)

        # Segmented Multi-state Bar
        bar_box = MDBoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=dp(10),
            spacing=dp(2),
        )
        if del_count > 0:
            bar_box.add_widget(
                MDCard(
                    size_hint=(del_pct / 100.0, 1),
                    style="filled",
                    theme_bg_color="Custom",
                    md_bg_color=[0.06, 0.65, 0.45, 1.0],  # Verde
                    radius=[dp(4), dp(4), dp(4), dp(4)],
                    elevation=0,
                )
            )
        if pen_count > 0:
            bar_box.add_widget(
                MDCard(
                    size_hint=(pen_pct / 100.0, 1),
                    style="filled",
                    theme_bg_color="Custom",
                    md_bg_color=[0.85, 0.47, 0.02, 1.0],  # Ámbar
                    radius=[dp(4), dp(4), dp(4), dp(4)],
                    elevation=0,
                )
            )
        if can_count > 0:
            bar_box.add_widget(
                MDCard(
                    size_hint=(can_pct / 100.0, 1),
                    style="filled",
                    theme_bg_color="Custom",
                    md_bg_color=[0.86, 0.15, 0.15, 1.0],  # Rojo
                    radius=[dp(4), dp(4), dp(4), dp(4)],
                    elevation=0,
                )
            )
        card.add_widget(bar_box)

        # Legend Row
        legend_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(26))
        lbl_ent = MDLabel(
            text=f"[color=#10B981]● Entregadas ({del_count})[/color]",
            markup=True,
            font_style="Label",
            role="small",
            size_hint_x=0.38,
        )
        lbl_pen = MDLabel(
            text=f"[color=#D97706]● En Cocina ({pen_count})[/color]",
            markup=True,
            halign="center",
            font_style="Label",
            role="small",
            size_hint_x=0.34,
        )
        lbl_can = MDLabel(
            text=f"[color=#EF4444]● Canceladas ({can_count})[/color]",
            markup=True,
            halign="right",
            font_style="Label",
            role="small",
            size_hint_x=0.28,
        )
        legend_row.add_widget(lbl_ent)
        legend_row.add_widget(lbl_pen)
        legend_row.add_widget(lbl_can)
        card.add_widget(legend_row)

        return card

    def _build_top_dishes_card(self, report: dict) -> MDCard:
        dishes = report.get("top_dishes", [])
        card_h = dp(64) + max(len(dishes), 1) * dp(38)

        card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=card_h,
            padding=[dp(14), dp(10), dp(14), dp(10)],
            spacing=dp(6),
            style="elevated",
            md_bg_color=[1.0, 1.0, 1.0, 1.0],
            radius=[dp(12), dp(12), dp(12), dp(12)],
            line_color=[0.88, 0.92, 0.96, 1.0],
            elevation=1,
        )

        title = MDLabel(
            text="[b][color=#0A3871]Top Platos Más Vendidos[/color][/b]",
            markup=True,
            font_style="Title",
            role="small",
            size_hint_y=None,
            height=dp(20),
        )
        card.add_widget(title)

        if not dishes:
            msg = MDLabel(
                text="[color=#64748B]Sin ventas registradas en este turno.[/color]",
                markup=True,
                font_style="Body",
                role="small",
                size_hint_y=None,
                height=dp(26),
            )
            card.add_widget(msg)
            return card

        badges = ["#1", "#2", "#3", "#4", "#5"]
        badge_colors = ["#D97706", "#64748B", "#B45309", "#94A3B8", "#94A3B8"]

        for idx, dish in enumerate(dishes[:4]):
            b_text = badges[idx] if idx < len(badges) else f"#{idx+1}"
            b_color = badge_colors[idx] if idx < len(badge_colors) else "#94A3B8"

            item_box = MDBoxLayout(orientation="vertical", size_hint_y=None, height=dp(32), spacing=dp(3))
            
            line1 = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(18))
            d_name = MDLabel(
                text=f"[b][color={b_color}][{b_text}][/color][/b] [color=#1E293B]{dish['name']}[/color]",
                markup=True,
                font_style="Body",
                role="small",
                size_hint_x=0.62,
                shorten=True,
                shorten_from="right",
            )
            d_stats = MDLabel(
                text=f"[b]{dish['quantity']} un.[/b] • [color=#10B981]{format_currency(dish['revenue'])}[/color]",
                markup=True,
                halign="right",
                font_style="Body",
                role="small",
                size_hint_x=0.38,
            )
            line1.add_widget(d_name)
            line1.add_widget(d_stats)

            # Intensity bar
            track = MDCard(
                size_hint=(1, None),
                height=dp(6),
                style="filled",
                theme_bg_color="Custom",
                md_bg_color=[0.92, 0.95, 0.98, 1.0],
                radius=[dp(3), dp(3), dp(3), dp(3)],
                elevation=0,
            )
            rel_ratio = max(min(dish.get("relative_pct", 50.0) / 100.0, 1.0), 0.05)
            intensity_bar = MDCard(
                size_hint=(rel_ratio, 1),
                style="filled",
                theme_bg_color="Custom",
                md_bg_color=[0.01, 0.53, 0.82, 0.85],
                radius=[dp(3), dp(3), dp(3), dp(3)],
                elevation=0,
            )
            track.add_widget(intensity_bar)

            item_box.add_widget(line1)
            item_box.add_widget(track)
            card.add_widget(item_box)

        return card

    def _build_order_history_section(self, all_orders: list):
        sec_title = MDLabel(
            text=f"[b][color=#0A3871]Auditoría Histórica de Pedidos ({len(all_orders)})[/color][/b]",
            markup=True,
            font_style="Title",
            role="medium",
            size_hint_y=None,
            height=dp(28),
        )
        self.content_container.add_widget(sec_title)

        # Search Bar
        search_field = MDTextField(
            MDTextFieldLeadingIcon(icon="magnify"),
            MDTextFieldHintText(text="Buscar comanda, cliente o plato..."),
            mode="outlined",
            size_hint_y=None,
            height=dp(44),
        )
        search_field.text = self.history_search
        search_field.bind(text=self._on_search_text_changed)
        self.content_container.add_widget(search_field)

        # Filter Chips Row
        del_count = sum(1 for o in all_orders if o.status == OrderStatus.DELIVERED)
        act_count = sum(1 for o in all_orders if o.status in (OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.READY))
        can_count = sum(1 for o in all_orders if o.status in (OrderStatus.CANCELLED, OrderStatus.REJECTED))

        chips_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(34),
            spacing=dp(6),
        )

        self.chip_all = create_button(
            text=f"Todos ({len(all_orders)})",
            style="filled" if self.history_filter == "ALL" else "tonal",
            size_hint=(0.28, None),
            height=dp(32),
            on_release=lambda x: self._set_history_filter("ALL"),
        )
        self.chip_del = create_button(
            text=f"Entregados ({del_count})",
            style="filled" if self.history_filter == "DELIVERED" else "tonal",
            size_hint=(0.28, None),
            height=dp(32),
            on_release=lambda x: self._set_history_filter("DELIVERED"),
        )
        self.chip_act = create_button(
            text=f"Cocina ({act_count})",
            style="filled" if self.history_filter == "ACTIVE" else "tonal",
            size_hint=(0.22, None),
            height=dp(32),
            on_release=lambda x: self._set_history_filter("ACTIVE"),
        )
        self.chip_can = create_button(
            text=f"Canc. ({can_count})",
            style="filled" if self.history_filter == "CANCELLED" else "tonal",
            size_hint=(0.22, None),
            height=dp(32),
            on_release=lambda x: self._set_history_filter("CANCELLED"),
        )

        chips_row.add_widget(self.chip_all)
        chips_row.add_widget(self.chip_del)
        chips_row.add_widget(self.chip_act)
        chips_row.add_widget(self.chip_can)
        self.content_container.add_widget(chips_row)

        # Dedicated orders container
        self.orders_list_box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
        )
        self.orders_list_box.bind(minimum_height=self.orders_list_box.setter("height"))
        self.content_container.add_widget(self.orders_list_box)

        self._update_orders_list(all_orders)

    def _set_history_filter(self, filter_name: str):
        self.history_filter = filter_name
        all_orders = self.order_service.order_repo.get_all()
        # Update chip styles
        if hasattr(self, "chip_all") and self.chip_all:
            self.chip_all.style = "filled" if filter_name == "ALL" else "tonal"
            self.chip_del.style = "filled" if filter_name == "DELIVERED" else "tonal"
            self.chip_act.style = "filled" if filter_name == "ACTIVE" else "tonal"
            self.chip_can.style = "filled" if filter_name == "CANCELLED" else "tonal"
        self._update_orders_list(all_orders)

    def _on_search_text_changed(self, instance, text: str):
        self.history_search = text
        if self.order_service:
            all_orders = self.order_service.order_repo.get_all()
            self._update_orders_list(all_orders)

    def _update_orders_list(self, all_orders: list):
        if not hasattr(self, "orders_list_box") or not self.orders_list_box:
            return

        self.orders_list_box.clear_widgets()

        filtered = []
        q = self.history_search.lower().strip()
        for o in all_orders:
            if self.history_filter == "DELIVERED" and o.status != OrderStatus.DELIVERED:
                continue
            if self.history_filter == "ACTIVE" and o.status not in (OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.READY):
                continue
            if self.history_filter == "CANCELLED" and o.status not in (OrderStatus.CANCELLED, OrderStatus.REJECTED):
                continue

            if q:
                c_match = str(o.comanda_number).lower()
                id_match = o.id_pedido.lower()
                name_match = o.customer_name.lower()
                dish_match = any(q in i.name.lower() for i in o.items)
                if q not in c_match and q not in id_match and q not in name_match and not dish_match:
                    continue

            filtered.append(o)

        if not filtered:
            empty_card = MDCard(
                size_hint_y=None,
                height=dp(52),
                padding=dp(10),
                style="outlined",
            )
            empty_card.add_widget(
                MDLabel(
                    text="[color=#64748B]No se encontraron comandas con los filtros aplicados.[/color]",
                    markup=True,
                    halign="center",
                    font_style="Body",
                    role="small",
                )
            )
            self.orders_list_box.add_widget(empty_card)
            return

        for order in filtered:
            st_text = ORDER_STATUS_LABELS.get(order.status, order.status.value)
            st_color = ORDER_STATUS_COLORS.get(order.status, "#64748B")

            o_card = MDCard(
                orientation="vertical",
                size_hint_y=None,
                height=dp(114),
                padding=[dp(12), dp(8), dp(12), dp(8)],
                spacing=dp(3),
                style="elevated",
                md_bg_color=[1.0, 1.0, 1.0, 1.0],
                radius=[dp(10), dp(10), dp(10), dp(10)],
                line_color=[0.88, 0.92, 0.96, 1.0],
                elevation=1,
            )

            o_row1 = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(20))
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
                    text=f"[b][color=#0288D1]{format_currency(order.total)}[/color][/b]",
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

            audit_btn = create_button(
                text="Auditoría y Detalle",
                icon="receipt-text-outline",
                style="tonal",
                size_hint=(1, None),
                height=dp(28),
                on_release=lambda x, o=order: self._show_comanda_audit_modal(o),
            )

            o_card.add_widget(o_row1)
            o_card.add_widget(o_row2)
            o_card.add_widget(o_row3)
            o_card.add_widget(audit_btn)
            self.orders_list_box.add_widget(o_card)

    def _show_comanda_audit_modal(self, order: Order):
        """Display detailed accounting and audit modal for a specific comanda."""
        self._hide_modals()

        st_text = ORDER_STATUS_LABELS.get(order.status, order.status.value)
        st_color = ORDER_STATUS_COLORS.get(order.status, "#64748B")
        is_active = order.status in (OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.READY)

        items_count = max(len(order.items), 1)
        items_box_h = min(items_count * dp(24), dp(84))
        modal_h = dp(410) if is_active else dp(370)

        self.audit_modal = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=modal_h,
            padding=[dp(16), dp(12), dp(16), dp(12)],
            spacing=dp(8),
            style="elevated",
            md_bg_color=[1.0, 1.0, 1.0, 1.0],
            radius=[dp(16), dp(16), dp(16), dp(16)],
            line_color=[0.04, 0.22, 0.44, 0.4],
            elevation=4,
        )

        # Header
        h_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(26))
        h_title = MDLabel(
            text=f"[b][color=#0A3871]Auditoría Comanda #{order.comanda_number}[/color][/b]",
            markup=True,
            font_style="Title",
            role="small",
        )
        h_status = MDLabel(
            text=f"[color={st_color}][b]{st_text}[/b][/color]",
            markup=True,
            halign="right",
            font_style="Label",
            role="medium",
        )
        h_row.add_widget(h_title)
        h_row.add_widget(h_status)
        self.audit_modal.add_widget(h_row)

        # Metadata Card
        meta_card = MDCard(
            orientation="vertical",
            size_hint=(1, None),
            height=dp(56),
            padding=[dp(8), dp(4), dp(8), dp(4)],
            spacing=dp(2),
            style="filled",
            theme_bg_color="Custom",
            md_bg_color=[0.95, 0.97, 1.0, 1.0],
            radius=[dp(8), dp(8), dp(8), dp(8)],
        )
        m1 = MDLabel(
            text=f"[color=#0A3871][b]ID Transacción:[/b][/color] [color=#64748B]{order.id_pedido}[/color]  |  [color=#0A3871][b]Hora:[/b][/color] [color=#64748B]{order.created_at.strftime('%H:%M')}[/color]",
            markup=True,
            font_style="Body",
            role="small",
        )
        m2 = MDLabel(
            text=f"[color=#0A3871][b]Cliente:[/b][/color] [color=#1E293B]{order.customer_name}[/color] [color=#64748B]({order.customer_role})[/color]",
            markup=True,
            font_style="Body",
            role="small",
        )
        meta_card.add_widget(m1)
        meta_card.add_widget(m2)
        self.audit_modal.add_widget(meta_card)

        # Items breakdown
        items_scroll = ScrollView(size_hint=(1, None), height=items_box_h)
        items_box = MDBoxLayout(orientation="vertical", spacing=dp(2), size_hint_y=None)
        items_box.bind(minimum_height=items_box.setter("height"))

        for item in order.items:
            i_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(22))
            i_name = MDLabel(
                text=f"• {item.quantity}x {item.name}",
                font_style="Body",
                role="small",
                size_hint_x=0.68,
                shorten=True,
                shorten_from="right",
            )
            i_sub = MDLabel(
                text=f"{format_currency(item.subtotal)}",
                font_style="Body",
                role="small",
                bold=True,
                halign="right",
                size_hint_x=0.32,
            )
            i_row.add_widget(i_name)
            i_row.add_widget(i_sub)
            items_box.add_widget(i_row)

        items_scroll.add_widget(items_box)
        self.audit_modal.add_widget(items_scroll)

        # Accounting Total
        tot_row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(26))
        tot_lbl = MDLabel(
            text=f"[b][color=#0A3871]Total Liquidación: {format_currency(order.total)}[/color][/b]",
            markup=True,
            font_style="Title",
            role="small",
        )
        tot_row.add_widget(tot_lbl)
        self.audit_modal.add_widget(tot_row)

        # Status note
        if order.status == OrderStatus.DELIVERED:
            note_text = "[color=#10B981]✓ Pedido cobrado y entregado en mesón.[/color]"
        elif order.status in (OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.READY):
            note_text = "[color=#D97706]⚠ Comanda activa en cocina pendiente de entrega.[/color]"
        else:
            note_text = "[color=#EF4444]✕ Comanda cancelada / fondos devueltos.[/color]"

        note_lbl = MDLabel(
            text=note_text,
            markup=True,
            font_style="Label",
            role="small",
            size_hint_y=None,
            height=dp(20),
        )
        self.audit_modal.add_widget(note_lbl)

        # Actions
        actions_box = MDBoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(36))
        if is_active:
            charge_btn = create_button(
                text="Cobrar en Caja",
                icon="cash-register",
                style="offer",
                size_hint=(0.55, None),
                height=dp(34),
                on_release=lambda x, o=order: self._charge_order_from_audit(o),
            )
            actions_box.add_widget(charge_btn)

        close_btn = create_button(
            text="Cerrar",
            style="outlined",
            size_hint=(0.45 if is_active else 1.0, None),
            height=dp(34),
            on_release=lambda x: self._hide_modals(),
        )
        actions_box.add_widget(close_btn)
        self.audit_modal.add_widget(actions_box)

        self.root_layout.add_widget(self.audit_modal, index=1)

    def _charge_order_from_audit(self, order: Order):
        self._hide_modals()
        success = self.order_service.mark_delivered(order.id_pedido)
        if success:
            self.status_label.text = f"[color=#10B981]Comanda #{order.comanda_number} cobrada y liquidada con éxito.[/color]"
        else:
            self.status_label.text = f"[color=#EF4444]Error liquidando comanda #{order.comanda_number}.[/color]"
        self._render_history_items()

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
            offer_label="30% OFF - Oferta Especial",
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
            offer_label=prod.offer_label or "Oferta Especial / Descuento",
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

        # 3. Category Selector (Select de categorías disponibles según el menú)
        cat_box = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(52),
        )
        self.input_cat = MDTextField(
            MDTextFieldLeadingIcon(icon="tag-outline"),
            MDTextFieldHintText(text="Categoría del Menú"),
            mode="outlined",
            size_hint=(0.68, None),
            height=dp(52),
            readonly=True,
        )
        self.input_cat.text = cat or "Menú Normal"
        cat_btn = create_button(
            text="Elegir",
            icon="menu-down",
            style="tonal",
            size_hint=(0.32, None),
            height=dp(48),
            on_release=lambda x: self._show_category_picker(),
        )
        cat_box.add_widget(self.input_cat)
        cat_box.add_widget(cat_btn)
        fields_box.add_widget(cat_box)

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

        # 6. DEDICATED OFFER / SPECIAL DISCOUNT SECTION
        self._is_offer_active = is_offer
        self.offer_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(175) if self._is_offer_active else dp(68),
            padding=[dp(14), dp(10), dp(14), dp(10)],
            spacing=dp(8),
            style="elevated",
            md_bg_color=SOFT_MINT,  # Fondo menta / verde claro
            radius=[dp(14), dp(14), dp(14), dp(14)],
            line_color=[0.40, 0.80, 0.50, 1.0],
            elevation=1,
        )

        self.toggle_offer_text = MDButtonText(
            text="Oferta / Descuento: ACTIVA" if self._is_offer_active else "Activar Oferta / Descuento Especial",
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
            md_bg_color=LIGHT_GREEN if self._is_offer_active else UCT_ICE_BLUE,
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
            MDTextFieldLeadingIcon(icon="tag-outline"),
            MDTextFieldHintText(text="Motivo (ej: Promo 2x1, Menú del día, 30% OFF, Por vencer)"),
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
            self.toggle_offer_btn.md_bg_color = LIGHT_GREEN
            self.toggle_offer_text.text = "Oferta / Descuento: ACTIVA"
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
            self.toggle_offer_text.text = "Activar Oferta / Descuento Especial"
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
                offer_label = self.input_offer_label.text.strip() or "Oferta Especial"
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

    # --- Category Selector Modal (Available Menu Categories) ---

    def _show_category_picker(self):
        """Display interactive select modal with available menu categories."""
        self._hide_modals()

        self.category_modal = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(380),
            padding=[dp(16), dp(12), dp(16), dp(12)],
            spacing=dp(6),
            style="elevated",
            md_bg_color=[1.0, 1.0, 1.0, 1.0],
            radius=[dp(16), dp(16), dp(16), dp(16)],
            line_color=[0.04, 0.22, 0.44, 0.4],
            elevation=4,
        )
        c_title = MDLabel(
            text="[b][color=#0A3871]Seleccionar Categoría del Menú[/color][/b]",
            markup=True,
            font_style="Title",
            role="small",
            size_hint_y=None,
            height=dp(26),
        )
        self.category_modal.add_widget(c_title)

        categories = [
            ("Menú Normal", "silverware"),
            ("Menú Ejecutivo", "star"),
            ("Menú Hipocalórico", "leaf"),
            ("Menú Vegetariano", "sprout"),
            ("Comidas Rápidas", "hamburger"),
            ("Bebidas", "cup"),
            ("Postres y Snacks", "cake-variant"),
        ]

        scroll_cats = ScrollView(size_hint=(1, 1))
        cats_list = MDBoxLayout(
            orientation="vertical",
            spacing=dp(6),
            size_hint_y=None,
        )
        cats_list.bind(minimum_height=cats_list.setter("height"))

        current_val = self.input_cat.text.strip() if self.input_cat else ""
        for cat_name, cat_icon in categories:
            is_selected = (current_val == cat_name)
            btn = create_button(
                text=cat_name,
                icon=cat_icon,
                style="filled" if is_selected else "tonal",
                size_hint=(1, None),
                height=dp(36),
                on_release=lambda x, c=cat_name: self._select_category(c),
            )
            cats_list.add_widget(btn)

        scroll_cats.add_widget(cats_list)
        self.category_modal.add_widget(scroll_cats)

        cancel_btn = create_button(
            text="Cerrar",
            style="outlined",
            size_hint=(1, None),
            height=dp(34),
            on_release=lambda x: self._hide_modals(),
        )
        self.category_modal.add_widget(cancel_btn)

        self.root_layout.add_widget(self.category_modal, index=1)

    def _select_category(self, cat_name: str):
        if self.input_cat:
            self.input_cat.text = cat_name
        self._hide_modals()

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
        self._hide_modals()

    def _hide_modals(self):
        if hasattr(self, "category_modal") and self.category_modal and self.category_modal in self.root_layout.children:
            self.root_layout.remove_widget(self.category_modal)
            self.category_modal = None
        if self.confirm_modal and self.confirm_modal in self.root_layout.children:
            self.root_layout.remove_widget(self.confirm_modal)
            self.confirm_modal = None
        if hasattr(self, "audit_modal") and self.audit_modal and self.audit_modal in self.root_layout.children:
            self.root_layout.remove_widget(self.audit_modal)
            self.audit_modal = None

