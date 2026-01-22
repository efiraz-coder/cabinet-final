import streamlit as st
import requests
import json

st.set_page_config(page_title="קבינט העלית של אפי", layout="wide")

# המפתח המתוקן בדיוק לפי הצילום (עם האות l הקטנה)
CORRECT_API_KEY = "AIzaSyDHmleHY-2_yfvsXqxxw_WQnXo-vCf9OfY"

API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={CORRECT_API_KEY}"

# --- אבטחה ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    st.title("🏛️ כניסה לקבינט")
    pwd = st.text_input("הזן סיסמה:", type="password")
    if st.button("התחבר"):
        if pwd == "אפי2026":
            st.session_state['auth'] = True
            st.rerun()
    st.stop()

# --- ממשק ---
st.title("🏛️ קבינט המוחות: נבחרת העלית")
st.markdown("### ויטגנשטיין, ארנדט, פיאז'ה, בנדורה, דרוקר והאלוול")

idea = st.text_area("הזן את סוגיית הליבה לדיון:", height=150)

if st.button("🚀 הפעל סימולציה"):
    if idea:
        with st.spinner("המפתח אומת. הקבינט מתכנס כעת..."):
            prompt_text = f"""
            נתח עבור אפי את הסוגיה: "{idea}"
            המשתתפים: לודוויג ויטגנשטיין, חנה ארנדט, זיגמונד פרויד, ז'אן פיאז'ה, אלברט בנדורה, 
            פיטר דרוקר, ג'ק וולש, ריד הופמן וד"ר אדוארד האלוול (ADHD).
            הכנס 'אורח בהפתעה' אקראי שמתפרץ לדיון.
            צור ויכוח סוער והסק 4 מסקנות מעשיות לאפי.
            כתוב בעברית מקצועית.
            """
            
            payload = {"contents": [{"parts": [{"text": prompt_text}]}]}
            headers = {'Content-Type': 'application/json'}
            
            try:
                response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
                if response.status_code == 200:
                    text = response.json()['candidates'][0]['content']['parts'][0]['text']
                    st.markdown(text)
                else:
                    st.error(f"שגיאת שרת: {response.status_code}")
                    st.json(response.json())
            except Exception as e:
                st.error(f"תקלה: {str(e)}")

st.divider()
st.caption("קבינט המוחות | המפתח תוקן | 2026")