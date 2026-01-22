import streamlit as st
import requests
import json
import re
import random

# הגדרת דף
st.set_page_config(page_title="קבינט המוחות של אפי", layout="wide")

# פונקציה לקריאה ל-API בצורה בטוחה
def call_gemini(prompt):
    try:
        api_key = st.secrets["GEMINI_KEY"]
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=20)
        if res.status_code == 200:
            return res.json()['candidates'][0]['content']['parts'][0]['text']
        return None
    except:
        return None

st.title("🏛️ קבינט המוחות של אפי")

# אתחול קבינט אם לא קיים
if 'current_cabinet' not in st.session_state:
    st.session_state.current_cabinet = [
        {"שם": "פיטר דרוקר", "תואר": "אבי הניהול"},
        {"שם": "סטיב ג'ובס", "תואר": "יזם וחדשן"},
        {"שם": "סון דזו", "תואר": "אסטרטג סיני"},
        {"שם": "זיגמונד פרויד", "תואר": "פסיכולוג"},
        {"שם": "חנה ארנדט", "תואר": "פילוסופית"},
        {"שם": "לאונרדו דה וינצ'י", "תואר": "גאון רב-תחומי"}
    ]

# הצגת המומחים
cols = st.columns(3)
for i, m in enumerate(st.session_state.current_cabinet):
    with cols[i % 3]:
        st.info(f"👤 **{m['שם']}**\n\n{m['תואר']}")

idea = st.text_area("🖋️ מה הנושא לדיון?", height=100)

if st.button("🔍 בנה שאלון אבחון"):
    if idea:
        with st.spinner("הקבינט מנסח שאלות..."):
            prompt = f"נושא: {idea}. נסח 6 שאלות (אחת לכל מומחה) בפורמט JSON בלבד: [{{'expert': '...', 'q': '...', 'options': ['א','ב','ג']}}]"
            raw = call_gemini(prompt)
            if raw:
                # ניקוי וחילוף ה-JSON
                match = re.search(r'\[.*\]', raw.replace('```json', '').replace('```', ''), re.DOTALL)
                if match:
                    st.session_state.qs = json.loads(match.group())
                    st.session_state.pop('res', None) # איפוס תוצאות קודמות
                else:
                    st.warning("הקבינט עמוס, נסה ללחוץ שוב.") # פותר את image_21039b
            else:
                st.error("לא ניתן לתקשר עם הקבינט. בדוק את המפתח.")

# התיקון הקריטי ל-Traceback (פותר את image_210814)
if 'qs' in st.session_state and st.session_state.qs:
    st.markdown("### 📝 שאלון אבחון")
    ans_data = []
    for i, item in enumerate(st.session_state.qs):
        st.write(f"**💬 {item.get('expert')} שואל/ת:**")
        choice = st.radio(item['q'], item['options'], key=f"q_{i}")
        ans_data.append(f"מומחה: {item.get('expert')} | תשובה: {choice}")

    if st.button("🚀 הפק תובנות סופיות"):
        with st.spinner("מנתח..."):
            p_final = f"נושא: {idea}. תשובות: {ans_data}. כתוב 5 תובנות וטבלה מסכמת."
            st.session_state.res = call_gemini(p_final)

if 'res' in st.session_state:
    st.success("📊 המלצות הקבינט:")
    st.write(st.session_state.res)