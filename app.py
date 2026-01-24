import streamlit as st
import google.generativeai as genai
import json
import re
import random

# --- 1. הגדרות API ---
def get_working_model():
    if "GEMINI_KEY" not in st.secrets:
        st.error("Missing GEMINI_KEY")
        return None
    genai.configure(api_key=st.secrets["GEMINI_KEY"])
    return 'models/gemini-1.5-flash' # שימוש ב-Flash למהירות מקסימלית

# --- 2. עיצוב (כהה עם תיבות בהירות וקריאות) ---
st.set_page_config(page_title="קבינט המוחות", layout="wide")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Assistant', sans-serif; direction: rtl; text-align: right; background-color: #0f172a; }
    .expert-box { 
        background-color: #ffffff; padding: 12px; border: 2px solid #3b82f6; 
        border-radius: 10px; text-align: center; color: #1e293b !important; 
        font-weight: bold; margin-bottom: 10px;
    }
    .chat-bubble { 
        background: #f8fafc; padding: 20px; border-radius: 15px; 
        border-right: 8px solid #3b82f6; color: #1e293b; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px;
    }
    label, p, span, h1 { color: #f8fafc !important; }
    .stTextArea textarea { color: #1e293b !important; background-color: #ffffff !important; }
    </style>
""", unsafe_allow_html=True)

# --- 3. ניהול המצב ---
if 'step' not in st.session_state: st.session_state.step = 'setup'
if 'history' not in st.session_state: st.session_state.history = []
if 'cabinet' not in st.session_state:
    st.session_state.cabinet = [
        {"name": "סוקרטס", "cat": "פילוסופיה"}, {"name": "מרקוס אורליוס", "cat": "פילוסופיה"},
        {"name": "ויקטור פראנקל", "cat": "פסיכולוגיה"}, {"name": "יונג", "cat": "פסיכולוגיה"},
        {"name": "מקלוהן", "cat": "תרבות"}, {"name": "הררי", "cat": "תרבות"},
        {"name": "סטיב ג'ובס", "cat": "חדשנות"}, {"name": "דה וינצ'י", "cat": "הנדסה"}
    ]

# --- שלב 0: הגדרה ---
if st.session_state.step == 'setup':
    st.title("🏛️ קבינט המוחות")
    cols = st.columns(4)
    for i, m in enumerate(st.session_state.cabinet):
        with cols[i % 4]: st.markdown(f"<div class='expert-box'>{m['name']}<br><small style='color: #475569;'>{m['cat']}</small></div>", unsafe_allow_html=True)
    
    st.write("---")
    idea = st.text_area("🖋️ תאר את המצב:", height=120)
    
    if st.button("🔍 שלח לבחינת הקבינט"):
        model_name = get_working_model()
        if model_name and idea:
            st.session_state.working_model = model_name
            st.session_state.user_idea = idea
            with st.spinner("הקבינט מגבש שאלות..."):
                model = genai.GenerativeModel(model_name)
                # פורמט קצר ומהיר יותר
                prompt = f"Topic: {idea}. Generate 3 diag questions in Hebrew. Return ONLY JSON list: [{{'q':'text', 'options':['a','b','c']}}]"
                try:
                    res = model.generate_content(prompt)
                    json_text = re.search(r'\[.*\]', res.text, re.DOTALL).group().replace("'", '"')
                    st.session_state.questions = json.loads(json_text)
                    st.session_state.step = 'diagnostic'
                    st.rerun()
                except: st.error("חלה שגיאה מהירה. נסה שוב.")

# --- שלב 1: אבחון ---
elif st.session_state.step == 'diagnostic':
    st.title("📝 אבחון הקבינט")
    ans_list = []
    for i, item in enumerate(st.session_state.questions):
        ans = st.radio(item['q'], item['options'], key=f"ans_{i}")
        ans_list.append(f"Q: {item['q']} | A: {ans}")
    
    if st.button("🚀 המשך לדיאלוג"):
        st.session_state.history.append({"role": "user", "parts": [f"Case: {st.session_state.user_idea}. Answers: {ans_list}"]})
        st.session_state.step = 'dialogue'
        st.rerun()

# --- שלב 2: דיאלוג ---
elif st.session_state.step == 'dialogue':
    st.title("💬 דבר הקבינט")
    for msg in st.session_state.history:
        if msg['role'] == 'model':
            st.markdown(f"<div class='chat-bubble'>{msg['parts'][0]}</div>", unsafe_allow_html=True)
        elif 'Case:' not in msg['parts'][0]:
            st.write(f"🔵 **אתה:** {msg['parts'][0]}")

    if st.session_state.history[-1]['role'] == 'user':
        with st.spinner("מעבד תובנה..."):
            expert = random.choice(st.session_state.cabinet)['name']
            instr = f"You are {expert}. Open with '{expert} היה נוהג לומר...'. Be brief, sharp, Hebrew."
            model = genai.GenerativeModel(st.session_state.working_model)
            res = model.generate_content([{"role": "user", "parts": [instr]}] + st.session_state.history)
            st.session_state.history.append({"role": "model", "parts": [res.text]})
            st.rerun()

    user_reply = st.chat_input("השב לקבינט...")
    if user_reply:
        st.session_state.history.append({"role": "user", "parts": [user_reply]})
        st.rerun()