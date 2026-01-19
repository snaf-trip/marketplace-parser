import re
from urllib.parse import urlparse

def get_wb_article_from_url(url: str) -> str | None:
    """
    Извлекает артикул Wildberries из ссылки.
    Пример:
    https://www.wildberries.ru/catalog/411454492/detail.aspx -> 411454492
    """
    try:
        path = urlparse(url).path
    except Exception:
        return None

    match = re.search(r"/catalog/(\d+)", path)
    if match:
        return match.group(1)

    return None
