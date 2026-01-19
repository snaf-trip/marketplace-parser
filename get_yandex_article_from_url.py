import re
from urllib.parse import urlparse

def get_yandex_market_article_from_url(url: str) -> str | None:
    """
    Извлекает артикул Яндекс Маркета из ссылки.
    Пример:
    https://market.yandex.ru/card/.../4889856746?do-waremd5=...
    -> 4889856746
    """
    try:
        parsed = urlparse(url)
        path = parsed.path.rstrip("/")
    except Exception:
        return None

    # Берём последнее число в path
    match = re.search(r"/(\d{6,})$", path)
    if match:
        return match.group(1)

    return None
