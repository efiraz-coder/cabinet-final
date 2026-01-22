import streamlit as st
import google.generativeai as genai

# הגדרות דף
st.set_page_config(page_title="קבינט העלית של אפי", layout="wide")

# חיבור ל-API
API_KEY = "AIzaSyB12avvwGP6ECzfzTFOLDdfJHW37EQJvVo"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- מנגנון סיסמה ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    st.title("🏛️ כניסה לקבינט העלית")
    pwd = st.text_input("הזן סיסמה:", type="password")
    if st.button("התחבר"):
        if pwd == "אפי2026":
            st.session_state['auth'] = True
            st.rerun()
        else:
            st.error("סיסמה שגויה")
    st.stop()

# --- ממשק האפליקציה ---
st.title("🏛️ קבינט המוחות: הנבחרת המורחבת")
st.markdown("### ארנדט וויטגנשטיין | פרויד, פיאז'ה ובנדורה | דרוקר, וולש והופמן | ד\"ר האלוול")

idea = st.text_area("הזן את סוגיית הליבה (למשל: איך למכור לידים לעורכי דין שסובלים מהצפת מידע):", height=150)

if st.button("🚀 הפעל סימולציית קבינט"):
    if not idea:
        st.warning("בבקשה הכנס נושא לדיון.")
    else:
        with st.spinner("הקבינט מתכנס לויכוח סוער..."):
            try:
                prompt = f"""
                נתח עבור אפי את סוגיית הליבה: "{idea}"
                
                הקבינט מורכב מהדמויות הבאות:
                1. פילוסופים: לודוויג ויטגנשטיין (ניתוח שפה ומשמעות) וחנה ארנדט (חשיבה ביקורתית והמרחב הציבורי).
                2. פסיכולוגים: זיגמונד פרויד (תת-מודע), ז'אן פיאז'ה (התפתחות קוגניטיבית) ואלברט בנדורה (למידה חברתית וחיקוי).
                3. מומחי ניהול: פיטר דרוקר (יעילות), ג'ק וולש (אגרסיביות) וריד הופמן (צמיחה מהירה).
                4. רפואה: ד"ר אדוארד האלוול (מומחה ADHD וקשב).
                5. אורח בהפתעה: דמות אקראית לחלוטין מתחום שונה (אמנות, צבא, היסטוריה).

                הנחיות לסימולציה:
                - צור ויכוח פורה: ויטגנשטיין יבקר את השפה של הלידים, ארנדט תדבר על האתיקה, בנדורה יסביר איך ליצור אפקט "עדר".
                - ד"ר האלוול ינתח את "כלכלת הקשב" והפרעת הקשב של השוק.
                - האורח בהפתעה יתפרץ באמצע הויכוח עם תובנה לא קשורה שהופכת לרלוונטית.
                - בסוף: 4 מסקנות אסטרטגיות בשורה התחתונה לאפי.
                
                כתוב בעברית עשירה ומקצועית.
                """
                
                response = model.generate_content(prompt)
                st.divider()
                st.markdown(response.text)
            except Exception as e:
                st.error(f"שגיאה: {str(e)}")

st.divider()
st.caption("מערכת הקבינט | גרסת העלית המעודכנת 2026")