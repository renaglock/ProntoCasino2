"""User and Role domain models with student cafeteria balance."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class UserRole(str, Enum):
    """User privilege roles supported by Pronto Casino UCT."""

    CLIENT = "CLIENT"      # Student / Regular customer (Renato)
    CASHIER = "CASHIER"    # Kitchen & cashier operator (Cristian / Sabor Único)
    ADMIN = "ADMIN"        # Store manager with CRUD permissions
    GUEST = "GUEST"        # Walk-in unauthenticated customer


@dataclass
class User:
    """User entity representing students, cashiers, and administrators."""

    id_usuario: str
    name: str
    role: UserRole
    email: Optional[str] = None
    balance: int = 15000  # Student cafeteria wallet in CLP
    is_active: bool = True
