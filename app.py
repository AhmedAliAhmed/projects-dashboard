import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# ============================================
# 1. إعداد الصفحة وتنسيق الخطوط (RTL)
# ============================================
st.set_page_config(
    page_title="الموقف المالي لمستخلصات المشاريع - شركة العمران المتقدم",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تنسيق واجهة المستخدم باللغة العربية خط Cairo وتنسيق RTL
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"], div, span, h1, h2, h3, h4, p {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl;
        text-align: right;
    }
    
    /* بطاقات KPIs */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #334155;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    [data-testid="stMetricValue"] {
        font-size: 1.4rem !important;
        font-weight: 700 !important;
        color: #38bdf8 !important;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.95rem !important;
        color: #94a3b8 !important;
    }
    
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }

    div.stButton > button:first-child {
        background-color: #009640 !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)


# ============================================
# 2. عرض شعار شركة العمران المتقدم
# ============================================
def render_logo():
    logo_path = "logo.png"
    assets_logo_path = "assets/logo.png"
    
    if os.path.exists(logo_path):
        st.image(logo_path, width=250)
    elif os.path.exists(assets_logo_path):
        st.image(assets_logo_path, width=250)
    else:
        # SVG لشعار شركة العمران المتقدم
        svg_logo = """
        <div style="background-color: white; padding: 8px 14px; border-radius: 10px; display: inline-block; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 210" width="220" height="92">
              <text x="10" y="80" font-family="'Cairo', sans-serif" font-weight="900" font-size="82" fill="#2d3136" letter-spacing="1">OMRAN</text>
              <rect x="10" y="105" width="95" height="24" fill="#009640" rx="2"/>
              <text x="115" y="125" font-family="'Cairo', sans-serif" font-weight="700" font-size="25" fill="#2d3136" letter-spacing="0.5">ADVANCED COMPANY</text>
              <text x="490" y="195" font-family="'Cairo', sans-serif" font-weight="700" font-size="44" fill="#4a5568" text-anchor="end">شركة العمران المتقدم</text>
            </svg>
        </div>
        """
        st.markdown(svg_logo, unsafe_allow_html=True)


# ============================================
# 3. البيانات المالية المحينة (نهاية أغسطس 2026م)
# ============================================
@st.cache_data
def get_actual_projects_data():
    raw_data = [
        {"id": 1, "project_name": "تقديم الخدمات الاستشارية لدراسة تطوير خطط تشغيل و صيانة المرافق الهامة", "total_due": 628950.00, "raised": 0.00, "payment_order_issued": 0.00, "target_raised": 628950.00},
        {"id": 2, "project_name": "الاشراف علي تصميم و انشاء المختبر البيطري المركزي", "total_due": 789063.30, "raised": 438368.50, "payment_order_issued": 394531.65, "target_raised": 0.00},
        {"id": 3, "project_name": "تقديم الخدمات الاستشارية للاشراف علي المشاريع الهندسية ببنك التنمية", "total_due": 241500.00, "raised": 241500.00, "payment_order_issued": 0.00, "target_raised": 0.00},
        {"id": 4, "project_name": "الاتفاقية الاطارية لخدمات الاشراف علي مشاريع إدارة المرافق بالمنطقة الوسطي", "total_due": 20152734.68, "raised": 0.00, "payment_order_issued": 6343344.10, "target_raised": 13809390.58},
        {"id": 5, "project_name": "الاشراف علي إدارة المرافق بالمنطقة الجنوبية", "total_due": 4222488.43, "raised": 0.00, "payment_order_issued": 3222488.43, "target_raised": 1000000.00},
        {"id": 6, "project_name": "الخدمات الاستشارية للاستفادة من المياه الجوفية و السطحية و مشاريع درء اخطار السيول", "total_due": 4260775.00, "raised": 1752600.00, "payment_order_issued": 1475450.00, "target_raised": 1032725.00},
        {"id": 7, "project_name": "الاتفاقية الاطارية لتصميم مشاريع المؤسسة العامة للري امر عمل (02)", "total_due": 5398330.00, "raised": 4508000.00, "payment_order_issued": 0.00, "target_raised": 890330.00},
        {"id": 8, "project_name": "ترميز مباني التراث المعماري وسط الرياض", "total_due": 3910460.00, "raised": 0.00, "payment_order_issued": 0.00, "target_raised": 3910460.00},
        {"id": 9, "project_name": "دراسة و تصميم مشروع انشاء قاعة الطعام بالمقر الرئيسي", "total_due": 439875.00, "raised": 439875.00, "payment_order_issued": 0.00, "target_raised": 0.00},
        {"id": 10, "project_name": "مبالغ تم دفعها للهندسية ولم يتم تحصيلها", "total_due": 2864500.00, "raised": 0.00, "payment_order_issued": 0.00, "target_raised": 2864500.00},
        {"id": 11, "project_name": "الاشراف علي المشاريع الصغيرة بجميع مناطق المملكة (المرحلة الثانية)", "total_due": 2996034.00, "raised": 0.00, "payment_order_issued": 0.00, "target_raised": 2996034.00},
        {"id": 12, "project_name": "الاتفاقية الاطارية لخدمات الاشراف علي مشاريع إدارة المرافق بالمنطقة الوسطي (2)", "total_due": 3800000.00, "raised": 0.00, "payment_order_issued": 0.00, "target_raised": 3800000.00}
    ]
    df = pd.DataFrame(raw_data)
    
    def classify_status(row):
        if row['payment_order_issued'] >= row['total_due'] and row['total_due'] > 0:
            return 'صرف كامل'
        elif row['payment_order_issued'] > 0:
            return 'صرف جزئي'
        elif row['raised'] > 0:
            return 'مرفوع حالياً'
        else:
            return 'بانتظار الرفع'
            
    df['status'] = df.apply(classify_status, axis=1)
    return df


def load_data(uploaded_file):
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file, skiprows=3, usecols="B:F", nrows=12)
            df.columns = ['project_name', 'total_due', 'raised', 'payment_order_issued', 'target_raised']
            df['id'] = range(1, len(df) + 1)
            df = df.fillna(0)
            return df
        except Exception:
            pass
    return get_actual_projects_data()


