from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
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
            if game.get("promotions") and game["promotions"].get("promotionalOffers"):
                # Extract the original price and end date of the offer
                original_price = game.get("price", {}).get("totalPrice", {}).get("formattedPrice", "Free")
                offer_end_date = game["promotions"]["promotionalOffers"][0]["promotionalOfferEndDate"]
                
                # Format the end date
                end_date = datetime.utcfromtimestamp(offer_end_date / 1000).strftime('%Y-%m-%d %H:%M:%S')
                
                free_games.append({
                    "title": game.get("title", "Unknown"),
                    "url": f"https://store.epicgames.com/p/{game.get('productSlug', '')}",
                    "cover": game.get("keyImages", [{}])[0].get("url", ""),
                    "original_price": original_price,
                    "free_until": end_date
                })
        
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
            cover_tag = result.select_one(".search_result_row img")  # Get the cover image
            
            if title_tag and price_tag and cover_tag:
                title = title_tag.text.strip()
                game_url = result.get("href", "")
                price = price_tag.text.strip()
                cover_url = cover_tag["src"]  # Extract the cover image URL
                
                if "Free" in price:
                    # Steam doesn't always show the original price in search results, so we'll use a placeholder
                    original_price = price.replace("Free", "").strip() or "Unknown"
                    
                    # Attempt to find the remaining time for the free offer (using a placeholder for now)
                    free_until = "Unknown"  # Steam may not always show the exact date
                    
                    games.append({
                        "title": title,
                        "url": game_url,
                        "cover": cover_url,
                        "original_price": original_price,
                        "free_until": free_until
                    })
        
        return games
    except requests.RequestException as e:
        print("Error fetching Steam Games:", e)
        return []

@app.get("/free-games")
async def free_games():
    epic_games = await get_epic_free_games()
    steam_games = await get_steam_free_games()
    return {"epic": epic_games, "steam": steam_games}
