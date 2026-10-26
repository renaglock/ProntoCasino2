"""JSON-backed order repository with persistent file storage and time.perf_counter() metrics."""

import json
import os
import time
from datetime import datetime
from typing import Dict, List, Optional
from punto_casino.models.order import Order, OrderStatus, PaymentMethod


class JsonOrderRepository:
    """Thread-safe JSON-persisted order repository for orders and reservations."""

    def __init__(self, file_path: Optional[str] = None) -> None:
        self._orders: Dict[str, Order] = {}
        self.last_io_duration_ms: float = 0.0

        if file_path is None:
            root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            file_path = os.path.join(root_dir, "data", "pedidos.json")
        self.file_path = file_path

        self._load_or_seed()

    def _load_or_seed(self) -> None:
        """Loads orders from JSON file or seeds representative orders if missing."""
        if os.path.exists(self.file_path):
            self._load_from_json()
        else:
            self._seed_sample_orders()
            self._save_to_json()

    def _load_from_json(self) -> None:
        """Reads orders from disk using safe context manager and json.load()."""
        start_time = time.perf_counter()
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._orders = {item["id_pedido"]: Order.from_dict(item) for item in data}
        except (json.JSONDecodeError, KeyError, FileNotFoundError):
            self._seed_sample_orders()
            self._save_to_json()
        self.last_io_duration_ms = (time.perf_counter() - start_time) * 1000

    def _save_to_json(self) -> None:
        """Persists all orders to JSON file using with open and json.dump()."""
        start_time = time.perf_counter()
        dirname = os.path.dirname(self.file_path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        payload = [o.to_dict() for o in self._orders.values()]
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=4, ensure_ascii=False)
        self.last_io_duration_ms = (time.perf_counter() - start_time) * 1000

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
                payment_method=PaymentMethod.BAES_JUNAEB.value,
                is_paid=True,
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
                payment_method=PaymentMethod.WEBPAY_PLUS.value,
                is_paid=True,
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
                payment_method=PaymentMethod.FINTOC_KHIPU.value,
                is_paid=True,
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
                payment_method=PaymentMethod.BECA_INTERNA.value,
                is_paid=True,
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
                payment_method=PaymentMethod.BAES_JUNAEB.value,
                is_paid=True,
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
                payment_method=PaymentMethod.EFECTIVO_POS.value,
                is_paid=False,
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
                payment_method=PaymentMethod.BAES_JUNAEB.value,
                is_paid=False,
                created_at=now - timedelta(minutes=80),
                updated_at=now - timedelta(minutes=78),
            ),
        ]

        for order in sample_orders:
            self._orders[order.id_pedido] = order

    def add(self, order: Order) -> Order:
        """Persist a new order and sync to disk JSON."""
        self._orders[order.id_pedido] = order
        self._save_to_json()
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
        """Update lifecycle status of an order and sync to disk JSON."""
        order = self._orders.get(order_id)
        if not order:
            return False
        order.status = new_status
        order.updated_at = datetime.now()
        self._save_to_json()
        return True


# Backward-compatible alias for existing imports
InMemoryOrderRepository = JsonOrderRepository
