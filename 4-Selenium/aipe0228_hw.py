# === 成品 ===

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
# from webdriver_manager.chrome import ChromeDriverManager
import time
import os, json

#嘗試典籍下一頁並抓取資料
def scrape_current_page(driver):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR,".c-listInfoGrid.c-listInfoGrid--gridCard ul li.c-listInfoGrid__item")
        )
    )
    razer_lists = driver.find_elements(By.CSS_SELECTOR, ".c-listInfoGrid.c-listInfoGrid--gridCard ul li.c-listInfoGrid__item")

    all_razer = []
    for razer_list in razer_lists:
            title = razer_list.find_element(By.CSS_SELECTOR, ".c-prodInfoV2__title")
            razer_name = title.get_attribute("title")
            razer_price = razer_list.find_element(By.CSS_SELECTOR, ".c-prodInfoV2__priceBar .c-prodInfoV2__price").text
            link = razer_list.find_element(By.CSS_SELECTOR, ".c-prodInfoV2__link.gtmClickV2")
            razer_link = link.get_attribute("href")
            if razer_link.startswith("/"):
                razer_link = "https://24h.pchome.com.tw" + razer_link
            img = razer_list.find_element(By.CSS_SELECTOR, ".c-prodInfoV2__head img")
            razer_imgsrc = img.get_attribute("src")
            
            all_razer.append({
                "name": razer_name,
                "price": razer_price,
                "link": razer_link,
                "img_src": razer_imgsrc
            })

    return all_razer

# ①建立 driver

def crawl_pchome(keyword:str ,pages: int = 18):
    service = Service()  # 如果 chromedriver 在 PATH 裡，這樣就可以；不行就要給 executable_path
    driver = webdriver.Chrome(service=service)
    all_razer = []

    url = f"https://24h.pchome.com.tw/search/?q={keyword}"
    driver.get(url)



    for page in range(1, pages+1):
        print(f"=== 查詢商品: {keyword} : 現在是第 {page} 頁 ===")        
        items = scrape_current_page(driver)
        all_razer.extend(items)

        if page == pages:
            break
        
        try:
            next_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, ".c-pagination__button.is-next")
                )
            )
            next_btn.click()
            time.sleep(2)
        except TimeoutException:
            print("找不到下一頁按鈕，提前結束。")
            break
    driver.quit

    filename = f"{keyword}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(all_razer, f, ensure_ascii=False, indent=2)

    print(f"{keyword} 總共抓到 {len(all_razer)} 筆，已輸出到 {filename}")
    return all_razer

# 呼叫 function crawl_pchome
crawl_pchome("razer")
        