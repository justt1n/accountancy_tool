from pydantic import BaseModel

class CrawlerData(BaseModel):
    url: str
    title: str
    content: str


class CrawlerModel(BaseModel):
    url: str
    siteName: str
    context: str