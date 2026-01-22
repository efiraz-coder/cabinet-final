import streamlit as st
import requests
import json

st.set_page_config(page_title="קבינט העלית של אפי", layout="wide")

# משיכת המפתח מה-Secrets בצורה מאובטחת
try:
    API_KEY = st.secrets["GEMINI_KEY"]
except:
    st.error("שגיאה: המפתח לא נמצא ב-Secrets של Streamlit!")
    st.stop()

# שימוש במודל Gemini 2.5 Pro היציב
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={API_KEY}"

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
idea = st.text_area("הזן סוגיית ליבה לדיון:", height=150)

if st.button("🚀 הפעל סימולציית קבינט"):
    if idea:
        with st.spinner("הקבינט של 2026 מתכנס לדיון (חיבור מאובטח)..."):
            prompt_text = f"נתח עבור אפי כקבינט של ארנדט, ויטגנשטיין, דרוקר והאלוול: {idea}. צור ויכוח והסק 4 מסקנות."
            payload = {"contents": [{"parts": [{"text": prompt_text}]}]}
            
            try:
                response = requests.post(API_URL, json=payload)
                if response.status_code == 200:
                    answer = response.json()['candidates'][0]['content']['parts'][0]['text']
                    st.markdown(answer)
                else:
                    st.error(f"שגיאת שרת {response.status_code}")
                    st.json(response.json())
            except Exception as e:
                st.error(f"תקלה בחיבור: {str(e)}")

st.divider()
st.caption("קבינט המוחות | חיבור מאובטח | 2026")