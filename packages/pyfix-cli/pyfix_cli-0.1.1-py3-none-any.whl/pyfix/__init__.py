# pyfix/__init__.py
from .core import enable_auto_explain

def enable():
    """Включить дружелюбные объяснения ошибок"""
    enable_auto_explain()

# Для совместимости: auto = enable (как callable)
auto = enable