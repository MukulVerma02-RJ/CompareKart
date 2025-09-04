import time
import random
import json
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def human_sleep(a=0.5, b=2.5):
    """Add random human-like delay"""
    time.sleep(random.uniform(a, b))


def get_driver():
    options = Options()
    options.add_argument("--headless=new")   # ✅ Headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # ✅ Use a temp user profile to avoid session conflicts
    temp_profile = tempfile.mkdtemp()
    options.add_argument(f"--user-data-dir={temp_profile}")

    driver = webdriver.Chrome(options=options)

    # ✅ Stealth patch (hide navigator.webdriver)
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"},
    )
    return driver


def scrape_vijay_sales(product_name):
    driver = get_driver()
    print("[info] Opening Vijay Sales")

    try:
        search_url = f"https://www.vijaysales.com/search-listing?q={product_name.replace(' ', '%20')}"
        driver.get(search_url)
        human_sleep(2, 4)

        # Wait for first product card
        product_card = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".product-card__link"))
        )

        title_elem = product_card.find_element(By.CSS_SELECTOR, ".product-name")
        price_elem = product_card.find_element(By.CSS_SELECTOR, ".discountedPrice")
        link = product_card.get_attribute("href")

        try:
            rating_elem = product_card.find_element(By.CSS_SELECTOR, "[data-rating-summary]")
            rating = rating_elem.get_attribute("data-rating-summary") or "N/A"
        except:
            rating = "N/A"

        return {
            "site": "Vijay Sales",
            "title": title_elem.text.strip(),
            "price": price_elem.text.strip().replace("₹", "").replace(",", ""),
            "link": link,
            "rating": rating
        }

    except Exception as e:
        return {
            "site": "Vijay Sales",
            "error": f"[error] Search failed: {str(e)}"
        }

    finally:
        driver.quit()


# ========== Test ==========
if __name__ == "__main__":
    query = input("Enter product name to search on Vijay Sales: ").strip()
    result = scrape_vijay_sales(query)
    print(json.dumps(result, indent=2))
