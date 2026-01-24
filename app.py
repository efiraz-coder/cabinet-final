import streamlit as st
import google.generativeai as genai
import json
import re
import random

# --- חלק 1: מנגנון ה-API החכם (סריקה דינמית) ---
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
    except Exception as e:
        st.error(f"Error: {e}")
        return None

# --- חלק 2: עיצוב קריא ומזמין ---
st.set_page_config(page_title="קבינט אפי", layout="wide")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Assistant', sans-serif; direction: rtl; text-align: right; }
    .expert-box { background-color: #ffffff; padding: 12px; border: 1px solid #d1d5db; border-radius: 10px; text-align: center; color: #1f2937 !important; }
    .chat-bubble { background: #f0f2f6; padding: 20px; border-radius: 15px; border-right: 5px solid #3b82f6; color: #1f2937; margin-bottom: 15px; }
    .stCheckbox label { font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- חלק 3: ניהול המצב (State) ---
if 'step' not in st.session_state: st.session_state.step = 'setup'
if 'history' not in st.session_state: st.session_state.history = []

# מאגר מומחים
POOL = {
    "פילוסופיה": ["סוקרטס", "אריסטו", "חנה ארנדט", "מרקוס אורליוס"],
    "פסיכולוגיה": ["פרויד", "יונג", "ויקטור פראנקל", "דניאל כהנמן"],
    "תרבות": ["מקלוהן", "אדוארד סעיד", "יובל נח הררי", "ניל פוסטמן"],
    "הפתעה": ["לאונרדו דה וינצ'י", "סטיב ג'ובס", "סון דזו", "איינשטיין"]
}

if 'cabinet' not in st.session_state:
    cab = []
    for cat in POOL:
        for name in random.sample(POOL[cat], 2): cab.append({"name": name, "cat": cat})
    st.session_state.cabinet = cab

# --- שלב 0: הגדרת הזירה (מיפוי והבנה) ---
if st.session_state.step == 'setup':
    st.title("🏛️ קבינט המוחות של אפי")
    
    cols = st.columns(4)
    for i, m in enumerate(st.session_state.cabinet):
        with cols[i % 4]: st.markdown(f"<div class='expert-box'><b>{m['name']}</b><br><small>{m['cat']}</small></div>", unsafe_allow_html=True)
    
    st.write("---")
    idea = st.text_area("🖋️ תאר את האתגר או התחושה (למשל: 'אובדן חברה קרובה'):", height=100)
    
    st.write("🔍 **מיפוי הערפל:** באיזה תחומי חיים זה פוגש אותך? (