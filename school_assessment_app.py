# school_assessment_app.py
import streamlit as st
import base64

# قراءة ملف HTML
with open('index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

st.set_page_config(
    page_title="منظومة تقييم المدارس - TBC",
    page_icon="🏫",
    layout="wide"
)

# إضافة عنوان ووصف للتطبيق
st.markdown("""
    <div style="text-align: center; padding: 10px; background: linear-gradient(135deg, #1e293b, #0f172a); border-radius: 12px; margin-bottom: 20px;">
        <h1 style="color: #fbbf24; font-size: 24px;">🏫 منظومة تقييم وتدقيق المدارس</h1>
        <p style="color: #94a3b8; font-size: 14px;">برنامج التقييم الميداني وحساب المؤشرات الفنية للهياكل والأنظمة</p>
    </div>
""", unsafe_allow_html=True)

# عرض الـ HTML في Streamlit
st.components.v1.html(html_content, height=1400, scrolling=True)

# إضافة footer
st.markdown("""
    <div style="text-align: center; padding: 15px; margin-top: 20px; border-top: 1px solid #e2e8f0; color: #94a3b8; font-size: 12px;">
        نظام تقييم المدارس الميداني &copy; 2026 - شركة تطوير للمباني (TBC) & مركز العمران المتقدم
    </div>
""", unsafe_allow_html=True)