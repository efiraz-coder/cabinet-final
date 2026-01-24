import streamlit as st
import google.generativeai as genai
import json
import re
import random

# הגדרות דף - עיצוב נקי וסידור מימין לשמאל
st.set_page_config(page_title="קבינט המוחות של אפי", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Assistant', sans-serif; direction: rtl; text-align: right; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; font-weight: bold; background-color: #f0f2f6; border: 1px solid #d1d5db; color: #1f2937; }
    .expert-box { background-color: #ffffff; padding: 12px; border: 1px solid #e5e7eb; border-radius: 10px; text-align: center; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); color: #1f2937; }
    .question-card { background-color: #f9fafb; padding: 20px; border-radius: 12px; margin-top: 20px; border-right: 5px solid #3b82f6; color: #1f2937; }
    .stRadio > label { font-size: 1.1em; font-weight: 600; color: #374151; }
    </style>
    """, unsafe_allow_html=True)

# בדיקת מפתח API ב-Secrets
if "GEMINI_KEY" not in st.secrets:
    st.error("שגיאה: המפתח GEMINI_KEY לא מוגדר ב-Secrets של Streamlit.")
    st.stop()

# אתחול המודל
genai.configure(api_key=st.secrets["GEMINI_KEY"])
MODEL_NAME = "gemini-1.5-flash"

# מאגר המומחים לפי קטגוריות (2 מכל סוג כפי שביקשת)
POOL = {
    "פילוסופיה": ["סוקרטס", "אריסטו", "חנה ארנדט", "פרידריך ניטשה", "מרקוס אורליוס", "סימון דה בובואר", "עמנואל קאנט", "ז'אן-פול סארטר"],
    "פסיכולוגיה": ["זיגמונד פרויד", "קארל יונג", "ויקטור פראנקל", "מלאני קליין", "דניאל כהנמן", "אברהם מאסלו", "קארל רוג'רס", "אריך פרום"],
    "תרבות": ["מרשל מקלוהן", "אדוארד סעיד", "רולאן בארת", "ניל פוסטמן", "יובל נח הררי", "מרגרט מיד", "מישל פוקו", "קלוד לוי-שטראוס"],
    "הפתעה": ["לאונרדו דה וינצ'י", "סטיב ג'ובס", "סון דזו", "אלברט איינשטיין", "מארי קירי", "שייקספיר", "קוקו שאנל", "צ'רלי צ'פלין"]
}

def generate_full_cabinet():
    cabinet = []
    for cat in ["פילוסופיה", "פסיכולוגיה", "תרבות", "הפתעה"]:
        names = random.sample(POOL[cat], 2)
        for name in names:
            cabinet.append({"name": name, "cat": cat})
    return cabinet

# ניהול המצב ב-Session
if 'cabinet' not in st.session_state:
    st.session_state.cabinet = generate_full_cabinet()

# --- ממשק משתמש ---
st.title("🏛️ קבינט המוחות של אפי")
st.write("חברי הקבינט שנבחרו עבורך למשימה זו (8 מומחים):")

# הצגת הקבינט בטבלה/עמודות
cols = st.columns(4)
for i, member in enumerate(st.session_state.cabinet):
    with cols[i % 4]:
        st.markdown(f"<div class='expert-box'><b>{member['name']}</b><br><small>{member['cat']}</small></div>", unsafe_allow_html=True)

# כפתור רענון - מחליף 4 חברים אקראיים (אחד מכל קטגוריה)
if st.button("🔄 רענן את הרכב הקבינט"):
    current = st.session_state.cabinet
    new_cabinet = []
    for cat in ["פילוסופיה", "פסיכולוגיה", "תרבות", "הפתעה"]:
        # בוחרים 2 חדשים לגמרי לכל קטגוריה כדי להבטיח שינוי
        names = random.sample(POOL[cat], 2)
        for name in names:
            new_cabinet.append({"name": name, "cat": cat})
    st.session_state.cabinet = new_cabinet
    # איפוס תוצאות קודמות ברענון
    for key in ['questions', 'final_report']:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

st.write("---")
idea = st.text_area("🖋️ תאר את המחשבה, הרגשה או דילמה שמעסיקה אותך:", height=120, placeholder="מה יושב לך על הלב היום?")

if st.button("🔍 התחל תהליך אבחון עמוק"):
    if not idea:
        st.warning("אנא כתוב משהו כדי שהקבינט יוכל להתייחס.")
    else:
        with st.spinner("ח