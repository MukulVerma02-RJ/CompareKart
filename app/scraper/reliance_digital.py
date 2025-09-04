import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def human_delay(a=0.5, b=2.5):
    time.sleep(random.uniform(a, b))

def get_driver():
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    return driver

def scrape_reliance_digital(product_name):
    driver = get_driver()
    wait = WebDriverWait(driver, 15)

    try:
        print("[info] Opening Reliance Digital")
        driver.get("https://www.reliancedigital.in/")

        # Close popup if appears
        try:
            popup = wait.until(EC.element_to_be_clickable((By.ID, "wzrk-cancel")))
            popup.click()
            print("[info] Closed popup")
        except:
            print("[warn] No popup found")

        # Search for the product
        print("[info] Searching...")
        search_input = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "search-input")))
        driver.execute_script("arguments[0].removeAttribute('readonly')", search_input)
        search_input.click()
        human_delay()
        search_input.send_keys(product_name)
        human_delay()
        search_input.send_keys(Keys.ENTER)

        # Wait for results
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "card-info-container")))
        human_delay()

        # Get first product
        product = driver.find_element(By.CLASS_NAME, "card-info-container")
        title = product.find_element(By.CLASS_NAME, "product-card-title").text.strip()
        price = product.find_element(By.CLASS_NAME, "price").text.strip().replace("₹", "").replace(",", "")
        try:
            rating = product.find_element(By.CLASS_NAME, "detail").text.strip("()")
        except:
            rating = "0"
        partial_link = product.find_element(By.TAG_NAME, "a").get_attribute("href")
        full_link = "https://www.reliancedigital.in" + partial_link if partial_link.startswith("/") else partial_link

        return {
            "site": "Reliance Digital",
            "title": title,
            "price": price,
            "link": full_link
        }

    except Exception as e:
        return {
            "site": "Reliance Digital",
            "error": f"[error] {str(e)}"
        }
    finally:
        driver.quit()

if __name__ == "__main__":
    import json
    query = input("Enter product name to search on Reliance Digital: ")
    result = scrape_reliance_digital(query)
    print(json.dumps(result, indent=2))

