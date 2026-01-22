import streamlit as st
import requests
import json
import re
import random

# הגדרת דף
st.set_page_config(page_title="קבינט המוחות של אפי", layout="wide")

# --- CSS: עיצוב נקי למניעת חפיפות ---
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
    textarea {
        background-color: #e8f5e9 !important; 
        border: 2px solid #2e7d32 !important;
        border-radius: 12px !important;
        padding: 15px !important;
    }
    div.stButton > button {
        background-color: #bbdefb !important; 
        color: #000000 !important;
        border: 2px solid #1976d2 !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        height: 3.5em !important;
        width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ניהול הדמויות ---
if 'current_cabinet' not in st.session_state:
    pool_std = [
        {"שם": "פיטר דרוקר", "תואר": "אבי הניהול", "התמחות": "אסטרטגיה וארגון"},
        {"שם": "זיגמונד פרויד", "תואר": "פסיכולוג", "התמחות": "תת מודע"},
        {"שם": "חנה ארנדט", "תואר": "פילוסופית", "התמחות": "חברה ופוליטיקה"},
        {"שם": "דניאל כהנמן", "תואר": "כלכלן", "התמחות": "קבלת החלטות"},
        {"שם": "אברהם מאסלו", "תואר": "פסיכולוג", "התמחות": "מוטיבציה"}
    ]
    pool_surp = [
        {"שם": "סון דזו", "תואר": "אסטרטג סיני", "התמחות": "אמנות המלחמה"},
        {"שם": "סטיב ג'ובס", "תואר": "יזם", "התמחות": "חדשנות ועיצוב"},
        {"שם": "מרקוס אורליוס", "תואר": "קיסר רומי", "התמחות": "חוסן מנטלי"},
        {"שם": "לאונרדו דה וינצ'י", "תואר": "גאון", "התמחות": "פתרון בעיות"}
    ]
    st.session_state.current_cabinet = random.sample(pool_std, 3) + random.sample(pool_surp, 3)

def call_api(prompt):
    try:
        api_key = st.secrets["GEMINI_KEY"]
        base_url = "https://generativelanguage.googleapis.com/v1beta/models/"
        model_url = "gemini-flash-latest:generateContent?key="
        full_url = f"{base_url}{model_url}{api_key}"
        
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        res = requests.post(full_url, json=payload, timeout=15)
        
        if res.status_code == 200:
            return res.json()['candidates'][0]['content']['parts'][0]['text']
        return None
    except Exception as e:
        return None

# --- ממשק ---
st.title("🏛️ קבינט המוחות של אפי")

st.subheader("👥 המומחים שמתכנסים עבורך:")
cols = st.columns(3)
for i, m in enumerate(st.session_state.current_cabinet):
    with cols[i % 3]:
        st.info(f"👤 **{m['שם']}**\n\n{m['תואר']}")

st.markdown("---")
idea = st.text_area("🖋️ תאר את האתגר שלך:", height=100, placeholder="למשל: איך להגדיל את המכירות בעסק שלי?")

if st.button("🔍 התחל סבב שאלות אישיות"):
    if idea:
        with st.spinner("חברי הקבינט מנתחים ומנסחים שאלות..."):
            experts_desc = ", ".join([f"{m['שם']} ({m['התמחות']})" for m in st.session_state.current_cabinet])
            
            # פרומפט הרבה יותר נוקשה למניעת שגיאות JSON
            prompt = f"""
            Task: Create a 6-question diagnostic survey for this problem: "{idea}".
            Experts: {experts_desc}.
            Instructions: Each expert asks ONE question from their perspective.
            Format: Output ONLY a valid JSON list of objects. No markdown, no comments.
            Structure: [{{"expert": "Name", "q": "Question", "options": ["Option A", "Option B", "Option C"]}}]
            """
            
            raw = call_api(prompt)
            # ניקוי שאריות טקסט שה-AI לפעמים מוסיף
            if raw:
                raw_clean = raw.replace('```json', '').replace('```', '').strip()
                match = re.search(r'\[.*\]', raw_clean, re.DOTALL)
                if match:
                    try:
                        st.session_state.qs = json.loads(match.group())
                        if 'res' in st.session_state: del st.session_state['res']
                        st.rerun()
                    except:
                        st.error("הקבינט שלח תשובה לא קריאה. נסה שוב.")
                else:
                    st.error("הקבינט זקוק לניסוח מחדש. אנא נסה שוב.")

if 'qs' in st.session_state and st.session_state.qs:
    st.subheader("📝 סבב שאלות האבחון")
    ans_data = []
    
    # הצגת השאלות בתוך תיבות מעוצבות
    for i, item in enumerate(st.session_state.qs):
        with st.container():
            st.markdown(f"**💬 {item.get('expert', 'מומחה')} שואל/ת:**")
            choice = st.radio(item['q'], item['options'], key=f"q_{i}")
            ans_data.append(f"מומחה: {item.get('expert')} | שאלה: {item['q']} | תשובה: {choice}")
            st.markdown("---")

    if st.button("🚀 הפק תובנות אסטרטגיות"):
        with st.spinner("מגבש המלצות סופיות..."):
            p_final = f"נושא: {idea}. תשובות לשאלון האבחון: {ans_data}. כתוב 5 תובנות אסטרטגיות עמוקות וטבלה מסכמת הכוללת: בעיה, פתרון, דרך ביצוע, ותפוקות."
            st.session_state.res = call_api(p_final)

if 'res' in st.session_state:
    st.markdown("### 📊 מסקנות הקבינט של אפי")
    st.info(st.session_state.res)