import streamlit as st
from src.update_excel import append_to_sheet, service
from src.update_configuration_sheet import update_configuration_sheet
import json




if 'admin_authenticated' not in st.session_state:
    st.session_state.admin_authenticated = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'main'
if 'authentication_failed' not in st.session_state:
    st.session_state['authentication_failed'] = False
if 'batch_storage' not in st.session_state:
    st.session_state.batch_storage = []

if 'selected_subject' not in st.session_state:
    st.session_state['selected_subject'] = 'DIC'
# Passcode for TA access
TA_PASSCODE = "1234"
subject_to_spreadsheet_id = {
    'DIC': '17zLyXGck6_1tGc7cf_KWFWDsV5RZzu7o5kHlkWN8JEc',
    'DMQL': '1wxcqkT3EhV_4sXhIFTMTadvDvgmnGSQK6OhvihAigI0',
}
# Streamlit UI
st.title('Quiz Attendance System')

if not st.session_state.admin_authenticated:
    if st.button('Admin Login'):
        st.session_state.current_page = 'admin_login'
        st.experimental_rerun()

# Admin Login "Page"
if st.session_state.current_page == 'admin_login':
    passcode_input = st.text_input("Enter TA passcode for administrative actions:", type="password")
    if passcode_input:
        if passcode_input == TA_PASSCODE:
            st.success("Authenticated successfully!")
            st.session_state.admin_authenticated = True
            st.session_state.current_page = 'admin_page'
            st.experimental_rerun()  # Navigate to admin page
        else:
            st.error("Incorrect passcode. Please try again.")
            st.session_state['authentication_failed'] = True


# Admin Page
if st.session_state.admin_authenticated and st.session_state.current_page == 'admin_page':
    subject = st.selectbox('Select Subject', ['DIC', 'DMQL'])
    st.session_state.selected_subject = subject
    with open('active_subject.txt', 'w') as file:
        file.write(st.session_state.selected_subject)
    new_column_name = st.text_input('Name for New Quiz Column',
                                    value='Quiz X')  # Provide a default or placeholder value

    if st.button('Create New Column') and new_column_name:
        # Call function to update the master sheet with a new column
        # Assuming 'update_configuration_sheet' now handles adding a new column
        success = update_configuration_sheet(service, subject, new_column_name, subject_to_spreadsheet_id)

        if success:
            st.success(f"New column '{new_column_name}' created successfully for {subject}.")
        else:
            st.error("Failed to create new column. Please try again.")

    if st.button('Log Out'):
        st.session_state.admin_authenticated = False
        st.session_state.current_page = 'main'  # Optionally reset the current page to 'main'
        st.experimental_rerun()  # Refresh the app to reflect the logout state

    if st.session_state['authentication_failed']:
        st.error("Incorrect passcode. Please try again.")

if st.session_state.current_page == 'main':
    with st.form("student_info", clear_on_submit=True):
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        ub_person_number = st.text_input("UB Person Number")
        submitted = st.form_submit_button("Submit")

        if submitted:
            try:
                with open('active_subject.txt', 'r') as file:
                    active_subject = file.read().strip()
                # Load the correct JSON file based on the selected subject
                json_filename = f'qr_code_mappings/{active_subject}.json'
                try:
                    with open(json_filename, 'r') as f:
                        qr_code_mapping = json.load(f)

                    qr_code_filename = qr_code_mapping.get(ub_person_number)
                    if qr_code_filename:
                        # Assuming the QR code images are stored relative to the Streamlit app's running directory
                        st.image(qr_code_filename, caption="Your QR Code", width=300)
                    else:
                        st.error("No QR code found for this UB Person Number.")
                except FileNotFoundError:
                    st.error(f"The file {json_filename} does not exist. Please ensure the QR codes have been generated.")
            except FileNotFoundError:
                st.error("The active subject file does not exist. Please ensure a TA has set the active subject.")
                active_subject = None  # Or handle this case as appropriate for your application
