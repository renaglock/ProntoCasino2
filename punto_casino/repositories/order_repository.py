"""In-memory order repository."""

from datetime import datetime
from typing import Dict, List, Optional
from punto_casino.models.order import Order, OrderStatus


class InMemoryOrderRepository:
    """Thread-safe in-memory order repository for active session."""

    def __init__(self) -> None:
        self._orders: Dict[str, Order] = {}
        self._seed_sample_orders()

    def _seed_sample_orders(self) -> None:
        """Seed representative session orders for accounting analytics and history testing."""
        from datetime import timedelta
        from punto_casino.models.order import OrderItem
        now = datetime.now()

        sample_orders = [
            Order(
                id_pedido="PED-A81B21",
                customer_name="Renato González",
                customer_id="usr-est-01",
                customer_role="CLIENT",
                comanda_number=101,
                items=[
                    OrderItem("MENU-01", "Pastel de Choclo", 4800, 1),
                    OrderItem("BEB-01", "Jugo Natural de Naranja", 1500, 1),
                ],
                status=OrderStatus.DELIVERED,
                created_at=now - timedelta(minutes=140),
                updated_at=now - timedelta(minutes=120),
            ),
            Order(
                id_pedido="PED-C44E89",
                customer_name="Camila Silva",
                customer_id="usr-est-02",
                customer_role="CLIENT",
                comanda_number=102,
                items=[
                    OrderItem("MENU-02", "Escalopa Kaiser con Puré Rústico", 6500, 1),
                    OrderItem("BEB-02", "Bebida en Lata 350ml", 1200, 1),
                ],
                status=OrderStatus.DELIVERED,
                created_at=now - timedelta(minutes=110),
                updated_at=now - timedelta(minutes=95),
            ),
            Order(
                id_pedido="PED-D99F12",
                customer_name="Prof. Matías Morales",
                customer_id="usr-prof-01",
                customer_role="CLIENT",
                comanda_number=103,
                items=[
                    OrderItem("MENU-03", "Pollo a la Plancha con Arroz Integral", 4600, 1),
                    OrderItem("BEB-01", "Jugo Natural de Naranja", 1500, 1),
                ],
                status=OrderStatus.DELIVERED,
                created_at=now - timedelta(minutes=75),
                updated_at=now - timedelta(minutes=60),
            ),
            Order(
                id_pedido="PED-E12B74",
                customer_name="Ignacio Tapia",
                customer_id="usr-est-03",
                customer_role="CLIENT",
                comanda_number=104,
                items=[
                    OrderItem("RAP-01", "Empanada de Pino al Horno", 1200, 2),
                    OrderItem("BEB-02", "Bebida en Lata 350ml", 1200, 1),
                ],
                status=OrderStatus.DELIVERED,
                created_at=now - timedelta(minutes=50),
                updated_at=now - timedelta(minutes=40),
            ),
            Order(
                id_pedido="PED-F66D33",
                customer_name="Valentina Rojas",
                customer_id="usr-est-04",
                customer_role="CLIENT",
                comanda_number=105,
                items=[
                    OrderItem("MENU-04", "Lasaña de Berenjenas y Espinaca", 4500, 1),
                ],
                status=OrderStatus.CONFIRMED,
                created_at=now - timedelta(minutes=25),
                updated_at=now - timedelta(minutes=20),
            ),
            Order(
                id_pedido="PED-G33A19",
                customer_name="Sebastián Castro",
                customer_id="usr-est-05",
                customer_role="CLIENT",
                comanda_number=106,
                items=[
                    OrderItem("MENU-01", "Pastel de Choclo", 4800, 1),
                ],
                status=OrderStatus.PENDING,
                created_at=now - timedelta(minutes=10),
                updated_at=now - timedelta(minutes=10),
            ),
            Order(
                id_pedido="PED-B11C02",
                customer_name="Constanza Vega",
                customer_id="usr-est-06",
                customer_role="CLIENT",
                comanda_number=107,
                items=[
                    OrderItem("RAP-01", "Empanada de Pino al Horno", 1200, 1),
                ],
                status=OrderStatus.CANCELLED,
                created_at=now - timedelta(minutes=80),
                updated_at=now - timedelta(minutes=78),
            ),
        ]

        for order in sample_orders:
            self._orders[order.id_pedido] = order

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

