from datetime import datetime
import io
import dash
import dash_bootstrap_components as dbc
from dash import ALL, MATCH, Input, Output, State, callback_context, dash_table, dcc, html
import pandas as pd
import plotly.graph_objects as go

# -----------------------------
# 1. البيانات الأولية (مع تصحيح الأبعاد)
# -----------------------------
data = [
    [
        "PRJ-001",
        "تقديم الخدمات الاستشارية لدراسة تطوير خطط تشغيل و صيانة المرافق الهامة",
        None,
        "وزارة البيئة و المياه و الزراعة",
        "قيد التنفيذ",
        24403000,
        24063850,
        2897500,
        21166350,
        2897500,
        0,
        0,
    ],
    [
        "PRJ-002",
        "الاشراف علي تصميم و انشاء المختبر البيطري المركزي",
        None,
        "وزارة البيئة و المياه و الزراعة",
        "قيد التنفيذ",
        15503196,
        11261424,
        1103692,
        10157732,
        1103692,
        0,
        0,
    ],
    [
        "PRJ-003",
        "تقديم الخدمات الاستشارية للاشراف علي المشاريع الهندسية ببنك التنمية",
        None,
        "بنك التنمية",
        "قيد التنفيذ",
        5796000,
        4588500,
        241500,
        4347000,
        241500,
        0,
        0,
    ],
    [
        "PRJ-004",
        (
            "الاتفاقية الاطارية لخدمات الاشراف علي مشاريع إدارة المرافق"
            " بالمنطقة الوسطي"
        ),
        None,
        "شركة تطوير المباني (TBC)",
        "قيد التنفيذ",
        84807056,
        84259287,
        19688745,
        64570542,
        19688745,
        0,
        0,
    ],
    [
        "PRJ-005",
        (
            "الاتفاقية الاطارية لخدمات الاشراف علي مشاريع إدارة المرافق"
            " بالمنطقة الوسطي امر عمل جديد"
        ),
        None,
        "شركة تطوير المباني (TBC)",
        "قيد التنفيذ",
        115408642,
        3600000,
        3600000,
        0,
        3600000,
        3,
        0,
    ],
    [
        "PRJ-006",
        "الاشراف علي إدارة المرافق بالمنطقة الجنوبية",
        None,
        "شركة تطوير المباني (TBC)",
        "قيد التنفيذ",
        30200000,
        26479727,
        5177966,
        21301761,
        5177966,
        0,
        0,
    ],
    [
        "PRJ-007",
        (
            "الخدمات الاستشارية للاستفادة من المياه الجوفية و السطحية و مشاريع"
            " درء اخطار السيول"
        ),
        None,
        "وزارة البيئة و المياه و الزراعة",
        "قيد التنفيذ",
        23292100,
        7441075,
        3792700,
        3648375,
        3792700,
        0,
        0,
    ],
    [
        "PRJ-008",
        (
            "الاتفاقية الاطارية لتصميم مشاريع المؤسسة العامة للري امر عمل (02)"
        ),
        None,
        "المؤسسة العامة للري",
        "قيد التنفيذ",
        5398330,
        4508000,
        4508000,
        0,
        4508000,
        0,
        0,
    ],
    [
        "PRJ-009",
        "ترميز مباني التراث المعماري وسط الرياض",
        None,
        "وزارة الثقافة",
        "قيد التنفيذ",
        4999240,
        3910460,
        3910460,
        0,
        3910460,
        0,
        0,
    ],
    [
        "PRJ-010",
        "دراسة و تصميم مشروع انشاء قاعة الطعام بالمقر الرئيسي",
        None,
        "المؤسسة العامة للري",
        "قيد التنفيذ",
        724500,
        724500,
        439875,
        284625,
        439875,
        1,
        0,
    ],
    # تم تصحيح الصفين التاليين بإضافة None لمدير المشروع لضبط عدد الأعمدة لـ 12
    [
        "PRJ-011",
        "الاشراف علي المشاريع الصغيرة بجميع مناطق المملكة",
        None,
        "وزارة البيئة و المياه و الزراعة",
        "قيد التنفيذ",
        22783158,
        22783158,
        -2,
        22783158,
        -2,
        1,
        1,
    ],
    [
        "PRJ-012",
        (
            "الاشراف علي المشاريع الصغيرة بجميع مناطق المملكة (المرحلة الثانية)"
        ),
        None,
        "وزارة البيئة و المياه و الزراعة",
        "قيد التنفيذ",
        20841128,
        3664500,
        3664500,
        0,
        3664500,
        0,
        0,
    ],
]

cols = [
    "Project ID",
    "Project Name",
    "Project Manager",
    "Client / Sector",
    "Status",
    "Contract Value",
    "Actual Cost",
    "Forecasted Spend",
    "Collected Amount",
    "Uncollected Amount",
    "% Spent",
    "% Collected",
]


