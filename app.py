import streamlit as st
import requests
import pandas as pd
import json
import re
import random

# הגדרת דף
st.set_page_config(page_title="קבינט המוחות של אפי", layout="wide")

# --- CSS: עיצוב צבעוני, גופנים וריווחים ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Heebo:wght@400;700&family=Assistant:wght@400;700&display=swap');

    .stApp { background-color: #f0f4f8 !important; }

    html, body, [class*="st-"] {
        font-family: 'Heebo', 'Assistant', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
        color: #000000 !important;
        line-height: 2.2 !important; 
    }

    textarea, input, [data-testid="stDataEditor"] {
        background-color: #e8f5e9 !important; 
        color: #000000 !important;
        border: 2px solid #2e7d32 !important;
        font-size: 1.3rem !important;
        border-radius: 10px;
    }

    div.stButton > button {
        background-color: #bbdefb !important; 
        color: #000000 !important;
        border: 2px solid #1976d2 !important;
        height: 3.5em !important;
        width: 100% !important;
        font-size: 1.4rem !important;
        font-weight: bold !important;
        border-radius: 12px !important;
    }

    div[data-baseweb="radio"] {
        background-color: #e3f2fd !important;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #90caf9;
        margin-bottom: 20px;
    }

    .result-box {
        border: 4px solid #1976d2;
        padding: 35px;
        background-color: #ffffff;
        margin-top: 30px;
        border-radius: 15px;
    }

    h1 { color: #0d47a1 !important; font-weight: 800 !important; }
    h3 { color: #1565c0 !important; border-bottom: 2px solid #1565c0; padding-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- ניהול מאגר דמויות ---
if 'pool_standard' not in st.session_state:
    st.session_state.pool_standard = [
        {"שם": "פיטר דרוקר", "תואר": "אבי הניהול", "התמחות": "אסטרטגיה וארגון"},
        {"שם": "חנה ארנדט", "תואר": "פילוסופית", "התמחות": "חברה ופוליטיקה"},
        {"שם": "זיגמונד פרויד", "תואר": "פסיכולוג", "התמחות": "תת מודע"},
        {"שם": "לודוויג ויטגנשטיין", "תואר": "פילוסוף", "התמחות": "לוגיקה"},
        {"שם": "ג'ק וולש", "תואר": "מנכ\"ל", "התמחות": "ניהול"},
        {"שם": "דניאל כהנמן", "תואר": "כלכלן", "התמחות": "קבלת החלטות"}
    ]
    st.session_state.pool_surprise = [
        {"שם": "סון דזו", "תואר": "אסטרטג", "התמחות": "אמנות המלחמה"},
        {"שם": "סטיב ג'ובס", "תואר": "יזם", "התמחות": "חדשנות"},
        {"שם": "מרקוס אורליוס", "תואר": "קיסר", "התמחות": "חוסן מנטלי"},
        {"שם": "לאונרדו דה וינצ'י", "תואר": "גאון", "התמחות": "יצירתיות"},
        {"שם": "קוקו שאנל", "תואר": "יזמית", "התמחות": "מיתוג"}
    ]

def refresh_cabinet():
    std = random.sample(st.session_state.pool_standard, 3)
    surp = random.sample(st.session_state.pool_surprise, 3)
    st.session_state.current_cabinet = std + surp

if 'current_cabinet' not in st.session_state:
    refresh_cabinet()

# --- פונקציות API ---
def call_gemini(prompt):
    try:
        API_KEY = st.secrets["GEMINI_KEY"]
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={API_KEY}"
        res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
        if res.status_code == 200:
            return res.json()['candidates'][0]['content']['parts'][0]['text']
        return "שגיאה בחיבור."
    except Exception as e:
        return f"תקלה: {str(e)}"

def extract_json(text):
    try:
        match = re.search(r'\[.*\]', text, re.DOTALL)
        return json.loads(match.group()) if match else None
    except:
        return None

# --- ממשק המשתמש ---
st.title("🏛️ קבינט המוחות של אפי")

st.subheader("👥 צוות הקבינט הנוכחי")
if st.button("🔄 רענן והחלף משתתפים"):
    refresh_cabinet()

for m in st.session_state.current_cabinet:
    st.markdown(f"👤 **{m['שם']}** | {m['תואר']} | {m['התמחות']}")

st.markdown("---")

st.subheader("🖋️ מה האתגר שלך?")
idea = st.text_area("תאר את המצב כאן:", height=100)

if st.button("🔍 צור שאלון אבחון"):
    if idea:
        names = [m['שם'] for m in st.session_state.current_cabinet]
        p = f"נושא: {idea}. קבינט: {names}. נסח 4 שאלות אבחון פשוטות ב-JSON: [{{'q': '...', 'options': [...]}}, ...]"
        with st.spinner("מגבש שאלות..."):
            res = call_gemini(p)
            st.session_state['qs'] = extract_json(res)

if 'qs' in st.session_state:
    st.subheader("📝 שאלון אבחון")
    ans_list = []
    for i, item in enumerate(st.session_state['qs']):
        st.markdown(f"**{i+1}. {item['q']}**")
        c = st.radio(f"שאלה {i}", item['options'], key=f"r_{i}")
        ans_list.append(f"ש: {item['q']} | ת: {c}")

    if st.button("🚀 הפק 5 תובנות אסטרטגיות"):
        names = [m['שם'] for m in st.session_state.current_cabinet]
        p = f"נושא: {idea}. תשובות: {ans_list}. קבינט: {names}. כתוב 5 תובנות וטבלה: בעיה, פתרון, דרך, תפוקות, תשומות."
        with st.spinner("מנתח..."):
            st.session_state['result'] = call_gemini(p)

if 'result' in st.session_state:
    st.markdown('<div class="result-box">', unsafe_allow_html=True)
    st.subheader("📊 סיכום הדיון")
    st.markdown(st.session_state['result'].replace('\n', '<br>'), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)