import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="Customer Analysis Dashboard",
    page_icon="📊",
    layout="wide"
)


def create_sample_data():
    np.random.seed(42)

    regions = ["North", "South", "East", "West"]
    segments = ["Premium", "Regular", "Basic"]

    n = 1000

    df = pd.DataFrame({
        "Customer ID": range(10001, 10001 + n),
        "Region": np.random.choice(regions, n),
        "Customer Segment": np.random.choice(
            segments,
            n,
            p=[0.25, 0.50, 0.25]
        ),
        "Age": np.random.randint(18, 65, n),
        "Orders": np.random.randint(1, 15, n),
        "Sales": np.random.uniform(500, 15000, n).round(2),
        "Order Date": pd.date_range(
            start="2024-01-01",
            periods=n,
            freq="12h"
        )
    })

    return df


def read_uploaded_file(uploaded_file):
    file_name = uploaded_file.name.lower()

    if file_name.endswith(".csv"):
        return pd.read_csv(uploaded_file)

    if file_name.endswith((".xlsx", ".xls")):
        return pd.read_excel(uploaded_file)

    return None


def standardize_columns(df):
    df = df.copy()

    df.columns = (
        df.columns
        .str.strip()
        .str.replace("_", " ", regex=False)
        .str.replace("-", " ", regex=False)
    )

    return df


def find_column(df, possible_names):
    normalized = {
        str(col).strip().lower(): col
        for col in df.columns
    }

    for name in possible_names:
        if name.lower() in normalized:
            return normalized[name.lower()]

    return None


st.title("Customer Analysis & Sales Dashboard")
st.caption(
    "Analyze customer behavior, sales performance, segments and regional trends."
)

st.sidebar.header("Data Source")

source = st.sidebar.radio(
    "Choose data",
    ["Use sample data", "Upload CSV / Excel"]
)

if source == "Use sample data":
    df = create_sample_data()

else:
    uploaded_file = st.sidebar.file_uploader(
        "Upload your dataset",
        type=["csv", "xlsx", "xls"]
    )

    if uploaded_file is None:
        st.info("Upload a CSV or Excel file to start the analysis.")
        st.stop()

    try:
        df = read_uploaded_file(uploaded_file)

        if df is None:
            st.error("Unsupported file format.")
            st.stop()

        df = standardize_columns(df)

    except Exception as e:
        st.error(f"Could not read the file: {e}")
        st.stop()


region_col = find_column(
    df,
    ["Region", "Area", "Location"]
)

segment_col = find_column(
    df,
    ["Customer Segment", "Segment", "Category"]
)

orders_col = find_column(
    df,
    ["Orders", "Order Count", "Order Quantity"]
)

sales_col = find_column(
    df,
    ["Sales", "Revenue", "Sales Amount", "Amount"]
)

age_col = find_column(
    df,
    ["Age", "Customer Age"]
)

date_col = find_column(
    df,
    ["Order Date", "Date", "Purchase Date"]
)


st.sidebar.header("Filters")

filtered_df = df.copy()

if region_col:
    regions = sorted(
        filtered_df[region_col]
        .dropna()
        .astype(str)
        .unique()
    )

    selected_regions = st.sidebar.multiselect(
        "Region",
        regions,
        default=regions
    )

    filtered_df = filtered_df[
        filtered_df[region_col].astype(str).isin(selected_regions)
    ]

if segment_col:
    segments = sorted(
        filtered_df[segment_col]
        .dropna()
        .astype(str)
        .unique()
    )

    selected_segments = st.sidebar.multiselect(
        "Customer Segment",
        segments,
        default=segments
    )

    filtered_df = filtered_df[
        filtered_df[segment_col].astype(str).isin(selected_segments)
    ]


if age_col:
    age_values = pd.to_numeric(
        filtered_df[age_col],
        errors="coerce"
    ).dropna()

    if not age_values.empty:
        min_age = int(age_values.min())
        max_age = int(age_values.max())

        if min_age < max_age:
            selected_age = st.sidebar.slider(
                "Age Range",
                min_age,
                max_age,
                (min_age, max_age)
            )

            filtered_df = filtered_df[
                pd.to_numeric(
                    filtered_df[age_col],
                    errors="coerce"
                ).between(
                    selected_age[0],
                    selected_age[1]
                )
            ]


st.subheader("Key Performance Indicators")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

total_records = len(filtered_df)

if orders_col:
    total_orders = pd.to_numeric(
        filtered_df[orders_col],
        errors="coerce"
    ).fillna(0).sum()
