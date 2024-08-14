from typing import List, Dict

from pydantic import BaseModel


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


class GetHeaderRequest(BaseModel):
    src_sheet_url: str
    src_sheet_name: str


class AccMultiFilterRequestV2(BaseModel):
    src_spreadsheets: Dict[str, List[str]]
    des_spreadsheet_id: str
    des_sheet_name: str
    columns: List[str]


class Spreadsheet(BaseModel):
    spreadsheet_id: str
    sheet_name: List[str]
    columns: List[str]

class AccMultiSpreadsheetFilterRequest(BaseModel):
    src_spreadsheets: Dict[str, Spreadsheet]
    des_spreadsheet_id: str
    des_sheet_name: str