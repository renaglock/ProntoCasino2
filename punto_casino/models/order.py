"""Order and OrderItem domain models with sequential comanda numbering."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class OrderStatus(str, Enum):
    """Lifecycle states of an order."""

    PENDING = "PENDING"          # Creado por cliente, pendiente por pagar en casino
    CONFIRMED = "CONFIRMED"      # Aprobado por cocina/caja y en preparación
    CANCELLED = "CANCELLED"      # Cancelado por el cliente
    REJECTED = "REJECTED"        # Rechazado por caja (falta de stock)
    READY = "READY"              # Preparado y listo para entrega en meson
    DELIVERED = "DELIVERED"      # Cobrado y entregado al cliente


class PaymentMethod(str, Enum):
    """Chilean higher-education payment methods (Punto 4, Plan Expansión)."""

    BAES_JUNAEB = "BAES_JUNAEB"    # Beca BAES JUNAEB (Edenred / Pluxee Sodexo) - >70% mercado
    WEBPAY_PLUS = "WEBPAY_PLUS"    # Transbank Webpay Plus (Débito / Crédito / CuentaRUT)
    FINTOC_KHIPU = "FINTOC_KHIPU"  # Open Finance TEF (Fintoc / Khipu)
    BECA_INTERNA = "BECA_INTERNA"  # Beca Interna de Alimentación DAE / Convenio UCT
    EFECTIVO_POS = "EFECTIVO_POS"  # Efectivo / Máquina POS en Mesón


PAYMENT_METHOD_LABELS = {
    PaymentMethod.BAES_JUNAEB: "Beca BAES",
    PaymentMethod.WEBPAY_PLUS: "Webpay Plus",
    PaymentMethod.FINTOC_KHIPU: "Transferencia TEF",
    PaymentMethod.BECA_INTERNA: "Beca DAE",
    PaymentMethod.EFECTIVO_POS: "Mesón",
}

PAYMENT_METHOD_ICONS = {
    PaymentMethod.BAES_JUNAEB: "school",
    PaymentMethod.WEBPAY_PLUS: "credit-card",
    PaymentMethod.FINTOC_KHIPU: "bank-transfer",
    PaymentMethod.BECA_INTERNA: "card-account-details-star",
    PaymentMethod.EFECTIVO_POS: "cash-register",
}


ORDER_STATUS_LABELS = {
    OrderStatus.PENDING: "Pendiente de pago",
    OrderStatus.CONFIRMED: "En Preparación",
    OrderStatus.READY: "Listo para retiro",
    OrderStatus.DELIVERED: "Entregado",
    OrderStatus.CANCELLED: "Cancelada",
    OrderStatus.REJECTED: "Rechazada",
}

ORDER_STATUS_COLORS = {
    OrderStatus.PENDING: "#D97706",    # Ámbar / Naranja pendiente
    OrderStatus.CONFIRMED: "#0288D1",  # Azul celeste cocina en preparación
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

    def to_dict(self) -> Dict[str, Any]:
        """Serializes OrderItem to dictionary."""
        return {
            "product_id": self.product_id,
            "name": self.name,
            "unit_price": self.unit_price,
            "quantity": self.quantity,
            "subtotal": self.subtotal,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OrderItem":
        """Instantiates OrderItem from dictionary."""
        return cls(
            product_id=data.get("product_id", ""),
            name=data.get("name", ""),
            unit_price=int(data.get("unit_price", 0)),
            quantity=int(data.get("quantity", 1)),
        )


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
    payment_method: str = PaymentMethod.BAES_JUNAEB.value
    is_paid: bool = False
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

    def to_dict(self) -> Dict[str, Any]:
        """Serializes Order entity to a JSON-compatible dictionary."""
        return {
            "id_pedido": self.id_pedido,
            "customer_name": self.customer_name,
            "comanda_number": self.comanda_number,
            "items": [item.to_dict() for item in self.items],
            "customer_id": self.customer_id,
            "customer_role": self.customer_role,
            "status": self.status.value if isinstance(self.status, OrderStatus) else str(self.status),
            "payment_method": self.payment_method,
            "is_paid": self.is_paid,
            "pickup_qr": self.pickup_qr,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "total": self.total,
            "total_items": self.total_items,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Order":
        """Instantiates an Order from a serialized dictionary."""
        raw_status = data.get("status", OrderStatus.PENDING.value)
        try:
            status = OrderStatus(raw_status)
        except ValueError:
            status = OrderStatus.PENDING

        raw_created = data.get("created_at")
        if isinstance(raw_created, str):
            try:
                created_at = datetime.fromisoformat(raw_created)
            except Exception:
                created_at = datetime.now()
        elif isinstance(raw_created, datetime):
            created_at = raw_created
        else:
            created_at = datetime.now()

        raw_updated = data.get("updated_at")
        if isinstance(raw_updated, str):
            try:
                updated_at = datetime.fromisoformat(raw_updated)
            except Exception:
                updated_at = datetime.now()
        elif isinstance(raw_updated, datetime):
            updated_at = raw_updated
        else:
            updated_at = datetime.now()

        raw_items = data.get("items", [])
        items = [OrderItem.from_dict(it) for it in raw_items]

        return cls(
            id_pedido=data.get("id_pedido", ""),
            customer_name=data.get("customer_name", ""),
            comanda_number=int(data.get("comanda_number", 101)),
            items=items,
            customer_id=data.get("customer_id"),
            customer_role=data.get("customer_role", "client"),
            status=status,
            payment_method=data.get("payment_method", PaymentMethod.BAES_JUNAEB.value),
            is_paid=bool(data.get("is_paid", False)),
            pickup_qr=data.get("pickup_qr"),
            created_at=created_at,
            updated_at=updated_at,
        )
