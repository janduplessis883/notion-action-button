import streamlit as st
import pandas as pd
import gspread
from streamlit_gsheets import GSheetsConnection
import streamlit_shadcn_ui as ui
import time
from io import StringIO
from notionhelper import NotionHelper

notion_diabetes = "129fdfd68a97808bb5ffe511100fe0eb"
notion_smi = "130fdfd68a978000a617fafb9e478dc8"

st.set_page_config(
    initial_sidebar_state="collapsed", page_title="notion-action-button", page_icon=":material/sync:"
)
st.image("title.png")
# Initialize session state variables for passcode verification
if "passcode_verified" not in st.session_state:
    st.session_state["passcode_verified"] = False

if not st.session_state["passcode_verified"]:
    # Show the passcode input only if not yet verified
    passcode_input = st.text_input("Enter Passcode to Sync", type="password")

    # Check if the entered passcode matches the stored passcode
    if passcode_input and passcode_input == st.secrets["security"]["passcode"]:
        st.session_state["passcode_verified"] = True
        st.success("Passcode correct! You may now sync the registers.")
    elif passcode_input:
        st.error("Incorrect passcode. Please try again.")

# Only show sync button after passcode verification
if st.session_state["passcode_verified"]:
    if st.button(":material/sync: Sync DM + SMI Registers"):
        with st.spinner("Syncing NHS numbers..."):

            # Clear cache
            st.cache_data.clear()
            st.cache_resource.clear()

            nh = NotionHelper()

            # Establish connection to Google Sheets
            gsheets = GSheetsConnection(...)
            conn = st.connection("gsheets", type=GSheetsConnection)

            # Read registers from Google Sheets
            dm_register = conn.read(worksheet="dm_register")
            smi_register = conn.read(worksheet="smi_register")

            # Fetch data from Notion
            dm_notion = nh.get_all_pages_as_dataframe(notion_diabetes)
            smi_notion = nh.get_all_pages_as_dataframe(notion_smi)

            # Calculate interventions
            dm_intervention = dm_register[~dm_register['NHS number'].isin(dm_notion['NHS number'])]
            smi_intervention = smi_register[~smi_register['NHS number'].isin(smi_notion['NHS number'])]

            # Convert DataFrames to CSV
            dm_csv = dm_intervention.to_csv(index=False)
            smi_csv = smi_intervention.to_csv(index=False)

            # Download buttons for CSVs
            st.download_button(
                label=":material/download_for_offline: Download DM Intervention CSV",
                data=dm_csv,
                file_name="dm_intervention.csv",
                mime="text/csv"
            )

            st.download_button(
                label=":material/download_for_offline: Download SMI Intervention CSV",
                data=smi_csv,
                file_name="smi_intervention.csv",
                mime="text/csv"
            )
