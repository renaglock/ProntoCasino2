"""User repository interacting directly with SQLite database."""

from typing import List, Optional
from punto_casino.models.user import User, UserRole
from punto_casino.repositories.database import DatabaseManager
from punto_casino.services.security import SecurityService


class UserRepository:
    """Provides secure database operations for users and credentials."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        self.db = db_manager

    def authenticate(self, email: str, plain_password: str) -> Optional[User]:
        """Authenticate user credentials using PBKDF2-HMAC-SHA256 and constant-time comparison."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id_usuario, name, email, password_hash, salt, role, balance, is_active
                FROM users
                WHERE lower(email) = lower(?)
                """,
                (email.strip(),),
            )
            row = cursor.fetchone()
            if not row:
                return None

            is_valid = SecurityService.verify_password(
                plain_password=plain_password,
                stored_hash_hex=row["password_hash"],
                salt_hex=row["salt"],
            )
            if not is_valid:
                return None

            return User(
                id_usuario=row["id_usuario"],
                name=row["name"],
                email=row["email"],
                role=UserRole(row["role"]),
                balance=row["balance"],
                is_active=bool(row["is_active"]),
            )

    def get_by_id(self, user_id: str) -> Optional[User]:
        """Fetch user by ID."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id_usuario, name, email, role, balance, is_active FROM users WHERE id_usuario = ?",
                (user_id,),
            )
            row = cursor.fetchone()
            if not row:
                return None
            return User(
                id_usuario=row["id_usuario"],
                name=row["name"],
                email=row["email"],
                role=UserRole(row["role"]),
                balance=row["balance"],
                is_active=bool(row["is_active"]),
            )

    def update_balance(self, user_id: str, new_balance: int) -> bool:
        """Update student cafeteria wallet balance."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET balance = ? WHERE id_usuario = ?",
                (new_balance, user_id),
            )
            conn.commit()
            return cursor.rowcount > 0

    def get_all(self) -> List[User]:
        """Retrieve all registered users."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id_usuario, name, email, role, balance, is_active FROM users")
            return [
                User(
                    id_usuario=r["id_usuario"],
                    name=r["name"],
                    email=r["email"],
                    role=UserRole(r["role"]),
                    balance=r["balance"],
                    is_active=bool(r["is_active"]),
                )
                for r in cursor.fetchall()
            ]

