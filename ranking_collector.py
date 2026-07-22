from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

URL = "https://shopping.yahoo.co.jp/promotion/event/k-cosmetics/?sc_i=shopping-pc-web-top--icons-icon_lnk"

def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36")
    driver = webdriver.Chrome(options=options)
    return driver

def fetch_rendered_html():
    driver = get_driver()
    driver.get(URL)

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#cat-serum .elItem"))
        )
        print(" 상품 요소를 찾았습니다.")
    except Exception as e:
        print(f"타임아웃: {e}")
        print("일단 현재 페이지 상태를 저장합니다.")

    time.sleep(2)
    html = driver.page_source
    driver.quit()
    return html

if __name__ == "__main__":
    html = fetch_rendered_html()
    print(f"페이지 길이: {len(html)} 글자")

    with open("page_rendered.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("page_rendered.html로 저장했습니다.")