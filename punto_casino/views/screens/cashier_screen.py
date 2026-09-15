"""Cashier order management screen for Cristian (Sabor Único) with numbered comandas and QR code scanner for checkout."""

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

from punto_casino.models.order import Order, OrderStatus, ORDER_STATUS_LABELS, ORDER_STATUS_COLORS
from punto_casino.services.cashier_service import CashierService
from punto_casino.utils.formatters import format_currency


class CashierScreen(MDScreen):
    """Cashier dashboard managing numbered comandas, action confirmations, and QR code checkout scanner."""

    def __init__(self, cashier_service: CashierService, on_navigate, **kwargs):
        super().__init__(**kwargs)
        self.cashier_service = cashier_service
        self.on_navigate = on_navigate

        self.root_layout = None
        self.orders_container = None
        self.status_label = None
        self.confirm_modal = None
        self.scanner_modal = None

        self._build_ui()

    def _build_ui(self):
        self.root_layout = MDBoxLayout(
            orientation="vertical",
            padding=[dp(16), dp(12), dp(16), dp(12)],
            spacing=dp(8),
        )

        # 1. Header with Scan & Refresh Actions
        header = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(42),
            spacing=dp(8),
        )
        title = MDLabel(
            text="[b][color=#0A3871]Caja y Cocina (Sabor Único)[/color][/b]",
            markup=True,
            font_style="Title",
            role="medium",
        )
        scan_btn = MDButton(
            MDButtonText(text="Escanear QR"),
            style="filled",
            size_hint_y=None,
            height=dp(34),
            on_release=lambda x: self._show_qr_scanner_modal(),
        )
        refresh_btn = MDButton(
            MDButtonText(text="Refrescar"),
            style="tonal",
            size_hint_y=None,
            height=dp(34),
            on_release=lambda x: self.refresh_orders(),
        )
        header.add_widget(title)
        header.add_widget(scan_btn)
        header.add_widget(refresh_btn)
        self.root_layout.add_widget(header)

        # 2. Status feedback
        self.status_label = MDLabel(
            text="Comandas en espera de preparación y entrega por código QR.",
            font_style="Body",
            role="small",
            size_hint_y=None,
            height=dp(20),
            markup=True,
        )
        self.root_layout.add_widget(self.status_label)

        # 3. Orders list
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
        """Refresh orders when cashier screen is entered."""
        self._hide_modals()
        if self.status_label:
            self.status_label.text = "Comandas en espera de preparación y entrega por código QR."
        self.refresh_orders()

    def refresh_orders(self):
        self.orders_container.clear_widgets()
        pending = self.cashier_service.get_pending_orders()

        if not pending:
            empty_card = MDCard(
                orientation="vertical",
                size_hint_y=None,
                height=dp(80),
                padding=dp(16),
                style="elevated",
                md_bg_color=[1.0, 1.0, 1.0, 1],
                radius=[dp(14), dp(14), dp(14), dp(14)],
                line_color=[0.88, 0.92, 0.96, 1],
            )
            empty_card.add_widget(
                MDLabel(
                    text="[color=#64748B]No hay comandas pendientes en cola de cocina.[/color]",
                    markup=True,
                    halign="center",
                    font_style="Body",
                    role="small",
                )
            )
            self.orders_container.add_widget(empty_card)
            return

        for order in pending:
            status_text = ORDER_STATUS_LABELS.get(order.status, order.status.value)
            status_color = ORDER_STATUS_COLORS.get(order.status, "#D97706")

            card = MDCard(
                orientation="vertical",
                size_hint_y=None,
                height=dp(130),
                padding=[dp(14), dp(10), dp(14), dp(10)],
                spacing=dp(4),
                style="elevated",
                md_bg_color=[1.0, 1.0, 1.0, 1],
                radius=[dp(14), dp(14), dp(14), dp(14)],
                line_color=[0.88, 0.92, 0.96, 1],
            )

            # Row 1: Comanda Number and Total
            top_line = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(24))
            comanda_label = MDLabel(
                text=f"[b][color=#0A3871]Comanda #{order.comanda_number}[/color][/b] [color=#64748B]({order.id_pedido})[/color]",
                markup=True,
                font_style="Title",
                role="small",
            )
            total_label = MDLabel(
                text=f"[b]{format_currency(order.total)}[/b]",
                markup=True,
                halign="right",
                font_style="Title",
                role="small",
            )
            top_line.add_widget(comanda_label)
            top_line.add_widget(total_label)

            # Row 2: Customer name & Status
            meta_line = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(20))
            client_label = MDLabel(
                text=f"Cliente: {order.customer_name} • {order.created_at.strftime('%H:%M')}",
                font_style="Body",
                role="small",
            )
            status_badge = MDLabel(
                text=f"[color={status_color}][b]{status_text}[/b][/color]",
                markup=True,
                halign="right",
                font_style="Label",
                role="medium",
            )
            meta_line.add_widget(client_label)
            meta_line.add_widget(status_badge)

            # Row 3: Items summary
            items_summary = ", ".join(f"{i.quantity}x {i.name}" for i in order.items)
            details_label = MDLabel(
                text=f"[color=#475569]Platos: {items_summary}[/color]",
                markup=True,
                font_style="Body",
                role="small",
                shorten=True,
                shorten_from="right",
                size_hint_y=None,
                height=dp(20),
            )

            # Row 4: Cashier action buttons
            actions = MDBoxLayout(
                orientation="horizontal",
                spacing=dp(8),
                size_hint_y=None,
                height=dp(32),
            )
            reject_btn = MDButton(
                MDButtonText(text="Rechazar"),
                style="outlined",
                size_hint_y=None,
                height=dp(28),
                on_release=lambda x, o=order: self._ask_reject_confirmation(o),
            )
            confirm_btn = MDButton(
                MDButtonText(text="Confirmar Cocina"),
                style="tonal",
                size_hint_y=None,
                height=dp(28),
                on_release=lambda x, o=order: self._ask_confirm_confirmation(o),
            )
            scan_charge_btn = MDButton(
                MDButtonText(text="Cobrar (QR)"),
                style="filled",
                size_hint_y=None,
                height=dp(28),
                on_release=lambda x, o=order: self._show_qr_scanner_modal(prefill_id=o.id_pedido),
            )
            actions.add_widget(reject_btn)
            actions.add_widget(confirm_btn)
            actions.add_widget(scan_charge_btn)

            card.add_widget(top_line)
            card.add_widget(meta_line)
            card.add_widget(details_label)
            card.add_widget(actions)
            self.orders_container.add_widget(card)

    def _show_qr_scanner_modal(self, prefill_id: str = ""):
        """Open cashier QR scanner interface for validating codes and charging orders."""
        self._hide_modals()

        self.scanner_modal = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(360),
            padding=[dp(18), dp(14), dp(18), dp(14)],
            spacing=dp(8),
            style="elevated",
            md_bg_color=[1.0, 1.0, 1.0, 1],
            radius=[dp(18), dp(18), dp(18), dp(18)],
            line_color=[0.04, 0.22, 0.44, 0.4],
            elevation=3,
        )

        title = MDLabel(
            text="[b][color=#0A3871]Escáner de Comandas y Cobro en Caja[/color][/b]",
            markup=True,
            font_style="Title",
            role="medium",
            size_hint_y=None,
            height=dp(24),
        )
        desc = MDLabel(
            text="[color=#64748B]Ingresa el código o selecciona la comanda para cobrar y entregar.[/color]",
            markup=True,
            font_style="Body",
            role="small",
            size_hint_y=None,
            height=dp(18),
        )
        self.scanner_modal.add_widget(title)
        self.scanner_modal.add_widget(desc)

        # Input field for QR payload or Order ID
        self.qr_input = MDTextField(
            MDTextFieldLeadingIcon(icon="qrcode-scan"),
            MDTextFieldHintText(text="Código de Pedido o Payload QR"),
            mode="outlined",
            size_hint_y=None,
            height=dp(50),
        )
        if prefill_id:
            self.qr_input.text = prefill_id
        self.scanner_modal.add_widget(self.qr_input)

        # Quick-scan simulator buttons for active orders
        pending = self.cashier_service.order_repo.get_all()
        active_orders = [o for o in pending if o.status in (OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.READY)]

        if active_orders:
            sim_box = MDBoxLayout(orientation="horizontal", spacing=dp(6), size_hint_y=None, height=dp(30))
            sim_lbl = MDLabel(
                text="Comandas activas:",
                font_style="Label",
                role="small",
                size_hint_x=None,
                width=dp(105),
            )
            sim_box.add_widget(sim_lbl)

            for ord_item in active_orders[:3]:  # Up to 3 quick buttons
                b = MDButton(
                    MDButtonText(text=f"#{ord_item.comanda_number}"),
                    style="tonal",
                    size_hint_y=None,
                    height=dp(28),
                    on_release=lambda x, p=ord_item.id_pedido: self._set_qr_input_and_preview(p),
                )
                sim_box.add_widget(b)
            self.scanner_modal.add_widget(sim_box)

        # Preview Container
        self.preview_box = MDBoxLayout(
            orientation="vertical",
            spacing=dp(2),
            size_hint_y=None,
            height=dp(70),
            padding=[dp(10), dp(4), dp(10), dp(4)],
            md_bg_color=[0.95, 0.97, 1.0, 1],
        )
        self.preview_label = MDLabel(
            text="Presiona 'Verificar Comanda' para previsualizar los platos.",
            font_style="Body",
            role="small",
            halign="center",
        )
        self.preview_box.add_widget(self.preview_label)
        self.scanner_modal.add_widget(self.preview_box)

        # Feedback label
        self.scanner_feedback = MDLabel(
            text="",
            markup=True,
            font_style="Label",
            role="small",
            halign="center",
            size_hint_y=None,
            height=dp(18),
        )
        self.scanner_modal.add_widget(self.scanner_feedback)

        # Action Buttons: Verify, Charge & Close
        btn_box = MDBoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(38))
        btn_verify = MDButton(
            MDButtonText(text="Verificar"),
            style="tonal",
            on_release=lambda x: self._on_verify_qr_input(),
        )
        btn_charge = MDButton(
            MDButtonText(text="Cobrar y Entregar"),
            style="filled",
            on_release=lambda x: self._on_execute_qr_checkout(),
        )
        btn_close = MDButton(
            MDButtonText(text="Cerrar"),
            style="outlined",
            on_release=lambda x: self._hide_modals(),
        )
        btn_box.add_widget(btn_verify)
        btn_box.add_widget(btn_charge)
        btn_box.add_widget(btn_close)
        self.scanner_modal.add_widget(btn_box)

        self.root_layout.add_widget(self.scanner_modal, index=1)

        if prefill_id:
            self._on_verify_qr_input()

    def _set_qr_input_and_preview(self, order_id: str):
        self.qr_input.text = order_id
        self._on_verify_qr_input()

    def _on_verify_qr_input(self):
        """Look up order from entered text and preview dishes and total."""
        code = self.qr_input.text.strip()
        if not code:
            self.scanner_feedback.text = "[color=#EF4444]Por favor ingresa un código QR o de comanda.[/color]"
            return

        order = self.cashier_service.order_repo.get_by_id(code)
        if not order:
            from punto_casino.utils.qr_generator import parse_pickup_payload
            parsed = parse_pickup_payload(code)
            if parsed and "order_id" in parsed:
                order = self.cashier_service.order_repo.get_by_id(parsed["order_id"])

        if not order:
            self.preview_label.text = f"No se encontró ninguna comanda con el código '{code}'."
            self.scanner_feedback.text = "[color=#EF4444]Código no encontrado.[/color]"
            return

        status_text = ORDER_STATUS_LABELS.get(order.status, order.status.value)
        items_str = ", ".join(f"{i.quantity}x {i.name}" for i in order.items)
        self.preview_label.text = (
            f"[b]Comanda #{order.comanda_number}[/b] • Cliente: {order.customer_name}\n"
            f"Platos: {items_str}\n"
            f"[b]Total a cobrar: {format_currency(order.total)}[/b] (Estado: {status_text})"
        )
        self.preview_label.markup = True
        self.scanner_feedback.text = "[color=#0288D1]Comanda verificada. Lista para cobrar.[/color]"

    def _on_execute_qr_checkout(self):
        """Execute checkout and delivery using cashier service."""
        code = self.qr_input.text.strip()
        if not code:
            self.scanner_feedback.text = "[color=#EF4444]Ingresa o verifica un código antes de cobrar.[/color]"
            return

        success, message, order = self.cashier_service.process_qr_payment(code)
        if success:
            self.scanner_feedback.text = f"[color=#10B981]{message}[/color]"
            self.status_label.text = f"[color=#10B981]{message}[/color]"
            self.refresh_orders()
        else:
            self.scanner_feedback.text = f"[color=#EF4444]{message}[/color]"

    def _ask_confirm_confirmation(self, order: Order):
        """Action confirmation before approving order for kitchen."""
        self._hide_modals()
        self.confirm_modal = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(135),
            padding=[dp(16), dp(12), dp(16), dp(12)],
            spacing=dp(8),
            style="elevated",
            md_bg_color=[1.0, 1.0, 1.0, 1],
            radius=[dp(14), dp(14), dp(14), dp(14)],
            line_color=[0.01, 0.53, 0.82, 0.6],
            elevation=3,
        )
        title = MDLabel(
            text="[b][color=#0A3871]Confirmar Comanda para Cocina[/color][/b]",
            markup=True,
            font_style="Title",
            role="small",
            size_hint_y=None,
            height=dp(22),
        )
        msg = MDLabel(
            text=f"¿Aprobar Comanda #{order.comanda_number} de {order.customer_name} por {format_currency(order.total)}?",
            font_style="Body",
            role="small",
            size_hint_y=None,
            height=dp(32),
        )
        btns = MDBoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(34))

        cancel_btn = MDButton(MDButtonText(text="Cancelar"), style="tonal", on_release=lambda x: self._hide_modals())
        accept_btn = MDButton(MDButtonText(text="Sí, Confirmar"), style="filled", on_release=lambda x: self._execute_confirm(order.id_pedido))
        btns.add_widget(cancel_btn)
        btns.add_widget(accept_btn)

        self.confirm_modal.add_widget(title)
        self.confirm_modal.add_widget(msg)
        self.confirm_modal.add_widget(btns)
        self.root_layout.add_widget(self.confirm_modal, index=1)

    def _ask_reject_confirmation(self, order: Order):
        """Action confirmation before rejecting order."""
        self._hide_modals()
        self.confirm_modal = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(135),
            padding=[dp(16), dp(12), dp(16), dp(12)],
            spacing=dp(8),
            style="elevated",
            md_bg_color=[1.0, 1.0, 1.0, 1],
            radius=[dp(14), dp(14), dp(14), dp(14)],
            line_color=[0.93, 0.27, 0.27, 0.6],
            elevation=3,
        )
        title = MDLabel(
            text="[b][color=#DC2626]Rechazar Comanda[/color][/b]",
            markup=True,
            font_style="Title",
            role="small",
            size_hint_y=None,
            height=dp(22),
        )
        msg = MDLabel(
            text=f"¿Rechazar Comanda #{order.comanda_number}? Se restituirá el stock al inventario de cocina.",
            font_style="Body",
            role="small",
            size_hint_y=None,
            height=dp(32),
        )
        btns = MDBoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(34))

        cancel_btn = MDButton(MDButtonText(text="Cancelar"), style="tonal", on_release=lambda x: self._hide_modals())
        reject_btn = MDButton(MDButtonText(text="Sí, Rechazar"), style="filled", on_release=lambda x: self._execute_reject(order.id_pedido))
        btns.add_widget(cancel_btn)
        btns.add_widget(reject_btn)

        self.confirm_modal.add_widget(title)
        self.confirm_modal.add_widget(msg)
        self.confirm_modal.add_widget(btns)
        self.root_layout.add_widget(self.confirm_modal, index=1)

    def _hide_modals(self):
        """Remove any active dynamic modal card cleanly."""
        if self.confirm_modal and self.confirm_modal in self.root_layout.children:
            self.root_layout.remove_widget(self.confirm_modal)
            self.confirm_modal = None
        if self.scanner_modal and self.scanner_modal in self.root_layout.children:
            self.root_layout.remove_widget(self.scanner_modal)
            self.scanner_modal = None

    def _execute_confirm(self, order_id: str):
        self._hide_modals()
        confirmed = self.cashier_service.confirm_order(order_id)
        if confirmed:
            self.status_label.text = f"Comanda #{confirmed.comanda_number} confirmada para preparación en cocina."
            self.refresh_orders()

    def _execute_reject(self, order_id: str):
        self._hide_modals()
        rejected = self.cashier_service.reject_order(order_id)
        if rejected:
            self.status_label.text = f"Comanda #{rejected.comanda_number} rechazada y stock restituido."
            self.refresh_orders()
