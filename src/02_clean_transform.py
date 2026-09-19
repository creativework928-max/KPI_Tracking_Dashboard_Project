from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

xlsx = RAW / "online_retail_II.xlsx"
if not xlsx.exists():
    raise FileNotFoundError("Run src/01_download_data.py first.")

# UCI workbook has two yearly sheets.
xls = pd.ExcelFile(xlsx)
frames = [pd.read_excel(xlsx, sheet_name=s) for s in xls.sheet_names]
df = pd.concat(frames, ignore_index=True)

df.columns = ["InvoiceNo","StockCode","Description","Quantity","InvoiceDate","UnitPrice","CustomerID","Country"]
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
df["InvoiceNo"] = df["InvoiceNo"].astype(str).str.strip()
df["StockCode"] = df["StockCode"].astype(str).str.strip()
df["Description"] = df["Description"].astype("string").str.strip()
df["Country"] = df["Country"].astype("string").str.strip()
df["CustomerID"] = pd.to_numeric(df["CustomerID"], errors="coerce")
df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
df["UnitPrice"] = pd.to_numeric(df["UnitPrice"], errors="coerce")

# Raw audit
audit = {
    "raw_rows": len(df),
    "duplicate_rows": int(df.duplicated().sum()),
    "missing_customer_id": int(df["CustomerID"].isna().sum()),
    "cancellation_rows": int(df["InvoiceNo"].str.upper().str.startswith("C").sum()),
    "negative_quantity_rows": int((df["Quantity"] < 0).sum()),
    "zero_price_rows": int((df["UnitPrice"] <= 0).sum()),
}
pd.DataFrame([audit]).to_csv(OUT / "data_quality_audit.csv", index=False)

# Clean revenue grain: valid product sale lines only.
clean = df.drop_duplicates().copy()
clean = clean[
    clean["InvoiceDate"].notna()
    & clean["Quantity"].notna()
    & clean["UnitPrice"].notna()
    & (clean["Quantity"] > 0)
    & (clean["UnitPrice"] > 0)
].copy()

# Remove non-product service/adjustment stock codes.
non_product = {"POST","D","M","DOT","BANK CHARGES","TEST001","S","AMAZONFEE","DCGS","DCGSSBOY"}
clean = clean[~clean["StockCode"].str.upper().isin(non_product)].copy()

clean["Revenue"] = clean["Quantity"] * clean["UnitPrice"]
clean["InvoiceDateDate"] = clean["InvoiceDate"].dt.normalize()
clean["Year"] = clean["InvoiceDate"].dt.year
clean["MonthNo"] = clean["InvoiceDate"].dt.month
clean["Month"] = clean["InvoiceDate"].dt.to_period("M").astype(str)
clean["Quarter"] = clean["InvoiceDate"].dt.to_period("Q").astype(str)
clean["IsRepeatEligible"] = clean["CustomerID"].notna()

# Fact
fact_cols = ["InvoiceNo","StockCode","Description","Quantity","UnitPrice","InvoiceDate",
             "InvoiceDateDate","CustomerID","Country","Revenue","Year","MonthNo","Month","Quarter"]
clean[fact_cols].to_csv(OUT / "fact_sales.csv", index=False)

# Dimensions
dates = pd.DataFrame({"Date": pd.date_range(clean["InvoiceDateDate"].min(), clean["InvoiceDateDate"].max(), freq="D")})
dates["Year"] = dates["Date"].dt.year
dates["MonthNo"] = dates["Date"].dt.month
dates["MonthName"] = dates["Date"].dt.strftime("%B")
dates["YearMonth"] = dates["Date"].dt.to_period("M").astype(str)
dates["Quarter"] = dates["Date"].dt.to_period("Q").astype(str)
dates.to_csv(OUT / "dim_date.csv", index=False)

products = clean[["StockCode","Description"]].drop_duplicates("StockCode").sort_values("StockCode")
products.to_csv(OUT / "dim_product.csv", index=False)

customers = clean[clean["CustomerID"].notna()][["CustomerID","Country"]].drop_duplicates()
customers = customers.sort_values(["CustomerID","Country"]).drop_duplicates("CustomerID")
customers.to_csv(OUT / "dim_customer.csv", index=False)

print("Rows after cleaning:", len(clean))
print("Net revenue:", round(clean["Revenue"].sum(),2))
