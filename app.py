import streamlit as st
import requests
import pandas as pd
import json
import re
import random

# הגדרת דף
st.set_page_config(page_title="קבינט המוחות של אפי", layout="wide")

# --- CSS עם גופנים מ-Google Fonts וצבעים מותאמים ---
st.markdown("""
    <style>
    /* משיכת גופנים מ-Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Heebo:wght@400;700&family=Assistant:wght@400;700&display=swap');

    html, body, [class*="st-"] {
        font-family: 'Heebo', 'Assistant', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
        color: #000000 !important;
        line-height: 2.0 !important;
    }

    /* עיצוב שדות כתיבה וטבלאות על רקע ירוק בהיר */
    textarea, input, [data-testid="stDataEditor"] {
        background-color: #e8f5e9 !important; /* ירוק בהיר */
        color: #000000 !important;
        border: 2px solid #2e7d32 !important;
        font-size: 1.3rem !important;
    }

    /* עיצוב כפתורים על רקע כחול בהיר עם כיתוב שחור */
    div.stButton > button {
        background-color: #e3f2fd !important; /* כחול בהיר */
        color: #000000 !important; /* כיתוב שחור */
        border: 2px solid #1976d2 !important;
        height: 3.5em !important;
        width: 100% !important;
        font-size: 1.4rem !important;
        font-weight: bold !important;
        border-radius: 10px !important;
    }

    /* עיצוב הרדיו (שאלון) על רקע כחול בהיר */
    div[data-baseweb="radio"] {
        background-color: #e3f2fd !important;
        padding: 15px;
        border-radius: 10px;
    }

    /* תיבת תוצאה סופית */
    .result-box {
        border: 3px solid #1976d2;
        padding: 30px;
        background-color: #ffffff;
        margin-top: 30px;
        font-size: 1.4rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ניהול דמויות (מאגר נתונים) ---
if 'pool_standard' not in st.session_state:
    st.session_state.pool_standard = [
        {"שם": "פיטר דרוקר", "תואר": "אבי הניהול המודרני", "התמחות": "אסטרטגיה וארגון"},
        {"שם": "חנה ארנדט", "תואר": "פילוסופית", "התמחות": "פוליטיקה וחברה"},
        {"שם": "זיגמונד פרויד", "תואר": "אבי הפסיכואנליזה", "התמחות": "תת מודע ודחפים"},
        {"שם": "לודוויג ויטגנשטיין", "תואר": "פילוסוף", "התמחות": "לוגיקה ושפה"},
        {"שם": "ג'ק וולש", "תואר": "מנכ\"ל GE האגדי", "התמחות": "ניהול ביצועים"},
        {"שם": "מרשל מקלוהן", "תואר": "חוקר תקשורת", "התמחות": "טכנולוגיה ומדיה"},
        {"שם": "אלברט בנדורה", "תואר": "פסיכולוג", "התמחות": "למידה חברתית"},
        {"שם": "אדוארד האלוול", "תואר": "ד\"ר לרפואה", "התמחות": "קשב וריכוז קוגניטיבי"}
    ]
    st.session_state.pool_surprise = [
        {"שם": "לאונרדו דה וינצ'י", "תואר": "איש אשכולות", "התמחות": "יצירתיות רב-תחומית"},
        {"שם": "סון דזו", "תואר": "אסטרטג צבאי", "התמחות": "אמנות המלחמה"},
        {"שם": "סטיב ג'ובס", "תואר": "יזם טכנולוגי", "התמחות": "חוויית משתמש וחדשנות"},
        {"שם": "מרקוס אורליוס", "תואר": "קיסר רומי", "התמחות": "סטואיציזם וחוסן"},
        {"שם": "מארי קירי", "תואר": "פיזיקאית", "התמחות": "חקר הלא נודע ופריצות דרך"},
        {"שם": "קוקו שאנל", "תואר": "מעצבת אופנה", "התמחות": "שבירת מוסכמות ומיתוג"}
    ]

# פונקציית הגרלת קבינט
def refresh_cabinet():
    std = random.sample(st.session_state.pool_standard, 3)
    surp = random.sample(st.session_state.pool_surprise, 3)
    st.session_state.current_cabinet = std + surp

if 'current_cabinet' not in st.session_state:
    refresh_cabinet()

# --- ממשק משתמש ---
st.title("🏛️ קבינט המוחות הדינמי של אפי")

st.subheader("👥 חברי הקבינט הנוכחיים")
# כפתור רענון אקראי
if st.button("🔄 רענן והחלף חברי קבינט"):
    refresh_cabinet()

# הצגת חברי הקבינט שורה אחר שורה
for member in st.session_state.current_cabinet:
    st.markdown(f"**{member['שם']}** | {member['תואר']} | {member['התמחות']}")

st.markdown("---")

# שלב 1
st.subheader("🖋️ מה הנושא שעל הפרק?")
idea = st.text_area("תאר את הסוגיה כאן:", height=100)

# פונקציות API (כמו קודם)
def call_gemini(prompt):
    try:
        API_KEY = st.secrets["GEMINI_KEY"]
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={API_KEY}"
        res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
        return res.json()['candidates'][0]['content']['parts'][0]['text']
    except: return "שגיאה בחיבור."

def extract_json(text):
    try:
        match = re.search(r'\[.*\]', text, re.DOTALL)
        return json.loads(match.group()) if match else None
    except: return None

if st.button("🔍 צור שאלון אבחון"):
    if idea:
        names = [m['שם'] for m in st.session_state.current_cabinet]
        prompt = f"נושא: {idea}. קבינט: {names}. נסח 4 שאלות אבחון פשוטות בJSON: [{{'q': '...', 'options': [...]}}, ...]"
        raw = call_gemini(prompt)
        st.session_state['qs'] = extract_json(raw)

if 'qs' in st.session_state:
    st.subheader("📝 שאלון אבחון")
    ans_list = []
    for i, item in enumerate(st.session_state['qs']):
        st.markdown(f"**{item['q']}**")
        choice = st.radio(f"שאלה {i}", item['options'], key=f"r_{i}")
        ans_list.append(f"ש: {item['q']} | ת: {choice}")

    if st.button("🚀 הפק 5 תובנות אסטרטגיות"):
        names = [m['שם'] for m in st.session_state.current_cabinet]
        prompt = f"נושא: {idea}. תשובות: {ans_list}. קבינט: {names}. ציין 5 תובנות עמוקות וטבלה: בעיה, פתרון, דרך, תפוקות, תשומות."
        st.session_state['result'] = call_gemini(prompt)

if 'result' in st.session_state:
    st.markdown('<div class="result-box">', unsafe_allow_html=True)
    st.markdown(st.session_state['result'].replace('\n', '<br>'), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)