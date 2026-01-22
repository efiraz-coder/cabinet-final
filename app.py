import streamlit as st
import requests
import json
import re
import random

# הגדרת דף
st.set_page_config(page_title="קבינט המוחות של אפי", layout="wide")

# --- CSS: עיצוב יוקרתי ומניעת חפיפות ---
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

# --- ניהול דמויות ---
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
        url = f"