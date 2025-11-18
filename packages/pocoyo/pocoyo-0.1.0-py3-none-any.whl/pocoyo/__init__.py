"""
Pocoyo Library - Простая библиотека для Telegram ботов и баз данных
"""

from .telegram_bot import SimpleBot
from .text_database import TextDatabase
from .sqlite_database import SQLiteDatabase

__all__ = ['SimpleBot', 'TextDatabase', 'SQLiteDatabase']

__version__ = "0.1.0"
__author__ = "pocoyodev"