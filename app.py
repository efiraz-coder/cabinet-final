import streamlit as st
import requests
import pandas as pd
import json
import re

# הגדרת דף רחב עם כותרת
st.set_page_config(page_title="קבינט המוחות של אפי", layout="wide")

# --- CSS משודרג: טיפוגרפיה מודרנית וכרטיסיות אסטרטגיות ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;700&display=swap');

    html, body, [class*="st-"] {
        font-family: 'Assistant', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
        color: #1a1a1a !important;
    }

    .stApp { background-color: #f4f7f9 !important; }

    /* עיצוב כותרת ראשית */
    h1 { 
        color: #1e3a8a !important; 
        font-weight: 700; 
        border-bottom: 4px solid #3b82f6; 
        padding-bottom: 15px;
        margin-bottom: 30px;
    }

    /* עיצוב כרטיסיות (Cards) לשלבי העבודה */
    .stFieldBlock, .story-box, .step-card {
        background-color: #ffffff !important;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        margin-bottom: 25px;
    }

    /* עיצוב תיבת הסיכום הסופי */
    .story-box {
        border-right: 12px solid #1e3a8a;
        line-height: 1.9;
        font-size: 1.15em;
    }

    /* כפתורים בעיצוב פרימיום */
    div.stButton > button {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        height: 3.8em;
        font-weight: 700;
        font-size: 1.1em;
        transition: transform 0.2s ease;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(59, 130, 246, 0.3);
    }

    /* טבלאות בעיצוב נקי */
    table { width: 100%; direction: rtl; border-collapse: collapse; margin-top: 20px; }
    th { background-color: #f1f5f9 !important; color: #1e3a8a !important; font-weight: 700; padding: 12px; border: 1px solid #cbd5e1; }
    td { padding: 12px; border: 1px solid #cbd5e1; background-color: #ffffff; }

    /* רדיו באטנס (שאלון אמריקאי) */
    div[data-baseweb="radio"] { gap: 10px; }
    label[data-baseweb="radio"] { 
        background-color: #f8fafc; 
        padding: 10px 20px; 
        border-radius: 8px; 
        border: 1px solid #e2e8f0; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- פונקציות עזר ---
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

# --- הגדרת משתתפים ---
if 'participants_df' not in st.session_state:
    data = {
        "שם": ["חנה ארנדט", "לודוויג ויטגנשטיין", "פיטר דרוקר", "אדוארד האלוול", "זיגמונד פרויד", "זאן פיאזה", "אלברט בנדורה", "גק וולש", "ריד הופמן"],
        "סיווג": ["פילוסופיה", "שפה", "ניהול", "קוגניציה", "פסיכולוגיה", "התפתחות", "חברה", "עסקים", "נטוורקינג"]
    }
    st.session_state['participants_df'] = pd.DataFrame(data)

# --- ממשק משתמש ---
st.title("🏛️ קבינט המוחות של אפי")

with st.expander("👤 ניהול הרכב הקבינט"):
    st.session_state['participants_df'] = st.data_editor(st.session_state['participants_df'], num_rows="dynamic", use_container_width=True)

# שלב 1: נושא
st.markdown('<div class="step-card">', unsafe_allow_html=True)
st.subheader("🖋️ שלב 1: הגדרת הסוגיה")
idea = st.text_area("על מה נדון היום?", height=100, placeholder="הזן את האתגר או הרעיון שלך...")
if st.button("🔍 התחל אבחון אסטרטגי"):
    if idea:
        members = ", ".join(st.session_state['participants_df']["שם"].tolist())
        prompt = f"נושא: {idea}. משתתפים: {members}. נסח 4 שאלות אבחון עם 3 אפשרויות לכל אחת ב-JSON: [{{'q': '...', 'options': [...]}}, ...]"
        with st.spinner("חברי הקבינט מתייעצים..."):
            raw = call_gemini(prompt)
            qs = extract_json(raw)
            if qs: st.session_state['structured_questions'] = qs
st.markdown('</div>', unsafe_allow_html=True)

# שלב 2: שאלון
if 'structured_questions' in st.session_state:
    st.markdown('<div class="step-card">', unsafe_allow_html=True)
    st.subheader("📝 שלב 2: אבחון מותאם אישית")
    st.progress(0.5) # מחוון התקדמות
    user_answers = []
    for i, item in enumerate(st.session_state['structured_questions']):
        st.write(f"**{item['q']}**")
        choice = st.radio(f"שאלה {i}", item['options'] + ["אחר (פירוט חופשי)"], key=f"r_{i}", label_visibility="collapsed")
        ans = choice
        if choice == "אחר (פירוט חופשי)":
            ans = st.text_input(f"פרט כאן (שאלה {i+1}):", key=f"t_{i}")
        user_answers.append(f"ש: {item['q']} | ת: {ans}")

    if st.button("🚀 הפק תוכנית פעולה"):
        summary_prompt = f"""
        נושא: {idea}. תשובות: {user_answers}. משתתפים: {st.session_state['participants_df']['שם'].tolist()}.
        1. סיפור לוגי מעמיק עם הפניות למספרים [1].
        2. פרק ציטוטים בסוף.
        3. טבלה אסטרטגית: | בעיה | פתרון | דרך | תפוקות | תשומות |
        """
        with st.spinner("הקבינט מגבש את המסקנות הסופיות..."):
            st.session_state['final_result'] = call_gemini(summary_prompt)
    st.markdown('</div>', unsafe_allow_html=True)

# שלב 3: תוצאה
if 'final_result' in st.session_state:
    st.markdown('<div class="story-box">', unsafe_allow_html=True)
    st.subheader("📜 התוצר האסטרטגי")
    st.markdown(st.session_state['final_result'].replace('\n', '<br>'), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("🧹 פתח סוגיה חדשה"):
        for k in ['structured_questions', 'final_result']:
            if k in st.session_state: del st.session_state[k]
        st.rerun()