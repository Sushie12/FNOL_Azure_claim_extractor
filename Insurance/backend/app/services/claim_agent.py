import json
import os
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from serpapi import GoogleSearch
from typing import Optional


# --- 1. Embedded SerpApi Tool ---
@tool
def check_market_price(vehicle_make: str, part_or_damage_desc: str, location: str) -> dict:
    """
    Queries SerpApi (Google Shopping) for real-time auto part market prices 
    for a given vehicle make and targeted location.
    """
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        return {"error": "SERPAPI_API_KEY not configured in environment variables."}

    query = f"{vehicle_make} {part_or_damage_desc} price"

    params = {
        "engine": "google_shopping",
        "q": query,
        "location": location,
        "hl": "en",
        "gl": "in" if "india" in location.lower() else "us",
        "api_key": api_key
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        shopping_results = results.get("shopping_results", [])[:5]

        items = []
        for item in shopping_results:
            items.append({
                "title": item.get("title"),
                "price": item.get("price"),
                "source": item.get("source"),
                "link": item.get("link")
            })

        return {"query": query, "location": location, "results": items}

    except Exception as e:
        return {"error": f"SerpApi lookup failed: {str(e)}"}


# --- 2. Pydantic Output Schema ---
class MarketComparisonResult(BaseModel):
    averageReplacementCost: Optional[float] = None
    damageEstimate: Optional[float] = None
    priceDifference: Optional[float] = 0.0
    isClaimAboveMarket: bool = False
    marketReasoning: str = ""


# --- 3. LLM Agent Function ---
async def evaluate_claim_with_agent(
    vehicle_make: str, 
    estimated_damage: float, 
    city_state_zip: str,
    country: str
) -> MarketComparisonResult:
    
    target_location = f"{city_state_zip}, {country}"

    # Fetch live market data using embedded SerpApi tool
    market_data = check_market_price.invoke({
        "vehicle_make": vehicle_make or "Vehicle",
        "part_or_damage_desc": "repair parts",
        "location": target_location
    })

    # Keeping your model name intact
    llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)
    structured_llm = llm.with_structured_output(MarketComparisonResult, method="json_mode")

    prompt = f"""
    You are an expert Auto Parts & Regional Repair Market Analyst.

    Claim Details:
    - Vehicle Make: {vehicle_make}
    - Estimated Damage Amount: ${estimated_damage}
    - Target Regional Market: {target_location}

    SerpApi Live Market Benchmark Data:
    {json.dumps(market_data, indent=2)}

    Task:
    1. Filter out irrelevant search noise (e.g., keychains, floor mats, toy cars, unrelated accessories).
    2. Compute a realistic average price benchmark for replacement parts in {target_location}.
    3. Compare the damage estimate (${estimated_damage}) against regional market averages.
    4. Respond with valid JSON using exactly these key names:
       - averageReplacementCost
       - damageEstimate
       - priceDifference
       - isClaimAboveMarket
       - marketReasoning
    """

    return await structured_llm.ainvoke(prompt)