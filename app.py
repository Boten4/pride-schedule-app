import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, date

# --- 1. הגדרות דף ---
# שיניתי את האייקון בדפדפן לדגל החדש אם תרצי, או שתשאירי רגיל
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
    /* הקטנת המרווח בין הכותרת לתמונה */
    .block-container { padding-top: 1rem; }
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
    return client.open_by_url("https://docs.google.com/spreadsheets/d/1UQQ5oqpMMiQPnJF0q2i-pUnl4jJxhpzJc2g-P2mxFCQ/edit?gid=0#gid=0").sheet1

# --- 3. פונקציה לרישום ---
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
    # --- חלק עליון: לוגו ארכיון לרוחב מלא ---
    try:
        # שם הקובץ כפי שהוא אצלך בגיטהאב
        st.image("archive_logo.png.jpg", use_container_width=True) 
    except:
        st.warning("לא נמצא לוגו ארכיון (archive_logo.png.jpg)")

    st.write("") # מרווח קטן

    # --- חלק תחתון: כותרת + דגל פרוגרסיבי קטן ---
    # יצרתי שתי עמודות: אחת לכותרת (רחבה) ואחת לדגל (צרה)
    col_title, col_flag = st.columns([5, 1])
    
    with col_title:
        st.title("לוח משמרות") # בלי אייקון
        
    with col_flag:
        try:
            # דגל פרוגרסיבי בקטן (רוחב 60 פיקסלים)
            st.image("progress-pride-flag.png", width=60) 
        except:
            pass

    st.write("בחרו תאריך כדי לראות את המשמרות:")
    
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
        
        for i, row in enumerate(data):
            date_str = str(row['Date'])
            if not date_str: continue
            try:
                shift_date = datetime.strptime(date_str, "%d/%m/%Y").date()
                if shift_date == selected_date:
                    daily_shifts.append((i, row))
            except ValueError:
                continue

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
        st.error("שגיאה בחיבור.")

if __name__ == "__main__":
    main()
