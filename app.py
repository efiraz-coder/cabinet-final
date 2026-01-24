import streamlit as st
import google.generativeai as genai
import json
import re
import random

# --- 1. הגדרות API ---
def setup_genai():
    if "GEMINI_KEY" not in st.secrets:
        st.error("Missing GEMINI_KEY in Streamlit Secrets!")
        return None
    genai.configure(api_key=st.secrets["GEMINI_KEY"])
    # שימוש במודל הפלאש היציב ביותר
    return genai.GenerativeModel('gemini-1.5-flash')

# --- 2. עיצוב ממשק חסין ---
st.set_page_config(page_title="קבינט המוחות", layout="wide")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Assistant', sans-serif; direction: rtl; text-align: right; background-color: #0f172a; }
    
    /* הבטחת טקסט שחור בתיבות לבנות */
    .stTextArea textarea { color: #000000 !important; background-color: #ffffff !important; border: 2px solid #3b82f6 !important; }
    .stTextInput input { color: #000000 !important; background-color: #ffffff !important; }
    
    label, p, h1, h2, h3, span { color: #f8fafc !important; }
    .expert-card { background-color: #ffffff; padding: 10px; border-radius: 8px; border: 2px solid #3b82f6; color: #1e293b !important; text-align: center; font-weight: bold; margin-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

# --- 3. פונקציות עזר ---
def safe_json_parse(text):
    try:
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match: return json.loads(match.group())
    except: return None

# --- 4. ניהול מצב האפליקציה ---
if 'step' not in st.session_state: st.session_state.step = 'setup'
if 'history' not in st.session_state: st.session_state.history = []

# --- שלב 0: מסך פתיחה ---
if st.session_state.step == 'setup':
    st.title("🏛️ קבינט המוחות")
    
    # הצגת חברי הקבינט
    cols = st.columns(4)
    cabinet = ["סוקרטס", "מרקוס אורליוס", "ויקטור פראנקל", "יונג", "מקלוהן", "הררי", "סטיב ג'ובס", "דה וינצ'י"]
    for i, name in enumerate(cabinet):
        with cols[i % 4]: st.markdown(f"<div class='expert-card'>{name}</div>", unsafe_allow_html=True)
    
    st.write("---")
    idea = st.text_area("🖋️ תאר את המקרה לדיון:", height=150, placeholder="למשל: התלבטות מקצועית או אישית...")
    
    if st.button("🔍 התחל אבחון"):
        model = setup_genai()
        if model and idea:
            with st.spinner("הקבינט מגבש שאלות..."):
                try:
                    prompt = f"Topic: {idea}. Task: Return 3 diagnostic questions in Hebrew as a JSON array: [{{'q':'question','options':['1','2','3']}}]. Return ONLY JSON."
                    response = model.generate_content(prompt)
                    questions = safe_json_parse(response.text)
                    
                    if questions:
                        st.session_state.questions = questions
                        st.session_state.user_idea = idea
                        st.session_state.step = 'diagnostic'
                        st.rerun()
                    else:
                        st.error("המודל החזיר תשובה לא תקינה. נסה שוב.")
                except Exception as e:
                    if "429" in str(e):
                        st.error("חרגת מהמכסה (Quota). המתן דקה ונסה שוב.")
                    else:
                        st.error(f"שגיאה: {str(e)}")

# --- שלב 1: אבחון ---
elif st.session_state.step == 'diagnostic':
    st.title("📝 שלב האבחון")
    ans_list = []
    for i, item in enumerate(st.session_state.questions):
        ans = st.radio(f"**{item['q']}**", item['options'], key=f"q_{i}")
        ans_list.append(f"Q: {item['q']} | A: {ans}")
    
    if st.button("🚀 הצג למליאה"):
        st.session_state.history.append({"role": "user", "content": f"דילמה: {st.session_state.user_idea}\nאבחון: {ans_list}"})
        st.session_state.step = 'dialogue'
        st.rerun()

# --- שלב 2: צ'אט ---
elif st.session_state.step == 'dialogue':
    st.title("💬 דיון בקבינט")
    
    for msg in st.session_state.history:
        if "דילמה:" in msg['content'] and len(st.session_state.history) > 1: continue
        with st.chat_message("assistant" if msg['role'] == "model" else "user"):
            st.write(msg['content'])

    if not st.session_state.history or st.session_state.history[-1]['role'] == 'user':
        with st.chat_message("assistant"):
            with st.spinner("חושב..."):
                model = setup_genai()
                expert = random.choice(["סוקרטס", "מרקוס אורליוס", "ויקטור פראנקל", "סטיב ג'ובס"])
                instr = f"You are {expert}. Respond in Hebrew. Start with: '{expert} היה נוהג לומר...'. Be brief."
                
                # היסטוריה לפורמט Gemini
                gem_hist = [{"role": m['role'], "parts": [m['content']]} for m in st.session_state.history]
                try:
                    res = model.generate_content([{"role": "user", "parts": [instr]}] + gem_hist)
                    st.write(res.text)
                    st.session_state.history.append({"role": "model", "content": res.text})
                except Exception as e:
                    st.error(f"שגיאה: {e}")

    if reply := st.chat_input("כתוב לקבינט..."):
        st.session_state.history.append({"role": "user", "content": reply})
        st.rerun()

    if st.sidebar.button("🔄 התחל מחדש"):
        st.session_state.step = 'setup'
        st.session_state.history = []
        st.rerun()