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
    
    /* עיצוב ספציפי לתיבת התאריך כדי שתהיה מימין לשמאל */
    .stDateInput input {
        text-align: right !important;
        direction: rtl !important;
    }
    
    /* הזזת האייקון של לוח השנה לצד שמאל (כדי שלא יסתיר את הטקסט בעברית) */
    div[data-baseweb="input"] > div {
        flex-direction: row-reverse;
    }

    /* עיצוב הכפתורים והמסגרות */
    .stButton button { width: 100%; border-radius: 8px; }
    div[data-testid="stExpander"] { border: 1px solid #ddd; border-radius: 10px; }
    
    /* הסתרת תפריטים מיותרים */
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
    st.write("בחרו תאריך בלוח השנה כדי לראות את המשמרות:")
    
    # --- רכיב לוח השנה ---
    # הוספתי help כדי שיהיה ברור
    selected_date = st.date_input(
        "📅 לחצו כאן לבחירת תאריך",
        value=date.today()
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

        # --- תצוגת התוצאות ---
        if not daily_shifts:
            st.info(f"לא נמצאו משמרות בתאריך {selected_date.strftime('%d/%m/%Y')}. נסו תאריך אחר!")
        else:
            st.success(f"נמצאו {len(daily_shifts)} משמרות לתאריך הזה:")
            
            for original_index, row in daily_shifts:
                time_range = row['Time']
                volunteer = str(row['Volunteer'])
                
                is_taken = len(volunteer) > 1
                
                if is_taken:
                    header = f"🔒 בשעה {time_range} (תפוס)"
                else:
                    header = f"🟢 בשעה {time_range} (פנוי להרשמה)"
                
                with st.expander(header, expanded=not is_taken):
                    if is_taken:
                        st.write(f"**מתנדב/ת:** {volunteer}")
                        st.caption("המשמרת הזו כבר מלאה.")
                    else:
                        st.markdown(f"### הרשמה לשעה {time_range} 👇")
                        with st.form(key=f"form_{original_index}"):
                            name = st.text_input("שם מלא", placeholder="חובה למלא")
                            phone = st.text_input("טלפון")
                            email = st.text_input("מייל")
                            
                            if st.form_submit_button("שריינו לי את המשמרת!"):
                                if name:
                                    register_volunteer(original_index, name, phone, email)
                                else:
                                    st.error("נא למלא שם מלא")

    except Exception as e:
        st.error("שגיאה בחיבור לנתונים. ודאו שה-Secrets מוגדרים נכון.")

if __name__ == "__main__":
    main()
