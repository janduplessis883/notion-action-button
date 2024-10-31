import streamlit as st
import pandas as pd
import gspread
from streamlit_gsheets import GSheetsConnection
import streamlit_shadcn_ui as ui
import time


st.set_page_config(
    layout="wide", initial_sidebar_state="collapsed", page_title="notion-action-button", page_icon=":material/sync:"
)

conn = st.connection("gsheets", type=GSheetsConnection)

# Time-to-live in seconds (10 minutes)
ttl_seconds = 20 * 60

action = st.button("Sync NHS Numbers")
if action:
    st.info('Syncing...')
    time.sleep(5)
    st.rerun()