# ============================================
# 4. مولد التقرير التنفيذي PDF المحدث للطباعة والحفظ
# ============================================
def generate_full_pdf_html(df, total_due, total_paid, total_raised, total_target):
    paid_pct = (total_paid / total_due * 100) if total_due > 0 else 0
    raised_pct = (total_raised / total_due * 100) if total_due > 0 else 0
    target_pct = (total_target / total_due * 100) if total_due > 0 else 0

    rows_html = ""
    for idx, row in df.iterrows():
        rows_html += f"""
        <tr>
            <td style="padding: 6px; border: 1px solid #cbd5e1; text-align: center;">{row['id']}</td>
            <td style="padding: 6px; border: 1px solid #cbd5e1; text-align: right; font-weight: bold;">{row['project_name']}</td>
            <td style="padding: 6px; border: 1px solid #cbd5e1; text-align: left;">{row['total_due']:,.2f} ﷼</td>
            <td style="padding: 6px; border: 1px solid #cbd5e1; text-align: left;">{row['raised']:,.2f} ﷼</td>
            <td style="padding: 6px; border: 1px solid #cbd5e1; text-align: left; color: #059669; font-weight: bold;">{row['payment_order_issued']:,.2f} ﷼</td>
            <td style="padding: 6px; border: 1px solid #cbd5e1; text-align: left; color: #d97706;">{row['target_raised']:,.2f} ﷼</td>
        </tr>
        """

    project_bars_html = ""
    for idx, row in df.iterrows():
        p_pct = (row['payment_order_issued'] / row['total_due'] * 100) if row['total_due'] > 0 else 0
        r_pct = (row['raised'] / row['total_due'] * 100) if row['total_due'] > 0 else 0
        t_pct = (row['target_raised'] / row['total_due'] * 100) if row['total_due'] > 0 else 0
        
        project_bars_html += f"""
        <div style="margin-bottom: 8px;">
            <div style="font-size: 11px; font-weight: bold; margin-bottom: 2px;">{row['id']}. {row['project_name']} ({row['total_due']:,.0f} ﷼)</div>
            <div style="background: #e2e8f0; height: 10px; border-radius: 5px; overflow: hidden; display: flex;">
                <div style="width: {min(p_pct, 100)}%; background: #10b981;" title="مدفوع"></div>
                <div style="width: {min(r_pct, 100)}%; background: #3b82f6;" title="مرفوع"></div>
                <div style="width: {min(t_pct, 100)}%; background: #f59e0b;" title="مستهدف"></div>
            </div>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>الموقف المالي لمستخلصات المشاريع حتى نهاية أغسطس 2026م - شركة العمران المتقدم</title>
        <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap" rel="stylesheet">
        <style>
            @media print {{
                @page {{ size: A4 portrait; margin: 10mm; }}
                body {{ background: white !important; -webkit-print-color-adjust: exact; }}
            }}
            body {{ font-family: 'Cairo', sans-serif; padding: 20px; background-color: #fff; color: #0f172a; direction: rtl; }}
            .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #009640; padding-bottom: 12px; margin-bottom: 20px; }}
            .title {{ font-size: 20px; font-weight: 800; color: #0f172a; margin: 0; }}
            .subtitle {{ font-size: 12px; color: #64748b; margin-top: 3px; }}
            
            .kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 20px; }}
            .kpi-card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px; text-align: center; }}
            .kpi-title {{ font-size: 11px; color: #64748b; margin-bottom: 3px; font-weight: 600; }}
            .kpi-value {{ font-size: 15px; font-weight: 800; color: #0f172a; }}
            .kpi-sub {{ font-size: 10px; margin-top: 2px; font-weight: 700; }}

            .section-header {{ font-size: 14px; font-weight: 700; color: #1e293b; margin: 18px 0 10px 0; border-right: 4px solid #009640; padding-right: 8px; }}
            
            .donut-box {{ display: flex; justify-content: space-around; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; margin-bottom: 20px; text-align: center; }}
            .donut-item {{ flex: 1; }}
            .badge {{ display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-left: 4px; }}

            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 10px; }}
            th {{ background-color: #0f172a; color: white; padding: 8px 4px; border: 1px solid #0f172a; text-align: center; }}
            td {{ padding: 6px 4px; border: 1px solid #cbd5e1; }}
            tr:nth-child(even) {{ background-color: #f8fafc; }}
            .total-row {{ background-color: #f1f5f9; font-weight: bold; font-size: 11px; }}
        </style>
    </head>
    <body onload="window.print()">
        <div class="header">
            <div>
                <h1 class="title">الموقف المالي لمستخلصات المشاريع حتى نهاية أغسطس 2026م</h1>
                <p class="subtitle">شركة العمران المتقدم | تاريخ الإصدار: {datetime.now().strftime('%Y-%m-%d')}</p>
            </div>
            <div style="text-align: left;">
                <h2 style="margin: 0; color: #009640; font-size: 20px; font-weight: 900;">شركة العمران المتقدم</h2>
                <span style="font-size: 10px; color: #64748b;">OMRAN ADVANCED COMPANY</span>
            </div>
        </div>

        <!-- 1. بطاقات KPIs الرئيسية -->
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">💰 إجمالي المستحق</div>
                <div class="kpi-value">{total_due:,.2f} ﷼</div>
                <div class="kpi-sub" style="color: #64748b;">12 مشروعاً</div>
            </div>
            <div class="kpi-card" style="border-top: 3px solid #10b981;">
                <div class="kpi-title">💳 صدر له أمر دفع</div>
                <div class="kpi-value" style="color: #059669;">{total_paid:,.2f} ﷼</div>
                <div class="kpi-sub" style="color: #10b981;">{paid_pct:.1f}% من المستحق</div>
            </div>
            <div class="kpi-card" style="border-top: 3px solid #3b82f6;">
                <div class="kpi-title">📤 مستخلصات مرفوعة</div>
                <div class="kpi-value" style="color: #2563eb;">{total_raised:,.2f} ﷼</div>
                <div class="kpi-sub" style="color: #3b82f6;">{raised_pct:.1f}% من المستحق</div>
            </div>
            <div class="kpi-card" style="border-top: 3px solid #f59e0b;">
                <div class="kpi-title">🎯 مستهدف رفعها</div>
                <div class="kpi-value" style="color: #d97706;">{total_target:,.2f} ﷼</div>
                <div class="kpi-sub" style="color: #f59e0b;">{target_pct:.1f}% من المستحق</div>
            </div>
        </div>

        <!-- 2. التوزيع المالي الإجمالي -->
        <div class="section-header">🎯 النسبة الإجمالية لحالة المبالغ المالية</div>
        <div class="donut-box">
            <div class="donut-item">
                <span class="badge" style="background: #10b981;"></span>
                <span style="font-weight: bold;">صدر له أمر دفع:</span> {total_paid:,.2f} ﷼ ({paid_pct:.1f}%)
            </div>
            <div class="donut-item">
                <span class="badge" style="background: #3b82f6;"></span>
                <span style="font-weight: bold;">مرفوع حالياً:</span> {total_raised:,.2f} ﷼ ({raised_pct:.1f}%)
            </div>
            <div class="donut-item">
                <span class="badge" style="background: #f59e0b;"></span>
                <span style="font-weight: bold;">مستهدف رفعه:</span> {total_target:,.2f} ﷼ ({target_pct:.1f}%)
            </div>
        </div>

        <!-- 3. مخطط توزيع المستخلصات تفصيلياً -->
        <div class="section-header">📊 توزيع نسب المستخلصات لكل مشروع</div>
        <div style="background: #fafafa; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; margin-bottom: 20px;">
            {project_bars_html}
        </div>

        <!-- 4. جدول المستخلصات التفصيلي الكامل -->
        <div class="section-header">📋 جدول المستخلصات التفصيلي للمشاريع</div>
        <table>
            <thead>
                <tr>
                    <th>م</th>
                    <th>اسم المشروع</th>
                    <th>المستحق حتى نهاية أغسطس</th>
                    <th>المستخلصات المرفوعة</th>
                    <th>صدر لها أمر دفع</th>
                    <th>مستهدف رفعها</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
                <tr class="total-row">
                    <td colspan="2" style="text-align: center;">الإجمالي العام</td>
                    <td style="text-align: left;">{total_due:,.2f} ﷼</td>
                    <td style="text-align: left;">{total_raised:,.2f} ﷼</td>
                    <td style="text-align: left; color: #059669;">{total_paid:,.2f} ﷼</td>
                    <td style="text-align: left; color: #d97706;">{total_target:,.2f} ﷼</td>
                </tr>
            </tbody>
        </table>
    </body>
    </html>
    """


