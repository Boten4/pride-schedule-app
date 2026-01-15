import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, date

# --- 1. הגדרות דף ---
st.set_page_config(page_title="שיבוץ משמרות - ארכיון הגאווה", page_icon="🏳️‍🌈", layout="centered")

# --- עיצוב מיוחד לעברית (CSS) ---
st.markdown("""
<style>
    /* כיוון כללי לימין */
    .stApp { direction: rtl; text-align: right; }
    
    /* יישור כל הטקסטים, הכותרות והתוויות לימין */
    h1, h2, h3, p, div, label, span { text-align: right !important; }
    
    /* עיצוב ספציפי לתיבת התאריך */
    .stDateInput input {
        text-align: right !important;
        direction: rtl !important;
    }
    
    /* הזזת האייקון של לוח השנה לצד שמאל */
    div[data-baseweb="input"] > div {
        flex-direction: row-reverse;
    }

    /* כפתורים ומסגרות */
    .stButton button { width: 100%; border-radius: 8px; }
    div[data-testid="stExpander"] { border: 1px solid #ddd; border-radius: 10px; }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
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
    
    # הקישור לקובץ שלך
    spreadsheet_url = "https://docs.google.com/spreadsheets/d/1UQQ5oqpMMiQPnJF0q2i-pUnl4jJxhpzJc2g-P2mxFCQ/edit?gid=0#gid=0"
    
    return client.open_by_url(spreadsheet_url).sheet1

# --- 3. פונקציה לרישום מתנדב ---
def register_volunteer(row_index, name, phone, email):
    try:
        sh = get_worksheet()
        actual_row = row_index + 2
        
        sh.update_cell(actual_row, 4, name)
        sh.update_cell(actual_row, 5, phone)
        sh.update_cell(actual_row, 6, email)
        
        st.balloons()
        st.success(f"תודה {name}! נרשמת בהצלחה. 🎉")
        st.rerun()
        
    except Exception as e:
        st.error(f"אירעה שגיאה בשמירה: {e}")

# --- 4. הממשק הראשי ---
def main():
    try:
        st.image("logo.jpg", width=120)
    except:
        pass
        
    st.title("לוח משמרות 🏳️‍🌈")
    st.write("בחרו תאריך כדי לראות את המשמרות:")
    
    # --- השינוי כאן: הוספנו פורמט יום/חודש/שנה ---
    selected_date = st.date_input(
        "📅 לחצו לבחירת תאריך",
        value=date.today(),
        format="DD/MM/YYYY"  # <-- זה מסדר את המספרים יפה
    )
