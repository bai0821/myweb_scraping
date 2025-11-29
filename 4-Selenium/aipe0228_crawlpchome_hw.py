# === 修改作品 ===

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
# from webdriver_manager.chrome import ChromeDriverManager
import time
import os, json


#滾輪
def scroll_to_bottom(driver, step=800):
    current = 0
    while True:
        driver.execute_script(f"window.scrollTo(0, {current});")
        current += step
        time.sleep(0.05)
        # 每次往下滾一段，直到超過目前頁面的總高度就停
        if current >= driver.execute_script("return document.body.scrollHeight"):
            break

#嘗試典籍下一頁並抓取資料
def scrape_current_page(driver):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR,".c-listInfoGrid.c-listInfoGrid--gridCard ul li.c-listInfoGrid__item")
        )
    )

    scroll_to_bottom(driver)


    razer_lists = driver.find_elements(By.CSS_SELECTOR, ".c-listInfoGrid.c-listInfoGrid--gridCard ul li.c-listInfoGrid__item")

    max_wait = 5
    start = time.time()
    while True:
        imgs = driver.find_elements(By.CSS_SELECTOR, ".c-prodInfoV2__head img")
        
        if not imgs:
            if time.time() - start > max_wait:
                break
            time.sleep(0.2)
            continue

        last_src = imgs[-1].get_attribute("src") or ""
        if not last_src.endswith(".svg"):
            break
        
        if time.time() -start > max_wait:
            break
        
        time.sleep(0.2)

    all_razer = []
    for razer_list in razer_lists:
        try:
            title_els = razer_list.find_elements(By.CSS_SELECTOR, ".c-prodInfoV2__title")
            if not title_els:
                continue
            title = title_els[0]
            razer_name = title.get_attribute("title") or title.text

            price_els = razer_list.find_element(By.CSS_SELECTOR, ".c-prodInfoV2__priceBar .c-prodInfoV2__price").text
            if price_els:
                razer_price = price_els
            else:
                razer_price = None


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
        except NoSuchElementException as e:
            # 這個 li 長得太奇怪，乾脆整個跳過
            print("某個商品結構怪怪的，跳過：", e)
            continue

    return all_razer

# 建立 driver

def crawl_pchome(keyword:str):
    service = Service() 
    driver = webdriver.Chrome(service=service)
    all_razer = []

    url = f"https://24h.pchome.com.tw/search/?q={keyword}"
    driver.get(url)

    page = 1
    max_pages = 100
    seen_first_links= set()

    while True:
        print(f"=== 查詢商品: {keyword} : 現在是第 {page} 頁 ===")       
        items = scrape_current_page(driver)
        print(f"第 {page} 頁抓到 {len(items)} 筆")
         # 這一頁完全沒商品 → 提早結束
        if not items:
            print("這一頁沒有商品，提前結束。")
            break

        #檢查這一頁是不是「跟之前某一頁重複」
        #用這一頁第一個商品的 link 當代表
        first_link = items[0]["link"]
        if first_link in seen_first_links:
            print("這一頁跟之前的某一頁內容一樣，應該已經是最後一頁，結束。")
            break
        seen_first_links.add(first_link)
        all_razer.extend(items)

        if page >= max_pages:
            print(f"已達安全上限 {max_pages} 頁，先停止，避免卡死。")
            break
        
        try:
            next_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, ".c-pagination__button.is-next")
                )
            )
            next_btn.click()
            page += 1  # 頁碼 +1
            time.sleep(2)
        except TimeoutException:
            print("找不到下一頁按鈕，提前結束。")
            break


    driver.quit()

    filename = f"{keyword}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(all_razer, f, ensure_ascii=False, indent=2)

    print(f"{keyword} 總共抓到 {len(all_razer)} 筆，已輸出到 {filename}")
    return all_razer

# 呼叫 function crawl_pchome
#使用方法! 改裡面的keyword就好
crawl_pchome("衛生紙")
        