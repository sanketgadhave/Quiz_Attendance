import qrcode
import pandas as pd
import json
import os

# Base URL for the Google Apps Script Web App handling attendance
base_url = "https://script.google.com/macros/s/AKfycbwFXeiQIe1q59EyZWUfn-LeblRlLIr-BrCSfRQJmdSf6MCY7iz0omj_vqow7cK5knFz/exec"

# Read the Excel file without header, assuming UB Person Numbers are in the first column (index 0)
students_df = pd.read_excel("DMQL_list.xlsx", usecols=[0, 1], header=None)

# Directory for QR codes
qr_code_dir = 'qr_codes/DMQL_A'  # Adjusted to include subject in the path
if not os.path.exists(qr_code_dir):
    os.makedirs(qr_code_dir)

# Initialize an empty dictionary for QR code mappings
qr_code_mappings = {}

for index, row in students_df.iterrows():
    ub_person_number_str = str(row[0])  # Access by column index
    section = str(row[1])
    # Updated QR data to include only ubPersonNumber in the query parameters
    qr_data = f"{base_url}?ubPersonNumber={ub_person_number_str}&section={section}"

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')

    qr_filename = f"{qr_code_dir}/{ub_person_number_str}_{section}.png"
    img.save(qr_filename)
    qr_code_mappings[f"{ub_person_number_str}"] = qr_filename

# Save the mappings to a JSON file
json_filename = 'qr_code_mappings/DMQL_A.json'
if not os.path.exists('qr_code_mappings'):
    os.makedirs('qr_code_mappings')
with open(json_filename, 'w') as json_file:
    json.dump(qr_code_mappings, json_file)

print(f"QR code mappings have been saved to {json_filename}.")
