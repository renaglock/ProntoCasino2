"""Order service orchestrating cart, reservations, and numbered comandas."""

import uuid
from typing import Dict, List, Optional
from punto_casino.models.order import Order, OrderItem, OrderStatus
from punto_casino.models.user import UserRole
from punto_casino.repositories.product_repository import InMemoryProductRepository
from punto_casino.repositories.order_repository import InMemoryOrderRepository
from punto_casino.services.auth_service import AuthService
from punto_casino.utils.qr_generator import generate_pickup_payload


class OrderService:
    """Handles cart operations, order reservation, numbered comandas, and student wallet checkout."""

    def __init__(
        self,
        product_repo: InMemoryProductRepository,
        order_repo: InMemoryOrderRepository,
        auth_service: AuthService,
    ) -> None:
        self.product_repo = product_repo
        self.order_repo = order_repo
        self.auth_service = auth_service
        self._cart: Dict[str, int] = {}  # product_id -> quantity
        self._next_comanda_number: int = 101

    def add_to_cart(self, product_id: str, quantity: int = 1) -> None:
        """Add product quantity to the active cart with inventory check."""
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise ValueError(f"Producto con ID {product_id} no existe.")
        if not product.is_active:
            raise ValueError(f"El plato '{product.name}' se encuentra deshabilitado.")

        current_qty = self._cart.get(product_id, 0)
        target_qty = current_qty + quantity

        if target_qty > product.stock:
            raise ValueError(
                f"Stock insuficiente para '{product.name}'. Disponible: {product.stock}"
            )

        self._cart[product_id] = target_qty

    def remove_from_cart(self, product_id: str, quantity: Optional[int] = None) -> None:
        """Decrease quantity or remove product entirely from cart."""
        if product_id not in self._cart:
            return
        if quantity is None or quantity >= self._cart[product_id]:
            del self._cart[product_id]
        else:
            self._cart[product_id] -= quantity

    def clear_cart(self) -> None:
        """Empty the active shopping cart."""
        self._cart.clear()

    def get_cart_items(self) -> List[OrderItem]:
        """Convert cart dictionary to a list of OrderItem instances."""
        items: List[OrderItem] = []
        for pid, qty in self._cart.items():
            prod = self.product_repo.get_by_id(pid)
            if prod:
                items.append(
                    OrderItem(
                        product_id=prod.id_producto,
                        name=prod.name,
                        unit_price=prod.price,
                        quantity=qty,
                    )
                )
        return items

    def get_cart_total(self) -> int:
        """Calculate total in CLP for all items currently in cart."""
        return sum(item.subtotal for item in self.get_cart_items())

    def checkout(self) -> Order:
        """Create numbered comanda, deduct student wallet, reserve stock, and persist order."""
        items = self.get_cart_items()
        if not items:
            raise ValueError("El carrito está vacío. Agrega platos antes de reservar.")

        total = self.get_cart_total()
        current_user = self.auth_service.current_user

        # Deduct wallet balance if student has positive balance
        if current_user.role == UserRole.CLIENT and current_user.balance >= total:
            self.auth_service.deduct_balance(total)

        # Deduct temporary stock
        for item in items:
            prod = self.product_repo.get_by_id(item.product_id)
            if prod:
                self.product_repo.update_stock(prod.id_producto, prod.stock - item.quantity)

        comanda_num = self._next_comanda_number
        self._next_comanda_number += 1

        order_id = f"PED-{uuid.uuid4().hex[:6].upper()}"
        pickup_payload = generate_pickup_payload(order_id, f"Comanda #{comanda_num} - {current_user.name}")

        order = Order(
            id_pedido=order_id,
            comanda_number=comanda_num,
            customer_name=current_user.name,
            customer_id=current_user.id_usuario,
            customer_role=current_user.role.value,
            items=items,
            status=OrderStatus.PENDING,
            pickup_qr=pickup_payload,
        )

        self.order_repo.add(order)
        self.clear_cart()
        return order

    def get_user_orders(self) -> List[Order]:
        """Fetch active orders for current authenticated user."""
        current_user = self.auth_service.current_user
        if current_user.role == UserRole.ADMIN or current_user.role == UserRole.CASHIER:
            return self.order_repo.get_all()
        return [o for o in self.order_repo.get_all() if o.customer_id == current_user.id_usuario]

    def cancel_order(self, order_id: str) -> bool:
        """Cancel a pending or confirmed order, restoring dishes stock."""
        order = self.order_repo.get_by_id(order_id)
        if not order:
            return False
        if order.status not in (OrderStatus.PENDING, OrderStatus.CONFIRMED):
            return False

        # Restore inventory stock
        for item in order.items:
            prod = self.product_repo.get_by_id(item.product_id)
            if prod:
                self.product_repo.update_stock(prod.id_producto, prod.stock + item.quantity)

        # Update order status
        return self.order_repo.update_status(order_id, OrderStatus.CANCELLED)
