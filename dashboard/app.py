import time
from pathlib import Path
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
PREVIEW = ROOT / "preview" / "demo_transactions.csv"

st.set_page_config(page_title="Executive KPI Command Center", page_icon="📊", layout="wide")

st.markdown("""
<style>
.main {background:#F6F8FB;}
.kpi-card {padding:18px;border-radius:14px;background:#FFFFFF;border:1px solid #E5E7EB;box-shadow:0 2px 10px rgba(0,0,0,.04);}
.kpi-label {font-size:13px;color:#64748B;font-weight:600;}
.kpi-value {font-size:28px;font-weight:800;color:#0F172A;}
.kpi-delta {font-size:12px;color:#2563EB;}
</style>
""", unsafe_allow_html=True)

st.title("Executive KPI Command Center")
st.caption("Revenue, growth, customer engagement and order-performance monitoring")

with st.sidebar:
    st.header("Controls")
    demo_mode = st.toggle("Use demo preview data", value=not (PROCESSED/"fact_sales.csv").exists())
    refresh = st.slider("Auto-refresh (seconds)", 0, 300, 0, 30)
    st.info("For production near-real-time use, replace the file layer with a database/API source.")

@st.cache_data(ttl=60)
def load_data(demo=False):
    path = PREVIEW if demo else PROCESSED/"fact_sales.csv"
    df = pd.read_csv(path, parse_dates=["InvoiceDate"])
    df["Revenue"] = df["Quantity"] * df["UnitPrice"]
    df["IsReturn"] = df["Quantity"] < 0
    df["Month"] = df["InvoiceDate"].dt.to_period("M").astype(str)
    return df

df = load_data(demo_mode)

min_date, max_date = df["InvoiceDate"].min().date(), df["InvoiceDate"].max().date()
d1, d2 = st.date_input("Date range", (min_date, max_date), min_value=min_date, max_value=max_date)
f = df[(df["InvoiceDate"].dt.date >= d1) & (df["InvoiceDate"].dt.date <= d2)].copy()

sales = f[f["Quantity"] > 0].copy()
returns = f[f["Quantity"] < 0].copy()
gross = sales["Revenue"].sum()
return_amt = abs(returns["Revenue"].sum())
net = gross - return_amt
orders = sales["InvoiceNo"].nunique()
customers = sales["CustomerID"].nunique()
aov = gross/orders if orders else 0
repeat = sales.dropna(subset=["CustomerID"]).groupby("CustomerID")["InvoiceNo"].nunique()
repeat_rate = ((repeat > 1).mean()*100) if len(repeat) else 0

cols = st.columns(6)
cards = [
    ("Net Revenue", f"£{net:,.0f}"),
    ("Gross Revenue", f"£{gross:,.0f}"),
    ("Orders", f"{orders:,.0f}"),
    ("Active Customers", f"{customers:,.0f}"),
    ("AOV", f"£{aov:,.2f}"),
    ("Repeat Rate", f"{repeat_rate:.1f}%"),
]
for c,(label,val) in zip(cols,cards):
    c.markdown(f'<div class="kpi-card"><div class="kpi-label">{label}</div><div class="kpi-value">{val}</div></div>', unsafe_allow_html=True)

monthly = sales.groupby("Month", as_index=False).agg(Revenue=("Revenue","sum"), Orders=("InvoiceNo","nunique"), Customers=("CustomerID","nunique"))
monthly["GrowthPct"] = monthly["Revenue"].pct_change()*100

fig = make_subplots(rows=1, cols=2, subplot_titles=("Monthly Revenue","Monthly Growth %"))
fig.add_trace(go.Scatter(x=monthly["Month"], y=monthly["Revenue"], mode="lines+markers", name="Revenue"), row=1,col=1)
fig.add_trace(go.Bar(x=monthly["Month"], y=monthly["GrowthPct"], name="Growth"), row=1,col=2)
fig.update_layout(height=420, margin=dict(l=20,r=20,t=60,b=20), template="plotly_white", legend=dict(orientation="h"))
st.plotly_chart(fig, use_container_width=True)

left,right = st.columns(2)
with left:
    top = sales.groupby("Description", as_index=False)["Revenue"].sum().nlargest(10,"Revenue").sort_values("Revenue")
    fig2 = go.Figure(go.Bar(x=top["Revenue"], y=top["Description"], orientation="h"))
    fig2.update_layout(title="Top 10 Products by Revenue", template="plotly_white", height=450, margin=dict(l=10,r=10,t=50,b=10))
    st.plotly_chart(fig2, use_container_width=True)
with right:
    country = sales.groupby("Country", as_index=False)["Revenue"].sum().nlargest(10,"Revenue").sort_values("Revenue")
    fig3 = go.Figure(go.Bar(x=country["Revenue"], y=country["Country"], orientation="h"))
    fig3.update_layout(title="Top Countries by Revenue", template="plotly_white", height=450, margin=dict(l=10,r=10,t=50,b=10))
    st.plotly_chart(fig3, use_container_width=True)

st.subheader("KPI Table")
show = monthly.copy()
st.dataframe(show.style.format({"Revenue":"£{:,.0f}","GrowthPct":"{:.1f}%"}), use_container_width=True)

if refresh:
    time.sleep(refresh)
    st.rerun()
