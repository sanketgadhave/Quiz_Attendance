import streamlit as st
from src.generate_qr_code import generate_qr_code
from src.update_excel import update_excel

excel_path = 'data_files/attendance.xlsx'
# Streamlit UI
st.title('Quiz Attendance System')

# TA Authentication
ta_auth = st.expander("TA Authentication")
with ta_auth:
    passcode_input = st.text_input("Enter the 4-digit passcode to access QR code scanner", type="password",
                                   key="ta_passcode")

    # Placeholder for authenticated section
    if passcode_input == "1234":  # Use a more secure passcode in a real app
        st.success("Authenticated Successfully! Ready to scan QR codes.")
        # Embed QR code scanner (placeholder, replace with actual implementation)
        st.markdown("""
            <div id="qr-reader" style="width:500px;height:500px;"></div>
            <script src="https://unpkg.com/html5-qrcode" type="text/javascript"></script>
            <script>
                function onScanSuccess(decodedText, decodedResult) {
                    // Handle on success condition with the decoded text or result.
                    console.log(`Code scanned = ${decodedText}`, decodedResult);
                }

                var html5QrcodeScanner = new Html5QrcodeScanner(
                    "qr-reader", { fps: 10, qrbox: 250 }, /* verbose= */ false);
                html5QrcodeScanner.render(onScanSuccess);
            </script>
        """, unsafe_allow_html=True)
    elif passcode_input:
        st.error("Incorrect passcode. Please try again.")

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