from fastapi import FastAPI
import requests
from datetime import datetime
import pytz
import logging

app = FastAPI()

# Set up logging to capture errors
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Function to get free games from Epic Games
async def get_epic_free_games():
    url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=lt-LT"  # Lithuanian locale
    try:
        logger.debug("Sending request to Epic Games API...")
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        games = data.get("data", {}).get("Catalog", {}).get("searchStore", {}).get("elements", [])

        free_games = []
        for game in games:
            promotions = game.get("promotions", {})
            
            # Check if "promotions" and "promotionalOffers" are valid and not None
            if promotions and "promotionalOffers" in promotions:
                promo_end_date_str = promotions["promotionalOffers"][0].get("promotionalOfferEndDate")
                timestamp = None

                # Check if we have a valid promotional end date string
                if promo_end_date_str:
                    try:
                        logger.debug(f"Parsing promotional offer end date for {game['title']}: {promo_end_date_str}")
                        # Convert "2/6/2025 at 6:00 PM" to a datetime object
                        promo_end_date = datetime.strptime(promo_end_date_str, "%m/%d/%Y at %I:%M %p")
                        # Make sure to localize it to the Lithuanian timezone (EET or EEST)
                        lithuanian_tz = pytz.timezone('Europe/Vilnius')
                        localized_promo_end_date = lithuanian_tz.localize(promo_end_date)
                        timestamp = int(localized_promo_end_date.timestamp())  # Convert to Unix timestamp
                    except ValueError as e:
                        logger.error(f"Error parsing date for {game['title']}: {e}")
                        timestamp = None  # If parsing fails, leave the timestamp as None

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
        logger.error(f"Error fetching Epic Games: {e}")
        return []

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return []

@app.get("/free-games")
async def free_games():
    epic_games = await get_epic_free_games()
    return {"epic": epic_games}
