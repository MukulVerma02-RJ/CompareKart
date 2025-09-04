import os, json, time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def _get_driver():
    options = Options()
    # ⚠️ headless OFF (Croma listing often fails headless)
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--log-level=3")
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    options.add_experimental_option("useAutomationExtension", False)
    service = Service(log_path=os.devnull)
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"},
    )
    return driver

def scrape_croma(product_name: str):
    driver = _get_driver()
    try:
        driver.get("https://www.croma.com/")

        # search bar
        search_input = WebDriverWait(driver, 12).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input#searchV2"))
        )
        search_input.clear()
        search_input.send_keys(product_name)
        search_input.send_keys(Keys.RETURN)

        # results
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "li.product-item"))
        )

        products = driver.find_elements(By.CSS_SELECTOR, "li.product-item")
        if not products:
            return {"site": "Croma", "error": "No products found on Croma"}

        first = products[0]

        # title
        try:
            title = first.find_element(By.CSS_SELECTOR, "h3.product-title").text.strip()
        except:
            title = "No title available"

        # robust price extraction (avoid ₹0)
        price = None
        for sel in ["span.amount", "span.new-price", "span.final-price", "span.pdpPrice", ".price", ".new-price span"]:
            try:
                txt = first.find_element(By.CSS_SELECTOR, sel).text.strip()
                if txt and txt not in ("₹0", "0", "₹ 0"):
                    price = txt
                    break
            except:
                continue
        if not price:
            price = "N/A"

        # link
        link = first.find_element(By.TAG_NAME, "a").get_attribute("href")

        return {
            "site": "Croma",
            "title": title,
            "price": price.replace("₹", "").replace(",", "").strip() if price != "N/A" else "N/A",
            "link": link
        }
    except Exception as e:
        return {"site": "Croma", "error": str(e)}
    finally:
        driver.quit()

if __name__ == "__main__":
    q = input("Enter product for Croma: ")
    print(json.dumps(scrape_croma(q), indent=2))
