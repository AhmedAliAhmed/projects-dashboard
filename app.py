import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# ============================================
# 1. إعداد الصفحة وستايل QuickBooks الأبيض الفاخر
# ============================================
st.set_page_config(
    page_title="QuickBooks Financial Dashboard - شركة العمران المتقدم",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"], [data-testid="stAppViewContainer"], .main {
        font-family: 'Cairo', 'Inter', sans-serif !important;
        direction: rtl;
        text-align: right;
        background-color: #F8FAFC !important;
        color: #0F172A !important;
    }
    
    /* بطاقات KPIs بنمط QuickBooks */
    [data-testid="stMetric"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 16px !important;
        padding: 16px 20px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
        margin-bottom: 12px;
    }
    
    [data-testid="stMetricLabel"] {
        color: #64748B !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stMetricValue"] {
        color: #0F172A !important;
        font-size: 1.6rem !important;
        font-weight: 800 !important;
    }

    /* التبويبات Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: transparent;
        border-bottom: 2px solid #E2E8F0;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        border-radius: 0px;
        color: #64748B;
        font-weight: 700;
        font-size: 15px;
    }
    
    .stTabs [aria-selected="true"] {
        color: #0284C7 !important;
        border-bottom: 3px solid #0284C7 !important;
    }

    /* زر استخراج التقرير PDF وردي/بنفسجي بارز مثل الصورة */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #a855f7 0%, #ec4899 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 9999px !important;
        padding: 10px 24px !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        box-shadow: 0 4px 14px rgba(168, 85, 247, 0.35) !important;
        transition: all 0.2s ease;
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(168, 85, 247, 0.45) !important;
    }
</style>
""", unsafe_allow_html=True)


# ============================================
# 2. تحميل بيانات المشاريع الفعلية
# ============================================
@st.cache_data
def get_actual_projects_data():
    raw_data = [
        {"id": 1, "project_name": "تقديم الخدمات الاستشارية لدراسة تطوير خطط تشغيل و صيانة المرافق الهامة", "total_due": 3237150.00, "raised": 0.00, "payment_order_issued": 2608200.00, "target_raised": 628950.00},
        {"id": 2, "project_name": "الاشراف علي تصميم و انشاء المختبر البيطري المركزي", "total_due": 789063.30, "raised": 0.00, "payment_order_issued": 394531.65, "target_raised": 394531.65},
        {"id": 3, "project_name": "تقديم الخدمات الاستشارية للاشراف علي المشاريع الهندسية ببنك التنمية", "total_due": 241500.00, "raised": 241500.00, "payment_order_issued": 0.00, "target_raised": 0.00},
        {"id": 4, "project_name": "الاتفاقية الاطارية لخدمات الاشراف علي مشاريع إدارة المرافق بالمنطقة الوسطي", "total_due": 20152734.68, "raised": 0.00, "payment_order_issued": 6343344.10, "target_raised": 13809390.58},
        {"id": 5, "project_name": "الاشراف علي إدارة المرافق بالمنطقة الجنوبية", "total_due": 4222488.43, "raised": 0.00, "payment_order_issued": 3222488.43, "target_raised": 1000000.00},
        {"id": 6, "project_name": "الخدمات الاستشارية للاستفادة من المياه الجوفية و السطحية و مشاريع درء اخطار السيول", "total_due": 4972625.00, "raised": 1752600.00, "payment_order_issued": 2187300.00, "target_raised": 1032725.00},
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


# ============================================
# 3. مولد التقرير التنفيذي PDF المباشر
# ============================================
def generate_pdf_report(df, total_due, total_paid, total_raised, total_target):
    rows_html = ""
    for idx, row in df.iterrows():
        rows_html += f"""
        <tr>
            <td style="padding: 8px; border: 1px solid #cbd5e1; text-align: center;">{row['id']}</td>
            <td style="padding: 8px; border: 1px solid #cbd5e1; text-align: right; font-weight: bold;">{row['project_name']}</td>
            <td style="padding: 8px; border: 1px solid #cbd5e1; text-align: left;">{row['total_due']:,.2f} ﷼</td>
            <td style="padding: 8px; border: 1px solid #cbd5e1; text-align: left;">{row['raised']:,.2f} ﷼</td>
            <td style="padding: 8px; border: 1px solid #cbd5e1; text-align: left; color: #059669; font-weight: bold;">{row['payment_order_issued']:,.2f} ﷼</td>
            <td style="padding: 8px; border: 1px solid #cbd5e1; text-align: left; color: #d97706;">{row['target_raised']:,.2f} ﷼</td>
        </tr>
        """

    return f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>تقرير المستخلصات التنفيذي - شركة العمران المتقدم</title>
        <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Cairo', sans-serif; padding: 30px; background-color: #fff; color: #0f172a; }}
            .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #009640; padding-bottom: 15px; margin-bottom: 25px; }}
            .title {{ font-size: 22px; font-weight: 800; color: #0f172a; margin: 0; }}
            .kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 25px; }}
            .kpi-card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px; text-align: center; }}
            .kpi-title {{ font-size: 12px; color: #64748b; margin-bottom: 4px; }}
            .kpi-value {{ font-size: 16px; font-weight: 700; color: #0f172a; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 12px; }}
            th {{ background-color: #0f172a; color: white; padding: 10px; border: 1px solid #0f172a; text-align: center; }}
        </style>
    </head>
    <body onload="window.print()">
        <div class="header">
            <div>
                <h1 class="title">التقرير المالي لخطط المستخلصات - أغسطس</h1>
                <p style="margin: 3px 0 0 0; color: #64748b; font-size: 13px;">تاريخ الإصدار: {datetime.now().strftime('%Y-%m-%d')}</p>
            </div>
            <div style="text-align: left;">
                <h2 style="margin: 0; color: #009640; font-size: 22px; font-weight: 900;">شركة العمران المتقدم</h2>
                <span style="font-size: 11px; color: #64748b;">OMRAN ADVANCED COMPANY</span>
            </div>
        </div>

        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">إجمالي المستحق</div>
                <div class="kpi-value">{total_due:,.2f} ﷼</div>
            </div>
            <div class="kpi-card" style="border-top: 3px solid #10b981;">
                <div class="kpi-title">صدر له أمر دفع</div>
                <div class="kpi-value" style="color: #059669;">{total_paid:,.2f} ﷼</div>
            </div>
            <div class="kpi-card" style="border-top: 3px solid #3b82f6;">
                <div class="kpi-title">مستخلصات مرفوعة</div>
                <div class="kpi-value" style="color: #2563eb;">{total_raised:,.2f} ﷼</div>
            </div>
            <div class="kpi-card" style="border-top: 3px solid #f59e0b;">
                <div class="kpi-title">مستهدف رفعها</div>
                <div class="kpi-value" style="color: #d97706;">{total_target:,.2f} ﷼</div>
            </div>
        </div>

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
            </tbody>
        </table>
    </body>
    </html>
    """


