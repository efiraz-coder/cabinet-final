import streamlit as st
import requests
import json

st.set_page_config(page_title="קבינט המוחות של אפי", layout="wide")

def call_gemini(prompt):
    if "GEMINI_KEY" not in st.secrets:
        st.error("המפתח חסר ב-Secrets!")
        return None
    
    # שימוש בכתובת הכי יציבה שיש היום
    api_key = st.secrets["GEMINI_KEY"]
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    try:
        res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=15)
        if res.status_code == 200:
            return res.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            # אם גם זה נכשל, ננסה כתובת חלופית אוטומטית
            st.error(f"שגיאת שרת {res.status_code}. גוגל אומר: {res.text}")
            return None
    except Exception as e:
        st.error(f"תקלה טכנית: {str(e)}")
        return None

st.title("🏛️ קבינט המוחות של אפי")

idea = st.text_area("🖋️ מה האתגר שלך?", height=100)

if st.button("🔍 התחל אבחון"):
    if idea:
        with st.spinner("בודק חיבור לקבינט..."):
            test_prompt = "ענה במילה אחת בלבד: האם אתה עובד?"
            response = call_gemini(test_prompt)
            if response:
                st.success("✅ הקבינט מחובר!")
                st.write(f"תשובת המומחים: {response}")
            else:
                st.error("❌ החיבור נכשל. בדוק אם יצרת מפתח ב-AI Studio תחת 'New Project'.")

st.info("טיפ: וודא שהמפתח נוצר ב-Google AI Studio ולא ב-Google Cloud Console.")