from fastapi import FastAPI
import requests
from datetime import datetime

app = FastAPI()

async def get_epic_free_games():
    url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=lt-LT"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        print("API Response:", data)  # Debugging

        games = data.get("data", {}).get("Catalog", {}).get("searchStore", {}).get("elements", [])
        free_games = []

        for game in games:
            promotions = game.get("promotions", {})
            
            if isinstance(promotions, dict):
                promotional_offers = promotions.get("promotionalOffers", [])

                if promotional_offers:
                    offer_end_date = promotional_offers[0]["promotionalOffers"][0].get("endDate")

                    print(f"Offer End Date for {game.get('title', 'Unknown')}: {offer_end_date}")  # Debugging

                    # Convert to timestamp
                    if offer_end_date:
                        try:
                            date_obj = datetime.fromisoformat(offer_end_date.replace("Z", "+00:00"))  # Convert UTC
                            offer_end_timestamp = int(date_obj.timestamp())  # Convert to integer timestamp
                        except ValueError:
                            offer_end_timestamp = None
                    else:
                        offer_end_timestamp = None

                    # Append game details
                    free_games.append({
                        "title": game.get("title", "Unknown"),
                        "url": f"https://store.epicgames.com/p/{game.get('productSlug', '')}",
                        "cover": game.get("keyImages", [{}])[0].get("url", ""),
                        "price": game.get("price", {}).get("totalPrice", {}).get("fmtPrice", "Free"),
                        "offer_end_date": offer_end_date,
                        "offer_end_date_timestamp": offer_end_timestamp
                    })

        return free_games
    
    except requests.RequestException as e:
        print(f"Error fetching Epic Games: {e}")
        return []

@app.get("/free-games")
async def free_games():
    epic_games = await get_epic_free_games()
    return {"epic": epic_games}
