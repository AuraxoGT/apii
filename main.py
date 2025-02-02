from fastapi import FastAPI
import requests
import json

app = FastAPI()

# Function to get free games from Epic Games
async def get_epic_free_games():
    url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=en-US"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Print the raw response to debug (remove this in production)
        # You can comment or remove this after debugging
        print(json.dumps(data, indent=4))  # This will print the response in a readable format
        
        games = data.get("data", {}).get("Catalog", {}).get("searchStore", {}).get("elements", [])
        
        free_games = []
        
        for game in games:
            # Check if the game has promotions and promotional offers
            promotions = game.get("promotions", {}).get("promotionalOffers", [])
            
            if promotions:
                # Extract the offer end date, if available
                offer_end_date = "N/A"
                for offer in promotions:
                    offer_end_date = offer.get("endDate", "N/A")
                    if offer_end_date != "N/A":
                        break  # Stop at the first valid offer end date
                
                free_games.append({
                    "title": game.get("title", "Unknown"),
                    "url": f"https://store.epicgames.com/p/{game.get('productSlug', '')}",
                    "cover": game.get("keyImages", [{}])[0].get("url", ""),  # Get the first image URL
                    "price": game.get("price", {}).get("totalPrice", {}).get("fmtPrice", "Free"),  # Price info
                    "offer_end_date": offer_end_date  # End date of the offer
                })
        
        return free_games
    
    except requests.RequestException as e:
        print("Error fetching Epic Games:", e)
        return []

@app.get("/free-games")
async def free_games():
    epic_games = await get_epic_free_games()
    return {"epic": epic_games}
