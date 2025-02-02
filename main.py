from fastapi import FastAPI
from fastapi.responses import JSONResponse
import requests

app = FastAPI()

# Function to fetch free Epic Games
async def get_epic_free_games():
    url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"
    response = requests.get(url)
    data = response.json()
    free_games = []

    for game in data["data"]["Catalog"]["searchStore"]["elements"]:
        game_title = game["title"]
        game_url = game["url"]
        game_description = game.get("description", "No description available")

        # Check if promotionalOffers and promotionalOfferEndDate exist
        offer_end_date = None
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

# Endpoint to get the free Epic Games
@app.get("/free-games")
async def free_games():
    try:
        epic_games = await get_epic_free_games()
        if not epic_games:
            return JSONResponse(status_code=404, content={"message": "No free games found"})
        return JSONResponse(status_code=200, content={"free_games": epic_games})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"An error occurred: {str(e)}"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
