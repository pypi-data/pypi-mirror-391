import json, hashlib, secrets, string
from datetime import datetime

def now_str() -> str:
    """Возвращает текущий timestamp в строковом формате."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def gen_token(length: int = 32) -> str:
    """Генерация безопасного токена."""
    return secrets.token_hex(length // 2)

def hash_text(text: str) -> str:
    """Хэширование строки SHA256."""
    return hashlib.sha256(text.encode()).hexdigest()

def random_string(length: int = 8) -> str:
    """Случайная строка (для тестовых логинов, кодов и т.п.)."""
    return "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))

def pretty_json(data) -> str:
    """Красивый JSON-вывод (удобно для логов и отладки)."""
    return json.dumps(data, indent=4, ensure_ascii=False)