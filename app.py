import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="קבינט העלית של אפי", layout="wide")

# חיבור ל-API
genai.configure(api_key="AIzaSyB12avvwGP6ECzfzTFOLDdfJHW37EQJvVo")

# שימוש בשם המודל המדויק והמעודכן ביותר
model = genai.GenerativeModel('gemini-1.5-flash-latest')

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

st.title("🏛️ קבינט המוחות: נבחרת העלית")
idea = st.text_area("הזן את סוגיית הליבה לדיון:", height=150)

if st.button("🚀 הפעל סימולציה"):
    with st.spinner("הקבינט מתכנס..."):
        try:
            prompt = f"""
            נתח את הסוגייה: "{idea}"
            המשתתפים: ויטגנשטיין, חנה ארנדט, פרויד, פיאז'ה, אלברט בנדורה, דרוקר, וולש, ריד הופמן וד"ר האלוול (ADHD).
            הוסף אורח אקראי בהפתעה מתחום שונה לגמרי.
            צור ויכוח סוער ופורה והסק 4 מסקנות מעשיות לאפי.
            """
            # הכרחי למנוע שגיאת 404
            response = model.generate_content(prompt)
            st.markdown(response.text)
        except Exception as e:
            st.error(f"שגיאה: {str(e)}")