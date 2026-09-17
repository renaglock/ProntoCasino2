"""Product domain model for Pronto Casino UCT."""

from dataclasses import dataclass


@dataclass
class Product:
    """Represents a dish or product item available in the university cafeteria."""

    id_producto: str
    name: str
    price: int  # CLP amount (e.g. 4800)
    stock: int
    category: str = "Menú Normal"
    ingredients: str = ""  # e.g., "Carne de vacuno, maíz, huevo | Ensalada mixta | Postre"
    is_active: bool = True
    description: str = ""
    is_offer: bool = False  # Indica si es producto por vencer o en liquidación
    original_price: int = 0  # Precio original antes del descuento
    offer_label: str = ""    # Motivo (ej: "Consumo hoy antes de 16:00 - 50% OFF")

    @property
    def has_stock(self) -> bool:
        """Returns True if product has available stock and is active."""
        return self.is_active and self.stock > 0

