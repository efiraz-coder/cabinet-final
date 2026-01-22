import streamlit as st
import requests

st.set_page_config(page_title="קבינט המוחות של אפי", layout="wide")

# המפתח שלך
API_KEY = "AIzaSyAxt5rZVuevd2Drx9-uGKUCLfhPzFkGAEg"

# פונקציה לבדיקה מה גוגל מרשה לנו
def get_available_models():
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
    response = requests.get(url)
    return response.json()

st.title("🏛️ קבינט המוחות: בדיקת חיבור")

# כפתור בדיקה
if st.button("🔍 בדוק אילו מודלים זמינים לי"):
    models_data = get_available_models()
    st.write("גוגל אומרת שהמודלים הבאים פתוחים עבורך:")
    st.json(models_data)

st.divider()

# ניסיון הרצה עם שם מודל גנרי (ללא מספר גרסה ספציפי)
idea = st.text_input("הזן נושא לבדיקה:")
if st.button("🚀 נסה להפעיל"):
    # אנחנו מנסים את השם הכי בסיסי שקיים במערכת
    test_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={API_KEY}"
    payload = {"contents": [{"parts": [{"text": f"תגיד שלום לאפי: {idea}"}]}]}
    
    res = requests.post(test_url, json=payload)
    if res.status_code == 200:
        st.success("הצלחה! הקבינט יכול לעבוד.")
        st.write(res.json()['candidates'][0]['content']['parts'][0]['text'])
    else:
        st.error(f"שגיאה {res.status_code}. לחץ על הכפתור למעלה כדי לראות איזה מודל גוגל רוצה.")
        st.json(res.json())