# ============================================
# 5. التطبيق الرئيسي
# ============================================
def main():
    st.sidebar.title("⚙️ الفلاتر واستخراج التقرير")
    st.sidebar.markdown("---")
    
    uploaded_file = st.sidebar.file_uploader("📂 رفع ملف Excel (اختياري)", type=["xlsx", "xls"])
    df = load_data(uploaded_file)

    # فلاتر البحث
    search_query = st.sidebar.text_input("🔍 بحث باسم المشروع:")
    selected_statuses = st.sidebar.multiselect(
        "حالة المستخلصات:",
        options=df['status'].unique(),
        default=df['status'].unique()
    )

    filtered_df = df[df['status'].isin(selected_statuses)]
    if search_query:
        filtered_df = filtered_df[filtered_df['project_name'].str.contains(search_query, case=False)]

    if filtered_df.empty:
        st.warning("⚠️ لا توجد مشاريع تطابق الفلاتر المحددة.")
        return

    # حساب المجاميع العامة
    total_due = filtered_df['total_due'].sum()
    total_raised = filtered_df['raised'].sum()
    total_paid = filtered_df['payment_order_issued'].sum()
    total_target = filtered_df['target_raised'].sum()

    paid_pct = (total_paid / total_due * 100) if total_due > 0 else 0
    raised_pct = (total_raised / total_due * 100) if total_due > 0 else 0
    target_pct = (total_target / total_due * 100) if total_due > 0 else 0

    # الهيدر والشعار
    col_logo, col_head, col_btn = st.columns([1.2, 2.2, 1.2])
    with col_logo:
        render_logo()
    with col_head:
        st.title("الموقف المالي لمستخلصات المشاريع حتى نهاية أغسطس 2026م")
        st.caption("شركة العمران المتقدم • موقف المستخلصات التفصيلي المحدث")

    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        export_pdf = st.button("📄 استخراج التقرير PDF", type="primary", use_container_width=True)

    # زر استخراج PDF بالشريط الجانبي
    st.sidebar.markdown("---")
    sidebar_pdf = st.sidebar.button("📄 استخراج التقرير PDF", use_container_width=True)

    # تشغيل نافذة طباعة التقرير الشامل كـ PDF
    if export_pdf or sidebar_pdf:
        st.info("🖨️ جاري فتح نافذة طباعة وحفظ التقرير بصيغة PDF...")
        pdf_code = generate_full_pdf_html(filtered_df, total_due, total_paid, total_raised, total_target)
        st.components.v1.html(pdf_code, height=750, scrolling=True)

    st.markdown("---")

    # ============================================
    # 6. بطاقات KPI
    # ============================================
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    kpi1.metric("💰 إجمالي المستحق", f"{total_due:,.2f} ﷼")
    kpi2.metric("💳 صدر لها أمر دفع", f"{total_paid:,.2f} ﷼", delta=f"{paid_pct:.1f}% من المستحق")
    kpi3.metric("📤 مستخلصات مرفوعة", f"{total_raised:,.2f} ﷼", delta=f"{raised_pct:.1f}% من المستحق")
    kpi4.metric("🎯 مستهدف رفعها", f"{total_target:,.2f} ﷼", delta=f"{target_pct:.1f}% من المستحق", delta_color="inverse")

    st.markdown("---")

    # ============================================
    # 7. الرسوم البيانية الرئيسية
    # ============================================
    col_c1, col_c2 = st.columns([2, 1])

    with col_c1:
        st.subheader("📊 تفاصيل المستخلصات لكل مشروع")
        
        melted_df = filtered_df.melt(
            id_vars=['project_name'],
            value_vars=['payment_order_issued', 'raised', 'target_raised'],
            var_name='Category',
            value_name='Amount'
        )
        
        category_map = {
            'payment_order_issued': 'صدر له أمر دفع',
            'raised': 'مرفوع حالياً',
            'target_raised': 'مستهدف رفعه'
        }
        melted_df['Category'] = melted_df['Category'].map(category_map)
        
        fig_bar = px.bar(
            melted_df,
            x='Amount',
            y='project_name',
            color='Category',
            orientation='h',
            barmode='stack',
            labels={'Amount': 'المبلغ (ريال)', 'project_name': 'المشروع', 'Category': 'الحالة'},
            color_discrete_map={
                'صدر له أمر دفع': '#10b981',
                'مرفوع حالياً': '#3b82f6',
                'مستهدف رفعه': '#f59e0b'
            }
        )
        fig_bar.update_layout(
            height=450,
            font=dict(family="Cairo"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=0, r=0, t=30, b=0)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_c2:
        st.subheader("🎯 النسبة الإجمالية لحالة المبالغ")
        
        summary_pie = pd.DataFrame({
            'الحالة': ['صدر له أمر دفع', 'مرفوع حالياً', 'مستهدف رفعه'],
            'المبلغ': [total_paid, total_raised, total_target]
        })
        
        fig_pie = px.pie(
            summary_pie,
            values='المبلغ',
            names='الحالة',
            hole=0.45,
            color='الحالة',
            color_discrete_map={
                'صدر له أمر دفع': '#10b981',
                'مرفوع حالياً': '#3b82f6',
                'مستهدف رفعه': '#f59e0b'
            }
        )
        fig_pie.update_traces(textinfo='percent+label')
        fig_pie.update_layout(
            height=450,
            font=dict(family="Cairo"),
            showlegend=False
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # ============================================
    # 8. الرسوم البيانية الفرعية
    # ============================================
    col_c3, col_c4 = st.columns(2)

    with col_c3:
        st.subheader("🏆 أكبر 5 مشاريع استحقاقاً")
        top5 = filtered_df.nlargest(5, 'total_due')
        fig_top5 = px.bar(
            top5,
            x='total_due',
            y='project_name',
            orientation='h',
            text_auto=',.0f',
            color='total_due',
            color_continuous_scale='Blues',
            labels={'total_due': 'المستحق (ريال)', 'project_name': ''}
        )
        fig_top5.update_layout(height=320, font=dict(family="Cairo"), showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig_top5, use_container_width=True)

    with col_c4:
        st.subheader("📌 توزيع المشاريع حسب حالة الصرف")
        status_df = filtered_df['status'].value_counts().reset_index()
        status_df.columns = ['الحالة', 'عدد المشاريع']
        
        fig_status = px.bar(
            status_df,
            x='الحالة',
            y='عدد المشاريع',
            color='الحالة',
            text_auto=True,
            color_discrete_map={'صرف جزئي': '#10b981', 'مرفوع حالياً': '#3b82f6', 'بانتظار الرفع': '#f59e0b', 'صرف كامل': '#059669'}
        )
        fig_status.update_layout(height=320, font=dict(family="Cairo"), showlegend=False)
        st.plotly_chart(fig_status, use_container_width=True)

    # ============================================
    # 9. الجدول التفصيلي الكامل
    # ============================================
    st.markdown("---")
    st.subheader("📋 جدول المستخلصات التفصيلي للمشاريع")

    table_df = filtered_df[['id', 'project_name', 'total_due', 'raised', 'payment_order_issued', 'target_raised', 'status']].copy()
    
    st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "id": st.column_config.Column("م", width="small"),
            "project_name": st.column_config.Column("المشروع", width="large"),
            "total_due": st.column_config.NumberColumn("المستحق حتى نهاية أغسطس", format="%.2f ﷼"),
            "raised": st.column_config.NumberColumn("المستخلصات المرفوعة", format="%.2f ﷼"),
            "payment_order_issued": st.column_config.NumberColumn("صدر لها أمر دفع", format="%.2f ﷼"),
            "target_raised": st.column_config.NumberColumn("مستهدف رفعها", format="%.2f ﷼"),
            "status": st.column_config.Column("حالة المشروع")
        }
    )

if __name__ == "__main__":
    main()