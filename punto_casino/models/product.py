"""Product domain model for Pronto Casino UCT."""

from dataclasses import dataclass
from typing import Any, Dict


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

    def to_dict(self) -> Dict[str, Any]:
        """Serializes Product entity to a JSON-compatible dictionary."""
        return {
            "id_producto": self.id_producto,
            "name": self.name,
            "price": self.price,
            "stock": self.stock,
            "category": self.category,
            "ingredients": self.ingredients,
            "is_active": self.is_active,
            "description": self.description,
            "is_offer": self.is_offer,
            "original_price": self.original_price,
            "offer_label": self.offer_label,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Product":
        """Instantiates a Product from a serialized dictionary."""
        return cls(
            id_producto=data.get("id_producto", ""),
            name=data.get("name", ""),
            price=int(data.get("price", 0)),
            stock=int(data.get("stock", 0)),
            category=data.get("category", "Menú Normal"),
            ingredients=data.get("ingredients", ""),
            is_active=bool(data.get("is_active", True)),
            description=data.get("description", ""),
            is_offer=bool(data.get("is_offer", False)),
            original_price=int(data.get("original_price", 0)),
            offer_label=data.get("offer_label", ""),
        )
