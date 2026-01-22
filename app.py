import streamlit as st
import requests
import pandas as pd

# הגדרת דף רחב
st.set_page_config(page_title="קבינט המוחות של אפי", layout="wide")

# --- הזרקת CSS לתיקון RTL מלא ועיצוב אסתטי ---
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
    st.error("המפתח (GEMINI_KEY) חסר ב-Secrets של Streamlit!")
    st.stop()

API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={API_KEY}"

def call_gemini(prompt):
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        res = requests.post(API_URL, json=payload)
        if res.status_code == 200:
            return res.json()['candidates'][0]['content']['parts'][0]['text']
        return f"שגיאת שרת: {res.status_code}"
    except Exception as e:
        return f"תקלה בחיבור: {str(e)}"

# --- ניהול משתתפים ---
if 'participants_df' not in st.session_state:
    names = ["חנה ארנדט", "לודוויג ויטגנשטיין", "פיטר דרוקר", "ד"ר אדוארד האלוול", "זיגמונד פרויד", "ז'אן פיאז'ה", "אלברט בנדורה", "ג'ק וולש", "ריד הופמן"]
    roles = ["פילוסופיה", "שפה", "ניהול", "קוגניציה", "פסיכולוגיה", "התפתחות", "חברה", "עסקים", "נטוורקינג"]
    st.session_state['participants_df'] = pd.DataFrame({"שם": names, "סיווג": roles})

st.title("🏛️ קבינט המוחות של אפי")

# --- עריכת הרכב ---
with st.expander("👤 עריכת הרכב הקבינט"):
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
            res_text = call_gemini(prompt)
            st.session_state['questions'] = res_text.split('\n')

if 'questions' in st.session_state:
    st.info("נא לענות כדי לדייק את הניתוח:")
    ans_list = []
    for i, q in enumerate(st.session_state['questions']):
        if q.strip():
            a = st.text_input(f"{q}", key=f"ans_{i}")
            ans_list.append(f"ש: {q} ת: {a}")

    # --- שלב ב: הדיון המסכם ---
    st.markdown("---")
    if st.button("🎭 הצג דיון סכם ומסר אסטרטגי"):
        members = ", ".join(st.session_state['participants_df']["שם"].tolist())
        user_context = "\n".join(ans_list)
        summary_prompt = f"""
        הנושא: {idea}. תשובות אפי: {user_context}. משתתפים: {members}.
        צור דיון מסכם במסר סיפורי-לוגי עמוק וידידותי המבוסס על חברי הקבינט. 
        לאחר מכן, הצע 2 כיווני פעולה עם אבני דרך, תשומות ותפוקות בטבלאות ברורות.
        הכל בעברית רהוטה ומיושר לימין.
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