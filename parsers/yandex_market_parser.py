from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def parse_yandex_market(driver):
    data = {"название": "", "цена": "", "оценка": "", "артикул": ""}
    print("parse_yandex_market started...")
    try:
        el_name = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "h1.ds-text")
            )
        )
        data["название"] = el_name.text.strip()
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

