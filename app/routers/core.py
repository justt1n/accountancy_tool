# app/routers/core.py

from fastapi import APIRouter, HTTPException

from app.constants import CONTEXTS
from app.models.context_request import ContextRequest
from app.models.request import CoreRequest
from app.services.context_manager import ContextManager
from app.services.accountancy_service import AccountancyService

router = APIRouter()


_context_manager_instance = None


def get_context_manager():
    global _context_manager_instance
    if _context_manager_instance is None:
        _context_manager_instance = ContextManager(CONTEXTS)
    return _context_manager_instance


RANGE_NAME = "Sheet1!A1"


@router.post("/core/test")
def test(request: CoreRequest):
    ctx_manager = get_context_manager()
    sheet_context = ctx_manager.get_context("sheet")
    sheet_context.get_data_from_sheet(request.src_sheet_url, RANGE_NAME)
    sheet_context.save_data_to_sheet(request.des_sheet_url, RANGE_NAME, sheet_context.data)
    return {"status": "OK"}


@router.post("/core/test2")
def test2(request: CoreRequest):
    ctx_manager = get_context_manager()
    sheet_context = ctx_manager.get_context("sheet")
    range_list = sheet_context.detect_ranges(request.src_sheet_url, 0)
    return {"status": "OK", "range": range_list}


@router.post("/core/test3")
def test3(request: CoreRequest):
    ctx_manager = get_context_manager()
    sheet_context = ctx_manager.get_context("sheet")
    range_list = sheet_context.detect_ranges(request.src_sheet_url, 0)
    for range in range_list:
        sheet_context.get_data_from_sheet(request.src_sheet_url, range)
        sheet_context.save_data_to_sheet(request.des_sheet_url, range, sheet_context.data)
    return {"status": "OK"}


@router.post("/core/test4")
def test4(request: CoreRequest):
    ctx_manager = get_context_manager()
    sheet_context = ctx_manager.get_context("sheet")
    data = sheet_context.filter_data_from_sheet(request.src_sheet_url, "Sheet1!A2:H23", "Trạng thái", "  trả")
    return {"status": "OK", "data": data}


@router.post("/core/filter")
def acc_filter(request: CoreRequest):
    ctx_manager = get_context_manager()
    accountancy_service = AccountancyService(ctx_manager, request)
    return accountancy_service.acc_filter()