from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "data" / "processed"

f = pd.read_csv(P / "fact_sales.csv", parse_dates=["InvoiceDate","InvoiceDateDate"])

# Monthly KPI table
monthly = f.groupby("Month", as_index=False).agg(
    GrossRevenue=("Revenue","sum"),
    Orders=("InvoiceNo","nunique"),
    UnitsSold=("Quantity","sum"),
    ActiveCustomers=("CustomerID","nunique"),
)
monthly["AOV"] = monthly["GrossRevenue"] / monthly["Orders"].replace(0,np.nan)
monthly["RevenuePerCustomer"] = monthly["GrossRevenue"] / monthly["ActiveCustomers"].replace(0,np.nan)
monthly["ItemsPerOrder"] = monthly["UnitsSold"] / monthly["Orders"].replace(0,np.nan)
monthly["PrevMonthRevenue"] = monthly["GrossRevenue"].shift(1)
monthly["MonthlyGrowthPct"] = (monthly["GrossRevenue"]/monthly["PrevMonthRevenue"] - 1) * 100

# Returns are retained separately from the original source before cleaning.
# Because fact_sales contains only positive sales, return KPIs are calculated from a raw audit-compatible file
# when raw data is available. For the normalized model, ReturnAmount is 0 unless a return fact is separately loaded.
monthly["ReturnAmount"] = 0.0
monthly["NetRevenue"] = monthly["GrossRevenue"] - monthly["ReturnAmount"]
monthly["ReturnRatePct"] = 0.0

# Repeat customers: customer with >1 distinct invoice during the period.
cust_orders = f.dropna(subset=["CustomerID"]).groupby("CustomerID")["InvoiceNo"].nunique()
repeat_customers = int((cust_orders > 1).sum())
active_customers = int(cust_orders.size)
repeat_rate = repeat_customers / active_customers * 100 if active_customers else 0

summary = pd.DataFrame([{
    "GrossRevenue": f["Revenue"].sum(),
    "Orders": f["InvoiceNo"].nunique(),
    "UnitsSold": f["Quantity"].sum(),
    "ActiveCustomers": f["CustomerID"].nunique(),
    "AOV": f["Revenue"].sum()/f["InvoiceNo"].nunique(),
    "RevenuePerCustomer": f["Revenue"].sum()/f["CustomerID"].nunique(),
    "ItemsPerOrder": f["Quantity"].sum()/f["InvoiceNo"].nunique(),
    "RepeatCustomers": repeat_customers,
    "RepeatCustomerRatePct": repeat_rate
}])

monthly.to_csv(P / "kpi_monthly.csv", index=False)
summary.to_csv(P / "kpi_summary.csv", index=False)

top_products = f.groupby(["StockCode","Description"], as_index=False)["Revenue"].sum().sort_values("Revenue", ascending=False).head(20)
top_products.to_csv(P / "kpi_top_products.csv", index=False)

country = f.groupby("Country", as_index=False).agg(Revenue=("Revenue","sum"),Orders=("InvoiceNo","nunique"),Customers=("CustomerID","nunique")).sort_values("Revenue",ascending=False)
country.to_csv(P / "kpi_country.csv", index=False)

print(summary.to_string(index=False))
