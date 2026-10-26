"""Generator for the Student Oral Defense and Study Guide PDF using PyCairo."""

import os
import cairo

PDF_FILENAME = "guia_estudio_defensa_oral.pdf"
PAGE_WIDTH = 595.27  # A4 width in points
PAGE_HEIGHT = 841.89 # A4 height in points
MARGIN_X = 42.0
MARGIN_Y = 44.0
CONTENT_WIDTH = PAGE_WIDTH - 2 * MARGIN_X

# Executive Color Palette
COLOR_NAVY = (0.04, 0.22, 0.44)       # #0A3871 UCT Navy Blue
COLOR_SKY = (0.01, 0.53, 0.82)        # #0288D1 Accent Blue
COLOR_DARK = (0.12, 0.16, 0.23)       # #1E293B Dark Charcoal
COLOR_MUTED = (0.39, 0.45, 0.55)      # #64748B Slate Grey
COLOR_BG_CARD = (0.97, 0.98, 0.99)    # #F8FAFC Off-white
COLOR_CODE_BG = (0.94, 0.96, 0.98)    # #F1F5F9 Soft code background
COLOR_BORDER = (0.84, 0.88, 0.93)     # #D6DFE8 Border
COLOR_GREEN = (0.06, 0.65, 0.45)      # #10B981 Emerald
COLOR_AMBER = (0.85, 0.47, 0.02)      # #D97706 Warm Amber
COLOR_PURPLE = (0.49, 0.23, 0.93)     # #7C3AED Violet
COLOR_WHITE = (1.0, 1.0, 1.0)


