import warnings
from datetime import datetime
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

warnings.filterwarnings("ignore")

# ============================================
# إعدادات الصفحة
# ============================================
st.set_page_config(
    page_title="📊 داشبورد إدارة المشاريع",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================
# تحميل ومعالجة البيانات
# ============================================
@st.cache_data
def load_all_data():
  """تحميل جميع البيانات من ملف الإكسل"""
  try:
    df_projects = pd.read_excel(
        "جميع المشاريع.xlsx", sheet_name="مدراء المشاريع", header=1
    )
    df_summary = pd.read_excel(
        "جميع المشاريع.xlsx", sheet_name="ملخص مستخلصات المشاريع", header=2
    )
    df_report = pd.read_excel(
        "جميع المشاريع.xlsx", sheet_name="تقرير عام المشاريع", header=2
    )

    df_projects = df_projects.dropna(how="all")
    df_projects.columns = [
        "م",
        "المشروع",
        "مدير_المشروع",
        "الحالة",
        "رقم_التواصل",
        "الإيميل",
    ]
    df_projects = df_projects[df_projects["م"].notna()]
    df_projects["م"] = df_projects["م"].astype(int)

    df_report = df_report.dropna(how="all")
    if len(df_report.columns) >= 14:
      df_report = df_report.iloc[:, :14]
      df_report.columns = [
          "",
          "م",
          "المشروع",
          "الجهة",
          "الموقع",
          "المدة",
          "تاريخ_الاستلام",
          "تاريخ_الانتهاء",
          "المنقضية",
          "المتبقية",
          "القيمة_الاجمالية",
          "ما_تم_رفعه",
          "ما_تم_صرفه",
          "المتبقي",
      ]

    df_report = df_report[df_report["م"].notna()]
    df_report["م"] = df_report["م"].astype(int)

    for col in ["القيمة_الاجمالية", "ما_تم_رفعه", "ما_تم_صرفه", "المتبقي"]:
      if col in df_report.columns:
        df_report[col] = pd.to_numeric(df_report[col], errors="coerce")

    try:
      df_south = pd.read_excel(
          "جميع المشاريع.xlsx", sheet_name="الجنوبية TBC", header=2
      )
      df_south = df_south.dropna(how="all")
      if len(df_south.columns) >= 8:
        df_south = df_south.iloc[:, :8]
        df_south.columns = [
            "رقم_المستخلص",
            "قيمة_المستخلص",
            "تاريخ_الرفع",
            "تاريخ_الاعتماد",
            "تاريخ_السداد",
            "قيمة_المسدد",
            "حالة_السداد",
            "ملاحظات",
        ]
        df_south = df_south[df_south["رقم_المستخلص"].notna()]
        df_south["قيمة_المستخلص"] = pd.to_numeric(
            df_south["قيمة_المستخلص"], errors="coerce"
        )
        df_south["المشروع"] = "الجنوبية"
    except:
      df_south = pd.DataFrame()

    return df_projects, df_summary, df_report, df_south

  except FileNotFoundError:
    st.error(
        "⚠️ ملف 'جميع المشاريع.xlsx' غير موجود في المستودع. يرجى رفعه بجانب"
        " ملف الكود."
    )
    return None, None, None, None


df_projects, df_summary, df_report, df_south = load_all_data()

if df_projects is None:
  st.stop()


# ============================================
# حساب المؤشرات الرئيسية (KPIs)
# ============================================
def calculate_kpis():
  if df_report.empty:
    return {}

  total_contracts = df_report["القيمة_الاجمالية"].sum()
  total_raised = df_report["ما_تم_رفعه"].sum()
  total_paid = df_report["ما_تم_صرفه"].sum()
  total_remaining = df_report["المتبقي"].sum()

  active_projects = (
      len(df_projects[df_projects["الحالة"] == "جاري"])
      if not df_projects.empty
      else 0
  )
  completed_projects = (
      len(df_projects[df_projects["الحالة"] == "منتهي"])
      if not df_projects.empty
      else 0
  )
  not_started = (
      len(df_projects[df_projects["الحالة"] == "لم يبدأ"])
      if not df_projects.empty
      else 0
  )

  return {
      "total_contracts": total_contracts,
      "total_raised": total_raised,
      "total_paid": total_paid,
      "total_remaining": total_remaining,
      "active_projects": active_projects,
      "completed_projects": completed_projects,
      "not_started": not_started,
      "total_projects": len(df_projects),
  }


kpis = calculate_kpis()

# ===== العنوان الرئيسي =====
st.markdown(
    """
    <div style='background: linear-gradient(135deg, #1a237e 0%, #0d47a1 100%); padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
        <h1 style='text-align: center; color: white; margin: 0;'>
            📊 داشبورد إدارة المشاريع
        </h1>
        <p style='text-align: center; color: #e3f2fd; margin: 5px 0 0 0; font-size: 16px;'>
            ADV CON CENTER - آخر تحديث: {}
        </p>
    </div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M")),
    unsafe_allow_html=True,
)

# ===== الشريط الجانبي =====
with st.sidebar:
  st.markdown("### 🔍 تصفية البيانات")
  status_filter = st.multiselect(
      "حالة المشروع",
      options=(
          ["الكل"] + list(df_projects["الحالة"].unique())
          if not df_projects.empty
          else ["الكل"]
      ),
      default=["الكل"],
  )

  managers = (
      ["الكل"] + list(df_projects["مدير_المشروع"].unique())
      if not df_projects.empty
      else ["الكل"]
  )
  manager_filter = st.selectbox("مدير المشروع", options=managers)

  owners = (
      ["الكل"] + list(df_report["الجهة"].unique())
      if not df_report.empty
      else ["الكل"]
  )
  owner_filter = st.selectbox("الجهة المالكة", options=owners)

  st.divider()
  st.markdown("### 📈 إحصائيات سريعة")
  col1, col2 = st.columns(2)
  with col1:
    st.metric("عدد المشاريع", kpis.get("total_projects", 0))
  with col2:
    st.metric("نشطة", kpis.get("active_projects", 0))

  st.divider()
  st.caption("© 2026 ADV CON CENTER")

# ===== بطاقات المؤشرات (KPIs) =====
st.markdown("### 🎯 مؤشرات الأداء الرئيسية")
kpi_cols = st.columns(6)

kpi_data = [
    ("💰 إجمالي العقود", kpis.get("total_contracts", 0), "ريال"),
    ("📤 المرفوع", kpis.get("total_raised", 0), "ريال"),
    ("✅ المصرُوف", kpis.get("total_paid", 0), "ريال"),
    ("📌 المتبقي", kpis.get("total_remaining", 0), "ريال"),
    ("🔄 نشطة", kpis.get("active_projects", 0), "مشروع"),
    ("✓ منتهية", kpis.get("completed_projects", 0), "مشروع"),
]

for idx, (label, value, unit) in enumerate(kpi_data):
  with kpi_cols[idx]:
    st.metric(
        label=label,
        value=f"{value:,.0f}",
        delta=f"{unit}" if value > 0 else None,
    )

st.divider()

# ===== تطبيق الفلاتر =====
filtered_projects = df_projects.copy()
filtered_report = df_report.copy()

if not filtered_projects.empty:
  if "الكل" not in status_filter:
    filtered_projects = filtered_projects[
        filtered_projects["الحالة"].isin(status_filter)
    ]
  if manager_filter != "الكل":
    filtered_projects = filtered_projects[
        filtered_projects["مدير_المشروع"] == manager_filter
    ]
  if not filtered_report.empty:
    if owner_filter != "الكل":
      filtered_report = filtered_report[
          filtered_report["الجهة"] == owner_filter
      ]

# ===== الصف الأول: مخططات ماليّة =====
st.markdown("### 📊 التحليل المالي للمشاريع")
col1, col2 = st.columns([2, 1])

with col1:
  if not filtered_report.empty:
    plot_df = filtered_report[filtered_report["المشروع"].notna()].copy().head(20)
    fig1 = go.Figure()
    fig1.add_trace(
        go.Bar(
            x=plot_df["المشروع"],
            y=plot_df["القيمة_الاجمالية"],
            name="القيمة الإجمالية",
            marker_color="#1a237e",
            text=plot_df["القيمة_الاجمالية"].apply(lambda x: f"{x:,.0f}"),
            textposition="outside",
        )
    )
    fig1.add_trace(
        go.Bar(
            x=plot_df["المشروع"],
            y=plot_df["ما_تم_صرفه"],
            name="المصرُوف",
            marker_color="#2e7d32",
            text=plot_df["ما_تم_صرفه"].apply(lambda x: f"{x:,.0f}"),
            textposition="outside",
        )
    )
    fig1.add_trace(
        go.Bar(
            x=plot_df["المشروع"],
            y=plot_df["المتبقي"],
            name="المتبقي",
            marker_color="#e65100",
            text=plot_df["المتبقي"].apply(lambda x: f"{x:,.0f}"),
            textposition="outside",
        )
    )
    fig1.update_layout(
        barmode="group",
        xaxis_tickangle=-30,
        height=450,
        showlegend=True,
        font=dict(size=11),
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
  if not filtered_projects.empty:
    status_counts = filtered_projects["الحالة"].value_counts()
    colors = {"جاري": "#4CAF50", "منتهي": "#2196F3", "لم يبدأ": "#FF9800"}
    fig2 = px.pie(
        values=status_counts.values,
        names=status_counts.index,
        color=status_counts.index,
        color_discrete_map=colors,
        hole=0.4,
    )
    fig2.update_layout(height=400, showlegend=True, font=dict(size=12))
    fig2.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ===== الجدول التفصيلي =====
st.markdown("### 📋 قائمة المشاريع التفصيلية")
if not filtered_projects.empty and not filtered_report.empty:
  merged_df = filtered_projects.merge(
      filtered_report[
          ["م", "القيمة_الاجمالية", "ما_تم_صرفه", "المتبقي", "الجهة"]
      ],
      on="م",
      how="left",
  )
else:
  merged_df = filtered_projects

search = st.text_input(
    "🔍 بحث سريع عن مشروع", placeholder="اكتب اسم المشروع..."
)
if search and not merged_df.empty:
  merged_df = merged_df[
      merged_df["المشروع"].str.contains(search, case=False, na=False)
  ]

if not merged_df.empty:
  cols_to_show = [
      "م",
      "المشروع",
      "مدير_المشروع",
      "الحالة",
      "القيمة_الاجمالية",
      "ما_تم_صرفه",
      "المتبقي",
  ]
  if "الجهة" in merged_df.columns:
    cols_to_show.insert(3, "الجهة")

  display_df = merged_df[cols_to_show].copy()
  for col in ["القيمة_الاجمالية", "ما_تم_صرفه", "المتبقي"]:
    if col in display_df.columns:
      display_df[col] = display_df[col].apply(
          lambda x: f"{x:,.0f}" if pd.notna(x) else "0"
      )

  st.dataframe(display_df, use_container_width=True, hide_index=True)

# ===== تذييل الصفحة =====
st.divider()
st.markdown(
    """
    <div style='text-align: center; padding: 20px; background-color: #f5f5f5; border-radius: 10px;'>
        <p style='color: #666; margin: 0; font-size: 14px;'>
            © 2026 ADV CON CENTER - تم تطوير هذا الداشبورد باستخدام Streamlit
        </p>
    </div>
""",
    unsafe_allow_html=True,
)