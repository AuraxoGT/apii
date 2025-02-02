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
                "url": f"https://store.epicgames.com/p/{game.get('productSlug', '')}"
            }
            for game in games if game.get("promotions") and game["promotions"].get("promotionalOffers")
        ]
        return free_games
    except requests.RequestException as e:
        print("Error fetching Epic Games:", e)
        return []

# Function to scrape free games from Steam
async def get_steam_free_games():
    url = "https://store.steampowered.com/search/?specials=1&category1=998"
    headers = {"User-Agent": "Mozilla/5.0"}  # Add User-Agent to avoid bot detection
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        games = []
        
        for result in soup.select(".search_result_row"):
            title_tag = result.select_one(".title")
            price_tag = result.select_one(".search_price")
            if title_tag and price_tag:
                title = title_tag.text.strip()
                game_url = result.get("href", "")
                price = price_tag.text.strip()
                
                if "Free" in price:
                    games.append({"title": title, "url": game_url})
        
        return games
    except requests.RequestException as e:
        print("Error fetching Steam Games:", e)
        return []

@app.get("/free-games")
async def free_games():
    epic_games = await get_epic_free_games()
    steam_games = await get_steam_free_games()
    return {"epic": epic_games, "steam": steam_games}
