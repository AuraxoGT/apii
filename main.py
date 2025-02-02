from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup

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
                "cover": game.get("keyImages", [{}])[0].get("url", "")  # Get the first image URL
            }
            for game in games if game.get("promotions") and game["promotions"].get("promotionalOffers")
        ]
        return free_games
    except requests.RequestException as e:
        print("Error fetching Epic Games:", e)
        return []


    except requests.RequestException as e:
        print("Error fetching Steam Games:", e)
        return []

@app.get("/free-games")
async def free_games():
    epic_games = await get_epic_free_games()
    return {"epic": epic_games}
