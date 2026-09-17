"""Cashier service managing numbered comanda queues, approvals, and inventory toggling."""

from typing import List, Optional
from punto_casino.models.order import Order, OrderStatus
from punto_casino.repositories.product_repository import InMemoryProductRepository
from punto_casino.repositories.order_repository import InMemoryOrderRepository
from punto_casino.services.auth_service import AuthService


class CashierService:
    """Provides cashier capabilities: accept/reject numbered comandas and manage inventory stock."""

    def __init__(
        self,
        product_repo: InMemoryProductRepository,
        order_repo: InMemoryOrderRepository,
        auth_service: AuthService,
    ) -> None:
        self.product_repo = product_repo
        self.order_repo = order_repo
        self.auth_service = auth_service

    def get_pending_orders(self) -> List[Order]:
        """Fetch all orders awaiting cashier confirmation sorted by comanda number."""
        return sorted(
            self.order_repo.get_by_status(OrderStatus.PENDING),
            key=lambda o: o.comanda_number,
        )

    def confirm_order(self, order_id: str) -> Optional[Order]:
        """Cashier confirms order: state moves to CONFIRMED."""
        order = self.order_repo.get_by_id(order_id)
        if not order:
            return None
        if order.status != OrderStatus.PENDING:
            raise ValueError(f"La comanda #{order.comanda_number} no está en estado pendiente.")

        self.order_repo.update_status(order_id, OrderStatus.CONFIRMED)
        return self.order_repo.get_by_id(order_id)

    def reject_order(self, order_id: str, reason: str = "") -> Optional[Order]:
        """Cashier rejects comanda: state moves to REJECTED, stock and student balance are refunded."""
        order = self.order_repo.get_by_id(order_id)
        if not order:
            return None
        if order.status != OrderStatus.PENDING:
            raise ValueError(f"La comanda #{order.comanda_number} no puede ser rechazada en estado {order.status.value}.")

        # Replenish reserved stock
        for item in order.items:
            prod = self.product_repo.get_by_id(item.product_id)
            if prod:
                self.product_repo.update_stock(prod.id_producto, prod.stock + item.quantity)

        # Refund student wallet if student
        if order.customer_role.upper() == "CLIENT" and order.customer_id:
            self.auth_service.refund_user_balance(order.customer_id, order.total)

        self.order_repo.update_status(order_id, OrderStatus.REJECTED)
        return self.order_repo.get_by_id(order_id)

    def get_history_orders(self) -> List[Order]:
        """Fetch all completed, delivered, rejected, or cancelled orders for shift audit."""
        completed_statuses = (OrderStatus.DELIVERED, OrderStatus.CANCELLED, OrderStatus.REJECTED)
        return [o for o in self.order_repo.get_all() if o.status in completed_statuses]


    def mark_ready(self, order_id: str) -> Optional[Order]:
        """Mark comanda prepared and ready for student pickup at counter."""
        order = self.order_repo.get_by_id(order_id)
        if not order or order.status != OrderStatus.CONFIRMED:
            return None
        self.order_repo.update_status(order_id, OrderStatus.READY)
        return self.order_repo.get_by_id(order_id)

    def mark_delivered(self, order_id: str) -> Optional[Order]:
        """Mark comanda delivered after verified pickup."""
        order = self.order_repo.get_by_id(order_id)
        if not order:
            return None
        self.order_repo.update_status(order_id, OrderStatus.DELIVERED)
        return self.order_repo.get_by_id(order_id)

    def process_qr_payment(self, qr_input: str):
        """Verify QR code payload or order ID, execute checkout in cashier, and mark as DELIVERED."""
        from punto_casino.utils.qr_generator import parse_pickup_payload

        clean_input = qr_input.strip()
        order_id = clean_input
        parsed = parse_pickup_payload(clean_input)
        if parsed and "order_id" in parsed:
            order_id = parsed["order_id"]

        order = self.order_repo.get_by_id(order_id)
        if not order:
            return False, f"No se encontró la comanda con código '{clean_input}'.", None

        if order.status == OrderStatus.CANCELLED:
            return False, f"La comanda #{order.comanda_number} fue cancelada por el cliente.", order

        if order.status == OrderStatus.DELIVERED:
            return False, f"La comanda #{order.comanda_number} ya fue cobrada y entregada.", order

        self.order_repo.update_status(order.id_pedido, OrderStatus.DELIVERED)
        updated_order = self.order_repo.get_by_id(order.id_pedido)
        return True, f"Comanda #{order.comanda_number} cobrada (${order.total:,} CLP) y entregada exitosamente.", updated_order
