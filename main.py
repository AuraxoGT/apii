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
        
        free_games = []
        for game in games:
            promotions = game.get("promotions", {})
            
            # Check if promotions is a valid dictionary and contains "promotionalOffers"
            if isinstance(promotions, dict):
                promotional_offers = promotions.get("promotionalOffers", [])
                
                # Check if promotionalOffers is not empty
                if promotional_offers:
                    offer_end_date = promotional_offers[0].get("promotionalOfferEndDate", None)
                    print(f"Found promotionalOfferEndDate: {offer_end_date}")  # Debugging line to check the offer end date
                    
                    free_games.append({
                        "title": game.get("title", "Unknown"),
                        "url": f"https://store.epicgames.com/p/{game.get('productSlug', '')}",
                        "cover": game.get("keyImages", [{}])[0].get("url", ""),  # Get the first image URL
                        "price": game.get("price", {}).get("totalPrice", {}).get("fmtPrice", "Free"),  # Price info
                        "offer_end_timestamp": (
                            convert_to_timestamp(offer_end_date)
                        )  # Offer end timestamp
                    })
        
        return free_games
    
    except requests.RequestException as e:
        print(f"Error fetching Epic Games: {e}")
        return []

def convert_to_timestamp(date_str: str) -> int:
    """Convert Epic Games' custom date string to a Unix timestamp."""
    if date_str:
        try:
            print(f"Attempting to parse date: {date_str}")  # Debugging line to see the date string before parsing
            # Adjust the date format to match "2/6/2025 at 6:00 PM"
            dt = datetime.strptime(date_str, "%m/%d/%Y at %I:%M %p")
            print(f"Parsed date: {dt}")  # Print parsed date
            return int(dt.timestamp())
        except ValueError as ve:
            print(f"Error parsing date: {ve}")  # Log the error if the date is not parsed
            return None  # Return None if parsing fails
    return None

@app.get("/free-games")
async def free_games():
    epic_games = await get_epic_free_games()
    return {"epic": epic_games}
