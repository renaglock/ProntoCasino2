"""Script to generate a pristine, professionally formatted PDF report on Pronto Casino architecture using PyCairo."""

import os
import cairo

PDF_FILENAME = "informe_arquitectura_pronto_casino.pdf"
PAGE_WIDTH = 595.27  # A4 width in points
PAGE_HEIGHT = 841.89 # A4 height in points
MARGIN_X = 45.0
MARGIN_Y = 48.0
CONTENT_WIDTH = PAGE_WIDTH - 2 * MARGIN_X

# Color definitions (RGB 0.0 - 1.0)
COLOR_NAVY = (0.04, 0.22, 0.44)       # #0A3871
COLOR_SKY = (0.01, 0.53, 0.82)        # #0288D1
COLOR_DARK = (0.12, 0.16, 0.23)       # #1E293B
COLOR_MUTED = (0.39, 0.45, 0.55)      # #64748B
COLOR_BG_CARD = (0.97, 0.98, 0.99)    # #F8FAFC
COLOR_BORDER = (0.86, 0.89, 0.93)     # #DDE3EA
COLOR_GREEN = (0.06, 0.65, 0.45)      # #10B981
COLOR_WHITE = (1.0, 1.0, 1.0)
COLOR_TAG_BG = (0.91, 0.95, 0.99)     # Light navy tint


