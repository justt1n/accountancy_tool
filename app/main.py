from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import core
from app.routers import gsp
import uvicorn
app = FastAPI()

origins = [
    "http://localhost:8080",  # Allow this origin
    # Add more origins if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(core.router, prefix="/api", tags=["core"])
app.include_router(gsp.router, prefix="/api/v2", tags=["gsp"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Crawler API"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

