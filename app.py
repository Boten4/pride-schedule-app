import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, date
import base64 # <-- הוספנו את זה בשביל הטריק של התמונה הצמודה

# --- 1. הגדרות דף ---
st.set_page_config(page_title="שיבוץ משמרות - ארכיון הגאווה", page_icon="🏳️‍⚧️", layout="centered")

# --- עיצוב CSS ---
st.markdown("""
<style>
    .stApp { direction: rtl; text-align: right; }
    h1, h2, h3, p, div, label, span, button { text-align: right !important; }
    .stDateInput input { text-align: right !important; direction: rtl !important; }
    div[data-baseweb="input"] > div { flex-direction: row-reverse; }
    .stButton button { width: 100%; border-radius: 8px; }
    div[data-testid="stExpander"] { border: 1px solid #ddd; border-radius: 10px; }
    .block-container { padding-top: 1rem; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* עיצוב מיוחד לכותרת כדי שהדגל יהיה בקו ישר עם הטקסט */
    .title-container {
        display: flex;
        align-items: center;
        gap: 10px; /* רווח קטנטן בין הטקסט לדגל */
    }
</style>
""", unsafe_allow_html=True)

# --- 2. חיבור לגוגל שיטס ---
def get_worksheet():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scopes
    )
    client = gspread.authorize(credentials)
    return client.open_by_url("
