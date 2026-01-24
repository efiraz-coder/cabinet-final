import streamlit as st
import google.generativeai as genai
import json
import re
import random

# --- 1. מנוע AI ---
def get_model():
    if "GEMINI_KEY" not in st.secrets:
        st.error("Missing GEMINI_KEY in secrets!")
        return None
    genai.configure(api_key=st.secrets["GEMINI_KEY"])
    return genai.GenerativeModel('models/gemini-1.5-flash')

# --- 2. עיצוב (CSS) - הבטחת קריאות מקסימלית ---
st.set_page_config(page_title="קבינט המוחות", layout="wide")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Assistant', sans-serif; direction: rtl; text-align: right; }
    
    /* פתרון בעיית הניגודיות - טקסט שחור בתיבות לבנות */
    .stTextArea textarea { 
        color: #000000 !important; 
        background-color: #ffffff !important; 
        border: 2px solid #3b82f6 !important;
    }
    
    /* שיפור נראות בועות הצ'אט */
    .stChatMessage { background-color: rgba(255, 255, 255, 0.05); border-radius: 10px; margin-bottom: 10px; }
    
    .expert-card { 
        background-color: #ffffff; padding: 10px; border-radius: 8px; 
        border: 2px solid #3b82f6; color: #1e293b; text-align: center; font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. ניהול המצב (State) ---
if 'step' not in st.session_state: st.session_state.step = 'setup'
if 'history' not in st.session_state: st.session_state.history = []
if 'cabinet' not in st.session_state:
    st.session_state.cabinet = [
        {"name": "סוקרטס"}, {"name": "מרקוס אורליוס"}, {"name": "ויקטור פראנקל"}, 
        {"name": "יונג"}, {"name": "מקלוהן"}, {"name": "הררי"}, 
        {"name": "סטיב ג'ובס"}, {"name": "דה וינצ'י"}
    ]

# --- שלב 0: הקמה ---
if st.session_state.step == 'setup':
    st.title("🏛️ קבינט המוחות")
    cols = st.columns(4)
    for i, m in enumerate(st.session_state.cabinet):
        with cols[i % 4]: st.markdown(f"<div class='expert-card'>{m['name']}</div>", unsafe_allow_html=True)
    
    st.write("---")
    idea = st.text_area("🖋️ תאר את המקרה לדיון:", height=150)
    
    if st.button("🔍 התחל אבחון קבינט"):
        model = get_model()
        if model and idea:
            st.session_state.user_idea = idea
            with st.spinner("מגבש שאלות..."):
                prompt = f"Topic: {idea[:500]}. Task: 3 diag questions in Hebrew. Return ONLY JSON array: [{{'q':'text','options':['a','b','c']}}]"
                try:
                    res = model.generate_content(prompt)
                    json_str = re.search(r'\[.*\]', res.text, re.DOTALL).group()
                    st.session_state.questions = json.loads(json_str)
                    st.session_state.step = 'diagnostic'
                    st.rerun()
                except: st.error("חלה שגיאה בעיבוד. נסה שוב.")

# --- שלב 1: אבחון ---
elif st.session_state.step == 'diagnostic':
    st.title("📝 אבחון")
    ans_list = []
    for i, item in enumerate(st.session_state.questions):
        ans = st.radio(item['q'], item['options'], key=f"q_{i}")
        ans_list.append(f"Q: {item['q']} | A: {ans}")
    
    if st.button("🚀 שלח לקבינט"):
        st.session_state.history.append({"role": "user", "content": f"מקרה: {st.session_state.user_idea}. אבחון: {ans_list}"})
        st.session_state.step = 'dialogue'
        st.rerun()

# --- שלב 2: צ'אט ---
elif st.session_state.step == 'dialogue':
    st.title("💬 דיון")
    
    for msg in st.session_state.history:
        if "מקרה:" in msg['content'] and len(st.session_state.history) > 1: continue
        with st.chat_message("assistant" if msg['role'] == "model" else "user"):
            st.write(msg['content'])

    # יצירת תגובה רק אם המשתמש שלח משהו
    if not st.session_state.history or st.session_state.history[-1]['role'] == 'user':
        with st.chat_message("assistant"):
            with st.spinner("חבר קבינט מגיב..."):
                expert = random.choice(st.session_state.cabinet)['name']
                instr = f"You are {expert}. Respond in Hebrew. Open with: '{expert} היה נוהג לומר...'. Be brief."
                model = get_model()
                # הכנת היסטוריה ל-Gemini
                hist = [{"role": m['role'], "parts": [m['content']]} for m in st.session_state.history]
                res = model.generate_content([{"role": "user", "parts": [instr]}] + hist)
                st.write(res.text)
                st.session_state.history.append({"role": "model", "content": res.text})

    if reply := st.chat_input("השב..."):
        st.session_state.history.append({"role": "user", "content": reply})
        st.rerun()