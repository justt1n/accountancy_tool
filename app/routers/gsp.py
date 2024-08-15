from fastapi import APIRouter

from app.constants import CONTEXTS
from app.models.request import GetSheetNameRequest, \
    AccMultiFilterRequestV2, GetHeaderRequest, AccMultiSpreadsheetFilterRequest
from app.services.context_manager import ContextManager

router = APIRouter()

_context_manager_instance = None


def get_context_manager():
    global _context_manager_instance
    if _context_manager_instance is None:
        _context_manager_instance = ContextManager(CONTEXTS)
    return _context_manager_instance


@router.post("/test")
def test(request: GetSheetNameRequest):
    ctx_manager = get_context_manager()
    gsp_context = ctx_manager.get_context("gspread")
    data = gsp_context.get_all_sheets(request.src_sheet_url)
    return {"status": "OK", "data": data}


@router.post("/test2")
def test2(request: AccMultiFilterRequestV2):
    # request_data = AccMultiFilterRequestV2(
    #     src_spreadsheets={
    #         "1IBaJugViSUO36_rNCKfOV1V5D-9YPSoD-vp6CN8GfY8": ["Product1", "Product2"]
    #         # "spreadsheet_id_2": ["SheetA", "SheetB"]
    #     },
    #     des_spreadsheet_id="1Mz_fwMlT6cS7sNBkoE1AUaGhjLE9f3XYhoAzy9X9dro",
    #     des_sheet_name="Payment1",
    #     columns=["Thời gian", "Rate", "Người bán", "Số lượng", "Đơn giá", "Sản phẩm", "Ví trả", "Trạng thái", "Note"]
    # )
    request_data = request
    ctx_manager = get_context_manager()
    gsp_context = ctx_manager.get_context("gspread")
    gsp_context.filter_and_transfer_data2(request_data.src_spreadsheets, request_data.des_spreadsheet_id,
                                          request_data.des_sheet_name, request_data.columns)
    return {"status": "OK", "request count": gsp_context.get_request_count()}

@router.post("/test3")
def test3(request: AccMultiSpreadsheetFilterRequest):
    ctx_manager = get_context_manager()
    gsp_context = ctx_manager.get_context("gspread")
    gsp_context.filter_and_transfer_data3(request.src_spreadsheets, request.des_spreadsheet_id,
                                          request.des_sheet_name)
    return {"status": "OK", "request count": gsp_context.get_request_count()}


@router.post("/headers")
def get_headers(request: GetHeaderRequest):
    ctx_manager = get_context_manager()
    gsp_context = ctx_manager.get_context("gspread")
    data = gsp_context.get_header(request.src_sheet_url, request.src_sheet_name)
    return {"status": "OK", "data": data}


@router.post("/filter")
def filter(request: AccMultiSpreadsheetFilterRequest):
    ctx_manager = get_context_manager()
    gsp_context = ctx_manager.get_context("gspread")
    gsp_context.filter_and_transfer_data3(request.src_spreadsheets, request.des_spreadsheet_id,
                                          request.des_sheet_name)
    return {"status": "OK", "request count": gsp_context.get_request_count()}

@router.post("/addScript")
def add_script():
    ctx_manager = get_context_manager()
    gsp_context = ctx_manager.get_context("gspread")
    data = gsp_context.clone_spreadsheet("1Mz_fwMlT6cS7sNBkoE1AUaGhjLE9f3XYhoAzy9X9dro")
    return {"status": "OK", "data": data}


