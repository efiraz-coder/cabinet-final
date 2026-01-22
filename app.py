import streamlit as st
import requests
import pandas as pd
import json
import re

# הגדרת דף נקייה ופשוטה
st.set_page_config(page_title="קבינט המוחות של אפי", layout="wide")

# CSS "ברזל" לפתרון כל בעיות העריכה
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
        line-height: 2.2 !important; /* ריווח ענק למניעת דריסת אותיות */
    }

    /* הגדלת פונטים דרמטית */
    p, li, label, span, input { font-size: 1.4rem !important; font-weight: 500 !important; }
    h1 { font-size: 3rem !important; color: #000000 !important; margin-bottom: 40px !important; }
    h3 { font-size: 2rem !important; color: #1e3a8a !important; margin-top: 30px !important; }

    /* תיקון כותרות שמתערבבות */
    .stExpander, .stMarkdown { margin-bottom: 25px !important; padding: 10px 0 !important; }

    /* עיצוב שדות קלט - נקי וברור */
    textarea, [data-baseweb="radio"] {
        background-color: #F9FAFB !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
        padding: 15px !important;
    }

    /* טבלה פשוטה שחור-לבן */
    table { width: 100%; border: 2px solid #000; margin-top: 20px; background-color: white; }
    th, td { border: 1px solid #000; padding: 15px; text-align: right; color: #000 !important; }
    th { background-color: #F0F0F0 !important; font-weight: bold; }

    /* כפתור בולט מאוד */
    div.stButton > button {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        height: 4em;
        width: 100%;
        font-size: 1.3rem !important;
        font-weight: bold;
        border-radius: 0px;
    }
    </style>
    """, unsafe_allow_html=True)

# פונקציות חיבור
def call_gemini(prompt):
    try:
        API_KEY = st.secrets["GEMINI_KEY"]
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={API_KEY}"
        res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
        return res.json()['candidates'][0]['content']['parts'][0]['text']
    except: return "שגיאה בחיבור לקבינט."

def extract_json(text):
    try:
        match = re.search(r'\[.*\]', text, re.DOTALL)
        return json.loads(match.group()) if match else None
    except: return None

# --- ממשק ---
st.title("🏛️ קבינט המוחות של אפי")

# שלב 1: נושא
st.subheader("🖋️ מה האתגר שלך היום?")
idea = st.text_area("תאר את המצב במילים פשוטות:", height=120)

if st.button("🔍 נתח ובנה שאלון אבחון"):
    if idea:
        prompt = f"נושא: {idea}. נסח 4 שאלות אבחון בשפה פשוטה ויומיומית ללא מושגים מקצועיים. החזר JSON בלבד: [{{'q': 'שאלה', 'options': ['א', 'ב', 'ג']}}, ...]"
        with st.spinner("מכין שאלון פשוט..."):
            raw = call_gemini(prompt)
            qs = extract_json(raw)
            if qs: st.session_state['qs'] = qs

# שלב 2: שאלון
if 'qs' in st.session_state:
    st.markdown("---")
    st.subheader("📝 בוא נבין את הפרטים")
    ans_list = []
    for i, item in enumerate(st.session_state['qs']):
        st.markdown(f"**{i+1}. {item['q']}**")
        choice = st.radio(f"בחירה {i}", item['options'] + ["אחר"], key=f"radio_{i}", label_visibility="collapsed")
        final = choice
        if choice == "אחר": final = st.text_input(f"פרט כאן (שאלה {i+1}):", key=f"text_{i}")
        ans_list.append(f"ש: {item['q']} | ת: {final}")

    if st.button("🚀 הפק 5 תובנות אסטרטגיות"):
        p_names = ["חנה ארנדט", "פיטר דרוקר", "זיגמונד פרויד", "גק וולש"]
        prompt = f"""
        נושא: {idea}. תשובות: {ans_list}. קבינט: {p_names}.
        משימה:
        1. ציין 5 נקודות תובנה אסטרטגיות עיקריות. 
        2. השתמש בשפה מקצועית מעמיקה אך מובנת לכל אדם.
        3. הצג טבלה מסודרת: | בעיה | פתרון | דרך | תפוקות | תשומות |
        שחור על לבן, אותיות גדולות, ללא דריסת שורות.
        """
        with st.spinner("הקבינט מגבש החלטות..."):
            st.session_state['result'] = call_gemini(prompt)

# שלב 3: תוצאה
if 'result' in st.session_state:
    st.markdown("---")
    st.subheader("📊 המלצות הקבינט - 5 נקודות עיקריות")
    # הצגת התוצאה עם ריווח שורות כפול
    st.markdown(st.session_state['result'].replace('\n', '<br><br>'), unsafe_allow_html=True)
    
    if st.button("🧹 התחל דיון חדש"):
        for k in ['qs', 'result']: 
            if k in st.session_state: del st.session_state[k]
        st.rerun()