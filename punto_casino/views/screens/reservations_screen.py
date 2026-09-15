"""Reservations screen showing interactive comanda details, QR codes, and cancellation flow."""

from kivy.metrics import dp
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen

from punto_casino.models.order import Order, OrderStatus, ORDER_STATUS_LABELS, ORDER_STATUS_COLORS
from punto_casino.services.order_service import OrderService
from punto_casino.services.auth_service import AuthService
from punto_casino.utils.formatters import format_currency
from punto_casino.utils.qr_generator import generate_qr_texture


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
        refresh_btn = MDButton(
            MDButtonText(text="Refrescar"),
            style="tonal",
            size_hint_y=None,
            height=dp(34),
            on_release=lambda x: self.refresh_reservations(),
        )
        header.add_widget(title)
        header.add_widget(refresh_btn)
        self.root_layout.add_widget(header)

        # Status note
        self.status_label = MDLabel(
            text="Toca cualquier reserva para ver el código QR y el detalle de entrega.",
            font_style="Body",
            role="small",
            size_hint_y=None,
            height=dp(20),
            markup=True,
        )
        self.root_layout.add_widget(self.status_label)

        # 2. Orders List
        scroll = ScrollView(size_hint=(1, 1))
        self.orders_container = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None,
        )
        self.orders_container.bind(minimum_height=self.orders_container.setter("height"))
        scroll.add_widget(self.orders_container)
        self.root_layout.add_widget(scroll)

        self.add_widget(self.root_layout)

    def on_enter(self):
        """Refresh user reservations when screen is visited."""
        self._hide_modals()
        if self.status_label:
            self.status_label.text = "Toca cualquier reserva para ver el código QR y el detalle de entrega."
        self.refresh_reservations()

    def refresh_reservations(self):
        self.orders_container.clear_widgets()
        orders = self.order_service.get_user_orders()

        if not orders:
            empty_card = MDCard(
                orientation="vertical",
                size_hint_y=None,
                height=dp(100),
                padding=dp(16),
                spacing=dp(6),
                style="elevated",
                md_bg_color=[1.0, 1.0, 1.0, 1],
                radius=[dp(14), dp(14), dp(14), dp(14)],
                line_color=[0.88, 0.92, 0.96, 1],
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

            card = MDCard(
                orientation="vertical",
                size_hint_y=None,
                height=dp(125),
                padding=[dp(14), dp(10), dp(14), dp(10)],
                spacing=dp(4),
                style="elevated",
                md_bg_color=[1.0, 1.0, 1.0, 1],
                radius=[dp(14), dp(14), dp(14), dp(14)],
                line_color=[0.88, 0.92, 0.96, 1],
            )

            # Top Line: Comanda # and Status Label ("Pendiente por pagar")
            top = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(24))
            comanda_lbl = MDLabel(
                text=f"[b][color=#0A3871]Comanda #{order.comanda_number}[/color][/b] [color=#64748B]({order.id_pedido})[/color]",
                markup=True,
                font_style="Title",
                role="small",
            )
            status_badge = MDLabel(
                text=f"[b][color={status_color}]{status_text}[/color][/b]",
                markup=True,
                halign="right",
                font_style="Label",
                role="medium",
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

            # Bottom Line: Total & View QR button
            bottom = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(32))
            total_lbl = MDLabel(
                text=f"[b]Total: {format_currency(order.total)}[/b] [color=#64748B]• {order.created_at.strftime('%H:%M')}[/color]",
                markup=True,
                font_style="Label",
                role="medium",
            )
            qr_btn = MDButton(
                MDButtonText(text="Ver QR y Detalle"),
                style="filled",
                size_hint_y=None,
                height=dp(28),
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

        self.detail_modal = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(420),
            padding=[dp(18), dp(14), dp(18), dp(14)],
            spacing=dp(8),
            style="elevated",
            md_bg_color=[1.0, 1.0, 1.0, 1],
            radius=[dp(18), dp(18), dp(18), dp(18)],
            line_color=[0.04, 0.22, 0.44, 0.4],
            elevation=3,
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

        # 2. Items list breakdown
        items_box = MDBoxLayout(orientation="vertical", spacing=dp(2), size_hint_y=None, height=dp(50))
        for item in order.items:
            row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(22))
            row.add_widget(
                MDLabel(
                    text=f"• {item.quantity}x {item.name}",
                    font_style="Body",
                    role="small",
                )
            )
            row.add_widget(
                MDLabel(
                    text=format_currency(item.subtotal),
                    halign="right",
                    font_style="Body",
                    role="small",
                    bold=True,
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

        # 3. QR Code visual texture
        qr_payload = order.pickup_qr or order.id_pedido
        try:
            qr_tex = generate_qr_texture(qr_payload)
            qr_widget = Image(
                texture=qr_tex,
                size_hint=(None, None),
                size=(dp(140), dp(140)),
                pos_hint={"center_x": 0.5},
            )
            self.detail_modal.add_widget(qr_widget)
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
            height=dp(30),
        )
        self.detail_modal.add_widget(instr_lbl)

        # 4. Actions: Cancel order (if eligible) & Close
        actions_box = MDBoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(38))

        if order.status in (OrderStatus.PENDING, OrderStatus.CONFIRMED):
            cancel_btn = MDButton(
                MDButtonText(text="Cancelar Reserva"),
                style="outlined",
                on_release=lambda x, o=order: self._ask_cancel_confirmation(o),
            )
            actions_box.add_widget(cancel_btn)

        close_btn = MDButton(
            MDButtonText(text="Cerrar"),
            style="filled",
            on_release=lambda x: self._hide_modals(),
        )
        actions_box.add_widget(close_btn)

        self.detail_modal.add_widget(actions_box)
        self.root_layout.add_widget(self.detail_modal, index=1)

    def _ask_cancel_confirmation(self, order: Order):
        """Show confirmation dialog before cancelling an active comanda."""
        self._hide_modals()

        self.confirm_modal = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(160),
            padding=[dp(16), dp(14), dp(16), dp(14)],
            spacing=dp(10),
            style="elevated",
            md_bg_color=[1.0, 1.0, 1.0, 1],
            radius=[dp(16), dp(16), dp(16), dp(16)],
            line_color=[0.93, 0.27, 0.27, 0.6],
            elevation=3,
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
            text=f"¿Estás seguro de cancelar la Comanda #{order.comanda_number} ({format_currency(order.total)})? Los platos reservados volverán al inventario del casino.",
            font_style="Body",
            role="small",
            size_hint_y=None,
            height=dp(42),
        )
        c_btns = MDBoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(38))
        btn_back = MDButton(
            MDButtonText(text="Volver"),
            style="tonal",
            on_release=lambda x: self._show_order_detail_modal(order),
        )
        btn_confirm = MDButton(
            MDButtonText(text="Sí, Cancelar"),
            style="filled",
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
            self.status_label.text = "[color=#EF4444]No se pudo cancelar la comanda.[/color]"
        self.refresh_reservations()

    def _hide_modals(self):
        """Cleanly remove dynamic modal cards to prevent memory leaks or FBO crashes."""
        if self.detail_modal and self.detail_modal in self.root_layout.children:
            self.root_layout.remove_widget(self.detail_modal)
            self.detail_modal = None
        if self.confirm_modal and self.confirm_modal in self.root_layout.children:
            self.root_layout.remove_widget(self.confirm_modal)
            self.confirm_modal = None
