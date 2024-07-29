from pydantic import BaseModel


class CoreRequest(BaseModel):
    src_sheet_url: str
    des_sheet_url: str


class AccRequest(BaseModel):
    pass