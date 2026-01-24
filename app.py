import streamlit as st
import google.generativeai as genai
import json
import re
import random

# --- 1. מנגנון גילוי מודלים אוטומטי (למניעת 404) ---
def get_available_model():
    if "GEMINI_KEY" not in st.secrets:
        st.error("Missing GEMINI_KEY in secrets")
        return None
    
    genai.configure(api_key=st.secrets["GEMINI_KEY"])
    
    try:
        # בדיקה אקטיבית איזה מודלים זמינים למפתח שלך
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # חיפוש מודל Flash גרסה 1.5, אם לא - Pro, אם לא - הראשון ברשימה
        for m_name in models:
            if '1.5-flash' in m_name: return m_name
        for m_name in models:
            if 'pro' in m_name: return m_name
            
        return models[0] if models else None
    except Exception as e:
        st.error(f"שגיאה בגישה ל-API: {e}")
        return None

# --- 2. עיצוב ממשק ---
st.set_page_config(page_title="קבינט המוחות", layout="wide")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Assistant', sans-serif; direction: rtl; text-align: right; background-color: #0f172a; }
    
    /* תיקון קריטי: טקסט שחור על רקע לבן בתיבות הקלט */
    .stTextArea textarea { color: #000000 !important; background-color: #ffffff !important; border: 2px solid #3b82f6 !important; font-size: 18px !important; }
    .stTextInput input { color: #000000 !important; background-color: #ffffff !important; }
    
    label, p, h1, h2, h3 { color: #f8fafc !important; }
    .expert-card { background-color: #ffffff; padding: 10px; border-radius: 8px; border: 2px solid #3b82f6; color: #1e293b !important; text-align: center; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 3. חילוץ JSON חסין ---
def robust_json_parser(text):
    try:
        match = re.search(r'\[\s*{.*}\s*\]', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except:
        pass
    return None

# --- 4. ניהול המצב (State) ---
if 'step' not in st.session_state: st.session_state.step = 'setup'
if 'history' not in st.session_state: st.session_state.history = []
if 'active_model' not in st.session_state: st.session_state.active_model = None

# --- שלב 0: הגדרת מקרה ---
if st.session_state.step == 'setup':
    st.title("🏛️ קבינט המוחות")
    
    if not st.session_state.active_model:
        st.session_state.active_model = get_available_model()
    
    if st.session_state.active_model:
        st.caption(f"מחובר למודל: {st.session_state.active_model}")
    
    cols = st.columns(4)
    cabinet = ["סוקרטס", "מרקוס אורליוס", "ויקטור פראנקל", "יונג", "מקלוהן", "הררי", "סטיב ג'ובס", "דה וינצ'י"]
    for i, name in enumerate(cabinet):
        # השורה שתוקנה: נוספו הגרשיים החסרים
        with cols[i % 4]: st.markdown(f"<div class='expert-card'>{name}</div>", unsafe_allow_html=True)
    
    st.write("---")
    idea = st.text_area("🖋️ תאר את המקרה לדיון:", height=150, placeholder="כתוב כאן את הדילמה שלך...")
    
    if st.button("🔍 התחל אבחון"):
        if st.session_state.active_model and idea:
            st.session_state.user_idea = idea
            with st.spinner("חברי הקבינט מגבשים שאלות..."):
                model = genai.GenerativeModel(st.session_state.active_model)
                prompt = (f"Topic: {idea}. Task: Generate 3 diagnostic questions in Hebrew. "
                          "Return ONLY a valid JSON array: [{'q':'text','options':['a','b','c']}]")
                try:
                    res = model.generate_content(prompt)
                    questions = robust_json_parser(res.text)
                    if questions:
                        st.session_state.questions = questions
                        st.session_state.step = 'diagnostic'
                        st.rerun()
                    else:
                        st.error("המודל החזיר תשובה בפורמט לא תקין. נסה ללחוץ שוב.")
                except Exception as e:
                    st.error(f"שגיאת מודל: {e}")

# --- שלב 1: אבחון מובנה ---
elif st.session_state.step == 'diagnostic':
    st.title("📝 שלב האבחון")
    st.write("השיבו על השאלות כדי לדייק את הדיון:")
    ans_list = []
    for i, item in enumerate(st.session_state.questions):
        ans = st.radio(f"**{item['q']}**", item['options'], key=f"q_{i}")
        ans_list.append(f"Q: {item['q']} | A: {ans}")
    
    if st.button("🚀 הצג למליאת הקבינט"):
        st.session_state.history.append({"role": "user", "content": f"מקרה: {st.session_state.user_idea}. אבחון: {ans_list}"})
        st.session_state.step = 'dialogue'
        st.rerun()

# --- שלב 2: הדיאלוג המרכזי ---
elif st.session_state.step == 'dialogue':
    st.title("💬 דיון בקבינט")
    
    # הצגת היסטוריית השיחה
    for msg in st.session_state.history:
        # הסתרת נתוני האבחון הגולמיים מהצ'אט
        if "מקרה:" in msg['content'] and len(st.session_state.history) > 1: continue
        with st.chat_message("assistant" if msg['role'] == "model" else "user"):
            st.write(msg['content'])

    # יצירת תגובה חדשה אם המשתמש שלח הודעה
    if not st.session_state.history or st.session_state.history[-1]['role'] == 'user':
        with st.chat_message("assistant"):
            with st.spinner("חבר קבינט מגבש תובנה..."):
                model = genai.GenerativeModel(st.session_state.active_model)
                expert = random.choice(["סוקרטס", "מרקוס אורליוס", "ויקטור פראנקל", "יונג", "סטיב ג'ובס"])
                instr = f"You are {expert}. Respond in Hebrew. Open with: '{expert} היה נוהג לומר...'. Be profound and brief."
                
                # המרה לפורמט Gemini
                hist = [{"role": m['role'], "parts": [m['content']]} for m in st.session_state.history]
                try:
                    res = model.generate_content([{"role": "user", "parts": [instr]}] + hist)
                    st.write(res.text)
                    st.session_state.history.append({"role": "model", "content": res.text})
                except Exception as e:
                    st.error(f"שגיאה בקבלת תגובה: {e}")

    if reply := st.chat_input("השב לקבינט..."):
        st.session_state.history.append({"role": "user", "content": reply})
        st.rerun()

    if st.sidebar.button("🔄 מקרה חדש"):
        st.session_state.step = 'setup'
        st.session_state.history = []
        st.rerun()