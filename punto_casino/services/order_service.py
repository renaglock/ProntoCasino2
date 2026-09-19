"""Order service orchestrating cart, reservations, and numbered comandas."""

import uuid
from typing import Any, Dict, List, Optional
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
        existing_orders = self.order_repo.get_all()
        self._next_comanda_number: int = (
            max([o.comanda_number for o in existing_orders], default=100) + 1
        )

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
        """Cancel a pending or confirmed order, restoring dishes stock and student balance."""
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

        # Refund student wallet if paid with balance
        if order.customer_role.upper() == "CLIENT" and order.customer_id:
            self.auth_service.refund_user_balance(order.customer_id, order.total)

        # Update order status
        return self.order_repo.update_status(order_id, OrderStatus.CANCELLED)

    def mark_delivered(self, order_id: str) -> bool:
        """Mark an active comanda as paid and delivered in cashier."""
        order = self.order_repo.get_by_id(order_id)
        if not order:
            return False
        if order.status in (OrderStatus.CANCELLED, OrderStatus.REJECTED, OrderStatus.DELIVERED):
            return False
        return self.order_repo.update_status(order_id, OrderStatus.DELIVERED)

    def get_sales_metrics(self) -> Dict[str, Any]:
        """Aggregate financial and operational sales metrics for administration."""
        return self.get_accounting_report()

    def get_accounting_report(self) -> Dict[str, Any]:
        """Generate comprehensive financial, category distribution, and top dishes report for administration."""
        orders = self.order_repo.get_all()
        delivered = [o for o in orders if o.status == OrderStatus.DELIVERED]
        pending = [o for o in orders if o.status in (OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.READY)]
        cancelled = [o for o in orders if o.status in (OrderStatus.CANCELLED, OrderStatus.REJECTED)]

        total_collected = sum(o.total for o in delivered)
        delivered_count = len(delivered)
        total_orders = len(orders)
        average_ticket = (total_collected // delivered_count) if delivered_count > 0 else 0
        delivery_rate = round((delivered_count / total_orders * 100), 1) if total_orders > 0 else 0.0

        # Sales and volume by category (based on delivered orders)
        category_data: Dict[str, Dict[str, Any]] = {}
        # Product ranking
        product_sales: Dict[str, Dict[str, Any]] = {}
        total_items_sold = 0

        for order in delivered:
            for item in order.items:
                total_items_sold += item.quantity
                prod = self.product_repo.get_by_id(item.product_id)
                cat = prod.category if prod else "Menú Normal"

                # Category aggregation
                if cat not in category_data:
                    category_data[cat] = {"revenue": 0, "quantity": 0, "category": cat}
                category_data[cat]["revenue"] += item.subtotal
                category_data[cat]["quantity"] += item.quantity

                # Product aggregation
                p_key = item.name
                if p_key not in product_sales:
                    product_sales[p_key] = {
                        "name": item.name,
                        "product_id": item.product_id,
                        "category": cat,
                        "quantity": 0,
                        "revenue": 0,
                    }
                product_sales[p_key]["quantity"] += item.quantity
                product_sales[p_key]["revenue"] += item.subtotal

        # Compute percentages for categories
        category_list = []
        for cat, val in category_data.items():
            pct = round((val["revenue"] / total_collected * 100), 1) if total_collected > 0 else 0.0
            category_list.append({
                "category": cat,
                "revenue": val["revenue"],
                "quantity": val["quantity"],
                "percentage": pct,
            })
        category_list.sort(key=lambda x: x["revenue"], reverse=True)

        # Top selling dishes
        top_dishes = list(product_sales.values())
        top_dishes.sort(key=lambda x: (x["quantity"], x["revenue"]), reverse=True)
        max_qty = top_dishes[0]["quantity"] if top_dishes else 1
        for d in top_dishes:
            d["relative_pct"] = round((d["quantity"] / max_qty * 100), 1)

        return {
            "total_orders": total_orders,
            "delivered_count": delivered_count,
            "pending_count": len(pending),
            "cancelled_count": len(cancelled),
            "total_collected": total_collected,
            "average_ticket": average_ticket,
            "delivery_rate": delivery_rate,
            "total_items_sold": total_items_sold,
            "category_sales": category_list,
            "top_dishes": top_dishes[:5],
        }


