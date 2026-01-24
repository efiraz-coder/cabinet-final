import streamlit as st
import google.generativeai as genai
import json
import re
import random

# --- 1. API ---
def get_working_model():
    if "GEMINI_KEY" not in st.secrets:
        st.error("Missing GEMINI_KEY")
        return None
    genai.configure(api_key=st.secrets["GEMINI_KEY"])
    try:
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for pref in ['models/gemini-1.5-flash', 'models/gemini-1.5-pro']:
            if pref in available: return pref
        return available[0] if available else None
    except: return None

# --- 2. עיצוב ---
st.set_page_config(page_title="קבינט המוחות", layout="wide")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Assistant', sans-serif; direction: rtl; text-align: right; }
    .expert-box { 
        background-color: #f1f5f9; padding: 10px; border: 1px solid #cbd5e1; 
        border-radius: 10px; text-align: center; font-weight: bold; font-size: 0.9em;
    }
    .chat-bubble { 
        background: #ffffff; padding: 25px; border-radius: 15px; 
        border-right: 6px solid #3b82f6; color: #1e293b; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. ניהול המצב ---
if 'step' not in st.session_state: st.session_state.step = 'setup'
if 'history' not in st.session_state: st.session_state.history = []

if 'cabinet' not in st.session_state:
    pool = {"פילוסופיה": ["סוקרטס", "מרקוס אורליוס"], "פסיכולוגיה": ["ויקטור פראנקל", "יונג"], 
            "תרבות": ["מקלוהן", "הררי"], "הפתעה": ["סטיב ג'ובס", "דה וינצ'י"]}
    st.session_state.cabinet = [{"name": n, "cat": c} for c, names in pool.items() for n in names]

# --- שלב 0: הגדרה ---
if st.session_state.step == 'setup':
    st.title("🏛️ קבינט המוחות")
    cols = st.columns(4)
    for i, m in enumerate(st.session_state.cabinet):
        with cols[i % 4]: 
            st.markdown(f"<div class='expert-box'>{m['name']}</div>", unsafe_allow_html=True)
    
    st.write("---")
    idea = st.text_area("🖋️ מה על ליבך?", height=100)
    personal_q = st.text_input("🎯 שאלה ספציפית לקבינט?")

    if st.button("🔍 בואו נתחיל"):
        model_name = get_working_model()
        if model_name and idea:
            st.session_state.working_model = model_name
            st.session_state.user_idea = idea
            with st.spinner("הקבינט מגבש שאלות..."):
                model = genai.GenerativeModel(model_name)
                json_format = '[{"q": "שאלה", "options": ["1", "2", "3"]}]'
                prompt = f"Topic: {idea}. Generate 3 diagnostic questions in Hebrew. Return ONLY JSON: {json_format}"
                try:
                    res = model.generate_content(prompt)
                    json_text = re.search(r'\[.*\]', res.text, re.DOTALL).group()
                    st.session_state.questions = json.loads(json_text)
                    st.session_state.step = 'diagnostic'
                    st.rerun()
                except: st.error("נסה שוב.")

# --- שלב 1: אבחון ---
elif st.session_state.step == 'diagnostic':
    st.title("📝 שלב ההקשבה")
    ans_list = []
    for i, item in enumerate(st.session_state.questions):
        ans = st.radio(item['q'], item['options'], key=f"ans_{i}")
        ans_list.append(f"Q: {item['q']} | A: {ans}")
    
    if st.button("🚀 שלח תשובות"):
        st.session_state.history.append({"role": "user", "parts": [f"המקרה: {st.session_state.user_idea}. תשובות: {ans_list}"]})
        st.session_state.step = 'dialogue'
        st.rerun()

# --- שלב 2: דיאלוג (ממוקד חבר אחד) ---
elif st.session_state.step == 'dialogue':
    st.title("💬 דיאלוג ממוקד")
    for msg in st.session_state.history:
        if msg['role'] == 'model':
            st.markdown(f"<div class='chat-bubble'>{msg['parts'][0]}</div>", unsafe_allow_html=True)
        elif 'המקרה:' not in msg['parts'][0]:
            st.info(f"👉 **אתה:** {msg['parts'][0]}")

    if st.session_state.history[-1]['role'] == 'user':
        with st.spinner("חבר קבינט נבחר מגיב..."):
            # בחירת חבר קבינט אחד אקראי לתגובה
            expert = random.choice(st.session_state.cabinet)['name']
            instr = (
                f"You are {expert} from the council. Respond in Hebrew. "
                f"You must use the exact phrase: '{expert} היה נוהג לומר...' followed by your core insight. "
                "Keep it concise, sharp, and focused only on your perspective. "
                "Structure: 1. Sharp reflection. 2. The quote. 3. One action item."
            )
            model = genai.GenerativeModel(st.session_state.working_model)
            res = model.generate_content([{"role": "user", "parts": [instr]}] + st.session_state.history)
            st.session_state.history.append({"role": "model", "parts": [res.text]})
            st.rerun()

    user_reply = st.chat_input("המשך דיאלוג...")
    if user_reply:
        st.session_state.history.append({"role": "user", "parts": [user_reply]})
        st.rerun()