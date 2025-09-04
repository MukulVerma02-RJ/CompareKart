import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options


def scrape_amazon(product_name: str):
    try:
        options = uc.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )

        driver = uc.Chrome(options=options)

        # Go to Amazon India
        driver.get("https://www.amazon.in/")
        time.sleep(2)

        # Search for the product
        search_box = driver.find_element(By.ID, "twotabsearchtextbox")
        search_box.send_keys(product_name)
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)

        # Find product results (ignore sponsored)
        results = driver.find_elements(By.XPATH, "//div[@data-component-type='s-search-result']")
        for result in results:
            try:
                title = result.find_element(By.TAG_NAME, "h2").text.strip()
                price = result.find_element(By.CLASS_NAME, "a-price-whole").text.strip()
                link = result.find_element(By.TAG_NAME, "a").get_attribute("href")
                try:
                    rating = result.find_element(By.CSS_SELECTOR, "span.a-icon-alt").get_attribute("innerHTML").split()[0]
                except:
                    rating = "0"

                driver.quit()
                return {
                    "site": "Amazon",
                    "title": title,
                    "price": price.replace("₹", "").replace(",", ""),
                    "link": link,
                }
            except:
                continue

        driver.quit()
        return {"site": "Amazon", "error": "No valid product found"}

    except Exception as e:
        return {"site": "Amazon", "error": str(e)}


if __name__ == "__main__":
    import json
    query = input("Enter product name to search on Amazon: ")
    result = scrape_amazon(query)
    print(json.dumps(result, indent=2))
