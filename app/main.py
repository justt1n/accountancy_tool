from fastapi import FastAPI
from app.routers import core
from app.services.context_manager import ContextManager

app = FastAPI()


app.include_router(core.router, prefix="/api", tags=["core"])


@app.get("/")
def read_root():
    return {"message": "Welcome to the Crawler API"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

