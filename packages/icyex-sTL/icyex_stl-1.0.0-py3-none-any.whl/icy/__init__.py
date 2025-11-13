"""
icyex-sTL - Telegram User Information Extractor
Extract detailed user information from Telegram with risk analysis
"""

from .client import TelegramUserExtractor
from .models import UserInfo

__version__ = "1.0.0"
__author__ = "IcyEx"
__all__ = ["TelegramUserExtractor", "UserInfo"]

