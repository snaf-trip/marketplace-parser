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

    return data

