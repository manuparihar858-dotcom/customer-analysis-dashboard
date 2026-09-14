# Customer Analysis Dashboard

An interactive customer and sales analytics dashboard built with Python, Pandas, Plotly, and Streamlit.

## Features

- Upload CSV or Excel datasets
- Use simulated sample data
- Automatic detection of common Region, Segment, Orders, Sales, Revenue, Amount, and Age columns
- Dynamic KPI reporting
- Region and customer-segment filters
- Sales by region
- Customer segment analysis
- Interactive data preview

## Technologies

Python, Pandas, NumPy, Plotly, Streamlit

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Recommended Columns

For the richest dashboard experience, use columns such as:

`Region`, `Segment`, `Orders`, `Sales`, `Age`

The app also recognizes common alternatives such as `Revenue`, `Amount`, `Sales Amount`, and `Customer Segment`.

## Data Disclaimer

Sample data is simulated for portfolio demonstration. Uploaded files are analyzed by the running Streamlit application and are not stored by this project intentionally.
