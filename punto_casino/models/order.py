"""Order and OrderItem domain models with sequential comanda numbering."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


class OrderStatus(str, Enum):
    """Lifecycle states of an order."""

    PENDING = "PENDING"          # Creado por cliente, pendiente por pagar en casino
    CONFIRMED = "CONFIRMED"      # Aprobado por cocina/caja
    CANCELLED = "CANCELLED"      # Cancelado por el cliente
    REJECTED = "REJECTED"        # Rechazado por caja (falta de stock)
    READY = "READY"              # Preparado y listo para entrega en meson
    DELIVERED = "DELIVERED"      # Cobrado y entregado al cliente


ORDER_STATUS_LABELS = {
    OrderStatus.PENDING: "Pendiente por pagar",
    OrderStatus.CONFIRMED: "Confirmado en cocina",
    OrderStatus.READY: "Listo para entrega",
    OrderStatus.DELIVERED: "Pagado y Entregado",
    OrderStatus.CANCELLED: "Cancelada",
    OrderStatus.REJECTED: "Rechazada",
}

ORDER_STATUS_COLORS = {
    OrderStatus.PENDING: "#D97706",    # Ámbar / Naranja pendiente
    OrderStatus.CONFIRMED: "#0288D1",  # Azul celeste cocina
    OrderStatus.READY: "#0D9488",      # Verde azulado listo
    OrderStatus.DELIVERED: "#10B981",  # Esmeralda entregado
    OrderStatus.CANCELLED: "#64748B",  # Gris pizarra cancelado
    OrderStatus.REJECTED: "#EF4444",   # Rojo rechazado
}


@dataclass
class OrderItem:
    """Individual product line item within an order."""

    product_id: str
    name: str
    unit_price: int
    quantity: int

    @property
    def subtotal(self) -> int:
        """Returns computed line item subtotal in CLP."""
        return self.unit_price * self.quantity


@dataclass
class Order:
    """Customer order entity with sequential comanda number."""

    id_pedido: str
    customer_name: str
    comanda_number: int = 101  # Sequential comanda number (#101, #102...)
    items: List[OrderItem] = field(default_factory=list)
    customer_id: Optional[str] = None
    customer_role: str = "client"
    status: OrderStatus = OrderStatus.PENDING
    pickup_qr: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    @property
    def total(self) -> int:
        """Total cost of the order in CLP."""
        return sum(item.subtotal for item in self.items)

    @property
    def total_items(self) -> int:
        """Total quantity of products across all line items."""
        return sum(item.quantity for item in self.items)
