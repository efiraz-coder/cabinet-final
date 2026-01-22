import streamlit as st
import requests
import json

st.set_page_config(page_title="קבינט העלית של אפי", layout="wide")

# המפתח האחרון ששלחת - הוספתי לו הגנה מרווחים
RAW_KEY = "AIzaSyCoonPoQvGp0AfZ_M5LKlBJEfQV9pI1TJw" 
API_KEY = RAW_KEY.strip()

# כתובת ה-API היציבה ביותר
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

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
st.markdown("### ויטגנשטיין, ארנדט, פיאז'ה, בנדורה, דרוקר, וולש, הופמן והאלוול")

idea = st.text_area("הזן נושא לדיון:", height=150, placeholder="למשל: אסטרטגיית לידים לעורכי דין...")

if st.button("🚀 הפעל סימולציה"):
    if idea:
        with st.spinner("הקבינט מתכנס..."):
            prompt_text = f"""
            נתח עבור אפי את: "{idea}"
            המשתתפים: לודוויג ויטגנשטיין, חנה ארנדט, זיגמונד פרויד, ז'אן פיאז'ה, אלברט בנדורה, 
            פיטר דרוקר, ג'ק וולש, ריד הופמן וד"ר אדוארד האלוול.
            הוסף אורח בהפתעה והסק 4 מסקנות מעשיות.
            כתוב בעברית.
            """
            
            payload = {"contents": [{"parts": [{"text": prompt_text}]}]}
            
            try:
                response = requests.post(API_URL, json=payload)
                if response.status_code == 200:
                    answer = response.json()['candidates'][0]['content']['parts'][0]['text']
                    st.markdown(answer)
                else:
                    st.error(f"שגיאה {response.status_code}: גוגל לא מאשר את המפתח.")
                    st.write("נסה להעתיק שוב את המפתח מ-AI Studio, וודא שלא חסרה אות בסוף.")
            except Exception as e:
                st.error(f"תקלה: {str(e)}")

st.divider()
st.caption("קבינט המוחות | 2026")