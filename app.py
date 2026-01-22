import streamlit as st
import requests
import json

st.set_page_config(page_title="קבינט העלית של אפי", layout="wide")

# המפתח שלך - העתקתי אותו בדיוק מההודעה האחרונה שלך
API_KEY = "AIzaSyCoonPoQvGp0AfZ_M5LKlBJEfQV9pI1TJw" 

# הכתובת המעודכנת לגרסה 1 (זה הפתרון ל-404)
API_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"

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
st.title("🏛️ קבינט המוחות של אפי")
idea = st.text_area("הזן נושא לדיון:", height=150)

if st.button("🚀 הפעל סימולציה"):
    if idea:
        with st.spinner("הקבינט מתכנס (חיבור יציב v1)..."):
            prompt_text = f"נתח עבור אפי כקבינט של ארנדט, ויטגנשטיין, פיאז'ה, בנדורה, דרוקר, האלוול ואורח בהפתעה: {idea}. צור ויכוח והסק 4 מסקנות."
            
            payload = {"contents": [{"parts": [{"text": prompt_text}]}]}
            
            try:
                # שליחת הבקשה לכתובת החדשה
                response = requests.post(API_URL, json=payload)
                if response.status_code == 200:
                    answer = response.json()['candidates'][0]['content']['parts'][0]['text']
                    st.markdown(answer)
                else:
                    st.error(f"שגיאה {response.status_code}")
                    st.json(response.json())
            except Exception as e:
                st.error(f"תקלה: {str(e)}")