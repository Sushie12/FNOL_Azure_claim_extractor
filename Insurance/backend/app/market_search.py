import os
from serpapi import GoogleSearch
from langchain_core.tools import tool

@tool
def check_market_price(vehicle_make: str, part_or_damage_desc: str, location: str = "United States") -> dict:
    """
    Queries Google Shopping using SerpApi to fetch live market prices for vehicle parts/repairs.
    """
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        return {"error": "SERPAPI_API_KEY missing from environment variables."}

    query = f"{vehicle_make} {part_or_damage_desc}"
    
    params = {
        "engine": "google_shopping",
        "q": query,
        "location": location,
        "hl": "en",
        "gl": "us",
        "api_key": api_key
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict().get("shopping_results", [])
        
        extracted_prices = []
        samples = []

        for item in results[:5]:  # Take top 5 market listings
            price_raw = item.get("price", "0").replace("$", "").replace(",", "").strip()
            try:
                price_val = float(price_raw)
                extracted_prices.append(price_val)
            except ValueError:
                continue

            samples.append({
                "title": item.get("title"),
                "price": item.get("price"),
                "source": item.get("source")
            })

        avg_price = sum(extracted_prices) / len(extracted_prices) if extracted_prices else 0.0

        return {
            "query": query,
            "average_market_price": round(avg_price, 2),
            "vendor_samples": samples
        }
    except Exception as e:
        return {"error": f"SerpApi query failed: {str(e)}"}