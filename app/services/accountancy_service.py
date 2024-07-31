from app.models.request import AccMultiFilterRequest, AccMultiProcessRequest


def color_to_rgb(color_name):
    colors = {
        "red": {"red": 1.0, "green": 0.0, "blue": 0.0},
        "green": {"red": 0.0, "green": 1.0, "blue": 0.0},
        "blue": {"red": 0.0, "green": 0.0, "blue": 1.0},
        # Add more colors as needed
    }
    return colors.get(color_name.lower(), {"red": 0.0, "green": 0.0, "blue": 0.0})


class AccountancyService:
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

    def acc_sync(self):
        range_list = self.sheet_context.detect_ranges(self.request.src_sheet_url, 0)
        for src_range in range_list:
            des_range = self.sheet_context.detect_ranges(self.request.des_sheet_url, 0)[0]
            self.sheet_context.sync_data(self.request.src_sheet_url, self.request.des_sheet_url, src_range, des_range)
        return {"status": "OK"}

    def acc_filter_multisheet(self, request: AccMultiFilterRequest):
        # sheets = self.sheet_context.get_all_sheets(request.src_sheet_url)
        sheets = request.src_sheet_names
        sheet_ids = []
        for sheet in sheets:
            sheet_id = self.sheet_context.get_sheet_id(request.src_sheet_url, sheet)
            sheet_ids.append(sheet_id)
        range_list = []
        for sheet_id in sheet_ids:
            range_data = self.sheet_context.detect_ranges(request.src_sheet_url, sheet_id)
            #because 1 sheet Product (src_sheet) has just 1 range
            range_list.append(range_data[0])

        for _range in range_list:
            des_cell = self.get_start_cell_to_create(request)
            self.save_data_to_cell(request, _range, des_cell)

        return {"status": "OK", "des_cell": range_list}

    def get_start_cell_to_create(self, request: AccMultiFilterRequest):
        try:
            sheet_id = self.sheet_context.get_sheet_id(request.des_sheet_url, request.des_sheet_name)
            des_last_range = self.sheet_context.detect_ranges(request.des_sheet_url, sheet_id)[-1]
        except IndexError:
            return request.des_sheet_name + "!" + "A1"

        des_last_start_cell, des_last_end_cell = des_last_range.split("!")[1].split(":")
        (des_start_cell_row, des_start_cell_col) = self.sheet_context.cell_to_indices(des_last_start_cell)
        (des_end_cell_row, des_end_cell_col) = self.sheet_context.cell_to_indices(des_last_end_cell)
        des_cell = self.sheet_context.indices_to_cell((des_start_cell_row, des_end_cell_col + 3))
        return request.des_sheet_name + "!" + des_cell

    def save_data_to_cell(self, request: AccMultiFilterRequest, range_of_data: str, des_cell: str):
        self.sheet_context.get_data_from_sheet(request.src_sheet_url, range_of_data)
        header, filter_data = self.sheet_context.filter_data_from_sheet(request.src_sheet_url, range_of_data,
                                                                        "Trạng thái", "chưa trả")
        header.insert(0, "ID")
        data = [header] + filter_data
        self.sheet_context.save_data_to_sheet(request.des_sheet_url, des_cell, data)
        return {"status": "OK"}

    def acc_process_multisheet(self, request: AccMultiProcessRequest):
        des_sheet_names = request.des_sheet_names
        des_sheet_ids = []
        for sheet in des_sheet_names:
            sheet_id = self.sheet_context.get_sheet_id(request.des_sheet_url, sheet)
            des_sheet_ids.append(sheet_id)
        des_range_list = []
        src_sheet_names = []
        des_sheet_mapping = {}
        for sheet_id in des_sheet_ids:
            range_data = self.sheet_context.detect_ranges(request.des_sheet_url, sheet_id)
            for _range in range_data:
                tmp_sheet_name = self.sheet_context.get_unique_values(request.des_sheet_url, _range, "ID")[0]
                des_range_list.append(_range)
                src_sheet_names.append(tmp_sheet_name.split("!")[0])
                des_sheet_mapping[tmp_sheet_name.split("!")[0]] = _range


        src_sheet_names = list(set(src_sheet_names))
        src_sheet_ranges = []
        for sheet in src_sheet_names:
            sheet_id = self.sheet_context.get_sheet_id(request.src_sheet_url, sheet)
            src_sheet_ranges.append(self.sheet_context.detect_ranges(request.src_sheet_url, sheet_id)[0])

        src_sheet_mapping = {}
        for range_str in src_sheet_ranges:
            prefix = range_str.split("!")[0]
            src_sheet_mapping[prefix] = range_str

        mapped_sheet_mapping = {}
        for key in src_sheet_mapping:
            if key in des_sheet_mapping:
                mapped_sheet_mapping[key] = (src_sheet_mapping[key], des_sheet_mapping[key])

        for key, value in mapped_sheet_mapping.items():
            self.sheet_context.sync_data(request.src_sheet_url, request.des_sheet_url, value[0], value[1])
            self.sheet_context.remove_rows_containing_value(request.des_sheet_url, value[1], "trả")


        return {"status": "OK", "des_cell": mapped_sheet_mapping}
