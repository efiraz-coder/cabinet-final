import streamlit as st
import requests
import pandas as pd
import json
import re
import random

# הגדרת דף רחב
st.set_page_config(page_title="קבינט המוחות של אפי", layout="wide")

# --- CSS: פתרון דריסת אותיות וצבעוניות ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Heebo:wght@400;700&display=swap');

    .stApp { background-color: #f0f4f8 !important; }

    /* מניעת דריסת טקסט באמצעות ריווח שורות ופדינג */
    html, body, [class*="st-"] {
        font-family: 'Heebo', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
        color: #000000 !important;
        line-height: 2.5 !important; 
    }

    /* עיצוב שדות כתיבה (ירוק) */
    textarea, input {
        background-color: #e8f5e9 !important;
        border: 2px solid #2e7d32 !important;
        border-radius: 10px !important;
        padding: 10px !important;
    }

    /* עיצוב כפתורים (כחול) */
    div.stButton > button {
        background-color: #bbdefb !important;
        color: #000000 !important;
        border: 2px solid #1976d2 !important;
        font-weight: bold !important;
        height: 3.5em !important;
        width: 100% !important;
        margin-top: 15px !important;
    }

    /* עיצוב שאלון (תכלת) */
    div[data-baseweb="radio"] {
        background-color: #e3f2fd !important;
        padding: 25px !important;
        border-radius: 15px !important;
        border: 1px solid #90caf9 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ניהול דמויות ---
if 'pool_standard' not in st.session_state:
    st.session_state.pool_standard = [
        {"שם": "פיטר דרוקר", "תואר": "אבי הניהול", "התמחות": "אסטרטגיה"},
        {"שם": "חנה ארנדט", "תואר": "פילוסופית", "התמחות": "חברה"},
        {"שם": "זיגמונד פרויד", "תואר": "פסיכולוג", "התמחות": "תת מודע"},
        {"שם": "דניאל כהנמן", "תואר": "כלכלן", "התמחות": "קבלת החלטות"}
    ]
    st.session_state.pool_surprise = [
        {"שם": "סון דזו", "תואר": "אסטרטג סיני", "התמחות": "אמנות המלחמה"},
        {"שם": "סטיב ג'ובס", "תואר": "יזם", "התמחות": "חדשנות"},
        {"שם": "קוקו שאנל", "תואר": "יזמית", "התמחות": "מיתוג"}
    ]

def refresh_cabinet():
    std = random.sample(st.session_state.pool_standard, 3)
    surp = random.sample(st.session_state.pool_surprise, 3)
    st.session_state.current_cabinet = std + surp

if 'current_cabinet' not in st.session_state:
    refresh_cabinet()

# --- פונקציות API חסינות ---
def call_gemini(prompt):
    try:
        API_KEY = st.secrets["GEMINI_KEY"]
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={API_KEY}"
        res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
        if res.status_code == 200:
            return res.json()['candidates'][0]['content']['parts'][0]['text']
        return "ERROR"
    except:
        return "ERROR"

def extract_json(text):
    try:
        match = re.search(r'\[.*\]', text, re.DOTALL)
        return json.loads(match.group()) if match else None
    except:
        return None

# --- ממשק ---
st.title("🏛️ קבינט המוחות של אפי")

st.subheader("👥 המשתתפים שנבחרו עבורך:")
if st.button("🔄 רענן והחלף משתתפים"):
    refresh_cabinet()

for m in st.session_state.current_cabinet:
    st.markdown(f"👤 **{m['שם']}** | {m['תואר']} | {m['התמחות']}")

st.markdown("---")

st.subheader("🖋️ מה האתגר שלך?")
idea = st.text_area("תאר את המצב כאן:", height=100)

if st.button("🔍 צור שאלון אבחון"):
    if idea:
        with st.spinner("הקבינט מגבש שאלות..."):
            names = [m['שם'] for m in st.session_state.current_cabinet]
            prompt = f"נושא: {idea}. קבינט: {names}. נסח 4 שאלות פשוטות ב-JSON בלבד: [{{'q': '...', 'options': [...]}}, ...]"
            res = call_gemini(prompt)
            data = extract_json(res)
            if data:
                st.session_state['qs'] = data
            else:
                st.error("הקבינט עמוס, נסה ללחוץ שוב.")

# בדיקה בטיחותית: מציג שאלון רק אם ה-JSON חזר תקין (מונע את שגיאת ה-Traceback)
if 'qs' in st.session_state and st.session_state['qs']:
    st.subheader("📝 שאלון אבחון")
    ans_list = []
    for i, item in enumerate(st.session_state['qs']):
        st.markdown(f"**{i+1}. {item['q']}**")
        c = st.radio(f"בחירה {i}", item['options'], key=f"r_{i}")
        ans_list.append(f"ש: {item['q']} | ת: {c}")

    if st.button("🚀 הפק תובנות אסטרטגיות"):
        with st.spinner("מנתח..."):
            prompt = f"נושא: {idea}. תשובות: {ans_list}. כתוב 5 תובנות וטבלה מסכמת."
            result = call_gemini(prompt)
            if result != "ERROR":
                st.session_state['result'] = result
            else:
                st.error("שגיאת תקשורת. נסה שוב.")

if 'result' in st.session_state:
    st.markdown("---")
    st.subheader("📊 סיכום הדיון")
    st.write(st.session_state['result'])