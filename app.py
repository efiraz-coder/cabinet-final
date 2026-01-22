import streamlit as st
import requests
import json

st.set_page_config(page_title="קבינט העלית של אפי", layout="wide")

# הדבק כאן את המפתח החדש שייצרת הרגע
API_KEY = "AIzaSyAxt5rZVuevd2Drx9-uGKUCLfhPzFkGAEg" 

# כתובת ה-API של המודל היציב ביותר
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={API_KEY}"

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

st.title("🏛️ קבינט המוחות של אפי")
idea = st.text_area("הזן את סוגיית הליבה לדיון:", height=150)

if st.button("🚀 הפעל סימולציה"):
    if idea:
        with st.spinner("הקבינט מתכנס (Gemini Pro)..."):
            prompt_text = f"""
            נתח עבור אפי את הסוגיה: "{idea}"
            המשתתפים: ויטגנשטיין, חנה ארנדט, פרויד, פיאז'ה, בנדורה, דרוקר והאלוול.
            צור ויכוח והסק 4 מסקנות מעשיות.
            """
            
            payload = {"contents": [{"parts": [{"text": prompt_text}]}]}
            
            try:
                response = requests.post(API_URL, json=payload)
                if response.status_code == 200:
                    answer = response.json()['candidates'][0]['content']['parts'][0]['text']
                    st.markdown(answer)
                else:
                    st.error(f"שגיאה {response.status_code}")
                    st.json(response.json())
            except Exception as e:
                st.error(f"תקלה: {str(e)}")