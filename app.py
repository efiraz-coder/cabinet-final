import streamlit as st
import google.generativeai as genai
import json
import re
import random

# הגדרות דף
st.set_page_config(page_title="קבינט המוחות של אפי", layout="wide", initial_sidebar_state="collapsed")

# חיבור למפתח ה-API דרך הספרייה הרשמית
if "GEMINI_KEY" not in st.secrets:
    st.error("המפתח GEMINI_KEY חסר ב-Secrets!")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_KEY"])

# פונקציה רשמית לקריאה למודל
def call_gemini(prompt):
    try:
        # שימוש במודל 1.5 פלאש דרך הספרייה הרשמית
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"שגיאה בקריאת המודל: {str(e)}")
        return None

# --- ממשק האפליקציה ---
st.title("🏛️ קבינט המוחות של אפי")

if 'cabinet' not in st.session_state:
    st.session_state.cabinet = [
        {"שם": "פיטר דרוקר", "מומחיות": "ניהול ואסטרטגיה"},
        {"שם": "סטיב ג'ובס", "מומחיות": "חדשנות וחווית משתמש"},
        {"שם": "דניאל כהנמן", "מומחיות": "קבלת החלטות"}
    ]

idea = st.text_area("🖋️ מה האתגר שלך?", height=100)

if st.button("🔍 הפעל את הקבינט"):
    if idea:
        with st.spinner("מתחבר לשרתי גוגל..."):
            # בדיקה פשוטה
            res = call_gemini(f"ענה בחיוב אם אתה שומע אותי. הנושא הוא: {idea}")
            if res:
                st.success("✅ הקבינט מחובר ופועל!")
                st.write(res)

if st.sidebar.button("נקה זיכרון"):
    st.session_state.clear()
    st.rerun()