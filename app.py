import streamlit as st
import requests
import pandas as pd
import json
import re
import random

# הגדרת דף
st.set_page_config(page_title="קבינט המוחות של אפי", layout="wide")

# --- CSS מעודכן: שינוי רקע דף וצבעוניות מוגדרת ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Heebo:wght@400;700&family=Assistant:wght@400;700&display=swap');

    /* שינוי רקע הדף כולו לתכלת-אפרפר בהיר ויוקרתי */
    .stApp {
        background-color: #f0f4f8 !important;
    }

    html, body, [class*="st-"] {
        font-family: 'Heebo', 'Assistant', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
        color: #000000 !important;
        line-height: 2.0 !important;
    }

    /* שדות כתיבה וטבלאות על רקע ירוק בהיר */
    textarea, input, [data-testid="stDataEditor"], [data-testid="stTable"] {
        background-color: #e8f5e9 !important; 
        color: #000000 !important;
        border: 2px solid #2e7d32 !important;
        font-size: 1.3rem !important;
        border-radius: 8px;
    }

    /* כפתורים על רקע כחול בהיר עם כיתוב שחור */
    div.stButton > button {
        background-color: #bbdefb !important; /* כחול בהיר מודגש מעט יותר */
        color: #000000 !important;
        border: 2px solid #1976d2 !important;
        height: 3.5em !important;
        width: 100% !important;
        font-size: 1.4rem !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }

    /* עיצוב שאלון (רדיו) על רקע כחול בהיר */
    div[data-baseweb="radio"] {
        background-color: #e3f2fd !important;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #90caf9;
    }

    /* תיבת תוצאה סופית - רקע לבן נקי כדי שהטקסט יקפוץ */
    .result-box {
        border: 4px solid #1976d2;
        padding: 35px;
        background-color: #ffffff;
        margin-top: 30px;
        border-radius: 15px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }

    /* הגדלת כותרות */
    h1 { color: #0d47a1 !important; font-weight: 800 !important; }
    h3 { color: #1565c0 !important; border-bottom: 2px solid #1565c0; padding-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- ניהול דמויות (כפי שביקשת) ---
if 'pool_standard' not in st.session_state:
    st.session_state.pool_standard = [
        {"שם": "פיטר דרוקר", "תואר": "אבי הניהול", "התמחות": "אסטרטגיה וארגון"},
        {"שם": "חנה ארנדט", "תואר": "פילוסופית", "התמחות": "חברה ופוליטיקה"},
        {"שם": "זיגמונד פרויד", "תואר": "פסיכולוג", "התמחות": "תת מודע ודחפים"},
        {"שם": "לודוויג ויטגנשטיין", "תואר": "פילוסוף שפה", "התמחות": "לוגיקה ומשמעות"},
        {"שם": "ג'ק וולש", "תואר": "מנכ\"ל אגדי", "התמחות": "ניהול ביצועים"},
        {"שם": "דניאל כהנמן", "תואר": "כלכלן התנהגותי", "התמחות": "קבלת החלטות"},
        {"שם": "אברהם מאסלו", "תואר": "פסיכולוג", "התמחות": "מדרג הצרכים ומוטיבציה"},
        {"שם": "מילטון פרידמן", "תואר": "כלכלן", "התמחות": "שוק חופשי ואסטרטגיה"}
    ]
    st.session_state.pool_surprise = [
        {"שם": "סון דזו", "תואר": "אסטרטג סיני", "התמחות": "אמנות המלחמה"},
        {"שם": "סטיב ג'ובס", "תואר": "יזם", "התמחות": "חוויית משתמש וחדשנות"},
        {"שם": "מרקוס אורליוס", "תואר": "קיסר ופילוסוף", "התמחות": "חוסן נפשי (סטואיציזם)"},
        {"שם": "לאונרדו דה וינצ'י", "תואר": "גאון רב-תחומי", "התמחות": "פתרון בעיות יצירתי"},
        {"שם": "אלכסנדר הגדול", "תואר": "מצביא", "התמחות": "כיבוש יעדים והתרחבות"},
        {"שם": "מרי קירי", "תואר": "מדענית", "התמחות": "חקר הלא נודע"}
    ]

def refresh_cabinet():
    # הגרלת 3 מהרגיל ו-3 מההפתעה
    std = random.sample(st.session_state.pool_standard, 3)
    surp = random.sample(st.session_state.pool_surprise, 3)
    st.session_state.current_cabinet = std + surp

if 'current_cabinet' not in st.session_state:
    refresh_cabinet()

# --- ממשק משתמש ---
st.title("🏛️ קבינט המוחות של אפי")

st.subheader("👥 הרכב הקבינט הנוכחי")
if st.button("🔄 רענן הרכב (החלף 4 מתוך 6)"):
    # פונקציית רענן ששומרת 2 ומחליפה 4 (באקראי)
    refresh_cabinet()

# תצוגת המשתתפים שורה אחר שורה
for m in st.session_state.current_cabinet:
    st.markdown(f"👤 **{m['שם']}** | {m['תואר']} | התמחות: {m['התמחות']}")

st.markdown("---")

# שלב 1: הזנת נושא
st.subheader("🖋️ מה הנושא שעל הפרק?")
idea = st.text_area("פרט את האתגר שלך:", height=100, placeholder="כתוב כאן...")

def call_gemini(prompt):
    try:
        API_KEY = st.secrets["GEMINI_KEY"]
        url = f"https://generativ