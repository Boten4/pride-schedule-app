import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, date

# --- 1. הגדרות דף (חייב להיות ראשון) ---
st.set_page_config(page_title="שיבוץ משמרות - ארכיון הגאווה", page_icon="🏳️‍🌈", layout="centered")

# --- עיצוב CSS (סידור לימין) ---
st.markdown("""
<style>
    /* כיוון כללי לימין */
    .stApp { direction: rtl; text-align: right; }
    
    /* יישור טקסטים לימין */
    h1, h2, h3, p, div, label, span, button { text-align: right !important; }
    
    /* סידור תיבת התאריך */
    .stDateInput input { text-align: right !important; direction: rtl !important; }
    div[data-baseweb="input"] > div { flex-direction: row-reverse; }

    /* כפתורים ומסגרות */
    .stButton button { width: 100%; border-radius: 8px; }
    div[data-testid="stExpander"] { border: 1px solid #ddd; border-radius: 10px; }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 2. חיבור לגוגל שיטס ---
def get_worksheet():
    # פונקציה שמתחברת לגיליון
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scopes
    )
    client = gspread.authorize(credentials)
    # הקישור לקובץ
    return client.open_by_url("https://docs.google.com/spreadsheets/d/1UQQ5oqpMMiQPnJF0q2i-pUnl4jJxhpzJc2g-P2mxFCQ/edit?gid=0#gid=0").sheet1

# --- 3. פונקציה לרישום מתנדב ---
def register_volunteer(row_index, name, phone, email):
    try:
        sh = get_worksheet()
        actual_row = row_index + 2
        sh.update_cell(actual_row, 4, name)
        sh.update_cell(actual_row, 5, phone)
        sh.update_cell(actual_row, 6, email)
        st.balloons()
        st.success(f"תודה {name}! נרשמת בהצלחה.")
        st.rerun()
    except Exception as e:
        st.error(f"שגיאה בשמירה: {e}")

# --- 4. המסך הראשי ---
def main():
    try:
        st.image("logo.jpg", width=120)
    except:
        pass
        
    st.title("לוח משמרות 🏳️‍🌈")
    st.write("בחרו תאריך כדי לראות את המשמרות:")
    
    # בחירת תאריך עם פורמט ישראלי
    selected_date = st.date_input(
        "📅 לחצו לבחירת תאריך",
        value=date.today(),
        format="DD/MM/YYYY"
    )
    st.write("---")

    try:
        sh = get_worksheet()
        data = sh.get_all_records()
        daily_shifts = []
        
        # חיפוש משמרות לפי התאריך שנבחר
        for i, row in enumerate(data):
            date_str = str(row['Date'])
            if not date_str: continue
            try:
                shift_date = datetime.strptime(date_str, "%d/%m/%Y").date()
                if shift_date == selected_date:
                    daily_shifts.append((i, row))
            except ValueError:
                continue

        # הצגת התוצאות
        if not daily_shifts:
            st.info(f"אין משמרות בתאריך {selected_date.strftime('%d/%m/%Y')}.")
        else:
            st.success(f"נמצאו {len(daily_shifts)} משמרות:")
            for original_index, row in daily_shifts:
                time_range = row['Time']
                volunteer = str(row['Volunteer'])
                is_taken = len(volunteer) > 1
                
                header = f"🔒 {time_range} (תפוס)" if is_taken else f"🟢 {time_range} (פנוי)"
                
                with st.expander(header, expanded=not is_taken):
                    if is_taken:
                        st.write(f"**מאויש ע\"י:** {volunteer}")
                    else:
                        with st.form(key=f"form_{original_index}"):
                            name = st.text_input("שם מלא")
                            phone = st.text_input("טלפון")
                            email = st.text_input("מייל")
                            if st.form_submit_button("הרשמה"):
                                if name:
                                    register_volunteer(original_index, name, phone, email)
                                else:
                                    st.error("חובה שם מלא")

    except Exception as e:
        st.error("שגיאה בחיבור. נסו לרענן את הדף.")

if __name__ == "__main__":
    main()
