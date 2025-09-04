from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import json
import time


def scrape_flipkart(query):
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get("https://www.flipkart.com")

        # Close login popup
        try:
            close_btn = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(text(),'✕')]"))
            )
            close_btn.click()
        except:
            pass

        # Search product
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)

        time.sleep(3)

        # Try catching any link that matches the pattern
        product_link = None
        links = driver.find_elements(By.XPATH, '//a[contains(@href, "/p/") and @rel="noopener noreferrer"]')

        print(f"[DEBUG] Found {len(links)} <a> tags matching generic product pattern")

        if links:
            product_link = links[0].get_attribute("href")
        else:
            return {"site": "Flipkart", "error": "No valid product found on Flipkart"}

        driver.get(product_link)
        time.sleep(2)

        try:
            title = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span.VU-ZEz"))
            ).text
        except:
            title = "Title not found"

        try:
            price = driver.find_element(By.CSS_SELECTOR, "div.Nx9bqj.CxhGGd").text
        except:
            price = "Price not found"

        try:
            rating = driver.find_element(By.CSS_SELECTOR, "div.XQDdHH").text
        except:
            rating = "Rating not found"

        return {
            "site": "Flipkart",
            "title": title,
            "price": price,
            "link": product_link
        }

    except Exception as e:
        return {"site": "Flipkart", "error": str(e)}
    finally:
        driver.quit()


if __name__ == "__main__":
    query = input("Enter product to search on Flipkart: ").strip()
    data = scrape_flipkart(query)
    print(json.dumps(data, indent=2))