def prepare_dataframe(raw_data):
  df = pd.DataFrame(raw_data, columns=cols)
  num_cols = [
      "Contract Value",
      "Actual Cost",
      "Forecasted Spend",
      "Collected Amount",
      "Uncollected Amount",
  ]
  for c in num_cols:
    df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

  df["Remaining Budget"] = df["Contract Value"] - df["Actual Cost"]
  df["% Actual Spent (calc)"] = (
      df["Actual Cost"] / df["Contract Value"].replace({0: pd.NA})
  ).fillna(0)
  df["% Collected (calc)"] = (
      df["Collected Amount"] / df["Contract Value"].replace({0: pd.NA})
  ).fillna(0)
  df["Spend Status"] = df.apply(
      lambda r: (
          "تجاوز الميزانية"
          if r["Forecasted Spend"] > r["Contract Value"]
          else "ضمن الميزانية"
      ),
      axis=1,
  )
  return df


# -----------------------------
# 2. إعداد التطبيق والواجهة
# -----------------------------
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    suppress_callback_exceptions=True,
)
server = app.server


def fmt_money(x):
  try:
    x = float(x)
  except:
    return "0"
  return f"{x:,.0f}"


def fmt_pct_from_ratio(r):
  try:
    r = float(r)
  except:
    return "0%"
  return f"{r*100:.1f}%"


def create_card(title, value_text, subtitle="", icon=None):
  return html.Div(
      className="card",
      children=[
          html.Div(
              style={
                  "display": "flex",
                  "alignItems": "center",
                  "justifyContent": "space-between",
              },
              children=[
                  html.Div(className="card-title", children=title),
                  html.Div(icon) if icon else html.Div(),
              ],
          ),
          html.Div(className="card-value", children=value_text),
          (
              html.Div(className="card-subtitle", children=subtitle)
              if subtitle
              else html.Div()
          ),
      ],
  )


# نافذة إضافة/تعديل مشروع
project_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("إدارة المشروع"), close_button=True),
        dbc.ModalBody([
            html.Div(
                id="modal-message",
                style={"color": "#ff6b6b", "marginBottom": "10px"},
            ),
            dbc.Row([
                dbc.Col(
                    [
                        dbc.Label("معرف المشروع"),
                        dbc.Input(
                            id="modal-project-id",
                            type="text",
                            placeholder="مثل: PRJ-013",
                        ),
                    ],
                    width=6,
                ),
                dbc.Col(
                    [
                        dbc.Label("اسم المشروع"),
                        dbc.Input(
                            id="modal-project-name",
                            type="text",
                            placeholder="اسم المشروع",
                        ),
                    ],
                    width=6,
                ),
            ]),
            dbc.Row([
                dbc.Col(
                    [
                        dbc.Label("مدير المشروع"),
                        dbc.Input(
                            id="modal-project-manager",
                            type="text",
                            placeholder="اسم المدير",
                        ),
                    ],
                    width=6,
                ),
                dbc.Col(
                    [
                        dbc.Label("القطاع / العميل"),
                        dbc.Input(
                            id="modal-client",
                            type="text",
                            placeholder="القطاع أو العميل",
                        ),
                    ],
                    width=6,
                ),
            ]),
            dbc.Row([
                dbc.Col(
                    [
                        dbc.Label("الحالة"),
                        dbc.Select(
                            id="modal-status",
                            options=[
                                {"label": s, "value": s}
                                for s in [
                                    "قيد التنفيذ",
                                    "مكتمل",
                                    "معلق",
                                    "ملغي",
                                ]
                            ],
                            value="قيد التنفيذ",
                        ),
                    ],
                    width=6,
                ),
                dbc.Col(
                    [
                        dbc.Label("قيمة العقد"),
                        dbc.Input(
                            id="modal-contract-value",
                            type="number",
                            placeholder="0",
                        ),
                    ],
                    width=6,
                ),
            ]),
            dbc.Row([
                dbc.Col(
                    [
                        dbc.Label("المصروف الفعلي"),
                        dbc.Input(
                            id="modal-actual-cost",
                            type="number",
                            placeholder="0",
                        ),
                    ],
                    width=6,
                ),
                dbc.Col(
                    [
                        dbc.Label("متوقع الصرف"),
                        dbc.Input(
                            id="modal-forecast-spend",
                            type="number",
                            placeholder="0",
                        ),
                    ],
                    width=6,
                ),
            ]),
            dbc.Row([
                dbc.Col(
                    [
                        dbc.Label("المبلغ المحصل"),
                        dbc.Input(
                            id="modal-collected-amount",
                            type="number",
                            placeholder="0",
                        ),
                    ],
                    width=6,
                ),
                dbc.Col(
                    [
                        dbc.Label("المتبقي تحصيله"),
                        dbc.Input(
                            id="modal-uncollected-amount",
                            type="number",
                            placeholder="0",
                        ),
                    ],
                    width=6,
                ),
            ]),
            dcc.Store(id="modal-edit-mode", data=None),
        ]),
        dbc.ModalFooter([
            dbc.Button(
                "إلغاء", id="modal-cancel", className="ms-auto", color="secondary"
            ),
            dbc.Button("حفظ المشروع", id="modal-save", color="primary"),
        ]),
    ],
    id="project-modal",
    size="lg",
)

