import streamlit as st
import google.generativeai as genai
import json
import re
import random

# ==========================================
# חלק 1: המנגנון החכם (Adapter)
# ==========================================
def call_gemini(prompt_list):
    """מנהל את התקשורת מול ה-API ומטפל בשגיאות 404"""
    if "GEMINI_KEY" not in st.secrets:
        st.error("Missing GEMINI_KEY")
        return None
    
    genai.configure(api_key=st.secrets["GEMINI_KEY"])
    # שימוש במודל שראינו שזמין אצלך
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    try:
        response = model.generate_content(prompt_list)
        return response.text
    except Exception as e:
        st.error(f"API Error: {e}")
        return None

# ==========================================
# חלק 2: "החוכמה" (Logic & Psychology)
# ==========================================
POOL = {
    "פילוסופיה": ["סוקרטס", "חנה ארנדט", "מרקוס אורליוס", "ניטשה", "סארטר"],
    "פסיכולוגיה": ["פרויד", "יונג", "ויקטור פראנקל", "דניאל כהנמן", "מאסלו"],
    "תרבות": ["מקלוהן", "אדוארד סעיד", "יובל נח הררי", "ניל פוסטמן"],
    "הפתעה": ["סטיב ג'ובס", "דה וינצ'י", "סון דזו", "איינשטיין"]
}

def get_init_cabinet():
    cab = []
    for cat in POOL:
        for name in random.sample(POOL[cat], 2):
            cab.append({"name": name, "cat": cat})
    return cab

# ==========================================
# חלק 3: העיצוב והממשק (UI/UX)
# ==========================================
st.set_page_config(page_title="קבינט אפי", layout="wide")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Assistant', sans-serif; direction: rtl; text-align: right; }
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; }
    .expert-box { background: #ffffff; padding: 12px; border: 1px solid #e5e7eb; border-radius: 10px; text-align: center; }
    .chat-bubble { background: #e9ecef; padding: 15px; border-radius: 15px; margin-bottom: 10px; border-right: 5px solid #3b82f6; color: #000; }
    </style>
""", unsafe_allow_html=True)

# ניהול מצבי אפליקציה
if 'step' not in st.session_state: st.session_state.step = 'setup'
if 'cabinet' not in st.session_state: st.session_state.cabinet = get_init_cabinet()
if 'history' not in st.session_state: st.session_state.history = []

# --- שלב 0: הגדרת הקבינט ---
if st.session_state.step == 'setup':
    st.title("🏛️ קבינט המוחות של אפי")
    st.write("חברי הקבינט שנבחרו עבורך:")
    cols = st.columns(4)
    for i, m in enumerate(st.session_state.cabinet):
        with cols[i % 4]: st.markdown(f"<div class='expert-box'><b>{m['name']}</b><br><small>{m['cat']}</small></div>", unsafe_allow_html=True)
    
    if st.button("🔄 רענן קבינט"):
        st.session_state.cabinet = get_init_cabinet()
        st.rerun()
        
    idea = st.text_area("🖋️ מה על ליבך היום?", height=100)
    if st.button("🔍 התחל אבחון"):
        if idea:
            st.session_state.user_idea = idea
            names = ", ".join([m['name'] for m in st.session_state.cabinet])
            prompt = f"נושא: {idea}. מומחים: {names}. נסח 6 שאלות אבחון עמוקות ואנושיות ב-JSON: " + '[{"q": "...", "options": ["...", "...", "..."]}]'
            res = call_gemini(prompt)
            if res:
                match = re.search(r'\[.*\]', res, re.DOTALL)
                if match:
                    st.session_state.questions = json.loads(match.group())
                    st.session_state.step = 'diagnostic'
                    st.rerun()

# --- שלב 1: אבחון (שאלון) ---
elif st.session_state.step == 'diagnostic':
    st.title("📝 הקשבה עצמית")
    ans_list = []
    for i, item in enumerate(st.session_state.questions):
        st.write(f"**{item['q']}**")
        ans = st.radio("בחר תשובה:", item['options'], key=f"q_{i}", label_visibility="collapsed")
        ans_list.append(f"שאלה: {item['q']} | תשובה: {ans}")
    
    if st.button("🚀 שלח תשובות לקבינט"):
        st.session_state.history.append({"role": "user", "parts": [f"הנושא שלי: {st.session_state.user_idea}. התשובות שלי לאבחון: {ans_list}"]})
        st.session_state.step = 'dialogue'
        st.rerun()

# --- שלב 2: הדיאלוג המתפתח (הצ'אט) ---
elif st.session_state.step == 'dialogue':
    st.title("💬 דיאלוג עם הקבינט")
    
    # הצגת היסטוריית הדיאלוג
    for msg in st.session_state.history:
        if msg['role'] == 'model':
            st.markdown(f"<div class='chat-bubble'>{msg['parts'][0]}</div>", unsafe_allow_html=True)
        elif msg['role'] == 'user' and 'הנושא שלי' not in msg['parts'][0]:
            st.write(f"👉 **אתה:** {msg['parts'][0]}")

    # קריאה לקבינט רק אם ההודעה האחרונה היא של המשתמש
    if st.session_state.history[-1]['role'] == 'user':
        with st.spinner("הקבינט דן בדבריך..."):
            names = ", ".join([m['name'] for m in st.session_state.cabinet])
            system_instruction = f"אתה קבינט חכם ({names}). נתח את דברי המשתמש, שקף דפוסי חשיבה, תן תובנה עמוקה וסיים בשאלה מעוררת מחשבה. אל תציין שמות מומחים."
            
            # בניית השיחה המלאה
            full_context = [{"role": "user", "parts": [system_instruction]}] + st.session_state.history
            response = call_gemini(full_context)
            if response:
                st.session_state.history.append({"role": "model", "parts": [response]})
                st.rerun()

    # תיבת תגובה לשואל
    with st.container():
        user_input = st.chat_input("השב לקבינט...")
        if user_input:
            st.session_state.history.append({"role": "user", "parts": [user_input]})
            st.rerun()

    if st.button("🏁 סיכום ומפת דרכים"):
        final_prompt = st.session_state.history + [{"role": "user", "parts": ["סכם את הדיאלוג ב-5 תובנות עומק ו-3 דרכי פעולה מעשיות."]}]
        summary = call_gemini(final_prompt)
        st.markdown("---")
        st.success("📊 מפת הדרכים שלך:")
        st.write(summary)