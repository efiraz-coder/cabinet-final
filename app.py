import streamlit as st
import requests
import pandas as pd

# הגדרת דף רחב
st.set_page_config(page_title="קבינט המוחות של אפי", layout="wide")

# --- הזרקת CSS לתיקון RTL מלא (כולל טבלאות) ---
st.markdown("""
    <style>
    /* הגדרת כיוון כללי למסך */
    .main, .block-container {
        direction: rtl;
        text-align: right;
    }
    
    /* יישור טבלאות (Data Editor) */
    [data-testid="stDataEditor"] {
        direction: rtl;
        text-align: right;
    }
    
    /* יישור כותרות עמודה בטבלה */
    .st-ae {
        text-align: right !important;
    }

    /* יישור תיבות טקסט וקלט */
    input, textarea {
        direction: rtl !important;
        text-align: right !important;
    }

    /* עיצוב תיבת הסיפור המסכם */
    .story-box {
        border-right: 6px solid #1abc9c;
        padding: 25px;
        background-color: #f4f7f6;
        border-radius: 15px 0 0 15px;
        line-height: 1.8;
        margin-bottom: 25px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }

    /* עיצוב כפתורים */
    div.stButton > button {
        width: 100%;
        border-radius: 10px;
        height: 3.5em;
        background-color: #2c3e50;
        color: white;
        font-weight: bold;
        border: none;
    }
    
    /* תיקון יישור לצ'קבוקסים */
    .stCheckbox {
        direction: rtl;
        display: flex;
        flex-direction: row-reverse;
        justify-content: flex-end;
    }
    </style>
    """, unsafe_allow_html=True)

# משיכת מפתח
API_KEY = st.secrets["GEMINI_KEY"]
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={API_KEY}"

def call_gemini(prompt):
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    res = requests.post(API_URL, json=payload)
    return res.json()['candidates'][0]['content']['parts'][0]['text'] if res.status_code == 200 else "תקלה בחיבור"

# --- ניהול משתתפים ---
if 'participants_df' not in st.session_state:
    st.session_state['participants_df'] = pd.DataFrame({
        "שם": ["חנה ארנדט", "לודוויג ויטגנשטיין", "פיטר דרוקר", "ד"ר אדוארד האלוול", "זיגמונד פרויד", "ז'אן פיאז'ה", "אלברט בנדורה", "ג'ק וולש", "ריד הופמן"],
        "סיווג": ["פילוסופיה", "שפה", "ניהול", "קוגניציה", "פסיכולוגיה", "התפתחות", "חברה", "עסקים", "נטוורקינג"]
    })

st.title("🏛️ קבינט המוחות של אפי")

# --- עריכת הרכב ---
with st.expander("👤 עריכת הרכב הקבינט - ניהול בטבלה"):
    st.session_state['participants_df'] = st.data_editor(
        st.session_state['participants_df'], 
        num_rows="dynamic", 
        use_container_width=True
    )

# --- שלב א: אבחון ---
st.subheader("🖋️ הגדרת הסוגיה")
idea = st.text_area("מה הנושא שעל הפרק?", height=80)

if st.button("❓ שאלות מנחות"):
    if idea:
        members = ", ".join(st.session_state['participants_df']["שם"].tolist())
        prompt = f"הנושא: {idea}. חברי הקבינט: {members}. נסח 4 שאלות אבחון קצרות לאפי על יכולותיו ומגבלותיו."
        with st.spinner("הקבינט מנסח שאלות..."):
            st.session_state['questions'] = call_gemini(prompt).split('\n')

# הצגת שאלות ומענה
if 'questions' in st.session_state:
    st.info("נא לענות כדי לדייק את הניתוח:")
    user_answers = ""
    for i, q in enumerate(st.session_state['questions']):
        if q.strip():
            ans = st.text_input(f"{q}", key=f"ans_{i}")
            user_answers += f"שאלה: {q} תשובה: {ans}\n"

    # --- שלב ב: הדיון המסכם ---
    st.markdown("---")
    if st.button("🎭 הצג דיון סכם ומסר אסטרטגי"):
        members = ", ".join(st.session_state['participants_df']["שם"].tolist())
        summary_prompt = f"""
        הנושא: {idea}. תשובות אפי: {user_answers}. משתתפים: {members}.
        צור דיון מסכם במסר סיפורי-לוגי עמוק. צטט דמויות מהקבינט.
        בסוף, הצג 2 כיווני פעולה הכוללים אבני דרך, תשומות ותפוקות.
        הוראה קריטית: הצג את כיווני הפעולה בטבלאות מעוצבות.
        יישר הכל לימין.
        """
        with st.spinner("הקבינט בסיכום סופי..."):
            st.session_state['final_story'] = call_gemini(summary_prompt)

# הצגת התוצאה
if 'final_story' in st.session_state:
    st.markdown("### 📜 סיכום אסטרטגי")
    st.markdown(f'<div class="story-box">{st.session_state["final_story"].replace("\n", "<br>")}</div>', unsafe_allow_html=True)

    if st.button("🗑️ דיון חדש"):
        for key in ['questions', 'final_story']:
            if key in st.session_state: del st.session_state[key]
        st.rerun()