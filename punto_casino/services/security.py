"""Cryptographic security service following NIST SP 800-63B and OWASP standards."""

import hashlib
import secrets
from typing import Tuple


class SecurityService:
    """Provides bank-grade password hashing, salting, and timing-safe verification."""

    ITERATIONS: int = 600_000  # OWASP 2024 recommended minimum for PBKDF2-HMAC-SHA256
    SALT_BYTES: int = 32       # 256 bits of cryptographic entropy

    @classmethod
    def hash_password(cls, plain_password: str) -> Tuple[str, str]:
        """Generate secure cryptographic hash and salt for a password.

        Returns:
            Tuple[str, str]: (password_hash_hex, salt_hex)
        """
        salt = secrets.token_bytes(cls.SALT_BYTES)
        derived_key = hashlib.pbkdf2_hmac(
            hash_name="sha256",
            password=plain_password.encode("utf-8"),
            salt=salt,
            iterations=cls.ITERATIONS,
        )
        return derived_key.hex(), salt.hex()

    @classmethod
    def verify_password(
        cls, plain_password: str, stored_hash_hex: str, salt_hex: str
    ) -> bool:
        """Verify password in constant time to prevent side-channel timing attacks.

        Returns:
            bool: True if valid, False otherwise.
        """
        try:
            salt = bytes.fromhex(salt_hex)
            computed_key = hashlib.pbkdf2_hmac(
                hash_name="sha256",
                password=plain_password.encode("utf-8"),
                salt=salt,
                iterations=cls.ITERATIONS,
            )
            return secrets.compare_digest(computed_key.hex(), stored_hash_hex)
        except (ValueError, TypeError):
            return False

