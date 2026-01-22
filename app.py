import streamlit as st
import requests
import json

st.set_page_config(page_title="קבינט העלית של אפי", layout="wide")

# המפתח החדש שייצרת
NEW_API_KEY = "AIzaSyDHmleHY-2_yfvsXqxxw_WQnXo-vCf9OfY" 

# שימוש במודל Gemini 1.5 Flash בגרסה העדכנית
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={NEW_API_KEY}"

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

# --- ממשק האפליקציה ---
st.title("🏛️ קבינט המוחות: נבחרת העלית")
st.markdown("### פילוסופיה | פסיכולוגיה | ניהול | ADHD")

idea = st.text_area("הזן את סוגיית הליבה לדיון:", height=150)

if st.button("🚀 הפעל סימולציית קבינט"):
    if idea:
        with st.spinner("המפתח החדש עובד! הקבינט מתכנס לדיון..."):
            prompt_text = f"""
            נתח עבור אפי את הסוגיה: "{idea}"
            
            המשתתפים בקבינט:
            1. לודוויג ויטגנשטיין וחנה ארנדט (פילוסופיה).
            2. זיגמונד פרויד, ז'אן פיאז'ה ואלברט בנדורה (פסיכולוגיה).
            3. פיטר דרוקר, ג'ק וולש וריד הופמן (ניהול).
            4. ד"ר אדוארד האלוול (מומחה ADHD).
            5. אורח בהפתעה: דמות אקראית ומפתיעה מתחום שונה שמתפרצת לדיון.

            הנחיות:
            - נהל ויכוח סוער ומרתק בין הדמויות.
            - כל דמות צריכה לתרום מהזווית הייחודית שלה לסוגיה.
            - בסוף, הסק 4 מסקנות מעשיות ואסטרטגיות לאפי.
            כתוב בעברית מקצועית ורהוטה.
            """
            
            payload = {"contents": [{"parts": [{"text": prompt_text}]}]}
            headers = {'Content-Type': 'application/json'}
            
            try:
                response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
                response_data = response.json()
                
                if response.status_code == 200:
                    text = response_data['candidates'][0]['content']['parts'][0]['text']
                    st.markdown(text)
                else:
                    st.error(f"שגיאה: {response.status_code}")
                    st.json(response_data)
            except Exception as e:
                st.error(f"תקלה בחיבור: {str(e)}")

st.divider()
st.caption("מערכת הקבינט | מחובר ב-API החדש | 2026")