import httpx
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

# Fetch free games from Epic Games Store
async def get_epic_free_games():
    url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()  # Raise an error for 4xx/5xx responses
            data = response.json()
    except httpx.HTTPStatusError as e:
        raise Exception(f"HTTP error occurred: {e.response.status_code}")
    except httpx.RequestError as e:
        raise Exception(f"Request error occurred: {str(e)}")
    
    free_games = []

    for game in data.get("data", {}).get("Catalog", {}).get("searchStore", {}).get("elements", []):
        game_title = game.get("title", "No title available")
        game_url = game.get("url", "#")
        game_description = game.get("description", "No description available")

        # Safely access 'promotions' and 'promotionalOffers'
        offer_end_date = "N/A"
        if "promotions" in game and "promotionalOffers" in game["promotions"]:
            if game["promotions"]["promotionalOffers"]:
                offer_end_date = game["promotions"]["promotionalOffers"][0].get("promotionalOfferEndDate", "N/A")

        free_games.append({
            "title": game_title,
            "url": game_url,
            "description": game_description,
            "offer_end_date": offer_end_date
        })

    return free_games

# Endpoint to fetch free games
@app.get("/free-games")
async def free_games():
    try:
        epic_games = await get_epic_free_games()
        return JSONResponse(content={"free_games": epic_games})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# Run the FastAPI application (via Uvicorn)
