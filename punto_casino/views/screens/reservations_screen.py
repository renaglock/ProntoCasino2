"""Reservations screen showing interactive comanda details, QR codes, and cancellation flow."""

from kivy.metrics import dp
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen

from punto_casino.models.order import Order, OrderStatus, ORDER_STATUS_LABELS, ORDER_STATUS_COLORS
from punto_casino.models.user import UserRole
from punto_casino.services.order_service import OrderService
from punto_casino.services.auth_service import AuthService
from punto_casino.utils.formatters import format_currency
from punto_casino.utils.qr_generator import generate_qr_texture
from punto_casino.views.components.ui_elements import create_button


class ReservationsScreen(MDScreen):
    """Customer view displaying pending/confirmed reservations with QR code modal and cancellation."""

    def __init__(self, order_service: OrderService, auth_service: AuthService, on_navigate, **kwargs):
        super().__init__(**kwargs)
        self.order_service = order_service
        self.auth_service = auth_service
        self.on_navigate = on_navigate

        self.root_layout = None
        self.orders_container = None
        self.status_label = None
        self.detail_modal = None
        self.confirm_modal = None

        self._build_ui()

    def _build_ui(self):
        self.root_layout = MDBoxLayout(
            orientation="vertical",
            padding=[dp(16), dp(12), dp(16), dp(12)],
            spacing=dp(8),
            theme_bg_color="Custom",
            md_bg_color=[0.96, 0.97, 0.99, 1.0],
        )

        # 1. Header with Refresh
        header = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(40),
            spacing=dp(10),
        )
        title = MDLabel(
            text="[b][color=#0A3871]Mis Reservas y Comandas UCT[/color][/b]",
            markup=True,
            font_style="Title",
            role="medium",
        )
        refresh_btn = create_button(
            text="Refrescar",
            icon="refresh",
            style="tonal",
            size_hint=(None, None),
            height=dp(34),
            width=dp(110),
            on_release=lambda x: self.refresh_reservations(),
        )
        header.add_widget(title)
        header.add_widget(refresh_btn)
        self.root_layout.add_widget(header)

        # 2. View Description / Status note (Fixed at the top)
        self.status_label = MDLabel(
            text="[color=#64748B]Revisa el estado de tus reservas y el detalle para retiro en casino.[/color]",
            font_style="Body",
            role="small",
            size_hint_y=None,
            height=dp(26),
            markup=True,
            padding=[dp(4), dp(2), dp(4), dp(2)],
        )
        self.root_layout.add_widget(self.status_label)

        # 2. Orders List
        self.scroll = ScrollView(size_hint=(1, 1))
        self.orders_container = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None,
        )
        self.orders_container.bind(minimum_height=self.orders_container.setter("height"))
        self.scroll.add_widget(self.orders_container)
        self.root_layout.add_widget(self.scroll)

        self.add_widget(self.root_layout)

    def on_enter(self):
        """Refresh user reservations when screen is visited."""
        self._hide_modals()
        current_user = self.auth_service.current_user
        is_cashier_or_admin = current_user and current_user.role in (UserRole.CASHIER, UserRole.ADMIN)
        if self.status_label:
            if is_cashier_or_admin:
                self.status_label.text = "[color=#64748B]Auditoría y control de reservas activas e historial de retiros.[/color]"
            else:
                self.status_label.text = "[color=#64748B]Revisa el estado de tus reservas y el detalle para retiro en casino.[/color]"
        self.refresh_reservations()

    def refresh_reservations(self):
        self.orders_container.clear_widgets()
        orders = self.order_service.get_user_orders()

        if not orders:
            empty_card = MDCard(
                orientation="vertical",
                size_hint_y=None,
                height=dp(100),
                padding=[dp(16), dp(14), dp(16), dp(14)],
                spacing=dp(6),
                style="outlined",
                theme_bg_color="Custom",
                md_bg_color=[1.0, 1.0, 1.0, 1],
                radius=[dp(14), dp(14), dp(14), dp(14)],
                line_color=[0.88, 0.92, 0.96, 1],
                elevation=0,
            )
            empty_card.add_widget(
                MDLabel(
                    text="[color=#64748B]No tienes reservas activas en este momento.\nVisita el catálogo para elegir tu menú y reservar sin filas.[/color]",
                    markup=True,
                    halign="center",
                    font_style="Body",
                    role="small",
                )
            )
            self.orders_container.add_widget(empty_card)
            return

        for order in orders:
            status_text = ORDER_STATUS_LABELS.get(order.status, order.status.value)
            status_color = ORDER_STATUS_COLORS.get(order.status, "#475569")

            # CRITICAL FIX: Explicit non-zero height dp(114) prevents OpenGL FBO Incomplete Attachment (36054) crash
            card = MDCard(
                orientation="vertical",
                size_hint_y=None,
                height=dp(114),
                padding=[dp(14), dp(10), dp(14), dp(10)],
                spacing=dp(5),
                style="outlined",
                theme_bg_color="Custom",
                md_bg_color=[1.0, 1.0, 1.0, 1],
                radius=[dp(14), dp(14), dp(14), dp(14)],
                line_color=[0.88, 0.92, 0.96, 1],
                elevation=0,
            )

            # Top Line: Comanda # and Status Label ("Pendiente por pagar")
            top = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(24), spacing=dp(4))
            comanda_lbl = MDLabel(
                text=f"[b][color=#0A3871]Comanda #{order.comanda_number}[/color][/b] [color=#64748B]({order.id_pedido})[/color]",
                markup=True,
                font_style="Title",
                role="small",
                size_hint_x=0.60,
                shorten=True,
                shorten_from="right",
            )
            status_badge = MDLabel(
                text=f"[b][color={status_color}]{status_text}[/color][/b]",
                markup=True,
                halign="right",
                font_style="Label",
                role="medium",
                size_hint_x=0.40,
                shorten=True,
                shorten_from="right",
            )
            top.add_widget(comanda_lbl)
            top.add_widget(status_badge)

            # Middle Line: Dishes summary
            items_str = ", ".join(f"{i.quantity}x {i.name}" for i in order.items)
            details_lbl = MDLabel(
                text=f"[color=#475569]Platos: {items_str}[/color]",
                markup=True,
                font_style="Body",
                role="small",
                shorten=True,
                shorten_from="right",
                size_hint_y=None,
                height=dp(20),
            )

            # Bottom Line: Total & View QR / Detail button with high contrast
            bottom = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(34))
            total_lbl = MDLabel(
                text=f"[b]Total: {format_currency(order.total)}[/b] [color=#64748B]• {order.created_at.strftime('%H:%M')}[/color]",
                markup=True,
                font_style="Label",
                role="medium",
            )
            current_user = self.auth_service.current_user
            is_cashier_or_admin = current_user and current_user.role in (UserRole.CASHIER, UserRole.ADMIN)
            btn_text = "Ver Detalle" if is_cashier_or_admin else "Ver QR y Detalle"
            btn_icon = "clipboard-text-outline" if is_cashier_or_admin else "qrcode-scan"

            qr_btn = create_button(
                text=btn_text,
                icon=btn_icon,
                style="filled",
                size_hint=(None, None),
                height=dp(32),
                on_release=lambda x, o=order: self._show_order_detail_modal(o),
            )
            bottom.add_widget(total_lbl)
            bottom.add_widget(qr_btn)

            card.add_widget(top)
            card.add_widget(details_lbl)
            card.add_widget(bottom)
            self.orders_container.add_widget(card)

    def _show_order_detail_modal(self, order: Order):
        """Display full comanda breakdown, in-memory QR code texture, and cancellation action."""
        self._hide_modals()

        status_text = ORDER_STATUS_LABELS.get(order.status, order.status.value)
        status_color = ORDER_STATUS_COLORS.get(order.status, "#475569")

        current_user = self.auth_service.current_user
        is_cashier_or_admin = current_user and current_user.role in (UserRole.CASHIER, UserRole.ADMIN)
        is_order_active = order.status in (OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.READY)

        # Calculate exact height to ensure zero blank void at the top of the card
        items_count = max(len(order.items), 1)
        items_box_h = min(items_count * dp(22), dp(66))
        if is_cashier_or_admin:
            # 32 (padding) + 26 (header) + 10 + items_box_h + 10 + 22 (total) + 10 + 78 (info_card) + 10 + 38 (actions)
            modal_h = items_box_h + dp(236)
        else:
            # 28 (padding) + 26 (header) + 8 + items_box_h + 8 + 22 (total) + 8 + 190 (qr) + 6 + 26 (instr) + 8 + 38 (actions)
            modal_h = items_box_h + dp(368)

        # Hide background scroll to avoid any visible leaks
        if hasattr(self, "scroll") and self.scroll:
            self.scroll.opacity = 0
            self.scroll.size_hint_y = None
            self.scroll.height = 0
            self.scroll.disabled = True

        self.detail_modal = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=modal_h,
            padding=[dp(18), dp(16), dp(18), dp(16)] if is_cashier_or_admin else [dp(18), dp(14), dp(18), dp(14)],
            spacing=dp(10) if is_cashier_or_admin else dp(8),
            style="outlined",
            theme_bg_color="Custom",
            md_bg_color=[1.0, 1.0, 1.0, 1],
            radius=[dp(18), dp(18), dp(18), dp(18)],
            line_color=[0.04, 0.22, 0.44, 0.4],
            elevation=0,
        )

        # 1. Header: Comanda and Status
        modal_header = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(26))
        m_title = MDLabel(
            text=f"[b][color=#0A3871]Comanda #{order.comanda_number}[/color][/b]",
            markup=True,
            font_style="Title",
            role="medium",
        )
        m_status = MDLabel(
            text=f"[b][color={status_color}]{status_text}[/color][/b]",
            markup=True,
            halign="right",
            font_style="Label",
            role="medium",
        )
        modal_header.add_widget(m_title)
        modal_header.add_widget(m_status)
        self.detail_modal.add_widget(modal_header)

        # 2. Items list breakdown (Anti-overlapping with single-line truncation)
        items_box = MDBoxLayout(orientation="vertical", spacing=dp(2), size_hint_y=None, height=items_box_h)
        for item in order.items:
            row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(20), spacing=dp(4))
            row.add_widget(
                MDLabel(
                    text=f"• {item.quantity}x {item.name}",
                    font_style="Body",
                    role="small",
                    shorten=True,
                    shorten_from="right",
                    size_hint_x=0.72,
                )
            )
            row.add_widget(
                MDLabel(
                    text=format_currency(item.subtotal),
                    halign="right",
                    font_style="Body",
                    role="small",
                    bold=True,
                    size_hint_x=0.28,
                )
            )
            items_box.add_widget(row)
        self.detail_modal.add_widget(items_box)

        # Total amount
        total_line = MDLabel(
            text=f"[b][color=#0A3871]Total a pagar en casino: {format_currency(order.total)}[/color][/b]",
            markup=True,
            font_style="Title",
            role="small",
            size_hint_y=None,
            height=dp(22),
        )
        self.detail_modal.add_widget(total_line)

        # 3. Role-based Body: Info card for Cashier/Admin vs QR Code for Client/Guest
        if is_cashier_or_admin:
            # Client details and comanda audit card for cashier/admin (NO QR code needed)
            info_card = MDCard(
                orientation="vertical",
                size_hint=(1, None),
                height=dp(78),
                padding=[dp(12), dp(8), dp(12), dp(8)],
                spacing=dp(3),
                style="outlined",
                theme_bg_color="Custom",
                md_bg_color=[0.96, 0.98, 1.0, 1.0],
                radius=[dp(10), dp(10), dp(10), dp(10)],
                line_color=[0.80, 0.88, 0.96, 1.0],
                elevation=0,
            )
            info_card.add_widget(
                MDLabel(
                    text=f"[b][color=#0A3871]Cliente:[/color][/b] {order.customer_name} [color=#64748B]({order.customer_role})[/color]",
                    markup=True,
                    font_style="Body",
                    role="small",
                    size_hint_y=None,
                    height=dp(18),
                )
            )
            info_card.add_widget(
                MDLabel(
                    text=f"[b][color=#0A3871]Código Transacción:[/color][/b] [color=#64748B]{order.id_pedido}[/color]",
                    markup=True,
                    font_style="Body",
                    role="small",
                    size_hint_y=None,
                    height=dp(18),
                )
            )
            info_card.add_widget(
                MDLabel(
                    text=f"[b][color=#0A3871]Fecha / Hora:[/color][/b] {order.created_at.strftime('%d/%m/%Y %H:%M')}",
                    markup=True,
                    font_style="Body",
                    role="small",
                    size_hint_y=None,
                    height=dp(18),
                )
            )
            self.detail_modal.add_widget(info_card)
        else:
            # QR Code only for client/guest to present at cashier desk
            qr_payload = order.pickup_qr or order.id_pedido
            try:
                qr_tex = generate_qr_texture(qr_payload)
                qr_card = MDCard(
                    size_hint=(None, None),
                    size=(dp(190), dp(190)),
                    pos_hint={"center_x": 0.5},
                    style="filled",
                    theme_bg_color="Custom",
                    md_bg_color=[1.0, 1.0, 1.0, 1.0],
                    radius=[dp(12), dp(12), dp(12), dp(12)],
                    line_color=[0.04, 0.22, 0.44, 0.2],
                    elevation=0,
                    padding=dp(4),
                )
                qr_widget = Image(
                    texture=qr_tex,
                    size_hint=(1, 1),
                    allow_stretch=True,
                    keep_ratio=True,
                )
                qr_card.add_widget(qr_widget)
                self.detail_modal.add_widget(qr_card)
            except Exception as e:
                err_lbl = MDLabel(
                    text=f"[color=#EF4444]Error generando QR: {e}[/color]",
                    markup=True,
                    halign="center",
                    size_hint_y=None,
                    height=dp(40),
                )
                self.detail_modal.add_widget(err_lbl)

            # Instructions
            instr_lbl = MDLabel(
                text="[color=#64748B]Muestra este código en la caja del casino para retirar y pagar tu pedido sin hacer fila.[/color]",
                markup=True,
                halign="center",
                font_style="Label",
                role="small",
                size_hint_y=None,
                height=dp(26),
            )
            self.detail_modal.add_widget(instr_lbl)

        # 4. Actions: Cancel order (if eligible) & Close with high contrast
        actions_box = MDBoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(38))

        if order.status in (OrderStatus.PENDING, OrderStatus.CONFIRMED):
            cancel_btn = create_button(
                text="Cancelar",
                icon="close",
                icon_size=dp(14),
                style="outlined",
                size_hint=(0.5, None),
                height=dp(36),
                on_release=lambda x, o=order: self._ask_cancel_confirmation(o),
            )
            actions_box.add_widget(cancel_btn)

        close_btn = create_button(
            text="Cerrar",
            style="filled",
            size_hint=(0.5 if order.status in (OrderStatus.PENDING, OrderStatus.CONFIRMED) else 1.0, None),
            height=dp(36),
            on_release=lambda x: self._hide_modals(),
        )
        actions_box.add_widget(close_btn)

        self.detail_modal.add_widget(actions_box)
        self.root_layout.add_widget(self.detail_modal, index=1)

    def _charge_order_as_cashier(self, order: Order):
        """Allow cashier or administrator to mark comanda as paid & delivered directly from detail view."""
        self._hide_modals()
        success = self.order_service.mark_delivered(order.id_pedido)
        if success:
            self.status_label.text = f"[color=#10B981]Comanda #{order.comanda_number} cobrada (${order.total:,} CLP) y entregada con éxito.[/color]"
        else:
            self.status_label.text = f"[color=#EF4444]No se pudo procesar el cobro de la comanda #{order.comanda_number}.[/color]"
        self.refresh_reservations()

    def _ask_cancel_confirmation(self, order: Order):
        """Show confirmation dialog before cancelling an active comanda."""
        self._hide_modals()

        if hasattr(self, "scroll") and self.scroll:
            self.scroll.opacity = 0
            self.scroll.size_hint_y = None
            self.scroll.height = 0
            self.scroll.disabled = True

        self.confirm_modal = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(160),
            padding=[dp(16), dp(14), dp(16), dp(14)],
            spacing=dp(10),
            style="outlined",
            theme_bg_color="Custom",
            md_bg_color=[1.0, 1.0, 1.0, 1],
            radius=[dp(16), dp(16), dp(16), dp(16)],
            line_color=[0.93, 0.27, 0.27, 0.6],
            elevation=0,
        )
        c_title = MDLabel(
            text="[b][color=#DC2626]Confirmar Cancelación de Reserva[/color][/b]",
            markup=True,
            font_style="Title",
            role="small",
            size_hint_y=None,
            height=dp(24),
        )
        c_msg = MDLabel(
            text=f"¿Estás seguro de cancelar la Comanda #{order.comanda_number} ({format_currency(order.total)})? Los platos volverán al inventario del casino.",
            font_style="Body",
            role="small",
            size_hint_y=None,
            height=dp(42),
        )
        c_btns = MDBoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(38))
        btn_back = create_button(
            text="Volver",
            style="tonal",
            size_hint=(0.5, None),
            height=dp(36),
            on_release=lambda x: self._show_order_detail_modal(order),
        )
        btn_confirm = create_button(
            text="Sí, Cancelar",
            icon="check",
            icon_size=dp(14),
            style="danger",
            size_hint=(0.5, None),
            height=dp(36),
            on_release=lambda x, o=order: self._execute_cancellation(o),
        )
        c_btns.add_widget(btn_back)
        c_btns.add_widget(btn_confirm)

        self.confirm_modal.add_widget(c_title)
        self.confirm_modal.add_widget(c_msg)
        self.confirm_modal.add_widget(c_btns)

        self.root_layout.add_widget(self.confirm_modal, index=1)

    def _execute_cancellation(self, order: Order):
        """Execute order cancellation in order service and update view."""
        self._hide_modals()
        success = self.order_service.cancel_order(order.id_pedido)
        if success:
            self.status_label.text = f"[color=#10B981]Comanda #{order.comanda_number} cancelada exitosamente.[/color]"
        else:
            self.status_label.text = f"[color=#EF4444]No se pudo cancelar la comanda.[/color]"
        self.refresh_reservations()

    def _hide_modals(self):
        """Cleanly remove dynamic modal cards and restore scrollable list."""
        if hasattr(self, "scroll") and self.scroll:
            self.scroll.opacity = 1
            self.scroll.size_hint_y = 1
            self.scroll.disabled = False
        if self.detail_modal and self.detail_modal in self.root_layout.children:
            self.root_layout.remove_widget(self.detail_modal)
            self.detail_modal = None
        if self.confirm_modal and self.confirm_modal in self.root_layout.children:
            self.root_layout.remove_widget(self.confirm_modal)
            self.confirm_modal = None
