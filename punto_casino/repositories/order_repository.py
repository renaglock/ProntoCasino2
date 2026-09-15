"""In-memory order repository."""

from datetime import datetime
from typing import Dict, List, Optional
from punto_casino.models.order import Order, OrderStatus


class InMemoryOrderRepository:
    """Thread-safe in-memory order repository for active session."""

    def __init__(self) -> None:
        self._orders: Dict[str, Order] = {}

    def add(self, order: Order) -> Order:
        """Persist a new order."""
        self._orders[order.id_pedido] = order
        return order

    def get_by_id(self, order_id: str) -> Optional[Order]:
        """Lookup order by ID."""
        return self._orders.get(order_id)

    def get_all(self) -> List[Order]:
        """Return all orders sorted newest first."""
        return sorted(self._orders.values(), key=lambda o: o.created_at, reverse=True)

    def get_by_status(self, status: OrderStatus) -> List[Order]:
        """Return orders matching a specific status."""
        return [o for o in self.get_all() if o.status == status]

    def get_by_customer(self, customer_name: str) -> List[Order]:
        """Return orders made by a specific customer."""
        return [o for o in self.get_all() if o.customer_name.lower() == customer_name.lower()]

    def update_status(self, order_id: str, new_status: OrderStatus) -> bool:
        """Update lifecycle status of an order."""
        order = self._orders.get(order_id)
        if not order:
            return False
        order.status = new_status
        order.updated_at = datetime.now()
        return True

