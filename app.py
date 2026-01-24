import streamlit as st
import google.generativeai as genai
import json
import re
import random

# --- 1. מנגנון API חסין ---
def get_working_model():
    if "GEMINI_KEY" not in st.secrets:
        return None
    genai.configure(api_key=st.secrets["GEMINI_KEY"])
    try:
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for pref in ['models/gemini-1.5-flash', 'models/gemini-1.5-pro']:
            if pref in available: return pref
        return available[0] if available else None
    except:
        return None

# --- 2. עיצוב וטקסטים מופרדים (למניעת SyntaxError) ---
st.set_page_config(page_title="קבינט אפי", layout="wide")

# טקסטים קבועים במשתנים נפרדים
TEXT_TITLE = "🏛️ קבינט המוחות של אפי"
TEXT_MAP_HEADER = "🔍 מיפוי תחומי השפעה"
TEXT_IDEA_PROMPT = "🖋️ תאר את האתגר שלך (אדם, רגש, מחשבה):"
TEXT_PERSONAL_Q = "🎯 שאלה ספציפית שתרצה להפנות לקבינט?"

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Assistant', sans-serif; direction: rtl; text-align: right; }
    .expert-box { background-color: #fff; padding: 12px; border: 1px solid #ddd; border-radius: 10px; text-align: center; color: #000 !important; }
    .chat-bubble { background: #f0f2f6; padding: 20px; border-radius: 15px; border-right: 5px solid #3b82f6; color: #000; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

if 'step' not in st.session_state: st.session_state.step = 'setup'
if 'history' not in st.session_state: st.session_state.history = []

# --- 3. לוגיקת הקבינט ---
if 'cabinet' not in st.session_state:
    pool = {
        "פילוסופיה": ["סוקרטס", "אריסטו", "חנה ארנדט", "מרקוס אורליוס"],
        "פסיכולוגיה": ["פרויד", "יונג", "ויקטור פראנקל", "דניאל כהנמן"],
        "תרבות": ["מקלוהן", "אדוארד סעיד", "יובל נח הררי", "ניל פוסטמן"],
        "הפתעה": ["לאונרדו דה וינצ'י", "סטיב ג'ובס", "סון דזו", "איינשטיין"]
    }
    cab = []
    for cat in pool:
        for name in random.sample(pool[cat], 2): cab.append({"name": name, "cat": cat})
    st.session_state.cabinet = cab

# --- שלב ההגדרה ---
if st.session_state.step == 'setup':
    st.title(TEXT_TITLE)
    cols = st.columns(4)
    for i, m in enumerate(st.session_state.cabinet):
        with cols[i % 4]:
            st.markdown(f"<div class='expert-box'><b>{m['name']}</b><br>{m['cat']}</div>", unsafe_allow_html=True)
    
    st.write("---")
    idea = st.text_area(TEXT_IDEA_PROMPT, height=100)
    
    st.write(TEXT_MAP_HEADER)
    c1, c2 = st.columns(2)
    with c1:
        regesh = st.checkbox("עולם הרגש והשקט הפנימי")
        work = st.checkbox("תפקוד יומיומי ופרנסה")
    with c2:
        meaning = st.checkbox("משמעות ותפיסת עתיד")
        social = st.checkbox("מערכות יחסים וסביבה")
    
    personal_q = st.text_input(TEXT_PERSONAL_Q)

    if st.button("🔍 התחל אבחון"):
        model_name = get_working_model()
        if model_name and idea:
            st.session_state.working_model = model_name
            st.session_state.user_idea = idea
            doms = [d for d, v in zip(["Emotional", "Functional", "Meaning", "Social"], [regesh, work, meaning, social]) if v]
            with st.spinner("..."):
                model = genai.GenerativeModel(model_name)
                # שימוש בטקסט אנגלי חלקי בתוך הפרומפט למניעת קריסת עברית
                prompt = f"Topic: {idea}. Selected Domains: {doms}. User Query: {personal_q}. " + \
                         "Instructions: Act as a council of experts. Identify if 'society/company' means human or business based on context. " + \
                         "Generate 5 deep diagnostic questions in Hebrew. Return ONLY JSON: " + \
                         '[{"q": "...", "options": ["...", "...", "..."]}]'
                res = model.generate_content(prompt)
                match = re.search(r'\[.*\]', res.text, re.DOTALL)
                if match:
                    st.session_state.questions = json.loads(match.group())
                    st.session_state.step = 'diagnostic'
                    st.rerun()

# --- שלב האבחון ---
elif st.session_state.step == 'diagnostic':
    st.title("📝 שלב ההקשבה")
    ans_list = []
    for i, item in enumerate(st.session_state.questions):
        st.write(f"**{item['q']}**")
        ans = st.radio("בחר תשובה:", item['options'], key=f"ans_{i}")
        ans_list.append(f"Q: {item['q']} | A: {ans}")
    
    if st.button("🚀 התחל דיאלוג"):
        st.session_state.history.append({"role": "user", "parts": [f"Context: {st.session_state.user_idea}. Answers: {ans_list}"]})
        st.session_state.step = 'dialogue'
        st.rerun()

# --- שלב הדיאלוג ---
elif st.session_state.step == 'dialogue':
    st.title("💬 דיאלוג עם הקבינט")
    for msg in st.session_state.history:
        if msg['role'] == 'model':
            st.markdown(f"<div class='chat-bubble'>{msg['parts'][0]}</div>", unsafe_allow_html=True)
        elif 'Context:' not in msg['parts'][0]:
            st.info(f"👉 {msg['parts'][0]}")

    if st.session_state.history[-1]['role'] == 'user':
        with st.spinner("..."):
            names = ", ".join([m['name'] for m in st.session_state.cabinet])
            instr = f"Act as this council: {names}. Be brief, empathetic, and sharp. No cliches. Reflect hidden patterns. End with one question."
            model = genai.GenerativeModel(st.session_state.working_model)
            full_msg = [{"role": "user", "parts": [instr]}] + st.session_state.history
            res = model.generate_content(full_msg)
            st.session_state.history.append({"role": "model", "parts": [res.text]})
            st.rerun()

    user_reply = st.chat_input("השב לקבינט...")
    if user_reply:
        st.session_state.history.append({"role": "user", "parts": [user_reply]})
        st.rerun()