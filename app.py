import streamlit as st
import requests
import json
import re
import random

# הגדרת דף
st.set_page_config(page_title="קבינט המוחות של אפי", layout="wide")

# --- CSS: פתרון חפיפת טקסטים ועיצוב צבעוני ---
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

    /* שדות קלט בירוק בהיר */
    textarea, input {
        background-color: #e8f5e9 !important;
        border: 2px solid #2e7d32 !important;
        border-radius: 12px !important;
        padding: 15px !important;
    }

    /* כפתורים בכחול בהיר */
    div.stButton > button {
        background-color: #bbdefb !important;
        color: #000000 !important;
        border: 2px solid #1976d2 !important;
        border-radius: 15px !important;
        font-weight: bold !important;
        height: 3.5em !important;
        width: 100% !important;
        margin-top: 20px !important;
    }

    /* תיבות שאלון בתכלת */
    div[data-baseweb="radio"] {
        background-color: #e3f2fd !important;
        padding: 20px !important;
        border-radius: 15px !important;
        border: 1px solid #90caf9 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ניהול דמויות ---
if 'cabinet' not in st.session_state:
    pool_std = [
        {"שם": "פיטר דרוקר", "תואר": "אבי הניהול", "התמחות": "אסטרטגיה"},
        {"שם": "זיגמונד פרויד", "תואר": "פסיכולוג", "התמחות": "תת מודע"},
        {"שם": "חנה ארנדט", "תואר": "פילוסופית", "התמחות": "חברה"},
        {"שם": "דניאל כהנמן", "תואר": "כלכלן", "התמחות": "קבלת החלטות"}
    ]
    pool_surp = [
        {"שם": "סון דזו", "תואר": "אסטרטג סיני", "התמחות": "אמנות המלחמה"},
        {"שם": "סטיב ג'ובס", "תואר": "יזם", "התמחות": "חדשנות"},
        {"שם": "מרקוס אורליוס", "תואר": "קיסר", "התמחות": "חוסן מנטלי"}
    ]
    st.session_state.cabinet = random.sample(pool_std, 3) + random.sample(pool_surp, 3)

# --- פונקציית API ---
def call_api(prompt):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={st.secrets['GEMINI_KEY']}"
        res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
        return res.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return None

# --- ממשק משתמש ---
st.title("🏛️ קבינט המוחות של אפי")

st.subheader("👥 חברי הקבינט שלך")
for m in st.session_state.cabinet:
    st.write(f"👤 **{m['שם']}** | {m['תואר']} | {m['התמחות']}")

st.markdown("---")
idea = st.text_area("🖋️ מה הנושא לדיון?", height=100)

if st.button("🔍 בנה שאלון אבחון"):
    if idea:
        with st.spinner("מכין שאלות..."):
            p = f"נושא: {idea}. נסח 4 שאלות אבחון קצרות ביומיומית בפורמט JSON בלבד: [{{'q': '...', 'options': [...]}}]"
            raw = call_api(p)
            match = re.search(r'\[.*\]', raw, re.DOTALL) if raw else None
            if match:
                st.session_state.qs = json.loads(match.group())
            else:
                st.error("הקבינט עמוס, נסה שוב.")

# הצגה בטוחה של השאלון
if 'qs' in st.session_state and st.session_state.qs:
    st.subheader("📝 שלב האבחון")
    ans_list = []
    for i, item in enumerate(st.session_state.qs):
        choice = st.radio(f"**{i+1}. {item['q']}**", item['options'], key=f"q_{i}")
        ans_list.append(f"שאלה: {item['q']} | תשובה: {choice}")

    if st.button("🚀 הפק תובנות סופיות"):
        with st.spinner("מנתח..."):
            names = [m['שם'] for m in st.session_state.cabinet]
            p_final = f"נושא: {idea}. תשובות: {ans_list}. קבינט: {names}. כתוב 5 תובנות וטבלה מסכמת."
            st.session_state.res = call_api(p_final)

if 'res' in st.session_state:
    st.markdown("---")
    st.markdown("### 📊 מסקנות הקבינט")
    st.write(st.session_state.res)