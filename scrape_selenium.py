#!/usr/bin/env python3
"""
Простой шаблон парсера на Selenium.
- Ввод ссылок вручную: пустая строка или 'done' -> окончание ввода
- Определение домена (tldextract)
- Для каждого домена используются CSS-селекторы из SELECTOR_CONFIG
- Результат сохраняется в output.md и output.csv
"""

import time
import random
from urllib.parse import urlparse
import tldextract
import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc



# ---------------------------
# Конфигурация селекторов
# ---------------------------
# Здесь ты будешь подставлять конкретные селекторы для маркетплейсов.
# Формат: "domain.tld": {"name": "selector1, selector2", "price": "...", "rating": "...", "sku": "..."}
# Если домен нет в конфиге, используется "default".
SELECTOR_CONFIG = {
    "ozon.ru": {
        # Название товара
        "name": "h1[data-widget='webProductHeading'], h1",

        # Цена (на Ozon несколько вариантов)
        "price": "span[data-widget='webPrice'] span, div[data-widget='webPrice'] span",

        # Рейтинг
        "rating": "div[data-widget='webReviewRating'] span",

        # Артикул (часто скрыт — берём из блока характеристик)
        "sku": "div[data-widget='webCharacteristics'] span"
    },

    "wildberries.ru": {
        "name": "h1",
        "price": "span.price-block__final-price, span.price-block__wallet-price",
        "rating": "span.product-review__rating",
        "sku": "span.product-article__number"
    },

    "market.yandex.ru": {
        "name": "h1[data-auto='productCardTitle'], h1",

        "price": "span[data-auto='snippet-price-current'], span[data-auto='price-value']",

        "rating": "span[data-auto='rating-value']",

        # Артикул у ЯМ редко явно виден — иногда есть, иногда нет
        "sku": "div[data-auto='sku'], span[data-auto='sku']"
    },

    # fallback
    "default": {
        "name": "h1",
        "price": "[itemprop='price'], .price",
        "rating": "[itemprop='ratingValue'], .rating",
        "sku": "[itemprop='sku'], .sku"
    }
}

def parse_ozon(driver):
    data = {
        "название": "",
        "цена": "",
        "оценка": "",
        "артикул": ""
    }

    # Название
    try:
        data["название"] = driver.find_element(By.TAG_NAME, "h1").text.strip()
    except:
        pass

    # Цена
    for el in driver.find_elements(By.TAG_NAME, "span"):
        txt = el.text.strip()
        if "₽" in txt:
            data["цена"] = txt
            break

    # Оценка
    for el in driver.find_elements(By.TAG_NAME, "div"):
        txt = el.text.strip()
        if "•" in txt and "отзыв" in txt:
            data["оценка"] = txt.split("•")[0].strip()
            break

    # Артикул
    for el in driver.find_elements(By.TAG_NAME, "div"):
        txt = el.text.strip()
        if txt.startswith("Артикул"):
            data["артикул"] = txt.replace("Артикул:", "").strip()
            break

    return data

def parse_wildberries(driver):
    data = {
        "название": "",
        "цена": "",
        "оценка": "",
        "артикул": ""
    }

    # Название
    try:
        data["название"] = driver.find_element(By.TAG_NAME, "h3").text.strip()
    except:
        pass

    # Цена
    for el in driver.find_elements(By.TAG_NAME, "h2"):
        txt = el.text.strip()
        if "₽" in txt:
            data["цена"] = txt
            break

    # Оценка
    for el in driver.find_elements(By.TAG_NAME, "span"):
        txt = el.text.strip()
        if "·" in txt and "оцен" in txt:
            data["оценка"] = txt.split("·")[0].strip()
            break

    # Артикул
    for el in driver.find_elements(By.TAG_NAME, "span"):
        txt = el.text.strip()
        if txt.isdigit() and len(txt) >= 6:
            data["артикул"] = txt
            break

    return data

def parse_yandex_market(driver):
    data = {
        "название": "",
        "цена": "",
        "оценка": "",
        "артикул": ""
    }

    # Название
    try:
        data["название"] = driver.find_element(
            By.CSS_SELECTOR,
            'h1[data-auto="productCardTitle"]'
        ).text.strip()
    except:
        pass

    # Цена
    try:
        data["цена"] = driver.find_element(
            By.CSS_SELECTOR,
            'span[data-auto="snippet-price-current"]'
        ).text.replace("\n", "").strip()
    except:
        pass

    # Оценка
    try:
        data["оценка"] = driver.find_element(
            By.CSS_SELECTOR,
            'span[data-auto="ratingValue"]'
        ).text.strip()
    except:
        pass

    # Артикул Маркета
    spec_blocks = driver.find_elements(By.CSS_SELECTOR, 'span[data-auto="product-spec"]')
    for spec in spec_blocks:
        if "Артикул" in spec.text:
            parent = spec.find_element(By.XPATH, "../..")
            spans = parent.find_elements(By.TAG_NAME, "span")
            for sp in spans:
                txt = sp.text.strip()
                if txt.isdigit():
                    data["артикул"] = txt
                    break

    return data



