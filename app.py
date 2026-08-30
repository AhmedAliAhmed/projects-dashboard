import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
import os

# ============================================
# 1. إعداد الصفحة وتنسيق RTL العربي
# ============================================
st.set_page_config(
    page_title="لوحة مؤشرات أداء المشاريع",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تطبيق خط Cairo وتنسيق الاتجاه من اليمين لليسار (RTL)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    
    html, body, [class*="css"], div, span, h1, h2, h3, h4, p {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl;
        text-align: right;
    }
    
    /* تنسيق بطاقات KPI */
    [data-testid="stMetric"] {
        background-color: #1e293b;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    [data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
        color: #38bdf8 !important;
    }

    .css-1d3550e, [data-testid="stSidebar"] {
        direction: rtl;
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)


# ============================================
# 2. تحميل البيانات مع آلية Fallback ذكية
# ============================================
@st.cache_data(ttl=3600)
def generate_sample_data():
    """إنشاء بيانات افتراضية احترافية في حال عدم وجود ملف Excel"""
    projects = [
        'برج العمران التجاري', 'مجمع السكني المرحلة الثانية', 'مركز اللوجستيات الذكي',
        'مشروع البنية التحتية الشمسية', 'تطوير مركز البيانات الرئيسي', 'مشروع الجسر الشمالي',
        'مستشفى العمران العام', 'توسعة طريق الملك فهد', 'مجمع المستودعات المركزية'
    ]
    regions = ['الوسطى', 'الجنوبية', 'الشرقية', 'الغربية', 'الشمالية']
    
    data = []
    for i, proj in enumerate(projects):
        total_due = float(np.random.randint(10, 80) * 100000)
        raised = float(total_due * np.random.uniform(0.5, 0.95))
        payment_issued = float(raised * np.random.uniform(0.7, 1.0))
        target_raised = float(total_due * 0.9)
        region = regions[i % len(regions)]
        
        status = 'مكتمل' if payment_issued >= total_due else ('جاري' if raised > 0 else 'متوقف')
        
        data.append({
            'project_name': proj,
            'total_due': total_due,
            'raised': raised,
            'payment_order_issued': payment_issued,
            'target_raised': target_raised,
            'status': status,
            'region': region
        })
    
    return pd.DataFrame(data)


def load_data(uploaded_file):
    """تحميل البيانات من الملف المرفوع أو المسار المحلي أو البيانات الافتراضية"""
    file_path = "data/Projects Financial Dashboard Template.xlsx"
    
    if uploaded_file is not None:
        source = uploaded_file
    elif os.path.exists(file_path):
        source = file_path
    else:
        st.info("ℹ️ يتم تشغيل اللوحة باستخدام **بيانات توضيحية**. يمكنك رفع ملف Excel الخاص بك من الشريط الجانبي.")
        return generate_sample_data()

    try:
        df = pd.read_excel(
            source,
            sheet_name="ملخص مستخلصات المشاريع (2)",
            skiprows=3,
            usecols="B:F",
            names=['project_name', 'total_due', 'raised', 'payment_order_issued', 'target_raised'],
            nrows=12
        )
        
        df = df.dropna(subset=['project_name'])
        df = df.fillna(0)
        
        # إضافة الحالة
        df['status'] = df.apply(
            lambda row: 'مكتمل' if row['total_due'] > 0 and row['payment_order_issued'] >= row['total_due'] 
            else 'جاري' if row['raised'] > 0 
            else 'متوقف', 
            axis=1
        )
        
        # إضافة المنطقة بشكل مستقر
        regions = ['الوسطى', 'الجنوبية', 'الشرقية', 'الغربية', 'الشمالية']
        df['region'] = [regions[i % len(regions)] for i in range(len(df))]
        
        return df
    
    except Exception as e:
        st.warning(f"⚠️ تعذر قراءة الشيت المحدد في ملف Excel. تم تفعيل البيانات التوضيحية. (التفاصيل: {e})")
        return generate_sample_data()


# ============================================
# 3. حساب المؤشرات (KPIs)
# ============================================
def calculate_kpis(df):
    total_due = df['total_due'].sum()
    total_raised = df['raised'].sum()
    total_paid = df['payment_order_issued'].sum()
    total_target = df['target_raised'].sum()
    
    payment_ratio = (total_paid / total_due * 100) if total_due > 0 else 0
    achievement_ratio = (total_raised / total_due * 100) if total_due > 0 else 0
    remaining_to_raise = total_due - total_raised
    
    return {
        'total_due': total_due,
        'total_raised': total_raised,
        'total_paid': total_paid,
        'total_target': total_target,
        'payment_ratio': payment_ratio,
        'achievement_ratio': achievement_ratio,
        'remaining_to_raise': remaining_to_raise
    }


# ============================================
# 4. التطبيق الرئيسي
# ============================================
def main():
    # الشريط الجانبي
    st.sidebar.title("⚙️ لوحة التحكم والفلاتر")
    st.sidebar.markdown("---")
    
    # رفع الملف
    uploaded_file = st.sidebar.file_uploader("📂 رفع ملف Excel", type=["xlsx", "xls"])
    
    # تحميل البيانات
    df = load_data(uploaded_file)
    
    if df.empty:
        st.error("❌ لا توجد بيانات صالحة للعرض.")
        return
    
    # الفلاتر
    project_filter = st.sidebar.multiselect(
        "اختر المشروع",
        options=df['project_name'].unique(),
        default=df['project_name'].unique()
    )
    
    region_filter = st.sidebar.multiselect(
        "اختر المنطقة",
        options=df['region'].unique(),
        default=df['region'].unique()
    )
    
    status_filter = st.sidebar.multiselect(
        "اختر الحالة",
        options=df['status'].unique(),
        default=df['status'].unique()
    )
    
    # تصفية البيانات
    filtered_df = df[
        (df['project_name'].isin(project_filter)) &
        (df['region'].isin(region_filter)) &
        (df['status'].isin(status_filter))
    ]
    
    if filtered_df.empty:
        st.warning("⚠️ لا توجد بيانات تطابق الفلاتر المحددة.")
        return
    
    # حساب المؤشرات
    kpis = calculate_kpis(filtered_df)
    
    # العنوان وتاريخ التحديث
    col_title, col_date = st.columns([3, 1])
    with col_title:
        st.title("📊 لوحة مؤشرات أداء المشاريع المالية")
    with col_date:
        st.markdown(f"**🔄 آخر تحديث:**\n`{datetime.now().strftime('%Y-%m-%d %H:%M')}`")
    
    st.markdown("---")
    
    # بطاقات KPIs
    col1, col2, col3, col4, col5 = st.columns(5)
    
    col1.metric(label="💰 إجمالي المستحق", value=f"{kpis['total_due']:,.0f} ﷼")
    col2.metric(label="📤 إجمالي المرفوع", value=f"{kpis['total_raised']:,.0f} ﷼", delta=f"{kpis['achievement_ratio']:.1f}% نسبة الإنجاز")
    col3.metric(label="💳 إجمالي المدفوع", value=f"{kpis['total_paid']:,.0f} ﷼", delta=f"{kpis['payment_ratio']:.1f}% نسبة الصرف")
    col4.metric(label="🎯 المستهدف للرفع", value=f"{kpis['total_target']:,.0f} ﷼")
    col5.metric(label="📉 المتبقي للرفع", value=f"{kpis['remaining_to_raise']:,.0f} ﷼")
    
    st.markdown("---")
    
    # الرسوم البيانية الرئيسية
    col_chart1, col_chart2 = st.columns([2, 1])
    
    with col_chart1:
        st.subheader("📊 مقارنة المستخلصات حسب المشروع")
        
        chart_data = filtered_df.melt(
            id_vars=['project_name'],
            value_vars=['total_due', 'raised', 'payment_order_issued', 'target_raised'],
            var_name='type',
            value_name='amount'
        )
        
        type_names = {
            'total_due': 'المستحق',
            'raised': 'المرفوع',
            'payment_order_issued': 'المدفوع',
            'target_raised': 'المستهدف'
        }
        chart_data['type'] = chart_data['type'].map(type_names)
        
        fig_bar = px.bar(
            chart_data,
            x='project_name',
            y='amount',
            color='type',
            barmode='group',
            labels={'project_name': 'المشروع', 'amount': 'المبلغ (ريال)', 'type': 'نوع المستخلص'},
            color_discrete_map={
                'المستحق': '#6366f1',
                'المرفوع': '#3b82f6',
                'المدفوع': '#10b981',
                'المستهدف': '#f59e0b'
            }
        )
        
        fig_bar.update_layout(
            height=400,
            xaxis_tickangle=-30,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            font=dict(family="Cairo")
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col_chart2:
        st.subheader("🎯 توزيع المستحق حسب المشروع")
        
        fig_pie = px.pie(
            filtered_df,
            values='total_due',
            names='project_name',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        
        fig_pie.update_layout(
            height=400,
            font=dict(family="Cairo"),
            showlegend=True,
            legend=dict(orientation="h", y=-0.2)
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # مخططات فرعية
    col_chart3, col_chart4 = st.columns(2)
    
    with col_chart3:
        st.subheader("📈 اتجاه المدفوعات الشهرية (تقديري)")
        
        months = ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو', 'يوليو', 'أغسطس']
        monthly_paid = np.linspace(kpis['total_paid'] * 0.05, kpis['total_paid'] * 0.2, 8)
        
        fig_line = px.line(
            x=months,
            y=monthly_paid,
            markers=True,
            labels={'x': 'الشهر', 'y': 'المبلغ المدفوع (ريال)'}
        )
        fig_line.update_traces(line_color='#10b981', line_width=3)
        fig_line.update_layout(height=320, font=dict(family="Cairo"))
        st.plotly_chart(fig_line, use_container_width=True)
    
    with col_chart4:
        st.subheader("📊 توزيع المشاريع حسب الحالة")
        
        status_counts = filtered_df['status'].value_counts().reset_index()
        status_counts.columns = ['الحالة', 'العدد']
        
        fig_status = px.pie(
            status_counts,
            values='العدد',
            names='الحالة',
            hole=0.3,
            color='الحالة',
            color_discrete_map={'مكتمل': '#10b981', 'جاري': '#3b82f6', 'متوقف': '#ef4444'}
        )
        
        fig_status.update_layout(height=320, font=dict(family="Cairo"))
        st.plotly_chart(fig_status, use_container_width=True)
    
    # الجدول التفصيلي
    st.markdown("---")
    st.subheader("📋 الجدول التفصيلي للمشاريع")
    
    display_df = filtered_df[[
        'project_name', 'region', 'status', 'total_due', 'raised', 'payment_order_issued', 'target_raised'
    ]].copy()
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "project_name": st.column_config.Column("اسم المشروع", width="medium"),
            "region": st.column_config.Column("المنطقة"),
            "status": st.column_config.Column("الحالة"),
            "total_due": st.column_config.NumberColumn("المستحق", format="%.2f ﷼"),
            "raised": st.column_config.NumberColumn("المرفوع", format="%.2f ﷼"),
            "payment_order_issued": st.column_config.NumberColumn("المدفوع", format="%.2f ﷼"),
            "target_raised": st.column_config.NumberColumn("المستهدف", format="%.2f ﷼")
        }
    )
    
    # الملخص والتحميل
    st.markdown("---")
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    
    top_project_name = filtered_df.loc[filtered_df['total_due'].idxmax(), 'project_name'] if not filtered_df.empty else "-"
    avg_paid = (kpis['total_paid'] / len(filtered_df)) if len(filtered_df) > 0 else 0
    
    col_stat1.info(f"📌 **إجمالي عدد المشاريع:** {len(filtered_df)}")
    col_stat2.info(f"💡 **متوسط المدفوع لكل مشروع:** {avg_paid:,.2f} ﷼")
    col_stat3.info(f"🏆 **أعلى مشروع استحقاقاً:** {top_project_name}")
    
    # زر تحميل CSV
    st.sidebar.markdown("---")
    st.sidebar.download_button(
        label="📥 تحميل البيانات المفلتة (CSV)",
        data=filtered_df.to_csv(index=False).encode('utf-8-sig'),
        file_name=f"projects_report_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

if __name__ == "__main__":
    main()