class PDFReportRenderer:
    def __init__(self, filename):
        self.filename = filename
        self.surface = cairo.PDFSurface(filename, PAGE_WIDTH, PAGE_HEIGHT)
        self.ctx = cairo.Context(self.surface)
        self.current_page = 1
        self.total_pages = 4
        self.cursor_y = MARGIN_Y

    def new_page(self):
        self._draw_footer()
        self.surface.show_page()
        self.current_page += 1
        self.cursor_y = MARGIN_Y
        self._draw_header()

    def _draw_header(self):
        ctx = self.ctx
        # Top banner line
        ctx.set_source_rgb(*COLOR_NAVY)
        ctx.rectangle(MARGIN_X, 26, CONTENT_WIDTH, 2.5)
        ctx.fill()

        # Running header text
        ctx.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(8.5)
        ctx.set_source_rgb(*COLOR_NAVY)
        ctx.move_to(MARGIN_X, 20)
        ctx.show_text("PRONTO CASINO UCT")

        ctx.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(8.5)
        ctx.set_source_rgb(*COLOR_MUTED)
        sub_text = "Informe de Arquitectura y Estructura del Software"
        ctx.move_to(MARGIN_X + 105, 20)
        ctx.show_text(f"|  {sub_text}")

        ver_text = "Desarrollo Móvil — 4° Semestre"
        x_ext = ctx.text_extents(ver_text)
        ctx.move_to(PAGE_WIDTH - MARGIN_X - x_ext.width, 20)
        ctx.show_text(ver_text)

        self.cursor_y = MARGIN_Y + 12

    def _draw_footer(self):
        ctx = self.ctx
        y_pos = PAGE_HEIGHT - 28

        # Footer divider line
        ctx.set_source_rgb(*COLOR_BORDER)
        ctx.set_line_width(0.75)
        ctx.move_to(MARGIN_X, y_pos - 8)
        ctx.line_to(PAGE_WIDTH - MARGIN_X, y_pos - 8)
        ctx.stroke()

        # Footer text
        ctx.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(8.0)
        ctx.set_source_rgb(*COLOR_MUTED)
        ctx.move_to(MARGIN_X, y_pos + 6)
        ctx.show_text("Pronto Casino Universidad — Plataforma Móvil Empresarial en Python y KivyMD")

        # Page numbering
        page_str = f"Página {self.current_page} de {self.total_pages}"
        ext = ctx.text_extents(page_str)
        ctx.move_to(PAGE_WIDTH - MARGIN_X - ext.width, y_pos + 6)
        ctx.show_text(page_str)

    def draw_cover_header(self):
        ctx = self.ctx
        # Top banner background block
        ctx.set_source_rgb(*COLOR_NAVY)
        ctx.rectangle(MARGIN_X, MARGIN_Y, CONTENT_WIDTH, 84)
        ctx.fill()

        # Accent sky blue bar
        ctx.set_source_rgb(*COLOR_SKY)
        ctx.rectangle(MARGIN_X, MARGIN_Y + 80, CONTENT_WIDTH, 4)
        ctx.fill()

        # Tag pill inside banner
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.18)
        ctx.rectangle(MARGIN_X + 16, MARGIN_Y + 12, 160, 16)
        ctx.fill()

        ctx.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(8.5)
        ctx.set_source_rgb(*COLOR_WHITE)
        ctx.move_to(MARGIN_X + 22, MARGIN_Y + 23)
        ctx.show_text("DESARROLLO MÓVIL • 4° SEMESTRE")

        # Main Title
        ctx.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(18)
        ctx.move_to(MARGIN_X + 16, MARGIN_Y + 50)
        ctx.show_text("Informe de Arquitectura y Estructura del Código")

        # Subtitle
        ctx.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(10.0)
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.90)
        ctx.move_to(MARGIN_X + 16, MARGIN_Y + 69)
        ctx.show_text("Plataforma Móvil 'Pronto Casino UCT' — Guía Técnica para Defensa Académica")

        self.cursor_y = MARGIN_Y + 100

    def draw_section_title(self, number_str, title_str):
        ctx = self.ctx
        self.cursor_y += 10

        if self.cursor_y > PAGE_HEIGHT - 95:
            self.new_page()

        # Icon/badge box
        badge_w = 20
        badge_h = 16
        ctx.set_source_rgb(*COLOR_NAVY)
        ctx.rectangle(MARGIN_X, self.cursor_y - 12, badge_w, badge_h)
        ctx.fill()

        ctx.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(9.5)
        ctx.set_source_rgb(*COLOR_WHITE)
        ext = ctx.text_extents(number_str)
        ctx.move_to(MARGIN_X + (badge_w - ext.width) / 2, self.cursor_y - 0.5)
        ctx.show_text(number_str)

        # Title text
        ctx.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(12)
        ctx.set_source_rgb(*COLOR_NAVY)
        ctx.move_to(MARGIN_X + badge_w + 8, self.cursor_y)
        ctx.show_text(title_str)

        # Thin rule under title
        ctx.set_source_rgb(*COLOR_BORDER)
        ctx.set_line_width(0.8)
        ctx.move_to(MARGIN_X, self.cursor_y + 5)
        ctx.line_to(PAGE_WIDTH - MARGIN_X, self.cursor_y + 5)
        ctx.stroke()

        self.cursor_y += 15

    def draw_paragraph(self, text, font_size=8.8, is_italic=False, color=COLOR_DARK, line_spacing=12.0):
        ctx = self.ctx
        ctx.select_font_face(
            "Helvetica",
            cairo.FONT_SLANT_ITALIC if is_italic else cairo.FONT_SLANT_NORMAL,
            cairo.FONT_WEIGHT_NORMAL
        )
        ctx.set_font_size(font_size)
        ctx.set_source_rgb(*color)

        words = text.split(" ")
        current_line = []
        for word in words:
            test_line = " ".join(current_line + [word])
            ext = ctx.text_extents(test_line)
            if ext.width > CONTENT_WIDTH - 4:
                if self.cursor_y > PAGE_HEIGHT - 65:
                    self.new_page()
                ctx.move_to(MARGIN_X, self.cursor_y)
                ctx.show_text(" ".join(current_line))
                self.cursor_y += line_spacing
                current_line = [word]
            else:
                current_line.append(word)

        if current_line:
            if self.cursor_y > PAGE_HEIGHT - 65:
                self.new_page()
            ctx.move_to(MARGIN_X, self.cursor_y)
            ctx.show_text(" ".join(current_line))
            self.cursor_y += line_spacing

    def _wrap_text_lines(self, text, max_width, font_size=8.5):
        """Helper to break a text into wrapped lines fitting within max_width."""
        ctx = self.ctx
        ctx.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(font_size)

        words = text.split(" ")
        lines = []
        curr = []
        for w in words:
            cand = " ".join(curr + [w])
            if ctx.text_extents(cand).width > max_width and curr:
                lines.append(" ".join(curr))
                curr = [w]
            else:
                curr.append(w)
        if curr:
            lines.append(" ".join(curr))
        return lines

    def draw_card(self, title, items, tag=None, tag_color=COLOR_SKY):
        """Draw an outlined card with multi-line word wrapping and hanging indents."""
        ctx = self.ctx
        card_inner_w = CONTENT_WIDTH - 28 # margins inside card
        line_h = 12.0

        # Calculate exact card height by pre-wrapping all item descriptions
        processed_items = []
        total_item_lines = 0

        for key, desc in items:
            key_prefix = f"• {key}:"
            ctx.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(8.5)
            key_w = ctx.text_extents(key_prefix).width + 4.5  # Add generous gap

            # Remaining width for the first line of description
            avail_first_w = max(40.0, card_inner_w - key_w)
            subsequent_indent = 14.0
            avail_subsequent_w = card_inner_w - subsequent_indent

            # Word wrap description
            ctx.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            ctx.set_font_size(8.5)

            words = desc.split(" ")
            lines = []
            curr = []
            is_first_line = True
            target_w = avail_first_w

            for w in words:
                cand = " ".join(curr + [w])
                if ctx.text_extents(cand).width > target_w and curr:
                    lines.append(" ".join(curr))
                    curr = [w]
                    is_first_line = False
                    target_w = avail_subsequent_w
                else:
                    curr.append(w)
            if curr:
                lines.append(" ".join(curr))

            processed_items.append((key_prefix, key_w, lines))
            total_item_lines += len(lines)

        card_h = 24 + (total_item_lines * line_h) + (len(items) * 3) + 6

        if self.cursor_y + card_h > PAGE_HEIGHT - 55:
            self.new_page()

        card_y = self.cursor_y

        # Background fill
        ctx.set_source_rgb(*COLOR_BG_CARD)
        ctx.rectangle(MARGIN_X, card_y, CONTENT_WIDTH, card_h)
        ctx.fill()

        # Border
        ctx.set_source_rgb(*COLOR_BORDER)
        ctx.set_line_width(0.75)
        ctx.rectangle(MARGIN_X, card_y, CONTENT_WIDTH, card_h)
        ctx.stroke()

        # Left accent stripe
        ctx.set_source_rgb(*tag_color)
        ctx.rectangle(MARGIN_X, card_y, 3.5, card_h)
        ctx.fill()

        # Card Title
        ctx.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(10.0)
        ctx.set_source_rgb(*COLOR_NAVY)
        ctx.move_to(MARGIN_X + 14, card_y + 16)
        ctx.show_text(title)

        # Optional Tag pill
        if tag:
            ctx.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(7.5)
            ext = ctx.text_extents(tag)
            pill_w = ext.width + 12
            pill_x = PAGE_WIDTH - MARGIN_X - pill_w - 10
            pill_y = card_y + 7

            ctx.set_source_rgb(*COLOR_TAG_BG)
            ctx.rectangle(pill_x, pill_y, pill_w, 13)
            ctx.fill()
            ctx.set_source_rgb(*COLOR_BORDER)
            ctx.set_line_width(0.6)
            ctx.rectangle(pill_x, pill_y, pill_w, 13)
            ctx.stroke()

            ctx.set_source_rgb(*tag_color)
            ctx.move_to(pill_x + 6, pill_y + 9.5)
            ctx.show_text(tag)

        # Render items
        curr_y = card_y + 29
        for key_prefix, key_w, lines in processed_items:
            for line_idx, line_text in enumerate(lines):
                if line_idx == 0:
                    # Draw bold key prefix
                    ctx.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
                    ctx.set_font_size(8.5)
                    ctx.set_source_rgb(*COLOR_DARK)
                    ctx.move_to(MARGIN_X + 14, curr_y)
                    ctx.show_text(key_prefix)

                    # Draw first line of description
                    ctx.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                    ctx.set_font_size(8.5)
                    ctx.set_source_rgb(*COLOR_MUTED)
                    ctx.move_to(MARGIN_X + 14 + key_w, curr_y)
                    ctx.show_text(line_text)
                else:
                    # Subsequent line with hanging indent
                    ctx.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                    ctx.set_font_size(8.5)
                    ctx.set_source_rgb(*COLOR_MUTED)
                    ctx.move_to(MARGIN_X + 14 + 12, curr_y)
                    ctx.show_text(line_text)

                curr_y += line_h
            curr_y += 3

        self.cursor_y = card_y + card_h + 8

    def draw_table(self, headers, rows, col_widths):
        """Draw a professional structured table with proper cell padding."""
        ctx = self.ctx
        row_h = 16.5
        header_h = 18.0
        table_h = header_h + (len(rows) * row_h)

        if self.cursor_y + table_h > PAGE_HEIGHT - 55:
            self.new_page()

        start_y = self.cursor_y

        # Header background
        ctx.set_source_rgb(*COLOR_NAVY)
        ctx.rectangle(MARGIN_X, start_y, CONTENT_WIDTH, header_h)
        ctx.fill()

        # Header text
        ctx.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(8.2)
        ctx.set_source_rgb(*COLOR_WHITE)

        cur_x = MARGIN_X + 8
        for i, header in enumerate(headers):
            ctx.move_to(cur_x, start_y + 12.0)
            ctx.show_text(header)
            cur_x += col_widths[i]

        # Rows
        cur_y = start_y + header_h
        for r_idx, row in enumerate(rows):
            if r_idx % 2 == 1:
                ctx.set_source_rgb(*COLOR_BG_CARD)
                ctx.rectangle(MARGIN_X, cur_y, CONTENT_WIDTH, row_h)
                ctx.fill()

            ctx.set_source_rgb(*COLOR_BORDER)
            ctx.set_line_width(0.5)
            ctx.move_to(MARGIN_X, cur_y + row_h)
            ctx.line_to(PAGE_WIDTH - MARGIN_X, cur_y + row_h)
            ctx.stroke()

            cur_x = MARGIN_X + 8
            for c_idx, cell in enumerate(row):
                if c_idx == 0:
                    ctx.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
                    ctx.set_font_size(7.4)
                    ctx.set_source_rgb(*COLOR_DARK)
                else:
                    ctx.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                    ctx.set_font_size(7.4)
                    ctx.set_source_rgb(*COLOR_MUTED)

                ctx.move_to(cur_x, cur_y + 11.5)
                # Clip cell if needed
                max_w = col_widths[c_idx] - 10
                cell_str = str(cell)
                if ctx.text_extents(cell_str).width > max_w:
                    while ctx.text_extents(cell_str + "…").width > max_w and len(cell_str) > 3:
                        cell_str = cell_str[:-1]
                    cell_str += "…"
                ctx.show_text(cell_str)
                cur_x += col_widths[c_idx]

            cur_y += row_h

        # Outer border
        ctx.set_source_rgb(*COLOR_BORDER)
        ctx.set_line_width(0.75)
        ctx.rectangle(MARGIN_X, start_y, CONTENT_WIDTH, table_h)
        ctx.stroke()

        self.cursor_y = cur_y + 10

    def finish(self):
        self._draw_footer()
        self.surface.finish()


