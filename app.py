import streamlit as st
import google.generativeai as genai
import json
import re
import random

# הגדרות דף
st.set_page_config(page_title="קבינט המוחות של אפי", layout="wide")

# ניקוי ממשק
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Assistant', sans-serif; direction: rtl; text-align: right; }
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; background-color: #f0f2f6; }
    .expert-box { background-color: #ffffff; padding: 10px; border: 1px solid #e5e7eb; border-radius: 10px; text-align: center; color: #000; }
    </style>
    """, unsafe_allow_html=True)

# פונקציה למציאת המודל הראשון שבאמת עובד אצלך
def get_working_model():
    if "GEMINI_KEY" not in st.secrets:
        st.error("Missing API Key")
        return None
    
    genai.configure(api_key=st.secrets["GEMINI_KEY"])
    try:
        # סריקת כל המודלים שזמינים למפתח שלך
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if not available:
            return None
        # עדיפות למודלים המהירים
        for pref in ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']:
            if pref in available:
                return pref
        return available[0]
    except Exception as e:
        st.error(f"Error scanning models: {e}")
        return None

# אתחול קבינט (8 חברים: 2 מכל סוג)
if 'cabinet' not in st.session_state:
    pool = {
        "פילוסופיה": ["סוקרטס", "אריסטו", "חנה ארנדט", "ניטשה", "מרקוס אורליוס"],
        "פסיכולוגיה": ["פרויד", "יונג", "ויקטור פראנקל", "כהנמן", "מאסלו"],
        "תרבות": ["מקלוהן", "אדוארד סעיד", "הררי", "פוסטמן", "מרגרט מיד"],
        "הפתעה": ["דה וינצ'י", "סטיב ג'ובס", "סון דזו", "איינשטיין", "שייקספיר"]
    }
    cab = []
    for cat, names in pool.items():
        selected = random.sample(names, 2)
        for n in selected:
            cab.append({"name": n, "cat": cat})
    st.session_state.cabinet = cab

# ממשק
st.title("🏛️ קבינט המוחות של אפי")

# הצגת המומחים
cols = st.columns(4)
for i, m in enumerate(st.session_state.cabinet):
    with cols[i % 4]:
        st.markdown(f"<div class='expert-box'><b>{m['name']}</b><br>{m['cat']}</div>", unsafe_allow_html=True)

if st.button("🔄 רענן הרכב (החלפת 4 מומחים)"):
    # מחליף אחד מכל קטגוריה
    for i in [0, 2, 4, 6]:
        cat = st.session_state.cabinet[i]['cat']
        st.session_state.cabinet[i]['name'] = random.choice(pool[cat])
    st.rerun()

st.write("---")
idea = st.text_area("🖋️ מה על ליבך היום?", height=100)

if st.button("🔍 התחל אבחון"):
    if idea:
        with st.spinner("הקבינט מתחבר..."):
            model_name = get_working_model()
            if not model_name:
                st.error("לא נמצא מודל פעיל. בדוק את המפתח ב-AI Studio.")
            else:
                model = genai.GenerativeModel(model_name)
                prompt = f"נושא: {idea}. נסח 6 שאלות אנושיות על רגשות ומחשבות. החזר רק JSON תקין: " + '[{"q": "...", "options": ["1", "2", "3"]}]'
                try:
                    res = model.generate_content(prompt)
                    match = re.search(r'\[.*\]', res.text, re.DOTALL)
                    if match:
                        st.session_state.qs = json.loads(match.group())
                        st.rerun()
                except Exception as e:
                    st.error(f"שגיאה בהפעלת {model_name}: {e}")

if 'qs' in st.session_state:
    st.write("### 📝 שלב ההקשבה")
    ans_data = []
    for i, item in enumerate(st.session_state.qs):
        st.write(f"**{item['q']}**")
        sel = st.radio("בחר תשובה:", item['options'], key=f"r_{i}", label_visibility="collapsed")
        ans_data.append(f"Q: {item['q']} | A: {sel}")
    
    if st.button("🚀 הפק תובנות"):
        model_name = get_working_model()
        model = genai.GenerativeModel(model_name)
        report = model.generate_content(f"נושא: {idea}. תשובות: {ans_data}. סכם ב-5 תובנות רכות.")
        st.session_state.report = report.text

if 'report' in st.session_state:
    st.success("📊 תובנות הקבינט:")
    st.markdown(st.session_state.report)