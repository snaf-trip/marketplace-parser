from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def parse_wildberries(driver):
    data = {"название": "", "цена": "", "оценка": "", "артикул": ""}

    # 1) название (h3 с классом productTitle)
    try:
        el_name = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "h3.productTitle--J2W7I")
            )
        )
        data["название"] = el_name.text.strip()
    except:
        pass

    # 2) цена (h2 с классом productPrice)
    try:
        el_price = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "h2.mo-typography_variant_title2.mo-typography_color_danger")
            )
        )
        data["цена"] = el_price.text.strip()
    except:
        pass

    # 3) оценка (span с классом productReviewRating)
    try:
        el_rating = driver.find_element(
            By.CSS_SELECTOR, "span.productReviewRating--gQDQG"
        )
        data["оценка"] = el_rating.text.split("·")[0].strip()  # только рейтинг, без кол-ва оценок
    except:
        pass

    # 4) артикул — часто последний span с цифрами длиннее 6
    try:
        spans = driver.find_elements(By.TAG_NAME, "span")
        for sp in spans[::-1]:  # идем с конца страницы
            txt = sp.text.strip()
            if txt.isdigit() and len(txt) >= 6:
                data["артикул"] = txt
                break
    except:
        pass

    return data
