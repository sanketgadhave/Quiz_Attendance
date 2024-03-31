def update_configuration_sheet(service, sheet_name, column_name, spreadsheet_id):
    """
    Updates a Google Sheet by appending a new column with the provided name.

    Parameters:
    - service: Authorized Google Sheets API service instance.
    - sheet_name: The name of the sheet within the spreadsheet to update. This allows targeting sections like 'MasterSheet_A' for DIC_A, 'MasterSheet_C' for DIC_C, or 'MasterSheet' for DMQL.
    - column_name: The name of the new column to append.
    - spreadsheet_id: The ID of the spreadsheet to update.
    """

    # Adjust the range name to dynamically target the correct sheet within the spreadsheet
    range_name = f"{sheet_name}!A1:Z1"

    # Retrieve the header row to find the last used column
    header_row = \
    service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute().get('values', [[]])[0]
    last_column_index = len(header_row) if header_row else 0

    # Determine the range for appending the new column using R1C1 notation
    new_column_range = f"{sheet_name}!R1C{last_column_index + 1}"

    # Prepare the request body to append the new column with the specified name
    append_column_body = {"values": [[column_name]]}

    # Execute the update request to append the new column
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=new_column_range,
        valueInputOption="USER_ENTERED",
        body=append_column_body
    ).execute()

    return True  # Indicate success