app.layout = html.Div(
    dir="rtl",
    style={
        "fontFamily": "Tajawal, Cairo, Arial, sans-serif",
        "background": "#0b1220",
        "color": "white",
        "minHeight": "100vh",
    },
    children=[
        # Stores & Download
        dcc.Store(
            id="projects-store", data=prepare_dataframe(data).to_dict("records")
        ),
        dcc.Download(id="download-csv"),
        # Header
        html.Div(
            style={
                "padding": "18px 24px",
                "borderBottom": "1px solid rgba(255,255,255,0.08)",
            },
            children=[
                html.Div(
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "space-between",
                        "gap": "16px",
                        "flexWrap": "wrap",
                    },
                    children=[
                        html.Div(children=[
                            html.H2(
                                "📊 منصة محفظة المشاريع (Contracts & Spend)",
                                style={"margin": 0, "fontWeight": 800},
                            ),
                            html.Div(
                                "لوحة احترافية لمتابعة الصرف والتحصيل والمتبقي",
                                style={"opacity": 0.85},
                            ),
                        ]),
                        html.Div(
                            style={
                                "display": "flex",
                                "gap": "10px",
                                "alignItems": "center",
                            },
                            children=[
                                dbc.Button(
                                    "➕ إضافة مشروع",
                                    id="add-project-btn",
                                    color="success",
                                    style={"fontWeight": "bold"},
                                ),
                                dbc.Button(
                                    "🔄 تحديث الكل",
                                    id="refresh-all-btn",
                                    color="info",
                                    style={"fontWeight": "bold"},
                                ),
                                html.Span(
                                    "Dashboard • مقاييس تفاعلية",
                                    style={
                                        "opacity": 0.85,
                                        "fontSize": "14px",
                                        "marginRight": "10px",
                                    },
                                ),
                            ],
                        ),
                    ],
                )
            ],
        ),
        # Filters
        html.Div(
            style={"padding": "18px 24px"},
            children=[
                html.Div(
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "repeat(4, minmax(0, 1fr))",
                        "gap": "14px",
                    },
                    children=[
                        html.Div([
                            html.Label(
                                "حالة المشروع",
                                style={"opacity": 0.9, "marginBottom": 8},
                            ),
                            dcc.Dropdown(
                                id="filter-status",
                                multi=True,
                                className="dropdown-dark",
                            ),
                        ]),
                        html.Div([
                            html.Label(
                                "القطاع / العميل",
                                style={"opacity": 0.9, "marginBottom": 8},
                            ),
                            dcc.Dropdown(
                                id="filter-client",
                                multi=True,
                                className="dropdown-dark",
                            ),
                        ]),
                        html.Div([
                            html.Label(
                                "مدير المشروع",
                                style={"opacity": 0.9, "marginBottom": 8},
                            ),
                            dcc.Dropdown(
                                id="filter-manager",
                                multi=True,
                                className="dropdown-dark",
                            ),
                        ]),
                        html.Div([
                            html.Label(
                                "بحث سريع",
                                style={"opacity": 0.9, "marginBottom": 8},
                            ),
                            dbc.Input(
                                id="search-input",
                                type="text",
                                placeholder="بحث باسم المشروع...",
                                style={
                                    "background": "#1a2332",
                                    "color": "white",
                                    "border": (
                                        "1px solid rgba(255,255,255,0.1)"
                                    ),
                                },
                            ),
                        ]),
                    ],
                )
            ],
        ),
        # Cards
        html.Div(
            style={"padding": "0 24px 18px 24px"},
            children=[
                html.Div(
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "repeat(4, minmax(0, 1fr))",
                        "gap": "14px",
                    },
                    children=[
                        html.Div(id="card-total-contract"),
                        html.Div(id="card-actual-spent"),
                        html.Div(id="card-forecast-spend"),
                        html.Div(id="card-remaining-budget"),
                    ],
                )
            ],
        ),
        # Charts
        html.Div(
            style={"padding": "0 24px 18px 24px"},
            children=[
                html.Div(
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "2fr 1fr",
                        "gap": "14px",
                    },
                    children=[
                        html.Div([
                            html.Div(
                                style={
                                    "display": "flex",
                                    "justifyContent": "space-between",
                                    "alignItems": "center",
                                    "marginBottom": 10,
                                },
                                children=[
                                    html.Div(
                                        style={
                                            "fontWeight": 800,
                                            "fontSize": 16,
                                            "opacity": 0.95,
                                        },
                                        children="مقارنة القيم حسب المشروع",
                                    ),
                                    html.Small(
                                        "انقر على الصف في الجدول أدناه لعرض"
                                        " التفاصيل",
                                        style={
                                            "opacity": 0.6,
                                            "fontSize": "12px",
                                        },
                                    ),
                                ],
                            ),
                            dcc.Graph(
                                id="bar-comparison",
                                style={
                                    "background": "#0f1830",
                                    "borderRadius": "12px",
                                    "padding": "8px",
                                },
                            ),
                        ]),
                        html.Div([
                            html.Div(
                                style={
                                    "marginBottom": 10,
                                    "fontWeight": 800,
                                    "fontSize": 16,
                                    "opacity": 0.95,
                                },
                                children="مؤشرات الإنجاز",
                            ),
                            html.Div(
                                style={
                                    "display": "grid",
                                    "gridTemplateColumns": "1fr",
                                    "gap": "14px",
                                },
                                children=[
                                    dcc.Graph(
                                        id="gauge-spent",
                                        style={
                                            "background": "#0f1830",
                                            "borderRadius": "12px",
                                            "padding": "8px",
                                        },
                                    ),
                                    dcc.Graph(
                                        id="gauge-collected",
                                        style={
                                            "background": "#0f1830",
                                            "borderRadius": "12px",
                                            "padding": "8px",
                                        },
                                    ),
                                ],
                            ),
                        ]),
                    ],
                )
            ],
        ),
        # Table
        html.Div(
            style={"padding": "0 24px 40px 24px"},
            children=[
                html.Div(
                    style={
                        "display": "flex",
                        "justifyContent": "space-between",
                        "alignItems": "center",
                        "marginBottom": 10,
                    },
                    children=[
                        html.Div(
                            style={
                                "fontWeight": 800,
                                "fontSize": 16,
                                "opacity": 0.95,
                            },
                            children=(
                                "جدول المشاريع التفصيلي (اضغط على الصف"
                                " للتفاصيل/التعديل)"
                            ),
                        ),
                        html.Div(
                            style={"display": "flex", "gap": "10px"},
                            children=[
                                dbc.Button(
                                    "📥 تصدير CSV",
                                    id="export-btn",
                                    color="secondary",
                                    size="sm",
                                ),
                                dbc.Button(
                                    "🗑️ حذف المشروع المحدد",
                                    id="delete-selected-btn",
                                    color="danger",
                                    size="sm",
                                ),
                            ],
                        ),
                    ],
                ),
                dcc.Loading(children=[
                    dash_table.DataTable(
                        id="projects-table",
                        style_table={
                            "overflowX": "auto",
                            "background": "#0f1830",
                            "borderRadius": "12px",
                        },
                        style_cell={
                            "textAlign": "right",
                            "padding": "10px",
                            "background": "#0f1830",
                            "color": "white",
                            "border": "1px solid rgba(255,255,255,0.06)",
                            "fontFamily": "Tajawal, Cairo, Arial, sans-serif",
                        },
                        style_header={
                            "background": "#0b142a",
                            "fontWeight": "bold",
                            "color": "white",
                        },
                        page_size=10,
                        sort_action="native",
                        filter_action="none",
                        row_selectable="single",
                        columns=[
                            {"name": "المعرف", "id": "Project ID"},
                            {"name": "اسم المشروع", "id": "Project Name"},
                            {"name": "مدير المشروع", "id": "Project Manager"},
                            {"name": "القطاع / العميل", "id": "Client / Sector"},
                            {"name": "الحالة", "id": "Status"},
                            {"name": "قيمة العقد", "id": "Contract Value_fmt"},
                            {
                                "name": "المصروف الفعلي",
                                "id": "Actual Cost_fmt",
                            },
                            {
                                "name": "المتبقي لم يصرف",
                                "id": "Remaining Budget_fmt",
                            },
                            {
                                "name": "المبلغ المحصّل",
                                "id": "Collected Amount_fmt",
                            },
                            {
                                "name": "المتبقي تحصيله",
                                "id": "Uncollected Amount_fmt",
                            },
                            {
                                "name": "% الصرف الفعلي",
                                "id": "% Actual Spent_fmt",
                            },
                            {"name": "% التحصيل", "id": "% Collected_fmt"},
                            {"name": "Spend Status", "id": "Spend Status"},
                        ],
                        data=[],
                        style_data_conditional=[],
                    )
                ]),
            ],
        ),
        # Detail Modal
        dbc.Modal(
            [
                dbc.ModalHeader(
                    dbc.ModalTitle("تفاصيل المشروع"), close_button=True
                ),
                dbc.ModalBody(id="project-detail-body"),
                dbc.ModalFooter([
                    dbc.Button(
                        "إغلاق",
                        id="detail-close",
                        className="ms-auto",
                        color="secondary",
                    ),
                    dbc.Button(
                        "✏️ تعديل المشروع",
                        id="open-edit-from-detail-btn",
                        color="primary",
                    ),
                ]),
            ],
            id="project-detail-modal",
            size="lg",
        ),
        # Add/Edit Modal
        project_modal,
        # Footer
        html.Div(
            style={
                "padding": "18px 24px",
                "opacity": 0.7,
                "borderTop": "1px solid rgba(255,255,255,0.08)",
                "display": "flex",
                "justifyContent": "space-between",
            },
            children=[
                html.Div("© Portfolio Dashboard • تم تحسينه وتحديثه"),
                html.Div(
                    id="footer-info",
                    children=f"آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                ),
            ],
        ),
        html.Style("""
            .card{
                background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02));
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 14px;
                padding: 14px 16px;
                min-height: 90px;
                transition: all 0.3s ease;
            }
            .card:hover{
                background: linear-gradient(180deg, rgba(255,255,255,0.10), rgba(255,255,255,0.04));
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(0,0,0,0.3);
            }
            .card-title{opacity:0.85; font-size:14px; font-weight:700; margin-bottom:10px}
            .card-value{font-size:24px; font-weight:900}
            .card-subtitle{opacity:0.8; margin-top:6px; font-size:13px}
            .dropdown-dark .Select-control{background:#1a2332 !important; border-color:rgba(255,255,255,0.1) !important; color:white !important}
            .dropdown-dark .Select-menu-outer{background:#1a2332 !important; border-color:rgba(255,255,255,0.1) !important}
            .dropdown-dark .Select-option{background:#1a2332 !important; color:white !important}
            .dropdown-dark .Select-option.is-selected{background:#0ea5e9 !important}
            .dropdown-dark .Select-option:hover{background:#2a3a52 !important}
            .dropdown-dark .Select-value-label{color:white !important}
            .dropdown-dark .Select-input input{color:white !important}
            .project-detail-card{background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06); border-radius:12px; padding:14px; margin-bottom:10px}
            .project-detail-card .label{opacity:0.7; font-size:12px}
            .project-detail-card .value{font-size:18px; font-weight:bold; margin-top:4px}
            .progress-bar-container{background:#1a2332; border-radius:8px; height:8px; overflow:hidden; margin-top:6px}
            .progress-bar-fill{height:100%; border-radius:8px; transition:width 0.5s ease}
        """),
    ],
)