# ============================================
# 4. التطبيق الرئيسي
# ============================================
def main():
    df = get_actual_projects_data()

    total_due = df['total_due'].sum()
    total_raised = df['raised'].sum()
    total_paid = df['payment_order_issued'].sum()
    total_target = df['target_raised'].sum()

    paid_pct = (total_paid / total_due * 100) if total_due > 0 else 0
    raised_pct = (total_raised / total_due * 100) if total_due > 0 else 0

    # --------------------------------------------
    # الهيدر العلوي بنمط QuickBooks
    # --------------------------------------------
    col_h1, col_h2 = st.columns([3, 1])
    
    with col_h1:
        st.markdown("<h1 style='font-size: 26px; font-weight: 800; margin: 0;'>QuickBooks financial dashboard</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #64748b; font-size: 14px; margin-top: 4px;'>🏢 شركة العمران المتقدم • Omran Advanced Company</p>", unsafe_allow_html=True)

    with col_h2:
        # زر استخراج التقرير PDF فقط كما بالصورة
        trigger_pdf = st.button("✨ AI Summary / PDF Report", use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --------------------------------------------
    # شريط التبويبات العلوي (Profit and Loss, Cash flow, Balance Sheet)
    # --------------------------------------------
    tab1, tab2, tab3 = st.tabs(["Profit and Loss", "Cash flow", "Balance Sheet"])

    # نافذة طباعة PDF عند الضغط على الزر
    if trigger_pdf:
        st.info("📄 جارٍ تجهيز التقرير واستخراج ملف PDF...")
        pdf_html = generate_pdf_report(df, total_due, total_paid, total_raised, total_target)
        st.components.v1.html(pdf_html, height=600, scrolling=True)

    # ============================================
    # التبويب الأول: Profit and Loss
    # ============================================
    with tab1:
        st.markdown("<h3 style='font-size: 18px; font-weight: 700; color: #334155; margin-bottom: 16px;'>Profit and Loss overview</h3>", unsafe_allow_html=True)

        col_left_kpis, col_right_chart = st.columns([2, 3])

        # 6 بطاقات KPIs على اليمين شبيهة بالصورة
        with col_left_kpis:
            k1, k2 = st.columns(2)
            with k1:
                st.metric("Total Income (المستحق)", f"${total_due/1e6:.1f}M")
                st.metric("Paid Ratio (نسبة الصرف)", f"{paid_pct:.1f}%")
                st.metric("Raised Ratio (نسبة الإنجاز)", f"{raised_pct:.1f}%")
            with k2:
                st.metric("Gross Paid (أمر دفع)", f"${total_paid/1e6:.1f}M")
                st.metric("Raised Amount (المرفوع)", f"${total_raised/1e6:.1f}M")
                st.metric("Target (المستهدف)", f"${total_target/1e6:.1f}M")

        # الرسم البياني المختلط على اليسار
        with col_right_chart:
            st.markdown("<div style='background-color: white; padding: 15px; border-radius: 16px; border: 1px solid #E2E8F0;'>", unsafe_allow_html=True)
            st.markdown("<b style='font-size: 15px; color: #0F172A;'>Operating Income and Expenses past 12 mos</b>", unsafe_allow_html=True)
            
            fig_combo = go.Figure()
            fig_combo.add_trace(go.Bar(x=df['id'].astype(str), y=df['payment_order_issued']/1e6, name='Paid Order (امر دفع)', marker_color='#0284C7'))
            fig_combo.add_trace(go.Bar(x=df['id'].astype(str), y=df['target_raised']/1e6, name='Target (مستهدف)', marker_color='#EAB308'))
            fig_combo.add_trace(go.Scatter(x=df['id'].astype(str), y=df['total_due']/1e6, name='Total Due (المستحق)', line=dict(color='#DC2626', width=2)))

            fig_combo.update_layout(
                height=310,
                template="plotly_white",
                font=dict(family="Cairo", size=11),
                barmode='group',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(l=10, r=10, t=30, b=10)
            )
            st.plotly_chart(fig_combo, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # الصف السفلي من الرسوم البيانية
        col_bot1, col_bot2 = st.columns([1, 1])

        with col_bot1:
            st.markdown("<div style='background-color: white; padding: 15px; border-radius: 16px; border: 1px solid #E2E8F0;'>", unsafe_allow_html=True)
            st.markdown("<b style='font-size: 15px; color: #0F172A;'>Gross Profit past 12 mos</b>", unsafe_allow_html=True)
            
            fig_line = px.line(df, x='id', y='total_due', markers=True)
            fig_line.update_traces(line_color='#0284C7', line_width=2.5)
            fig_line.update_layout(height=260, template="plotly_white", font=dict(family="Cairo"), margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig_line, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_bot2:
            st.markdown("<div style='background-color: white; padding: 15px; border-radius: 16px; border: 1px solid #E2E8F0;'>", unsafe_allow_html=True)
            st.markdown("<b style='font-size: 15px; color: #0F172A;'>Expense by Account name as of today</b>", unsafe_allow_html=True)
            
            fig_donut = px.pie(df, values='total_due', names='project_name', hole=0.55, color_discrete_sequence=px.colors.qualitative.Set2)
            fig_donut.update_layout(height=260, template="plotly_white", font=dict(family="Cairo"), showlegend=False, margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig_donut, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # ============================================
    # التبويب الثاني: Cash flow
    # ============================================
    with tab2:
        st.subheader("📈 تحليل التدفقات النقدية والتحصيل")
        st.dataframe(
            df[['id', 'project_name', 'total_due', 'payment_order_issued', 'raised']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "id": st.column_config.Column("م"),
                "project_name": st.column_config.Column("اسم المشروع"),
                "total_due": st.column_config.NumberColumn("المستحق", format="%.2f ﷼"),
                "payment_order_issued": st.column_config.NumberColumn("أمر دفع", format="%.2f ﷼"),
                "raised": st.column_config.NumberColumn("مرفوع", format="%.2f ﷼")
            }
        )

    # ============================================
    # التبويب الثالث: Balance Sheet
    # ============================================
    with tab3:
        st.subheader("📋 السجل التفصيلي المكتمل للمشاريع")
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "id": st.column_config.Column("م"),
                "project_name": st.column_config.Column("اسم المشروع"),
                "total_due": st.column_config.NumberColumn("المستحق حتى نهاية أغسطس", format="%.2f ﷼"),
                "raised": st.column_config.NumberColumn("المستخلصات المرفوعة", format="%.2f ﷼"),
                "payment_order_issued": st.column_config.NumberColumn("صدر لها أمر دفع", format="%.2f ﷼"),
                "target_raised": st.column_config.NumberColumn("مستهدف رفعها", format="%.2f ﷼"),
                "status": st.column_config.Column("الحالة")
            }
        )

if __name__ == "__main__":
    main()