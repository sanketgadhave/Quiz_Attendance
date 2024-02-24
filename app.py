import streamlit as st
from src.generate_qr_code import generate_qr_code
from src.update_excel import update_excel

excel_path = 'data_files/attendance.xlsx'
# Streamlit UI
st.title('Quiz Attendance System')

with st.form("student_info", clear_on_submit=True):
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    ub_person_number = st.text_input("UB Person Number")
    submitted = st.form_submit_button("Submit")

    if submitted:
        data = {
            'First Name': first_name,
            'Last Name': last_name,
            'UB Person Number': ub_person_number,
        }

        # Generate QR code
        qr_data = f"{first_name} {last_name} {ub_person_number}"
        qr_code_image = generate_qr_code(qr_data)
        data['QR Code'] = qr_data  # You might want to store a reference instead

        update_excel(data, excel_path)

        # Display QR Code
        st.image(qr_code_image, caption='Your QR Code', use_column_width=True)