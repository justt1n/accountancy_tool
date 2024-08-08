from pydantic import BaseModel
from typing import List, Dict

class CoreRequest(BaseModel):
    src_sheet_url: str
    des_sheet_url: str


class AccMultiFilterRequest(BaseModel):
    src_sheet_url: str
    des_sheet_url: str
    src_sheet_names: list
    des_sheet_name: str

class AccMultiProcessRequest(BaseModel):
    src_sheet_url: str
    des_sheet_url: str
    des_sheet_names: list

class GetSheetNameRequest(BaseModel):
    src_sheet_url: str


class AccMultiFilterRequestV2(BaseModel):
    src_spreadsheets: Dict[str, List[str]]
    des_spreadsheet_id: str
    des_sheet_name: str
    columns: List[int]