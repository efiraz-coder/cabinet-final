import streamlit as st
import google.generativeai as genai
import json
import re
import random

# ==========================================
# חלק 1: המנגנון החכם (Adapter - סריקה דינמית)
# ==========================================
def get_working_model():
    """סורק את החשבון שלך ובוחר רק מודל שבאמת פתוח עבורך"""
    if "GEMINI_KEY" not in st.secrets:
        st.error("Missing GEMINI_KEY")
        return None
    
    genai.configure(api_key=st.secrets["GEMINI_KEY"])
    try:
        available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for pref in ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']:
            if pref in available:
                return pref
        return available[0] if available else None
    except Exception as e:
        st.error(f"Error scanning models: {e}")
        return None

# ==========================================
# חלק 2: עיצוב קריא (UI - תיקון הלבן על לבן)
# ==========================================
st.set_page_config(page_title="קבינט אפי", layout="wide")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Assistant', sans-serif; direction: rtl; text-align: right; }
    .expert-box { 
        background-color: #ffffff; 
        padding: 12px; 
        border: 1px solid #d1d5db; 
        border-radius: 10px; 
        text-align: center; 
        color: #1f2937 !important; /* טקסט כהה וקריא */
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .chat-bubble { 
        background: #f0f2f6; 
        padding: 18px; 
        border-radius: 15px; 
        border-right: 5px solid #3b82f6; 
        color: #1f2937; 
        margin-bottom: 15px;
    }
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# חלק 3: לוגיקת הקבינט והדיאלוג
# ==========================================
if 'step' not in st.session_state: st.session_state.step = 'setup'
if 'history' not in st.session_state: st.session_state.history = []

POOL = {
    "פילוסופיה": ["סוקרטס", "אריסטו", "חנה ארנדט", "מרקוס אורליוס", "ניטשה"],
    "פסיכולוגיה": ["פרויד", "יונג", "ויקטור פראנקל", "דניאל כהנמן", "מאסלו"],
    "תרבות": ["מקלוהן", "אדוארד סעיד", "יובל נח הררי", "ניל פוסטמן"],
    "הפתעה": ["לאונרדו דה וינצ'י", "סטיב ג'ובס", "סון דזו", "איינשטיין", "שייקספיר"]
}

if 'cabinet' not in st.session_state:
    cab = []
    for cat in POOL:
        selected = random.sample(POOL[cat], 2)
        for name in selected: cab.append({"name": name, "cat": cat})
    st.session_state.cabinet = cab

# --- שלב ההגדרה ---
if st.session_state.step == 'setup':
    st.title("🏛️ קבינט המוחות של אפי")
    st.write("חברי הקבינט שלך (2 מכל תחום):")
    cols = st.columns(4)
    for i, m in enumerate(st.session_state.cabinet):
        with cols[i % 4]:
            st.markdown(f"<div class='expert-box'><b>{m['name']}</b><br><small>{m['cat']}</small></div>", unsafe_allow_html=True)

    if st.button("🔄 רענן את הקבינט (החלפת 4 מומחים)"):
        for i in [0, 2, 4, 6]: # מחליף אחד מכל זוג
            cat = st.session_state.cabinet[i]['cat']
            st.session_state.cabinet[i]['name'] = random.choice(POOL[cat])
        st.rerun()

    idea = st.text_area("🖋️ מה המחשבה או הדילמה שמעסיקה אותך?", height=100)
    if st.button("🔍 התחל באבחון"):
        model_name = get_working_model()
        if model_name and idea:
            st.session_state.working_model = model_name
            st.session_state.user_idea = idea
            with st.spinner("הקבינט מגבש שאלות..."):
                model = genai.GenerativeModel(model_name)
                prompt = f"נושא: {idea}. נסח 6 שאלות אנושיות, פשוטות ואמפתיות על רגשות ודפוסי חשיבה. החזר רק JSON: " + '[{"q": "...", "options": ["...", "...", "..."]}]'
                res = model.generate_content(prompt)
                match = re.search(r'\[.*\]', res.text, re.DOTALL)
                if match:
                    st.session_state.questions = json.loads(match.group())
                    st.session_state.step = 'diagnostic'
                    st.rerun()

# --- שלב האבחון ---
elif st.session_state.step == 'diagnostic':
    st.title("📝 הקשבה עצמית")
    ans_list = []
    for i, item in enumerate(st.session_state.questions):
        st.write(f"**{item['q']}**")
        ans = st.radio("בחר את התשובה הקרובה לליבך:", item['options'], key=f"ans_{i}")
        ans_list.append(f"שאלה: {item['q']} | תשובה: {ans}")
    
    if st.button("🚀 שלח תשובות והתחל דיאלוג"):
        st.session_state.history.append({"role": "user", "parts": [f"הנושא: {st.session_state.user_idea}. התשובות שלי: {ans_list}"]})
        st.session_state.step = 'dialogue'
        st.rerun()

# --- שלב הדיאלוג המתפתח ---
elif st.session_state.step == 'dialogue':
    st.title("💬 דיאלוג עם הקבינט")
    
    # הצגת היסטוריה
    for msg in st.session_state.history:
        if msg['role'] == 'model':
            st.markdown(f"<div class='chat-bubble'>{msg['parts'][0]}</div>", unsafe_allow_html=True)
        elif 'הנושא' not in msg['parts'][0]:
            st.write(f"👉 **אתה:** {msg['parts'][0]}")

    # יצירת תגובת קבינט
    if st.session_state.history[-1]['role'] == 'user':
        with st.spinner("הקבינט מגיב..."):
            names = ", ".join([m['name'] for m in st.session_state.cabinet])
            instruction = f"פעל כקבינט החכמים ({names}). נתח את דברי המשתמש, שקף לו דפוסי חשיבה ורגשות סמויים. אל תזכיר שמות. סיים בשאלה."
            model = genai.GenerativeModel(st.session_state.working_model)
            # בניית היסטוריה מלאה לדיאלוג
            full_messages = [{"role": "user", "parts": [instruction]}] + st.session_state.history
            res = model.generate_content(full_messages)
            st.session_state.history.append({"role": "model", "parts": [res.text]})
            st.rerun()

    user_reply = st.chat_input("כתוב כאן את תגובתך לקבינט...")
    if user_reply:
        st.session_state.history.append({"role": "user", "parts": [user_reply]})
        st.rerun()

    if st.button("🏁 סכם תובנות ודרכי פעולה"):
        model = genai.GenerativeModel(st.session_state.working_model)
        summary = model.generate_content(st.session_state.history + [{"role": "user", "parts": ["סכם עבורי ב-5 תובנות עומק ו-3 דרכי פעולה לבהירות."]}] )
        st.markdown("---")
        st.success("📊 המלצות הקבינט הסופיות:")
        st.write(summary.text)