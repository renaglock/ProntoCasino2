"""Authentication service connecting to database and validating credentials."""

from typing import List, Optional, Tuple
from punto_casino.models.user import User, UserRole
from punto_casino.repositories.user_repository import UserRepository


class AuthService:
    """Manages active user session, credential authentication, and database wallet updates."""

    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo
        # Default session: Renato Escárate from DB
        default_user = self.user_repo.get_by_id("EST-01")
        if not default_user:
            default_user = User("EST-01", "Renato Escárate", UserRole.CLIENT, "renato@uct.cl", 0)
        self._current_user: User = default_user

    @property
    def current_user(self) -> User:
        """Currently authenticated user."""
        return self._current_user

    def authenticate_credentials(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and plain password against database hash."""
        user = self.user_repo.authenticate(email, password)
        if user:
            self._current_user = user
            return user
        return None

    def quick_login(self, role_key: str) -> Optional[User]:
        """Convenient quick authentication using verified database accounts."""
        role_map = {
            "estudiante": ("renato@uct.cl", "Renato2026!"),
            "cajero": ("cristian@uct.cl", "Cristian2026!"),
            "admin": ("admin@uct.cl", "Admin2026!"),
            "invitado": ("invitado@uct.cl", "Invitado2026!"),
        }
        creds = role_map.get(role_key.lower())
        if creds:
            return self.authenticate_credentials(creds[0], creds[1])
        return None

    def get_available_profiles(self) -> List[Tuple[str, str, str]]:
        """Return profiles for quick selection: (key, name, email)."""
        return [
            ("estudiante", "🎓 Estudiante (Renato)", "renato@uct.cl"),
            ("cajero", "🧑‍🍳 Cajero (Cristian - Sabor Único)", "cristian@uct.cl"),
            ("admin", "⚙️ Administrador General", "admin@uct.cl"),
            ("invitado", "👤 Invitado Público", "invitado@uct.cl"),
        ]

    def deduct_balance(self, amount: int) -> bool:
        """Atomically deduct balance from student in database."""
        user = self._current_user
        if user.role == UserRole.CLIENT:
            if user.balance < amount:
                return False
            new_balance = user.balance - amount
            success = self.user_repo.update_balance(user.id_usuario, new_balance)
            if success:
                user.balance = new_balance
                return True
            return False
        return True

    def refund_balance(self, amount: int) -> None:
        """Atomically refund balance to student in database."""
        user = self._current_user
        if user.role == UserRole.CLIENT:
            new_balance = user.balance + amount
            self.user_repo.update_balance(user.id_usuario, new_balance)
            user.balance = new_balance

    def refund_user_balance(self, user_id: Optional[str], amount: int) -> bool:
        """Atomically refund balance to any specific user ID in the database."""
        if not user_id or amount <= 0:
            return False
        user = self.user_repo.get_by_id(user_id)
        if not user or user.role != UserRole.CLIENT:
            return False
        new_balance = user.balance + amount
        success = self.user_repo.update_balance(user_id, new_balance)
        if success and self._current_user.id_usuario == user_id:
            self._current_user.balance = new_balance
        return success

