import streamlit as st
import requests
import json
import re
import random

# הגדרות דף
st.set_page_config(page_title="קבינט המוחות של אפי", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Assistant', sans-serif; direction: rtl; text-align: right; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; font-weight: bold; background-color: #bbdefb; border: 2px solid #1976d2; color: #000; }
    .expert-card { background-color: #ffffff; padding: 15px; border-right: 5px solid #1976d2; border-radius: 8px; margin-bottom: 15px; box-shadow: 1px 1px 5px rgba(0,0,0,0.1); color: #000; }
    </style>
    """, unsafe_allow_html=True)

def call_cabinet_api(prompt):
    if "GEMINI_KEY" not in st.secrets:
        st.error("⚠️ המפתח GEMINI_KEY לא נמצא ב-Secrets!")
        return None
    
    api_key = st.secrets["GEMINI_KEY"]
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            st.error(f"שגיאת שרת ({response.status_code})")
            return None
    except Exception as e:
        st.error(f"תקלה: {str(e)}")
        return None

if 'cabinet' not in st.session_state:
    pool = [
        {"שם": "פיטר דרוקר", "תואר": "אבי הניהול", "מומחיות": "אסטרטגיה"},
        {"שם": "סטיב ג'ובס", "תואר": "יזם", "מומחיות": "חדשנות"},
        {"שם": "סון דזו", "תואר": "אסטרטג סיני", "מומחיות": "טקטיקה"},
        {"שם": "זיגמונד פרויד", "תואר": "פסיכולוג", "מומחיות": "נפש האדם"},
        {"שם": "דניאל כהנמן", "תואר": "כלכלן", "מומחיות": "קבלת החלטות"},
        {"שם": "מרקוס אורליוס", "תואר": "קיסר רומי", "מומחיות": "חוסן"}
    ]
    st.session_state.cabinet = random.sample(pool, 6)

st.title("🏛️ קבינט המוחות של אפי")

cols = st.columns(3)
for i, m in enumerate(st.session_state.cabinet):
    with cols[i % 3]:
        st.info(f"👤 **{m['שם']}**\n\n{m['תואר']}")

idea = st.text_area("🖋️ מה האתגר שלך?", height=120)

if st.button("🔍 שלח לאבחון המומחים"):
    if idea:
        with st.spinner("הקבינט מנסח שאלות..."):
            experts_list = ", ".join([m['שם'] for m in st.session_state.cabinet])
            
            # שים לב לסוגריים הכפולים {{ }} כאן למטה - זה התיקון!
            prompt = f"""
            Task: Act as a board of experts for: "{idea}".
            Experts: {experts_list}.
            Output: Return ONLY a valid JSON array.
            Format: [{{ "expert": "Name", "q": "Question", "options": ["1", "2", "3"] }}]
            Language: Hebrew.
            """
            
            raw = call_cabinet_api(prompt)
            if raw:
                clean_raw = raw.replace('```json', '').replace('```', '').strip()
                match = re.search(r'\[.*\]', clean_raw, re.DOTALL)
                if match:
                    st.session_state.qs = json.loads(match.group())
                    st.rerun()

if 'qs' in st.session_state:
    st.markdown("---")
    user_answers = []
    for i, item in enumerate(st.session_state.qs):
        st.markdown(f"<div class='expert-card'>💡 <b>{item['expert']}</b> שואל/ת:</div>", unsafe_allow_html=True)
        choice = st.radio(item['q'], item['options'], key=f"ans_{i}")
        user_answers.append(f"{item['expert']}: {choice}")
    
    if st.button("🚀 הפק דו\"ח תובנות"):
        with st.spinner("מסכם..."):
            final_p = f"האתגר: {idea}. תשובות: {user_answers}. סכם ב-5 תובנות וטבלה."
            st.session_state.final_result = call_cabinet_api(final_p)

if 'final_result' in st.session_state:
    st.success("📊 המלצות הקבינט:")
    st.markdown(st.session_state.final_result)