import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="קבינט המוחות של אפי", layout="wide")

# CSS לשיפור הניראות ויישור RTL
st.markdown("""
    <style>
    .main, .block-container { direction: rtl; text-align: right; }
    input, textarea, .stSelectbox { direction: rtl !important; text-align: right !important; color: black !important; }
    .story-box { border-right: 8px solid #1abc9c; padding: 30px; background-color: #ffffff; color: #1a1a1a !important; border-radius: 15px 0 0 15px; line-height: 1.8; font-size: 1.1em; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .quote-section { background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-top: 20px; font-style: italic; }
    div.stButton > button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #2c3e50; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

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
idea = st.text_area("מה הנושא שעל הפרק?", height=80)

if st.button("❓ שאלות מנחות"):
    if idea:
        members = ", ".join(st.session_state['participants_df']["שם"].tolist())
        prompt = f"נושא: {idea}. משתתפים: {members}. נסח 4 שאלות אבחון. לכל שאלה הצע 3 תשובות אפשריות קצרות. ענה בפורמט JSON: [{{'q': 'שאלה', 'options': ['א', 'ב', 'ג']}}, ...]"
        res = call_gemini(prompt)
        try:
            # ניקוי פורמט JSON מהתשובה
            clean_res = res.replace('```json', '').replace('```', '').strip()
            st.session_state['structured_questions'] = json.loads(clean_res)
        except:
            st.error("הקבינט מתקשה בעיבוד השאלות, נסה שנית.")

if 'structured_questions' in st.session_state:
    st.markdown("### 📝 שאלון אבחון מהיר")
    user_answers = []
    for i, item in enumerate(st.session_state['structured_questions']):
        options = item['options'] + ["אחר (כתיבה חופשית)"]
        choice = st.radio(item['q'], options, key=f"q_{i}")
        
        final_ans = choice
        if choice == "אחר (כתיבה חופשית)":
            final_ans = st.text_input(f"פרט עבור: {item['q']}", key=f"text_{i}")
        
        user_answers.append(f"שאלה: {item['q']} | תשובה: {final_ans}")

    st.markdown("---")
    if st.button("🎭 הפק סיכום אסטרטגי"):
        members = ", ".join(st.session_state['participants_df']["שם"].tolist())
        context = "\n".join(user_answers)
        summary_prompt = f"""
        נושא: {idea}. תשובות: {context}. משתתפים: {members}.
        
        משימה:
        1. ספר סיפור לוגי עמוק המנתח את המצב. הוסף מספר בסוגריים [x] בסוף משפטים המפנים לציטטות.
        2. בסוף הסיפור, הוסף פרק 'מקורות וציטטות מהקבינט' עם הציטוטים המתאימים למספרים.
        3. הצג טבלה אחת מסודרת: | בעיה | פתרון | דרך | תפוקות | תשומות |
        4. יישור לימין, שפה עשירה.
        """
        with st.spinner("הקבינט מעבד את הנתונים..."):
            st.session_state['final_result'] = call_gemini(summary_prompt)

if 'final_result' in st.session_state:
    st.markdown("### 📜 התוצר האסטרטגי")
    st.markdown(f'<div class="story-box">{st.session_state["final_result"].replace("\n", "<br>")}</div>', unsafe_allow_html=True)
    if st.button("🗑️ ניקוי דיון"):
        for k in ['structured_questions', 'final_result']:
            if k in st.session_state: del st.session_state[k]
        st.rerun()