# ---------------------------
# Утилиты
# ---------------------------
def get_root_domain(url: str) -> str:
    """Возвращает eTLD+1 (например: amazon.com, ozon.ru)"""
    try:
        ext = tldextract.extract(url)
        if ext.suffix:
            return f"{ext.domain}.{ext.suffix}"
        return ext.domain
    except Exception:
        # fallback: взять netloc
        return urlparse(url).netloc

def pick_selectors_for_domain(domain: str) -> dict:
    """Берёт конфиг селекторов для домена, иначе default"""
    return SELECTOR_CONFIG.get(domain, SELECTOR_CONFIG["default"])

def find_any_text(driver: webdriver.Chrome, selector_list: str) -> str:
    """
    selector_list - строка, где селекторы разделены запятыми.
    Возвращает текст первого найденного элемента.
    """
    for sel in [s.strip() for s in selector_list.split(",")]:
        if not sel:
            continue
        try:
            elems = driver.find_elements(By.CSS_SELECTOR, sel)
            if elems:
                # объединяем текст всех найденных элементов (обычно первый)
                texts = [e.text.strip() for e in elems if e.text.strip()]
                if texts:
                    return texts[0]
        except Exception:
            continue
    return ""

# ---------------------------
# Парсинг одной страницы
# ---------------------------
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

    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )

    domain = get_root_domain(url)

    if domain == "ozon.ru":
        parsed = parse_ozon(driver)

    elif domain == "wildberries.ru":
        parsed = parse_wildberries(driver)  # сделаем позже

    elif domain == "market.yandex.ru":
        parsed = parse_yandex_market(driver)  # тоже позже

    else:
        print(f"[WARN] Неизвестный маркетплейс: {domain}")
        parsed = {}

    # Объединяем данные
    for key in ["название", "цена", "оценка", "артикул"]:
        data[key] = parsed.get(key, "")

    return data


# ---------------------------
# Основная логика
# ---------------------------
def main():
    print("=== Парсер маркетплейсов (Selenium) ===")
    print("Вставляй ссылки по одной и нажимай Enter.")
    print("Чтобы закончить ввод — оставь строку пустой или введи 'done'.\n")

    # Считываем ссылки
    urls = []
    while True:
        try:
            u = input(f"Ссылка #{len(urls)+1}: ").strip()
        except (EOFError, KeyboardInterrupt):
            # Ctrl+D / Ctrl+C -> заканчиваем ввод
            print("\nВвод завершён.")
            break
        if u == "" or u.lower() == "done":
            break
        urls.append(u)
        print(f"Добавлено: {u} (всего ссылок: {len(urls)})")

    if not urls:
        print("Нет ссылок — выходим.")
        return

    # Настройка Selenium (Chrome). Поставь headless=False, если хочешь видеть окно браузера.
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # options.add_argument("--headless=new")  # если хочешь без GUI: раскомментируй
    # Можно рандомизировать User-Agent при желании:
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                         "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")

    print("\nЗапускаю браузер...")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.set_window_size(1200, 900)

    results = []
    try:
        for i, url in enumerate(urls, start=1):
            print(f"\n[{i}/{len(urls)}] Парсинг: {url}")
            try:
                row = parse_product_page(driver, url)
                print("  Название:", (row["название"] or "<не найдено>")[:120])
                print("  Цена   :", row["цена"] or "<не найдено>")
                print("  Оценка :", row["оценка"] or "<не найдено>")
                print("  Артикул:", row["артикул"] or "<не найдено>")
                results.append(row)
            except Exception as e:
                print("  Ошибка при парсинге:", e)
            # Политичный отдых между запросами
            time.sleep(1.0 + random.random()*2.0)
    finally:
        driver.quit()

    # Сохранение результатов
    df = pd.DataFrame(results, columns=["название", "цена", "оценка", "артикул", "фото", "ссылка"])
    # Сохраняем в CSV и Markdown
    df.to_csv("output.csv", index=False, encoding="utf-8-sig")
    try:
        md = df.to_markdown(index=False)
    except Exception:
        # Если не получилось через pandas (редко), делаем через простой формат вручную
        md = df.to_csv(index=False, sep="|")
    with open("output.md", "w", encoding="utf-8") as f:
        f.write(md)

    print("\nГотово! Результаты сохранены в: output.csv и output.md")
    print("Пример Markdown-таблицы (первые строки):\n")
    print(md.splitlines()[:15])

if __name__ == "__main__":
    main()

