import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, date

# --- 1. הגדרות דף ---
st.set_page_config(page_title="שיבוץ משמרות - ארכיון הגאווה", page_icon="🏳️‍🌈", layout="wide")

# עיצוב לימין (RTL) וכרטיסיות יפות
st.markdown("""
<style>
    .stApp { direction: rtl; text-align: right; }
    h1, h2, h3, p, div, label, input, span { text-align: right !important; }
    .stButton button { width: 100%; border-radius: 8px; font-weight: bold; }
    
    /* עיצוב הכרטיסייה */
    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #f9f9f9;
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    
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
    
    # הקישור הישיר שלך
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
    # כותרת
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.title("🏳️‍🌈 לוח משמרות")
        st.write("בחרו כרטיסייה והירשמו למשמרת:")
    st.write("---")

    try:
        sh = get_worksheet()
        data = sh.get_all_records()

        # סינון ומיון משמרות עתידיות
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
        
        # מיון לפי תאריך (שהכי קרוב יופיע ראשון)
        future_shifts.sort(key=lambda x: x[2])

        if not future_shifts:
            st.info("אין כרגע משמרות פנויות. חזרו בקרוב! ❤️")
        
        # --- תצוגת הגריד (לוח שנה) ---
        # אנחנו יוצרים שורות של 3 כרטיסים בכל שורה
        cols_per_row = 3
        cols = st.columns(cols_per_row)
        
        for idx, (original_index, row, shift_date) in enumerate(future_shifts):
            # בחירת העמודה הנכונה (0, 1 או 2)
            current_col = cols[idx % cols_per_row]
            
            with current_col:
                # מסגרת לכל משמרת
                with st.container(border=True):
                    day_name = row['Day']
                    time_range = row['Time']
                    volunteer = str(row['Volunteer'])
                    date_display = shift_date.strftime("%d/%m/%Y")
                    
                    # כותרת הכרטיס
                    st.markdown(f"### 📅 {day_name}")
                    st.markdown(f"**{date_display}**")
                    st.markdown(f"⏰ {time_range}")
                    
                    is_taken = len(volunteer) > 1
                    
                    st.write("---")
                    
                    if is_taken:
                        st.warning(f"🔒 **תפוס ע\"י:**\n{volunteer}")
                    else:
                        st.markdown("🟢 **פנוי להרשמה**")
                        # טופס הרשמה קטן בתוך הכרטיס
                        with st.form(key=f"card_form_{original_index}"):
                            name = st.text_input("שם מלא", placeholder="חובה למלא")
                            phone = st.text_input("טלפון")
                            email = st.text_input("מייל")
                            
                            if st.form_submit_button("אני בא/ה! ✋"):
                                if name:
                                    register_volunteer(original_index, name, phone, email)
                                else:
                                    st.error("חסר שם")

    except Exception as e:
        st.error("שגיאת התחברות לטבלה. בדקו את ה-Secrets.")
        # st.code(e)

if __name__ == "__main__":
    main()
