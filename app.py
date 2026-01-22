import streamlit as st
import requests
import pandas as pd
import json
import re

# הגדרת דף נקייה
st.set_page_config(page_title="קבינט המוחות של אפי", layout="wide")

# --- CSS "ברזל" לניגודיות מקסימלית ומניעת דריסת אותיות ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');

    /* לבן מוחלט וטקסט שחור מוחלט */
    .stApp { background-color: #FFFFFF !important; }
    
    html, body, [class*="st-"] {
        font-family: 'Assistant', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
        color: #000000 !important;
        line-height: 2.0 !important; /* ריווח כפול למניעת הצטופפות */
    }

    /* הגדלת פונטים משמעותית */
    p, li, label, span { font-size: 1.3rem !important; }
    h1 { font-size: 2.8rem !important; border-bottom: 3px solid #000; padding-bottom: 10px; }
    h3 { font-size: 1.8rem !important; color: #1e3a8a !important; }

    /* תיקון שדות קלט - שחור על לבן בלבד */
    input, textarea, [data-baseweb="radio"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
    }

    /* כרטיסיות עבודה נקיות */
    .work-card {
        border: 2px solid #EEEEEE;
        padding: 40px;
        margin-bottom: 30px;
        border-radius: 0px; /* מראה של מסמך רשמי */
    }

    /* טבלה נקייה */
    table { width: 100%; border: 2px solid #000; margin-top: 20px; }
    th, td { border: 1px solid #000; padding: 15px; text-align: right; color: #000 !important; }
    th { background-color: #F0F0F0 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- פונקציות ליבה ---
def call_gemini(prompt):
    API_KEY = st.secrets["GEMINI_KEY"]
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    res = requests.post(url, json=payload)
    return res.json()['candidates'][0]['content']['parts'][0]['text'] if res.status_code == 200 else ""

def extract_json(text):
    try:
        match = re.search(r'\[.*\]', text, re.DOTALL)
        return json.loads(match.group()) if match else None
    except: return None

# --- ניהול קבינט ---
if 'participants_df' not in st.session_state:
    st.session_state['participants_df'] = pd.DataFrame({
        "שם": ["חנה ארנדט", "לודוויג ויטגנשטיין", "פיטר דרוקר", "אדוארד האלוול", "זיגמונד פרויד"],
        "תפקיד": ["פילוסופיה", "לוגיקה", "אסטרטגיה", "קוגניציה", "פסיכולוגיה"]
    })

st.title("🏛️ קבינט המוחות של אפי")

# תצוגת קבינט פשוטה
with st.expander("👤 חברי הקבינט הפעילים"):
    st.session_state['participants_df'] = st.data_editor(st.session_state['participants_df'], use_container_width=True)

# שלב 1
st.markdown('<div class="work-card">', unsafe_allow_html=True)
st.subheader("🖋️ מה האתגר שלך?")
idea = st.text_area("", height=100, placeholder="תאר את הבעיה כאן...")

if st.button("🔍 נתח סוגיה"):
    if idea:
        prompt = f"נושא: {idea}. נסח 4 שאלות אבחון פשוטות מאוד. החזר JSON בלבד: [{{'q': 'שאלה', 'options': ['תשובה 1', 'תשובה 2', 'תשובה 3']}}, ...]"
        raw = call_gemini(prompt)
        qs = extract_json(raw)
        if qs: st.session_state['structured_questions'] = qs
st.markdown('</div>', unsafe_allow_html=True)

# שלב 2
if 'structured_questions' in st.session_state:
    st.markdown('<div class="work-card">', unsafe_allow_html=True)
    st.subheader("📝 שאלון דיוק אסטרטגי")
    user_answers = []
    for i, item in enumerate(st.session_state['structured_questions']):
        st.markdown(f"**{item['q']}**")
        choice = st.radio(f"שאלה {i}", item['options'] + ["אחר"], key=f"r_{i}", label_visibility="collapsed")
        ans = choice
        if choice == "אחר": ans = st.text_input(f"פרט (שאלה {i+1}):", key=f"t_{i}")
        user_answers.append(f"ש: {item['q']} | ת: {ans}")

    if st.button("🚀 הפק ניתוח קבינט"):
        members = ", ".join(st.session_state['participants_df']["שם"].tolist())
        summary_prompt = f"""
        נושא: {idea}. תשובות: {user_answers}. קבינט: {members}.
        משימה:
        1. ציין 5 נקודות תובנה עיקריות. השתמש בשפה מקצועית מעמיקה אך ברורה ופשוטה.
        2. לאחר מכן, הצג טבלה: | בעיה | פתרון | דרך | תפוקות | תשומות |
        הכל בשחור על לבן, יישור לימין, ללא הצטופפות אותיות.
        """
        st.session_state['final_result'] = call_gemini(summary_prompt)
    st.markdown('</div>', unsafe_allow_html=True)

# שלב 3 - התוצאה הסופית
if 'final_result' in st.session_state:
    st.markdown('<div class="work-card">', unsafe_allow_html=True)
    st.subheader("📊 סיכום אסטרטגי - 5 תובנות")
    st.markdown(st.session_state['final_result'].replace('\n', '<br>'), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)