# -----------------------------
# 3. Callbacks التفاعلية
# -----------------------------

# تحديث خيارات التصفية عند تغير البيانات
@app.callback(
    Output("filter-status", "options"),
    Output("filter-status", "value"),
    Output("filter-client", "options"),
    Output("filter-client", "value"),
    Output("filter-manager", "options"),
    Output("filter-manager", "value"),
    Input("projects-store", "data"),
)
def sync_filter_options(store_data):
  if not store_data:
    return [], [], [], [], [], []
  df = pd.DataFrame(store_data)
  statuses = sorted(df["Status"].dropna().unique().tolist())
  clients = sorted(df["Client / Sector"].dropna().unique().tolist())
  managers = sorted(df["Project Manager"].dropna().astype(str).unique().tolist())

  return (
      [{"label": s, "value": s} for s in statuses],
      statuses,
      [{"label": c, "value": c} for c in clients],
      clients,
      [{"label": m, "value": m} for m in managers],
      managers,
  )


# الفلترة الحسابية للـ Dataframe
def get_filtered_df(store_data, status_vals, client_vals, manager_vals, search):
  if not store_data:
    return pd.DataFrame(columns=cols)
  df = pd.DataFrame(store_data)
  if status_vals:
    df = df[df["Status"].isin(status_vals)]
  if client_vals:
    df = df[df["Client / Sector"].isin(client_vals)]
  if manager_vals:
    df = df[df["Project Manager"].fillna("—").isin(manager_vals)]
  if search:
    df = df[df["Project Name"].str.contains(search, case=False, na=False)]
  return df


