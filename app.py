import streamlit as st
from src.generate_qr_code import generate_qr_code
from src.update_excel import append_to_sheet

# Streamlit UI
st.title('Quiz Attendance System')

with st.form("student_info", clear_on_submit=True):
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    ub_person_number = st.text_input("UB Person Number")
    submitted = st.form_submit_button("Submit")

    if submitted:
        # Prepare data for Google Sheets
        data = [first_name, last_name, ub_person_number, ""]  # Leave "Custom" column empty for now
        append_to_sheet(data, "Sheet1")  # Simplified range, adjust if necessary

        # Generate QR code with URL
        # Assuming you have a web service endpoint or script ready to handle the query and mark attendance
        base_url = "https://script.google.com/macros/s/AKfycbzYdiYkY8ceFPQmlSJ_3pThrm8oOAatJ_af7v5ALIRGX7qlGVEDLUULpoosV1mOBC4wJQ/exec"
        qr_data = f"{base_url}?ubPersonNumber={ub_person_number}"
        qr_code_image = generate_qr_code(qr_data)

        # Display QR Code
        st.image(qr_code_image.getvalue(), caption='Your QR Code', use_column_width=True)