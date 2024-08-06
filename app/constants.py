from app.services.contexts.sheet_context import SheetContext
from app.services.contexts.drive_context import DriveContext
from app.services.contexts.google_context import GoogleContext
from app.services.contexts.gspread import GSpreadContext
from app.services.context_manager import ContextManager

context_manager = ContextManager()

google_context = GoogleContext(context_manager)
context_manager.register_context("google", google_context)
sheet_context = SheetContext(context_manager)
context_manager.register_context("sheet", sheet_context)
drive_context = DriveContext(context_manager)
context_manager.register_context("drive", drive_context)
gspread_context = GSpreadContext(context_manager)
context_manager.register_context("gspread", gspread_context)

CONTEXTS = {
    "google": google_context,
    "sheet": sheet_context,
    "drive": drive_context,
    "gspread": gspread_context
}




