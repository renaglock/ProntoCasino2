"""Abstract base repository protocols."""

from typing import List, Optional, Protocol
from punto_casino.models.product import Product
from punto_casino.models.order import Order, OrderStatus


class ProductRepository(Protocol):
    """Protocol for product persistence operations."""

    def get_all(self) -> List[Product]:
        """Retrieve all products."""
        ...

    def get_by_id(self, product_id: str) -> Optional[Product]:
        """Retrieve product by its unique ID."""
        ...

    def search(self, query: str) -> List[Product]:
        """Search products by name or category."""
        ...

    def update_stock(self, product_id: str, new_stock: int) -> bool:
        """Update available inventory count."""
        ...

    def set_active_status(self, product_id: str, is_active: bool) -> bool:
        """Enable or disable product availability."""
        ...


class OrderRepository(Protocol):
    """Protocol for order persistence operations."""

    def add(self, order: Order) -> Order:
        """Save a new order."""
        ...

    def get_by_id(self, order_id: str) -> Optional[Order]:
        """Find order by its unique ID."""
        ...

    def get_all(self) -> List[Order]:
        """Retrieve all orders."""
        ...

    def get_by_status(self, status: OrderStatus) -> List[Order]:
        """Retrieve orders by lifecycle state."""
        ...

    def update_status(self, order_id: str, new_status: OrderStatus) -> bool:
        """Update order status."""
        ...