else:
    total_orders = 0

if sales_col:
    sales_values = pd.to_numeric(
        filtered_df[sales_col],
        errors="coerce"
    ).fillna(0)

    total_sales = sales_values.sum()

    if total_orders > 0:
        average_order_value = total_sales / total_orders
    else:
        average_order_value = 0
else:
    total_sales = 0
    average_order_value = 0


kpi1.metric(
    "Total Customers / Records",
    f"{total_records:,}"
)

kpi2.metric(
    "Total Orders",
    f"{total_orders:,.0f}"
)

kpi3.metric(
    "Total Sales",
    f"₹{total_sales:,.2f}"
)

kpi4.metric(
    "Average Order Value",
    f"₹{average_order_value:,.2f}"
)


st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Sales by Region")

    if region_col and sales_col:
        region_sales = (
            filtered_df
            .assign(
                _sales=pd.to_numeric(
                    filtered_df[sales_col],
                    errors="coerce"
                ).fillna(0)
            )
            .groupby(region_col)["_sales"]
            .sum()
            .reset_index()
        )

        fig = px.bar(
            region_sales,
            x=region_col,
            y="_sales",
            title="Sales Performance by Region",
            labels={"_sales": "Sales"}
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:
        st.warning(
            "Region and Sales columns are required for this chart."
        )


with col2:
    st.subheader("Customer Segments")

    if segment_col:
        segment_count = (
            filtered_df[segment_col]
            .value_counts()
            .reset_index()
        )

        segment_count.columns = [
            segment_col,
            "Customers"
        ]

        fig = px.pie(
            segment_count,
            names=segment_col,
            values="Customers",
            title="Customer Segment Distribution"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:
        st.warning(
            "A Customer Segment column is required for this chart."
        )


st.subheader("Monthly Sales Trend")

if date_col and sales_col:
    trend_df = filtered_df.copy()

    trend_df[date_col] = pd.to_datetime(
        trend_df[date_col],
        errors="coerce"
    )

    trend_df[sales_col] = pd.to_numeric(
        trend_df[sales_col],
        errors="coerce"
    )

    trend_df = trend_df.dropna(
        subset=[date_col, sales_col]
    )

    if not trend_df.empty:
        trend_df["Month"] = (
            trend_df[date_col]
            .dt.to_period("M")
            .astype(str)
        )

        monthly_sales = (
            trend_df
            .groupby("Month")[sales_col]
            .sum()
            .reset_index()
        )

        fig = px.line(
            monthly_sales,
            x="Month",
            y=sales_col,
            markers=True,
            title="Monthly Sales Trend"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:
        st.warning(
            "Valid date and sales data are required."
        )

else:
    st.info(
        "Upload data containing Date and Sales columns "
        "to view the monthly sales trend."
    )


st.subheader("Sales by Age Group")

if age_col and sales_col:
    age_df = filtered_df.copy()

    age_df[age_col] = pd.to_numeric(
        age_df[age_col],
        errors="coerce"
    )

    age_df[sales_col] = pd.to_numeric(
        age_df[sales_col],
        errors="coerce"
    )

    age_df = age_df.dropna(
        subset=[age_col, sales_col]
    )

    if not age_df.empty:
        age_df["Age Group"] = pd.cut(
            age_df[age_col],
            bins=[0, 25, 35, 45, 55, 100],
            labels=[
                "18-25",
                "26-35",
                "36-45",
                "46-55",
                "56+"
            ]
        )

        age_sales = (
            age_df
            .groupby("Age Group", observed=False)[sales_col]
            .sum()
            .reset_index()
        )

        fig = px.bar(
            age_sales,
            x="Age Group",
            y=sales_col,
            title="Sales by Age Group"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:
        st.warning("Valid age and sales data are required.")

else:
    st.info(
        "Age and Sales columns are required for this analysis."
    )


st.subheader("Filtered Customer Data")

st.dataframe(
    filtered_df,
    use_container_width=True,
    height=400
)


st.subheader("Data Summary")

summary_col1, summary_col2, summary_col3 = st.columns(3)

summary_col1.metric(
    "Rows",
    f"{len(filtered_df):,}"
)

summary_col2.metric(
    "Columns",
    f"{len(filtered_df.columns):,}"
)

summary_col3.metric(
    "Missing Values",
    f"{filtered_df.isna().sum().sum():,}"
)


st.caption(
    "Data can be analyzed using the sample dataset or your own CSV/Excel file."
)
