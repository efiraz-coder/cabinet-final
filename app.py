import streamlit as st
import google.generativeai as genai
import json
import re
import random
import time

# --- 1. גילוי מודלים חכם עם העדפה ל-Flash (חוסך Quota) ---
def get_available_model():
    if "GEMINI_KEY" not in st.secrets:
        st.error("Missing GEMINI_KEY in secrets")
        return None
    
    genai.configure(api_key=st.secrets["GEMINI_KEY"])
    
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # סדר עדיפויות: Flash 1.5 (הכי יציב וזול) -> Flash אחר -> Pro
        priority = ['models/gemini-1.5-flash', 'flash', 'pro']
        for p in priority:
            for m_name in models:
                if p in m_name: return m_name
        return models[0] if models else None
    except Exception as e:
        if "429" in str(e) or "quota" in str(e).lower():
            st.error("המכסה החינמית של גוגל הסתיימה לבינתיים. נסה שוב בעוד דקה.")
        else:
            st.error(f"שגיאת התחברות: {e}")
        return None

# --- 2. עיצוב ממשק ---
st.set_page_config(page_title="קבינט המוחות", layout="wide")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Assistant', sans-serif; direction: rtl; text-align: right; background-color: #0f172a; }
    .stTextArea textarea { color: #000000 !important; background-color: #ffffff !important; border: 2px solid #3b82f6 !important; font-size: 18px !important; }
    label, p, h1, h2, h3 { color: #f8fafc !important; }
    .expert-card { background-color: #ffffff; padding: 10px; border-radius: 8px; border: 2px solid #3b82f6; color: #1e293b !important; text-align: center; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 3. לוגיקה עמידה ---
def robust_json_parser(text):
    try:
        match = re.search(r'\[\s*{.*}\s*\]', text, re.DOTALL)
        if match: return json.loads(match.group())
    except: pass
    return None

if 'step' not in st.session_state: st.session_state.step = 'setup'
if 'history' not in st.session_state: st.session_state.history = []
if 'active_model' not in st.session_state: st.session_state.active_model = None

# --- שלב 0: הקמה ---
if st.session_state.step == 'setup':
    st.title("🏛️ קבינט המוחות")
    
    if not st.session_state.active_model:
        with st.spinner("מתחבר לקבינט..."):
            st.session_state.active_model = get_available_model()
    
    if st.session_state.active_model:
        st.caption(f"מחובר למערכת דרך: {st.session_state.active_model}")
    
    cols = st.columns(4)
    cabinet = ["סוקרטס", "מרקוס אורליוס", "ויקטור פראנקל", "יונג", "מקלוהן", "הררי", "סטיב ג'ובס", "דה וינצ'י"]
    for i, name in enumerate(cabinet):
        with cols[i % 4]: st.markdown(f"<div class='expert-card'>{name}</div>", unsafe_allow_html=True)
    
    st.write("---")
    idea = st.text_area("🖋️ תאר את המקרה לדיון:", height=150)
    
    if st.button("🔍 התחל אבחון"):
        if st.session_state.active_model and idea:
            st.session_state.user_idea = idea
            with st.spinner("מגבש שאלות..."):
                try:
                    model = genai.GenerativeModel(st.session_state.active_model)
                    res = model.generate_content(f"Topic: {idea}. Return JSON array of 3 diag questions: [{{'q':'text','options':['a','b','c']}}]")
                    questions = robust_json_parser(res.text)
                    if questions:
                        st.session_state.questions = questions
                        st.session_state.step = 'diagnostic'
                        st.rerun()
                    else:
                        st.warning("התקבל פורמט לא תקין, נסה שוב.")
                except Exception as e:
                    if "429" in str(e):
                        st.error("יותר מדי בקשות בזמן קצר. המתן 30 שניות ונסה שוב.")
                    else:
                        st.error(f"שגיאה: {e}")

# (שאר השלבים נשארים זהים...)
# (מפאת קוצר המקום לא שיניתי את שלב 1 ו-2 כי הם עובדים על אותה לוגיקה)