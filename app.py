import streamlit as st
import google.generativeai as genai
import json
import re
import random

# --- 1. מנגנון API חכם וסורק מודלים ---
def get_working_model():
    if "GEMINI_KEY" not in st.secrets:
        st.error("Missing GEMINI_KEY in Secrets")
        return None
    genai.configure(api_key=st.secrets["GEMINI_KEY"])
    try:
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for pref in ['models/gemini-1.5-flash', 'models/gemini-1.5-pro']:
            if pref in available: return pref
        return available[0] if available else None
    except:
        return None

# --- 2. עיצוב המרחב הטיפולי ---
st.set_page_config(page_title="קבינט המוחות", layout="wide")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Assistant', sans-serif; direction: rtl; text-align: right; }
    .expert-box { background-color: #fff; padding: 15px; border: 1px solid #ddd; border-radius: 12px; text-align: center; color: #1f2937 !important; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .chat-bubble { background: #f8fafc; padding: 25px; border-radius: 15px; border-right: 6px solid #3b82f6; color: #1e293b; margin-bottom: 20px; line-height: 1.6; font-size: 1.1em; }
    .stCheckbox label { font-size: 1.1em; font-weight: 500; }
    </style>
""", unsafe_allow_html=True)

# --- 3. ניהול מצב והרכב הקבינט ---
if 'step' not in st.session_state: st.session_state.step = 'setup'
if 'history' not in st.session_state: st.session_state.history = []

if 'cabinet' not in st.session_state:
    pool = {
        "פילוסופיה": ["סוקרטס", "אריסטו", "חנה ארנדט", "מרקוס אורליוס", "ניטשה"],
        "פסיכולוגיה": ["פרויד", "יונג", "ויקטור פראנקל", "דניאל כהנמן", "מאסלו"],
        "תרבות": ["מקלוהן", "אדוארד סעיד", "יובל נח הררי", "ניל פוסטמן"],
        "הפתעה": ["לאונרדו דה וינצ'י", "סטיב ג'ובס", "סון דזו", "איינשטיין", "מרים פרץ"]
    }
    cab = []
    for cat in pool:
        for name in random.sample(pool[cat], 2): cab.append({"name": name, "cat": cat})
    st.session_state.cabinet = cab

# --- שלב 0: הגדרת האתגר והמיפוי ---
if st.session_state.step == 'setup':
    st.title("🏛️ קבינט המוחות")
    st.subheader("המומחים שנבחרו עבורך הפעם:")
    cols = st.columns(4)
    for i, m in enumerate(st.session_state.cabinet):
        with cols[i % 4]:
            st.markdown(f"<div class='expert-box'><b>{m['name']}</b><br><small>{m['cat']}</small></div>", unsafe_allow_html=True)
    
    st.write("---")
    idea = st.text_area("🖋️ תאר את האתגר או המצב שלך:", height=100, placeholder="למשל: 'חבר לא מגיע בזמן לפגישות' או 'אובדן חברה קרובה'...")
    
    st.write("🔍 **מיפוי הערפל:** באילו תחומים תרצה שהקבינט יתמקד?")
    c1, c2 = st.columns(2)
    with c1:
        regesh = st.checkbox("עולם הרגש והשקט הפנימי")
        work = st.checkbox("תפקוד יומיומי, קריירה וביצועים")
    with c2:
        meaning = st.checkbox("משמעות, ערכים ותפיסת עתיד")
        social = st.checkbox("מערכות יחסים, גבולות ותקשורת")
    
    personal_q = st.text_input("🎯 שאלה ספציפית שבוערת בך?")

    if st.button("🔍 בואו נתחיל"):
        model_name = get_working_model()
        if model_name and idea:
            st.session_state.working_model = model_name
            st.session_state.user_idea = idea
            doms = [d for d, v in zip(["רגש", "תפקוד", "משמעות", "חברה"], [regesh, work, meaning, social]) if v]
            with st.spinner("הקבינט לומד את ההקשר ומגבש שאלות..."):
                model = genai.GenerativeModel(model_name)
                # פרומפט הנחיה קשיח למניעת קלישאות ובלבול סמנטי
                prompt = f"""
                Topic: {idea}. Selected Focus: {doms}. User's Direct Question: {personal_q}. 
                Experts: {[m['name'] for m in st.session_state.cabinet]}.
                Task: Generate 5 deep, empathetic diagnostic questions in HEBREW. 
                1. Identify the semantic context (personal loss vs professional vs social). 
                2. Be specific, NOT generic. 
                Return ONLY JSON: [{"q": "...", "options": ["...", "...", "..."]}]
                """
                res = model.generate_content(prompt)
                match = re.search(r'\[.*\]', res.text, re.DOTALL)
                if match:
                    st.session_state.questions = json.loads(match.group())
                    st.session_state.step = 'diagnostic'
                    st.rerun()

# --- שלב 1: שלב האבחון (ההקשבה) ---
elif st.session_state.step == 'diagnostic':
    st.title("📝 שלב ההקשבה")
    st.write("כדי שנוכל לדייק, ענה על השאלות הבאות:")
    ans_list = []
    for i, item in enumerate(st.session_state.questions):
        st.write(f"**{item['q']}**")
        ans = st.radio("בחר תשובה:", item['options'], key=f"ans_{i}", label_visibility="collapsed")
        ans_list.append(f"שאלה: {item['q']} | תשובה: {ans}")
    
    if st.button("🚀 שלח תשובות וקבל תובנות מהקבינט"):
        st.session_state.history.append({"role": "user", "parts": [f"המקרה: {st.session_state.user_idea}. תשובות לאבחון: {ans_list}"]})
        st.session_state.step = 'dialogue'
        st.rerun()

# --- שלב 2: הדיאלוג והתובנות ---
elif st.session_state.step == 'dialogue':
    st.title("💬 הדיאלוג עם הקבינט")
    
    for msg in st.session_state.history:
        if msg['role'] == 'model':
            st.markdown(f"<div class='chat-bubble'>{msg['parts'][0]}</div>", unsafe_allow_html=True)
        elif 'המקרה:' not in msg['parts'][0]:
            st.info(f"👉 **אתה:** {msg['parts'][0]}")

    if st.session_state.history[-1]['role'] == 'user':
        with st.spinner("הקבינט מעבד את הנתונים..."):
            names = ", ".join([m['name'] for m in st.session_state.cabinet])
            # הנחיית ה"וואו" - אמפתיה, סדר, ללא קלישאות
            instr = f"""
            You are a council of experts: {names}. 
            The user is looking for "Seder Ba-Rosh" (clarity). 
            Response Structure in HEBREW:
            1. Reflection (1-2 sentences): Empathy and identifying the core struggle.
            2. Three Pillars of Clarity (numbered): Deep insights without cliches.
            3. The Compass Question: One focused question to move forward.
            Be personal, NOT generic. If the context is personal loss, be tender. If it's a conflict, be strategic.
            """
            model = genai.GenerativeModel(st.session_state.working_model)
            full_msg = [{"role": "user", "parts": [instr]}] + st.session_state.history
            res = model.generate_content(full_msg)
            st.session_state.history.append({"role": "model", "parts": [res.text]})
            st.rerun()

    user_reply = st.chat_input("המשך את הדיאלוג או שאל שאלה נוספת...")
    if user_reply:
        st.session_state.history.append({"role": "user", "parts": [user_reply]})
        st.rerun()

    if st.button("🏁 סיכום ומפת דרכים סופית"):
        model = genai.GenerativeModel(st.session_state.working_model)
        sum_res = model.generate_content(st.session_state.history + [{"role": "user", "parts": ["סכם את כל הדיאלוג ב-5 תובנות זהב ו-2 צעדים מעשיים למחר בבוקר. בלי קלישאות."]}] )
        st.markdown("---")
        st.success("📊 מפת הדרכים שלך:")
        st.write(sum_res.text)
        if st.button("🔄 התחל מחדש"):
            st.session_state.clear()
            st.rerun()