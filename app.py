import streamlit as st
import google.generativeai as genai
import json
import re
import random

# הגדרות דף ועיצוב
st.set_page_config(page_title="קבינט המוחות של אפי", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Assistant', sans-serif; direction: rtl; text-align: right; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; font-weight: bold; background-color: #bbdefb; border: 2px solid #1976d2; color: #000; }
    .expert-card { background-color: #ffffff; padding: 15px; border-right: 5px solid #1976d2; border-radius: 8px; margin-bottom: 15px; box-shadow: 1px 1px 5px rgba(0,0,0,0.1); color: #000; }
    </style>
    """, unsafe_allow_html=True)

# התחברות למפתח (וודא שהוא ב-Secrets)
if "GEMINI_KEY" not in st.secrets:
    st.error("המפתח GEMINI_KEY חסר ב-Secrets!")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_KEY"])

# שימוש במודל שנמצא אצלך כפעיל
WORKING_MODEL = "gemini-2.5-flash"

def call_cabinet(prompt):
    try:
        model = genai.GenerativeModel(WORKING_MODEL)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"שגיאה: {e}")
        return None

# אתחול חברי הקבינט
if 'cabinet' not in st.session_state:
    pool = [
        {"שם": "פיטר דרוקר", "תמחות": "אסטרטגיה וניהול"},
        {"שם": "סטיב ג'ובס", "תמחות": "חדשנות וחווית משתמש"},
        {"שם": "סון דזו", "תמחות": "טקטיקה ותמרון"},
        {"שם": "זיגמונד פרויד", "תמחות": "פסיכולוגיה ותת-מודע"},
        {"שם": "חנה ארנדט", "תמחות": "אתיקה ופילוסופיה"},
        {"שם": "דניאל כהנמן", "תמחות": "קבלת החלטות"}
    ]
    st.session_state.cabinet = random.sample(pool, 6)

st.title("🏛️ קבינט המוחות של אפי")
st.subheader("היועצים האסטרטגיים שלך מוכנים לניתוח")

idea = st.text_area("🖋️ תאר את האתגר שלך:", height=100, placeholder="למשל: איך להגדיל את נפח הפעילות העסקית?")

if st.button("🔍 התחל אבחון עם הקבינט"):
    if idea:
        with st.spinner("המומחים מגבשים שאלות..."):
            experts_list = ", ".join([f"{m['שם']} ({m['תמחות']})" for m in st.session_state.cabinet])
            prompt = f"""
            נושא: {idea}. 
            מומחים: {experts_list}.
            נסח 6 שאלות אבחון קצרות (אחת לכל מומחה).
            החזר אך ורק פורמט JSON תקין:
            [ {{"expert": "שם", "q": "שאלה", "options": ["א", "ב", "ג"]}} ]
            """
            raw = call_cabinet(prompt)
            if raw:
                match = re.search(r'\[.*\]', raw.replace('```json', '').replace('```', ''), re.DOTALL)
                if match:
                    st.session_state.qs = json.loads(match.group())
                    st.session_state.pop('res', None)
                    st.rerun()

if 'qs' in st.session_state:
    st.write("---")
    ans_list = []
    for i, item in enumerate(st.session_state.qs):
        st.markdown(f"<div class='expert-card'>💡 <b>{item['expert']}</b> שואל/ת:</div>", unsafe_allow_html=True)
        choice = st.radio(item['q'], item['options'], key=f"q_{i}")
        ans_list.append(f"{item['expert']}: {choice}")
    
    if st.button("🚀 הפק דו\"ח תובנות סופי"):
        with st.spinner("הקבינט מסכם את הדיון..."):
            final_p = f"נושא: {idea}. תשובות: {ans_list}. כתוב 5 תובנות עמוקות וטבלה מסכמת עם צעדים לביצוע."
            st.session_state.res = call_cabinet(final_p)

if 'res' in st.session_state:
    st.write("---")
    st.success("📊 המלצות הקבינט של אפי:")
    st.markdown(st.session_state.res)