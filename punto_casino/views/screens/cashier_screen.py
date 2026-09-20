"""Cashier order management screen for Cristian (Sabor Único) with anti-overflow cards, live OpenCV QR scanner, and order history."""

from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.metrics import dp
from kivy.uix.image import Image
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
from punto_casino.services.cashier_service import CashierService
from punto_casino.utils.formatters import format_currency
from punto_casino.utils.qr_generator import (
    decode_qr_image,
    parse_pickup_payload,
    generate_pickup_payload,
)
from punto_casino.views.components.ui_elements import create_button, VIBRANT_ORANGE, CRIMSON_RED, UCT_NAVY, WHITE


class CashierScreen(MDScreen):
    """Cashier dashboard managing numbered comandas, 2-tier action buttons, live OpenCV QR scanner, and shift history."""

    def __init__(self, cashier_service: CashierService, on_navigate, **kwargs):
        super().__init__(**kwargs)
        self.cashier_service = cashier_service
        self.on_navigate = on_navigate

        self.current_tab = "queue"  # "queue" or "history"
        self.root_layout = None
        self.orders_container = None
        self.status_label = None
        self.scanner_modal = None
        self.confirm_modal = None

        # Live OpenCV QR Scanner state
        self._camera = None
        self._camera_event = None
        self._is_camera_active = False
        self.cam_container = None
        self.cam_widget = None
        self.cam_placeholder_lbl = None
        self.cam_btn = None

        self._build_ui()

    def _build_ui(self):
        self.root_layout = MDBoxLayout(
            orientation="vertical",
            padding=[dp(14), dp(10), dp(14), dp(10)],
            spacing=dp(8),
            theme_bg_color="Custom",
            md_bg_color=[0.96, 0.97, 0.99, 1.0],
        )

        # 1. Header with Scan & Tab Switcher (High contrast, vector icons)
        header = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(108),
            spacing=dp(6),
        )

        # 1.1 Title Row
        title_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(34),
            spacing=dp(8),
        )
        title = MDLabel(
            text="[b][color=#0A3871]Caja y Cocina (Sabor Único)[/color][/b]",
            markup=True,
            font_style="Title",
            role="medium",
        )
        scan_btn = create_button(
            text="Escáner QR",
            icon="qrcode-scan",
            style="filled",
            size_hint=(None, None),
            height=dp(32),
            on_release=lambda x: self._show_qr_scanner_modal(),
        )
        title_row.add_widget(title)
        title_row.add_widget(scan_btn)

        # 1.2 View Description / Status Feedback (Always fixed at the top)
        self.status_label = MDLabel(
            text="[color=#64748B]Comandas activas listas para preparación y cobro en mesón.[/color]",
            font_style="Body",
            role="small",
            size_hint_y=None,
            height=dp(22),
            markup=True,
            padding=[dp(2), dp(2), dp(2), dp(2)],
        )

        # 1.3 Tabs: Cola Activa vs Historial Turno
        tabs_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(36),
            spacing=dp(8),
        )
        self.btn_tab_queue = create_button(
            text="Cola Activa",
            icon="tray-full",
            style="filled" if self.current_tab == "queue" else "tonal",
            size_hint=(0.5, None),
            height=dp(34),
            on_release=lambda x: self._switch_tab("queue"),
        )
        self.btn_tab_history = create_button(
            text="Historial Turno",
            icon="history",
            style="filled" if self.current_tab == "history" else "tonal",
            size_hint=(0.5, None),
            height=dp(34),
            on_release=lambda x: self._switch_tab("history"),
        )
        tabs_row.add_widget(self.btn_tab_queue)
        tabs_row.add_widget(self.btn_tab_history)

        header.add_widget(title_row)
        header.add_widget(self.status_label)
        header.add_widget(tabs_row)
        self.root_layout.add_widget(header)

        # 3. Orders Scroll Container
        self.scroll = ScrollView(size_hint=(1, 1))
        self.orders_container = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            size_hint_y=None,
        )
        self.orders_container.bind(minimum_height=self.orders_container.setter("height"))
        self.scroll.add_widget(self.orders_container)
        self.root_layout.add_widget(self.scroll)

        self.add_widget(self.root_layout)

    def on_enter(self):
        """Refresh orders when cashier screen is entered."""
        self._hide_modals()
        self.refresh_orders()

    def _switch_tab(self, tab_name: str):
        self.current_tab = tab_name
        self._hide_modals()
        if tab_name == "queue":
            self.btn_tab_queue.style = "filled"
            self.btn_tab_history.style = "tonal"
            self.status_label.text = "Cola de comandas activas pendientes de entrega."
        else:
            self.btn_tab_queue.style = "tonal"
            self.btn_tab_history.style = "filled"
            self.status_label.text = "Historial de comandas entregadas, canceladas y rechazadas."
        self.refresh_orders()

    def refresh_orders(self):
        self.orders_container.clear_widgets()

        if self.current_tab == "queue":
            orders = self.cashier_service.get_pending_orders()
            empty_text = "No hay comandas pendientes en cola de cocina."
        else:
            orders = self.cashier_service.get_history_orders()
            empty_text = "No hay comandas registradas en el historial de este turno."

        if not orders:
            empty_card = MDCard(
                orientation="vertical",
                size_hint_y=None,
                height=dp(70),
                padding=dp(12),
                style="outlined",
                theme_bg_color="Custom",
                md_bg_color=[1.0, 1.0, 1.0, 1.0],
                radius=[dp(12), dp(12), dp(12), dp(12)],
                line_color=[0.88, 0.92, 0.96, 1.0],
                elevation=0,
            )
            empty_card.add_widget(
                MDLabel(
                    text=f"[color=#64748B]{empty_text}[/color]",
                    markup=True,
                    halign="center",
                    font_style="Body",
                    role="small",
                )
            )
            self.orders_container.add_widget(empty_card)
            return

        for order in orders:
            card = self._build_comanda_card(order, is_history=(self.current_tab == "history"))
            self.orders_container.add_widget(card)

    def _build_comanda_card(self, order: Order, is_history: bool = False) -> MDCard:
        status_text = ORDER_STATUS_LABELS.get(order.status, order.status.value)
        status_color = ORDER_STATUS_COLORS.get(order.status, "#D97706")

        if not is_history:
            if order.status in (OrderStatus.PENDING, OrderStatus.CONFIRMED):
                card_h = dp(175)
            elif order.status == OrderStatus.READY:
                card_h = dp(140)
            else:
                card_h = dp(98)
        else:
            card_h = dp(98)

        card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=card_h,
            padding=[dp(14), dp(10), dp(14), dp(10)],
            spacing=dp(6),
            style="outlined",
            theme_bg_color="Custom",
            md_bg_color=[1.0, 1.0, 1.0, 1.0],
            radius=[dp(12), dp(12), dp(12), dp(12)],
            line_color=[0.88, 0.92, 0.96, 1.0],
            elevation=0,
        )

        # Line 1: Comanda Number & Total
        line1 = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(24), spacing=dp(4))
        c_title = MDLabel(
            text=f"[b][color=#0A3871]Comanda #{order.comanda_number}[/color][/b] [color=#64748B]({order.id_pedido})[/color]",
            markup=True,
            font_style="Title",
            role="small",
            size_hint_x=0.64,
            shorten=True,
            shorten_from="right",
        )
        c_total = MDLabel(
            text=f"[b][color=#0288D1]{format_currency(order.total)}[/color][/b]",
            markup=True,
            halign="right",
            font_style="Title",
            role="small",
            size_hint_x=0.36,
        )
        line1.add_widget(c_title)
        line1.add_widget(c_total)
        card.add_widget(line1)

        # Line 2: Customer Name & Status Badge
        line2 = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(20), spacing=dp(4))
        c_meta = MDLabel(
            text=f"[color=#475569]Cliente: {order.customer_name} • {order.created_at.strftime('%H:%M')}[/color]",
            markup=True,
            font_style="Body",
            role="small",
            size_hint_x=0.58,
            shorten=True,
            shorten_from="right",
        )
        c_badge = MDLabel(
            text=f"[color={status_color}][b]{status_text}[/b][/color]",
            markup=True,
            halign="right",
            font_style="Label",
            role="small",
            size_hint_x=0.42,
            shorten=True,
            shorten_from="right",
        )
        line2.add_widget(c_meta)
        line2.add_widget(c_badge)
        card.add_widget(line2)

        # Line 3: Order Line Items Summary
        items_summary = ", ".join(f"{i.quantity}x {i.name}" for i in order.items)
        c_items = MDLabel(
            text=f"[color=#64748B]Platos: {items_summary}[/color]",
            markup=True,
            font_style="Body",
            role="small",
            shorten=True,
            shorten_from="right",
            size_hint_y=None,
            height=dp(18),
        )
        card.add_widget(c_items)

        # Active Queue Action Buttons (High contrast, ergonomic 2-tier layout)
        if not is_history and order.status == OrderStatus.PENDING:
            # Tier 1: Direct Charge Action (1-tap, no webcam required)
            tier1_btn = create_button(
                text="Cobrar y Entregar",
                icon="cash-register",
                style="filled",
                size_hint=(1, None),
                height=dp(34),
                on_release=lambda x, o=order: self._ask_charge_comanda(o),
            )
            card.add_widget(tier1_btn)

            # Tier 2: Kitchen Confirmation & Rejection
            tier2_box = MDBoxLayout(
                orientation="horizontal",
                spacing=dp(8),
                size_hint_y=None,
                height=dp(32),
            )
            conf_btn = create_button(
                text="Confirmar Cocina",
                icon="check",
                style="success",
                size_hint=(0.5, None),
                height=dp(30),
                on_release=lambda x, o=order: self._ask_confirm(o),
            )
            rej_btn = create_button(
                text="Rechazar",
                icon="close",
                style="danger",
                size_hint=(0.5, None),
                height=dp(30),
                on_release=lambda x, o=order: self._ask_reject(o),
            )
            tier2_box.add_widget(conf_btn)
            tier2_box.add_widget(rej_btn)
            card.add_widget(tier2_box)
        elif not is_history and order.status == OrderStatus.CONFIRMED:
            # Tier 1: Cashier can ALWAYS charge confirmed orders
            tier1_btn = create_button(
                text="Cobrar y Entregar",
                icon="cash-register",
                style="filled",
                size_hint=(1, None),
                height=dp(34),
                on_release=lambda x, o=order: self._ask_charge_comanda(o),
            )
            card.add_widget(tier1_btn)

            # Tier 2: Mark ready in kitchen or open QR scanner
            tier2_box = MDBoxLayout(
                orientation="horizontal",
                spacing=dp(8),
                size_hint_y=None,
                height=dp(32),
            )
            ready_btn = create_button(
                text="Listo Cocina",
                icon="check-all",
                style="tonal",
                size_hint=(0.5, None),
                height=dp(30),
                on_release=lambda x, o=order: self._mark_order_ready(o),
            )
            scan_btn = create_button(
                text="Escanear QR",
                icon="qrcode-scan",
                style="outlined",
                size_hint=(0.5, None),
                height=dp(30),
                on_release=lambda x, o=order: self._show_qr_scanner_modal(prefill_id=o.id_pedido),
            )
            tier2_box.add_widget(ready_btn)
            tier2_box.add_widget(scan_btn)
            card.add_widget(tier2_box)
        elif not is_history and order.status == OrderStatus.READY:
            ready_btn = create_button(
                text="Cobrar y Entregar",
                icon="cash-register",
                style="filled",
                size_hint=(1, None),
                height=dp(34),
                on_release=lambda x, o=order: self._ask_charge_comanda(o),
            )
            card.add_widget(ready_btn)

        return card

    def on_leave(self):
        """Ensure background camera capture is cleanly stopped when leaving cashier screen."""
        self._stop_camera()
        self._hide_modals()

    # --- Live OpenCV QR Scanner Modal & Controls ---

    def _show_qr_scanner_modal(self, prefill_id: str = ""):
        self._hide_modals()

        # Hide background scroll to avoid any background card leaking
        if hasattr(self, "scroll") and self.scroll:
            self.scroll.opacity = 0
            self.scroll.size_hint_y = None
            self.scroll.height = 0
            self.scroll.disabled = True

        self.scanner_modal = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(455),
            padding=[dp(16), dp(12), dp(16), dp(12)],
            spacing=dp(6),
            style="outlined",
            theme_bg_color="Custom",
            md_bg_color=[1.0, 1.0, 1.0, 1.0],
            radius=[dp(16), dp(16), dp(16), dp(16)],
            line_color=[0.04, 0.22, 0.44, 0.4],
            elevation=0,
        )

        title = MDLabel(
            text="[b][color=#0A3871]Lector QR y Cobro en Caja[/color][/b]",
            markup=True,
            font_style="Title",
            role="medium",
            size_hint_y=None,
            height=dp(24),
        )
        self.scanner_modal.add_widget(title)

        # 1. Live Camera / QR Scanner Viewport
        self.cam_container = MDCard(
            orientation="vertical",
            size_hint=(1, None),
            height=dp(160),
            style="filled",
            theme_bg_color="Custom",
            md_bg_color=[0.93, 0.96, 0.99, 1.0],
            radius=[dp(10), dp(10), dp(10), dp(10)],
            line_color=[0.04, 0.22, 0.44, 0.25],
            elevation=0,
            padding=dp(4),
        )
        self.cam_placeholder_lbl = MDLabel(
            text="[b][color=#0A3871]Cámara en Espera[/color][/b]\n[color=#64748B]Presiona 'Escanear con Cámara' para activar el lector en tiempo real por webcam, o usa 'Demo QR'.[/color]",
            halign="center",
            markup=True,
            font_style="Body",
            role="small",
        )
        self.cam_container.add_widget(self.cam_placeholder_lbl)
        self.scanner_modal.add_widget(self.cam_container)

        # 2. Scanner Mode Buttons Row
        scan_tools_row = MDBoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(34))
        self.cam_btn = create_button(
            text="Escanear con Cámara",
            icon="camera",
            style="offer",
            size_hint=(0.58, None),
            height=dp(34),
            on_release=lambda x: self._toggle_camera(),
        )
        demo_btn = create_button(
            text="Demo QR",
            icon="qrcode-scan",
            style="tonal",
            size_hint=(0.42, None),
            height=dp(34),
            on_release=lambda x: self._simulate_sample_qr(),
        )
        scan_tools_row.add_widget(self.cam_btn)
        scan_tools_row.add_widget(demo_btn)
        self.scanner_modal.add_widget(scan_tools_row)

        # 3. Code Input (Explicit title label prevents floating hint collision)
        input_container = MDBoxLayout(orientation="vertical", spacing=dp(2), size_hint_y=None, height=dp(56))
        input_title = MDLabel(
            text="[b][color=#0A3871]Código de Comanda / Pedido:[/color][/b]",
            markup=True,
            font_style="Label",
            role="medium",
            size_hint_y=None,
            height=dp(16),
        )
        self.qr_text_input = MDTextField(
            MDTextFieldLeadingIcon(icon="barcode-scan"),
            mode="outlined",
            size_hint_y=None,
            height=dp(38),
        )
        if prefill_id:
            self.qr_text_input.text = prefill_id
        input_container.add_widget(input_title)
        input_container.add_widget(self.qr_text_input)
        self.scanner_modal.add_widget(input_container)

        # 4. Status / Feedback box
        self.scanner_feedback_lbl = MDLabel(
            text="Listo para escanear o validar comanda.",
            font_style="Body",
            role="small",
            size_hint_y=None,
            height=dp(20),
            markup=True,
        )
        if prefill_id:
            self._on_verify_code()
        self.scanner_modal.add_widget(self.scanner_feedback_lbl)

        # 5. 2-Tier Modal Actions (High contrast, vector icons):
        charge_btn = create_button(
            text="Cobrar y Entregar Pedido",
            icon="check",
            style="filled",
            size_hint=(1, None),
            height=dp(36),
            on_release=lambda x: self._on_execute_charge(),
        )
        self.scanner_modal.add_widget(charge_btn)

        t2_row = MDBoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(32))
        verify_btn = create_button(
            text="Verificar",
            icon="magnify",
            style="tonal",
            size_hint=(0.5, None),
            height=dp(32),
            on_release=lambda x: self._on_verify_code(),
        )
        close_btn = create_button(
            text="Cerrar",
            style="outlined",
            size_hint=(0.5, None),
            height=dp(32),
            on_release=lambda x: self._hide_modals(),
        )
        t2_row.add_widget(verify_btn)
        t2_row.add_widget(close_btn)
        self.scanner_modal.add_widget(t2_row)

        self.root_layout.add_widget(self.scanner_modal, index=1)

    def _toggle_camera(self):
        """Toggle OpenCV camera feed on/off."""
        if self._is_camera_active:
            self._stop_camera()
        else:
            self._start_camera()

    def _start_camera(self):
        """Initialize OpenCV VideoCapture and start frame polling."""
        try:
            import cv2
        except ImportError:
            self.scanner_feedback_lbl.text = "[color=#EF4444]Librería OpenCV no instalada.[/color]"
            return

        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                self.scanner_feedback_lbl.text = "[color=#EF4444]No se detectó cámara web física disponible.[/color]"
                return

            self._camera = cap
            self._is_camera_active = True
            self.cam_container.clear_widgets()
            self.cam_widget = Image(size_hint=(1, 1), allow_stretch=True, keep_ratio=True)
            self.cam_container.add_widget(self.cam_widget)

            if self.cam_btn:
                for c in self.cam_btn.children:
                    if isinstance(c, MDButtonText):
                        c.text = "Detener Cámara"
                self.cam_btn.md_bg_color = CRIMSON_RED

            self.scanner_feedback_lbl.text = "[color=#0288D1]Enfoca el código QR de la reserva...[/color]"
            self._camera_event = Clock.schedule_interval(self._update_camera_frame, 1.0 / 20.0)
        except Exception as e:
            self.scanner_feedback_lbl.text = f"[color=#EF4444]Error iniciando cámara: {e}[/color]"

    def _update_camera_frame(self, dt):
        """Capture frame, blit to Kivy texture, and detect QR code with OpenCV."""
        if not self._camera or not self._camera.isOpened():
            self._stop_camera()
            return

        ret, frame = self._camera.read()
        if not ret or frame is None:
            return

        # Update Kivy texture for live preview
        import cv2
        try:
            buf = cv2.flip(frame, 0).tobytes()
            tex = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt="bgr")
            tex.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")
            if self.cam_widget:
                self.cam_widget.texture = tex
        except Exception:
            pass

        # Detect and decode QR comanda with OpenCV
        try:
            decoded_val = decode_qr_image(frame)
            if decoded_val:
                parsed = parse_pickup_payload(decoded_val)
                order_id = parsed["order_id"] if (parsed and "order_id" in parsed) else decoded_val.strip()
                self.qr_text_input.text = order_id
                self._stop_camera()
                self._on_verify_code()
                self.scanner_feedback_lbl.text = (
                    f"[b][color=#10B981]✓ ¡QR Leído con Éxito! ({order_id})[/color][/b]"
                )
        except Exception:
            pass

    def _stop_camera(self):
        """Stop camera polling and release hardware resources cleanly."""
        if self._camera_event:
            self._camera_event.cancel()
            self._camera_event = None
        if self._camera:
            try:
                self._camera.release()
            except Exception:
                pass
            self._camera = None

        self._is_camera_active = False
        if hasattr(self, "cam_container") and self.cam_container:
            self.cam_container.clear_widgets()
            if self.cam_placeholder_lbl:
                self.cam_container.add_widget(self.cam_placeholder_lbl)

        if self.cam_btn:
            for c in self.cam_btn.children:
                if isinstance(c, MDButtonText):
                    c.text = "Escanear con Cámara"
            self.cam_btn.md_bg_color = VIBRANT_ORANGE

    def _simulate_sample_qr(self):
        """Demonstrate instant OpenCV QR decoding pipeline on the next pending comanda."""
        pending = self.cashier_service.get_pending_orders()
        if not pending:
            pending = self.cashier_service.order_repo.get_all()
        if not pending:
            self.scanner_feedback_lbl.text = "[color=#EF4444]No hay pedidos registrados para simular escaneo.[/color]"
            return

        order = pending[0]
        # Generate payload & decode via OpenCV utility
        payload = generate_pickup_payload(order.id_pedido, order.customer_name)
        parsed = parse_pickup_payload(payload)
        self.qr_text_input.text = parsed["order_id"]
        self._on_verify_code()
        self.scanner_feedback_lbl.text = (
            f"[b][color=#10B981]✓ QR Leído por OpenCV: Comanda #{order.comanda_number} ({order.customer_name})[/color][/b]"
        )

    def _on_verify_code(self):
        val = self.qr_text_input.text.strip()
        if not val:
            self.scanner_feedback_lbl.text = "[color=#EF4444]Ingresa un código de pedido o QR.[/color]"
            return

        parsed = parse_pickup_payload(val)
        order_id = parsed["order_id"] if (parsed and "order_id" in parsed) else val

        order = self.cashier_service.order_repo.get_by_id(order_id)
        if not order:
            self.scanner_feedback_lbl.text = f"[color=#EF4444]No existe orden con código {order_id}[/color]"
            return

        status_text = ORDER_STATUS_LABELS.get(order.status, order.status.value)
        self.scanner_feedback_lbl.text = (
            f"[color=#10B981]Comanda #{order.comanda_number} ({order.customer_name}) - "
            f"{format_currency(order.total)} [{status_text}][/color]"
        )

    def _on_execute_charge(self):
        val = self.qr_text_input.text.strip()
        if not val:
            self.scanner_feedback_lbl.text = "[color=#EF4444]Ingresa un código de pedido.[/color]"
            return

        success, msg, order = self.cashier_service.process_qr_payment(val)
        if success:
            self.status_label.text = f"[color=#10B981]{msg}[/color]"
            self._hide_modals()
            self.refresh_orders()
        else:
            self.scanner_feedback_lbl.text = f"[color=#EF4444]{msg}[/color]"

    def _ask_charge_comanda(self, order: Order):
        """Show clear confirmation modal to charge and deliver comanda immediately."""
        self._hide_modals()

        if hasattr(self, "scroll") and self.scroll:
            self.scroll.opacity = 0
            self.scroll.size_hint_y = None
            self.scroll.height = 0
            self.scroll.disabled = True

        self.confirm_modal = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(175),
            padding=[dp(16), dp(12), dp(16), dp(12)],
            spacing=dp(10),
            style="outlined",
            theme_bg_color="Custom",
            md_bg_color=[1.0, 1.0, 1.0, 1.0],
            radius=[dp(16), dp(16), dp(16), dp(16)],
            line_color=[0.04, 0.22, 0.44, 0.4],
            elevation=0,
        )
        c_title = MDLabel(
            text="[b][color=#0A3871]Cobrar y Entregar Comanda[/color][/b]",
            markup=True,
            font_style="Title",
            role="medium",
            size_hint_y=None,
            height=dp(24),
        )
        c_msg = MDLabel(
            text=f"¿Cobrar [b]{format_currency(order.total)}[/b] a [b]{order.customer_name}[/b] (Comanda #{order.comanda_number}) y registrar entrega?",
            markup=True,
            font_style="Body",
            role="small",
            size_hint_y=None,
            height=dp(40),
        )
        c_btns = MDBoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(36))
        btn_cancel = create_button(
            text="Cancelar",
            style="tonal",
            size_hint=(0.4, None),
            height=dp(34),
            on_release=lambda x: self._hide_modals(),
        )
        btn_charge = create_button(
            text="Confirmar Cobro",
            icon="cash-register",
            icon_size=dp(14),
            style="filled",
            size_hint=(0.6, None),
            height=dp(34),
            on_release=lambda x, o=order: self._execute_direct_charge(o),
        )
        c_btns.add_widget(btn_cancel)
        c_btns.add_widget(btn_charge)

        self.confirm_modal.add_widget(c_title)
        self.confirm_modal.add_widget(c_msg)
        self.confirm_modal.add_widget(c_btns)

        self.root_layout.add_widget(self.confirm_modal, index=1)

    def _execute_direct_charge(self, order: Order):
        """Execute payment and mark order DELIVERED without requiring camera scanning."""
        self._hide_modals()
        success, msg, _ = self.cashier_service.process_qr_payment(order.id_pedido)
        if success:
            self.status_label.text = f"[color=#10B981]{msg}[/color]"
        else:
            self.status_label.text = f"[color=#EF4444]{msg}[/color]"
        self.refresh_orders()

    def _mark_order_ready(self, order: Order):
        """Mark comanda prepared and ready in kitchen."""
        self._hide_modals()
        self.cashier_service.mark_ready(order.id_pedido)
        self.status_label.text = f"[color=#10B981]Comanda #{order.comanda_number} lista para retiro en mesón.[/color]"
        self.refresh_orders()

    def _ask_confirm(self, order: Order):
        self._hide_modals()
        self.cashier_service.confirm_order(order.id_pedido)
        self.status_label.text = f"[color=#10B981]Comanda #{order.comanda_number} confirmada en cocina.[/color]"
        self.refresh_orders()

    def _ask_reject(self, order: Order):
        self._hide_modals()
        self.cashier_service.reject_order(order.id_pedido)
        self.status_label.text = f"[color=#EF4444]Comanda #{order.comanda_number} rechazada y saldo devuelto.[/color]"
        self.refresh_orders()

    def _hide_modals(self):
        self._stop_camera()
        if hasattr(self, "scroll") and self.scroll:
            self.scroll.opacity = 1
            self.scroll.size_hint_y = 1
            self.scroll.disabled = False
        if self.scanner_modal and self.scanner_modal in self.root_layout.children:
            self.root_layout.remove_widget(self.scanner_modal)
            self.scanner_modal = None
        if self.confirm_modal and self.confirm_modal in self.root_layout.children:
            self.root_layout.remove_widget(self.confirm_modal)
            self.confirm_modal = None
