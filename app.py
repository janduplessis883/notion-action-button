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
    layout="wide", initial_sidebar_state="collapsed", page_title="notion-action-button", page_icon=":material/sync:"
)

action = st.button("Sync DM + SMI Registers")
if action:
    with st.spinner("Sync NHS numbers..."):
        nh = NotionHelper()

        gsheets = GSheetsConnection(...)
        conn = st.connection("gsheets", type=GSheetsConnection)

        dm_register = conn.read(worksheet="dm_register")
        smi_register = conn.read(worksheet="smi_register")

        dm_notion = nh.get_all_pages_as_dataframe(notion_diabetes)
        smi_notion = nh.get_all_pages_as_dataframe(notion_smi)

        dm_intervention = dm_register[~dm_register['NHS number'].isin(dm_notion['NHS number'])]
        smi_intervention = smi_register[~smi_register['NHS number'].isin(smi_notion['NHS number'])]

        # Convert DataFrames to CSV
        dm_csv = dm_intervention.to_csv(index=False)
        smi_csv = smi_intervention.to_csv(index=False)

        # Add download buttons for CSVs
        st.download_button(
            label="Download DM Intervention CSV",
            data=dm_csv,
            file_name="dm_intervention.csv",
            mime="text/csv"
        )

        st.download_button(
            label="Download SMI Intervention CSV",
            data=smi_csv,
            file_name="smi_intervention.csv",
            mime="text/csv"
        )
