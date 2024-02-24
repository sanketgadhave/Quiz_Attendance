import os
import pandas as pd


# Function to update the Excel file
def update_excel(data, path):
    # Check if the Excel file exists
    if os.path.exists(path):
        df = pd.read_excel(path)
    else:
        df = pd.DataFrame(columns=['First Name', 'Last Name', 'UB Person Number', 'QR Code'])
    new_row = pd.DataFrame([data])
    print(data)
    # Append new data
    df = pd.concat([df, new_row], ignore_index=True)
    #df = df.append(data, ignore_index=True)

    # Save the updated DataFrame to Excel
    with pd.ExcelWriter(path, engine='openpyxl', mode='w') as writer:
        df.to_excel(writer, index=False)