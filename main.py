from fastapi import FastAPI
import requests
from datetime import datetime
import pytz

app = FastAPI()

# Function to get free games from Epic Games
async def get_epic_free_games():
    url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=lt-LT"  # Lithuanian locale
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        games = data.get("data", {}).get("Catalog", {}).get("searchStore", {}).get("elements", [])

        free_games = []
        for game in games:
            promotions = game.get("promotions", {}).get("promotionalOffers", [])
            if promotions:
                promo_end_date_str = promotions[0].get("promotionalOfferEndDate")
                timestamp = None
                
                # Check if we have a valid promotional end date string
                if promo_end_date_str:
                    # Convert "2/6/2025 at 6:00 PM" to a datetime object
                    try:
                        promo_end_date = datetime.strptime(promo_end_date_str, "%m/%d/%Y at %I:%M %p")
                        # Make sure to localize it to the Lithuanian timezone (EET or EEST)
                        lithuanian_tz = pytz.timezone('Europe/Vilnius')
                        localized_promo_end_date = lithuanian_tz.localize(promo_end_date)
                        timestamp = int(localized_promo_end_date.timestamp())  # Convert to Unix timestamp
                    except ValueError as e:
                        print(f"Error parsing date for {game['title']}: {e}")

                # Add the game details including the timestamp
                free_games.append({
                    "title": game.get("title", "Unknown"),
                    "url": f"https://store.epicgames.com/p/{game.get('productSlug', '')}",
                    "cover": game.get("keyImages", [{}])[0].get("url", ""),
                    "price": game.get("price", {}).get("totalPrice", {}).get("fmtPrice", "Free"),
                    "offer_end_date_timestamp": timestamp  # Timestamp of the offer end date
                })

        return free_games

    except requests.RequestException as e:
        print("Error fetching Epic Games:", e)
        return []

@app.get("/free-games")
async def free_games():
    epic_games = await get_epic_free_games()
    return {"epic": epic_games}
