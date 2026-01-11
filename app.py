
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date, timedelta
import time
import base64
st.set_page_config(page_title="שיבוץ משמרות - ארכיון הגאווה", page_icon="logo.jpg", layout="centered")# --- 1. עיצוב לימין (RTL) ---
st.markdown("""
    <style>
    .stApp { direction: rtl; text-align: right; }
    .stMarkdown, .stButton, .stSelectbox, .stTextInput, .stDateInput, .stImage {
        direction: rtl; text-align: right;
    }
    h1, h2, h3, p { text-align: right; }
    input { text-align: right; }
    label { direction: rtl; text-align: right; width: 100%; }
    div[data-testid="stImage"] > img {
        display: block; margin-left: auto; margin-right: 0;
    }
    </style>
""", unsafe_allow_html=True)

# --- פונקציה מיוחדת להצגת וידאו כאפקט (Overlay) ---
def show_video_overlay(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        bin_str = base64.b64encode(data).decode()
        
        # קוד HTML שמציג את הוידאו על כל המסך
        video_html = f"""
            <style>
            .overlay-video {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                z-index: 999999;
                object-fit: cover;
                opacity: 0.9;
                pointer-events: none;
                mix-blend-mode: multiply;
            }}
            </style>
            <video class="overlay-video" autoplay muted playsinline>
                <source src="data:video/mp4;base64,{bin_str}" type="video/mp4">
            </video>
        """
        st.markdown(video_html, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"לא נמצא הקובץ {file_path}")

# --- 2. הגדרות קבועות ---
hebrew_days = {
    6: "ראשון", 0: "שני", 1: "שלישי", 2: "רביעי", 3: "חמישי"
}

shifts_hours = ["09:00-12:00", "12:00-15:00"]

# --- 3. לוגו וכותרת ---
try:
    st.image("logo.jpg", use_container_width=True)
except:
    st.warning("לא נמצא קובץ לוגו בשם logo.jpg")

st.markdown("<h2 style='text-align: right; direction: rtl;'>שיבוץ להתנדבות בארכיון הגאווה הישראלי</h2>", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 4. אזור ניהול (מוגן בסיסמה) ---
with st.expander("🔒 כניסה למנהלים (יצירת משמרות)"):
    # כאן הוספנו את בקשת הסיסמה
    admin_password = st.text_input("הזן סיסמת מנהל כדי לפתוח את האפשרויות:", type="password")
    
    # בדיקת הסיסמה (כרגע מוגדרת כ-archive2026)
    if admin_password == "archive2026":
        st.success("הגישה אושרה ✅")
        st.write("לחץ כאן רק בתחילת חודש כדי לייצר את המשמרות.")
        if st.button("צר משמרות אוטומטית לחודש הקרוב"):
            today = date.today()
            new_data = []
            for i in range(30):
                current_date = today + timedelta(days=i)
                if current_date.weekday() in [4, 5]: continue
                wd = current_date.weekday()
                if wd in hebrew_days:
                    day_name = hebrew_days[wd]
                    for h in shifts_hours:
                        new_data.append({
                            "Date": current_date.strftime("%d/%m/%Y"),
                            "Day": day_name, "Time": h,
                            "Volunteer": "", "Phone": "", "Email": ""
                        })
            if new_data:
                df_new = pd.DataFrame(new_data)
                conn.update(worksheet="Sheet1", data=df_new)
                st.success(f"נוצרו {len(df_new)} משמרות!")
                time.sleep(1)
                st.rerun()
    elif admin_password:
        st.error("סיסמה שגויה ❌")

st.divider()

# --- 5. אזור הרשמה ---
try:
    df = conn.read(worksheet="Sheet1", ttl=0).fillna("")
    
    if "Phone" not in df.columns: df["Phone"] = ""
    if "Email" not in df.columns: df["Email"] = ""
    
    available_shifts = df[df["Volunteer"] == ""].copy()

    st.subheader("הרשמה למשמרת 📝")
    st.write("בחרי תאריך בלוח השנה כדי לראות שעות פנויות:")

    selected_date_obj = st.date_input("בחר תאריך:", value=date.today(), format="DD/MM/YYYY")
    selected_date_str = selected_date_obj.strftime("%d/%m/%Y")
    daily_shifts = available_shifts[available_shifts["Date"] == selected_date_str]

    if not daily_shifts.empty:
        st.success(f"נמצאו משמרות פנויות ליום {daily_shifts.iloc[0]['Day']} ({selected_date_str})!")
        
        with st.form("signup_form"):
            selected_time = st.selectbox("בחרי שעה רצויה:", daily_shifts["Time"])
            volunteer_name = st.text_input("שם מלא:")
            volunteer_phone = st.text_input("מספר טלפון:")
            volunteer_email = st.text_input("כתובת אימייל:")
            
            submitted = st.form_submit_button("שבצי אותי למשמרת! ✅")

            if submitted:
                if volunteer_name and volunteer_phone:
                    mask = (df["Date"] == selected_date_str) & (df["Time"] == selected_time)
                    
                    if not df[mask].empty and df.loc[mask, "Volunteer"].iloc[0] == "":
                        row_index = df[mask].index[0]
                        df.at[row_index, "Volunteer"] = volunteer_name
                        df.at[row_index, "Phone"] = volunteer_phone
                        df.at[row_index, "Email"] = volunteer_email
                        conn.update(worksheet="Sheet1", data=df)
                        
                        st.success(f"תודה {volunteer_name}! נרשמת בהצלחה.")
                        
                        show_video_overlay("lines.mp4")
                        time.sleep(8)
                        
                        st.rerun()
                    else:
                        st.error("אופס! המשמרת הזו נתפסה.")
                else:
                    st.warning("חובה למלא שם וטלפון.")
    else:
        st.info(f'אין משמרות פנויות בתאריך {selected_date_str}.')

except Exception as e:

    st.error("שגיאה בטעינת הנתונים.")

