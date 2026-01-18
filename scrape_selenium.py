#!/usr/bin/env python3
"""
Парсер маркетплейсов (Ozon / Wildberries / Yandex Market)
с защитой от проверки устройства.
"""

import time
import random
from urllib.parse import urlparse
import tldextract
import pandas as pd

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import undetected_chromedriver as uc


# ---------------------------
# Парсеры маркетплейсов
# ---------------------------

def parse_ozon(driver):
    data = {"название": "", "цена": "", "оценка": "", "артикул": ""}

    try:
        data["название"] = driver.find_element(By.TAG_NAME, "h1").text.strip()
    except:
        pass

    for el in driver.find_elements(By.TAG_NAME, "span"):
        txt = el.text.strip()
        if "₽" in txt:
            data["цена"] = txt
            break

    for el in driver.find_elements(By.TAG_NAME, "div"):
        txt = el.text.strip()
        if "•" in txt and "отзыв" in txt:
            data["оценка"] = txt.split("•")[0].strip()
            break

    for el in driver.find_elements(By.TAG_NAME, "div"):
        txt = el.text.strip()
        if txt.startswith("Артикул"):
            data["артикул"] = txt.replace("Артикул:", "").strip()
            break

    return data


def parse_wildberries(driver):
    data = {"название": "", "цена": "", "оценка": "", "артикул": ""}

    try:
        data["название"] = driver.find_element(By.TAG_NAME, "h3").text.strip()
    except:
        pass

    for el in driver.find_elements(By.TAG_NAME, "h2"):
        txt = el.text.strip()
        if "₽" in txt:
            data["цена"] = txt
            break

    for el in driver.find_elements(By.TAG_NAME, "span"):
        txt = el.text.strip()
        if "·" in txt and "оцен" in txt:
            data["оценка"] = txt.split("·")[0].strip()
            break

    for el in driver.find_elements(By.TAG_NAME, "span"):
        txt = el.text.strip()
        if txt.isdigit() and len(txt) >= 6:
            data["артикул"] = txt
            break

    return data


def parse_yandex_market(driver):
    data = {"название": "", "цена": "", "оценка": "", "артикул": ""}

    try:
        data["название"] = driver.find_element(
            By.CSS_SELECTOR, 'h1[data-auto="productCardTitle"]'
        ).text.strip()
    except:
        pass

    try:
        data["цена"] = driver.find_element(
            By.CSS_SELECTOR, 'span[data-auto="snippet-price-current"]'
        ).text.replace("\n", "").strip()
    except:
        pass

    try:
        data["оценка"] = driver.find_element(
            By.CSS_SELECTOR, 'span[data-auto="ratingValue"]'
        ).text.strip()
    except:
        pass

    specs = driver.find_elements(By.CSS_SELECTOR, 'span[data-auto="product-spec"]')
    for spec in specs:
        if "Артикул" in spec.text:
            parent = spec.find_element(By.XPATH, "../..")
            for sp in parent.find_elements(By.TAG_NAME, "span"):
                if sp.text.strip().isdigit():
                    data["артикул"] = sp.text.strip()
                    break

    return data


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

    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )

    domain = get_root_domain(url)

    if domain == "ozon.ru":
        parsed = parse_ozon(driver)
    elif domain == "wildberries.ru":
        parsed = parse_wildberries(driver)
    elif domain == "market.yandex.ru":
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
    for site in ["https://www.ozon.ru", "https://www.wildberries.ru", "https://market.yandex.ru"]:
        driver.get(site)
        time.sleep(random.uniform(4, 6))

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
