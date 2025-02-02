from fastapi import FastAPI
import requests
from datetime import datetime

app = FastAPI()

# Function to get free games from Epic Games
async def get_epic_free_games():
    url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=lt-LT"
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
                "offer_end_date": (
                    # Use 'endDate' and convert it to a timestamp
                    game.get("promotions", {}).get("promotionalOffers", [{}])[0].get("endDate", None)
                )  
            }
            for game in games if game.get("promotions") and game["promotions"].get("promotionalOffers")
        ]

        # Convert endDate from string to timestamp (if available)
        for game in free_games:
            offer_end_date = game.get("offer_end_date")
            if offer_end_date:
                try:
                    # Convert the end date to a timestamp
                    game["offer_end_date_timestamp"] = datetime.strptime(offer_end_date, "%m/%d/%Y %I:%M %p").timestamp()
                except ValueError:
                    game["offer_end_date_timestamp"] = None

        return free_games
    
    except requests.RequestException as e:
        print("Error fetching Epic Games:", e)
        return []

@app.get("/free-games")
async def free_games():
    epic_games = await get_epic_free_games()
    return {"epic": epic_games}
