from fastapi import FastAPI
import requests
from datetime import datetime

app = FastAPI()

# Function to get free games from Epic Games
async def get_epic_free_games():
    url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=en-US"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        games = data.get("data", {}).get("Catalog", {}).get("searchStore", {}).get("elements", [])
        
        free_games = [
            {
                "title": game.get("title", "Unknown"),
                "url": f"https://store.epicgames.com/p/{game.get('productSlug', '')}",
                "cover": game.get("keyImages", [{}])[0].get("url", ""),  # Get the first image URL
                "price": game.get("price", {}).get("totalPrice", {}).get("fmtPrice", "Free"),  # Price info
                "offer_end_timestamp": (
                    convert_to_timestamp(
                        game.get("promotions", {}).get("promotionalOffers", [{}])[0].get("promotionalOfferEndDate", None)
                    )
                )  # Offer end timestamp
            }
            for game in games if game.get("promotions") and game["promotions"].get("promotionalOffers")
        ]
        
        return free_games
    
    except requests.RequestException as e:
        print("Error fetching Epic Games:", e)
        return []

def convert_to_timestamp(date_str: str) -> int:
    """Convert date string to a Unix timestamp."""
    if date_str:
        try:
            # Assuming the date is in ISO 8601 format, e.g., "2025-02-05T00:00:00.000Z"
            dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
            return int(dt.timestamp())
        except ValueError:
            return None  # If there's a parsing error, return None
    return None

@app.get("/free-games")
async def free_games():
    epic_games = await get_epic_free_games()
    return {"epic": epic_games}
