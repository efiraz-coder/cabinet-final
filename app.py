import streamlit as st
import requests
import json
import re
import random

# הגדרת דף - מניעת חפיפות
st.set_page_config(page_title="קבינט המוחות של אפי", layout="wide")

# --- CSS: עיצוב חסין וקריא ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');
    .stApp { background-color: #f0f4f8 !important; }
    html, body, [class*="st-"] {
        font-family: 'Assistant', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
        line-height: 2.3 !important; 
    }
    /* תיבות קלט ועיצוב כפתורים */
    textarea { background-color: #e8f5e9 !important; border: 2px solid #2e7d32 !important; border-radius: 12px; padding: 15px; }
    div.stButton > button {
        background-color: #bbdefb !important; color: #000 !important;
        border: 2px solid #1976d2 !important; font-weight: bold !important;
        height: 3.5em !important; width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ניהול דמויות ---
if 'current_cabinet' not in st.session_state:
    pool_std = [
        {"שם": "פיטר דרוקר", "תואר": "אבי הניהול", "התמחות": "אסטרטגיה וניהול"},
        {"שם": "זיגמונד פרויד", "תואר": "פסיכולוג", "התמחות": "תת מודע"},
        {"שם": "חנה ארנדט", "תואר": "פילוסופית", "התמחות": "אתיקה וחברה"},
        {"שם": "דניאל כהנמן", "תואר": "כלכלן", "התמחות": "קבלת החלטות"}
    ]
    pool_surp = [
        {"שם": "סון דזו", "תואר": "אסטרטג סיני", "התמחות": "אמנות המלחמה"},
        {"שם": "סטיב ג'ובס", "תואר": "יזם", "התמחות": "חדשנות"},
        {"שם": "מרקוס אורליוס", "תואר": "קיסר רומי", "התמחות": "חוסן מנטלי"}
    ]
    st.session_state.current_cabinet = random.sample(pool_std, 3) + random.sample(pool_surp, 3)

# --- פונקציית API חסינה ---
def call_gemini(prompt):
    try:
        api_key = st.secrets["GEMINI_KEY"]
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
        res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=20)
        if res.status_code == 200:
            return res.json()['candidates'][0]['content']['parts'][0]['text']
        return None
    except:
        return None

# --- ממשק משתמש ---
st.title("🏛️ קבינט המוחות של אפי")

st.subheader("👥 חברי הקבינט המייעצים לך:")
cols = st.columns(3)
for i, m in enumerate(st.session_state.current_cabinet):
    with cols[i % 3]:
        st.info(f"👤 **{m['שם']}**\n\n{m['תואר']}")

st.markdown("---")
idea = st.text_area("🖋️ תאר את האתגר שלך:", height=100, placeholder="מה מטריד אותך היום?")

if st.button("🔍 התחל סבב שאלות אבחון"):
    if idea:
        with st.spinner("חברי הקבינט מנסחים שאלות..."):
            prompt = f"נושא: {idea}. נסח 6 שאלות (אחת לכל מומחה) בפורמט JSON בלבד: [{{'expert': '...', 'q': '...', 'options': ['א','ב','ג']}}]"
            raw = call_gemini(prompt)
            if raw:
                # ניקוי פורמט JSON מתוך התשובה
                match = re.search(r'\[.*\]', raw.replace('```json', '').replace('```', ''), re.DOTALL)
                if match:
                    st.session_state.qs = json.loads(match.group())
                    if 'res' in st.session_state: del st.session_state['res']
                else:
                    st.warning("הקבינט לא הצליח לגבש פורמט תקין. נסה ללחוץ שוב.")
            else:
                st.error("בעיית תקשורת עם הקבינט. בדוק את מפתח ה-API או נסה שוב.")

# הצגה בטוחה של השאלון - פותר את בעיית ה-Traceback
if 'qs' in st.session_state and st.session_state.qs:
    st.subheader("📝 שאלות האבחון של המומחים")
    ans_data = []
    for i, item in enumerate(st.session_state.qs):
        st.write(f"**💬 {item.get('expert', 'מומחה')} שואל:**")
        choice = st.radio(item['q'], item['options'], key=f"q_{i}")
        ans_data.append(f"מומחה: {item.get('expert')} | תשובה: {choice}")

    if st.button("🚀 הפק תובנות אסטרטגיות"):
        with st.spinner("מנתח נתונים..."):
            p_final = f"נושא: {idea}. תשובות: {ans_data}. כתוב 5 תובנות וטבלה מסכמת."
            st.session_state.res = call_gemini(p_final)

if 'res' in st.session_state:
    st.success("📊 מסקנות הקבינט:")
    st.write(st.session_state.res)