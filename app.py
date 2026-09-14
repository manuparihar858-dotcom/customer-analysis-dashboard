import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(
    page_title="Customer Analysis Dashboard",
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def create_sample_data():
    rng = np.random.default_rng(42)
    n = 1200

    regions = rng.choice(
        ["North", "South", "East", "West"], n, p=[0.28, 0.24, 0.22, 0.26]
    )
    ages = rng.integers(18, 71, n)
    segments = rng.choice(
        ["High Value", "Regular", "Low Value"], n, p=[0.22, 0.53, 0.25]
    )
    orders = np.array([
        rng.integers(6, 13) if s == "High Value"
        else rng.integers(3, 8) if s == "Regular"
        else rng.integers(1, 4)
        for s in segments
    ])
    avg_order = rng.integers(650, 1900, n)
    sales = orders * avg_order
    months = rng.choice(
        ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
         "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], n
    )

    df = pd.DataFrame({
        "Customer ID": [f"C{i+1:04d}" for i in range(n)],
        "Region": regions,
        "Age": ages,
        "Segment": segments,
        "Orders": orders,
        "Sales": sales,
        "Month": months
    })

    age_bins = [17, 25, 35, 45, 55, 70]
    age_labels = ["18–25", "26–35", "36–45", "46–55", "56–70"]
    df["Age Group"] = pd.cut(
        df["Age"], bins=age_bins, labels=age_labels, include_lowest=True
    )
    return df


def prepare_uploaded_data(uploaded_file):
    if uploaded_file.name.lower().endswith(".csv"):
        return pd.read_csv(uploaded_file)

    return pd.read_excel(uploaded_file)


def standardize_columns(df):
    result = df.copy()
    result.columns = [
        str(c).strip().replace("_", " ").replace("-", " ")
        for c in result.columns
    ]
    return result


st.markdown("""
<style>
.block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
.dashboard-title {font-size: 2rem; font-weight: 800; margin-bottom: 0;}
.dashboard-subtitle {color: #64748b; margin-top: .2rem; margin-bottom: 1rem;}
div[data-testid="stMetric"] {
    background: white; border: 1px solid #e2e8f0;
    border-radius: 12px; padding: 12px;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="dashboard-title">CUSTOMER ANALYSIS DASHBOARD</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="dashboard-subtitle">Customer behavior, sales performance and value segmentation</div>',
    unsafe_allow_html=True
)

st.sidebar.header("Data Source")
source = st.sidebar.radio(
    "Choose data",
    ["Use sample data", "Upload CSV / Excel"]
)

if source == "Upload CSV / Excel":
    uploaded = st.sidebar.file_uploader(
        "Upload your dataset",
        type=["csv", "xlsx", "xls"],
        help="For best results, include columns such as Region, Segment, Orders and Sales."
    )

    if uploaded is None:
        st.info("Upload a CSV or Excel file from the sidebar to analyze your own data.")
        st.caption("You can also choose 'Use sample data' to preview the dashboard.")
        st.stop()

    try:
        df = standardize_columns(prepare_uploaded_data(uploaded))
    except Exception as e:
        st.error(f"Could not read the uploaded file: {e}")
        st.stop()

    st.success(f"Loaded {len(df):,} rows from {uploaded.name}")
else:
    df = create_sample_data()
    st.sidebar.caption("Using simulated portfolio data.")

# Try to identify common column names
lower_map = {str(c).lower(): c for c in df.columns}

def find_col(names):
    for name in names:
        if name.lower() in lower_map:
            return lower_map[name.lower()]
    return None

region_col = find_col(["Region", "Area", "Location"])
segment_col = find_col(["Segment", "Customer Segment", "Category"])
orders_col = find_col(["Orders", "Order Count", "Order Quantity"])
sales_col = find_col(["Sales", "Revenue", "Sales Amount", "Amount"])
age_col = find_col(["Age"])

st.sidebar.header("Dashboard Filters")

if region_col:
    region_options = ["All"] + sorted(df[region_col].dropna().astype(str).unique().tolist())
    region = st.sidebar.selectbox("Region", region_options)
else:
    region = "All"

if segment_col:
    segment_options = ["All"] + sorted(df[segment_col].dropna().astype(str).unique().tolist())
    segment = st.sidebar.selectbox("Customer Segment", segment_options)
else:
    segment = "All"

filtered = df.copy()

if region != "All" and region_col:
    filtered = filtered[filtered[region_col].astype(str) == region]

if segment != "All" and segment_col:
    filtered = filtered[filtered[segment_col].astype(str) == segment]

sales_value = (
    pd.to_numeric(filtered[sales_col], errors="coerce").fillna(0).sum()
    if sales_col else 0
)
orders_value = (
    pd.to_numeric(filtered[orders_col], errors="coerce").fillna(0).sum()
    if orders_col else len(filtered)
)
aov = sales_value / orders_value if orders_value else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Records", f"{len(filtered):,}")
c2.metric("Total Orders", f"{orders_value:,.0f}")
c3.metric("Total Sales", f"₹{sales_value:,.0f}")
c4.metric("Average Order Value", f"₹{aov:,.0f}")

st.divider()

if not sales_col:
    st.warning("No Sales/Revenue column was detected. Add a column named Sales, Revenue, Sales Amount, or Amount for sales charts.")

left, right = st.columns([1.25, 1])

with left:
    st.subheader("Sales by Region")
    if region_col and sales_col:
        region_sales = filtered.copy()
        region_sales["_sales"] = pd.to_numeric(
            region_sales[sales_col], errors="coerce"
        ).fillna(0)
        region_sales = (
            region_sales.groupby(region_col, as_index=False)["_sales"]
            .sum()
            .sort_values("_sales", ascending=False)
        )
        fig = px.bar(
            region_sales, x=region_col, y="_sales", text="_sales",
            template="plotly_white",
            labels={"_sales": "Sales (₹)", region_col: ""}
        )
        fig.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")
        fig.update_layout(height=390, margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("A Region and Sales column are needed for this chart.")

with right:
    st.subheader("Customer Segments")
    if segment_col and sales_col:
        seg = filtered.copy()
        seg["_sales"] = pd.to_numeric(seg[sales_col], errors="coerce").fillna(0)
        seg = seg.groupby(segment_col, as_index=False)["_sales"].sum()
        fig = px.pie(
            seg, names=segment_col, values="_sales", hole=.58,
            template="plotly_white"
        )
        fig.update_layout(height=390, margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("A Segment and Sales column are needed for this chart.")

st.subheader("Data Preview")
st.dataframe(filtered.head(100), use_container_width=True, hide_index=True, height=360)

st.caption(
    "Portfolio project • Supports CSV and Excel uploads. Sample data is simulated "
    "for demonstration and does not represent a real client or business."
)
