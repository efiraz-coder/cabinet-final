import streamlit as st
import requests
import pandas as pd

# הגדרת דף
st.set_page_config(page_title="קבינט המוחות של אפי", layout="wide")

# הזרקת CSS ל-RTL מלא ועיצוב נקי
st.markdown("""
    <style>
    .main, .block-container { direction: rtl; text-align: right; }
    [data-testid="stDataEditor"] { direction: rtl; text-align: right; }
    input, textarea { direction: rtl !important; text-align: right !important; }
    .story-box {
        border-right: 6px solid #1abc9c;
        padding: 25px;
        background-color: #f4f7f6;
        border-radius: 15px 0 0 15px;
        line-height: 1.8;
        margin-bottom: 25px;
    }
    div.stButton > button {
        width: 100%;
        border-radius: 10px;
        height: 3.5em;
        background-color: #2c3e50;
        color: white;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# משיכת מפתח
try:
    API_KEY = st.secrets["GEMINI_KEY"]
except:
    st.error("המפתח חסר ב-Secrets!")
    st.stop()

API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={API_KEY}"

def call_gemini(prompt):
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        res = requests.post(API_URL, json=payload)
        if res.status_code == 200:
            return res.json()['candidates'][0]['content']['parts'][0]['text']
        return ""
    except:
        return ""

# ניהול משתתפים
if 'participants_df' not in st.session_state:
    names = ["חנה ארנדט", "לודוויג ויטגנשטיין", "פיטר דרוקר", "אדוארד האלוול", "זיגמונד פרויד", "זאן פיאזה", "אלברט בנדורה", "גק וולש", "ריד הופמן"]
    roles = ["פילוסופיה", "שפה", "ניהול", "קוגניציה", "פסיכולוגיה", "התפתחות", "חברה", "עסקים", "נטוורקינג"]
    st.session_state['participants_df'] = pd.DataFrame({"שם": names, "סיווג": roles})

st.title("🏛️ קבינט המוחות של אפי")

with st.expander("👤 ניהול חברי הקבינט"):
    st.session_state['participants_df'] = st.data_editor(st.session_state['participants_df'], num_rows="dynamic", use_container_width=True)

st.subheader("🖋️ שלב א': הגדרת הסוגיה")
idea = st.text_area("מה הנושא שעל הפרק?", height=80)

if st.button("❓ שאלות מנחות"):
    if idea:
        members = ", ".join(st.session_state['participants_df']["שם"].tolist())
        # הנחיה קשיחה לקבלת שאלות בלבד
        prompt = f"נושא: {idea}. משתתפים: {members}. נסח אך ורק 4 שאלות אבחון קצרות. אל תוסיף פתיח, הסברים או סיומת. רק השאלות עצמן בשורות נפרדות."
        with st.spinner("הקבינט מנסח שאלות..."):
            res_text = call_gemini(prompt)
            # סינון שורות ריקות או טקסט שאינו שאלה
            st.session_state['questions'] = [q.strip() for q in res_text.split('\n') if '?' in q or '？' in q]

if 'questions' in st.session_state:
    st.markdown("### 📝 שאלות האבחון של הקבינט")
    ans_list = []
    # הצגת השאלות בלבד ככותרות לשדות הקלט
    for i, q in enumerate(st.session_state['questions']):
        # הסרת מספרי שורות אם המודל הוסיף (כמו 1. או 2.)
        clean_q = q.lstrip('0123456789. -')
        a = st.text_input(clean_q, key=f"ans_{i}", placeholder="הזן תשובתך כאן...")
        ans_list.append(f"שאלה: {clean_q} | תשובה: {a}")

    st.markdown("---")
    if st.button("🎭 הצג דיון סכם ומסר אסטרטגי"):
        members = ", ".join(st.session_state['participants_df']["שם"].tolist())
        user_context = "\n".join(ans_list)
        summary_prompt = f"""
        הנושא: {idea}. תשובות אפי: {user_context}. משתתפים: {members}.
        צור דיון מסכם במסר סיפורי-לוגי המבוסס על חברי הקבינט. 
        לאחר הדיון, הצע 2 כיווני פעולה עם אבני דרך, תשומות ותפוקות בטבלאות.
        יישור לימין, עברית רהוטה.
        """
        with st.spinner("הקבינט בסיכום סופי..."):
            st.session_state['final_story'] = call_gemini(summary_prompt)

if 'final_story' in st.session_state:
    st.markdown("### 📜 סיכום אסטרטגי")
    st.markdown(f'<div class="story-box">{st.session_state["final_story"].replace("\n", "<br>")}</div>', unsafe_allow_html=True)
    if st.button("🗑️ דיון חדש"):
        del st.session_state['questions']
        del st.session_state['final_story']
        st.rerun()