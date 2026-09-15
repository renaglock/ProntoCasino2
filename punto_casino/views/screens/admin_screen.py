"""Admin screen with full professional CRUD and action confirmation."""

from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText

from punto_casino.models.product import Product
from punto_casino.repositories.product_repository import InMemoryProductRepository
from punto_casino.utils.formatters import format_currency


class AdminScreen(MDScreen):
    """Admin dashboard with full CRUD capabilities for cafeteria dishes and products."""

    def __init__(self, product_repo: InMemoryProductRepository, on_navigate, **kwargs):
        super().__init__(**kwargs)
        self.product_repo = product_repo
        self.on_navigate = on_navigate

        self.root_layout = None
        self.products_container = None
        self.status_label = None
        self.form_card = None
        self.confirm_card = None

        # Form fields
        self.input_id = None
        self.input_name = None
        self.input_cat = None
        self.input_price = None
        self.input_stock = None
        self.input_ingredients = None
        self._editing_product_id = None

        self._build_ui()

    def _build_ui(self):
        self.root_layout = MDBoxLayout(
            orientation="vertical",
            padding=[dp(16), dp(12), dp(16), dp(12)],
            spacing=dp(10),
        )

        # Header
        header = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(48),
            spacing=dp(10),
        )
        title = MDLabel(
            text="Panel de Administración - CRUD de Platos",
            bold=True,
            font_style="Title",
            role="medium",
        )
        new_btn = MDButton(
            MDButtonText(text="+ Nuevo Plato"),
            style="filled",
            on_release=lambda x: self._show_create_form(),
        )
        header.add_widget(title)
        header.add_widget(new_btn)
        self.root_layout.add_widget(header)

        # Status feedback
        self.status_label = MDLabel(
            text="Gestiona el catálogo de platos y productos del casino.",
            size_hint_y=None,
            height=dp(22),
            font_style="Label",
            role="medium",
        )
        self.root_layout.add_widget(self.status_label)

        # Products list scroll
        scroll = ScrollView(size_hint=(1, 1))
        self.products_container = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None,
        )
        self.products_container.bind(minimum_height=self.products_container.setter("height"))
        scroll.add_widget(self.products_container)
        self.root_layout.add_widget(scroll)

        self.add_widget(self.root_layout)

    def on_enter(self):
        """Refresh products when entering admin panel."""
        self.refresh_products()

    def refresh_products(self):
        self.products_container.clear_widgets()
        products = self.product_repo.get_all(include_inactive=True)

        for prod in products:
            card = MDCard(
                orientation="vertical",
                size_hint_y=None,
                height=dp(110),
                padding=dp(10),
                spacing=dp(4),
                style="outlined",
            )
            top_line = MDBoxLayout(orientation="horizontal")
            top_line.add_widget(
                MDLabel(
                    text=f"[b]{prod.id_producto}[/b] - {prod.name}",
                    markup=True,
                )
            )
            top_line.add_widget(
                MDLabel(
                    text=f"{format_currency(prod.price)} | Stock: {prod.stock}",
                    halign="right",
                    font_style="Label",
                    role="small",
                )
            )

            ing_label = MDLabel(
                text=f"Cat: {prod.category} | {prod.ingredients or 'Sin detalles'}",
                font_style="Body",
                role="small",
                size_hint_y=None,
                height=dp(20),
            )

            actions = MDBoxLayout(
                orientation="horizontal",
                spacing=dp(8),
                size_hint_y=None,
                height=dp(34),
            )
            edit_btn = MDButton(
                MDButtonText(text="Editar"),
                style="tonal",
                on_release=lambda x, p=prod: self._show_edit_form(p),
            )
            del_btn = MDButton(
                MDButtonText(text="Eliminar"),
                style="outlined",
                on_release=lambda x, p=prod: self._ask_delete_confirmation(p),
            )
            actions.add_widget(edit_btn)
            actions.add_widget(del_btn)

            card.add_widget(top_line)
            card.add_widget(ing_label)
            card.add_widget(actions)
            self.products_container.add_widget(card)

    def _show_create_form(self):
        self._editing_product_id = None
        self._build_and_show_form(
            title_text="Nuevo Plato en Catálogo",
            pid=f"MENU-0{len(self.product_repo.get_all(True)) + 1}",
            name="",
            cat="Menú Normal",
            price="4800",
            stock="20",
            ingredients="",
            id_editable=True,
        )

    def _show_edit_form(self, prod: Product):
        self._editing_product_id = prod.id_producto
        self._build_and_show_form(
            title_text=f"Editar Plato: {prod.name}",
            pid=prod.id_producto,
            name=prod.name,
            cat=prod.category,
            price=str(prod.price),
            stock=str(prod.stock),
            ingredients=prod.ingredients,
            id_editable=False,
        )

    def _build_and_show_form(self, title_text, pid, name, cat, price, stock, ingredients, id_editable):
        self._hide_form()
        self._hide_confirmation()

        self.form_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(340),
            padding=dp(12),
            spacing=dp(6),
            style="elevated",
        )
        form_title = MDLabel(text=title_text, bold=True, size_hint_y=None, height=dp(22))
        self.input_id = MDTextField(MDTextFieldHintText(text="ID Producto (ej: MENU-05)"), size_hint_y=None, height=dp(40))
        self.input_id.text = pid
        self.input_id.disabled = not id_editable

        self.input_name = MDTextField(MDTextFieldHintText(text="Nombre del Plato"), size_hint_y=None, height=dp(40))
        self.input_name.text = name

        self.input_cat = MDTextField(MDTextFieldHintText(text="Categoría (Menú Normal / Ejecutivo / etc.)"), size_hint_y=None, height=dp(40))
        self.input_cat.text = cat

        self.input_price = MDTextField(MDTextFieldHintText(text="Precio en CLP (ej: 4500)"), size_hint_y=None, height=dp(40))
        self.input_price.text = price

        self.input_stock = MDTextField(MDTextFieldHintText(text="Stock inicial (ej: 20)"), size_hint_y=None, height=dp(40))
        self.input_stock.text = stock

        self.input_ingredients = MDTextField(MDTextFieldHintText(text="Ingredientes y Acompañamientos"), size_hint_y=None, height=dp(40))
        self.input_ingredients.text = ingredients

        form_buttons = MDBoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(36))
        cancel_btn = MDButton(MDButtonText(text="Cancelar"), style="outlined", on_release=lambda x: self._hide_form())
        save_btn = MDButton(MDButtonText(text="Guardar en Catálogo"), style="filled", on_release=lambda x: self._save_product())
        form_buttons.add_widget(cancel_btn)
        form_buttons.add_widget(save_btn)

        self.form_card.add_widget(form_title)
        self.form_card.add_widget(self.input_id)
        self.form_card.add_widget(self.input_name)
        self.form_card.add_widget(self.input_cat)
        self.form_card.add_widget(self.input_price)
        self.form_card.add_widget(self.input_stock)
        self.form_card.add_widget(self.input_ingredients)
        self.form_card.add_widget(form_buttons)

        self.root_layout.add_widget(self.form_card, index=1)

    def _hide_form(self):
        if self.form_card and self.form_card in self.root_layout.children:
            self.root_layout.remove_widget(self.form_card)
            self.form_card = None

    def _save_product(self):
        pid = self.input_id.text.strip()
        name = self.input_name.text.strip()
        cat = self.input_cat.text.strip() or "Menú Normal"
        try:
            price = int(self.input_price.text.strip())
            stock = int(self.input_stock.text.strip())
        except ValueError:
            self.status_label.text = "Error: Precio y Stock deben ser números enteros."
            return

        if not pid or not name:
            self.status_label.text = "Error: ID y Nombre son obligatorios."
            return

        ingredients = self.input_ingredients.text.strip()

        if self._editing_product_id:
            prod = Product(id_producto=pid, name=name, price=price, stock=stock, category=cat, ingredients=ingredients)
            self.product_repo.update(prod)
            self.status_label.text = f"Plato '{name}' actualizado exitosamente."
        else:
            prod = Product(id_producto=pid, name=name, price=price, stock=stock, category=cat, ingredients=ingredients)
            self.product_repo.create(prod)
            self.status_label.text = f"Nuevo plato '{name}' agregado al catálogo."

        self._hide_form()
        self.refresh_products()

    def _ask_delete_confirmation(self, prod: Product):
        """Trigger action confirmation dialog before deleting."""
        self._hide_form()
        self._hide_confirmation()

        self.confirm_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(120),
            padding=dp(12),
            spacing=dp(8),
            style="elevated",
        )
        title = MDLabel(text="⚠️ Confirmar Eliminación", bold=True, size_hint_y=None, height=dp(24))
        msg = MDLabel(text=f"¿Está seguro de eliminar '{prod.name}' ({prod.id_producto})?", size_hint_y=None, height=dp(28))
        btns = MDBoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(36))

        cancel_btn = MDButton(
            MDButtonText(text="Cancelar"),
            style="tonal",
            on_release=lambda x: self._hide_confirmation(),
        )
        delete_btn = MDButton(
            MDButtonText(text="Sí, Eliminar"),
            style="filled",
            on_release=lambda x: self._execute_delete(prod.id_producto, prod.name),
        )
        btns.add_widget(cancel_btn)
        btns.add_widget(delete_btn)

        self.confirm_card.add_widget(title)
        self.confirm_card.add_widget(msg)
        self.confirm_card.add_widget(btns)

        self.root_layout.add_widget(self.confirm_card, index=1)

    def _hide_confirmation(self):
        if self.confirm_card and self.confirm_card in self.root_layout.children:
            self.root_layout.remove_widget(self.confirm_card)
            self.confirm_card = None

    def _execute_delete(self, product_id: str, name: str):
        self._hide_confirmation()
        success = self.product_repo.delete(product_id)
        if success:
            self.status_label.text = f"Plato '{name}' eliminado del catálogo."
            self.refresh_products()
        else:
            self.status_label.text = "No se pudo eliminar el plato."

