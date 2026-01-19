import re
from urllib.parse import urlparse

def get_ozon_article_from_url(url: str) -> str | None:
    """
    Извлекает артикул Ozon из ссылки.
    Примеры:
    https://www.ozon.ru/product/krossovki-nk-2317540083/
    -> 2317540083
    """
    try:
        path = urlparse(url).path.rstrip("/")
    except Exception:
        return None

    # Берём последнее число после дефиса
    match = re.search(r"-(\d{6,})$", path)
    if match:
        return match.group(1)

    return None
