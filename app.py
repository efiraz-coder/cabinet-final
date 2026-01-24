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
    try:
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for pref in ['models/gemini-1.5-flash', 'models/gemini-1.5-pro']:
            if pref in available: return pref
        return available[0] if available else None
    except: return None

# --- 2. עיצוב מתוקן (טקסט כהה על רקע בהיר) ---
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
        padding: 15px; 
        border: 2px solid #3b82f6; 
        border-radius: 12px; 
        text-align: center; 
        color: #1e293b !important; 
        font-weight: bold;
        margin-bottom: 10px;
    }
    .chat-bubble { 
        background: #f8fafc; 
        padding: 25px; 
        border-radius: 15px; 
        border-right: 8px solid #3b82f6; 
        color: #1e293b; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
        margin-bottom: 20px;
        line-height: 1.6;
    }
    /* תיקון צבעי טקסט בטפסים */
    label, p, span { color: #f8fafc !important; }
    .stTextArea textarea { color: #1e293b !important; }
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
        {"name": "סטיב ג'ובס", "cat": "חדשנות"}, {"name": "דה וינצ'י", "cat": "אמנות והנדסה"}
    ]

# --- שלב 0: הצגת הקבינט והזנת נושא ---
if st.session_state.step == 'setup':
    st.title("🏛️ קבינט המוחות")
    st.write("חברי הקבינט המייעצים לך:")
    cols = st.columns(4)
    for i, m in enumerate(st.session_state.cabinet):
        with cols[i % 4]: 
            st.markdown(f"<div class='expert-box'>{m['name']}<br><small style='color: #64748b;'>{m['cat']}</small></div>", unsafe_allow_html=True)
    
    st.write("---")
    idea = st.text_area("🖋️ תאר את המצב או הקונפליקט:", height=150, placeholder="לדוגמה: הקושי להתמודד עם חוסר הסבלנות בבית...")
    
    if st.button("🔍 שלח לבחינת הקבינט"):
        model_name = get_working_model()
        if model_name and idea:
            st.session_state.working_model = model_name
            st.session_state.user_idea = idea
            with st.spinner("הקבינט מגבש שאלות אבחון..."):
                model = genai.GenerativeModel(model_name)
                # הקבינט שואל, לא המשתמש
                prompt = (
                    f"המקרה: {idea}. אתה קבינט המוחות. "
                    f"נסח 4 שאלות אבחון עמוקות בעברית שיעזרו לאדם להבין את שורש הבעיה. "
                    f"החזר אך ורק פורמט JSON תקני כזה: "
                    f'[{{"q": "שאלה", "options": ["אפשרות א", "אפשרות ב", "אפשרות ג"]}}]'
                )
                try:
                    res = model.generate_content(prompt)
                    json_text = re.search(r'\[.*\]', res.text, re.DOTALL).group()
                    st.session_state.questions = json.loads(json_text)
                    st.session_state.step = 'diagnostic'
                    st.rerun()
                except: st.error("חלה שגיאה בעיבוד. נסה שוב.")

# --- שלב 1: שאלות הקבינט ---
elif st.session_state.step == 'diagnostic':
    st.title("📝 שלב האבחון")
    st.write("הקבינט מבקש להבין טוב יותר:")
    ans_list = []
    for i, item in enumerate(st.session_state.questions):
        ans = st.radio(item['q'], item['options'], key=f"ans_{i}")
        ans_list.append(f"שאלה: {item['q']} | תשובה: {ans}")
    
    if st.button("🚀 המשך לדיאלוג עם הקבינט"):
        st.session_state.history.append({"role": "user", "parts": [f"המקרה: {st.session_state.user_idea}. אבחון: {ans_list}"]})
        st.session_state.step = 'dialogue'
        st.rerun()

# --- שלב 2: תגובת חבר קבינט נבחר ---
elif st.session_state.step == 'dialogue':
    st.title("💬 דבר הקבינט")
    
    for msg in st.session_state.history:
        if msg['role'] == 'model':
            st.markdown(f"<div class='chat-bubble'>{msg['parts'][0]}</div>", unsafe_allow_html=True)
        elif 'המקרה:' not in msg['parts'][0]:
            st.write(f"🟢 **אתה:** {msg['parts'][0]}")

    if st.session_state.history[-1]['role'] == 'user':
        with st.spinner("אחד מחברי הקבינט מגבש תובנה..."):
            expert = random.choice(st.session_state.cabinet)['name']
            instr = (
                f"אתה {expert}. ענה בעברית בצורה חדה ומעמיקה. "
                f"עליך לפתוח בדיוק כך: '{expert} היה נוהג לומר...' ולאחר מכן להציג את התובנה שלך. "
                f"מבנה התשובה: 1. שיקוף המצב. 2. הציטוט והתובנה. 3. שאלה מצפנית אחת. "
                f"צמצם את התגובה למינימום ההכרחי והעוצמתי."
            )
            model = genai.GenerativeModel(st.session_state.working_model)
            res = model.generate_content([{"role": "user", "parts": [instr]}] + st.session_state.history)
            st.session_state.history.append({"role": "model", "parts": [res.text]})
            st.rerun()

    user_reply = st.chat_input("השב לחבר הקבינט...")
    if user_reply:
        st.session_state.history.append({"role": "user", "parts": [user_reply]})
        st.rerun()