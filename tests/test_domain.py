"""Unit tests for domain models, repositories, and application services."""

import os
import unittest
from punto_casino.models.user import UserRole
from punto_casino.models.product import Product
from punto_casino.models.order import OrderStatus
from punto_casino.repositories.database import DatabaseManager
from punto_casino.repositories.user_repository import UserRepository
from punto_casino.repositories.product_repository import InMemoryProductRepository
from punto_casino.repositories.order_repository import InMemoryOrderRepository
from punto_casino.services.auth_service import AuthService
from punto_casino.services.order_service import OrderService
from punto_casino.services.cashier_service import CashierService


class TestDomainServices(unittest.TestCase):
    """Test suite covering critical business workflows."""

    def _clean_test_db(self):
        for suffix in ("", "-wal", "-shm"):
            p = self.test_db + suffix
            if os.path.exists(p):
                try:
                    os.remove(p)
                except OSError:
                    pass

    def setUp(self):
        self.test_db = "test_punto_casino.db"
        self._clean_test_db()
        self.db_manager = DatabaseManager(self.test_db)
        self.user_repo = UserRepository(self.db_manager)
        self.prod_repo = InMemoryProductRepository()
        self.order_repo = InMemoryOrderRepository()
        self.auth_service = AuthService(self.user_repo)
        self.order_service = OrderService(self.prod_repo, self.order_repo, self.auth_service)
        self.cashier_service = CashierService(self.prod_repo, self.order_repo, self.auth_service)

    def tearDown(self):
        self._clean_test_db()

    def test_auth_quick_login(self):
        user = self.auth_service.quick_login("admin")
        self.assertIsNotNone(user)
        self.assertEqual(user.role, UserRole.ADMIN)
        self.assertEqual(self.auth_service.current_user.email, "admin@uct.cl")

    def test_product_repository_crud(self):
        initial_count = len(self.prod_repo.get_all())
        self.assertGreater(initial_count, 0)
        
        # Test add product via create
        new_prod = self.prod_repo.create(
            Product(
                id_producto="MENU-99",
                name="Cazuela de Ave",
                category="Menú Normal",
                price=4200,
                stock=15,
                ingredients="Pollo, zapallo, choclo, papas",
            )
        )
        self.assertEqual(new_prod.name, "Cazuela de Ave")
        self.assertEqual(new_prod.id_producto, "MENU-99")
        self.assertEqual(len(self.prod_repo.get_all()), initial_count + 1)

        # Test set active status
        self.prod_repo.set_active_status(new_prod.id_producto, False)
        updated = self.prod_repo.get_by_id(new_prod.id_producto)
        self.assertFalse(updated.is_active)

    def test_order_creation_and_cart_workflow(self):
        self.auth_service.quick_login("estudiante")
        prods = self.prod_repo.get_all()
        prod1 = prods[0]

        # Add to cart
        self.order_service.add_to_cart(prod1.id_producto, 2)
        self.assertEqual(self.order_service.get_cart_count(), 2)
        self.assertEqual(self.order_service.get_cart_total(), prod1.price * 2)

        # Checkout order
        order = self.order_service.checkout()
        self.assertIsNotNone(order)
        self.assertEqual(order.total, prod1.price * 2)
        self.assertEqual(order.status, OrderStatus.PENDING)
        self.assertEqual(self.order_service.get_cart_count(), 0)

    def test_cashier_processing_workflow(self):
        # Place order
        self.auth_service.quick_login("estudiante")
        prods = self.prod_repo.get_all()
        self.order_service.add_to_cart(prods[0].id_producto, 1)
        order = self.order_service.checkout()

        # Cashier confirms
        self.cashier_service.confirm_order(order.id_pedido)
        updated = self.order_repo.get_by_id(order.id_pedido)
        self.assertEqual(updated.status, OrderStatus.CONFIRMED)

        # Cashier marks ready
        self.cashier_service.mark_ready(order.id_pedido)
        updated = self.order_repo.get_by_id(order.id_pedido)
        self.assertEqual(updated.status, OrderStatus.READY)

        # Cashier delivers
        self.cashier_service.mark_delivered(order.id_pedido)
        updated = self.order_repo.get_by_id(order.id_pedido)
        self.assertEqual(updated.status, OrderStatus.DELIVERED)

    def test_accounting_report_metrics(self):
        report = self.order_service.get_accounting_report()
        self.assertIn("total_collected", report)
        self.assertIn("average_ticket", report)
        self.assertIn("delivery_rate", report)
        self.assertIn("category_sales", report)
        self.assertIn("top_dishes", report)
        self.assertGreater(report["total_collected"], 0)
        self.assertGreater(len(report["top_dishes"]), 0)

    def test_category_color_coherence(self):
        from punto_casino.core.config import CATEGORY_PALETTE, get_category_style

        for cat in ["Menú Normal", "Menú Ejecutivo", "Menú Hipocalórico", "Comidas Rápidas", "Bebidas"]:
            style = get_category_style(cat)
            self.assertIn("hex", style)
            self.assertIn("rgba", style)
            self.assertIn("label", style)
            self.assertTrue(style["hex"].startswith("#"))
            self.assertEqual(len(style["rgba"]), 4)

        unknown = get_category_style("Categoría Inexistente")
        self.assertEqual(unknown["hex"], "#64748B")


if __name__ == "__main__":
    unittest.main()
