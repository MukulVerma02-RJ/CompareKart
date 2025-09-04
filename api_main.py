import time
import json
import os
import re
import webbrowser
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import concurrent.futures

# Import scrapers
from app.scraper import amazon, flipkart, croma, vijaysales, reliance_digital

app = FastAPI()

# Allow frontend (index.html) to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Price Normalizer ----------
def normalize_price(price):
    """
    Convert any price string (like 'Rs. 64,490', '₹74900.00', '2499.00', etc.)
    into a clean format: ₹64,900 or ₹2,499
    """
    if not price:
        return None

    # Keep only digits and decimal point
    clean = re.sub(r"[^\d.]", "", str(price))

    if clean == "":
        return None

    try:
        # Convert to float first (to handle decimals like 2499.00 correctly)
        value = float(clean)

        # Round to integer (since ecommerce prices are usually whole rupees)
        value = int(round(value))

        return f"₹{value:,}"   # Adds commas automatically
    except:
        return None


# ---------- Compare Endpoint ----------
@app.post("/compare")
async def compare(request: Request):
    body = await request.json()
    product = body.get("product")
    started_at = datetime.now()
    results = []

    scrapers = {
        "Amazon": amazon.scrape_amazon,
        "Flipkart": flipkart.scrape_flipkart,
        "Croma": croma.scrape_croma,
        "Vijay Sales": vijaysales.scrape_vijay_sales,
        "Reliance Digital": reliance_digital.scrape_reliance_digital,
    }

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_site = {executor.submit(scraper, product): site for site, scraper in scrapers.items()}

        for future in concurrent.futures.as_completed(future_to_site):
            site = future_to_site[future]
            try:
                res = future.result()
                result = {
                    "site": site,
                    "title": res.get("title"),
                    "price": normalize_price(res.get("price")),
                    "link": res.get("link"),
                    "error": res.get("error"),
                }
            except Exception as e:
                result = {
                    "site": site,
                    "title": None,
                    "price": None,
                    "link": None,
                    "error": str(e),
                }
            results.append(result)

    duration_ms = int((datetime.now() - started_at).total_seconds() * 1000)

    os.makedirs("scraped_results", exist_ok=True)
    filename = f"scraped_results/{product.replace(' ', '_')}_{started_at.strftime('%Y%m%d_%H%M%S')}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(
            {
                "product": product,
                "started_at": started_at.isoformat(),
                "duration_ms": duration_ms,
                "results": results,
                "saved_to": filename,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    return {
        "product": product,
        "started_at": started_at.isoformat(),
        "duration_ms": duration_ms,
        "results": results,
        "saved_to": filename,
    }


@app.get("/")
async def root():
    return {"message": "CompareKart API is running!"}


# ---------- Auto Open Frontend ----------
if __name__ == "__main__":
    import uvicorn

    # ✅ Launch frontend in browser automatically
    frontend_path = os.path.abspath("frontend/index.html")
    if os.path.exists(frontend_path):
        webbrowser.open(f"file://{frontend_path}")

    uvicorn.run("api_main:app", host="127.0.0.1", port=8000, reload=True)

# uvicorn api_main:app --reload --port 8000