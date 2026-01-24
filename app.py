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

# --- 2. עיצוב UI חסין (טקסט שחור בתיבות כתיבה) ---
st.set_page_config(page_title="קבינט המוחות", layout="wide")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');
    html, body, [class*="st-"] { 
        font-family: 'Assistant', sans-serif; 
        direction: rtl; 
        text-align: right; 
        background-color: #0f172a; 
    }
    .expert-box { 
        background-color: #ffffff; 
        padding: 10px; 
        border: 2px solid #3b82f6; 
        border-radius: 8px; 
        text-align: center; 
        color: #1e293b !important; 
        font-weight: bold;
    }
    .chat-bubble { 
        background: #f8fafc; 
        padding: 20px; 
        border-radius: 12px; 
        border-right: 8px solid #3b82f6; 
        color: #1e293b; 
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    /* תיקון קריטי לניגודיות טקסט */
    .stTextArea textarea {
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    label, p, h1, h2, span { color: #f8fafc !important; }
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

# --- שלב 0: פתיחה והזנת מקרה ---
if st.session_state.step == 'setup':
    st.title("🏛️ קבינט המוחות")
    cols = st.columns(4)
    for i, m in enumerate(st.session_state.cabinet):
        with cols[i % 4]: 
            st.markdown(f"<div class='expert-box'>{m['name']}</div>", unsafe_allow_html=True)
    
    st.write("---")
    idea = st.text_area("🖋️ תאר את המצב שבפנינו:", height=150)
    
    if st.button("🔍 הערכת קבינט"):
        model_name = get_working_model()
        if model_name and idea:
            st.session_state.working_model = model_name
            st.session_state.user_idea = idea
            with st.spinner("הקבינט מגבש שאלות אבחון..."):
                model = genai.GenerativeModel(model_name)
                prompt = (
                    f"Subject: {idea}. Generate 3 deep diagnostic questions in Hebrew. "
                    "Return ONLY a JSON array: [{'q': 'text', 'options': ['a', 'b', 'c']}]."
                )
                try:
                    res = model.generate_content(prompt)
                    clean_text = res.text.replace("```json", "").replace("```", "").strip()
                    st.session_state.questions = json.loads(clean_text)
                    st.session_state.step = 'diagnostic'
                    st.rerun()
                except:
                    st.error("הקבינט לא הצליח לעבד את השאלות. נסה שוב.")

# --- שלב 1: אבחון הקבינט ---
elif st.session_state.step == 'diagnostic':
    st.title("📝 אבחון הקבינט")
    ans_list = []
    for i, item in enumerate(st.session_state.questions):
        st.write(f"**{item['q']}**")
        ans = st.radio("בחר תשובה:", item['options'], key=f"ans_{i}", label_visibility="collapsed")
        ans_list.append(f"Q: {item['q']} | A: {ans}")
    
    if st.button("🚀 קבלת תובנה"):
        st.session_state.history.append({"role": "user", "parts": [f"המקרה: {st.session_state.user_idea}. אבחון: {ans_list}"]})
        st.session_state.step = 'dialogue'
        st.rerun()

# --- שלב 2: דיאלוג ממוקד ---
elif st.session_state.step == 'dialogue':
    st.title("💬 דבר הקבינט