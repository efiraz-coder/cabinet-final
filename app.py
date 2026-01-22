import streamlit as st
import requests
import pandas as pd
import json
import re

# הגדרת דף
st.set_page_config(page_title="קבינט המוחות של אפי", layout="wide")

# CSS לתיקון ניראות מוחלטת של כפתורים וטקסט
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');

    /* רקע לבן מוחלט לאפליקציה */
    .stApp { background-color: #FFFFFF !important; }
    
    /* טקסט שחור עז וריווח שורות */
    html, body, [class*="st-"] {
        font-family: 'Assistant', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
        color: #000000 !important;
        line-height: 2.2 !important; 
    }

    /* תיקון כפתורים: כיתוב לבן על רקע שחור, תמיד גלוי */
    div.stButton > button {
        background-color: #000000 !important;
        color: #FFFFFF !important; /* כיתוב לבן */
        border: 2px solid #000000 !important;
        height: 3.5em !important;
        width: 100% !important;
        font-size: 1.4rem !important;
        font-weight: 800 !important; /* אותיות עבות */
        border-radius: 8px !important;
        opacity: 1 !important;
        display: block !important;
    }
    
    /* אפקט מעבר עכבר על כפתור */
    div.stButton > button:hover {
        background-color: #333333 !important;
        color: #FFFFFF !important;
    }

    /* הגדלת פונטים של שאלות ושדות קלט */
    p, li, label, span, input { font-size: 1.4rem !important; color: #000000 !important; }
    
    /* תיקון טבלת המשתתפים */
    [data-testid="stDataEditor"] {
        border: 2px solid #000000 !important;
        background-color: #FFFFFF !important;
    }
    </style>
    """, unsafe_allow_html=True)

# פונקציות ליבה
def call_gemini(prompt):
    try:
        API_KEY = st.secrets["GEMINI_KEY"]
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={API_KEY}"
        res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
        return res.json()['candidates'][0]['content']['parts'][0]['text']
    except: return "שגיאה בחיבור."

def extract_json(text):
    try:
        match = re.search(r'\[.*\]', text, re.DOTALL)
        return json.loads(match.group()) if match else None
    except: return None

# --- ממשק המשתמש ---

st.title("🏛️ קבינט המוחות של אפי")

# טבלת משתתפים גלויה
st.subheader("👥 חברי הקבינט (ערוך או הוסף שורות למטה)")
if 'participants_df' not in st.session_state:
    st.session_state['participants_df'] = pd.DataFrame([
        {"שם": "חנה ארנדט", "מומחיות": "פילוסופיה"},
        {"שם": "פיטר דרוקר", "מומחיות": "ניהול"},
        {"שם": "זיגמונד פרויד", "מומחיות": "פסיכולוגיה"}
    ])

st.session_state['participants_df'] = st.data_editor(
    st.session_state['participants_df'], 
    num_rows="dynamic", 
    use_container_width=True
)

st.markdown("---")

# שלב 1
st.subheader("🖋️ מה הנושא שעל הפרק?")
idea = st.text_area("תאר את הסוגיה כאן:", height=100)

if st.button("לחץ כאן ליצירת שאלון"):
    if idea:
        prompt = f"נושא: {idea}. נסח 4 שאלות אבחון פשוטות. החזר JSON בלבד: [{{'q': 'שאלה', 'options': ['1','2','3']}}, ...]"
        with st.spinner("מכין שאלות..."):
            raw = call_gemini(prompt)
            qs = extract_json(raw)
            if qs: st.session_state['qs'] = qs

# שלב 2
if 'qs' in st.session_state:
    st.subheader("📝 שאלון אבחון")
    ans_list = []
    for i, item in enumerate(st.session_state['qs']):
        st.markdown(f"**{i+1}. {item['q']}**")
        choice = st.radio(f"שאלה {i}", item['options'] + ["אחר"], key=f"radio_{i}")
        ans_list.append(f"ש: {item['q']} | ת: {choice}")

    if st.button("לחץ כאן לקבלת 5 תובנות"):
        members = ", ".join(st.session_state['participants_df']["שם"].tolist())
        prompt = f"""
        נושא: {idea}. תשובות: {ans_list}. קבינט: {members}.
        משימה:
        1. כתוב 5 תובנות אסטרטגיות פשוטות וברורות.
        2. הצג טבלה: | בעיה | פתרון | דרך | תפוקות | תשומות |
        """
        with st.spinner("כותב תובנות..."):
            st.session_state['result'] = call_gemini(prompt)

# שלב 3
if 'result' in st.session_state:
    st.markdown("### 📊 תוצאות הניתוח")
    st.write(st.session_state['result'])
    if st.button("התחל מחדש"):
        for k in ['qs', 'result']: 
            if k in st.session_state: del st.session_state[k]
        st.rerun()