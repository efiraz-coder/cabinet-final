import streamlit as st
import requests
import pandas as pd

# הגדרת דף
st.set_page_config(page_title="קבינט המוחות של אפי", layout="wide")

# הזרקת CSS ל-RTL מלא וניראות מקסימלית
st.markdown("""
    <style>
    .main, .block-container { direction: rtl; text-align: right; }
    [data-testid="stDataEditor"] { direction: rtl; text-align: right; }
    input, textarea { direction: rtl !important; text-align: right !important; color: black !important; }
    
    /* תיבת הסיכום - טקסט שחור וברור */
    .story-box {
        border-right: 8px solid #1abc9c;
        padding: 30px;
        background-color: #ffffff;
        color: #1a1a1a !important;
        border-radius: 15px 0 0 15px;
        line-height: 1.8;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        font-size: 1.1em;
    }
    
    div.stButton > button {
        width: 100%;
        border-radius: 10px;
        height: 3.5em;
        background-color: #2c3e50;
        color: white;
        font-weight: bold;
    }
    
    /* יישור טבלאות בתוך המארק דאון */
    table { width: 100%; direction: rtl; text-align: right; border-collapse: collapse; }
    th, td { border: 1px solid #ddd; padding: 8px; text-align: right; }
    th { background-color: #f2f2f2; }
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
        return "שגיאה בתקשורת עם השרת"
    except:
        return "תקלה טכנית בחיבור"

# ניהול משתתפים
if 'participants_df' not in st.session_state:
    names = ["חנה ארנדט", "לודוויג ויטגנשטיין", "פיטר דרוקר", "אדוארד האלוול", "זיגמונד פרויד", "זאן פיאזה", "אלברט בנדורה", "גק וולש", "ריד הופמן"]
    roles = ["פילוסופיה", "שפה", "ניהול", "קוגניציה", "פסיכולוגיה", "התפתחות", "חברה", "עסקים", "נטוורקינג"]
    st.session_state['participants_df'] = pd.DataFrame({"שם": names, "סיווג": roles})

st.title("🏛️ קבינט המוחות של אפי")

with st.expander("👤 ניהול חברי הקבינט"):
    st.session_state['participants_df'] = st.data_editor(st.session_state['participants_df'], num_rows="dynamic", use_container_width=True)

st.subheader("🖋️ שלב א': הגדרת הסוגיה")
idea = st.text_area("מה הנושא שעל הפרק?", height=80, placeholder="כתוב כאן...")

if st.button("❓ שאלות מנחות"):
    if idea:
        members = ", ".join(st.session_state['participants_df']["שם"].tolist())
        prompt = f"נושא: {idea}. משתתפים: {members}. נסח 4 שאלות אבחון קצרות בלבד בלי הסברים. כל שאלה בשורה חדשה."
        with st.spinner("הקבינט מנסח שאלות..."):
            res_text = call_gemini(prompt)
            st.session_state['questions'] = [q.strip() for q in res_text.split('\n') if '?' in q or '？' in q]

if 'questions' in st.session_state:
    st.markdown("### 📝 שאלות האבחון")
    ans_list = []
    for i, q in enumerate(st.session_state['questions']):
        clean_q = q.lstrip('0123456789. -')
        a = st.text_input(clean_q, key=f"ans_{i}")
        ans_list.append(f"שאלה: {clean_q} | תשובה: {a}")

    st.markdown("---")
    if st.button("🎭 הצג דיון סכם (כולל אורח בהפתעה)"):
        members = ", ".join(st.session_state['participants_df']["שם"].tolist())
        user_context = "\n".join(ans_list)
        summary_prompt = f"""
        הנושא: {idea}. תשובות אפי: {user_context}. משתתפים: {members}.
        
        הוראות:
        1. בצע דיון מסכם סיפורי-לוגי המבוסס על המשתתפים.
        2. הוסף 'אורח בהפתעה' (דמות היסטורית/תרבותית רלוונטית שלא ברשימה) שיתרום זווית ייחודית.
        3. הצע 2 כיווני פעולה עם אבני דרך, תשומות ותפוקות בטבלאות Markdown.
        4. הכל בעברית, יישור לימין.
        """
        with st.spinner("הקבינט והאורח מסכמים..."):
            st.session_state['final_story'] = call_gemini(summary_prompt)

if 'final_story' in st.session_state:
    st.markdown("### 📜 הסיכום האסטרטגי")
    # תיקון תצוגה כדי למנוע טקסט לבן על רקע לבן
    st.markdown(f'<div class="story-box">{st.session_state["final_story"].replace("\n", "<br>")}</div>', unsafe_allow_html=True)
    
    if st.button("🗑️ דיון חדש"):
        for k in ['questions', 'final_story']:
            if k in st.session_state: del st.session_state[k]
        st.rerun()