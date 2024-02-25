def get_active_sheet_name(service, subject, subject_to_spreadsheet_id):
    config_spreadsheet_id = subject_to_spreadsheet_id['DIC']  # Assuming configuration is stored in the DIC sheet
    config_range = "Configuration!A:B"

    # Fetch existing configuration data
    try:
        result = service.spreadsheets().values().get(spreadsheetId=config_spreadsheet_id, range=config_range).execute()
        values = result.get('values', [])
    except Exception as e:
        print(f"Error fetching configuration data: {e}")
        return None

    # Iterate through configuration data to find the active sheet name for the given subject
    print("In SheetManagement", subject)
    for row in values:
        if row and row[0] == subject:
            return row[1]  # Return the ActiveSheetName if subject matches
    return None


def get_active_subject(service, config_spreadsheet_id):
    # Fetch the active subject from the "Configuration" sheet
    active_subject_range = "Configuration!B2"  # The cell where the active subject is stored
    result = service.spreadsheets().values().get(
        spreadsheetId=config_spreadsheet_id, range=active_subject_range
    ).execute()
    values = result.get('values', [])

    if values:
        return values[0][0]  # Return the active subject
    else:
        return None