from fastapi import FastAPI
import httpx
from datetime import datetime

app = FastAPI()

async def get_epic_free_games():
    url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=lt-LT"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()  # This should work fine in httpx
        
        games = data.get("data", {}).get("Catalog", {}).get("searchStore", {}).get("elements", [])
        free_games = []

        for game in games:
            promotions = game.get("promotions", {})

            if isinstance(promotions, dict):
                promotional_offers = promotions.get("promotionalOffers", [])

                if promotional_offers:
                    offer_end_date = promotional_offers[0]["promotionalOffers"][0].get("endDate", None)
                    
                    # Convert offer_end_date safely
                    try:
                        if offer_end_date:
                            date_obj = datetime.fromisoformat(offer_end_date.replace("Z", "+00:00"))
                            offer_end_timestamp = int(date_obj.timestamp())
                        else:
                            offer_end_timestamp = None
                    except ValueError:
                        offer_end_timestamp = None

                    # Check if game is free
                    price_info = game.get("price", {}).get("totalPrice", {})
                    is_free = price_info.get("discountPrice", 1) == 0  # More reliable check

                    if is_free:
                        free_games.append({
                            "title": game.get("title", "Unknown"),
                            "url": f"https://store.epicgames.com/p/{game.get('productSlug', '')}" if game.get("productSlug") else "https://store.epicgames.com/",
                            "cover": game.get("keyImages", [{}])[0].get("url", ""),
                            "price": "Free",
                            "offer_end_date": offer_end_date,
                            "offer_end_date_timestamp": offer_end_timestamp
                        })

        return free_games
    
    except httpx.RequestError as e:
        return {"error": f"Error fetching Epic Games: {e}"}

@app.get("/free-games")
async def free_games():
    return {"epic": await get_epic_free_games()}
