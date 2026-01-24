import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="קבינט המוחות של אפי", layout="wide")

if "GEMINI_KEY" not in st.secrets:
    st.error("המפתח חסר ב-Secrets!")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_KEY"])

st.title("🏛️ קבינט המוחות של אפי")

# פונקציה שמוצאת מודל עובד בחשבון שלך
def get_working_model():
    try:
        # רשימת כל המודלים שזמינים למפתח שלך
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if available_models:
            # נבחר את המודל הכי מתקדם שיש ברשימה
            for preferred in ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']:
                if preferred in available_models:
                    return preferred
            return available_models[0] # אם לא מצאנו מה שרצינו, ניקח את הראשון
        return None
    except Exception as e:
        st.error(f"שגיאה בסריקת מודלים: {e}")
        return None

if st.button("בצע בדיקת חיבור סופית"):
    with st.spinner("סורק מודלים זמינים בחשבון שלך..."):
        model_name = get_working_model()
        if model_name:
            st.success(f"✅ נמצא מודל פעיל: {model_name}")
            try:
                model = genai.GenerativeModel(model_name)
                res = model.generate_content("תגיד שלום")
                st.write("תשובת המודל:", res.text)
            except Exception as e:
                st.error(f"נמצא מודל אבל הוא לא מגיב: {e}")
        else:
            st.error("❌ לא נמצא שום מודל פעיל בחשבון הזה. וודא שיצרת את המפתח ב-Google AI Studio.")

st.info("אם הבדיקה מצליחה, אני אבנה לך את כל הקבינט סביב השם שנמצא.")