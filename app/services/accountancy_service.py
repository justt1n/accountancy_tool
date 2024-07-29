from app.models.request import CoreRequest


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

    def acc_process(self):
        range_list = self.sheet_context.detect_ranges(self.request.des_sheet_url, 0)
        for element in range_list:
            self.sheet_context.remove_rows_containing_value(self.request.des_sheet_url, "Sheet1!A2:I23", "trả")


    def color_to_rgb(self, color_name):
        colors = {
            "red": {"red": 1.0, "green": 0.0, "blue": 0.0},
            "green": {"red": 0.0, "green": 1.0, "blue": 0.0},
            "blue": {"red": 0.0, "green": 0.0, "blue": 1.0},
            # Add more colors as needed
        }
        return colors.get(color_name.lower(), {"red": 0.0, "green": 0.0, "blue": 0.0})

    def remove_rows_containing_value(self, data, value):
        # Extract header
        header = data[0]

        # Filter rows that do not contain the specified value
        filtered_data = [row for row in data[1:] if value not in ' '.join(row)]

        # Return the header and filtered data
        return [header] + filtered_data
