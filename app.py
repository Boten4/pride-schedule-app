import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, date

# --- 1. הגדרות דף ---
st.set_page_config(page_title="שיבוץ משמרות - ארכיון הגאווה", page_icon="🏳️‍🌈", layout="centered")

# עיצוב לימין (RTL)
st.markdown("""
<style>
    .stApp { direction: rtl; text-align: right; }
    h1, h2, h3, p, div, label, input, span { text-align: right !important; }
    .stButton button { width: 100%; border-radius: 10px; }
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
    
    # הקישור הישיר לקובץ ששלחת
    spreadsheet_url = "https://docs.google.com/spreadsheets/d/1UQQ5oqpMMiQPnJF0q2i-pUnl4jJxhpzJc2g-P2mxFCQ/edit?gid=0#gid=0"
    
    return client.open_by_url(spreadsheet_url).sheet1

# --- 3. פונקציה לרישום מתנדב ---
def register_volunteer(row_index, name, phone, email):
    try:
        sh = get_worksheet()
        actual_row = row_index + 2  # המרה למספר שורה אמיתי בגיליון
        
        # עדכון העמודות (D=4, E=5, F=6)
        sh.update_cell(actual_row, 4, name)
        sh.update_cell(actual_row, 5, phone)
        sh.update_cell(actual_row, 6, email)
        
        st.balloons()
        st.success(f"תודה {name}! נרשמת בהצלחה למשמרת. 🎉")
        st.rerun()
        
    except Exception as e:
        st.error(f"אירעה שגיאה בשמירה: {e}")

# --- 4. הממשק הראשי (גרסת בדיקה) ---
def main():
    # לוגו
    try:
        st.image("logo.jpg", width=150)
    except:
        pass
        
    st.title("לוח משמרות - ארכיון הגאווה 🏳️‍🌈")
    st.write("---")

    # --- בדיקת חיבור ---
    try:
        # בדיקה 1: הדפסת המייל של הרובוט
        try:
            robot_email = st.secrets["gcp_service_account"]["client_email"]
            st.info(f"🤖 הרובוט מנסה להתחבר עם המייל: \n\n `{robot_email}`")
            st.write("👆 וודאי שהמייל הזה נמצא ברשימת ה-Share בגוגל שיטס!")
        except:
            st.error("❌ לא הצלחנו אפילו לקרוא את המייל מה-Secrets. האם הקובץ secrets.toml תקין?")

        sh = get_worksheet()
        data = sh.get_all_records()

        # אם הגענו לפה - החיבור הצליח!
        st.success("✅ החיבור הצליח! הטבלה נטענה.")

        # --- המשך הקוד הרגיל (סינון משמרות) ---
        future_shifts = []
        for i, row in enumerate(data):
            date_str = str(row['Date'])
            if not date_str: continue
            try:
                shift_date = datetime.strptime(date_str, "%d/%m/%Y").date()
                if shift_date >= date.today():
                    future_shifts.append((i, row, shift_date))
            except ValueError:
                continue

        if not future_shifts:
            st.info("כרגע לא פורסמו משמרות חדשות.")

        for original_index, row, shift_date in future_shifts:
            day_name = row['Day']
            time_range = row['Time']
            volunteer = str(row['Volunteer'])
            date_display = shift_date.strftime("%d/%m/%Y")
            header_text = f"📅 {day_name} {date_display} | ⏰ {time_range}"
            is_taken = len(volunteer) > 1
            
            if is_taken:
                expander_title = f"🔒 {header_text} (תפוס)"
            else:
                expander_title = f"🟢 {header_text} (פנוי)"

            with st.expander(expander_title, expanded=not is_taken):
                if is_taken:
                    st.write(f"**מאויש על ידי:** {volunteer}")
                else:
                    with st.form(key=f"form_{original_index}"):
                        name = st.text_input("שם מלא (חובה)")
                        phone = st.text_input("טלפון")
                        email = st.text_input("אימייל")
                        submit = st.form_submit_button("שריינו לי את המשמרת!")
                        if submit:
                            if name:
                                register_volunteer(original_index, name, phone, email)
                            else:
                                st.error("חובה למלא שם מלא.")

    except Exception as e:
        # כאן אנחנו מדפיסים את השגיאה האמיתית
        st.error("🚨 שגיאה טכנית בחיבור:")
        st.code(e) # זה יראה לנו בדיוק מה הבעיה
