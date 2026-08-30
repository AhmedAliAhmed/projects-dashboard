import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# ============================================
# 1. إعداد الصفحة
# ============================================
st.set_page_config(
    page_title="لوحة مؤشرات المشاريع",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# 2. تحميل البيانات
# ============================================
@st.cache_data
def load_data():
    file_path = "data/Projects Financial Dashboard Template.xlsx"
    
    try:
        # قراءة البيانات من الشيت المحدد
        df = pd.read_excel(
            file_path,
            sheet_name="ملخص مستخلصات المشاريع (2)",
            skiprows=3,  # تخطي العناوين العلوية
            usecols="B:F",  # الأعمدة المطلوبة
            names=[
                'project_name',
                'total_due',
                'raised',
                'payment_order_issued',
                'target_raised'
            ],
            nrows=12  # عدد المشاريع
        )
        
        # تنظيف البيانات
        df = df.dropna(subset=['project_name'])
        df = df.replace(0, np.nan)  # تحويل الأصفار إلى NaN للرسوم البيانية
        
        # إضافة عمود الحالة المقترح
        df['status'] = df.apply(
            lambda row: 'مكتمل' if row['total_due'] == row['payment_order_issued'] 
            else 'جاري' if row['raised'] > 0 
            else 'متوقف', 
            axis=1
        )
        
        # إضافة عمود المنطقة (مثال - يمكن تعديله حسب البيانات الفعلية)
        regions = ['الوسطى', 'الجنوبية', 'الشرقية', 'الغربية', 'الشمالية']
        df['region'] = np.random.choice(regions, len(df))
        
        return df
    
    except Exception as e:
        st.error(f"خطأ في تحميل الملف: {e}")
        return pd.DataFrame()

# ============================================
# 3. حساب المؤشرات
# ============================================
def calculate_kpis(df):
    total_due = df['total_due'].sum()
    total_raised = df['raised'].sum()
    total_paid = df['payment_order_issued'].sum()
    total_target = df['target_raised'].sum()
    
    # نسبة المدفوع من المستحق
    payment_ratio = (total_paid / total_due * 100) if total_due > 0 else 0
    
    # نسبة الإنجاز المالي
    achievement_ratio = (total_raised / total_due * 100) if total_due > 0 else 0
    
    # المتبقي للرفع
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
    # تحميل البيانات
    df = load_data()
    
    if df.empty:
        st.warning("⚠️ لا توجد بيانات لعرضها. يرجى التأكد من وجود ملف Excel في المسار المحدد.")
        return
    
    # ============================================
    # 4.1 الشريط الجانبي (Slicers)
    # ============================================
    st.sidebar.title("🔍 فلتر البيانات")
    st.sidebar.markdown("---")
    
    # فلتر المشروع
    project_filter = st.sidebar.multiselect(
        "اختر المشروع",
        options=df['project_name'].unique(),
        default=df['project_name'].unique()
    )
    
    # فلتر المنطقة
    region_filter = st.sidebar.multiselect(
        "اختر المنطقة",
        options=df['region'].unique(),
        default=df['region'].unique()
    )
    
    # فلتر الحالة
    status_filter = st.sidebar.multiselect(
        "اختر الحالة",
        options=df['status'].unique(),
        default=df['status'].unique()
    )
    
    # تطبيق الفلاتر
    filtered_df = df[
        (df['project_name'].isin(project_filter)) &
        (df['region'].isin(region_filter)) &
        (df['status'].isin(status_filter))
    ]
    
    if filtered_df.empty:
        st.warning("⚠️ لا توجد بيانات تطابق الفلاتر المحددة.")
        return
    
    # ============================================
    # 4.2 حساب المؤشرات
    # ============================================
    kpis = calculate_kpis(filtered_df)
    
    # ============================================
    # 4.3 العنوان وتاريخ التحديث
    # ============================================
    col_title, col_date = st.columns([3, 1])
    with col_title:
        st.title("📊 لوحة مؤشرات أداء المشاريع")
    with col_date:
        st.markdown(f"**🔄 آخر تحديث:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    st.markdown("---")
    
    # ============================================
    # 4.4 بطاقات KPIs
    # ============================================
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="💰 إجمالي المستحق",
            value=f"{kpis['total_due']:,.2f}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="📤 إجمالي المرفوع",
            value=f"{kpis['total_raised']:,.2f}",
            delta=f"{kpis['achievement_ratio']:.1f}%"
        )
    
    with col3:
        st.metric(
            label="💳 إجمالي المدفوع",
            value=f"{kpis['total_paid']:,.2f}",
            delta=f"{kpis['payment_ratio']:.1f}%"
        )
    
    with col4:
        st.metric(
            label="🎯 المستهدف للرفع",
            value=f"{kpis['total_target']:,.2f}",
            delta=None
        )
    
    with col5:
        st.metric(
            label="📉 المتبقي للرفع",
            value=f"{kpis['remaining_to_raise']:,.2f}",
            delta=None
        )
    
    st.markdown("---")
    
    # ============================================
    # 4.5 الرسوم البيانية
    # ============================================
    col_chart1, col_chart2 = st.columns([2, 1])
    
    # 4.5.1 مخطط عمودي للمقارنة
    with col_chart1:
        st.subheader("📊 مقارنة المستخلصات حسب المشروع")
        
        # تحضير البيانات للرسم
        chart_data = filtered_df.melt(
            id_vars=['project_name'],
            value_vars=['total_due', 'raised', 'payment_order_issued', 'target_raised'],
            var_name='type',
            value_name='amount'
        )
        
        # استبدال الأسماء العربية
        type_names = {
            'total_due': 'المستحق',
            'raised': 'المرفوع',
            'payment_order_issued': 'المدفوع',
            'target_raised': 'المستهدف'
        }
        chart_data['type'] = chart_data['type'].map(type_names)
        
        # رسم المخطط العمودي
        fig_bar = px.bar(
            chart_data,
            x='project_name',
            y='amount',
            color='type',
            barmode='group',
            title="مقارنة المستخلصات حسب المشروع",
            labels={'project_name': 'المشروع', 'amount': 'المبلغ', 'type': 'نوع المستخلص'},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        
        fig_bar.update_layout(
            height=400,
            xaxis_tickangle=-45,
            legend_title_text='',
            showlegend=True
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # 4.5.2 مخطط دائري
    with col_chart2:
        st.subheader("🎯 توزيع المستحق حسب المشروع")
        
        fig_pie = px.pie(
            filtered_df,
            values='total_due',
            names='project_name',
            title="نسبة كل مشروع من إجمالي المستحق",
            hole=0.3,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        
        fig_pie.update_layout(
            height=400,
            showlegend=True,
            legend_title_text=''
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # ============================================
    # 4.6 مخططات إضافية
    # ============================================
    col_chart3, col_chart4 = st.columns(2)
    
    # 4.6.1 مخطط خطي - اتجاه المدفوعات (محاكاة)
    with col_chart3:
        st.subheader("📈 اتجاه المدفوعات (محاكاة)")
        
        # محاكاة بيانات شهرية
        months = ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو', 'يوليو', 'أغسطس']
        monthly_paid = np.random.uniform(100000, 500000, 8)
        
        fig_line = px.line(
            x=months,
            y=monthly_paid,
            title="اتجاه المدفوعات الشهرية (محاكاة)",
            labels={'x': 'الشهر', 'y': 'المبلغ المدفوع'}
        )
        
        fig_line.update_layout(height=300)
        st.plotly_chart(fig_line, use_container_width=True)
    
    # 4.6.2 مخطط دائري للحالات
    with col_chart4:
        st.subheader("📊 توزيع المشاريع حسب الحالة")
        
        status_counts = filtered_df['status'].value_counts()
        
        fig_status = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="حالة المشاريع",
            hole=0.3,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig_status.update_layout(height=300)
        st.plotly_chart(fig_status, use_container_width=True)
    
    # ============================================
    # 4.7 الجدول التفصيلي
    # ============================================
    st.markdown("---")
    st.subheader("📋 الجدول التفصيلي للمشاريع")
    
    # تنسيق الأرقام
    display_df = filtered_df.copy()
    display_df['total_due'] = display_df['total_due'].apply(lambda x: f"{x:,.2f}")
    display_df['raised'] = display_df['raised'].apply(lambda x: f"{x:,.2f}")
    display_df['payment_order_issued'] = display_df['payment_order_issued'].apply(lambda x: f"{x:,.2f}")
    display_df['target_raised'] = display_df['target_raised'].apply(lambda x: f"{x:,.2f}")
    
    # إعادة تسمية الأعمدة
    display_df.columns = [
        'اسم المشروع',
        'المستحق',
        'المرفوع',
        'المدفوع',
        'المستهدف',
        'الحالة',
        'المنطقة'
    ]
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )
    
    # ============================================
    # 4.8 إحصائيات إضافية
    # ============================================
    st.markdown("---")
    st.subheader("📊 ملخص إضافي")
    
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    
    with col_stat1:
        st.info(f"**عدد المشاريع:** {len(filtered_df)}")
    
    with col_stat2:
        st.info(f"**متوسط المدفوع لكل مشروع:** {kpis['total_paid']/len(filtered_df):,.2f}")
    
    with col_stat3:
        st.info(f"**أعلى مشروع مستحق:** {filtered_df['project_name'][filtered_df['total_due'].idxmax()]}")
    
    # ============================================
    # 4.9 تحميل البيانات
    # ============================================
    st.sidebar.markdown("---")
    st.sidebar.download_button(
        label="📥 تحميل البيانات المُفلترة",
        data=filtered_df.to_csv(index=False).encode('utf-8'),
        file_name=f"filtered_data_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

# ============================================
# 5. تشغيل التطبيق
# ============================================
if __name__ == "__main__":
    main()