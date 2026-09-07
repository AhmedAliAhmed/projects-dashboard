import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import hashlib
from datetime import datetime
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, AdaBoostRegressor, BaggingRegressor, ExtraTreesRegressor
from sklearn.tree import DecisionTreeRegressor
import warnings
warnings.filterwarnings('ignore')

# -----------------------------
# 0. إعدادات الصفحة والتنسيق المظلم
# -----------------------------
st.set_page_config(
    page_title="الموقف المالي لمستخلصات المشاريع 2026م",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# تطبيق CSS مخصص للتنسيق المظلم باللغة العربية
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
        text-align: right;
    }
    .stApp {
        background-color: #0b1220;
        color: white;
    }
    div[data-testid="metric-container"] {
        background: linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 15px;
    }
    .main-header {
        font-size: 26px;
        font-weight: 800;
        color: white;
        margin-bottom: 5px;
    }
    .sub-header {
        color: rgba(255,255,255,0.7);
        font-size: 14px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 1. نظام الحماية بكلمة مرور
# -----------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

PASSWORD_HASH = hashlib.sha256("123456".encode()).hexdigest()

def check_password(password):
    return hashlib.sha256(password.encode()).hexdigest() == PASSWORD_HASH

if not st.session_state.authenticated:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="background: rgba(255,255,255,0.04); padding: 40px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.08); text-align: center;">
            <h2 style="color: white; margin-bottom: 10px;">🔐 منصة مستخلصات المشاريع 2026م</h2>
            <p style="color: rgba(255,255,255,0.7); margin-bottom: 20px;">يرجى إدخال كلمة المرور للوصول إلى لوحة التحكم</p>
        </div>
        """, unsafe_allow_html=True)
        
        password_input = st.text_input("كلمة المرور", type="password", key="pass_field")
        if st.button("تسجيل الدخول", use_container_width=True, type="primary"):
            if check_password(password_input):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ كلمة المرور غير صحيحة")
        st.caption("🔑 كلمة المرور الافتراضية: 123456")
    st.stop()

# -----------------------------
# 2. البيانات الأولية لمستخلصات المشاريع 2026م
# -----------------------------
initial_data = [
    ["PRJ-001", "تقديم الخدمات الاستشارية لدراسة تطوير خطط تشغيل و صيانة المرافق الهامة", "وزارة البيئة و المياه و الزراعة", "قيد التنفيذ", 628950.00, 0.00, 0.00, 628950.00],
    ["PRJ-002", "الاشراف علي تصميم و انشاء المختبر البيطري المركزي", "وزارة البيئة و المياه و الزراعة", "قيد التنفيذ", 832900.15, 0.00, 394531.65, 394531.65],
    ["PRJ-003", "تقديم الخدمات الاستشارية للاشراف علي المشاريع الهندسية ببنك التنمية", "بنك التنمية", "مكتمل", 241500.00, 241500.00, 0.00, 0.00],
    ["PRJ-004", "الاتفاقية الاطارية لخدمات الاشراف علي مشاريع إدارة المرافق بالمنطقة الوسطي", "شركة تطوير المباني (TBC)", "قيد التنفيذ", 19666576.68, 0.00, 5857186.10, 13809390.58],
    ["PRJ-005", "الاشراف علي إدارة المرافق بالمنطقة الجنوبية", "شركة تطوير المباني (TBC)", "قيد التنفيذ", 4222488.43, 0.00, 3222488.43, 1000000.00],
    ["PRJ-006", "الخدمات الاستشارية للاستفادة من المياه الجوفية و السطحية و مشاريع درء اخطار السيول", "وزارة البيئة و المياه و الزراعة", "قيد التنفيذ", 3261425.00, 1187950.00, 1040750.00, 1032725.00],
    ["PRJ-007", "الاتفاقية الاطارية لتصميم مشاريع المؤسسة العامة للري امر عمل (02)", "المؤسسة العامة للري", "قيد التنفيذ", 5398330.00, 4508000.00, 0.00, 890330.00],
    ["PRJ-008", "ترميز مباني التراث المعماري وسط الرياض", "وزارة الثقافة", "قيد التنفيذ", 3910460.00, 0.00, 0.00, 3910460.00],
    ["PRJ-009", "دراسة و تصميم مشروع انشاء قاعة الطعام بالمقر الرئيسي", "المؤسسة العامة للري", "مكتمل", 439875.00, 439875.00, 0.00, 0.00],
    ["PRJ-010", "مبالغ تم دفعها للهندسية ولم يتم تحصيلها", "القطاع الهندسي والمالي", "معلق", 2864500.00, 0.00, 0.00, 2864500.00],
    ["PRJ-011", "الاشراف علي المشاريع الصغيرة بجميع مناطق المملكة (المرحلة الثانية)", "وزارة البيئة و المياه و الزراعة", "قيد التنفيذ", 2996034.00, 0.00, 0.00, 2996034.00],
    ["PRJ-012", "الاتفاقية الاطارية لخدمات الاشراف علي مشاريع إدارة المرافق بالمنطقة الوسطي", "شركة تطوير المباني (TBC)", "قيد التنفيذ", 3800000.00, 0.00, 0.00, 3800000.00],
]

cols = [
    "Project ID", "Project Name", "Client / Sector", "Status",
    "Total Due Amount", "Submitted Claims", "Payment Orders Issued", "Targeted Claims"
]

if "df_projects" not in st.session_state:
    st.session_state.df_projects = pd.DataFrame(initial_data, columns=cols)

# -----------------------------
# 3. الهيدر والتحكم
# -----------------------------
top_col1, top_col2 = st.columns([3, 1])
with top_col1:
    st.markdown('<div class="main-header">📊 الموقف المالي لمستخلصات المشاريع 2026م</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">متابعة المستخلصات المستحقة، المرفوعة، أوامر الدفع، والمستهدف رفعها (تحديث أغسطس 2026م)</div>', unsafe_allow_html=True)

with top_col2:
    if st.button("🚪 تسجيل الخروج", type="secondary"):
        st.session_state.authenticated = False
        st.rerun()

# -----------------------------
# 4. التبويبات الرئيسيّة
# -----------------------------
tab1, tab2 = st.tabs(["📊 مستخلصات المشاريع", "🤖 تحليل النماذج (ML)"])

with tab1:
    # -----------------------------
    # الفلاتر والبحث
    # -----------------------------
    df = st.session_state.df_projects.copy()
    
    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        statuses = ["الكل"] + list(df["Status"].unique())
        sel_status = st.selectbox("حالة المشروع", statuses)
    with f_col2:
        clients = ["الكل"] + list(df["Client / Sector"].unique())
        sel_client = st.selectbox("القطاع / العميل", clients)
    with f_col3:
        search_query = st.text_input("بحث باسم المشروع", "")

    # تطبيق التصفية
    filtered_df = df.copy()
    if sel_status != "الكل":
        filtered_df = filtered_df[filtered_df["Status"] == sel_status]
    if sel_client != "الكل":
        filtered_df = filtered_df[filtered_df["Client / Sector"] == sel_client]
    if search_query:
        filtered_df = filtered_df[filtered_df["Project Name"].str.contains(search_query, case=False, na=False)]

    # حساب الإجماليات
    total_due = filtered_df["Total Due Amount"].sum()
    total_submitted = filtered_df["Submitted Claims"].sum()
    total_orders = filtered_df["Payment Orders Issued"].sum()
    total_targeted = filtered_df["Targeted Claims"].sum()

    # -----------------------------
    # بطاقات الإحصائيات (KPI Cards)
    # -----------------------------
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("إجمالي المستخلصات المستحقة", f"{total_due:,.2f} ر.س", "حتى نهاية أغسطس")
    k2.metric("المستخلصات المرفوعة", f"{total_submitted:,.2f} ر.س", f"{(total_submitted/total_due*100 if total_due else 0):.1f}%")
    k3.metric("صدر لها أمر دفع", f"{total_orders:,.2f} ر.س", f"{(total_orders/total_due*100 if total_due else 0):.1f}%")
    k4.metric("مستهدف رفعها", f"{total_targeted:,.2f} ر.س", f"{(total_targeted/total_due*100 if total_due else 0):.1f}%")

    st.markdown("---")

    # -----------------------------
    # الرسم البياني الخطي والعمودي
    # -----------------------------
    g_col1, g_col2 = st.columns([2, 1])
    
    with g_col1:
        st.subheader("📈 مسار حركة المستخلصات لكل مشروع")
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(x=filtered_df["Project Name"], y=filtered_df["Total Due Amount"], name="المستحقة", mode="lines+markers", line=dict(color="#3b82f6", width=3)))
        fig_line.add_trace(go.Scatter(x=filtered_df["Project Name"], y=filtered_df["Targeted Claims"], name="مستهدف رفعها", mode="lines+markers", line=dict(color="#f59e0b", width=3, dash="dot")))
        fig_line.add_trace(go.Scatter(x=filtered_df["Project Name"], y=filtered_df["Payment Orders Issued"], name="صدر أمر دفع", mode="lines+markers", line=dict(color="#22c55e", width=3, dash="dash")))
        fig_line.add_trace(go.Scatter(x=filtered_df["Project Name"], y=filtered_df["Submitted Claims"], name="مرفوعة", mode="lines+markers", line=dict(color="#a855f7", width=2)))
        
        fig_line.update_layout(
            paper_bgcolor="#0f1830", plot_bgcolor="#0f1830", font=dict(color="white"),
            height=380, margin=dict(l=20, r=20, t=30, b=80),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_line, use_container_width=True)

    with g_col2:
        st.subheader("🎯 مؤشرات الإنجاز")
        pct_orders = (total_orders / total_due * 100) if total_due else 0
        
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=round(pct_orders, 1),
            number={"suffix": "%", "font": {"size": 24, "color": "white"}},
            gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#22c55e"}},
            title={"text": "نسبة أوامر الدفع الصادرة", "font": {"color": "white", "size": 14}}
        ))
        fig_gauge.update_layout(paper_bgcolor="#0f1830", height=380, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)

    # -----------------------------
    # الجدول التفاعلي القابل للتعديل المباشر
    # -----------------------------
    st.subheader("✏️ جدول المستخلصات (يمكنك التعديل المباشر على الأرقام في الخلايا أدناه)")
    
    # تحضير الجدول للعرض والتعديل
    edited_df = st.data_editor(
        filtered_df,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Total Due Amount": st.column_config.NumberColumn("المستحقة حتى النهاية", format="%.2f ر.س"),
            "Submitted Claims": st.column_config.NumberColumn("المستخلصات المرفوعة", format="%.2f ر.س"),
            "Payment Orders Issued": st.column_config.NumberColumn("صدر لها أمر دفع", format="%.2f ر.س"),
            "Targeted Claims": st.column_config.NumberColumn("مستهدف رفعها", format="%.2f ر.س"),
        },
        key="data_editor"
    )

    # زر تحديث البيانات
    if st.button("💾 حفظ التعديلات وإعادة الحساب"):
        st.session_state.df_projects = edited_df
        st.success("✅ تم حفظ التعديلات وإعادة حساب الإجماليات بنجاح!")
        st.rerun()

    # تصدير ملف CSV
    csv_data = edited_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 تصدير البيانات إلى CSV",
        data=csv_data,
        file_name="project_claims_2026.csv",
        mime="text/csv"
    )

with tab2:
    st.subheader("🤖 تحليل وتقييم أداء نماذج التعلم الآلي (ML)")
    
    # توليد بيانات وتقييم النماذج
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
        fig_ml = px.bar(res_df, x='النموذج', y='R² Score', text='R² Score', title="مقارنة أداء النماذج (R² Score)", color_discrete_sequence=['#0ea5e9'])
        fig_ml.update_layout(paper_bgcolor="#0f1830", plot_bgcolor="#0f1830", font=dict(color="white"), height=350)
        st.plotly_chart(fig_ml, use_container_width=True)

    with ml_col2:
        fig_dist = px.histogram(ml_data, x='price', nbins=30, title="توزيع الأسعار في بيانات التدريب", color_discrete_sequence=['#22c55e'])
        fig_dist.update_layout(paper_bgcolor="#0f1830", plot_bgcolor="#0f1830", font=dict(color="white"), height=350)
        st.plotly_chart(fig_dist, use_container_width=True)

    st.dataframe(res_df, use_container_width=True)