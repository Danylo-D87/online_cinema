from fastapi import FastAPI
from src.routes.genre import router as genres_router
from src.routes.movies import router as movies_router
# from src.routes.favorite_movies import router as favorite_movies_router

app = FastAPI(
    title="My Movie API",
    description="API for managing movies, genres, actors, etc.",
    version="0.1.0",
)


app.include_router(genres_router)
app.include_router(movies_router)
# app.include_router(favorite_movies_router)

# Ви можете додати інші роутери тут, наприклад:
# from src.routes.movies import router as movies_router
# app.include_router(movies_router)


@app.get("/")
async def root():
    return {"message": "Welcome to the Movie API! Visit /docs for API documentation."}

# Щоб запустити застосунок, використовуйте Uvicorn:
# uvicorn main:app --reload
# (якщо ваш файл називається main.py)