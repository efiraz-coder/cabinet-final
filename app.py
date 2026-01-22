import streamlit as st
import requests
import pandas as pd
import json
import re

st.set_page_config(page_title="קבינט המוחות של אפי", layout="wide")

# --- CSS מתוקן: מניעת דריסת אותיות והגדלת פונטים ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');

    html, body, [class*="st-"] {
        font-family: 'Assistant', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
        color: #1a1a1a !important;
        line-height: 1.6 !important; /* מונע דריסת אותיות */
    }

    /* הגדלת אותיות כללית */
    p, span, label, input, button { font-size: 1.2rem !important; }
    h1 { font-size: 2.5rem !important; color: #1e3a8a !important; padding-bottom: 20px; }
    h3 { font-size: 1.8rem !important; margin-top: 25px !important; }

    .stApp { background-color: #ffffff !important; }

    /* תיקון טבלת משתתפים - בהירות מקסימלית */
    [data-testid="stDataEditor"] { 
        background-color: #ffffff !important; 
        border: 1px solid #e2e8f0;
        font-size: 1.1rem !important;
    }

    /* כרטיסיות עם ריווח */
    .step-card {
        background-color: #f8fafc !important;
        padding: 30px;
        border-radius: 15px;
        border: 1px solid #e2e8f0;
        margin-bottom: 30px;
    }

    /* תיבת סיכום */
    .story-box {
        background-color: #ffffff !important;
        border-right: 12px solid #1e3a8a;
        padding: 35px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        font-size: 1.3rem !important;
        line-height: 2 !important;
    }

    /* תיקון לאייקונים וכותרות שעולים אחד על השני */
    .stExpander { margin-top: 15px !important; border: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- פונקציות ---
def extract_json(text):
    try:
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match: return json.loads(match.group())
        return json.loads(text)
    except: return None

def call_gemini(prompt):
    API_KEY = st.secrets["GEMINI_KEY"]
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    res = requests.post(url, json=payload)
    return res.json()['candidates'][0]['content']['parts'][0]['text'] if res.status_code == 200 else ""

# --- תוכן ---
st.title("🏛️ קבינט המוחות של אפי")

if 'participants_df' not in st.session_state:
    st.session_state['participants_df'] = pd.DataFrame({
        "שם": ["חנה ארנדט", "לודוויג ויטגנשטיין", "פיטר דרוקר", "אדוארד האלוול", "זיגמונד פרויד", "זאן פיאזה", "אלברט בנדורה", "גק וולש", "ריד הופמן"],
        "מומחיות": ["פילוסופיה וחברה", "לוגיקה ושפה", "ניהול ואסטרטגיה", "הפרעות קשב וריכוז", "פסיכולוגיה", "למידה וילדים", "התנהגות חברתית", "מנהיגות עסקית", "קשרים ויזמות"]
    })

with st.expander("👤 מי יושב היום בקבינט? (לחץ לעריכה)"):
    st.session_state['participants_df'] = st.data_editor(st.session_state['participants_df'], use_container_width=True)

st.markdown('<div class="step-card">', unsafe_allow_html=True)
st.subheader("🖋️ מה הנושא שעל הפרק?")
idea = st.text_area("", height=100, placeholder="למשל: אני מרגיש תקוע בשיווק של העסק החדש שלי...")

if st.button("❓ התחל להתייעץ"):
    if idea:
        prompt = f"""
        נושא: {idea}. 
        משימה: נסח 4 שאלות אבחון פשוטות. 
        חשוב מאוד: אל תשתמש במושגים מקצועיים מפסיכולוגיה או פילוסופיה. 
        דבר בשפה יומיומית שכל אדם מבין.
        החזר JSON: [{{'q': 'שאלה פשוטה', 'options': ['תשובה א', 'תשובה ב', 'תשובה ג']}}, ...]
        """
        with st.spinner("הקבינט חושב על שאלות פשוטות..."):
            raw = call_gemini(prompt)
            qs = extract_json(raw)
            if qs: st.session_state['structured_questions'] = qs
st.markdown('</div>', unsafe_allow_html=True)

if 'structured_questions' in st.session_state:
    st.markdown('<div class="step-card">', unsafe_allow_html=True)
    st.subheader("📝 בוא נדייק את התמונה")
    user_answers = []
    for i, item in enumerate(st.session_state['structured_questions']):
        st.markdown(f"**{item['q']}**")
        choice = st.radio(f"שאלה {i}", item['options'] + ["אחר (כתוב בעצמך)"], key=f"r_{i}", label_visibility="collapsed")
        ans = choice
        if choice == "אחר (כתוב בעצמך)":
            ans = st.text_input(f"פרט כאן:", key=f"t_{i}")
        user_answers.append(f"שאלה: {item['q']} | תשובה: {ans}")

    if st.button("🎭 הצג סיכום והנחיות"):
        summary_prompt = f"""
        נושא: {idea}. תשובות: {user_answers}. 
        כתוב סיפור מעניין ומחכים המבוסס על חברי הקבינט. 
        בסוף הצג טבלה: | בעיה | פתרון | דרך | תפוקות | תשומות |
        השתמש בשפה פשוטה, חמה ומעודדת.
        """
        with st.spinner("הקבינט מכין לך מפת דרכים..."):
            st.session_state['final_result'] = call_gemini(summary_prompt)
    st.markdown('</div>', unsafe_allow_html=True)

if 'final_result' in st.session_state:
    st.markdown('<div class="story-box">', unsafe_allow_html=True)
    st.markdown(st.session_state['final_result'].replace('\n', '<br>'), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)