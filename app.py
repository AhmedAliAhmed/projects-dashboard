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
    page_title="لوحة مستخلصات أداء المشاريع",
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
</style>
""", unsafe_allow_html=True)

# ============================================
# 2. إدراج بيانات المشاريع الفعلية (أغسطس)
# ============================================
@st.cache_data
def get_actual_projects_data():
    raw_data = [
        {
            "id": 1,
            "project_name": "تقديم الخدمات الاستشارية لدراسة تطوير خطط تشغيل و صيانة المرافق الهامة",
            "total_due": 3237150.00,
            "raised": 0.00,
            "payment_order_issued": 2608200.00,
            "target_raised": 628950.00
        },
        {
            "id": 2,
            "project_name": "الاشراف علي تصميم و انشاء المختبر البيطري المركزي",
            "total_due": 789063.30,
            "raised": 0.00,
            "payment_order_issued": 394531.65,
            "target_raised": 394531.65
        },
        {
            "id": 3,
            "project_name": "تقديم الخدمات الاستشارية للاشراف علي المشاريع الهندسية ببنك التنمية",
            "total_due": 241500.00,
            "raised": 241500.00,
            "payment_order_issued": 0.00,
            "target_raised": 0.00
        },
        {
            "id": 4,
            "project_name": "الاتفاقية الاطارية لخدمات الاشراف علي مشاريع إدارة المرافق بالمنطقة الوسطي",
            "total_due": 20152734.68,
            "raised": 0.00,
            "payment_order_issued": 6343344.10,
            "target_raised": 13809390.58
        },
        {
            "id": 5,
            "project_name": "الاشراف علي إدارة المرافق بالمنطقة الجنوبية",
            "total_due": 4222488.43,
            "raised": 0.00,
            "payment_order_issued": 3222488.43,
            "target_raised": 1000000.00
        },
        {
            "id": 6,
            "project_name": "الخدمات الاستشارية للاستفادة من المياه الجوفية و السطحية و مشاريع درء اخطار السيول",
            "total_due": 4972625.00,
            "raised": 1752600.00,
            "payment_order_issued": 2187300.00,
            "target_raised": 1032725.00
        },
        {
            "id": 7,
            "project_name": "الاتفاقية الاطارية لتصميم مشاريع المؤسسة العامة للري امر عمل (02)",
            "total_due": 5398330.00,
            "raised": 4508000.00,
            "payment_order_issued": 0.00,
            "target_raised": 890330.00
        },
        {
            "id": 8,
            "project_name": "ترميز مباني التراث المعماري وسط الرياض",
            "total_due": 3910460.00,
            "raised": 0.00,
            "payment_order_issued": 0.00,
            "target_raised": 3910460.00
        },
        {
            "id": 9,
            "project_name": "دراسة و تصميم مشروع انشاء قاعة الطعام بالمقر الرئيسي",
            "total_due": 439875.00,
            "raised": 439875.00,
            "payment_order_issued": 0.00,
            "target_raised": 0.00
        },
        {
            "id": 10,
            "project_name": "مبالغ تم دفعها للهندسية ولم يتم تحصيلها",
            "total_due": 2864500.00,
            "raised": 0.00,
            "payment_order_issued": 0.00,
            "target_raised": 2864500.00
        },
        {
            "id": 11,
            "project_name": "الاشراف علي المشاريع الصغيرة بجميع مناطق المملكة (المرحلة الثانية)",
            "total_due": 2996034.00,
            "raised": 0.00,
            "payment_order_issued": 0.00,
            "target_raised": 2996034.00
        },
        {
            "id": 12,
            "project_name": "الاتفاقية الاطارية لخدمات الاشراف علي مشاريع إدارة المرافق بالمنطقة الوسطي (2)",
            "total_due": 3800000.00,
            "raised": 0.00,
            "payment_order_issued": 0.00,
            "target_raised": 3800000.00
        }
    ]
    df = pd.DataFrame(raw_data)
    
    # تحديد حالة المستخلص للمشروع
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
# 3. التطبيق الرئيسي
# ============================================
def main():
    st.sidebar.title("⚙️ خيارات الفلترة والتصدير")
    st.sidebar.markdown("---")
    
    uploaded_file = st.sidebar.file_uploader("📂 رفع ملف Excel مُحدث (اختياري)", type=["xlsx", "xls"])
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

    # الهيدر الرئيسي
    col_head1, col_head2 = st.columns([3, 1])
    with col_head1:
        st.title("📊 لوحة مستخلصات أداء المشاريع - أغسطس")
        st.caption("متابعة المستخلصات المستحقة، المرفوعة، وأوامر الدفع الصادرة")
    with col_date := col_head2:
        st.markdown(f"**🗓️ الفترة:** حتى نهاية أغسطس\n\n**🔄 التحديث:** `{datetime.now().strftime('%Y-%m-%d')}`")

    st.markdown("---")

    # ============================================
    # 4. بطاقات KPI
    # ============================================
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    kpi1.metric("💰 إجمالي المستحق", f"{total_due:,.2f} ﷼")
    kpi2.metric("💳 صدر لها أمر دفع", f"{total_paid:,.2f} ﷼", delta=f"{paid_pct:.1f}% من المستحق")
    kpi3.metric("📤 مستخلصات مرفوعة", f"{total_raised:,.2f} ﷼", delta=f"{raised_pct:.1f}% من المستحق")
    kpi4.metric("🎯 مستهدف رفعها", f"{total_target:,.2f} ﷼", delta=f"{target_pct:.1f}% من المستحق", delta_color="inverse")

    st.markdown("---")

    # ============================================
    # 5. الرسوم البيانية الرئيسية
    # ============================================
    col_c1, col_c2 = st.columns([2, 1])

    with col_c1:
        st.subheader("📊 تفاصيل المستخلصات لكل مشروع")
        
        # تجهيز البيانات للرسم التجميعي
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
    # 6. الرسوم البيانية الفرعية
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
    # 7. الجدول التفصيلي الكامل
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

    # ============================================
    # 8. تصدير البيانات
    # ============================================
    st.sidebar.markdown("---")
    st.sidebar.download_button(
        label="📥 تحميل تقرير المستخلصات (CSV)",
        data=filtered_df.to_csv(index=False).encode('utf-8-sig'),
        file_name=f"August_Projects_Financial_Report_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

if __name__ == "__main__":
    main()