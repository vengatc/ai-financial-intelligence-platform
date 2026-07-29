"""Utility functions for the AI Financial Intelligence Platform."""

import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def get_timestamp() -> str:
    """Get current timestamp as ISO format string."""
    return datetime.now().isoformat()


def format_currency(amount: float, currency: str = "USD") -> str:
    """Format a number as currency string."""
    symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "INR": "₹",
    }
    symbol = symbols.get(currency, currency)
    return f"{symbol}{amount:,.2f}"


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """Calculate percentage change between two values."""
    if old_value == 0:
        return 0.0
    return ((new_value - old_value) / abs(old_value)) * 100