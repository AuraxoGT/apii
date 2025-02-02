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

        # Safely navigate through the response structure
        games = data.get("data", {}).get("Catalog", {}).get("searchStore", {}).get("elements", [])
        
        free_games = []
        for game in games:
            # Safely handle the promotions and promotionalOffers
            promotions = game.get("promotions", {})  # Ensure promotions is a dictionary
            
            # Check if "promotions" exists and is a dictionary
            if isinstance(promotions, dict):
                promotional_offers = promotions.get("promotionalOffers", [])
                
                if promotional_offers:
                    # Get the offer end date from the first promotional offer
                    offer_end_date = promotional_offers[0].get("promotionalOfferEndDate", None)
                    
                    # Convert the end date to a timestamp if it exists
                    if offer_end_date:
                        try:
                            # Parsing date string: 02/06/2025 6:00 PM
                            date_obj = datetime.strptime(offer_end_date, "%m/%d/%Y %I:%M %p")
                            offer_end_timestamp = date_obj.timestamp()
                        except ValueError:
                            offer_end_timestamp = None
                    else:
                        offer_end_timestamp = None

                    # Append the game details with the timestamp
                    free_games.append({
                        "title": game.get("title", "Unknown"),
                        "url": f"https://store.epicgames.com/p/{game.get('productSlug', '')}",
                        "cover": game.get("keyImages", [{}])[0].get("url", ""),
                        "price": game.get("price", {}).get("totalPrice", {}).get("fmtPrice", "Free"),
                        "offer_end_date": offer_end_date,
                        "offer_end_date_timestamp": offer_end_timestamp  # Add the timestamp field
                    })
            else:
                print(f"Skipping game due to missing or invalid 'promotions' data: {game}")

        return free_games
    
    except requests.RequestException as e:
        print(f"Error fetching Epic Games: {e}")
        return []

@app.get("/free-games")
async def free_games():
    epic_games = await get_epic_free_games()
    return {"epic": epic_games}
