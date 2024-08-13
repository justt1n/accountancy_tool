class AccountancyServiceV2:
    def __init__(self, context_manager, request):
        self.context_manager = context_manager
        self.gsp_context = self.context_manager.get_context("gspread")
        self.request = request
        self.gsp_context.src_sheet_metadata = self.gsp_context.get_sheet_metadata(request.src_sheet_url)
        self.gsp_context.des_sheet_metadata = self.gsp_context.get_sheet_metadata(request.des_sheet_url)
