import streamlit as st
import requests
import json

st.set_page_config(page_title="קבינט העלית של אפי", layout="wide")

# המפתח החדש והתקין שלך
NEW_API_KEY = "AIzaSyAxt5rZVuevd2Drx9-uGKUCLfhPzFkGAEg"

# הכתובת היציבה ביותר של גוגל למפתח הזה
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={NEW_API_KEY}"

# --- מנגנון כניסה ---
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

# --- ממשק הקבינט ---
st.title("🏛️ קבינט המוחות של אפי")
st.markdown("### ויטגנשטיין, ארנדט, פיאז'ה, בנדורה, דרוקר, הופמן והאלוול")

idea = st.text_area("הזן סוגיית ליבה לדיון (למשל: אסטרטגיה עסקית או ADHD):", height=150)

if st.button("🚀 הפעל סימולציה"):
    if idea:
        with st.spinner("המפתח אומת! הקבינט מתכנס לדיון..."):
            prompt_text = f"""
            נתח עבור אפי את הסוגיה: "{idea}"
            השתתפות: לודוויג ויטגנשטיין, חנה ארנדט, זיגמונד פרויד, ז'אן פיאז'ה, אלברט בנדורה, 
            פיטר דרוקר, ג'ק וולש, ריד הופמן וד"ר אדוארד האלוול.
            הוסף 'אורח בהפתעה' והסק 4 מסקנות מעשיות.
            כתוב בעברית מקצועית ורהוטה.
            """
            
            payload = {"contents": [{"parts": [{"text": prompt_text}]}]}
            
            try:
                response = requests.post(API_URL, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
                
                if response.status_code == 200:
                    answer = response.json()['candidates'][0]['content']['parts'][0]['text']
                    st.success("החיבור הצליח!")
                    st.markdown(answer)
                else:
                    st.error(f"שגיאה {response.status_code}")
                    st.json(response.json())
            except Exception as e:
                st.error(f"תקלה בחיבור: {str(e)}")

st.divider()
st.caption("קבינט המוחות | מפתח מעודכן | 2026")