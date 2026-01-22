import streamlit as st
import requests
import pandas as pd
import json
import re
import random

# הגדרת דף בסיסית
st.set_page_config(page_title="קבינט המוחות של אפי", layout="wide")

# --- CSS מתקדם לפתרון בעיות עריכה וניראות ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');

    /* רקע דף תכלת בהיר יוקרתי */
    .stApp { background-color: #f0f7ff !important; }

    /* הגדרות טקסט וגופנים - מניעת דריסה */
    html, body, [class*="st-"] {
        font-family: 'Assistant', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
        color: #1a1a1a !important;
        line-height: 2.2 !important; /* ריווח שורות ענק למניעת עליה אחת על השנייה */
    }

    /* כותרות מרווחות */
    h1, h2, h3 { 
        padding-top: 20px !important; 
        padding-bottom: 10px !important;
        margin-bottom: 15px !important;
    }

    /* שדות כתיבה וטבלאות על רקע ירוק בהיר מאוד */
    textarea, input, [data-testid="stDataEditor"] {
        background-color: #f1fbf1 !important;
        border: 2px solid #a5d6a7 !important;
        border-radius: 10px !important;
        font-size: 1.2rem !important;
    }

    /* כפתורים על רקע כחול בהיר עם כיתוב שחור בולט */
    div.stButton > button {
        background-color: #bbdefb !important;
        color: #000000 !important;
        border: 2px solid #1e88e5 !important;
        height: 3.8em !important;
        width: 100% !important;
        font-size: 1.3rem !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
    }

    /* תיבת התוצאה הסופית */
    .result-box {
        border: 4px solid #1e88e5;
        padding: 40px;
        background-color: #ffffff;
        border-radius: 20px;
        margin-top: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- לוגיקת קבינט אקראי ---
if 'pool_standard' not in st.session_state:
    st.session_state.pool_standard = [
        {"שם": "פיטר דרוקר", "תואר": "אבי הניהול", "התמחות": "אסטרטגיה וארגון"},
        {"שם": "חנה ארנדט", "תואר": "פילוסופית", "התמחות": "חברה ופוליטיקה"},
        {"שם": "זיגמונד פרויד", "תואר": "פסיכולוג", "התמחות": "תת מודע ודחפים"},
        {"שם": "לודוויג ויטגנשטיין", "תואר": "פילוסוף", "התמחות": "לוגיקה ושפה"},
        {"שם": "ג'ק וולש", "תואר": "מנכ\"ל", "התמחות": "מנהיגות ביצועית"}
    ]
    st.session_state.pool_surprise = [
        {"שם": "סון דזו", "תואר": "אסטרטג", "התמחות": "אמנות המלחמה"},
        {"שם": "קוקו שאנל", "תואר": "יזמית", "התמחות": "מיתוג ושבירת מוסכמות"},
        {"שם": "מרקוס אורליוס", "תואר": "קיסר", "התמחות": "חוסן מנטלי וסטואיציזם"}
    ]

def refresh_cabinet():
    std = random.sample(st.session_state.pool_standard, 3)
    surp = random.sample(st.session_state.pool_surprise, 3)
    st.session_state.current_cabinet = std + surp

if 'current_cabinet' not in st.session_state:
    refresh_cabinet()

# --- פונקציות API (כולל טיפול בשגיאות) ---
def call_gemini(prompt):
    try:
        API_KEY = st.secrets["GEMINI_KEY"]
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={API_KEY}"
        res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
        if res.status_code == 200:
            return res.json()['candidates'][0]['content']['parts'][0]['text']
        return "שגיאה זמנית בתקשורת. אנא נסה שוב."
    except:
        return "המערכת עמוסה כרגע. נסה שוב בעוד רגע."

def extract_json(text):
    try:
        match = re.search(r'\[.*\]', text, re.DOTALL)
        return json.loads(match.group()) if match else None
    except: return None

# --- הממשק הויזואלי ---
st.title("🏛️ קבינט המוחות של אפי")

st.subheader("👥 צוות הקבינט שלך לה