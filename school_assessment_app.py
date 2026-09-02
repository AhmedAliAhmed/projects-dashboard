import streamlit as st

# قراءة ملف HTML
with open('index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# إعدادات صفحة Streamlit
st.set_page_config(
    page_title="منظومة تقييم وتدقيق المدارس",
    page_icon="🏫",
    layout="wide"
)

# عرض محتوى HTML
st.components.v1.html(html_content, height=1500, scrolling=True)