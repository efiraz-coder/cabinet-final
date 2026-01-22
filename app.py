import streamlit as st
import requests
import json
import re
import random

# הגדרת דף - layout רחב למניעת צפיפות
st.set_page_config(page_title="קבינט המוחות של אפי", layout="wide")

# --- CSS: עיצוב נקי, מרווח ומונע חפיפות ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@400;700&display=swap');

    .stApp { background-color: #f0f4f8 !important; }

    html, body, [class*="st-"] {
        font-family: 'Assistant', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
        color: #000000 !important;
        line-height: 2.2 !important; 
    }

    /* עיצוב תיבות הטקסט */
    textarea {
        background-color: #e8f5e9 !important; 
        border: 2px solid #2e7d32 !important;
        border-radius: 12px !important;
        padding: 15px !important;
    }

    /* עיצוב הכפתורים */
    div.stButton > button {
        background-color: #bbdefb !important; 
        color: #000000 !important;
        border: 2px solid #1976d2 !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        height: 3.5em !important;
        width: 100% !important;
    }

    /* עיצוב כרטיסיית שאלה של מומחה */
    .expert-box {
        background-color: #ffffff;
        padding: 20px;
        border-right: 6px solid #1976d2;
        border-radius: 10px;
        margin-bottom: 25px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ניהול הזיכרון והדמויות ---
if 'current_cabinet' not in st.session_state:
    pool_std = [
        {"שם": "פיטר דרוקר", "תואר": "אבי הניהול", "התמחות": "אסטרטגיה וארגון"},
        {"שם": "זיגמונד פרויד", "תואר": "פסיכולוג", "התמחות": "תת מודע ודחפים"},
        {"שם": "חנה ארנדט", "תואר": "פילוסופית", "התמחות": "חברה ופוליטיקה"},
        {"שם": "דניאל כהנמן", "תואר": "כלכלן", "התמחות": "קבלת החלטות"},
        {"שם": "אברהם מאסלו", "תואר": "פסיכולוג", "התמחות": "צרכים ומוטיבציה"}
    ]
    pool_surp = [
        {"שם": "סון דזו", "תואר": "אסטרטג סיני", "התמחות": "אמנות המלחמה"},
        {"שם": "סטיב ג'ובס", "תואר": "יזם", "התמחות": "חדשנות ועיצוב"},
        {"שם": "מרקוס אורליוס", "תואר": "קיסר רומי", "התמחות": "חוסן וסטואיציזם"},
        {"שם": "לאונרדו דה וינצ'י", "תואר": "גאון", "התמחות": "יצירתיות רב-תחומית"}
    ]
    # הגרלה ראשונית: 3 מהקבועים ו-3 מההפתעה
    st.session_state.current_cabinet = random.sample(pool_std, 3) + random.sample(pool_surp, 3)

def call_api(prompt):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={st.secrets['GEMINI_KEY']}"
        res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
        if res.status_code == 200:
            return res.json()['candidates'][0]['content']['parts'][0]['text']
        return None
    except:
        return None

# --- ממשק המשתמש ---
st.title("🏛️ קבינט המוחות של אפי")

st.subheader("👥 חברי הקבינט שמתכנסים עבורך:")
# הצגת המומחים בצורה אופקית ונקייה
cols = st.columns(3)
for i, m in enumerate(st.session_state.current_cabinet):
    with cols[i % 3]:
        st.info(f"👤 **{m['שם']}**\n\n{m['תואר']}")

st.markdown("---")
idea = st.text_area("🖋️ תאר את האתגר או הבעיה שלך:", height=100)

if st.button("🔍 התחל סבב שאלות אישיות"):
    if idea:
        with st.spinner("חברי הקבינט מנתחים את דבריך ומנסחים שאלות..."):
            experts_list = [f"{m['שם']} ({m['התמחות']})" for m in st.session_state.current_cabinet]
            prompt = f"""נושא: {idea}. מומחים: {experts_list}.
            נסח 6 שאלות (אחת לכל מומחה). כל שאלה חייבת לשקף את הזווית הייחודית של המומחה.
            החזר JSON בלבד: [{{'expert': 'שם המומחה', 'q': 'שאלה', 'options': ['א','ב','ג']}}, ...]"""
            
            raw = call_api(prompt)
            match = re.search(r'\[.*\]', raw, re.DOTALL) if raw else None
            if match:
                st.session_state.qs = json.loads(match.group())
                st.session_state.pop('res', None) # איפוס תוצאות קודמות
            else:
                st.error("הקבינט זקוק לניסוח מ