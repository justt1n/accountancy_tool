import json
import os
from functools import wraps

import gspread
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Decorator to count requests
request_count = 0


def count_requests(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        global request_count
        request_count += 1
        return func(*args, **kwargs)

    return wrapper


# Apply the decorator to gspread methods
gspread.Client.open_by_key = count_requests(gspread.Client.open_by_key)
gspread.Worksheet.get_all_values = count_requests(gspread.Worksheet.get_all_values)
gspread.Worksheet.update = count_requests(gspread.Worksheet.update)
gspread.Worksheet.format = count_requests(gspread.Worksheet.format)


class GSpreadContext:
    def __init__(self, ctx_manager):
        self.google_context = ctx_manager.get_context("google")
        self.gc = gspread.authorize(self.google_context.scoped_creds)
        self.drive_service = build('drive', 'v3', credentials=self.google_context.scoped_creds)
        self.script_service = build('script', 'v1', credentials=self.google_context.client_creds)

    @staticmethod
    def indices_to_cell(indices):
        row, col = indices
        col_str = ""
        while col >= 0:
            col_str = chr(col % 26 + ord('A')) + col_str
            col = col // 26 - 1
        return f"{col_str}{row + 1}"

    @staticmethod
    def col_to_index(col_str):
        index = 0
        for char in col_str:
            index = index * 26 + ord(char.upper()) - ord('A') + 1
        return index - 1

    def create_spreadsheet(self, title, email):
        # Tạo một bảng tính mới
        spreadsheet = self.gc.create(title)
        spreadsheet.share(email, perm_type='user', role='writer')
        return spreadsheet.id

    def add_apps_script2(self, spreadsheet_id):
        try:
            # Step 1: Get the content of the existing Apps Script project
            original_script_id = '1NOkmTIVu99Gn62nk6VzHZxn9yjMI5nTMnUUaYi2c7vLG5ibkZyUVCubL'
            original_script_content = self.script_service.projects().getContent(
                scriptId=original_script_id
            ).execute()

            # Step 2: Create a new Apps Script project

            create_project_response = self.script_service.projects().create(
                title = 'Cloned Script for Spreadsheet',
                parentId = spreadsheet_id
            ).execute()
            new_script_id = create_project_response['scriptId']

            # Step 3: Update the new project with the content from the original project
            update_request = {
                'files': original_script_content['files']  # Copy all files from the original script
            }
            self.script_service.projects().updateContent(
                scriptId=new_script_id,
                body=update_request
            ).execute()

            # Step 4: Deploy the new Apps Script project and attach it to the new spreadsheet
            deployment_request = {
                'versionNumber': 1,
                'manifestFileName': 'appsscript',
                'description': 'Deployment of cloned script',
            }
            self.script_service.projects().deployments().create(
                scriptId=new_script_id,
                body=deployment_request
            ).execute()

            return new_script_id

        except HttpError as e:
            print(f"Failed to clone and deploy Apps Script project: {e}")
            raise

    def add_apps_script(self, original_script_id):
        try:
            # Step 1: Get the content of the existing Apps Script project
            original_script_content = self.script_service.projects().getContent(
                scriptId=original_script_id
            ).execute()

            # Step 2: Create a new spreadsheet
            new_spreadsheet = self.gc.create('New Spreadsheet')
            new_spreadsheet_id = new_spreadsheet.id

            # Step 3: Create a new Apps Script project
            create_project_request = {
                'parentId': '1Ax7KII2IpOtxLzDWMtPSg2R86jj0iai-DrtHG5vVJtU',
                'title': 'Cloned Script for New Spreadsheet',
            }
            create_project_response = self.script_service.projects().create(
                body=create_project_request
            ).execute()
            new_script_id = create_project_response['scriptId']

            # Step 4: Update the new project with the content from the original project
            update_request = {
                'files': original_script_content['files']  # Reuse all files from the original script
            }
            self.script_service.projects().updateContent(
                scriptId=new_script_id,
                body=update_request
            ).execute()

            # Step 5: Deploy the new Apps Script project and attach it to the new spreadsheet
            deployment_request = {
                'versionNumber': 1,
                'manifestFileName': 'appsscript',
                'description': 'Deployment of cloned script',
            }
            self.script_service.projects().deployments().create(
                scriptId=new_script_id,
                body=deployment_request
            ).execute()

            return new_script_id, new_spreadsheet_id

        except HttpError as e:
            print(f"Failed to clone and deploy Apps Script project: {e}")
            raise

    def clone_spreadsheet(self, original_spreadsheet_id):
        try:
            # Open the original spreadsheet
            original_spreadsheet = self.gc.open_by_key(original_spreadsheet_id)
            original_title = original_spreadsheet.title

            # Create a new spreadsheet with the same title
            new_spreadsheet = self.gc.copy(original_spreadsheet_id, title=original_title, copy_permissions=True)
            new_spreadsheet_id = new_spreadsheet.id

            return new_spreadsheet_id
        except HttpError as e:
            print(f"Failed to clone spreadsheet: {e}")
            raise

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

    def filter_and_transfer_data3(self, src_spreadsheets, des_spreadsheet_id, des_sheet_name):
        des_spreadsheet = self.gc.open_by_key(des_spreadsheet_id)
        des_sheet = des_spreadsheet.worksheet(des_sheet_name)
        des_sheet.clear()
        col_offset = 0  # Column offset between data ranges

        for index, spreadsheet_info in src_spreadsheets.items():
            product_spreadsheet = self.gc.open_by_key(spreadsheet_info.spreadsheet_id)

            product_sheet = product_spreadsheet.worksheet(spreadsheet_info.sheet_name)
            values = product_sheet.get_all_values()
            values = [row for row in values if any(cell.strip() for cell in row)]
            if not values:
                continue

            # Detect the starting row and column using detect_ranges
            detected_ranges = self.detect_ranges(spreadsheet_info.spreadsheet_id, product_sheet.id)
            if not detected_ranges:
                continue

            # Get the starting cell of the first (and only) range
            start_cell, end_cell = detected_ranges[0].split(":")
            start_cell = start_cell.split("!")[1]
            start_row, start_col = gspread.utils.a1_to_rowcol(start_cell)

            # Extract header row from the detected start_row
            header_row = values[0]

            try:
                # Ensure all columns exist in the header row
                col_indices = [header_row.index(col_name) for col_name in spreadsheet_info.columns]
            except ValueError as e:
                raise ValueError(f"Column '{e.args[0]}' not found in the header row of sheet '{spreadsheet_info.sheet_name}'")

            # Create the new header row for the filtered values
            new_header_row = [header_row[idx] for idx in col_indices] + ["Identifier"]
            status_col_index = header_row.index("Trạng thái")

            filtered_values = [new_header_row]  # Insert header at the beginning
            for row_idx, row in enumerate(values[1:], start=start_row):
                row = [item.strip().lower() for item in row]
                if 'unpaid' in row:
                    filtered_row = [row[idx] for idx in col_indices]
                    # Calculate begin_col and end_col based on the current col_offset
                    begin_col = gspread.utils.rowcol_to_a1(1, col_offset + 2)
                    end_col = gspread.utils.rowcol_to_a1(1, col_offset + 1 + len(spreadsheet_info.columns) + 1)
                    # Add identifier information into a cell separated by "#"
                    identifier = f"{spreadsheet_info.spreadsheet_id}#{spreadsheet_info.sheet_name}#{begin_col}:{end_col}#{self.indices_to_cell((row_idx, status_col_index))}"
                    filtered_row.append(identifier)
                    filtered_values.append(filtered_row)

            if filtered_values:
                start_col_offset = col_offset + 2  # Adjusted offset to 2
                end_col = start_col_offset + len(spreadsheet_info.columns) + 1  # +1 for the identifier information
                if end_col > des_sheet.col_count:
                    raise ValueError(
                        f"End column {end_col} exceeds the sheet's column count {des_sheet.col_count}")

                start_cell = gspread.utils.rowcol_to_a1(1, start_col_offset)
                end_cell = gspread.utils.rowcol_to_a1(len(filtered_values), end_col)
                cell_range = f"{start_cell}:{end_cell}"

                des_sheet.update(cell_range, filtered_values)
                col_offset += len(spreadsheet_info.columns) + 1 + 2  # Horizontal spacing between datasets

                # Set the identifier column to wrap text to clip
                identifier_col = start_col_offset + len(spreadsheet_info.columns)
                identifier_range = f"{gspread.utils.rowcol_to_a1(1, identifier_col)}:{gspread.utils.rowcol_to_a1(len(filtered_values), identifier_col)}"
                des_sheet.format(identifier_range, {"wrapStrategy": "CLIP"})


    def filter_and_transfer_data2(self, product_spreadsheets, payment_spreadsheet_id, payment_sheet_name, columns):
        payment_spreadsheet = self.gc.open_by_key(payment_spreadsheet_id)
        payment_sheet = payment_spreadsheet.worksheet(payment_sheet_name)

        col_offset = 0  # Column offset between data ranges

        for product_spreadsheet_id, sheet_names in product_spreadsheets.items():
            product_spreadsheet = self.gc.open_by_key(product_spreadsheet_id)

            for sheet_name in sheet_names:
                product_sheet = product_spreadsheet.worksheet(sheet_name)
                values = product_sheet.get_all_values()
                values = [row for row in values if any(cell.strip() for cell in row)]
                if not values:
                    continue

                # Detect the starting row and column using detect_ranges
                detected_ranges = self.detect_ranges(product_spreadsheet_id, product_sheet.id)
                if not detected_ranges:
                    continue

                # Get the starting cell of the first (and only) range
                start_cell, end_cell = detected_ranges[0].split(":")
                start_cell = start_cell.split("!")[1]
                start_row, start_col = gspread.utils.a1_to_rowcol(start_cell)

                # Extract header row from the detected start_row
                header_row = values[0]

                try:
                    # Ensure all columns exist in the header row
                    col_indices = [header_row.index(col_name) for col_name in columns]
                except ValueError as e:
                    raise ValueError(f"Column '{e.args[0]}' not found in the header row of sheet '{sheet_name}'")

                # Create the new header row for the filtered values
                new_header_row = [header_row[idx] for idx in col_indices] + ["Identifier"]
                status_col_index = header_row.index("Trạng thái")

                filtered_values = [new_header_row]  # Insert header at the beginning
                for row_idx, row in enumerate(values[1:], start=start_row):
                    row = [item.strip().lower() for item in row]
                    if 'unpaid' in row:
                        filtered_row = [row[idx] for idx in col_indices]
                        # Calculate begin_col and end_col based on the current col_offset
                        begin_col = gspread.utils.rowcol_to_a1(1, col_offset + 2)
                        end_col = gspread.utils.rowcol_to_a1(1, col_offset + 1 + len(columns) + 1)
                        # Add identifier information into a cell separated by "#"
                        identifier = f"{product_spreadsheet_id}#{sheet_name}#{begin_col}:{end_col}#{self.indices_to_cell((row_idx, status_col_index))}"
                        filtered_row.append(identifier)
                        filtered_values.append(filtered_row)

                if filtered_values:
                    start_col_offset = col_offset + 2  # Adjusted offset to 2
                    end_col = start_col_offset + len(columns) + 1  # +1 for the identifier information
                    if end_col > payment_sheet.col_count:
                        raise ValueError(
                            f"End column {end_col} exceeds the sheet's column count {payment_sheet.col_count}")

                    start_cell = gspread.utils.rowcol_to_a1(1, start_col_offset)
                    end_cell = gspread.utils.rowcol_to_a1(len(filtered_values), end_col)
                    cell_range = f"{start_cell}:{end_cell}"

                    payment_sheet.update(cell_range, filtered_values)
                    col_offset += len(columns) + 1 + 2  # Horizontal spacing between datasets

                    # Set the identifier column to wrap text to clip
                    identifier_col = start_col_offset + len(columns)
                    identifier_range = f"{gspread.utils.rowcol_to_a1(1, identifier_col)}:{gspread.utils.rowcol_to_a1(len(filtered_values), identifier_col)}"
                    payment_sheet.format(identifier_range, {"wrapStrategy": "CLIP"})

    def filter_and_transfer_data(self, product_spreadsheets, payment_spreadsheet_id, payment_sheet_name, columns):
        payment_spreadsheet = self.gc.open_by_key(payment_spreadsheet_id)
        payment_sheet = payment_spreadsheet.worksheet(payment_sheet_name)

        col_offset = 0  # Column offset between data ranges

        for product_spreadsheet_id, sheet_names in product_spreadsheets.items():
            product_spreadsheet = self.gc.open_by_key(product_spreadsheet_id)

            for sheet_name in sheet_names:
                product_sheet = product_spreadsheet.worksheet(sheet_name)
                values = product_sheet.get_all_values()
                values = [row for row in product_sheet.get_all_values() if any(cell.strip() for cell in row)]
                if not values:
                    continue

                # Detect the starting row and column (e.g., B2)
                start_row, start_col = 0, 0
                for i, row in enumerate(values):
                    if any(cell.strip() for cell in row):
                        start_row = i
                        start_col = next((idx for idx, cell in enumerate(row) if cell.strip()), 0)
                        break

                # Retrieve the header row
                header_row = values[start_row]
                col_indices = [header_row.index(col_name) for col_name in columns]

                # Create the new header row for the filtered values
                new_header_row = [header_row[idx] for idx in col_indices] + ["Identifier"]

                filtered_values = [new_header_row]  # Insert header at the beginning
                for row_idx, row in enumerate(values[start_row + 1:], start=start_row + 1):  # Skip the header row
                    if 'unpaid' in row:
                        filtered_row = [row[idx] for idx in col_indices]
                        # Add identifier information into a cell separated by "#"
                        identifier = f"{product_spreadsheet_id}#{sheet_name}#{self.indices_to_cell((row_idx + 1, start_col + 1))}"  # Adjust for correct cell reference
                        filtered_row.append(identifier)
                        filtered_values.append(filtered_row)

                if filtered_values:
                    start_col_offset = col_offset + 2  # Adjusted offset to 2
                    end_col = start_col_offset + len(columns) + 1  # +1 for the identifier information
                    if end_col > payment_sheet.col_count:
                        raise ValueError(
                            f"End column {end_col} exceeds the sheet's column count {payment_sheet.col_count}")

                    start_cell = gspread.utils.rowcol_to_a1(1, start_col_offset)
                    end_cell = gspread.utils.rowcol_to_a1(len(filtered_values), end_col)
                    cell_range = f"{start_cell}:{end_cell}"

                    payment_sheet.update(cell_range, filtered_values)
                    col_offset += len(columns) + 1 + 2  # Horizontal spacing between datasets

                    # Set the identifier column to wrap text to clip
                    identifier_col = start_col_offset + len(columns)
                    identifier_range = f"{gspread.utils.rowcol_to_a1(1, identifier_col)}:{gspread.utils.rowcol_to_a1(len(filtered_values), identifier_col)}"
                    payment_sheet.format(identifier_range, {"wrapStrategy": "CLIP"})

    def get_all_sheets(self, spreadsheet_id):
        spreadsheet = self.gc.open_by_key(spreadsheet_id)
        sheet_titles = []

        for sheet in spreadsheet.worksheets():
            sheet_titles.append(sheet.title)  # Store the title of each sheet

        return sheet_titles

    def get_header(self, spreadsheet_id, sheet_name):
        spreadsheet = self.gc.open_by_key(spreadsheet_id)
        sheet = spreadsheet.worksheet(sheet_name)
        values = sheet.get_all_values()
        values = [row for row in values if any(cell.strip() for cell in row)]
        start_row, start_col = 0, 0
        for i, row in enumerate(values):
            if any(cell.strip() for cell in row):
                start_row = i
                start_col = next((idx for idx, cell in enumerate(row) if cell.strip()), 0)
                break

        header_row = values[start_row]
        header_row = [col for col in header_row if col]
        return header_row

    def get_request_count(self):
        global request_count
        return request_count
