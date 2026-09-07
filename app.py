import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import hashlib
from datetime import datetime
import streamlit.components.v1 as components
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, AdaBoostRegressor, BaggingRegressor, ExtraTreesRegressor
from sklearn.tree import DecisionTreeRegressor
import warnings
warnings.filterwarnings('ignore')

# -----------------------------
# 0. إعدادات الصفحة والتنسيق
# -----------------------------
st.set_page_config(
    page_title="شركة العمران المتقدم | الموقف المالي لمستخلصات المشاريع 2026م",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# تنسيق الجمالية العربية للهوية
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl;
        text-align: right;
    }
    .stApp {
        background-color: #f8fafc;
        color: #1e293b;
    }
    
    .brand-title {
        font-size: 26px;
        font-weight: 900;
        color: #00a859;
        margin: 0;
        line-height: 1.2;
    }
    .brand-subtitle {
        font-size: 13px;
        color: #64748b;
        font-weight: 700;
    }
    .report-main-title {
        font-size: 24px;
        font-weight: 800;
        color: #0f172a;
        margin: 0;
    }
    .report-date {
        font-size: 13px;
        color: #64748b;
        font-weight: 600;
    }
    .green-divider {
        height: 4px;
        background: linear-gradient(90deg, #00a859 0%, #10b981 100%);
        border-radius: 2px;
        margin: 15px 0 25px 0;
    }

    .kpi-card {
        background: #ffffff;
        border-radius: 14px;
        padding: 16px 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }
    .kpi-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    .kpi-title {
        font-size: 14px;
        font-weight: 700;
        color: #475569;
    }
    .kpi-value {
        font-size: 22px;
        font-weight: 900;
        line-height: 1.2;
    }
    .kpi-sub {
        font-size: 13px;
        font-weight: 700;
        margin-top: 6px;
    }

    .summary-box {
        background: #ffffff;
        border-radius: 14px;
        padding: 20px;
        border: 1px solid #e2e8f0;
        margin-bottom: 25px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }
    .section-title {
        font-size: 17px;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 1. نظام الحماية بكلمة مرور (12345)
# -----------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

PASSWORD_HASH = hashlib.sha256("12345".encode()).hexdigest()

def check_password(password):
    return hashlib.sha256(password.encode()).hexdigest() == PASSWORD_HASH

if not st.session_state.authenticated:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="background: #ffffff; padding: 40px; border-radius: 20px; border: 1px solid #e2e8f0; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.05);">
            <h2 style="color: #00a859; font-weight: 900; margin-bottom: 5px;">شركة العمران المتقدم</h2>
            <p style="color: #64748b; font-size: 13px; font-weight: 700; margin-bottom: 25px;">OMRAN ADVANCED COMPANY</p>
            <h4 style="color: #0f172a; font-weight: 800;">🔐 تسجيل الدخول لتقرير المستخلصات 2026م</h4>
        </div>
        """, unsafe_allow_html=True)
        
        password_input = st.text_input("كلمة المرور", type="password", key="pass_field")
        if st.button("تسجيل الدخول", use_container_width=True, type="primary"):
            if check_password(password_input):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ كلمة المرور غير صحيحة")
        st.caption("🔑 كلمة المرور الافتراضية: 12345")
    st.stop()

# -----------------------------
# 2. البيانات الأولية طِبقاً للصورة
# -----------------------------
initial_data = [
    ["1", "تقديم الخدمات الاستشارية لدراسة تطوير خطط تشغيل و صيانة المرافق الهامة", "وزارة البيئة و المياه و الزراعة", "قيد التنفيذ", 628950.00, 0.00, 0.00, 628950.00],
    ["2", "الاشراف علي تصميم و انشاء المختبر البيطري المركزي", "وزارة البيئة و المياه و الزراعة", "قيد التنفيذ", 832900.15, 0.00, 394531.65, 394531.65],
    ["3", "تقديم الخدمات الاستشارية للاشراف علي المشاريع الهندسية ببنك التنمية", "بنك التنمية", "مكتمل", 241500.00, 241500.00, 0.00, 0.00],
    ["4", "الاتفاقية الاطارية لخدمات الاشراف علي مشاريع إدارة المرافق بالمنطقة الوسطي", "شركة تطوير المباني (TBC)", "قيد التنفيذ", 19666576.68, 0.00, 5857186.10, 13809390.58],
    ["5", "الاشراف علي إدارة المرافق بالمنطقة الجنوبية", "شركة تطوير المباني (TBC)", "قيد التنفيذ", 4222488.43, 0.00, 3222488.43, 1000000.00],
    ["6", "الخدمات الاستشارية للاستفادة من المياه الجوفية و السطحية و مشاريع درء اخطار السيول", "وزارة البيئة و المياه و الزراعة", "قيد التنفيذ", 3261425.00, 1187950.00, 1040750.00, 1032725.00],
    ["7", "الاتفاقية الاطارية لتصميم مشاريع المؤسسة العامة للري امر عمل (02)", "المؤسسة العامة للري", "قيد التنفيذ", 5398330.00, 4508000.00, 0.00, 890330.00],
    ["8", "ترميز مباني التراث المعماري وسط الرياض", "وزارة الثقافة", "قيد التنفيذ", 3910460.00, 0.00, 0.00, 3910460.00],
    ["9", "دراسة و تصميم مشروع انشاء قاعة الطعام بالمقر الرئيسي", "المؤسسة العامة للري", "مكتمل", 439875.00, 439875.00, 0.00, 0.00],
    ["10", "مبالغ تم دفعها للهندسية ولم يتم تحصيلها", "القطاع الهندسي والمالي", "معلق", 2864500.00, 0.00, 0.00, 2864500.00],
    ["11", "الاشراف علي المشاريع الصغيرة بجميع مناطق المملكة (المرحلة الثانية)", "وزارة البيئة و المياه و الزراعة", "قيد التنفيذ", 2996034.00, 0.00, 0.00, 2996034.00],
    ["12", "الاتفاقية الاطارية لخدمات الاشراف علي مشاريع إدارة المرافق بالمنطقة الوسطي", "شركة تطوير المباني (TBC)", "قيد التنفيذ", 3800000.00, 0.00, 0.00, 3800000.00],
]

cols = [
    "م", "اسم المشروع", "القطاع / العميل", "الحالة",
    "Total Due Amount", "Submitted Claims", "Payment Orders Issued", "Targeted Claims"
]

if "df_projects" not in st.session_state:
    st.session_state.df_projects = pd.DataFrame(initial_data, columns=cols)

# -----------------------------
# 3. الهيدر الرسمي للهوية
# -----------------------------
h_col1, h_col2 = st.columns([2, 1])

with h_col1:
    st.markdown('<div class="report-main-title">الموقف المالي لمستخلصات المشاريع 2026م ( شركة العمران المتقدم )</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="report-date">تاريخ الإصدار حتى نهاية شهر أغسطس: {datetime.now().strftime("%Y-%m-%d")}</div>', unsafe_allow_html=True)

with h_col2:
    st.markdown("""
    <div style="text-align: left;">
        <div class="brand-title">شركة العمران المتقدم</div>
        <div class="brand-subtitle">OMRAN ADVANCED COMPANY</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="green-divider"></div>', unsafe_allow_html=True)

# -----------------------------
# 4. التبويبات الرئيسيّة
# -----------------------------
tab1, tab2 = st.tabs(["📊 الموقف المالي والتقرير", "🤖 تحليل النماذج (ML)"])

with tab1:
    # -----------------------------
    # 1. الجدول التفاعلي (يأتي أولاً لتنعكس أي تعديلات فورياً)
    # -----------------------------
    st.markdown('<div class="section-title">✏️ جدول تعديل المستخلصات (أي تعديل ينعكس فورياً على البطاقات والرسوم البيانية)</div>', unsafe_allow_html=True)
    
    edited_df = st.data_editor(
        st.session_state.df_projects,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "م": st.column_config.TextColumn("م", disabled=True),
            "اسم المشروع": st.column_config.TextColumn("اسم المشروع"),
            "Total Due Amount": st.column_config.NumberColumn("المستحقة حتى النهاية", format="%.2f ر.س"),
            "Submitted Claims": st.column_config.NumberColumn("المستخلصات المرفوعة", format="%.2f ر.س"),
            "Payment Orders Issued": st.column_config.NumberColumn("صدر لها أمر دفع", format="%.2f ر.س"),
            "Targeted Claims": st.column_config.NumberColumn("مستهدف رفعها", format="%.2f ر.س"),
        },
        key="projects_editor"
    )

    # حفظ حالة التعديل تلقائياً
    st.session_state.df_projects = edited_df

    # -----------------------------
    # 2. حساب الإجماليات والنسب فورياً من الجدول المعدّل
    # -----------------------------
    total_due = edited_df["Total Due Amount"].sum()
    total_orders = edited_df["Payment Orders Issued"].sum()
    total_submitted = edited_df["Submitted Claims"].sum()
    total_targeted = edited_df["Targeted Claims"].sum()

    pct_orders = (total_orders / total_due * 100) if total_due else 0
    pct_submitted = (total_submitted / total_due * 100) if total_due else 0
    pct_targeted = (total_targeted / total_due * 100) if total_due else 0

    st.markdown("<br>", unsafe_allow_html=True)

    # -----------------------------
    # 3. بطاقات KPI الأربع (تتحديث فورياً)
    # -----------------------------
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown(f"""
        <div class="kpi-card" style="border-top: 4px solid #475569;">
            <div class="kpi-header"><span class="kpi-title">💰 إجمالي المستحق</span><span>📦</span></div>
            <div class="kpi-value" style="color: #0f172a;">{total_due:,.2f} <span style="font-size:14px;">ريال</span></div>
            <div class="kpi-sub" style="color: #64748b;">{len(edited_df)} مشروعاً</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown(f"""
        <div class="kpi-card" style="border-top: 4px solid #10b981;">
            <div class="kpi-header"><span class="kpi-title">💳 صدر له أمر دفع</span><span>🟢</span></div>
            <div class="kpi-value" style="color: #10b981;">{total_orders:,.2f} <span style="font-size:14px;">ريال</span></div>
            <div class="kpi-sub" style="color: #059669;">{pct_orders:.1f}% من المستحق</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="kpi-card" style="border-top: 4px solid #3b82f6;">
            <div class="kpi-header"><span class="kpi-title">🏦 مستخلصات مرفوعة</span><span>🔵</span></div>
            <div class="kpi-value" style="color: #3b82f6;">{total_submitted:,.2f} <span style="font-size:14px;">ريال</span></div>
            <div class="kpi-sub" style="color: #2563eb;">{pct_submitted:.1f}% من المستحق</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="kpi-card" style="border-top: 4px solid #f59e0b;">
            <div class="kpi-header"><span class="kpi-title">🎯 مستهدف رفعها</span><span>🟡</span></div>
            <div class="kpi-value" style="color: #f59e0b;">{total_targeted:,.2f} <span style="font-size:14px;">ريال</span></div>
            <div class="kpi-sub" style="color: #d97706;">{pct_targeted:.1f}% من المستحق</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # -----------------------------
    # 4. النسبة الإجمالية لحالة المبالغ المالية (تتحدث فورياً)
    # -----------------------------
    st.markdown("""
    <div class="summary-box">
        <div class="section-title">🎯 النسبة الإجمالية لحالة المبالغ المالية (محدث فورياً)</div>
    """, unsafe_allow_html=True)

    s_col1, s_col2, s_col3 = st.columns(3)
    s_col1.markdown(f"🟢 **صدر له أمر دفع:** <span style='color:#10b981; font-weight:800;'>{total_orders:,.2f} ريال</span> ({pct_orders:.1f}%)", unsafe_allow_html=True)
    s_col2.markdown(f"🔵 **مرفوع حالياً:** <span style='color:#3b82f6; font-weight:800;'>{total_submitted:,.2f} ريال</span> ({pct_submitted:.1f}%)", unsafe_allow_html=True)
    s_col3.markdown(f"🟡 **مستهدف رفعه:** <span style='color:#f59e0b; font-weight:800;'>{total_targeted:,.2f} ريال</span> ({pct_targeted:.1f}%)", unsafe_allow_html=True)

    fig_summary_bar = go.Figure()
    fig_summary_bar.add_trace(go.Bar(y=['المحفظة'], x=[total_orders], name='صدر أمر دفع', orientation='h', marker=dict(color='#10b981')))
    fig_summary_bar.add_trace(go.Bar(y=['المحفظة'], x=[total_submitted], name='مرفوع', orientation='h', marker=dict(color='#3b82f6')))
    fig_summary_bar.add_trace(go.Bar(y=['المحفظة'], x=[total_targeted], name='مستهدف رفعه', orientation='h', marker=dict(color='#f59e0b')))
    
    fig_summary_bar.update_layout(
        barmode='stack', height=50, margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(showticklabels=False, showgrid=False),
        yaxis=dict(showticklabels=False, showgrid=False),
        showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_summary_bar, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # -----------------------------
    # 5. توزيع نسب المستخلصات لكل مشروع (يتحدث فورياً)
    # -----------------------------
    st.markdown('<div class="section-title">📊 توزيع نسب المستخلصات لكل مشروع (محدث فورياً)</div>', unsafe_allow_html=True)

    edited_df['chart_label'] = edited_df.apply(lambda r: f"{r['م']}. {r['اسم المشروع']} ({r['Total Due Amount']:,.0f} ريال)", axis=1)

    fig_project_bars = go.Figure()
    fig_project_bars.add_trace(go.Bar(y=edited_df['chart_label'], x=edited_df['Payment Orders Issued'], name='صدر أمر دفع', orientation='h', marker=dict(color='#10b981')))
    fig_project_bars.add_trace(go.Bar(y=edited_df['chart_label'], x=edited_df['Submitted Claims'], name='مرفوع حالياً', orientation='h', marker=dict(color='#3b82f6')))
    fig_project_bars.add_trace(go.Bar(y=edited_df['chart_label'], x=edited_df['Targeted Claims'], name='مستهدف رفعه', orientation='h', marker=dict(color='#f59e0b')))

    fig_project_bars.update_layout(
        barmode='stack',
        height=550,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor='#ffffff',
        plot_bgcolor='#ffffff',
        font=dict(family="Cairo", size=12, color="#0f172a"),
        xaxis=dict(showgrid=True, gridcolor="#f1f5f9", tickformat=",.0f"),
        yaxis=dict(autorange="reversed"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_project_bars, use_container_width=True)

    # -----------------------------
    # 6. تصدير البيانات والتقرير الرسمية
    # -----------------------------
    st.markdown("---")
    st.markdown("### 📑 تصدير البيانات والتقرير الرسمي (تحديث فوراً مع الأرقام الجديدة)")

    def generate_html_report(dataframe):
        tot_due = dataframe["Total Due Amount"].sum()
        tot_orders = dataframe["Payment Orders Issued"].sum()
        tot_sub = dataframe["Submitted Claims"].sum()
        tot_targ = dataframe["Targeted Claims"].sum()
        
        rows_html = ""
        for idx, row in dataframe.iterrows():
            rows_html += f"""
            <tr>
                <td>{row['م']}</td>
                <td style="text-align: right; font-weight: bold;">{row['اسم المشروع']}</td>
                <td>{row['Total Due Amount']:,.2f}</td>
                <td>{row['Submitted Claims']:,.2f}</td>
                <td>{row['Payment Orders Issued']:,.2f}</td>
                <td>{row['Targeted Claims']:,.2f}</td>
            </tr>
            """
            
        html_content = f"""
        <!DOCTYPE html>
        <html dir="rtl">
        <head>
            <meta charset="utf-8">
            <title>الموقف المالي لمستخلصات المشاريع 2026م ( شركة العمران المتقدم )</title>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;800;900&display=swap');
                body {{ font-family: 'Cairo', sans-serif; padding: 25px; background: #fff; color: #1e293b; }}
                .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #00a859; padding-bottom: 15px; margin-bottom: 20px; }}
                .brand-name {{ font-size: 24px; font-weight: 900; color: #00a859; }}
                .kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 25px; }}
                .kpi {{ border: 1px solid #cbd5e1; padding: 15px; border-radius: 10px; text-align: center; }}
                .kpi-val {{ font-size: 18px; font-weight: 800; margin-top: 5px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ border: 1px solid #cbd5e1; padding: 10px; text-align: center; font-size: 12px; }}
                th {{ background-color: #00a859; color: white; font-size: 13px; }}
                tr:nth-child(even) {{ background-color: #f8fafc; }}
                .footer-total {{ background-color: #e2e8f0; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div>
                    <h2 style="margin:0; font-weight:900;">الموقف المالي لمستخلصات المشاريع 2026م ( شركة العمران المتقدم )</h2>
                    <p style="margin:5px 0 0 0; color:#64748b; font-size:12px;">تاريخ الإصدار حتى نهاية شهر أغسطس: {datetime.now().strftime('%Y-%m-%d')}</p>
                </div>
                <div style="text-align: left;">
                    <div class="brand-name">شركة العمران المتقدم</div>
                    <div style="font-size:11px; color:#64748b; font-weight:700;">OMRAN ADVANCED COMPANY</div>
                </div>
            </div>

            <div class="kpi-grid">
                <div class="kpi"><div>إجمالي المستحق</div><div class="kpi-val">{tot_due:,.2f} ريال</div></div>
                <div class="kpi" style="border-color:#10b981;"><div style="color:#10b981;">صدر له أمر دفع</div><div class="kpi-val" style="color:#10b981;">{tot_orders:,.2f} ريال</div></div>
                <div class="kpi" style="border-color:#3b82f6;"><div style="color:#3b82f6;">مستخلصات مرفوعة</div><div class="kpi-val" style="color:#3b82f6;">{tot_sub:,.2f} ريال</div></div>
                <div class="kpi" style="border-color:#f59e0b;"><div style="color:#f59e0b;">مستهدف رفعها</div><div class="kpi-val" style="color:#f59e0b;">{tot_targ:,.2f} ريال</div></div>
            </div>

            <table>
                <thead>
                    <tr>
                        <th>م</th>
                        <th>اسم المشروع</th>
                        <th>المستحقة حتى النهاية</th>
                        <th>المستخلصات المرفوعة</th>
                        <th>صدر له أمر دفع</th>
                        <th>مستهدف رفعها</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                    <tr class="footer-total">
                        <td colspan="2">الإجمالي العام (ريال سعودي)</td>
                        <td>{tot_due:,.2f}</td>
                        <td>{tot_sub:,.2f}</td>
                        <td>{tot_orders:,.2f}</td>
                        <td>{tot_targ:,.2f}</td>
                    </tr>
                </tbody>
            </table>
        </body>
        </html>
        """
        return html_content

    html_report_data = generate_html_report(edited_df)
    csv_data = edited_df.to_csv(index=False).encode('utf-8-sig')

    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        st.download_button(
            label="📑 تنزيل التقرير الرسمي PDF / HTML",
            data=html_report_data,
            file_name="Omran_Financial_Report_2026.html",
            mime="text/html",
            type="primary",
            use_container_width=True
        )

    with btn_col2:
        st.download_button(
            label="📥 تصدير ملف Excel/CSV",
            data=csv_data,
            file_name="Omran_Projects_2026.csv",
            mime="text/csv",
            use_container_width=True
        )

with tab2:
    st.subheader("🤖 تحليل وتقييم أداء نماذج التعلم الآلي (ML)")
    
    @st.cache_data
    def get_ml_results():
        np.random.seed(42)
        n = 200
        df_ml = pd.DataFrame({
            'size': np.random.uniform(500, 5000, n),
            'rooms': np.random.randint(1, 10, n),
            'age': np.random.randint(0, 50, n),
            'location_score': np.random.uniform(1, 10, n),
            'price': np.random.uniform(100000, 1000000, n)
        })
        df_ml['price'] = (100000 + df_ml['size']*150 + df_ml['rooms']*20000 - df_ml['age']*5000 + df_ml['location_score']*30000 + np.random.normal(0, 50000, n))
        
        X = df_ml[['size', 'rooms', 'age', 'location_score']]
        y = df_ml['price']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        scaler = MinMaxScaler()
        X_train_s = scaler.fit_transform(X_train)
        X_test_s = scaler.transform(X_test)
        
        models = {
            'الانحدار الخطي': LinearRegression(),
            'شجرة القرار': DecisionTreeRegressor(random_state=42, max_depth=10),
            'الغابة العشوائية': RandomForestRegressor(n_estimators=100, random_state=42),
            'تعزيز التدرج': GradientBoostingRegressor(random_state=42),
            'AdaBoost': AdaBoostRegressor(random_state=42),
            'Bagging': BaggingRegressor(random_state=42),
            'Extra Trees': ExtraTreesRegressor(random_state=42),
        }
        res = []
        for name, m in models.items():
            m.fit(X_train_s, y_train)
            pred = m.predict(X_test_s)
            mse = mean_squared_error(y_test, pred)
            r2 = r2_score(y_test, pred)
            res.append({'النموذج': name, 'MSE': round(mse, 2), 'R² Score': round(r2, 4), 'RMSE': round(np.sqrt(mse), 2)})
        return pd.DataFrame(res), df_ml

    res_df, ml_data = get_ml_results()

    ml_col1, ml_col2 = st.columns([2, 1])
    with ml_col1:
        fig_ml = px.bar(res_df, x='النموذج', y='R² Score', text='R² Score', title="مقارنة أداء النماذج (R² Score)", color_discrete_sequence=['#00a859'])
        fig_ml.update_layout(paper_bgcolor="#ffffff", plot_bgcolor="#ffffff", font=dict(color="#0f172a"), height=350)
        st.plotly_chart(fig_ml, use_container_width=True)

    with ml_col2:
        fig_dist = px.histogram(ml_data, x='price', nbins=30, title="توزيع الأسعار في بيانات التدريب", color_discrete_sequence=['#10b981'])
        fig_dist.update_layout(paper_bgcolor="#ffffff", plot_bgcolor="#ffffff", font=dict(color="#0f172a"), height=350)
        st.plotly_chart(fig_dist, use_container_width=True)

    st.dataframe(res_df, use_container_width=True)