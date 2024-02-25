def update_configuration_sheet(service, subject, new_sheet_name, subject_to_spreadsheet_id):
    config_spreadsheet_id = subject_to_spreadsheet_id['DIC']  # Configuration storage location
    config_range = "Configuration!A2:B"

    spreadsheet_info = service.spreadsheets().get(spreadsheetId=subject_to_spreadsheet_id[subject]).execute()
    sheet_names = [sheet['properties']['title'] for sheet in spreadsheet_info.get('sheets', [])]
    if new_sheet_name in sheet_names:
        print("INSIDEEEEE")
        # If the sheet already exists, return a message indicating so
        return None

    # Fetch existing configuration data
    result = service.spreadsheets().values().get(spreadsheetId=config_spreadsheet_id, range=config_range).execute()
    values = result.get('values', [])

    # Check if the subject already has an entry and determine the update range
    row_to_update = None
    for i, row in enumerate(values, start=2):  # Start=2 accounts for header row and 1-based indexing
        if row and row[0] == subject:
            row_to_update = i
            break

    # Prepare the request body for updating or appending the active sheet name
    if row_to_update:
        # Subject found, prepare to update its active sheet name
        update_range = f"Configuration!B{row_to_update}"
        value_input_option = "RAW"
        update_body = {
            "values": [[new_sheet_name]]
        }
        service.spreadsheets().values().update(
            spreadsheetId=config_spreadsheet_id, range=update_range,
            valueInputOption=value_input_option, body=update_body
        ).execute()
    else:
        # Subject not found, append a new entry
        append_body = {
            "values": [[subject, new_sheet_name]]
        }
        append_range = "Configuration!A:B"  # Append at the end of the Configuration sheet
        service.spreadsheets().values().append(
            spreadsheetId=config_spreadsheet_id, range=append_range,
            valueInputOption="USER_ENTERED", body=append_body, insertDataOption="INSERT_ROWS"
        ).execute()

    service.spreadsheets().values().update(
        spreadsheetId=config_spreadsheet_id,
        range="Configuration!B2",
        valueInputOption="RAW",
        body={"values": [[subject]]}  # Set the active subject
    ).execute()

    # Return the active sheet name for further use
    return new_sheet_name