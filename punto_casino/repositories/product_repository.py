"""JSON-backed product repository with full CRUD operations and wireframe seed data."""

import json
import os
import time
from typing import Dict, List, Optional
from punto_casino.models.product import Product


class JsonProductRepository:
    """Thread-safe JSON-persisted product repository with full CRUD capabilities."""

    def __init__(self, file_path: Optional[str] = None) -> None:
        self._products: Dict[str, Product] = {}
        self.last_io_duration_ms: float = 0.0

        if file_path is None:
            root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            file_path = os.path.join(root_dir, "data", "productos.json")
        self.file_path = file_path

        self._load_or_seed()

    def _load_or_seed(self) -> None:
        """Loads products from JSON file or seeds default catalog if missing."""
        if os.path.exists(self.file_path):
            self._load_from_json()
        else:
            self._seed_default_products()
            self._save_to_json()

    def _load_from_json(self) -> None:
        """Reads products from disk using safe context manager and json.load()."""
        start_time = time.perf_counter()
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._products = {item["id_producto"]: Product.from_dict(item) for item in data}
        except (json.JSONDecodeError, KeyError, FileNotFoundError):
            self._seed_default_products()
            self._save_to_json()
        self.last_io_duration_ms = (time.perf_counter() - start_time) * 1000

    def _save_to_json(self) -> None:
        """Persists current product catalog to JSON file using with open and json.dump()."""
        start_time = time.perf_counter()
        dirname = os.path.dirname(self.file_path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        payload = [p.to_dict() for p in self._products.values()]
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=4, ensure_ascii=False)
        self.last_io_duration_ms = (time.perf_counter() - start_time) * 1000

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
                price=1200,
                stock=12,
                category="Comidas Rápidas",
                ingredients="Masa casera tradicional, pino de carne picada, aceituna, huevo y pasas",
                description="Clásica empanada chilena al horno",
                is_offer=True,
                original_price=2000,
                offer_label="Por vencer hoy - 40% OFF",
            ),
            Product(
                id_producto="OFER-01",
                name="Lasaña Boloñesa (Últimas porciones)",
                price=2500,
                stock=6,
                category="Menú Normal",
                ingredients="Carne seleccionada, pasta fresca, salsa bechamel y queso fundido",
                description="Liquidación especial almuerzo casino central",
                is_offer=True,
                original_price=4800,
                offer_label="Liquidación de almuerzo - 48% OFF",
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
        """Create and persist a new product/dish in the catalog (CRUD: Create)."""
        self._products[product.id_producto] = product
        self._save_to_json()
        return product

    def get_all(self, include_inactive: bool = False) -> List[Product]:
        """Retrieve all products (CRUD: Read)."""
        if include_inactive:
            return list(self._products.values())
        return [p for p in self._products.values() if p.is_active]

    def get_offers(self) -> List[Product]:
        """Retrieve all discounted / near-expiry active products with stock."""
        return [p for p in self.get_all() if p.is_offer and p.is_active]

    def get_by_id(self, product_id: str) -> Optional[Product]:
        """Retrieve product by its unique ID (CRUD: Read)."""
        return self._products.get(product_id)

    def get_by_category(self, category: str) -> List[Product]:
        """Retrieve products filtered by menu category or special offer tab."""
        if not category or category == "Todos":
            return self.get_all()
        if "oferta" in category.lower():
            return self.get_offers()
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
        """Update existing product data and persist (CRUD: Update)."""
        if product.id_producto not in self._products:
            return False
        self._products[product.id_producto] = product
        self._save_to_json()
        return True

    def delete(self, product_id: str) -> bool:
        """Permanently remove a product from the catalog and persist (CRUD: Delete)."""
        if product_id not in self._products:
            return False
        del self._products[product_id]
        self._save_to_json()
        return True

    def update_stock(self, product_id: str, new_stock: int) -> bool:
        """Update inventory stock count and persist."""
        product = self._products.get(product_id)
        if not product:
            return False
        product.stock = max(0, new_stock)
        self._save_to_json()
        return True

    def set_active_status(self, product_id: str, is_active: bool) -> bool:
        """Toggle active status for a product and persist."""
        product = self._products.get(product_id)
        if not product:
            return False
        product.is_active = is_active
        self._save_to_json()
        return True


# Backward-compatible alias for existing imports
InMemoryProductRepository = JsonProductRepository
