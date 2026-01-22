import streamlit as st
import requests
import json
import re
import random

# הגדרות דף ועיצוב (UI)
st.set_page_config(page_title="קבינט המוחות של אפי", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Assistant', sans-serif; direction: rtl; text-align: right; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; font-weight: bold; background-color: #bbdefb; border: 2px solid #1976d2; }
    .expert-card { background-color: #ffffff; padding: 15px; border-right: 5px solid #1976d2; border-radius: 8px; margin-bottom: 15px; box-shadow: 1px 1px 5px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# פונקציה לתקשורת עם ה-API של גוגל
def call_cabinet_api(prompt):
    # משיכת המפתח מה-Secrets שהגדרת
    if "GEMINI_KEY" not in st.secrets:
        st.error("⚠️ המפתח GEMINI_KEY לא נמצא ב-Secrets של Streamlit!")
        return None
    
    api_key = st.secrets["GEMINI_KEY"]
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    try:
        response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=30)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            st.error(f"שגיאת שרת ({response.status_code}). נסה ללחוץ שוב.")
            return None
    except Exception as e:
        st.error(f"תקלה בתקשורת: {str(e)}")
        return None

# אתחול חברי הקבינט (3 קבועים ו-3 משתנים)
if 'cabinet' not in st.session_state:
    pool_std = [
        {"שם": "פיטר דרוקר", "תואר": "אבי הניהול", "מומחיות": "אסטרטגיה וארגון"},
        {"שם": "זיגמונד פרויד", "תואר": "פסיכולוג", "מומחיות": "תת מודע ודחפים"},
        {"שם": "דניאל כהנמן", "תואר": "כלכלן", "מומחיות": "קבלת החלטות"}
    ]
    pool_surp = [
        {"שם": "סון דזו", "תואר": "אסטרטג צבאי", "מומחיות": "אמנות המלחמה"},
        {"שם": "סטיב ג'ובס", "תואר": "יזם", "מומחיות": "חדשנות ועיצוב"},
        {"שם": "חנה ארנדט", "תואר": "פילוסופית", "מומחיות": "אתיקה וחברה"},
        {"שם": "לאונרדו דה וינצ'י", "תואר": "איש אשכולות", "מומחיות": "פתרון בעיות יצירתי"}
    ]
    st.session_state.cabinet = pool_std + random.sample(pool_surp, 3)

# --- ממשק משתמש ---
st.title("🏛️ קבינט המוחות של אפי")
st.write("ברוך הבא לקבינט. המומחים מחכים לאתגר שלך.")

# תיאור הבעיה
idea = st.text_area("🖋️ תאר את האתגר או הבעיה שעל הפרק:", height=120, placeholder="למשל: איך אני יכול להגדיל את המכירות בעסק שלי ב-20% בחצי שנה?")

if st.button("🔍 התחל סבב שאלות אבחון"):
    if idea:
        with st.spinner("חברי הקבינט מנתחים את הבעיה ומנסחים שאלות..."):
            experts_info = ", ".join([f"{m['שם']} ({m['מומחיות']})" for m in st.session_state.cabinet])
            prompt = f"""נושא: {idea}. 
            חברי הקבינט: {experts_info}.
            עבור כל חבר קבינט, נסח שאלה אחת ספציפית וקצרה שמתאימה למומחיותו.
            החזר אך ורק פורמט JSON תקני במבנה הבא: 
            [
              {{"expert": "שם המומחה", "q": "השאלה שלו", "options": ["תשובה 1", "תשובה 2", "תשובה 3"]}}
            ]
            סה"כ 6 שאלות."""
            
            raw = call_cabinet_api(prompt)
            if raw:
                # ניקוי פורמט JSON מהתשובה
                clean_raw = raw.replace('```json', '').replace('```', '').strip()
                match = re.search(r'\[.*\]', clean_raw, re.DOTALL)
                if match:
                    st.session_state.qs = json.loads(match.group())
                    st.session_state.pop('final_result', None) # איפוס תוצאות קודמות
                else:
                    st.error("הקבינט שלח תשובה לא ברורה. נסה שוב.")

# הצגת השאלון במידה והוא נוצר
if 'qs' in st.session_state and st.session_state.qs:
    st.markdown("---")
    st.subheader("📝 שאלות האבחון של חברי הקבינט")
    user_answers = []
    
    for i, item in enumerate(st.session_state.qs):
        st.markdown(f"<div class='expert-card'><b>{item['expert']} שואל/ת:</b></div>", unsafe_allow_html=True)
        choice = st.radio(item['q'], item['options'], key=f"choice_{i}")
        user_answers.append(f"מומחה: {item['expert']} | שאלה: {item['q']} | תשובה: {choice}")
    
    if st.button("🚀 הפק תובנות אסטרטגיות"):
        with st.spinner("הקבינט מעבד את כל המידע למסקנות..."):
            final_prompt = f"הבעיה: {idea}. התשובות שניתנו: {user_answers}. כתוב 5 תובנות אסטרטגיות עמוקות וטבלה מסכמת הכוללת: בעיה, פתרון מוצע, וצעדים לביצוע."
            st.session_state.final_result = call_cabinet_api(final_prompt)

# הצגת תוצאות סופיות
if 'final_result' in st.session_state:
    st.markdown("---")
    st.success("📊 סיכום הדיון והמלצות הקבינט:")
    st.write(st.session_state.final_result)