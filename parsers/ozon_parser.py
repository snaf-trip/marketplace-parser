from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

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

    return data

