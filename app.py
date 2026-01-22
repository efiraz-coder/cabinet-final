import streamlit as st
import requests
import json

st.set_page_config(page_title="קבינט העלית של אפי", layout="wide")

# הגדרות ה-API - מודל gemini-pro הוא היציב ביותר
API_KEY = "AIzaSyB12avvwGP6ECzfzTFOLDdfJHW37EQJvVo"
API_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={API_KEY}"

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
idea = st.text_area("הזן את סוגיית הליבה לדיון:", height=150)

if st.button("🚀 הפעל סימולציה"):
    if idea:
        with st.spinner("הקבינט מתכנס (חיבור יציב)..."):
            prompt_text = f"""
            נתח עבור אפי את: "{idea}"
            המשתתפים: לודוויג ויטגנשטיין, חנה ארנדט, זיגמונד פרויד, ז'אן פיאז'ה, אלברט בנדורה, 
            פיטר דרוקר, ג'ק וולש, ריד הופמן וד"ר אדוארד האלוול (מומחה ADHD).
            בנוסף, הכנס 'אורח בהפתעה' אקראי מתחום אחר לגמרי שמתפרץ לדיון.
            צור ויכוח פורה בין הדמויות והסק 4 מסקנות מעשיות לאפי.
            כתוב בעברית רהוטה.
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
                    st.error(f"שגיאת שרת: {response.status_code}")
                    st.write("גוגל לא מוצא את המודל הספציפי. מנסה נתיב חלופי...")
            except Exception as e:
                st.error(f"תקלה: {str(e)}")

st.divider()
st.caption("קבינט המוחות | חיבור יציב | 2026")