# تحديث الكروت والإحصائيات والمخططات والجدول
@app.callback(
    Output("card-total-contract", "children"),
    Output("card-actual-spent", "children"),
    Output("card-forecast-spend", "children"),
    Output("card-remaining-budget", "children"),
    Output("bar-comparison", "figure"),
    Output("gauge-spent", "figure"),
    Output("gauge-collected", "figure"),
    Output("projects-table", "data"),
    Output("projects-table", "style_data_conditional"),
    Input("projects-store", "data"),
    Input("filter-status", "value"),
    Input("filter-client", "value"),
    Input("filter-manager", "value"),
    Input("search-input", "value"),
)
def update_dashboard(
    store_data, status_vals, client_vals, manager_vals, search_term
):
  dff = get_filtered_df(
      store_data, status_vals, client_vals, manager_vals, search_term
  )

  total_contract = (
      dff["Contract Value"].sum() if not dff.empty else 0
  )
  total_actual = dff["Actual Cost"].sum() if not dff.empty else 0
  total_forecast = (
      dff["Forecasted Spend"].sum() if not dff.empty else 0
  )
  remaining = dff["Remaining Budget"].sum() if not dff.empty else 0
  total_collected = (
      dff["Collected Amount"].sum() if not dff.empty else 0
  )

  cards = (
      create_card(
          "إجمالي قيمة العقود",
          fmt_money(total_contract),
          "Contract Value",
          "💰",
      ),
      create_card(
          "إجمالي المصروف الفعلي",
          fmt_money(total_actual),
          "Actual Cost",
          "💳",
      ),
      create_card(
          "إجمالي متوقع الصرف",
          fmt_money(total_forecast),
          "Forecasted Spend",
          "📊",
      ),
      create_card(
          "المتبقي لم يصرف", fmt_money(remaining), "Remaining Budget", "📈"
      ),
  )

  # Plotly Horizontal Bar
  fig_bar = go.Figure()
  if not dff.empty:
    fig_bar.add_trace(
        go.Bar(
            name="قيمة العقد",
            y=dff["Project Name"],
            x=dff["Contract Value"],
            orientation="h",
            text=dff["Contract Value"].apply(lambda x: f"{x:,.0f}"),
            textposition="outside",
            marker_color="#0ea5e9",
        )
    )
    fig_bar.add_trace(
        go.Bar(
            name="متوقع الصرف",
            y=dff["Project Name"],
            x=dff["Forecasted Spend"],
            orientation="h",
            text=dff["Forecasted Spend"].apply(lambda x: f"{x:,.0f}"),
            textposition="outside",
            marker_color="#fbbf24",
        )
    )
    fig_bar.add_trace(
        go.Bar(
            name="المبلغ المحصّل",
            y=dff["Project Name"],
            x=dff["Collected Amount"],
            orientation="h",
            text=dff["Collected Amount"].apply(lambda x: f"{x:,.0f}"),
            textposition="outside",
            marker_color="#22c55e",
        )
    )
  fig_bar.update_layout(
      barmode="group",
      height=400,
      legend=dict(
          orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
      ),
      margin=dict(l=30, r=20, t=20, b=20),
      paper_bgcolor="#0f1830",
      plot_bgcolor="#0f1830",
      font=dict(color="white"),
  )
  fig_bar.update_yaxes(tickfont=dict(color="white"), automargin=True)
  fig_bar.update_xaxes(tickfont=dict(color="white"), automargin=True)

  # Gauges
  pct_spent = (
      (total_actual / total_contract) * 100 if total_contract != 0 else 0
  )
  pct_collected = (
      (total_collected / total_contract) * 100 if total_contract != 0 else 0
  )

  fig_g1 = go.Figure(
      go.Indicator(
          mode="gauge+number",
          value=round(pct_spent, 1),
          number={"suffix": "%", "font": {"size": 22, "color": "white"}},
          gauge={
              "axis": {"range": [0, max(100, pct_spent)]},
              "bar": {"color": "#00d084"},
              "steps": [
                  {"range": [0, 60], "color": "#1f2937"},
                  {"range": [60, 85], "color": "#0ea5e9"},
                  {"range": [85, 100], "color": "#ef4444"},
              ],
          },
          title={
              "text": "نسبة الصرف الفعلي",
              "font": {"color": "white", "size": 14},
          },
      )
  )
  fig_g1.update_layout(
      height=220,
      margin=dict(l=20, r=20, t=30, b=10),
      paper_bgcolor="#0f1830",
      font=dict(color="white"),
  )

  fig_g2 = go.Figure(
      go.Indicator(
          mode="gauge+number",
          value=round(pct_collected, 1),
          number={"suffix": "%", "font": {"size": 22, "color": "white"}},
          gauge={
              "axis": {"range": [0, max(100, pct_collected)]},
              "bar": {"color": "#22c55e"},
              "steps": [
                  {"range": [0, 60], "color": "#1f2937"},
                  {"range": [60, 85], "color": "#a78bfa"},
                  {"range": [85, 100], "color": "#22c55e"},
              ],
          },
          title={
              "text": "نسبة التحصيل",
              "font": {"color": "white", "size": 14},
          },
      )
  )
  fig_g2.update_layout(
      height=220,
      margin=dict(l=20, r=20, t=30, b=10),
      paper_bgcolor="#0f1830",
      font=dict(color="white"),
  )

  # Data Table Records
  table_df = dff.copy()
  if not table_df.empty:
    table_df["Contract Value_fmt"] = table_df["Contract Value"].map(fmt_money)
    table_df["Actual Cost_fmt"] = table_df["Actual Cost"].map(fmt_money)
    table_df["Remaining Budget_fmt"] = table_df["Remaining Budget"].map(
        fmt_money
    )
    table_df["Collected Amount_fmt"] = table_df["Collected Amount"].map(
        fmt_money
    )
    table_df["Uncollected Amount_fmt"] = table_df["Uncollected Amount"].map(
        fmt_money
    )
    table_df["% Actual Spent_fmt"] = table_df["% Actual Spent (calc)"].map(
        fmt_pct_from_ratio
    )
    table_df["% Collected_fmt"] = table_df["% Collected (calc)"].map(
        fmt_pct_from_ratio
    )
    table_df["Project Manager"] = table_df["Project Manager"].fillna("—")
    table_records = table_df.to_dict("records")
  else:
    table_records = []

  style_conditional = [
      {
          "if": {
              "filter_query": "{Remaining Budget} >= 0",
              "column_id": "Remaining Budget_fmt",
          },
          "backgroundColor": "rgba(16,185,129,0.22)",
          "color": "white",
          "fontWeight": "bold",
      },
      {
          "if": {
              "filter_query": "{Remaining Budget} < 0",
              "column_id": "Remaining Budget_fmt",
          },
          "backgroundColor": "rgba(239,68,68,0.22)",
          "color": "white",
          "fontWeight": "bold",
      },
      {
          "if": {
              "filter_query": "{Spend Status} = 'ضمن الميزانية'",
              "column_id": "Spend Status",
          },
          "backgroundColor": "rgba(16,185,129,0.18)",
          "color": "#4ade80",
      },
      {
          "if": {
              "filter_query": "{Spend Status} = 'تجاوز الميزانية'",
              "column_id": "Spend Status",
          },
          "backgroundColor": "rgba(239,68,68,0.18)",
          "color": "#f87171",
      },
  ]

  return (
      cards[0],
      cards[1],
      cards[2],
      cards[3],
      fig_bar,
      fig_g1,
      fig_g2,
      table_records,
      style_conditional,
  )


# عرض نافذة التفاصيل عند النقر على صف في الجدول
@app.callback(
    Output("project-detail-modal", "is_open"),
    Output("project-detail-body", "children"),
    Input("projects-table", "active_cell"),
    Input("detail-close", "n_clicks"),
    State("projects-table", "data"),
    prevent_initial_call=True,
)
def toggle_project_detail(active_cell, close_clicks, table_data):
  ctx = callback_context
  if not ctx.triggered:
    return False, ""
  trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

  if trigger_id == "detail-close":
    return False, ""

  if trigger_id == "projects-table" and active_cell and table_data:
    row_idx = active_cell["row"]
    if row_idx < len(table_data):
      p = table_data[row_idx]
      detail_view = html.Div([
          html.Div(
              style={
                  "display": "grid",
                  "gridTemplateColumns": "1fr 1fr",
                  "gap": "12px",
              },
              children=[
                  html.Div(
                      className="project-detail-card",
                      children=[
                          html.Div(
                              className="label", children="معرف المشروع"
                          ),
                          html.Div(
                              className="value", children=p.get("Project ID")
                          ),
                      ],
                  ),
                  html.Div(
                      className="project-detail-card",
                      children=[
                          html.Div(className="label", children="الحالة"),
                          html.Div(
                              className="value", children=p.get("Status")
                          ),
                      ],
                  ),
                  html.Div(
                      className="project-detail-card",
                      children=[
                          html.Div(className="label", children="اسم المشروع"),
                          html.Div(
                              className="value",
                              children=p.get("Project Name"),
                              style={"fontSize": "15px"},
                          ),
                      ],
                  ),
                  html.Div(
                      className="project-detail-card",
                      children=[
                          html.Div(
                              className="label", children="القطاع / العميل"
                          ),
                          html.Div(
                              className="value", children=p.get("Client / Sector")
                          ),
                      ],
                  ),
                  html.Div(
                      className="project-detail-card",
                      children=[
                          html.Div(
                              className="label", children="مدير المشروع"
                          ),
                          html.Div(
                              className="value",
                              children=p.get("Project Manager"),
                          ),
                      ],
                  ),
                  html.Div(
                      className="project-detail-card",
                      children=[
                          html.Div(
                              className="label", children="Spend Status"
                          ),
                          html.Div(
                              className="value",
                              children=p.get("Spend Status"),
                              style={
                                  "color": (
                                      "#22c55e"
                                      if p.get("Spend Status")
                                      == "ضمن الميزانية"
                                      else "#ef4444"
                                  )
                              },
                          ),
                      ],
                  ),
              ],
          ),
          html.Div(
              style={
                  "display": "grid",
                  "gridTemplateColumns": "repeat(4, 1fr)",
                  "gap": "10px",
                  "marginTop": "10px",
              },
              children=[
                  html.Div(
                      className="project-detail-card",
                      children=[
                          html.Div(className="label", children="قيمة العقد"),
                          html.Div(
                              className="value",
                              children=p.get("Contract Value_fmt"),
                          ),
                      ],
                  ),
                  html.Div(
                      className="project-detail-card",
                      children=[
                          html.Div(
                              className="label", children="المصروف الفعلي"
                          ),
                          html.Div(
                              className="value",
                              children=p.get("Actual Cost_fmt"),
                          ),
                      ],
                  ),
                  html.Div(
                      className="project-detail-card",
                      children=[
                          html.Div(
                              className="label", children="المبلغ المحصل"
                          ),
                          html.Div(
                              className="value",
                              children=p.get("Collected Amount_fmt"),
                          ),
                      ],
                  ),
                  html.Div(
                      className="project-detail-card",
                      children=[
                          html.Div(
                              className="label", children="المتبقي لم يصرف"
                          ),
                          html.Div(
                              className="value",
                              children=p.get("Remaining Budget_fmt"),
                          ),
                      ],
                  ),
              ],
          ),
      ])
      return True, detail_view

  return False, ""


# التحكم بفتح مودال الإضافة والتعديل
@app.callback(
    Output("project-modal", "is_open"),
    Output("modal-edit-mode", "data"),
    Output("modal-project-id", "value"),
    Output("modal-project-name", "value"),
    Output("modal-project-manager", "value"),
    Output("modal-client", "value"),
    Output("modal-status", "value"),
    Output("modal-contract-value", "value"),
    Output("modal-actual-cost", "value"),
    Output("modal-forecast-spend", "value"),
    Output("modal-collected-amount", "value"),
    Output("modal-uncollected-amount", "value"),
    Output("modal-message", "children"),
    Input("add-project-btn", "n_clicks"),
    Input("open-edit-from-detail-btn", "n_clicks"),
    Input("modal-cancel", "n_clicks"),
    State("projects-table", "active_cell"),
    State("projects-table", "data"),
    State("projects-store", "data"),
    prevent_initial_call=True,
)
def control_project_modal(
    add_clicks,
    edit_clicks,
    cancel_clicks,
    active_cell,
    table_data,
    store_data,
):
  ctx = callback_context
  if not ctx.triggered:
    return (
        False,
        None,
        "",
        "",
        "",
        "",
        "قيد التنفيذ",
        None,
        None,
        None,
        None,
        None,
        "",
    )
  trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

  if trigger_id == "add-project-btn":
    max_num = 0
    if store_data:
      for row in store_data:
        pid = str(row.get("Project ID", ""))
        if pid.startswith("PRJ-"):
          try:
            val = int(pid.split("-")[1])
            if val > max_num:
              max_num = val
          except:
            pass
    new_id = f"PRJ-{max_num + 1:03d}"
    return (
        True,
        None,
        new_id,
        "",
        "",
        "",
        "قيد التنفيذ",
        0,
        0,
        0,
        0,
        0,
        "",
    )

  elif trigger_id == "open-edit-from-detail-btn" and active_cell and table_data:
    row_idx = active_cell["row"]
    if row_idx < len(table_data):
      p = table_data[row_idx]
      return (
          True,
          p.get("Project ID"),
          p.get("Project ID"),
          p.get("Project Name"),
          p.get("Project Manager"),
          p.get("Client / Sector"),
          p.get("Status"),
          p.get("Contract Value"),
          p.get("Actual Cost"),
          p.get("Forecasted Spend"),
          p.get("Collected Amount"),
          p.get("Uncollected Amount"),
          "",
      )

  return (
      False,
      None,
      "",
      "",
      "",
      "",
      "قيد التنفيذ",
      None,
      None,
      None,
      None,
      None,
      "",
  )