def build_pdf():
    renderer = PDFReportRenderer(PDF_FILENAME)

    # ----------------------------------------------------
    # PÁGINA 1: Portada, Problema/Solución y Clean Architecture
    # ----------------------------------------------------
    renderer.draw_cover_header()

    renderer.draw_section_title("1", "Propósito del Proyecto y Problema Resuelto")
    renderer.draw_paragraph(
        "Pronto Casino UCT es una solución de ingeniería de software móvil diseñada para optimizar de forma integral "
        "el flujo de reservas, comandas y retiros rápidos en recintos de alimentación universitaria. Resuelve de raíz "
        "las aglomeraciones críticas en horarios punta (12:30 a 14:30 hrs), los tiempos muertos en filas de espera, "
        "los descuadres manuales de caja y el desperdicio de comida mediante la sincronización digital en tiempo real "
        "entre estudiantes, personal de cocina, cajeros y administradores."
    )

    renderer.draw_section_title("2", "Patrón Arquitectónico: Clean Architecture")
    renderer.draw_paragraph(
        "El código no mezcla la interfaz con la base de datos. Se encuentra estructurado bajo los principios de Clean Architecture "
        "y separación estricta de responsabilidades (SoC). La comunicación viaja en una sola dirección: la interfaz gráfica "
        "dispara eventos hacia la capa de servicios, los servicios ejecutan las reglas del negocio y se comunican con los "
        "repositorios, y los repositorios ejecutan consultas parametrizadas sobre SQLite."
    )

    # Architecture Table
    headers = ["Capa de Software", "Ubicación en Código", "Responsabilidad Principal", "Tecnología"]
    rows = [
        ["1. Presentación (UI)", "punto_casino/views/", "Pantallas, componentes visuales, eventos táctiles", "KivyMD 2.0 / M3"],
        ["2. Servicios / Negocio", "punto_casino/services/", "Lógica de pedidos, RBAC, hash criptográfico, KPIs", "Python 3.12 Estándar"],
        ["3. Repositorios / Datos", "punto_casino/repositories/", "Persistencia en SQLite WAL, consultas SQL preparadas", "SQLite3 WAL Mode"],
        ["4. Dominio / Entidades", "punto_casino/models/", "Definición pura de datos (Product, Order, User)", "Python Dataclasses"],
        ["5. Núcleo y Utilidades", "punto_casino/core & utils/", "Configuraciones globales, QR en RAM, formato CLP", "OpenGL Texture / SII"]
    ]
    col_widths = [105, 125, 175, 100]
    renderer.draw_table(headers, rows, col_widths)

    renderer.draw_section_title("3", "Punto de Entrada de la Aplicación (main.py)")
    renderer.draw_paragraph(
        "El archivo main.py actúa como el orquestador central (Composition Root) del sistema. Cumple 4 roles fundamentales:"
    )
    renderer.draw_card(
        "Responsabilidades de main.py (ProntoCasinoApp)",
        [
            ("Resolución Móvil", "Fija la ventana a 380x720 dp (Smartphone Canvas) con adaptación responsiva hasta 360x640 dp."),
            ("Inyección de Dependencias", "Instancia la base de datos, repositorios y servicios pasándolos a cada pantalla."),
            ("Gestor de Pantallas (MDScreenManager)", "Administra la navegación fluida con transiciones sin reconstruir el árbol de widgets."),
            ("Barra Superior Institucional", "Muestra la identidad UCT (#0A3871), el usuario activo y botón de cierre de sesión.")
        ],
        tag="ORQUESTADOR",
        tag_color=COLOR_NAVY
    )

    # ----------------------------------------------------
    # PÁGINA 2: Dominio, Repositorios y Servicios de Negocio
    # ----------------------------------------------------
    renderer.new_page()

    renderer.draw_section_title("4", "Capa de Dominio y Modelos (punto_casino/models/)")
    renderer.draw_paragraph(
        "Contiene entidades puras que representan el negocio gastronómico universitario sin dependencias externas:"
    )
    renderer.draw_card(
        "Entidades del Dominio Gastronómico",
        [
            ("user.py (User & UserRole)", "Define los 4 roles del sistema: Estudiante/Funcionario (client), Invitado (guest), Cajero (cashier) y Administrador (admin)."),
            ("product.py (Product)", "Representa los platos: id_producto ('MENU-010'), nombre, categoría oficial, precio CLP, stock y estado de oferta."),
            ("order.py (Order & OrderStatus)", "Modela la comanda secuencial (#101, #102) y la máquina de estados: PENDING -> CONFIRMED -> READY -> DELIVERED.")
        ],
        tag="DOMAIN LAYER",
        tag_color=COLOR_SKY
    )

    renderer.draw_section_title("5", "Capa de Persistencia y Datos (punto_casino/repositories/)")
    renderer.draw_paragraph(
        "Aísla las operaciones SQL de la aplicación para garantizar robustez, velocidad y defensa contra inyecciones:"
    )
    renderer.draw_card(
        "Persistencia y Base de Datos SQLite",
        [
            ("database.py (DatabaseManager)", "Abre conexión con SQLite en modo WAL (Write-Ahead Logging) y PRAGMA foreign_keys = ON para alta concurrencia."),
            ("user_repository.py (UserRepository)", "Persistencia de usuarios con credenciales protegidas. Realiza consultas 100% parametrizadas (placeholders '?')."),
            ("product_repository.py", "Gestión de catálogo, actualización de stock unitario y activación/desactivación preventiva de platos."),
            ("order_repository.py", "Almacenamiento de comandas históricas, filtrado por usuario y auditoría cronológica de transacciones.")
        ],
        tag="DATA LAYER",
        tag_color=COLOR_GREEN
    )

    renderer.draw_section_title("6", "Capa de Lógica de Negocio (punto_casino/services/)")
    renderer.draw_paragraph(
        "Encapsula las reglas operativas, seguridad criptográfica y cálculo de métricas financieras del casino:"
    )
    renderer.draw_card(
        "Servicios de Aplicación y Seguridad",
        [
            ("security.py (SecurityManager)", "Hashing con PBKDF2-HMAC-SHA256 (600.000 iteraciones + sal de 32 bytes) y secrets.compare_digest."),
            ("auth_service.py (AuthService)", "Gestiona la sesión del usuario, verificación de contraseñas y validación de permisos por rol (RBAC)."),
            ("order_service.py (OrderService)", "Lógica del carrito de compras, cálculo de totales, reservas, descuentos y motor contable de KPIs."),
            ("cashier_service.py (CashierService)", "Cola de comandas de cocina en vivo, confirmación de pedidos, cobro en 1-toque y lector QR con OpenCV.")
        ],
        tag="BUSINESS LOGIC",
        tag_color=COLOR_NAVY
    )

    # ----------------------------------------------------
    # PÁGINA 3: Capa de Presentación (Vistas y Pantallas KivyMD)
    # ----------------------------------------------------
    renderer.new_page()

    renderer.draw_section_title("7", "Capa de Presentación: Pantallas (punto_casino/views/screens/)")
    renderer.draw_paragraph(
        "Cada pantalla hereda de MDScreen y representa un caso de uso específico según el rol del usuario conectado:"
    )

    renderer.draw_card(
        "1. LoginScreen (Autenticación e Ingreso)",
        [
            ("Funcionalidad", "Formulario de correo institucional y contraseña con validaciones."),
            ("Botones de Acceso Rápido", "Permite ingresar como Estudiante, Cajero, Administrador o Invitado en un solo toque para pruebas ágiles."),
            ("Seguridad Visual", "Ocultamiento de contraseña con toggle visual y retroalimentación de credenciales inválidas.")
        ],
        tag="AUTH VIEW",
        tag_color=COLOR_SKY
    )

    renderer.draw_card(
        "2. CatalogScreen (Menú del Día y Carrito)",
        [
            ("Exploración de Menú", "Filtrado por categorías: Menú Normal, Ejecutivo, Hipocalórico, Vegetariano, Rápido, Bebidas y Ofertas."),
            ("Carrito Reactivo", "Suma y resta instantánea de platos con control de stock en vivo (impide pedir sin existencias disponibles)."),
            ("Transición Cero-Latencia", "Mecanismo de 'dirty check' que evita redibujar la lista si no hubo cambios, logrando 0 ms de lag.")
        ],
        tag="CLIENT VIEW",
        tag_color=COLOR_GREEN
    )

    renderer.draw_card(
        "3. ReservationsScreen (Comandas, Retiro y Código QR)",
        [
            ("QR Dinámico en Memoria", "Genera el QR de retiro directamente como textura OpenGL en RAM, sin escribir archivos en disco."),
            ("Segregación por Rol", "Los estudiantes ven el código QR para retiro; cajeros y administradores ven la ficha ejecutiva de auditoría."),
            ("Anclaje Superior M3", "El detalle del pedido se ancla firmemente en la cabecera superior según el estándar corporativo M3.")
        ],
        tag="RESERVATIONS",
        tag_color=COLOR_NAVY
    )

    renderer.draw_card(
        "4. CashierScreen (Operación de Cocina y Caja)",
        [
            ("Cola de Comandas", "Listado en tiempo real de pedidos en cocina clasificados por estado (Pendiente, Confirmado, Listo)."),
            ("Despacho en 1-Toque", "Botón directo 'Cobrar y Entregar' para mesón rápido sin obligar a escaneo óptico si hay fila."),
            ("Escáner QR Integrado", "Permite escanear con cámara web física (OpenCV) o validar de forma simulada en escritorio.")
        ],
        tag="CASHIER VIEW",
        tag_color=COLOR_SKY
    )

    renderer.draw_card(
        "5. AdminScreen (Gestión de Platos y Métricas Contables)",
        [
            ("Gestión de Menú", "Creación y edición de platos con selector interactivo de categorías (cat_select_card) e insignias de ID."),
            ("Motor de Ofertas", "Activación de precios con descuento y etiquetas personalizadas ('Promo Alumnos', 'Por Vencer', '30% OFF')."),
            ("Analítica Financiera", "Dashboard con KPIs en CLP, ticket promedio, barra de balance operativo y ranking de platos demandados.")
        ],
        tag="ADMIN VIEW",
        tag_color=COLOR_NAVY
    )

    # ----------------------------------------------------
    # PÁGINA 4: Utilidades, Pruebas y Claves para la Defensa
    # ----------------------------------------------------
    renderer.new_page()

    renderer.draw_section_title("8", "Componentes Reutilizables y Utilidades")
    renderer.draw_card(
        "Módulos de Soporte (views/components & utils)",
        [
            ("ui_elements.py (M3NavItem)", "Barra de navegación táctil en el 100% de la superficie del tab, eliminando el efecto 'interruptor'."),
            ("Tarjetas Outlined (Sin Sombras)", "Se fuerza style='outlined' y elevation=0 para evitar artefactos negros en entornos OpenGL por software."),
            ("qr_generator.py", "Convierte matrices QR en arreglos de bytes y texturas Kivy (Texture.create) de forma 100% en memoria RAM."),
            ("formatters.py", "Formatea cifras numéricas a formato chileno oficial ($X.XXX CLP) sin decimales según normativa SII.")
        ],
        tag="COMPONENTS & UTILS",
        tag_color=COLOR_GREEN
    )

    renderer.draw_section_title("9", "Suite de Pruebas Automatizadas (tests/test_domain.py)")
    renderer.draw_paragraph(
        "El proyecto cuenta con 6 pruebas automatizadas con unittest que certifican la solidez técnica antes de cada despliegue:"
    )
    headers_t = ["Prueba Unitaria", "Flujo Evaluado", "Criterio de Aprobación"]
    rows_t = [
        ["test_auth_quick_login", "Autenticación de usuarios por rol", "Verifica retorno de sesión con perfil y correo institucional."],
        ["test_product_repository_crud", "Catálogo y control de inventario", "Valida creación de platos, conteo de stock y toggle activo/inactivo."],
        ["test_order_creation_and_cart", "Carrito reactivo y checkout", "Comprueba suma de totales, vaciado del carrito y comanda PENDING."],
        ["test_cashier_processing", "Ciclo de vida de la comanda", "Valida transición: PENDING -> CONFIRMED -> READY -> DELIVERED."],
        ["test_accounting_report", "Motor de reportería y KPIs", "Certifica recaudación CLP, ticket promedio, top platos y categorías."],
        ["test_category_palette_colors", "Consistencia visual M3", "Asegura que cada categoría de comida posea su color distintivo."]
    ]
    col_widths_t = [115, 140, 250]
    renderer.draw_table(headers_t, rows_t, col_widths_t)

    renderer.draw_section_title("10", "Puntos Clave para Explicarle al Profesor (Tips de Examen)")
    renderer.draw_paragraph(
        "Al momento de defender el proyecto frente al docente, se recomienda destacar los siguientes 4 pilares de ingeniería:"
    )
    renderer.draw_card(
        "Argumentos Técnicos de Alto Impacto",
        [
            ("1. ¿Por qué Clean Architecture?", "Explicar que la UI (KivyMD) puede reemplazarse por Flutter o React sin tocar la lógica ni los datos."),
            ("2. ¿Por qué PBKDF2 con 600k iteraciones?", "Cumple las directrices del NIST y OWASP Mobile para neutralizar ataques de fuerza bruta con GPUs."),
            ("3. ¿Por qué SQLite en modo WAL?", "Permite lecturas y escrituras simultáneas en el casino sin bloqueos de archivo (database locked)."),
            ("4. ¿Por qué QR en memoria RAM?", "Protege la memoria flash del teléfono del alumno evitando escribir y borrar imágenes temporales continuamente.")
        ],
        tag="DEFENSA ORAL",
        tag_color=COLOR_NAVY
    )

    renderer.finish()
    print(f"Informe generado exitosamente en: {PDF_FILENAME}")


if __name__ == "__main__":
    build_pdf()
