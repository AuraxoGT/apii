from fastapi import FastAPI
import requests
from datetime import datetime

app = FastAPI()

# Function to get free games from Epic Games based on region
async def get_epic_free_games(region="LT"):
    locale_map = {
        "US": "en-US",
        "GB": "en-GB",
        "DE": "de-DE",
        "FR": "fr-FR",
        "LT": "lt-LT",
        # Add other regions as needed
    }
    
    locale = locale_map.get(region.upper(), "en-US")  # Default to "en-US" if region not found
    
    url = f"https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale={locale}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        games = data.get("data", {}).get("Catalog", {}).get("searchStore", {}).get("elements", [])
        
        free_games = []
        for game in games:
            promotions = game.get("promotions", {})
            
            if isinstance(promotions, dict) and "promotionalOffers" in promotions:
                promotional_offers = promotions["promotionalOffers"]
                
                if promotional_offers:
                    offer_end_date = promotional_offers[0].get("promotionalOfferEndDate", None)
                    
                    if offer_end_date:
                        free_games.append({
                            "title": game.get("title", "Unknown"),
                            "url": f"https://store.epicgames.com/p/{game.get('productSlug', '')}",
                            "cover": game.get("keyImages", [{}])[0].get("url", ""),
                            "price": game.get("price", {}).get("totalPrice", {}).get("fmtPrice", "Free"),
                            "offer_end_timestamp": convert_to_timestamp(offer_end_date)
                        })
        
        return free_games
    
    except requests.RequestException as e:
        print(f"Error fetching Epic Games: {e}")
        return []

def convert_to_timestamp(date_str: str) -> int:
    """Convert Epic Games' custom date string to a Unix timestamp."""
    if date_str:
        try:
            dt = datetime.strptime(date_str, "%m/%d/%Y at %I:%M %p")
            return int(dt.timestamp())
        except ValueError as ve:
            print(f"Error parsing date: {ve}")
            return None
    return None

@app.get("/free-games")
async def free_games(region: str = "US"):
    epic_games = await get_epic_free_games(region)
    return {"epic": epic_games}
