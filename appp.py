import streamlit as st
import streamlit.components.v1 as components

# ضبط إعدادات الصفحة
st.set_page_config(
    page_title="منظومة تقييم وتدقيق المدارس",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# إخفاء الهيدر والفوتر الافتراضي لـ Streamlit
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {padding: 0rem !important;}
    </style>
""", unsafe_allow_html=True)

# قراءة وعرض ملف الـ HTML
with open("index.html", "r", encoding="utf-8") as f:
    html_content = f.read()

components.html(html_content, height=950, scrolling=True)