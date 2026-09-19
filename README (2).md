# KPI Tracking & Dashboard Creation — End-to-End BI Project

## Objective
Build a professional KPI tracking and interactive dashboard solution from raw e-commerce transactions. The project covers ingestion, data quality, transformation, KPI engineering, SQL, Power BI DAX, and a Streamlit interactive dashboard.

## Dataset
**Primary dataset:** UCI Machine Learning Repository — Online Retail II, a real two-year UK online-retail transaction dataset with 1,067,371 instances. The official UCI record states that it covers 01/12/2009–09/12/2011 and is licensed CC BY 4.0.

Official source: https://archive.ics.uci.edu/dataset/502/online+retail+ii
DOI: https://doi.org/10.24432/C5CG6D

The raw workbook is intentionally NOT bundled because it is ~43.5 MB and the UCI license/source should be respected. The pipeline downloads it directly from UCI.

## KPI scope
- Total Revenue / Net Revenue
- Gross Revenue
- Returns Amount
- Monthly Revenue Growth %
- Orders
- Units Sold
- Average Order Value
- Active Customers
- Repeat Customer Rate
- Revenue per Customer
- Average Items per Order
- Return Rate
- Top Products / Countries

## Important definition
This dataset contains sales transactions, not web analytics events. Therefore “customer engagement” is operationalized using transaction behavior: active customers, order frequency, repeat-customer rate, items/order, and revenue/customer. Do not present these as website clicks or sessions.

## Architecture
UCI raw XLSX → Python ingestion → cleaning/validation → KPI tables → SQLite/CSV → Power BI / Streamlit dashboard.

## Run
1. `python -m venv .venv`
2. Windows: `.venv\Scripts\activate`
3. `pip install -r requirements.txt`
4. `python src/01_download_data.py`
5. `python src/02_clean_transform.py`
6. `python src/03_build_kpis.py`
7. `python src/04_export_powerbi.py`
8. `streamlit run dashboard/app.py`

For a quick visual preview without downloading the 43.5 MB source workbook, run:
`streamlit run dashboard/app.py` and enable **Use demo preview data**.

## Power BI
Load `data/processed/fact_sales.csv`, `dim_date.csv`, `dim_product.csv`, and `dim_customer.csv`. Create a one-to-many relationship from `dim_date[Date]` to `fact_sales[InvoiceDateDate]`. Mark `dim_date` as the date table.

DAX measures are provided in `powerbi/DAX_Measures.txt`.

## Realtime/near-realtime design
The historical UCI dataset is static, so it cannot be a true live feed. The dashboard is designed to support near-real-time operation: replace the source with a database/API table, refresh the extract on a schedule, and let Streamlit/Power BI refresh the model. The KPI logic remains unchanged.
