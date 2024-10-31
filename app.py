import streamlit as st
import pandas as pd
import gspread
from streamlit_gsheets import GSheetsConnection
import streamlit_shadcn_ui as ui
import time
from io import StringIO

notion_diabetes = "129fdfd68a97808bb5ffe511100fe0eb"
notion_smi = "130fdfd68a978000a617fafb9e478dc8"

st.set_page_config(
    layout="wide", initial_sidebar_state="collapsed", page_title="notion-action-button", page_icon=":material/sync:"
)

action = st.button("Sync NHS Numbers")
if action:
    with st.spinner("Sync NHS numbers..."):

        gsheets = GSheetsConnection(...)
        conn = st.connection("gsheets", type=GSheetsConnection)

        dm_register = conn.read(worksheet="dm_register")
        st.dataframe(dm_register)

        smi_register = conn.read(worksheet="smi_register")
        st.dataframe(smi_register)
















        st.download_button(
            label="Download Empty CSV",
            file_name="empty.csv",
            data="text/csv"
        )










settings = st.checkbox('Settings')
if settings:
    st.write("DM + SMI Register - Google Sheet")
    st.write("Notion Databases fixed IDs")
