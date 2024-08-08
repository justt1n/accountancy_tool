import gspread
from googleapiclient.discovery import build
import json


class GSpreadContext:
    def __init__(self, ctx_manager):
        google_context = ctx_manager.get_context("google")
        self.gc = gspread.authorize(google_context.scoped_creds)
        self.drive_service = build('drive', 'v3', credentials=google_context.scoped_creds)
        self.script_service = build('script', 'v1', credentials=google_context.scoped_creds)

    def create_spreadsheet(self, title, email):
        # Tạo một bảng tính mới
        spreadsheet = self.gc.create(title)
        spreadsheet.share(email, perm_type='user', role='writer')
        return spreadsheet.id

    def add_apps_script(self, spreadsheet_id, script_content):
        # Tạo một dự án script mới
        script_request = {
            'title': 'Spreadsheet Automation Script',
            'parentId': spreadsheet_id
        }

        script_response = self.drive_service.files().create(body=script_request,
                                                            fields='id').execute()
        script_id = script_response.get('id')

        # Cập nhật nội dung script
        update_request = {
            'files': [{
                'name': 'Code.gs',
                'type': 'SERVER_JS',
                'source': script_content
            }]
        }

        self.script_service.projects().updateContent(
            body=update_request,
            scriptId=script_id
        ).execute()

        return script_id

    def setup(self, title, email, script_content, is_payment=False):
        spreadsheet_id = self.create_spreadsheet(title, email)
        script_id = self.add_apps_script(spreadsheet_id, script_content)
        with open('storage/onEnterCell.txt', 'r') as file:
            on_enter_cell = file.read()
        if is_payment:
            self.add_apps_script(spreadsheet_id, on_enter_cell)
        return spreadsheet_id, script_id

    # CORE
    def detect_ranges(self, spreadsheet_id, sheet_id):
        spreadsheet = self.gc.open_by_key(spreadsheet_id)
        sheet = spreadsheet.get_worksheet_by_id(sheet_id)

        max_rows = sheet.row_count
        max_cols = sheet.col_count

        values = sheet.get_all_values()

        non_empty_cells = set()
        for r_idx, row in enumerate(values):
            for c_idx, cell in enumerate(row):
                if cell:
                    non_empty_cells.add((r_idx, c_idx))

        visited = set()

        def find_range(r, c):
            if (r, c) in non_empty_cells and (r, c) not in visited:
                min_r, max_r = r, r
                min_c, max_c = c, c
                # Expand vertically
                for i in range(r, max_rows):
                    if (i, c) in non_empty_cells:
                        max_r = i
                    else:
                        break
                # Expand horizontally
                for j in range(c, max_cols):
                    if (r, j) in non_empty_cells:
                        max_c = j
                    else:
                        break
                # Mark all cells in the range as visited
                for i in range(min_r, max_r + 1):
                    for j in range(min_c, max_c + 1):
                        visited.add((i, j))
                return (min_r, min_c, max_r, max_c)
            return None

        ranges = []
        for r_idx in range(max_rows):
            for c_idx in range(max_cols):
                range_coords = find_range(r_idx, c_idx)
                if range_coords:
                    min_r, min_c, max_r, max_c = range_coords
                    range_str = f"{sheet.title}!{gspread.utils.rowcol_to_a1(min_r + 1, min_c + 1)}:{gspread.utils.rowcol_to_a1(max_r + 1, max_c + 1)}"
                    ranges.append(range_str)

        return ranges

    def filter_and_transfer_data(self, product_spreadsheets, payment_spreadsheet_id, payment_sheet_name, columns):
        payment_spreadsheet = self.gc.open_by_key(payment_spreadsheet_id)
        payment_sheet = payment_spreadsheet.worksheet(payment_sheet_name)

        col_offset = 0  # Độ lệch cột giữa các dải dữ liệu

        for product_spreadsheet_id, sheet_names in product_spreadsheets.items():
            product_spreadsheet = self.gc.open_by_key(product_spreadsheet_id)

            for sheet_name in sheet_names:
                product_sheet = product_spreadsheet.worksheet(sheet_name)
                values = product_sheet.get_all_values()

                filtered_values = []
                for row_idx, row in enumerate(values):
                    if 'unpaid' in row:
                        filtered_row = [row[col] for col in columns]
                        # Thêm thông tin nhận diện vào một cell cách nhau bởi "#"
                        identifier = f"{product_spreadsheet_id}#{sheet_name}#{row_idx + 1}"  # row_idx + 1 to convert to 1-based indexing
                        filtered_row.append(identifier)
                        filtered_values.append(filtered_row)

                if filtered_values:
                    start_cell = gspread.utils.rowcol_to_a1(1, col_offset + 1)
                    end_cell = gspread.utils.rowcol_to_a1(len(filtered_values),
                                                          col_offset + len(columns) + 1)  # +1 cho thông tin nhận diện
                    cell_range = f"{start_cell}:{end_cell}"

                    payment_sheet.update(cell_range, filtered_values)
                    col_offset += len(columns) + 1 + 2  # Cách nhau theo chiều ngang 2 cell

    def get_all_sheets(self, spreadsheet_id):
        spreadsheet = self.gc.open_by_key(spreadsheet_id)
        sheet_titles = []

        for sheet in spreadsheet.worksheets():
            sheet_titles.append(sheet.title)  # Store the title of each sheet

        return sheet_titles


