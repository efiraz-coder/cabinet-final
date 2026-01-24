import streamlit as st
import google.generativeai as genai
import json
import re
import random

# --- 1. הגדרות API ---
def get_working_model():
    if "GEMINI_KEY" not in st.secrets:
        st.error("Missing GEMINI_KEY in secrets")
        return None
    genai.configure(api_key=st.secrets["GEMINI_KEY"])
    return 'models/gemini-1.5-flash'

# --- 2. עיצוב ממשק ---
st.set_page_config(page_title="קבינט המוחות", layout="wide")
st.markdown("""
    <style>
    @import url('[https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap](https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap)');
    html, body, [class*="st-"] { font-family: 'Assistant', sans-serif; direction: rtl; text-align: right; background-color: #0f172a; }
    .stTextArea textarea { color: #000000 !important; background-color: #ffffff !important; font-size: 18px !important; }
    .expert-box { background-color: #ffffff; padding: 10px; border: 2px solid #3b82f6; border-radius: 8px; text-align: center; color: #1e293b !important; font-weight: bold; }
    label, p, h1, h2 { color: #f8fafc !important; }
    </style>
""", unsafe_allow_html=True)

# --- 3. ניהול המצב ---
if 'step' not in st.session_state: st.session_state.step = 'setup'
if 'history' not in st.session_state: st.session_state.history = []

# --- פונקציית חילוץ JSON חסינה ---
def robust_json_parser(text):
    try:
        # מחפש את המערך הראשון שמתחיל ב-[ ומסתיים ב-]
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            json_str = match.group()
            return json.loads(json_str)
    except Exception as e:
        st.error(f"Error parsing: {e}")
    return None

# --- שלב 0: מסך פתיחה ---
if st.session_state.step == 'setup':
    st.title("🏛️ קבינט המוחות")
    st.write("תאר את הדילמה שלך והקבינט יתחיל באבחון:")
    
    idea = st.text_area("", height=150, placeholder="למשל: אני מתלבט אם לעזוב עבודה יציבה לטובת סטארטאפ...")
    
    if st.button("🔍 התחל אבחון"):
        model_id = get_working_model()
        if model_id and idea:
            st.session_state.user_idea = idea
            with st.spinner("חברי הקבינט בונים שאלות אבחון..."):
                model = genai.GenerativeModel(model_id)
                # הנחיה הרבה יותר נוקשה למודל
                prompt = (
                    f"Topic: {idea}. Task: Generate 3 diagnostic questions in Hebrew. "
                    "Return ONLY a plain JSON array of objects. No markdown, no comments. "
                    "Format: [{'q': 'question', 'options': ['a', 'b', 'c']}]"
                )
                response = model.generate_content(prompt)
                questions = robust_json_parser(response.text)
                
                if questions:
                    st.session_state.questions = questions
                    st.session_state.step = 'diagnostic'
                    st.rerun()
                else:
                    st.error("המודל החזיר תשובה בפורמט לא תקין. נסה שוב.")

# --- שלב 1: שאלות אבחון ---
elif st.session_state.step == 'diagnostic':
    st.title("📝 שלב האבחון")
    ans_list = []
    for i, item in enumerate(st.session_state.questions):
        ans = st.radio(f"**{item['q']}**", item['options'], key=f"q_{i}")
        ans_list.append(f"Q: {item['q']} | A: {ans}")
    
    if st.button("🚀 המשך לדיון במליאה"):
        st.session_state.history.append({"role": "user", "content": f"מקרה: {st.session_state.user_idea}. תשובות: {ans_list}"})
        st.session_state.step = 'dialogue'
        st.rerun()

# --- שלב 2: הדיאלוג ---
elif st.session_state.step == 'dialogue':
    st.title("💬 דיון בקבינט")
    
    for msg in st.session_state.history:
        if "מקרה:" in msg['content'] and len(st.session_state.history) > 1: continue
        with st.chat_message("assistant" if msg['role'] == "model" else "user"):
            st.write(msg['content'])

    if st.session_state.history[-1]['role'] == 'user':
        with st.chat_message("assistant"):
            with st.spinner("חבר קבינט מגבש תגובה..."):
                experts = ["סוקרטס", "מרקוס אורליוס", "ויקטור פראנקל", "סטיב ג'ובס"]
                expert = random.choice(experts)
                model = genai.GenerativeModel(get_working_model())
                
                instr = f"You are {expert}. Respond in Hebrew. Open with: '{expert} היה נוהג לומר...'. Be deep and brief."
                gemini_hist = [{"role": m['role'], "parts": [m['content']]} for m in st.session_state.history]
                
                res = model.generate_content([{"role": "user", "parts": [instr]}] + gemini_hist)
                st.write(res.text)
                st.session_state.history.append({"role": "model", "content": res.text})

    if reply := st.chat_input("השב לקבינט..."):
        st.session_state.history.append({"role": "user", "content": reply})
        st.rerun()