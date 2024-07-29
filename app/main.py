from fastapi import FastAPI
from app.routers import core
import uvicorn
app = FastAPI()


app.include_router(core.router, prefix="/api", tags=["core"])


@app.get("/")
def read_root():
    return {"message": "Welcome to the Crawler API"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

