import streamlit as st
import requests
import pandas as pd
import json
import re
import random

# הגדרת דף
st.set_page_config(page_title="קבינט המוחות של אפי", layout="wide")

# --- CSS: גופנים, צבעים וריווחים למניעת דריסת אותיות ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Heebo:wght@400;700&family=Assistant:wght@400;700&display=swap');

    /* רקע דף תכלת-אפרפר בהיר */
    .stApp { background-color: #f0f4f8 !important; }

    html, body, [class*="st-"] {
        font-family: 'Heebo', 'Assistant', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
        color: #000000 !important;
        line-height: 2.2 !important; 
    }

    /* שדות כתיבה וטבלאות על רקע ירוק בהיר */
    textarea, input, [data-testid="stDataEditor"] {
        background-color: #e8f5e9 !important; 
        color: #000000 !important;
        border: 2px solid #2e7d32 !important;
        font-size: 1.3rem !important;
        border-radius: 10px;
    }

    /* כפתורים על רקע כחול בהיר עם כיתוב שחור */
    div.stButton > button {
        background-color: #bbdefb !important; 
        color: #000000 !important;
        border: 2px solid #1976d2 !important;
        height: 3.5em !important;
        width: 100% !important;
        font-size: 1.4rem !important;
        font-weight: bold !important;
        border-radius: 12px !important;
    }

    /* עיצוב שאלון (רדיו) על רקע כחול בהיר */
    div[data-baseweb="radio"] {
        background-color: #e3f2fd !important;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #90caf9;
        margin-bottom: 20px;
    }

    /* תיבת תוצאה סופית - לבן נקי */
    .result-box {
        border: 4px solid #1976d2;
        padding: 35px;
        background-color: #ffffff;
        margin-top: 30px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }

    h1 { color: #0d47a1 !important; font-weight: 800 !important; margin-bottom: 30px !important; }
    h3 { color: #1565c0 !important; border-bottom: 2px solid #1565c0; padding-bottom: 5px; margin-top: 30px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- מאגר דמויות ---
if 'pool_standard' not in st.session_state:
    st.session_state.pool_standard = [
        {"שם": "פיטר דרוקר", "תואר": "אבי הניהול", "התמחות": "אסטרטגיה וארגון"},
        {"שם": "חנה ארנדט", "תואר": "פילוסופית", "התמחות": "חברה ופוליטיקה"},
        {"שם": "זיגמונד פרויד", "תואר": "פסיכולוג", "התמחות": "תת מודע ודחפים"},
        {"שם": "לודוויג ויטגנשטיין", "תואר": "פילוסוף שפה", "התמחות": "לוגיקה ומשמעות"},
        {"שם": "ג'ק וולש", "תואר": "מנכ\"ל GE האגדי", "התמחות": "ניהול ביצועים"},
        {"שם": "דניאל כהנמן", "תואר": "כלכלן התנהגותי", "התמחות": "קבלת החלטות"},
        {"שם": "אברהם מאסלו", "תואר": "פסיכולוג", "התמחות": "מוטיבציה"},
        {"שם": "מילטון פרידמן", "תואר": "כלכלן", "התמחות": "שוק חופשי"}
    ]
    st.session_state.pool_surprise = [
        {"שם": "סון דזו", "תואר": "אסטרטג סיני", "התמחות": "אמנות המלחמה"},
        {"שם": "סטיב ג'ובס", "תואר": "יזם", "התמחות": "חדשנות וחוויית משתמש"},
        {"שם": "מרקוס אורליוס", "תואר": "קיסר רומי", "התמחות": "חוסן מנטלי"},
        {"שם": "לאונרדו דה וינצ'י", "תואר": "גאון רב-תחומי", "התמחות": "יצירתיות"},
        {"שם": "קוקו שאנל", "תואר": "יזמית אופנה", "התמחות": "מיתוג ושבירת מוסכמות"},
        {"שם": "ניקולה טסלה", "תואר": "ממציא", "התמחות": "חזון טכנולוגי"}
    ]

def refresh_cabinet():
    # בחירה אקראית: 3 רגילים ו-3 הפתעה
    std = random.sample(st.session_state.pool_standard, 3)
    surp = random.sample(st.session_state.pool_surprise, 3)
    st.session_state.current_cabinet = std + surp

if 'current_cabinet' not in st.session_state:
    refresh_cabinet()

# --- פונקציות API ---
def call_gemini(prompt):
    try: