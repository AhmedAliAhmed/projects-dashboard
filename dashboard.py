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
# تحميل ومعالجة البيانات بشكل ذكي
# ============================================
@st.cache_data
def load_all_data():
  """تحميل جميع البيانات من ملف الإكسل بشكل مرن يتعرف على أسماء الشيتات تلقائياً"""
  try:
    file_path = "جميع المشاريع.xlsx"
    xls = pd.ExcelFile(file_path)
    sheet_names = xls.sheet_names

    # 1. البحث عن شيت مدراء المشاريع
    project_sheet = next(
        (s for s in sheet_names if "مدراء" in s or "المشاريع" in s),
        sheet_names[0],
    )
    df_projects = pd.read_excel(xls, sheet_name=project_sheet, header=1)
    df_projects = df_projects.dropna(how="all")
    if len(df_projects.columns) >= 6:
      df_projects = df_projects.iloc[:, :6]
      df_projects.columns = [
          "م",
          "المشروع",
          "مدير_المشروع",
          "الحالة",
          "رقم_التواصل",
          "الإيميل",
      ]
    df_projects = df_projects[df_projects["م"].notna()]
    df_projects["م"] = pd.to_numeric(df_projects["م"], errors="coerce")

    # 2. البحث عن شيت التقرير العام
    report_sheet = next(
        (
            s
            for s in sheet_names
            if "تقرير" in s or "عام" in s or "التقرير" in s
        ),
        None,
    )
    if report_sheet:
      df_report = pd.read_excel(xls, sheet_name=report_sheet, header=2)
    elif len(sheet_names) > 1:
      df_report = pd.read_excel(xls, sheet_name=sheet_names[1], header=2)
    else:
      df_report = pd.DataFrame()

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
    df_report["م"] = pd.to_numeric(df_report["م"], errors="coerce")

    for col in ["القيمة_الاجمالية", "ما_تم_رفعه", "ما_تم_صرفه", "المتبقي"]:
      if col in df_report.columns:
        df_report[col] = pd.to_numeric(df_report[col], errors="coerce")

    # 3. البحث عن شيت المستخلصات
    summary_sheet = next(
        (s for s in sheet_names if "مستخلصات" in s or "ملخص" in s), None
    )
    df_summary = (
        pd.read_excel(xls, sheet_name=summary_sheet, header=2)
        if summary_sheet
        else pd.DataFrame()
    )

    south_sheet = next((s for s in sheet_names if "الجنوبية" in s), None)
    if south_sheet:
      df_south = pd.read_excel(xls, sheet_name=south_sheet, header=2)
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
    else:
      df_south = pd.DataFrame()

    return df_projects, df_summary, df_report, df_south

  except Exception as e:
    st.error(
        f"⚠️ يتعذر إيجاد ملف الإكسل 'جميع المشاريع.xlsx' في المستودع. تأكد من"
        f" رفعه بنفس الاسم. التفاصيل: {e}"
    )
    return None, None, None, None


df_projects, df_summary, df_report, df_south = load_all_data()

if df_projects is None or df_projects.empty:
  st.stop()


# ============================================
# حساب المؤشرات الرئيسية (KPIs)
# ============================================
def calculate_kpis():
  if df_report is None or df_report.empty:
    return {}

  total_contracts = (
      df_report["القيمة_الاجمالية"].sum()
      if "القيمة_الاجمالية" in df_report.columns
      else 0
  )
  total_raised = (
      df_report["ما_تم_رفعه"].sum() if "ما_تم_رفعه" in df_report.columns else 0
  )
  total_paid = (
      df_report["ما_تم_صرفه"].sum() if "ما_تم_صرفه" in df_report.columns else 0
  )
  total_remaining = (
      df_report["المتبقي"].sum() if "المتبقي" in df_report.columns else 0
  )

  active_projects = (
      len(df_projects[df_projects["الحالة"] == "جاري"])
      if "الحالة" in df_projects.columns
      else 0
  )
  completed_projects = (
      len(df_projects[df_projects["الحالة"] == "منتهي"])
      if "الحالة" in df_projects.columns
      else 0
  )

  return {
      "total_contracts": total_contracts,
      "total_raised": total_raised,
      "total_paid": total_paid,
      "total_remaining": total_remaining,
      "active_projects": active_projects,
      "completed_projects": completed_projects,
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
  status_options = (
      ["الكل"] + list(df_projects["الحالة"].dropna().unique())
      if "الحالة" in df_projects.columns
      else ["الكل"]
  )
  status_filter = st.multiselect(
      "حالة المشروع", options=status_options, default=["الكل"]
  )

  manager_options = (
      ["الكل"] + list(df_projects["مدير_المشروع"].dropna().unique())
      if "مدير_المشروع" in df_projects.columns
      else ["الكل"]
  )
  manager_filter = st.selectbox("مدير المشروع", options=manager_options)

  owner_options = (
      ["الكل"] + list(df_report["الجهة"].dropna().unique())
      if "الجهة" in df_report.columns
      else ["الكل"]
  )
  owner_filter = st.selectbox("الجهة المالكة", options=owner_options)

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
  if "الكل" not in status_filter and "الحالة" in filtered_projects.columns:
    filtered_projects = filtered_projects[
        filtered_projects["الحالة"].isin(status_filter)
    ]
  if manager_filter != "الكل" and "مدير_المشروع" in filtered_projects.columns:
    filtered_projects = filtered_projects[
        filtered_projects["مدير_المشروع"] == manager_filter
    ]
  if not filtered_report.empty and owner_filter != "الكل":
    if "الجهة" in filtered_report.columns:
      filtered_report = filtered_report[
          filtered_report["الجهة"] == owner_filter
      ]

# ===== الصف الأول: مخططات ماليّة =====
st.markdown("### 📊 التحليل المالي للمشاريع")
col1, col2 = st.columns([2, 1])

with col1:
  if (
      not filtered_report.empty
      and "المشروع" in filtered_report.columns
      and "القيمة_الاجمالية" in filtered_report.columns
  ):
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
    if "ما_تم_صرفه" in plot_df.columns:
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
    if "المتبقي" in plot_df.columns:
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
  if not filtered_projects.empty and "الحالة" in filtered_projects.columns:
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
if (
    not filtered_projects.empty
    and not filtered_report.empty
    and "م" in filtered_projects.columns
    and "م" in filtered_report.columns
):
  cols_to_merge = [
      c
      for c in ["م", "القيمة_الاجمالية", "ما_تم_صرفه", "المتبقي", "الجهة"]
      if c in filtered_report.columns
  ]
  merged_df = filtered_projects.merge(
      filtered_report[cols_to_merge], on="م", how="left"
  )
else:
  merged_df = filtered_projects

search = st.text_input(
    "🔍 بحث سريع عن مشروع", placeholder="اكتب اسم المشروع..."
)
if search and not merged_df.empty and "المشروع" in merged_df.columns:
  merged_df = merged_df[
      merged_df["المشروع"].str.contains(search, case=False, na=False)
  ]

if not merged_df.empty:
  cols_to_show = [
      c
      for c in [
          "م",
          "المشروع",
          "مدير_المشروع",
          "الحالة",
          "القيمة_الاجمالية",
          "ما_تم_صرفه",
          "المتبقي",
      ]
      if c in merged_df.columns
  ]
  if "الجهة" in merged_df.columns and "الجهة" not in cols_to_show:
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