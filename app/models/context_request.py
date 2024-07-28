from pydantic import BaseModel


class ContextRequest(BaseModel):
    context_name: str
    sheet_name: str
