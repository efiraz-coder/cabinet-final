import streamlit as st
import google.generativeai as genai
import json
import re
import random

# הגדרות דף
st.set_page_config(page_title="קבינט המוחות של אפי", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Assistant', sans-serif; direction: rtl; text-align: right; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; font-weight: bold; background-color: #f0f2f6; border: 1px solid #d1d5db; }
    .expert-box { background-color: #ffffff; padding: 10px; border: 1px solid #e5e7eb; border-radius: 8px; text-align: center; margin-bottom: 10px; }
    .question-card { background-color: #f9fafb; padding: 20px; border-radius: 12px; margin-bottom: 20px; border-right: 4px solid #3b82f6; }
    </style>
    """, unsafe_allow_html=True)

# חיבור ל-API
if "GEMINI_KEY" not in st.secrets:
    st.error("המפתח חסר ב-Secrets!")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_KEY"])
MODEL_NAME = "gemini-1.5-flash" # המודל היציב ביותר כרגע

# מאגר מומחים לפי קטגוריות
POOL = {
    "פילוסופיה": ["סוקרטס", "אריסטו", "חנה ארנדט", "פרידריך ניטשה", "מרקוס אורליוס", "סימון דה בובואר"],
    "פסיכולוגיה": ["זיגמונד פרויד", "קארל יונג", "ויקטור פראנקל", "מלאני קליין", "דניאל כהנמן", "אברהם מאסלו"],
    "תרבות": ["מרשל מקלוהן", "אדוארד סעיד", "רולאן בארת", "ניל פוסטמן", "יובל נח הררי", "מרגרט מיד"],
    "הפתעה": ["לאונרדו דה וינצ'י", "סטיב ג'ובס", "סון דזו", "אלברט איינשטיין", "מארי קירי", "שייקספיר"]
}

def get_new_cabinet():
    cabinet = []
    for cat in ["פילוסופיה", "פסיכולוגיה", "תרבות", "הפתעה"]:
        cabinet.extend([{"name": n, "cat": cat} for n in random.sample(POOL[cat], 2)])
    return cabinet

# ניהול מצב (Session State)
if 'cabinet' not in st.session_state:
    st.session_state.cabinet = get_new_cabinet()

# --- ממשק משתמש ---
st.title("🏛️ קבינט המוחות של אפי")
st.write("הכירו את חברי הקבינט שנבחרו עבורכם:")

# הצגת חברי הקבינט
cols = st.columns(4)
for i, member in enumerate(st.session_state.cabinet):
    with cols[i % 4]:
        st.markdown(f"<div class='expert-box'><b>{member['name']}</b><br><small>{member['cat']}</small></div>", unsafe_allow_html=True)

if st.button("🔄 רענן חברי קבינט (החלפת 4 משתתפים)"):
    # החלפת אחד מכל קטגוריה
    new_cabinet = []
    for cat in ["פילוסופיה", "פסיכולוגיה", "תרבות", "הפתעה"]:
        new_cabinet.extend([{"name": n, "cat": cat} for n in random.sample(POOL[cat], 2)])
    st.session_state.cabinet = new_cabinet
    st.rerun()

st.write("---")
idea = st.text_area("🖋️ תאר את המחשבה, ההרגשה או האתגר שמעסיק אותך:", height=100)

if st.button("🔍 התחל בתהליך האבחון"):
    if idea:
        with st.spinner("חברי הקבינט מתבוננים פנימה..."):
            experts_str = ", ".join([m['name'] for m in st.session_state.cabinet])
            prompt = f"""
            הנושא: {idea}. 
            המומחים (לרקע בלבד): {experts_str}.
            המשימה: נסח 6 שאלות אבחון עמוקות בשפה אנושית, פשוטה ואמפתית. 
            אל תזכיר את שמות המומחים. השאלות צריכות לעזור לאדם להבין את רגשותיו, דפוסי החשיבה שלו ואיך הוא רואה את העולם.
            החזר אך ורק פורמט JSON:
            [ {{"q": "השאלה", "options": ["תשובה רגשית 1", "תשובה מחשבתית 2", "תשובה מעשית 3"]}} ]
            """
            try:
                model = genai.GenerativeModel(MODEL_NAME)
                res = model.generate_content(prompt)
                clean_json = re.search(r'\[.*\]', res.text.replace('```json', '').replace('```', ''), re.DOTALL)
                if clean_json:
                    st.session_state.questions = json.loads(clean_json.group())
                    st.session_state.pop('final_report