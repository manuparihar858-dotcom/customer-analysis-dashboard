import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(
    page_title="Customer Analysis Dashboard",
    page_icon="📊",
    layout="wide"
)

# -----------------------------
# Sample dataset
# -----------------------------
@st.cache_data
def create_data():
    rng = np.random.default_rng(42)
    n = 1200

    regions = rng.choice(
        ["North", "South", "East", "West"],
        n, p=[0.28, 0.24, 0.22, 0.26]
    )
    ages = rng.integers(18, 71, n)
    segments = rng.choice(
        ["High Value", "Regular", "Low Value"],
        n, p=[0.22, 0.53, 0.25]
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

df = create_data()

# -----------------------------
# Styling
# -----------------------------
st.markdown("""
<style>
.block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
.dashboard-title {
    font-size: 2rem;
    font-weight: 800;
    margin-bottom: 0;
}
.dashboard-subtitle {
    color: #64748b;
    margin-top: 0.2rem;
    margin-bottom: 1rem;
}
div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 12px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="dashboard-title">CUSTOMER ANALYSIS DASHBOARD</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="dashboard-subtitle">Customer behavior, sales performance and value segmentation</div>',
    unsafe_allow_html=True
)

# -----------------------------
# Sidebar filters
# -----------------------------
st.sidebar.header("Dashboard Filters")

region = st.sidebar.selectbox(
    "Region",
    ["All"] + sorted(df["Region"].unique().tolist())
)

segment = st.sidebar.selectbox(
    "Customer Segment",
    ["All"] + ["High Value", "Regular", "Low Value"]
)

age_group = st.sidebar.selectbox(
    "Age Group",
    ["All"] + df["Age Group"].cat.categories.tolist()
)

filtered = df.copy()

if region != "All":
    filtered = filtered[filtered["Region"] == region]

if segment != "All":
    filtered = filtered[filtered["Segment"] == segment]

if age_group != "All":
    filtered = filtered[filtered["Age Group"].astype(str) == age_group]

# -----------------------------
# KPI cards
# -----------------------------
customers = len(filtered)
orders = int(filtered["Orders"].sum())
sales = int(filtered["Sales"].sum())
aov = int(sales / orders) if orders else 0

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Customers", f"{customers:,}")
c2.metric("Total Orders", f"{orders:,}")
c3.metric("Total Sales", f"₹{sales:,.0f}")
c4.metric("Average Order Value", f"₹{aov:,.0f}")

st.divider()

# -----------------------------
# Sales by region
# -----------------------------
left, right = st.columns([1.25, 1])

with left:
    st.subheader("Sales by Region")

    region_sales = (
        filtered.groupby("Region", as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=False)
    )

    fig_region = px.bar(
        region_sales,
        x="Region",
        y="Sales",
        text="Sales",
        template="plotly_white",
        labels={"Sales": "Sales (₹)", "Region": ""}
    )
    fig_region.update_traces(
        texttemplate="₹%{text:,.0f}",
        textposition="outside"
    )
    fig_region.update_layout(
        height=390,
        margin=dict(l=10, r=10, t=20, b=10)
    )
    st.plotly_chart(fig_region, use_container_width=True)

with right:
    st.subheader("Customer Segments")

    segment_sales = (
        filtered.groupby("Segment", as_index=False)["Sales"]
        .sum()
    )

    fig_segment = px.pie(
        segment_sales,
        names="Segment",
        values="Sales",
        hole=0.58,
        template="plotly_white"
    )
    fig_segment.update_layout(
        height=390,
        margin=dict(l=10, r=10, t=20, b=10),
        legend=dict(orientation="h", y=-0.05)
    )
    st.plotly_chart(fig_segment, use_container_width=True)

# -----------------------------
# Monthly sales
# -----------------------------
st.subheader("Monthly Sales Trend")

month_order = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
]

monthly = (
    filtered.groupby("Month", as_index=False)["Sales"]
    .sum()
)
monthly["Month"] = pd.Categorical(
    monthly["Month"], categories=month_order, ordered=True
)
monthly = monthly.sort_values("Month")

fig_month = px.line(
    monthly,
    x="Month",
    y="Sales",
    markers=True,
    template="plotly_white",
    labels={"Sales": "Sales (₹)", "Month": ""}
)
fig_month.update_layout(
    height=360,
    margin=dict(l=10, r=10, t=20, b=10)
)
st.plotly_chart(fig_month, use_container_width=True)

# -----------------------------
# Age group + customer table
# -----------------------------
left, right = st.columns([1, 1.2])

with left:
    st.subheader("Sales by Age Group")

    age_sales = (
        filtered.groupby("Age Group", observed=False, as_index=False)["Sales"]
        .sum()
    )

    fig_age = px.bar(
        age_sales,
        x="Age Group",
        y="Sales",
        template="plotly_white",
        labels={"Sales": "Sales (₹)", "Age Group": ""}
    )
    fig_age.update_layout(
        height=350,
        margin=dict(l=10, r=10, t=20, b=10)
    )
    st.plotly_chart(fig_age, use_container_width=True)

with right:
    st.subheader("Filtered Customer Data")

    display_df = filtered[
        ["Customer ID", "Region", "Age", "Age Group",
         "Segment", "Orders", "Sales"]
    ].sort_values("Sales", ascending=False)

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=350
    )

st.caption(
    "Portfolio project • Simulated data created for demonstration purposes. "
    "This dashboard does not represent a real client or business."
)
