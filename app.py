import streamlit as st
import google.generativeai as genai
import json
import re
import random

# הגדרות בסיסיות
st.set_page_config(page_title="קבינט אפי", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Assistant', sans-serif; direction: rtl; text-align: right; }
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; background-color: #f0f2f6; }
    .expert-box { background-color: #ffffff; padding: 10px; border: 1px solid #e5e7eb; border-radius: 10px; text-align: center; color: #000; }
    .question-card { background-color: #f9fafb; padding: 15px; border-radius: 10px; border-right: 5px solid #3b82f6; color: #000; margin-top: 15px; }
    </style>
    """, unsafe_allow_html=True)

# חיבור ל-API
if "GEMINI_KEY" not in st.secrets:
    st.error("Missing GEMINI_KEY in Secrets")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_KEY"])
MODEL_NAME = "gemini-1.5-flash"

# מאגר מומחים
POOL = {
    "פילוסופיה": ["סוקרטס", "אריסטו", "חנה ארנדט", "ניטשה", "מרקוס אורליוס", "קאנט"],
    "פסיכולוגיה": ["פרויד", "יונג", "ויקטור פראנקל", "כהנמן", "מאסלו", "אריך פרום"],
    "תרבות": ["מקלוהן", "אדוארד סעיד", "פוסטמן", "הררי", "מרגרט מיד", "פוקו"],
    "הפתעה": ["דה וינצ'י", "סטיב ג'ובס", "סון דזו", "איינשטיין", "שייקספיר", "קוקו שאנל"]
}

def get_cabinet():
    res = []
    for cat in ["פילוסופיה", "פסיכולוגיה", "תרבות", "הפתעה"]:
        for name in random.sample(POOL[cat], 2):
            res.append({"name": name, "cat": cat})
    return res

if 'cabinet' not in st.session_state:
    st.session_state.cabinet = get_cabinet()

# תצוגה
st.title("🏛️ קבינט המוחות של אפי")
st.write("חברי הקבינט הנוכחיים (8 מומחים):")

cols = st.columns(4)
for i, m in enumerate(st.session_state.cabinet):
    with cols[i % 4]:
        st.markdown(f"<div class='expert-box'><b>{m['name']}</b><br>{m['cat']}</div>", unsafe_allow_html=True)

if st.button("🔄 רענן הרכב קבינט"):
    st.session_state.cabinet = get_cabinet()
    for k in ['qs', 'report']: 
        if k in st.session_state: del st.session_state[k]
    st.rerun()

st.write("---")
idea = st.text_area("🖋️ מה מעסיק אותך?", height=100)

if st.button("🔍 התחל אבחון"):
    if idea:
        with st.spinner("מנסח שאלות..."):
            names = ", ".join([m['name'] for m in st.session_state.cabinet])
            prompt = f"נושא: {idea}. מומחים: {names}. נסח 6 שאלות אנושיות על רגשות ודפוסי חשיבה. בלי שמות מומחים. החזר רק JSON: " + '[{"q": "...", "options": ["1", "2", "3"]}]'
            try:
                model = genai.GenerativeModel(MODEL_NAME)
                resp = model.generate_content(prompt)
                match = re.search(r'\[.*\]', resp.text, re.DOTALL)
                if match:
                    st.session_state.qs = json.loads(match.group())
                    if 'report' in st.session_state: del st.session_state['report']
                    st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

if 'qs' in st.session_state:
    st.write("### 📝 שלב ההקשבה")
    ans_data = []
    for i, item in enumerate(st.session_state.qs):
        st.markdown(f"<div class='question-card'>{item['q']}</div>", unsafe_allow_html=True)
        sel = st.radio("בחר תשובה:", item['options'], key=f"r_{i}", label_visibility="collapsed")
        ans_data.append(f"Q: {item['q']} | A: {sel}")
    
    if st.button("🚀 הפק תובנות"):
        with st.spinner("מנתח..."):
            p2 = f"נושא: {idea}. תשובות: {ans_data}. כתוב 5 תובנות עומק פסיכולוגיות בשפה רכה."
            try:
                model = genai.GenerativeModel(MODEL_NAME)
                res = model.generate_content(p2)
                st.session_state.report = res.text
            except:
                st.error("שגיאה בהפקה")

if 'report' in st.session_state:
    st.write("---")
    st.success("📊 תובנות הקבינט:")
    st.markdown(st.session_state.report)