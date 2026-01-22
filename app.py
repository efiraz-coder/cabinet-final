import streamlit as st
import requests
import json
import re
import random

# הגדרת דף
st.set_page_config(page_title="קבינט המוחות של אפי", layout="wide")

# --- CSS: עיצוב נקי למניעת חפיפות ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');

    .stApp { background-color: #f0f4f8 !important; }

    html, body, [class*="st-"] {
        font-family: 'Assistant', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
        color: #000000 !important;
        line-height: 2.2 !important; 
    }

    textarea {
        background-color: #e8f5e9 !important; 
        border: 2px solid #2e7d32 !important;
        border-radius: 12px !important;
        padding: 15px !important;
    }

    div.stButton > button {
        background-color: #bbdefb !important; 
        color: #000000 !important;
        border: 2px solid #1976d2 !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        height: 3.5em !important;
        width: 100% !important;
    }

    .expert-question {
        background-color: #ffffff;
        padding: 15px;
        border-right: 5px solid #1976d2;
        border-radius: 8px;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ניהול הדמויות ---
if 'current_cabinet' not in st.session_state:
    pool_std = [
        {"שם": "פיטר דרוקר", "תואר": "אבי הניהול", "התמחות": "אסטרטגיה וארגון"},
        {"שם": "זיגמונד פרויד", "תואר": "פסיכולוג", "התמחות": "תת מודע ודחפים"},
        {"שם": "חנה ארנדט", "תואר": "פילוסופית", "התמחות": "חברה ופוליטיקה"},
        {"שם": "דניאל כהנמן", "תואר": "כלכלן", "התמחות": "קבלת החלטות"},
        {"שם": "אברהם מאסלו", "תואר": "פסיכולוג", "התמחות": "צרכים ומוטיבציה"}
    ]
    pool_surp = [
        {"שם": "סון דזו", "תואר": "אסטרטג סיני", "התמחות": "אמנות המלחמה"},
        {"שם": "סטיב ג'ובס", "תואר": "יזם", "התמחות": "חדשנות ועיצוב"},
        {"שם": "מרקוס אורליוס", "תואר": "קיסר רומי", "התמחות": "חוסן וסטואיציזם"},
        {"שם": "לאונרדו דה וינצ'י", "תואר": "גאון", "התמחות": "יצירתיות רב-תחומית"}
    ]
    st.session_state.current_cabinet = random.sample(pool_std, 3) + random.sample(pool_surp, 3)

def call_api(prompt):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={st.secrets['GEMINI_KEY']}"
        res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
        if res.status_code == 200:
            return res.json()['candidates'][0]['content']['parts'][0]['text']
        return None
    except:
        return None

# --- ממשק ---
st.title("🏛️ קבינט המוחות של אפי")

st.subheader("👥 המומחים שמתכנסים עבורך:")
cols = st.columns(3)
for i, m in enumerate(st.session_state.current_cabinet):
    with cols[i % 3]:
        st.info(f"👤 **{m['שם']}**\n\n{m['תואר']}")

st.markdown("---")
idea = st.text_area("🖋️ תאר את האתגר שלך:", height=100)

if st.button("🔍 התחל סבב שאלות אישיות"):
    if idea:
        with st.spinner("חברי הקבינט מנסחים שאלות..."):
            experts_list = [f"{m['שם']} ({m['התמחות']})" for m in st.session_state.current_cabinet]
            prompt = f"""נושא: {idea}. מומחים: {experts_list}.
            נסח 6 שאלות (אחת לכל מומחה). כל שאלה חייבת לשקף את הזווית של המומחה.
            החזר JSON בלבד: [{{'expert': 'שם המומחה', 'q': 'שאלה', 'options': ['א','ב','ג']}}, ...]"""
            
            raw = call_api(prompt)
            match = re.search(r'\[.*\]', raw, re.DOTALL) if raw else None
            if match:
                st.session_state.qs = json.loads(match.group())
                if 'res' in st.session_state: del st.session_state['res']
            else:
                st.error("הקבינט זקוק לניסוח מחדש. אנא נסה שוב.")

if 'qs' in st.session_state and st.session_state.qs:
    st.subheader("📝 סבב שאלות האבחון")
    ans_data = []
    
    for i, item in enumerate(st.session_state.qs):
        st.markdown(f"**💬 {item['expert']} שואל/ת:**")
        choice = st.radio(item['q'], item['options'], key=f"q_{i}")
        ans_data.append(f"מומחה: {item['expert']} | שאלה: {item['q']} | תשובה: {choice}")

    if st.button("🚀 הפק תובנות אסטרטגיות"):
        with st.spinner("מגבש המלצות..."):
            p_final = f"נושא: {idea}. תשובות: {ans_data}. כתוב 5 תובנות וטבלה מסכמת."
            st.session_state.res = call_api(p_final)

if 'res' in st.session_state:
    st.markdown("---")
    st.markdown("### 📊 מסקנות הקבינט של אפי")
    st.write(st.session_state.res)