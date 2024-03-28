def update_configuration_sheet(service, subject, column_name, subject_to_spreadsheet_id):
    spreadsheet_id = subject_to_spreadsheet_id[subject]  # Use the spreadsheet ID for the selected subject

    # Retrieve information about the "MasterSheet"
    master_sheet_name = "MasterSheet"  # Replace with your actual master sheet name if different
    range_name = f"{master_sheet_name}!A1:Z1"  # This range should be wide enough to cover all existing columns

    # Get the header row from the master sheet to find the last used column
    header_row = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=range_name
    ).execute().get('values', [[]])[0]  # Get the first (and only) row

    # Find the index of the last column with data (the header row)
    last_column_index = len(header_row) if header_row else 0
    new_column_range = f"{master_sheet_name}!R1C{last_column_index + 1}"  # Using R1C1 notation for appending column

    # Append the new column with the TA-provided name
    append_column_body = {
        "values": [[column_name]]
    }
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=new_column_range,
        valueInputOption="USER_ENTERED",
        body=append_column_body
    ).execute()

    # Optionally update configuration if needed
    # Your existing logic for updating configuration goes here

    return column_name