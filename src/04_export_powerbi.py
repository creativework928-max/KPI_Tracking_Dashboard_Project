from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "data" / "processed"

# Power BI-friendly long-format KPI table.
monthly = pd.read_csv(P / "kpi_monthly.csv")
long = monthly.melt(
    id_vars=["Month"],
    value_vars=["GrossRevenue","Orders","UnitsSold","ActiveCustomers","AOV","RevenuePerCustomer","ItemsPerOrder","MonthlyGrowthPct"],
    var_name="KPI",
    value_name="Value"
)
long.to_csv(P / "powerbi_kpi_long.csv", index=False)
print("Power BI export ready.")
