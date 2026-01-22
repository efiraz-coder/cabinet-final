import streamlit as st
import requests
import pandas as pd
import json
import re

# הגדרת דף
st.set_page_config(page_title="קבינט המוחות של אפי", layout="wide")

# CSS אגרסיבי - דורס את הגדרות המערכת לטובת שחור על לבן
st.markdown("""
    <style>
    /* הפיכת כל הרקע ללבן נקי */
    .stApp {
        background-color: #FFFFFF !important;
    }
    
    /* הפיכת כל הטקסט באפליקציה לשחור עז */
    .stApp, .stMarkdown, p, h1, h2, h3, h4, li, span, label {
        color: #000000 !important;
        direction: rtl !important;
        text-align: right !important;
    }

    /* עיצוב שדות הקלט - רקע אפור בהיר מאוד עם טקסט שחור */
    input, textarea, [data-baseweb="select"], [data-baseweb="radio"] {
        background-color: #F8F9FA !important;
        color: #000000 !important;
        border: 2px solid #2c3e50 !important;
    }

    /* תיבת הסיכום האסטרטגי - מראה של מסמך רשמי */
    .story-box {
        border-right: 10px solid #2c3e50;
        padding: 30px;
        background-color: #FFFFFF;
        color: #000000 !important;
        border-radius: 5px;
        line-height: 1.8;
        font-size: 1.2em;
        box-shadow: 0 0 15px rgba(0,0,0,0.1);
        margin-top: 20px;
        border: 1px solid #EEEEEE;
    }

    /* טבלאות - שחור על לבן */
    table {
        width: 100%;
        border-collapse: collapse;
        color: #000000 !important;
        background-color: white !important;
    }
    th, td {
        border: 1px solid #000000 !important;
        padding: 12px;
        text-align: right;
    }
    th {
        background-color: #F2F2F2 !important;
    }

    /* כפתור הפעלה גדול ובולט */
    div.stButton > button {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        border-radius: 0px;
        height: 4em;
        font-size: 1.2em;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# פונקציית חילוץ JSON
def extract_json(text):
    try:
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match: return json.loads(match.group())
        return json.loads(text)
    except: return None

# חיבור ל-API
API_KEY = st.secrets["GEMINI_KEY"]
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={API_KEY}"

def call_gemini(prompt):
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    res = requests.post(API_URL, json=payload)
    return res.json()['candidates'][0]['content']['parts'][0]['text'] if res.status_code == 200 else ""

# ניהול משתתפים
if 'participants_df' not in st.session_state:
    names = ["חנה ארנדט", "לודוויג ויטגנשטיין", "פיטר דרוקר", "אדוארד האלוול", "זיגמונד פרויד", "זאן פיאזה", "אלברט בנדורה", "גק וולש", "ריד הופמן"]
    roles = ["פילוסופיה", "שפה", "ניהול", "קוגניציה", "פסיכולוגיה", "התפתחות", "חברה", "עסקים", "נטוורקינג"]
    st.session_state['participants_df'] = pd.DataFrame({"שם": names, "סיווג": roles})

st.title("🏛️ קבינט המוחות של אפי")

with st.expander("👤 ניהול חברי הקבינט"):
    st.session_state['participants_df'] = st.data_editor(st.session_state['participants_df'], num_rows="dynamic", use_container_width=True)

st.subheader("🖋️ שלב א': הגדרת הסוגיה")
idea = st.text_area("מה הנושא שעל הפרק?", height=100)

if st.button("❓ שלח וקבל שאלות אבחון"):
    if idea:
        members = ", ".join(st.session_state['participants_df']["שם"].tolist())
        prompt = f"""
        נושא: {idea}. משתתפים: {members}. 
        נסח 4 שאלות אבחון. לכל שאלה הצע 3 תשובות אפשריות.
        החזר אך ורק פורמט JSON תקני:
        [
          {{"q": "שאלה 1", "options": ["אופציה א", "אופציה ב", "אופציה ג"]}},
          ...
        ]
        """
        with st.spinner("הקבינט מגבש שאלות..."):
            raw_res = call_gemini(prompt)
            questions = extract_json(raw_res)
            if questions: st.session_state['structured_questions'] = questions
            else: st.error("הקבינט לא הצליח לייצר שאלון, נסה שוב.")

if 'structured_questions' in st.session_state:
    st.markdown("### 📝 שאלון אבחון מהיר (בחר תשובה):")
    user_answers = []
    for i, item in enumerate(st.session_state['structured_questions']):
        options = item['options'] + ["אחר (פרט למטה)"]
        st.write(f"**{i+1}. {item['q']}**")
        choice = st.radio(f"בחירה לשאלה {i}", options, key=f"q_{i}", label_visibility="collapsed")
        
        final_ans = choice
        if choice == "אחר (פרט למטה)":
            final_ans = st.text_input(f"כתוב תשובה משלך לשאלה {i+1}:", key=f"text_{i}")
        
        user_answers.append(f"שאלה: {item['q']} | תשובה: {final_ans}")

    st.markdown("---")
    if st.button("🎭 הפק סיכום אסטרטגי סופי"):
        members = ", ".join(st.session_state['participants_df']["שם"].tolist())
        context = "\n".join(user_answers)
        summary_prompt = f"""
        נושא: {idea}. תשובות אפי: {context}. משתתפים: {members}.
        
        דרישות:
        1. סיפור לוגי מעמיק המנתח את המצב. הוסף מספר בסוגריים [1], [2] להפניה לציטוטים.
        2. בסוף, פרק 'ציטוטים מהקבינט' לפי המספרים.
        3. טבלה אסטרטגית הכוללת: | בעיה | פתרון | דרך | תפוקות | תשומות |
        עברית רהוטה, הכל בשחור על לבן.
        """
        with st.spinner("הקבינט כותב..."):
            st.session_state['final_result'] = call_gemini(summary_prompt)

if 'final_result' in st.session_state:
    st.markdown("### 📜 התוצר האסטרטגי")
    st.markdown(f'<div class="story-box">{st.session_state["final_result"].replace("\n", "<br>")}</div>', unsafe_allow_html=True)
    if st.button("🗑️ נקה הכל והתחל מחדש"):
        for k in ['structured_questions', 'final_result']:
            if k in st.session_state: del st.session_state[k]
        st.rerun()