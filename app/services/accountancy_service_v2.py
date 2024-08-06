from app.models.request import AccMultiFilterRequest, AccMultiProcessRequest

class AccountancyServiceV2:
    def __init__(self, context_manager, request):
        self.context_manager = context_manager
        self.sheet_context = self.context_manager.get_context("sheet")
        self.request = request
        self.sheet_context.src_sheet_metadata = self.sheet_context.get_sheet_metadata(request.src_sheet_url)
        self.sheet_context.des_sheet_metadata = self.sheet_context.get_sheet_metadata(request.des_sheet_url)

    def acc_filter(self):
        range_list = self.sheet_context.detect_ranges(self.request.src_sheet_url, 0)
        for element in range_list:
            self.sheet_context.get_data_from_sheet(self.request.src_sheet_url, element)
            header, filter_data = self.sheet_context.filter_data_from_sheet(self.request.src_sheet_url, "Sheet1!A2:H23",
                                                                            "Trạng thái", "chưa trả")
            header.insert(0, "ID")
            data = [header] + filter_data
            self.sheet_context.save_data_to_sheet(self.request.des_sheet_url, element, data)
        return {"status": "OK"}

    def _acc_filter(self, request: AccMultiFilterRequest, src_range: list, des_cell: str):
        range_list = self.sheet_context.detect_ranges(request.src_sheet_url, 0)
        for element in range_list:
            self.sheet_context.get_data_from_sheet(request.src_sheet_url, element)
            header, filter_data = self.sheet_context.filter_data_from_sheet(request.src_sheet_url, "Sheet1!A2:H23",
                                                                            "Trạng thái", "chưa trả")
            header.insert(0, "ID")
            data = [header] + filter_data
            self.sheet_context.save_data_to_sheet(request.des_sheet_url, des_cell, data)
        return {"status": "OK"}

    def acc_process(self):
        range_list = self.sheet_context.detect_ranges(self.request.des_sheet_url, 0)
        for src_range in range_list:
            des_range = self.sheet_context.detect_ranges(self.request.des_sheet_url, 0)[0]
            self.sheet_context.sync_data(self.request.src_sheet_url, self.request.des_sheet_url, src_range, des_range)
            self.sheet_context.remove_rows_containing_value(self.request.des_sheet_url, src_range, "trả")
        return {"status": "OK"}
