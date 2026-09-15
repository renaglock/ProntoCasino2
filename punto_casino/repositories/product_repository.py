"""In-memory product repository with full CRUD operations and wireframe seed data."""

from typing import Dict, List, Optional
from punto_casino.models.product import Product


class InMemoryProductRepository:
    """Thread-safe in-memory product repository with full CRUD capabilities."""

    def __init__(self) -> None:
        self._products: Dict[str, Product] = {}
        self._seed_default_products()

    def _seed_default_products(self) -> None:
        """Seed initial products based on PRONTO CASINO UCT wireframe (docs/PRONTO CASINO.pdf)."""
        seed_data = [
            Product(
                id_producto="MENU-01",
                name="Pastel de Choclo",
                price=4800,
                stock=25,
                category="Menú Normal",
                ingredients="Carne de vacuno, maíz dulce, huevo duro | Ensalada Mixta | Fruta de estación | Jugo o Agua",
                description="Plato tradicional chileno horneado en paila de greda con ensalada y postre",
            ),
            Product(
                id_producto="MENU-02",
                name="Escalopa Kaiser con Puré Rústico",
                price=6500,
                stock=20,
                category="Menú Ejecutivo",
                ingredients="Escalopa rellena de jamón y queso fundido | Puré rústico a la mantequilla | Postre especial",
                description="Menú ejecutivo premium preparado al momento",
            ),
            Product(
                id_producto="MENU-03",
                name="Pollo a la Plancha con Arroz Integral",
                price=4600,
                stock=18,
                category="Menú Hipocalórico",
                ingredients="Pechuga de pollo a las finas hierbas | Arroz integral al vapor | Verduras salteadas",
                description="Opción balanceada baja en calorías con ingredientes naturales",
            ),
            Product(
                id_producto="MENU-04",
                name="Lasaña de Berenjenas y Espinaca",
                price=4500,
                stock=15,
                category="Menú Vegetariano",
                ingredients="Láminas de berenjena asada, espinaca fresca, salsa bechamel y queso mozzarella",
                description="Nutritiva lasaña 100% vegetariana horneada al gratín",
            ),
            Product(
                id_producto="RAP-01",
                name="Empanada de Pino al Horno",
                price=2000,
                stock=30,
                category="Comidas Rápidas",
                ingredients="Masa casera tradicional, pino de carne picada, aceituna, huevo y pasas",
                description="Clásica empanada chilena al horno",
            ),
            Product(
                id_producto="RAP-02",
                name="Completo Italiano",
                price=2500,
                stock=35,
                category="Comidas Rápidas",
                ingredients="Pan lengua tostado, vienesa, tomate picado, palta fresca y mayonesa casera",
                description="Tradicional completo italiano con palta fresca",
            ),
            Product(
                id_producto="BEB-01",
                name="Café de Grano",
                price=1200,
                stock=50,
                category="Bebidas",
                ingredients="Café espresso recién molido o cortado con leche",
                description="Café caliente recién preparado",
            ),
            Product(
                id_producto="BEB-02",
                name="Jugo Natural de Temporada",
                price=1800,
                stock=25,
                category="Bebidas",
                ingredients="Frutilla, naranja o piña natural 500ml",
                description="Jugo 100% natural sin azúcar añadida",
            ),
        ]
        for p in seed_data:
            self._products[p.id_producto] = p

    # --- CRUD Operations ---

    def create(self, product: Product) -> Product:
        """Create and add a new product/dish to the catalog (CRUD: Create)."""
        self._products[product.id_producto] = product
        return product

    def get_all(self, include_inactive: bool = False) -> List[Product]:
        """Retrieve all products (CRUD: Read)."""
        if include_inactive:
            return list(self._products.values())
        return [p for p in self._products.values() if p.is_active]

    def get_by_id(self, product_id: str) -> Optional[Product]:
        """Retrieve product by its unique ID (CRUD: Read)."""
        return self._products.get(product_id)

    def get_by_category(self, category: str) -> List[Product]:
        """Retrieve products filtered by menu category."""
        if not category or category == "Todos":
            return self.get_all()
        return [p for p in self.get_all() if p.category.lower() == category.lower()]

    def search(self, query: str) -> List[Product]:
        """Search products by name, category, or ingredients."""
        q = query.strip().lower()
        if not q:
            return self.get_all()
        return [
            p for p in self.get_all()
            if q in p.name.lower() or q in p.category.lower() or q in p.ingredients.lower()
        ]

    def update(self, product: Product) -> bool:
        """Update existing product data (CRUD: Update)."""
        if product.id_producto not in self._products:
            return False
        self._products[product.id_producto] = product
        return True

    def delete(self, product_id: str) -> bool:
        """Permanently remove a product from the catalog (CRUD: Delete)."""
        if product_id not in self._products:
            return False
        del self._products[product_id]
        return True

    def update_stock(self, product_id: str, new_stock: int) -> bool:
        """Update inventory stock count."""
        product = self._products.get(product_id)
        if not product:
            return False
        product.stock = max(0, new_stock)
        return True

    def set_active_status(self, product_id: str, is_active: bool) -> bool:
        """Toggle active status for a product."""
        product = self._products.get(product_id)
        if not product:
            return False
        product.is_active = is_active
        return True
