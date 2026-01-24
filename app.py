import streamlit as st
import google.generativeai as genai
import json
import re
import random

# --- 1. הגדרות API מיוצבות ---
def setup_model():
    if "GEMINI_KEY" not in st.secrets:
        st.error("Missing GEMINI_KEY in secrets")
        return None
    genai.configure(api_key=st.secrets["GEMINI_KEY"])
    
    # ניסיון להשתמש בגרסה היציבה ביותר
    # אם gemini-1.5-flash לא נמצא, המערכת תנסה לעבור ל-gemini-pro
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        # בדיקה קצרה אם המודל מגיב (אופציונלי, כאן נגדיר רק את השם)
        return model
    except:
        try:
            return genai.GenerativeModel('gemini-pro')
        except Exception as e:
            st.error(f"לא ניתן למצוא מודל נתמך: {e}")
            return None

# --- 2. עיצוב ממשק ---
st.set_page_config(page_title="קבינט המוחות", layout="wide")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Assistant', sans-serif; direction: rtl; text-align: right; background-color: #0f172a; }
    .stTextArea textarea { color: #000000 !important; background-color: #ffffff !important; border: 2px solid #3b82f6 !important; }
    label, p, h1, h2 { color: #f8fafc !important; }
    </style>
""", unsafe_allow_html=True)

# --- 3. פונקציית עזר לחילוץ JSON ---
def extract_json(text):
    try:
        # מחפש את המערך בתוך הטקסט
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except:
        pass
    return None

# --- 4. ניהול המצב ---
if 'step' not in st.session_state: st.session_state.step = 'setup'
if 'history' not in st.session_state: st.session_state.history = []

# --- שלב 0: מסך פתיחה ---
if st.session_state.step == 'setup':
    st.title("🏛️ קבינט המוחות")
    idea = st.text_area("🖋️ תאר את הדילמה שלך:", height=150)
    
    if st.button("🔍 התחל אבחון"):
        model = setup_model()
        if model and idea:
            st.session_state.user_idea = idea
            with st.spinner("הקבינט מגבש שאלות..."):
                prompt = (
                    f"Topic: {idea}. Task: 3 diagnostic questions in Hebrew. "
                    "Return ONLY a plain JSON array: [{'q':'question', 'options':['a','b','c']}]"
                )
                try:
                    response = model.generate_content(prompt)
                    questions = extract_json(response.text)
                    if questions:
                        st.session_state.questions = questions
                        st.session_state.step = 'diagnostic'
                        st.rerun()
                    else:
                        st.warning("הקבינט לא הצליח לייצר שאלות בפורמט הנכון. נסה שוב.")
                except Exception as e:
                    st.error(f"שגיאת תקשורת עם המודל: {e}")

# --- שלב 1: אבחון ---
elif st.session_state.step == 'diagnostic':
    st.title("📝 אבחון")
    ans_list = []
    for i, item in enumerate(st.session_state.questions):
        ans = st.radio(f"**{item['q']}**", item['options'], key=f"q_{i}")
        ans_list.append(f"Q: {item['q']} | A: {ans}")
    
    if st.button("🚀 המשך לדיון"):
        st.session_state.history.append({"role": "user", "content": f"מקרה: {st.session_state.user_idea}. אבחון: {ans_list}"})
        st.session_state.step = 'dialogue'
        st.rerun()

# --- שלב 2: דיאלוג ---
elif st.session_state.step == 'dialogue':
    st.title("💬 דיון בקבינט")
    
    for msg in st.session_state.history:
        if "מקרה:" in msg['content'] and len(st.session_state.history) > 1: continue
        with st.chat_message("assistant" if msg['role'] == "model" else "user"):
            st.write(msg['content'])

    if not st.session_state.history or st.session_state.history[-1]['role'] == 'user':
        with st.chat_message("assistant"):
            with st.spinner("חבר קבינט משיב..."):
                model = setup_model()
                expert = random.choice(["סוקרטס", "מרקוס אורליוס", "ויקטור פראנקל", "יונג"])
                instr = f"You are {expert}. Respond in Hebrew. Open with: '{expert} היה נוהג לומר...'. Be deep and brief."
                
                # בניית היסטוריה תקינה
                gemini_hist = [{"role": m['role'], "parts": [m['content']]} for m in st.session_state.history]
                try:
                    res = model.generate_content([{"role": "user", "parts": [instr]}] + gemini_hist)
                    st.write(res.text)
                    st.session_state.history.append({"role": "model", "content": res.text})
                except Exception as e:
                    st.error(f"שגיאה בקבלת תגובה: {e}")

    if reply := st.chat_input("השב..."):
        st.session_state.history.append({"role": "user", "content": reply})
        st.rerun()