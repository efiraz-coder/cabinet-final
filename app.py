import streamlit as st
import requests
import json

st.set_page_config(page_title="קבינט המוחות של אפי", layout="centered")

# עיצוב RTL
st.markdown("""
    <style>
    .main { direction: rtl; text-align: right; }
    div.stButton > button { width: 100%; border-radius: 20px; background-color: #f0f2f6; }
    .stTextArea textarea { direction: rtl; }
    </style>
    """, unsafe_allow_html=True)

# משיכת מפתח מה-Secrets
API_KEY = st.secrets["GEMINI_KEY"]
MODEL_NAME = "gemini-flash-latest" 
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"

def call_gemini(prompt):
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    response = requests.post(API_URL, json=payload)
    if response.status_code == 200:
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    return f"שגיאה: {response.status_code}"

# --- ניהול משתתפים ---
if 'participants' not in st.session_state:
    st.session_state['participants'] = "ארנדט, ויטגנשטיין, דרוקר, האלוול, פרויד, בנדורה"

# --- כניסה ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    st.title("🏛️ כניסה לקבינט")
    pwd = st.text_input("הזן סיסמה:", type="password")
    if st.button("התחבר"):
        if pwd == "אפי2026":
            st.session_state['auth'] = True
            st.rerun()
    st.stop()

# --- ממשק משתמש ---
st.title("🏛️ קבינט המוחות של אפי")

with st.expander("👤 עריכת הרכב הקבינט"):
    st.session_state['participants'] = st.text_area("שמות המשתתפים:", value=st.session_state['participants'])

# --- שלב 1: הצגת הנושא ושאלות אבחון ---
st.subheader("שלב א': הגדרת הסוגיה")
idea = st.text_area("על מה נדון היום?", height=100)

if st.button("🔍 בקש שאלות אבחון מהקבינט"):
    if idea:
        with st.spinner("הקבינט מגבש שאלות אבחון..."):
            diag_prompt = f"""
            הנושא: {idea}
            משתתפי הקבינט: {st.session_state['participants']}
            לפני מתן פתרונות, על הקבינט לשאול את המבקש (אפי) 4 שאלות ממוקדות שיעזרו להם להבין 
            את יכולותיו, מגבלותיו, המשאבים שלו והקשר הסוגיה לחייו. 
            כתוב את השאלות בצורה ישירה, קצרה ומימין לשמאל.
            """
            questions = call_gemini(diag_prompt)
            st.session_state['diag_questions'] = questions
            st.session_state['step'] = 2

if 'diag_questions' in st.session_state:
    st.info("❓ שאלות הקבינט עבורך:")
    st.markdown(f"<div style='direction: rtl;'>{st.session_state['diag_questions']}</div>", unsafe_allow_html=True)
    
    # --- שלב 2: תשובות המשתמש ופתרון סופי ---
    st.subheader("שלב ב': תשובות אפי וניתוח אסטרטגי")
    user_answers = st.text_area("הזן כאן את תשובותיך ומידע רלוונטי על עצמך:", height=150)
    
    if st.button("🚀 הפק אסטרטגיה מותאמת אישית"):
        with st.spinner("הקבינט מעבד את הנתונים ומגבש כיווני פעולה..."):
            final_prompt = f"""
            הסוגיה המקורית: {idea}
            השאלות שנשאלו: {st.session_state['diag_questions']}
            התשובות של אפי: {user_answers}
            המשתתפים: {st.session_state['participants']}
            
            בהתבסס על המידע האישי שסיפק אפי, צור דיון קצר והצע 2 כיווני פעולה מותאמים אישית.
            לכל כיוון פעולה פרט:
            1. אבני דרך (לו"ז ושלבים)
            2. תשומות (זמן, כסף, אנרגיה, כלים)
            3. תפוקות (מה ייחשב כהצלחה)
            
            הקפד על שורות קצרות, עברית רהוטה ויישור לימין.
            """
            final_result = call_gemini(final_prompt)
            st.markdown("---")
            st.markdown(f"<div style='direction: rtl; text-align: right;'>{final_result}</div>", unsafe_allow_html=True)

if st.button("🗑️ נקה דיון והתחל מחדש"):
    for key in ['diag_questions', 'step']:
        if key in st.session_state: del st.session_state[key]
    st.rerun()