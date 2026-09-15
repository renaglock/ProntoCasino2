"""Currency and date formatting utilities for Chilean Peso (CLP)."""

from datetime import datetime


def format_currency(amount: int) -> str:
    """Format integer amount as Chilean Peso string (e.g., 2000 -> '$2.000')."""
    formatted_number = f"{amount:,}".replace(",", ".")
    return f"${formatted_number}"


def format_datetime(dt: datetime) -> str:
    """Format datetime into standard cafeteria receipt date format."""
    return dt.strftime("%d/%m/%Y %H:%M")

