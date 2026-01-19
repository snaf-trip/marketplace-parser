#!/usr/bin/env python3
"""
Парсер маркетплейсов (Ozon / Wildberries / Yandex Market)
с защитой от проверки устройства.
"""

import time
import random
import tldextract
import pandas as pd

import undetected_chromedriver as uc

from parsers.wb_parser import parse_wildberries
from parsers.ozon_parser import parse_ozon
from parsers.yandex_market_parser import parse_yandex_market

from ask_marketplace import ask_marketplace
from markets_config import  MARKETPLACE_CONFIG

# ---------------------------
# Утилиты
# ---------------------------

def get_root_domain(url: str) -> str:
    ext = tldextract.extract(url)
    return f"{ext.domain}.{ext.suffix}" if ext.suffix else ext.domain


def parse_product_page(driver, url):
    data = {
        "название": "",
        "цена": "",
        "оценка": "",
        "артикул": "",
        "фото": "img",
        "ссылка": url
    }

    driver.get(url)

    # WebDriverWait(driver, 20).until(
    #     EC.presence_of_element_located((By.TAG_NAME, "h1"))
    # )

    domain = get_root_domain(url)
    print(domain)

    if domain == "ozon.ru":
        parsed = parse_ozon(driver)
    elif domain == "wildberries.ru":
        parsed = parse_wildberries(driver)
    elif domain == "yandex.ru":
        parsed = parse_yandex_market(driver)
    else:
        parsed = {}

    for k in ["название", "цена", "оценка", "артикул"]:
        data[k] = parsed.get(k, "")

    return data


# ---------------------------
# Основная логика
# ---------------------------

def main():
    print("=== Парсер маркетплейсов ===")
    urls = []

    marketplace = ask_marketplace()
    config = MARKETPLACE_CONFIG[marketplace]

    print(f"\n✅ Выбран маркетплейс: {marketplace}")


    while True:
        u = input(f"Ссылка #{len(urls)+1}: ").strip()
        if not u or u.lower() == "done":
            break
        urls.append(u)
        print(f"Добавлено ({len(urls)})")

    if not urls:
        print("Нет ссылок — выход.")
        return

    # --- undetected Chrome ---
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0.0.0 Safari/537.36"
    )

    print("\nЗапуск браузера...")
    driver = uc.Chrome(options=options)

    # 🔥 Прогрев
    # for site in ["https://www.ozon.ru", "https://www.wildberries.ru", "https://market.yandex.ru"]:
    for site in [config["base_url"]]:
        driver.get(site)
        time.sleep(25)

    # 1. Пользователь выбирает с каким маркет плейсом работает
    # 2. скидывает артикли через запятую или ссылки оставить...?
    # 3. ссылки мы потом создаём сами используя артикль и константу url
    # 4. с прогревом тоже становится удобнее работать благодаря первому пункту


    results = []

    try:
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] {url}")
            row = parse_product_page(driver, url)

            print("  Название:", row["название"] or "<нет>")
            print("  Цена   :", row["цена"] or "<нет>")
            print("  Оценка :", row["оценка"] or "<нет>")
            print("  Артикул:", row["артикул"] or "<нет>")

            results.append(row)
            time.sleep(random.uniform(3, 6))
    finally:
        driver.quit()

    df = pd.DataFrame(results)
    df.to_csv("output.csv", index=False, encoding="utf-8-sig")
    with open("output.md", "w", encoding="utf-8") as f:
        f.write(df.to_markdown(index=False))

    print("\n✅ Готово: output.csv и output.md")


if __name__ == "__main__":
    main()
