import streamlit as st
import requests
import json

st.set_page_config(page_title="קבינט העלית של אפי", layout="wide")

# המפתח שלך
API_KEY = "AIzaSyB12avvwGP6ECzfzTFOLDdfJHW37EQJvVo"
# שימוש ב-Gemini Pro בנתיב v1beta - השילוב הכי פחות "רגיש" לשגיאות
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={API_KEY}"

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
st.markdown("### המודל: Gemini Pro | ויטגנשטיין, ארנדט, פיאז'ה, בנדורה, דרוקר והאלוול")

idea = st.text_area("הזן את סוגיית הליבה לדיון (למשל: שוק הלידים בארה\"ב):", height=150)

if st.button("🚀 הפעל סימולציית קבינט"):
    if idea:
        with st.spinner("הקבינט מתכנס (Gemini Pro)..."):
            prompt_text = f"""
            נתח עבור אפי את הסוגיה הבאה: "{idea}"
            
            הקבינט כולל את:
            1. פילוסופים: לודוויג ויטגנשטיין וחנה ארנדט.
            2. פסיכולוגים: זיגמונד פרויד, ז'אן פיאז'ה ואלברט בנדורה.
            3. מומחי ניהול: פיטר דרוקר, ג'ק וולש וריד הופמן.
            4. רפואה: ד"ר אדוארד האלוול (מומחה ADHD).
            5. אורח בהפתעה: דמות אקראית ומפתיעה מתחום שונה לגמרי.

            הנחיות:
            - נהל ויכוח סוער בין המשתתפים. כל אחד תוקף את הנושא מהזווית שלו.
            - ויטגנשטיין ינתח את המילים שמשמשות למכירת הליד.
            - ד"ר האלוול ינתח את מצב הקשב של עורכי הדין (הלקוחות).
            - הסק 4 מסקנות מעשיות לאפי.
            כתוב בעברית מקצועית.
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
                    st.error(f"שגיאת שרת ({response.status_code})")
                    st.json(response_data)
            except Exception as e:
                st.error(f"תקלה בחיבור: {str(e)}")

st.divider()
st.caption("קבינט המוחות | Powered by Gemini Pro | 2026")