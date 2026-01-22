import streamlit as st
import requests
import json

st.set_page_config(page_title="קבינט העלית של אפי", layout="wide")

# המפתח התקין שלך
API_KEY = "AIzaSyAxt5rZVuevd2Drx9-uGKUCLfhPzFkGAEg"

# שם המודל המדויק מהרשימה ששלחת (Gemini 2.5 Pro)
MODEL_NAME = "gemini-2.5-pro"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"

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

# --- ממשק הקבינט ---
st.title("🏛️ קבינט המוחות של אפי")
st.markdown("### המודל: Gemini 2.5 Pro | ויטגנשטיין, ארנדט, דרוקר והאלוול")

idea = st.text_area("הזן סוגיית ליבה לדיון:", height=150, placeholder="על מה נדבר היום?")

if st.button("🚀 הפעל סימולציית קבינט"):
    if idea:
        with st.spinner("הקבינט של 2026 מתכנס לדיון..."):
            prompt_text = f"""
            נתח עבור אפי את הסוגיה: "{idea}"
            המשתתפים: לודוויג ויטגנשטיין, חנה ארנדט, זיגמונד פרויד, ז'אן פיאז'ה, אלברט בנדורה, 
            פיטר דרוקר, ג'ק וולש, ריד הופמן וד"ר אדוארד האלוול.
            הכנס 'אורח בהפתעה' והסק 4 מסקנות מעשיות.
            כתוב בעברית מקצועית ומרתקת.
            """
            
            payload = {"contents": [{"parts": [{"text": prompt_text}]}]}
            
            try:
                response = requests.post(API_URL, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
                
                if response.status_code == 200:
                    answer = response.json()['candidates'][0]['content']['parts'][0]['text']
                    st.success("חיבור הצליח - Gemini 2.5 Pro בפעולה!")
                    st.markdown(answer)
                else:
                    st.error(f"שגיאה {response.status_code}")
                    st.json(response.json())
            except Exception as e:
                st.error(f"תקלה בחיבור: {str(e)}")

st.divider()
st.caption("קבינט המוחות | Powered by Gemini 2.5 Pro | 2026")