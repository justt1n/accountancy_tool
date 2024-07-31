from pydantic import BaseModel


class CoreRequest(BaseModel):
    src_sheet_url: str
    des_sheet_url: str


class AccMultiFilterRequest(BaseModel):
    src_sheet_url: str
    des_sheet_url: str
    src_sheet_name: list
    des_sheet_name: str

class AccMultiProcessRequest(BaseModel):
    src_sheet_url: str
    des_sheet_url: str
    des_sheet_name: list

