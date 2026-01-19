from parsers.ozon_parser import parse_ozon
from parsers.wb_parser import parse_wildberries
from parsers.yandex_market_parser import parse_yandex_market

MARKETPLACE_CONFIG = {
    "ozon": {
        "domain": "ozon.ru",
        "base_url": "https://www.ozon.ru",
        "parser": parse_ozon,
        "wait_tag": "h1",
        "warmup_time": 25,
    },
    "wildberries": {
        "domain": "wildberries.ru",
        "base_url": "https://www.wildberries.ru",
        "parser": parse_wildberries,
        "wait_tag": "h3",
        "warmup_time": 25,
    },
    "yandex_market": {
        "domain": "market.yandex.ru",
        "base_url": "https://market.yandex.ru",
        "parser": parse_yandex_market,
        "wait_tag": '[data-auto="productCardTitle"]',
        "warmup_time": 25
    },
}