# حفظ المشروع وإضافته للخزان `projects-store`
@app.callback(
    Output("projects-store", "data"),
    Output("project-modal", "is_open", allow_duplicate=True),
    Output("modal-message", "children", allow_duplicate=True),
    Input("modal-save", "n_clicks"),
    State("modal-edit-mode", "data"),
    State("modal-project-id", "value"),
    State("modal-project-name", "value"),
    State("modal-project-manager", "value"),
    State("modal-client", "value"),
    State("modal-status", "value"),
    State("modal-contract-value", "value"),
    State("modal-actual-cost", "value"),
    State("modal-forecast-spend", "value"),
    State("modal-collected-amount", "value"),
    State("modal-uncollected-amount", "value"),
    State("projects-store", "data"),
    prevent_initial_call=True,
)
def save_project_to_store(
    n_clicks,
    edit_id,
    project_id,
    name,
    manager,
    client,
    status,
    contract_val,
    actual_val,
    forecast_val,
    collected_val,
    uncollected_val,
    store_data,
):
  if not n_clicks:
    return dash.no_update, dash.no_update, dash.no_update

  if not project_id or not name or not client:
    return (
        dash.no_update,
        True,
        "⚠️ يرجى ملء الحقول الإلزامية (المعرف، الاسم، العميل)",
    )

  df = pd.DataFrame(store_data) if store_data else pd.DataFrame(columns=cols)

  contract = float(contract_val or 0)
  actual = float(actual_val or 0)
  forecast = float(forecast_val or 0)
  collected = float(collected_val or 0)
  uncollected = float(uncollected_val or 0)
  remaining = contract - actual
  spent_ratio = actual / contract if contract != 0 else 0
  collected_ratio = collected / contract if contract != 0 else 0
  spend_status = (
      "تجاوز الميزانية" if forecast > contract else "ضمن الميزانية"
  )

  new_row = {
      "Project ID": project_id,
      "Project Name": name,
      "Project Manager": manager,
      "Client / Sector": client,
      "Status": status,
      "Contract Value": contract,
      "Actual Cost": actual,
      "Forecasted Spend": forecast,
      "Collected Amount": collected,
      "Uncollected Amount": uncollected,
      "% Spent": spent_ratio,
      "% Collected": collected_ratio,
      "Remaining Budget": remaining,
      "% Actual Spent (calc)": spent_ratio,
      "% Collected (calc)": collected_ratio,
      "Spend Status": spend_status,
  }

  if edit_id:
    df = df[df["Project ID"] != edit_id]

  df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
  return df.to_dict("records"), False, ""


# حذف المشروع المحدد
@app.callback(
    Output("projects-store", "data", allow_duplicate=True),
    Input("delete-selected-btn", "n_clicks"),
    State("projects-table", "active_cell"),
    State("projects-table", "data"),
    State("projects-store", "data"),
    prevent_initial_call=True,
)
def delete_selected_project(n_clicks, active_cell, table_data, store_data):
  if not n_clicks or not active_cell or not table_data:
    return dash.no_update

  row_idx = active_cell["row"]
  if row_idx < len(table_data):
    target_id = table_data[row_idx].get("Project ID")
    df = pd.DataFrame(store_data)
    df = df[df["Project ID"] != target_id]
    return df.to_dict("records")
  return dash.no_update


# تصدير البيانات إلى ملف CSV
@app.callback(
    Output("download-csv", "data"),
    Input("export-btn", "n_clicks"),
    State("projects-store", "data"),
    prevent_initial_call=True,
)
def export_csv(n_clicks, store_data):
  if not n_clicks or not store_data:
    return dash.no_update
  df = pd.DataFrame(store_data)
  return dcc.send_data_frame(
      df.to_csv, "projects_portfolio.csv", index=False, encoding="utf-8-sig"
  )


# تحديث البيانات وإعادة الحساب عند النقر على "تحديث الكل"
@app.callback(
    Output("projects-store", "data", allow_duplicate=True),
    Input("refresh-all-btn", "n_clicks"),
    State("projects-store", "data"),
    prevent_initial_call=True,
)
def refresh_all_store(n_clicks, store_data):
  if not n_clicks or not store_data:
    return dash.no_update
  df = pd.DataFrame(store_data)
  df = prepare_dataframe(df.to_dict("records"))
  return df.to_dict("records")


if __name__ == "__main__":
  app.run_server(host="0.0.0.0", port=8050, debug=True)