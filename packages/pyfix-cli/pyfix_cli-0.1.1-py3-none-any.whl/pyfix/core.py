# pyfix/core.py
import sys
import yaml
import os
from pathlib import Path

# Путь к базе ошибок
DATA_PATH = Path(__file__).parent / "errors.yaml"


def load_error_db():
    with open(DATA_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


ERROR_DB = load_error_db()


def explain_error(exc_type, exc_value, exc_traceback):
    """Генерирует дружелюбное объяснение ошибки на русском"""
    exc_name = exc_type.__name__
    msg = str(exc_value)

    # Ищем по точному типу + ключевым словам
    for pattern, data in ERROR_DB.items():
        if pattern == exc_name or (pattern.startswith(exc_name + ":") and pattern.split(":", 1)[1] in msg):
            return format_explanation(data, msg)

    # Дефолтное объяснение
    return f"🔹 {exc_name}: {msg}\n\n💡 Нет специального объяснения. Попробуйте `pyfix explain \"{exc_name}\"`"


def format_explanation(data, msg):
    lines = []
    lines.append(f"🔹 {data.get('title', 'Ошибка')}")
    if "why" in data:
        lines.append(f"🧠 Почему: {data['why']}")
    if "how_to_fix" in data:
        lines.append(f"🛠 Как починить:")
        for i, step in enumerate(data["how_to_fix"], 1):
            lines.append(f"   {i}. {step}")
    if "example" in data:
        lines.append(f"\n📋 Пример:")
        lines.append("   " + data["example"].replace("\n", "\n   "))
    if "common_in" in data:
        lines.append(f"\n📌 Часто встречается у: {', '.join(data['common_in'])}")
    return "\n".join(lines)


def global_excepthook(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    print("\n" + "=" * 60)
    print("🚨 pyfix: дружелюбное объяснение ошибки")
    print("=" * 60)
    print(explain_error(exc_type, exc_value, exc_traceback))
    print("=" * 60)
    print("💡 Совет: включите pyfix: `import pyfix; pyfix.enable()`")
    print()


def enable_auto_explain():
    sys.excepthook = global_excepthook