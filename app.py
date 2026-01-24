import streamlit as st
import requests
import json
import re
import random

st.set_page_config(page_title="קבינט המוחות של אפי", layout="wide")

# --- פונקציית API חכמה שמנסה כמה מודלים ---
def call_cabinet_api(prompt):
    if "GEMINI_KEY" not in st.secrets:
        st.error("⚠️ המפתח חסר ב-Secrets!")
        return None
    
    api_key = st.secrets["GEMINI_KEY"]
    # רשימת מודלים אפשריים לפי סדר עדיפות
    models_to_try = [
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-pro"
    ]
    
    last_error = ""
    for model_name in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        try:
            res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=10)
            if res.status_code == 200:
                return res.json()['candidates'][0]['content']['parts'][0]['text']
            else:
                last_error = res.text
                continue # נכשל? נסה את המודל הבא
        except:
            continue
            
    st.error(f"כל המודלים נכשלו. שגיאה אחרונה: {last_error}")
    return None

# --- עיצוב וממשק ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Assistant', sans-serif; direction: rtl; text-align: right; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; font-weight: bold; background-color: #bbdefb; border: 2px solid #1976d2; }
    </style>
    """, unsafe_allow_html=True)

if 'cabinet' not in st.session_state:
    pool = [{"שם": "פיטר דרוקר", "תואר": "אסטרטגיה"}, {"שם": "סטיב ג'ובס", "תואר": "יזמות"}, {"שם": "סון דזו", "תואר": "טקטיקה"}]
    st.session_state.cabinet = pool

st.title("🏛️ קבינט המוחות של אפי")

idea = st.text_area("🖋️ מה האתגר שלך?", height=120)

if st.button("🔍 התחל אבחון"):
    if idea:
        with st.spinner("הקבינט בודק תקשורת ומנסח שאלות..."):
            prompt = f"נושא: {idea}. נסח 3 שאלות אבחון בפורמט JSON בלבד: [{{'expert': '...', 'q': '...', 'options': ['1','2','3']}}]"
            raw = call_cabinet_api(prompt)
            if raw:
                match = re.search(r'\[.*\]', raw.replace('```json', '').replace('```', ''), re.DOTALL)
                if match:
                    st.session_state.qs = json.loads(match.group())
                    st.rerun()

if 'qs' in st.session_state:
    for i, item in enumerate(st.session_state.qs):
        st.write(f"💡 **{item['expert']}** שואל:")
        st.radio(item['q'], item['options'], key=f"q_{i}")
    
    if st.button("🚀 הפק דו\"ח"):
        st.write("מכין דו\"ח...")