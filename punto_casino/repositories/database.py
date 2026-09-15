"""SQLite Database Manager with WAL mode and ACID transaction support."""

import os
import sqlite3
from typing import Any, Dict, List, Optional
from punto_casino.services.security import SecurityService


class DatabaseManager:
    """Manages SQLite database connections, schema migrations, and secure seeding."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        if db_path is None:
            root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            db_path = os.path.join(root_dir, "punto_casino.db")
        self.db_path = db_path
        self._init_database()

    def get_connection(self) -> sqlite3.Connection:
        """Create and configure a thread-safe connection with WAL mode."""
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        # Enable WAL mode for high concurrency (non-blocking readers/writers)
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        return conn

    def _init_database(self) -> None:
        """Create tables and seed initial data if necessary."""
        with self.get_connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id_usuario TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    role TEXT NOT NULL,
                    balance INTEGER DEFAULT 0,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS products (
                    id_producto TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    price INTEGER NOT NULL,
                    stock INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    ingredients TEXT,
                    is_active INTEGER DEFAULT 1
                );

                CREATE TABLE IF NOT EXISTS orders (
                    id_pedido TEXT PRIMARY KEY,
                    comanda_number INTEGER NOT NULL,
                    customer_id TEXT NOT NULL,
                    customer_name TEXT NOT NULL,
                    total INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    pickup_qr TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(customer_id) REFERENCES users(id_usuario)
                );
                """
            )
            self._seed_users(conn)
            self._seed_products(conn)

    def _seed_users(self, conn: sqlite3.Connection) -> None:
        """Seed initial secure accounts if users table is empty."""
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            accounts = [
                ("EST-01", "Renato Escárate", "renato@uct.cl", "Renato2026!", "CLIENT", 0),
                ("CAJ-01", "Cristian (Sabor Único)", "cristian@uct.cl", "Cristian2026!", "CASHIER", 0),
                ("ADM-01", "Administrador General", "admin@uct.cl", "Admin2026!", "ADMIN", 0),
                ("INV-01", "Invitado Público", "invitado@uct.cl", "Invitado2026!", "GUEST", 0),
            ]
            for uid, name, email, raw_pwd, role, balance in accounts:
                pwd_hash, salt = SecurityService.hash_password(raw_pwd)
                conn.execute(
                    """
                    INSERT INTO users (id_usuario, name, email, password_hash, salt, role, balance)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (uid, name, email, pwd_hash, salt, role, balance),
                )
            conn.commit()

    def _seed_products(self, conn: sqlite3.Connection) -> None:
        """Seed wireframe products if products table is empty."""
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products")
        if cursor.fetchone()[0] == 0:
            seed_dishes = [
                ("MENU-01", "Pastel de Choclo", 4800, 25, "Menú Normal", "Carne de vacuno, maíz dulce, huevo | Ensalada | Postre"),
                ("MENU-02", "Escalopa Kaiser con Puré", 6500, 20, "Menú Ejecutivo", "Escalopa con jamón y queso | Puré rústico | Postre"),
                ("MENU-03", "Pollo a la Plancha y Arroz", 4600, 18, "Menú Hipocalórico", "Pechuga de pollo a las hierbas | Arroz integral | Verduras"),
                ("MENU-04", "Lasaña de Berenjenas", 4500, 15, "Menú Vegetariano", "Berenjenas asadas, espinaca fresca, bechamel y mozzarella"),
                ("RAP-01", "Empanada de Pino Horno", 2000, 30, "Comidas Rápidas", "Masa tradicional, pino de carne, aceituna y huevo"),
                ("RAP-02", "Completo Italiano", 2500, 35, "Comidas Rápidas", "Pan lengua tostado, vienesa, tomate, palta y mayo casera"),
                ("BEB-01", "Café de Grano", 1200, 50, "Bebidas", "Café espresso recién molido caliente"),
                ("BEB-02", "Jugo Natural 500ml", 1800, 25, "Bebidas", "Jugo 100% natural de fruta de temporada"),
            ]
            for pid, name, price, stock, cat, ing in seed_dishes:
                conn.execute(
                    """
                    INSERT INTO products (id_producto, name, price, stock, category, ingredients, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, 1)
                    """,
                    (pid, name, price, stock, cat, ing),
                )
            conn.commit()
