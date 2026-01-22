import streamlit as st
import requests
import json
import re
import random

# הגדרות דף - עיצוב נקי ומותאם לעברית
st.set_page_config(page_title="קבינט המוחות של אפי", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Assistant', sans-serif; direction: rtl; text-align: right; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; font-weight: bold; background-color: #bbdefb; border: 2px solid #1976d2; color: #000; }
    .expert-card { background-color: #ffffff; padding: 15px; border-right: 5px solid #1976d2; border-radius: 8px; margin-bottom: 15px; box-shadow: 1px 1px 5px rgba(0,0,0,0.1); color: #000; }
    .stRadio > label { font-weight: bold !important; color: #1976d2 !important; }
    </style>
    """, unsafe_allow_html=True)

# פונקציית API - גרסה יציבה למניעת שגיאות 404
def call_cabinet_api(prompt):
    if "GEMINI_KEY" not in st.secrets:
        st.error("⚠️ המפתח GEMINI_KEY לא נמצא ב-Secrets של Streamlit!")
        return None
    
    api_key = st.secrets["GEMINI_KEY"]
    # שימוש במודל gemini-pro שהוא היציב ביותר לכתובת הזו
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
    
    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            st.error(f"שגיאת שרת ({response.status_code}). וודא שהמפתח תקין ולחץ שוב.")
            return None
    except Exception as e:
        st.error(f"תקלה בתקשורת: {str(e)}")
        return None

# אתחול חברי הקבינט בזיכרון (אם עדיין לא קיימים)
if 'cabinet' not in st.session_state:
    pool_std = [
        {"שם": "פיטר דרוקר", "תואר": "אבי הניהול", "מומחיות": "אסטרטגיה וארגון"},
        {"שם": "זיגמונד פרויד", "תואר": "פסיכולוג", "מומחיות": "תת מודע ומוטיבציה"},
        {"שם": "דניאל כהנמן", "תואר": "כלכלן", "מומחיות": "קבלת החלטות ופסיכולוגיה"}
    ]
    pool_surp = [
        {"שם": "סון דזו", "תואר": "אסטרטג סיני", "מומחיות": "אמנות המלחמה ותמרון"},
        {"שם": "סטיב ג'ובס", "תואר": "יזם", "מומחיות": "חדשנות וחוויית משתמש"},
        {"שם": "חנה ארנדט", "תואר": "פילוסופית", "מומחיות": "אתיקה, חברה וכוח"},
        {"שם": "מרקוס אורליוס", "תואר": "קיסר רומי", "מומחיות": "חוסן מנטלי וסטואיציזם"}
    ]
    st.session_state.cabinet = pool_std + random.sample(pool_surp, 3)

# --- ממשק משתמש (UI) ---
st.title("🏛️ קבינט המוחות של אפי")
st.subheader("היועצים האסטרטגיים שלך מוכנים לפעולה")

# הצגת חברי הקבינט הנוכחיים
cols = st.columns(3)
for i, m in enumerate(st.session_state.cabinet):
    with cols[i % 3]:
        st.info(f"👤 **{m['שם']}**\n\n{m['תואר']}")

st.markdown("---")

# תיאור האתגר
idea = st.text_area("🖋️ מה האתגר או הבעיה שתרצה להציג לקבינט?", height=120, placeholder="למשל: איך לבנות תוכנית עבודה לשנה הבאה שתגדיל את הרווחיות?")

if st.button("🔍 שלח לאבחון המומחים"):
    if idea:
        with st.spinner("חברי הקבינט דנים בבעיה ומנסחים שאלות..."):
            experts_list = ", ".join([f"{m['שם']} ({m['מומחיות']})" for m in st.session_state.cabinet])
            prompt = f"""
            Task: Act as a board of experts for this challenge: "{idea}".
            The experts are: {experts_list}.
            Instructions: Each expert must ask one unique, sharp diagnostic question based on their expertise.
            Output: Return ONLY a valid JSON array.
            Format: [{"expert": "Expert Name", "q": "The Question", "options": ["Option 1", "Option 2", "Option 3"]}]
            Total: 6 questions. Language: Hebrew.
            """
            
            raw = call_cabinet_api(prompt)
            if raw:
                # ניקוי שאריות מה-AI כדי לחלץ רק את ה-JSON
                clean_raw = raw.replace('```json', '').replace('```', '').strip()
                match = re.search(r'\[.*\]', clean_raw, re.DOTALL)
                if match:
                    st.session_state.qs = json.loads(match.group())
                    st.session_state.pop('final_result', None) # איפוס תוצאות קודמות
                    st.rerun()
                else:
                    st.error("הקבינט שלח תשובה שאינה בפורמט הנכון. נסה ללחוץ שוב.")

# הצגת שאלון האבחון
if 'qs' in st.session_state and st.session_state.qs:
    st.markdown("---")
    st.subheader("📝 שאלות האבחון של חברי הקבינט")
    user_answers = []
    
    for i, item in enumerate(st.session_state.qs):
        st.markdown(f"<div class='expert-card'>💡 <b>{item['expert']}</b> שואל/ת:</div>", unsafe_allow_html=True)
        choice = st.radio(item['q'], item['options'], key=f"ans_{i}")
        user_answers.append(f"מומחה: {item['expert']} | שאלה: {item['q']} | תשובה: {choice}")
    
    st.markdown("---")
    if st.button("🚀 הפק דו\"ח תובנות סופי"):
        with st.spinner("הקבינט מסכם את המלצותיו..."):
            final_prompt = f"האתגר: {idea}. התשובות שניתנו: {user_answers}. כתוב 5 תובנות אסטרטגיות עמוקות המשלבות את דעות המומחים, וטבלה מסכמת עם צעדי פעולה (Action Items)."
            st.session_state.final_result = call_cabinet_api(final_prompt)

# הצגת התוצאה הסופית
if 'final_result' in st.session_state:
    st.markdown("---")
    st.success("📊 המלצות הקבינט של אפי:")
    st.markdown(st.session_state.final_result)