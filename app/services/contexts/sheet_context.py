from googleapiclient.discovery import build

DONE_FILTER_VALUE = [
    "trả"
]

FILTER_COLUMN = "Trạng thái"

NOT_DONE_FILTER_VALUE = [
    "chưa trả"
]


class SheetContext:
    def __init__(self, context_manager):
        google_context = context_manager.get_context("google")
        creds = google_context.creds
        self.sheet_service = build('sheets', 'v4', credentials=creds)
        self.data = None
        self.src_sheet_metadata = None
        self.des_sheet_metadata = None

    ##### UNIT #####

    @staticmethod
    def cell_to_indices(cell: str):
        import re
        try:
            match = re.match(r"([A-Za-z]+)([0-9]+)", cell.split('!')[-1])
            if not match:
                raise ValueError(f"Invalid cell format: {cell}")
            col_str, row_str = match.groups()
            row_index = int(row_str) - 1
            col_index = sum(
                (ord(char.upper()) - ord('A') + 1) * (26 ** exp) for exp, char in enumerate(reversed(col_str))) - 1
            return row_index, col_index
        except Exception as e:
            print(f"Error parsing cell '{cell}': {e}")
            return None

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

    @staticmethod
    def getRangeFromCell(start_cell, len_of_range):
        for i in range(len_of_range):
            yield f"{start_cell[0]}{int(start_cell[1:]) + i}"

    def batch_update_cells(self, spreadsheet_id, updates):
        body = {
            "valueInputOption": "RAW",
            "data": updates
        }
        self.sheet_service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id, body=body).execute()

    def get_sheet_metadata(self, spreadsheet_id: str):
        sheet_metadata = self.sheet_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        return sheet_metadata

    def get_data_from_sheet(self, spreadsheet_id: str, range_name: str):
        result = self.sheet_service.spreadsheets().values().get(spreadsheetId=spreadsheet_id,
                                                                range=range_name).execute()
        self.data = result.get('values', [])
        return self.data

    def get_sheet_id(self, spreadsheet_id, sheet_title):
        sheet_metadata = self.sheet_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheets = sheet_metadata.get('sheets', [])
        for sheet in sheets:
            if sheet.get('properties', {}).get('title') == sheet_title:
                return sheet.get('properties', {}).get('sheetId')
        return None

    def get_all_sheets(self, spreadsheet_id):
        sheet_metadata = self.sheet_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheets = sheet_metadata.get('sheets', [])
        sheet_titles = [sheet.get('properties', {}).get('title', '') for sheet in sheets]
        return sheet_titles

    def save_data_to_sheet(self, spreadsheet_id: str, range_name: str, data: list):
        update_request = {
            "range": range_name,
            "majorDimension": "ROWS",
            "values": data
        }

        batch_update_values_request_body = {
            "valueInputOption": "RAW",
            "data": update_request
        }

        response = self.sheet_service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=batch_update_values_request_body
        ).execute()

        return response

    def clear_range(self, spreadsheet_id, range_name):
        self.sheet_service.spreadsheets().values().clear(spreadsheetId=spreadsheet_id, range=range_name,
                                                         body={}).execute()

    def update_range(self, spreadsheet_id, range_name, values):
        body = {
            'values': values
        }
        self.sheet_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=range_name,
            valueInputOption='RAW', body=body).execute()

    def update_cell(self, spreadsheet_id, cell_range, value):
        body = {
            'values': [[value]]
        }
        self.sheet_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=cell_range,
            valueInputOption='RAW', body=body).execute()

    ##### COMPLEX #####

    # return ranges of none empty data range
    def detect_ranges(self, spreadsheet_id: str, sheet_id: int):
        # Retrieve the spreadsheet metadata to get the sheet names and grid properties
        sheet_metadata = self.sheet_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheets = sheet_metadata.get('sheets', [])

        ranges = []

        for sheet in sheets:
            if sheet.get('properties', {}).get('sheetId') != sheet_id:
                continue

            sheet_title = sheet.get('properties', {}).get('title')
            grid_props = sheet.get('properties', {}).get('gridProperties', {})
            max_rows = grid_props.get('rowCount')
            max_cols = grid_props.get('columnCount')

            # Define a range that covers the entire sheet
            range_name = f"{sheet_title}!A1:{self.indices_to_cell((max_rows - 1, max_cols - 1))}"

            # Retrieve the values within the defined range
            result = self.sheet_service.spreadsheets().values().get(spreadsheetId=spreadsheet_id,
                                                                    range=range_name).execute()
            values = result.get('values', [])

            # Detect non-empty ranges and their starting cells
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

            for r_idx in range(max_rows):
                for c_idx in range(max_cols):
                    range_coords = find_range(r_idx, c_idx)
                    if range_coords:
                        min_r, min_c, max_r, max_c = range_coords
                        range_str = f"{sheet_title}!{self.indices_to_cell((min_r, min_c))}:{self.indices_to_cell((max_r, max_c))}"
                        ranges.append(range_str)

        return ranges

    # return starting cells of none empty data range
    def get_non_empty_ranges_start(self, spreadsheet_id: str, sheet_id: int):
        # Retrieve the spreadsheet metadata to get the sheet names and grid properties
        sheet_metadata = self.sheet_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheets = sheet_metadata.get('sheets', [])

        starting_cells = []

        for sheet in sheets:
            if sheet.get('properties', {}).get('sheetId') != sheet_id:
                continue

            grid_props = sheet.get('properties', {}).get('gridProperties', {})
            max_rows = grid_props.get('rowCount')
            max_cols = grid_props.get('columnCount')

            # Define a range that covers the entire sheet
            range_name = f"{sheet.get('properties', {}).get('title')}!A1:{self.indices_to_cell((max_rows - 1, max_cols - 1))}"

            # Retrieve the values within the defined range
            result = self.sheet_service.spreadsheets().values().get(spreadsheetId=spreadsheet_id,
                                                                    range=range_name).execute()
            values = result.get('values', [])

            # Detect non-empty ranges and their starting cells
            non_empty_cells = set()

            for r_idx, row in enumerate(values):
                for c_idx, cell in enumerate(row):
                    if cell:
                        non_empty_cells.add((r_idx, c_idx))

            visited = set()

            def find_range_start(r, c):
                if (r, c) in non_empty_cells and (r, c) not in visited:
                    visited.add((r, c))
                    for i in range(r, max_rows):
                        for j in range(c, max_cols):
                            if (i, j) in non_empty_cells:
                                visited.add((i, j))
                            else:
                                break
                    return self.indices_to_cell((r, c))
                return None

            for r_idx in range(max_rows):
                for c_idx in range(max_cols):
                    start_cell = find_range_start(r_idx, c_idx)
                    if start_cell:
                        starting_cells.append(start_cell)

        return starting_cells

    # return header and data of filtered data
    def filter_data_from_sheet(self, spreadsheet_id: str, range_name: str, input_header: str, input_value):
        input_value = str(input_value).strip().lower()
        # Retrieve the values within the defined range
        result = self.sheet_service.spreadsheets().values().get(spreadsheetId=spreadsheet_id,
                                                                range=range_name).execute()
        values = result.get('values', [])

        if not values:
            return []  # Return empty list if no values found

        # Find the index of the column with the specified header
        header = values[0]
        try:
            col_index = header.index(input_header)
        except ValueError:
            return []  # Return empty list if the column name is not found

        # Parse the range_name to get the sheet title
        sheet_title, cell_range = range_name.split('!')
        cell_range_start = cell_range.split(':')[0]

        # Find the starting row index of the range (assuming standard A1 notation)
        start_row_idx = int(''.join(filter(str.isdigit, cell_range_start))) - 1

        # Iterate through the rows to find matching values in the specified column
        matching_cells = []
        filter_data = []
        for r_idx, row in enumerate(values[1:], start=1):  # Skip header row
            if len(row) > col_index and str(row[col_index]).strip().lower() == input_value:
                cell_address = f"{sheet_title}!{self.indices_to_cell((start_row_idx + r_idx, col_index))}"
                matching_cells.append(cell_address)
                filter_data.append(row)

        for i in range(len(filter_data)):
            filter_data[i].insert(0, matching_cells[i])
        return header, filter_data

    def get_unique_values(self, spreadsheet_id: str, range_name: str, col_title: str):
        # Retrieve the values within the defined range
        values = self.get_data_from_sheet(spreadsheet_id, range_name)

        if not values:
            return []  # Return empty list if no values found

        # Find the index of the column with the specified title
        header = values[0]
        try:
            col_index = header.index(col_title)
        except ValueError:
            return []  # Return empty list if the column name is not found

        # Collect unique values from the specified column
        unique_values = set()
        for row in values[1:]:  # Skip header row
            if len(row) > col_index:
                unique_values.add(row[col_index])

        return list(unique_values)

    def fill_color_to_matching_cells(self, spreadsheet_id: str, matching_cells: list, color: dict):
        requests = []
        for cell in matching_cells:
            sheet_title, cell_id = cell.split('!')
            start_row_idx = int(''.join(filter(str.isdigit, cell_id.split(':')[0]))) - 1
            start_col_idx = ord(cell_id[0]) - ord('A')
            end_row_idx = int(
                ''.join(filter(str.isdigit, cell_id.split(':')[1]))) - 1 if ':' in cell_id else start_row_idx
            end_col_idx = ord(cell_id.split(':')[-1][0]) - ord('A') if ':' in cell_id else start_col_idx

            requests.append({
                "repeatCell": {
                    "range": {
                        "sheetId": self.get_sheet_id(spreadsheet_id, sheet_title),
                        "startRowIndex": start_row_idx,
                        "endRowIndex": end_row_idx + 1,
                        "startColumnIndex": start_col_idx,
                        "endColumnIndex": end_col_idx + 1,
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": color
                        }
                    },
                    "fields": "userEnteredFormat.backgroundColor"
                }
            })

        body = {
            "requests": requests
        }

        self.sheet_service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()

    def fill_color_to_matching_range(self, spreadsheet_id: str, start_cells: list, len_of_range: int, color: dict):
        requests = []
        for cell in start_cells:
            range_str = self.getRangeFromCell(cell, len_of_range)
            sheet_title, cell_range = range_str.split('!')
            start_cell, end_cell = cell_range.split(':')
            start_row_idx = int(''.join(filter(str.isdigit, start_cell))) - 1
            start_col_idx = self.col_to_index(''.join(filter(str.isalpha, start_cell)))
            end_row_idx = int(''.join(filter(str.isdigit, end_cell))) - 1
            end_col_idx = self.col_to_index(''.join(filter(str.isalpha, end_cell)))

            requests.append({
                "repeatCell": {
                    "range": {
                        "sheetId": self.get_sheet_id(spreadsheet_id, sheet_title),
                        "startRowIndex": start_row_idx,
                        "endRowIndex": end_row_idx + 1,
                        "startColumnIndex": start_col_idx,
                        "endColumnIndex": end_col_idx + 1,
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": color
                        }
                    },
                    "fields": "userEnteredFormat.backgroundColor"
                }
            })

        body = {
            "requests": requests
        }

        self.sheet_service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()

    def remove_rows_containing_value(self, spreadsheet_id, range_name, value: str):
        # Retrieve data from the specified range
        data = self.get_data_from_sheet(spreadsheet_id, range_name)

        if not data:
            return

        # Extract header and filter rows
        filtered_data = []
        filtered_data += [sublist for sublist in data if value not in sublist]

        # Clear the original range
        self.clear_range(spreadsheet_id, range_name)

        # Update the range with filtered data
        self.update_range(spreadsheet_id, range_name, filtered_data)

    def sync_data(self, src_spreadsheet_id, des_spreadsheet_id, src_range, des_range):

        src_data = self.get_data_from_sheet(src_spreadsheet_id, src_range)
        des_data = self.get_data_from_sheet(des_spreadsheet_id, des_range)

        des_filter_data = [row for row in des_data if DONE_FILTER_VALUE[0] in row]

        sync_col = ["Ví trả", FILTER_COLUMN]

        src_header = src_data[0]
        des_header = des_data[0]

        src_sync_index = [src_header.index(col) for col in sync_col]

        des_sync_index = [des_header.index(col) for col in sync_col]

        def create_des_sync_data(des_data, des_sync_index):
            _des_sync_data = []

            for sublist in des_data:
                sync_sublist = [sublist[i] for i in des_sync_index]
                _des_sync_data.append(sync_sublist)

            return _des_sync_data

        des_sync_data = create_des_sync_data(des_filter_data, des_sync_index)

        cell_to_sync = []
        for sublist in des_filter_data:
            tmp_cell_to_sync = sublist[0]
            tmp_r, tmp_c = self.cell_to_indices(tmp_cell_to_sync)
            for i in src_sync_index:
                cell_to_sync.append(tmp_cell_to_sync.split("!")[0] + "!" +self.indices_to_cell((tmp_r, i)))

        def map_cells_to_data(des_sync_data, cell_to_sync):
            # Flatten des_sync_data
            flat_des_sync_data = [item for sublist in des_sync_data for item in sublist]

            # Create a dictionary to map each cell to its corresponding data
            _cell_data_map = dict(zip(cell_to_sync, flat_des_sync_data))

            return _cell_data_map

        cell_data_map = map_cells_to_data(des_sync_data, cell_to_sync)

        updates = []

        for cell, value in cell_data_map.items():
            updates.append({
                "range": cell,
                "values": [[value]]
            })

        if updates:
            self.batch_update_cells(src_spreadsheet_id, updates)

        return {"status": "OK"}
