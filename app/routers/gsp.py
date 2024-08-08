from fastapi import APIRouter

from app.constants import CONTEXTS
from app.models.request import CoreRequest, AccMultiFilterRequest, AccMultiProcessRequest, GetSheetNameRequest
from app.services.accountancy_service import AccountancyService
from app.services.context_manager import ContextManager

router = APIRouter()

_context_manager_instance = None


def get_context_manager():
    global _context_manager_instance
    if _context_manager_instance is None:
        _context_manager_instance = ContextManager(CONTEXTS)
    return _context_manager_instance

@router.post("/test")
def test(request: CoreRequest):
    ctx_manager = get_context_manager()
    gsp_context = ctx_manager.get_context("gspread")
    data = gsp_context.get_all_sheets(request.src_sheet_url)
    return {"status": "OK", "data": data}


@router.post("/test2")
def test2(request: CoreRequest):
    ctx_manager = get_context_manager()
    gsp_context = ctx_manager.get_context("gspread")
    gsp_context.filter_and_transfer_data()
    return {"status": "OK", "data": data}