class StudyGuideRenderer:
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
        ctx.set_source_rgb(*COLOR_AMBER)
        ctx.rectangle(MARGIN_X, 22, CONTENT_WIDTH, 2.5)
        ctx.fill()

        ctx.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(8.5)
        ctx.set_source_rgb(*COLOR_NAVY)
        ctx.move_to(MARGIN_X, 17)
        ctx.show_text("GUÍA DE ESTUDIO Y DEFENSA ORAL — PRONTO CASINO UCT")

        ctx.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(8.5)
        ctx.set_source_rgb(*COLOR_MUTED)
        ctx.move_to(MARGIN_X + 270, 17)
        ctx.show_text("|  Preparación Técnica para Evaluación Docente")

        ver_text = "Jorge, Yeremi y Renato"
        x_ext = ctx.text_extents(ver_text)
        ctx.move_to(PAGE_WIDTH - MARGIN_X - x_ext.width, 17)
        ctx.show_text(ver_text)

        self.cursor_y = MARGIN_Y + 8

    def _draw_footer(self):
        ctx = self.ctx
        y_pos = PAGE_HEIGHT - 26

        ctx.set_source_rgb(*COLOR_BORDER)
        ctx.set_line_width(0.75)
        ctx.move_to(MARGIN_X, y_pos - 8)
        ctx.line_to(PAGE_WIDTH - MARGIN_X, y_pos - 8)
        ctx.stroke()

        ctx.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(8.0)
        ctx.set_source_rgb(*COLOR_MUTED)
        ctx.move_to(MARGIN_X, y_pos + 6)
        ctx.show_text("Material de Preparación para la Defensa de 15 Minutos (5 min demo + 10 min preguntas) — UCT")

        page_str = f"Página {self.current_page} de {self.total_pages}"
        ext = ctx.text_extents(page_str)
        ctx.move_to(PAGE_WIDTH - MARGIN_X - ext.width, y_pos + 6)
        ctx.show_text(page_str)

    def draw_cover_header(self):
        ctx = self.ctx
        ctx.set_source_rgb(*COLOR_NAVY)
        ctx.rectangle(MARGIN_X, MARGIN_Y, CONTENT_WIDTH, 92)
        ctx.fill()

        ctx.set_source_rgb(*COLOR_AMBER)
        ctx.rectangle(MARGIN_X, MARGIN_Y + 88, CONTENT_WIDTH, 4)
        ctx.fill()

        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.18)
        ctx.rectangle(MARGIN_X + 16, MARGIN_Y + 12, 215, 16)
        ctx.fill()

        ctx.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(8.0)
        ctx.set_source_rgb(*COLOR_WHITE)
        ctx.move_to(MARGIN_X + 22, MARGIN_Y + 23)
        ctx.show_text("MATERIAL DE ESTUDIO PARA DEFENSA ORAL")

        ctx.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(17)
        ctx.move_to(MARGIN_X + 16, MARGIN_Y + 52)
        ctx.show_text("Guía Técnica de Defensa y Demostración en Vivo")

        ctx.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(9.5)
        ctx.set_source_rgba(1.0, 1.0, 1.0, 0.90)
        ctx.move_to(MARGIN_X + 16, MARGIN_Y + 72)
        ctx.show_text("Respuestas Clave, Paso a Paso de la Demo y Explicación del Código Modificado")

        self.cursor_y = MARGIN_Y + 104

    def draw_section_title(self, number_str, title_str):
        ctx = self.ctx
        self.cursor_y += 8

        if self.cursor_y > PAGE_HEIGHT - 95:
            self.new_page()

        badge_w = 22
        badge_h = 16
        ctx.set_source_rgb(*COLOR_NAVY)
        ctx.rectangle(MARGIN_X, self.cursor_y - 12, badge_w, badge_h)
        ctx.fill()

        ctx.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(9.0)
        ctx.set_source_rgb(*COLOR_WHITE)
        ext = ctx.text_extents(number_str)
        ctx.move_to(MARGIN_X + (badge_w - ext.width) / 2, self.cursor_y - 0.5)
        ctx.show_text(number_str)

        ctx.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(11.5)
        ctx.set_source_rgb(*COLOR_NAVY)
        ctx.move_to(MARGIN_X + badge_w + 8, self.cursor_y)
        ctx.show_text(title_str)

        ctx.set_source_rgb(*COLOR_BORDER)
        ctx.set_line_width(0.75)
        ctx.move_to(MARGIN_X, self.cursor_y + 5)
        ctx.line_to(PAGE_WIDTH - MARGIN_X, self.cursor_y + 5)
        ctx.stroke()

        self.cursor_y += 14

    def draw_paragraph(self, text, font_size=8.6, is_italic=False, color=COLOR_DARK, line_spacing=11.8):
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

    def draw_card(self, title, items, tag=None, tag_color=COLOR_SKY):
        ctx = self.ctx
        card_inner_w = CONTENT_WIDTH - 28
        line_h = 11.5

        processed_items = []
        total_item_lines = 0

        for key, desc in items:
            key_prefix = f"• {key}:"
            ctx.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(8.3)
            key_w = ctx.text_extents(key_prefix).width + 4.5

            avail_first_w = max(40.0, card_inner_w - key_w)
            subsequent_indent = 12.0
            avail_subsequent_w = card_inner_w - subsequent_indent

            ctx.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            ctx.set_font_size(8.3)

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

        card_h = 22 + (total_item_lines * line_h) + (len(items) * 2.5) + 6

        if self.cursor_y + card_h > PAGE_HEIGHT - 55:
            self.new_page()

        card_y = self.cursor_y

        ctx.set_source_rgb(*COLOR_BG_CARD)
        ctx.rectangle(MARGIN_X, card_y, CONTENT_WIDTH, card_h)
        ctx.fill()

        ctx.set_source_rgb(*COLOR_BORDER)
        ctx.set_line_width(0.75)
        ctx.rectangle(MARGIN_X, card_y, CONTENT_WIDTH, card_h)
        ctx.stroke()

        ctx.set_source_rgb(*tag_color)
        ctx.rectangle(MARGIN_X, card_y, 3.5, card_h)
        ctx.fill()

        ctx.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(9.5)
        ctx.set_source_rgb(*COLOR_NAVY)
        ctx.move_to(MARGIN_X + 12, card_y + 15)
        ctx.show_text(title)

        if tag:
            ctx.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(7.0)
            ext = ctx.text_extents(tag)
            pill_w = ext.width + 10
            pill_x = PAGE_WIDTH - MARGIN_X - pill_w - 8
            pill_y = card_y + 6

            ctx.set_source_rgb(0.91, 0.95, 0.99)
            ctx.rectangle(pill_x, pill_y, pill_w, 12)
            ctx.fill()
            ctx.set_source_rgb(*COLOR_BORDER)
            ctx.set_line_width(0.5)
            ctx.rectangle(pill_x, pill_y, pill_w, 12)
            ctx.stroke()

            ctx.set_source_rgb(*tag_color)
            ctx.move_to(pill_x + 5, pill_y + 9)
            ctx.show_text(tag)

        curr_y = card_y + 28
        for key_prefix, key_w, lines in processed_items:
            for line_idx, line_text in enumerate(lines):
                if line_idx == 0:
                    ctx.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
                    ctx.set_font_size(8.3)
                    ctx.set_source_rgb(*COLOR_DARK)
                    ctx.move_to(MARGIN_X + 12, curr_y)
                    ctx.show_text(key_prefix)

                    ctx.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                    ctx.set_font_size(8.3)
                    ctx.set_source_rgb(*COLOR_MUTED)
                    ctx.move_to(MARGIN_X + 12 + key_w, curr_y)
                    ctx.show_text(line_text)
                else:
                    ctx.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                    ctx.set_font_size(8.3)
                    ctx.set_source_rgb(*COLOR_MUTED)
                    ctx.move_to(MARGIN_X + 12 + 10, curr_y)
                    ctx.show_text(line_text)

                curr_y += line_h
            curr_y += 2.5

        self.cursor_y = card_y + card_h + 8

    def draw_table(self, headers, rows, col_widths):
        ctx = self.ctx
        row_h = 15.5
        header_h = 17.0
        table_h = header_h + (len(rows) * row_h)

        if self.cursor_y + table_h > PAGE_HEIGHT - 55:
            self.new_page()

        start_y = self.cursor_y

        ctx.set_source_rgb(*COLOR_NAVY)
        ctx.rectangle(MARGIN_X, start_y, CONTENT_WIDTH, header_h)
        ctx.fill()

        ctx.select_font_face("Helvetica", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(8.0)
        ctx.set_source_rgb(*COLOR_WHITE)

        cur_x = MARGIN_X + 8
        for i, header in enumerate(headers):
            ctx.move_to(cur_x, start_y + 11.5)
            ctx.show_text(header)
            cur_x += col_widths[i]

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

                ctx.move_to(cur_x, cur_y + 11.0)
                max_w = col_widths[c_idx] - 8
                cell_str = str(cell)
                if ctx.text_extents(cell_str).width > max_w:
                    while ctx.text_extents(cell_str + "…").width > max_w and len(cell_str) > 3:
                        cell_str = cell_str[:-1]
                    cell_str += "…"
                ctx.show_text(cell_str)
                cur_x += col_widths[c_idx]

            cur_y += row_h

        ctx.set_source_rgb(*COLOR_BORDER)
        ctx.set_line_width(0.75)
        ctx.rectangle(MARGIN_X, start_y, CONTENT_WIDTH, table_h)
        ctx.stroke()

        self.cursor_y = cur_y + 10

    def finish(self):
        self._draw_footer()
        self.surface.finish()


def build_study_guide():
    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        PDF_FILENAME
    )
    renderer = StudyGuideRenderer(output_path)

    # ====================================================
    # PÁGINA 1: Introducción y Resumen de Cambios Técnicos
    # ====================================================
    renderer.draw_cover_header()

    renderer.draw_card(
        "Objetivo de esta Guía de Estudio",
        [
            ("Propósito", "Preparar a Jorge Mendoza, Yeremi Navarro y Renato Escarate para rendir con excelencia la defensa oral presencial de 15 minutos (5 min demo + 10 min preguntas cruzadas)."),
            ("Enfoque", "Explicar con total claridad qué se modificó en el código, cómo funciona cada patrón y cómo argumentar frente al docente para obtener la nota máxima (5/5 pts en los 5 criterios)."),
        ],
        tag="DEFENSA ORAL",
        tag_color=COLOR_AMBER,
    )

    renderer.draw_section_title("1", "Resumen de los Cambios Implementados en el Código")
    renderer.draw_paragraph(
        "Para responder a los requisitos obligatorios de la pauta, se realizaron 5 intervenciones técnicas estratégicas en el código:"
    )

    renderer.draw_card(
        "Mapa de Archivos Modificados e Intervenciones",
        [
            ("1. punto_casino/models/product.py", "Se implementaron los métodos to_dict() y from_dict(). to_dict() transforma el objeto Producto en un diccionario estándar de Python listo para JSON. from_dict() permite reconstruir el objeto tipado."),
            ("2. punto_casino/models/order.py", "Se dotó a Order y OrderItem de to_dict() y from_dict(). to_dict() maneja fechas complejas convirtiendo created_at en string estándar con .isoformat() y serializa la lista de ítems de forma anidada."),
            ("3. punto_casino/repositories/product_repository.py", "Se evolucionó a JsonProductRepository. Ahora lee y escribe de forma permanente en data/productos.json usando with open(..., encoding='utf-8') y json.dump(indent=4)/json.load()."),
            ("4. punto_casino/repositories/order_repository.py", "Se implementó JsonOrderRepository. Guarda y sincroniza todas las comandas en data/pedidos.json. Mide el tiempo de I/O en disco con time.perf_counter()."),
            ("5. punto_casino/services/order_service.py", "En get_accounting_report() se integró NumPy (np.mean, np.median, np.std) para calcular la media, mediana y dispersión del ticket de compra, junto con telemetría de milisegundos."),
            ("6. punto_casino/views/screens/admin_screen.py", "En la pantalla de Administrador se agregaron 3 badges visuales que muestran la Mediana (NumPy), Desv. Estándar (NumPy) y el tiempo de cómputo en ms."),
            ("7. tests/test_domain.py", "Se añadieron 4 pruebas unitarias automatizadas (13 en total, 100% aprobadas) que validan to_dict(), from_dict(), persistencia JSON y cálculos NumPy."),
        ],
        tag="CAMBIOS TÉCNICOS",
        tag_color=COLOR_NAVY,
    )

    # ====================================================
    # PÁGINA 2: Guión Paso a Paso para la Demostración en Vivo
    # ====================================================
    renderer.new_page()
    renderer.draw_section_title("2", "Guión de la Demostración en Vivo (5 Minutos)")
    renderer.draw_paragraph(
        "La pauta de evaluación exige explícitamente: 'Demostración en Vivo (5 min): El grupo ejecuta la app, demuestra la carga inicial "
        "desde el JSON, registra un nuevo elemento (evidenciando la fecha automática) y comprueba la actualización del archivo en disco.' "
        "Sigan este guión exacto frente al profesor:"
    )

    renderer.draw_card(
        "Paso 1: Evidenciar el Fichero JSON en VS Code antes de Abrir la App (30 seg)",
        [
            ("Acción", "Abran VS Code y muestren la carpeta 'data/'. Abran el archivo 'data/pedidos.json'."),
            ("Qué decirle al profesor", "'Profesor, aquí en data/pedidos.json tenemos almacenadas las comandas en formato estructurado JSON. Fíjese en el último pedido registrado (ej: comanda #107) y que cada registro incluye su timestamp ISO.'"),
        ],
        tag="PASO 1",
        tag_color=COLOR_SKY,
    )

    renderer.draw_card(
        "Paso 2: Ejecutar la App y Demostrar la Carga Inicial (1 min)",
        [
            ("Acción", "Ejecuten en la terminal: './kivy_env/bin/python3 main.py' (o desde VS Code con F5)."),
            ("Qué decirle al profesor", "'Al iniciar, la app ejecuta JsonProductRepository y JsonOrderRepository, que leen con json.load() y with open(..., encoding=\"utf-8\") los datos en disco, reconstruyendo los objetos con from_dict().'"),
            ("En pantalla", "Hagan login rápido como 'Estudiante' o 'Cajero' y muestren que las comandas y platos ya están cargados."),
        ],
        tag="PASO 2",
        tag_color=COLOR_SKY,
    )

    renderer.draw_card(
        "Paso 3: Registrar un Nuevo Pedido y Evidenciar Fecha Automática (1.5 min)",
        [
            ("Acción", "Entren como Estudiante -> Catálogo -> Agreguen un plato (ej. 'Pastel de Choclo') al carrito -> Toquen 'Pagar' -> Seleccionen 'Beca BAES JUNAEB'."),
            ("Qué mostrar en la UI", "La comanda se genera de inmediato con un nuevo número correlativo (#108), estado CONFIRMED y marca de tiempo automática generada con datetime.now() visible en la tarjeta (ej. 14:48 hrs)."),
            ("Qué decirle al profesor", "'El timestamp no es estático ni hardcodeado: lo asigna automáticamente la entidad Order al instanciarse en la capa de modelos.'"),
        ],
        tag="PASO 3",
        tag_color=COLOR_GREEN,
    )

    renderer.draw_card(
        "Paso 4: Comprobar la Actualización Inmediata del Archivo en Disco (1 min)",
        [
            ("Acción", "Vuelvan a la ventana de VS Code con 'data/pedidos.json' abierto y bajen hasta el final del archivo."),
            ("Qué mostrar", "El nuevo pedido #108 aparece escrito en el JSON con su id_pedido, items, created_at y total."),
            ("Qué decirle al profesor", "'En el momento en que se completó la compra, el servicio invocó a order_repo.add(), el cual ejecutó _save_to_json() con with open() y json.dump(indent=4), persistiendo la información de forma segura.'"),
        ],
        tag="PASO 4",
        tag_color=COLOR_GREEN,
    )

    renderer.draw_card(
        "Paso 5: Mostrar la Integración de NumPy y time.perf_counter() en Admin (1 min)",
        [
            ("Acción", "En la app móvil, toquen 'Salir' e inicien sesión rápida como 'Administrador' (admin@uct.cl)."),
            ("Qué mostrar", "Muestren la tarjeta superior 'Resumen Contable del Casino'. Señalen las pastillas morada y naranja: 'Mediana (NumPy)' y 'Desv. Est. (NumPy)', además del tiempo en ms de perf_counter()."),
            ("Qué decirle al profesor", "'Aquí integramos NumPy como librería científica del stack para calcular analítica de compras en tiempo real: convertimos los totales a un arreglo vectorial NumPy y calculamos media, mediana y desviación estándar en menos de 1 ms medido con perf_counter().'"),
        ],
        tag="PASO 5",
        tag_color=COLOR_PURPLE,
    )

    # ====================================================
    # PÁGINA 3: Preguntas Técnicas del Docente y Cómo Responder
    # ====================================================
    renderer.new_page()
    renderer.draw_section_title("3", "Ronda de Preguntas Técnicas del Docente (10 Minutos)")
    renderer.draw_paragraph(
        "El docente realizará preguntas cruzadas para comprobar el dominio del código fuente. Aquí tienen las respuestas exactas:"
    )

    renderer.draw_card(
        "Pregunta 1: ¿Por qué usaron 'with open()' y qué pasa si no se usa?",
        [
            ("Respuesta recomendada", "'Usamos with open() porque implementa el patrón Context Manager en Python (__enter__ y __exit__). Garantiza que el descriptor de archivo en el sistema operativo se cierre inmediatamente al finalizar el bloque, incluso si ocurre una excepción como falta de memoria o error de parseo. Si usáramos open() simple sin with y la app crashea a mitad de escritura, el archivo queda bloqueado, los buffers no se vacían (flush) y el archivo JSON se corrompe.'"),
        ],
        tag="PREGUNTA 1",
        tag_color=COLOR_NAVY,
    )

    renderer.draw_card(
        "Pregunta 2: ¿Por qué es necesario el método to_dict() en vez de guardar el objeto directo?",
        [
            ("Respuesta recomendada", "'El serializador nativo json.dump() de Python solo sabe convertir tipos primitivos (dict, list, str, int, float, bool). Nuestras clases de dominio Product y Order contienen objetos complejos como enumeraciones (OrderStatus, PaymentMethod) e instancias datetime. El método to_dict() se encarga de transformar esos tipos complejos en representaciones primitivas estándar (como strings ISO 8601), desacoplando además el modelo de negocio del formato de almacenamiento.'"),
        ],
        tag="PREGUNTA 2",
        tag_color=COLOR_NAVY,
    )

    renderer.draw_card(
        "Pregunta 3: ¿Por qué la carpeta services/ debe estar 100% libre de Kivy?",
        [
            ("Respuesta recomendada", "'Es la base del principio de Separación de Responsabilidades (SoC) y Clean Architecture. Si la lógica de negocio importara widgets de Kivy o KivyMD, no podríamos ejecutar pruebas unitarias automáticas sin levantar ventanas gráficas, ni podríamos reutilizar la lógica de negocio en una futura versión web o de consola. Al mantener services/ en Python puro, ejecutamos tests/test_domain.py en segundos en cualquier entorno.'"),
        ],
        tag="PREGUNTA 3",
        tag_color=COLOR_NAVY,
    )

    renderer.draw_card(
        "Pregunta 4: ¿Qué función real cumple NumPy en su proyecto?",
        [
            ("Respuesta recomendada", "'NumPy no está puesto como un adorno ni en un print suelto: procesa el vector contable de ventas en la capa de servicios (get_accounting_report()). Cuando el casino tiene decenas o cientos de comandas, NumPy realiza operaciones vectorizadas en memoria en lenguaje C, calculando la mediana de consumo (que es más representativa que la media porque no se distorsiona con compras gigantes atípicas) y la desviación estándar para analizar la dispersión del gasto de los estudiantes.'"),
        ],
        tag="PREGUNTA 4",
        tag_color=COLOR_NAVY,
    )

    renderer.draw_card(
        "Pregunta 5: ¿Cómo garantizan que las fechas no se desconfiguren al guardar y leer?",
        [
            ("Respuesta recomendada", "'Al persistir, usamos created_at.isoformat(), que genera un estándar internacional sin ambigüedad horaria (YYYY-MM-DDTHH:MM:SS). Al cargar desde el JSON con from_dict(), usamos datetime.fromisoformat(), lo que reconstruye un objeto datetime formal de Python. Así podemos seguir realizando operaciones temporales como ordenar pedidos cronológicamente o calcular tiempos de espera.'"),
        ],
        tag="PREGUNTA 5",
        tag_color=COLOR_NAVY,
    )

    # ====================================================
    # PÁGINA 4: Glosario de Conceptos y Rúbrica 5/5
    # ====================================================
    renderer.new_page()
    renderer.draw_section_title("4", "Glosario Rápido de Conceptos Clave para la Defensa")
    renderer.draw_paragraph(
        "Términos técnicos que deben usar con naturalidad durante su exposición oral:"
    )

    renderer.draw_card(
        "Vocabulario Técnico Esencial",
        [
            ("SoC (Separation of Concerns)", "Separación de responsabilidades: dividir el programa en módulos donde cada uno tiene una única razón para cambiar (UI en views, lógica en services, datos en models/repos)."),
            ("Serialización", "Proceso de convertir un objeto en memoria (instancia de clase) a un formato de texto transmisible o almacenable (JSON) mediante to_dict(). Deserialización es el proceso inverso con from_dict()."),
            ("Context Manager (with open)", "Protocolo de Python que asegura la adquisición y liberación determinista de recursos del sistema operativo."),
            ("UTF-8 (encoding)", "Codificación de caracteres estándar que asegura que tildes, ñ y caracteres en español se guarden y lean sin romper el archivo ni mostrar caracteres extraños (mojibake)."),
            ("Vectorización (NumPy)", "Capacidad de aplicar operaciones matemáticas sobre arreglos continuos de memoria sin usar bucles for manuales en Python, alcanzando velocidades nativas de C."),
            ("time.perf_counter()", "Reloj monotónico de alta resolución en Python diseñado específicamente para medir intervalos de tiempo de ejecución sin verse afectado por ajustes del reloj del sistema."),
        ],
        tag="GLOSARIO",
        tag_color=COLOR_NAVY,
    )

    renderer.draw_section_title("5", "Estrategia para Obtener 5/5 en Cada Criterio de la Rúbrica")

    renderer.draw_table(
        ["Criterio de Evaluación", "Qué exige la Rúbrica para Excelente (5 pts)", "Cómo lo demostramos en la app"],
        [
            ("Arquitectura Modular (SoC)", "Estructura impecable (views, services, models) con separación total.", "Mostrar carpetas; services/ tiene 0 imports de Kivy; main.py solo orquesta."),
            ("Persistencia JSON y POO", "Clases POO robustas con to_dict() y persistencia limpia json.dump/load.", "Mostrar Product y Order con to_dict(), y la creación en vivo en data/pedidos.json."),
            ("Manejo de Ficheros y Fechas", "Uso correcto de with open(encoding='utf-8') y timestamps automáticos.", "Mostrar el código de _save_to_json() con with open y fecha ISO generada por datetime.now()."),
            ("Librería Adicional", "Librería adicional integrada aportando valor real al flujo de la app.", "Mostrar en pantalla Admin la Mediana y Desv. Est. calculadas con NumPy y perf_counter()."),
            ("Informe Técnico y Defensa", "Informe técnico impecable y dominio total del código en la defensa.", "Entregar el PDF de 5 páginas y responder las preguntas con este guión."),
        ],
        [100, 190, 220]
    )

    renderer.draw_card(
        "Consejo Final para el Equipo",
        [
            ("División del Equipo", "Jorge puede abrir la demo e introducir la arquitectura (SoC); Yeremi puede explicar el modelado POO, to_dict() y el guardado en JSON; Renato puede explicar la analítica con NumPy y los timestamps."),
            ("Seguridad y Confianza", "El proyecto cuenta con 13 pruebas unitarias aprobadas, código limpio y dos informes formales. ¡Tienen todo listo para obtener la nota máxima!"),
        ],
        tag="¡ÉXITO EN LA DEFENSA!",
        tag_color=COLOR_GREEN,
    )

    renderer.finish()
    print(f"Guía de estudio generada exitosamente en: {output_path}")


if __name__ == "__main__":
    build_study_guide()
