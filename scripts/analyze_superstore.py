import json
from pathlib import Path

import numpy as np
import pandas as pd

SRC = Path("work/Sample-Superstore.xlsx")
OUT = Path("work/superstore_analysis")
OUT.mkdir(parents=True, exist_ok=True)

orders = pd.read_excel(SRC, sheet_name="Orders")
people = pd.read_excel(SRC, sheet_name="People")
returns = pd.read_excel(SRC, sheet_name="Returns")

initial_rows = len(orders)
initial_cols = len(orders.columns)
missing_before = int(orders.isna().sum().sum())
duplicate_rows = int(orders.duplicated().sum())

orders = orders.drop_duplicates().copy()
orders["Postal Code"] = orders["Postal Code"].fillna("Unknown").astype(str).str.replace(r"\.0$", "", regex=True)
orders["Order Date"] = pd.to_datetime(orders["Order Date"])
orders["Ship Date"] = pd.to_datetime(orders["Ship Date"])
orders["Ship Days"] = (orders["Ship Date"] - orders["Order Date"]).dt.days
orders["Order Year"] = orders["Order Date"].dt.year
orders["Order Month"] = orders["Order Date"].dt.month
orders["Order Month Name"] = orders["Order Date"].dt.strftime("%b")
orders["Year Month"] = orders["Order Date"].dt.to_period("M").astype(str)
orders["Profit Margin"] = np.where(orders["Sales"] != 0, orders["Profit"] / orders["Sales"], 0)
orders["Discount Band"] = pd.cut(
    orders["Discount"],
    bins=[-0.001, 0, 0.1, 0.2, 0.4, 1.0],
    labels=["0%", "0-10%", "10-20%", "20-40%", "40%+"],
)

returns_clean = returns[["Order ID", "Returned"]].drop_duplicates(subset=["Order ID"]).copy()
returns_clean["Returned Flag"] = returns_clean["Returned"].eq("Yes")
orders = orders.merge(returns_clean[["Order ID", "Returned Flag"]], on="Order ID", how="left")
orders["Returned Flag"] = orders["Returned Flag"].fillna(False)
orders["Returned"] = np.where(orders["Returned Flag"], "Yes", "No")

orders = orders.merge(people, on="Region", how="left")
orders["Person"] = orders["Person"].fillna("Unassigned")

orders["Net Sales After Returns"] = np.where(orders["Returned Flag"], 0, orders["Sales"])
orders["Return Sales"] = np.where(orders["Returned Flag"], orders["Sales"], 0)
orders["Loss Flag"] = orders["Profit"] < 0

numeric_cols = ["Sales", "Quantity", "Discount", "Profit", "Ship Days", "Profit Margin", "Net Sales After Returns", "Return Sales"]
for col in numeric_cols:
    orders[col] = pd.to_numeric(orders[col], errors="coerce").fillna(0)

quality_rows = [
    ["Source file", str(SRC.name)],
    ["Source URL", "https://github.com/PacktPublishing/Getting-Started-with-Tableau-2019.2/blob/master/Chapter03/Sample-Superstore.xlsx"],
    ["Initial order rows", initial_rows],
    ["Initial order columns", initial_cols],
    ["Dropped duplicate order rows", duplicate_rows],
    ["Missing values before cleaning", missing_before],
    ["Missing Postal Code values filled", 11],
    ["Unique returned orders", int(returns_clean["Order ID"].nunique())],
    ["Cleaned order rows", len(orders)],
    ["Cleaned missing values", int(orders.isna().sum().sum())],
    ["Order date range", f"{orders['Order Date'].min().date()} to {orders['Order Date'].max().date()}"],
]

def money(x):
    return float(round(x, 2))

def pct(x):
    return float(round(x, 4))

overview = {
    "total_sales": money(orders["Sales"].sum()),
    "total_profit": money(orders["Profit"].sum()),
    "profit_margin": pct(orders["Profit"].sum() / orders["Sales"].sum()),
    "orders": int(orders["Order ID"].nunique()),
    "customers": int(orders["Customer ID"].nunique()),
    "return_rate": pct(orders.loc[orders["Returned Flag"], "Order ID"].nunique() / orders["Order ID"].nunique()),
    "avg_ship_days": float(round(orders["Ship Days"].mean(), 2)),
    "loss_order_lines": int(orders["Loss Flag"].sum()),
}

monthly = (
    orders.groupby("Year Month", as_index=False)
    .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique"), Return_Sales=("Return Sales", "sum"))
)
monthly["Profit Margin"] = monthly["Profit"] / monthly["Sales"]

region = (
    orders.groupby(["Region", "Person"], as_index=False)
    .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique"), Customers=("Customer ID", "nunique"), Return_Sales=("Return Sales", "sum"))
)
region["Profit Margin"] = region["Profit"] / region["Sales"]
region["Return Sales %"] = region["Return_Sales"] / region["Sales"]

category = (
    orders.groupby(["Category", "Sub-Category"], as_index=False)
    .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Quantity=("Quantity", "sum"), Orders=("Order ID", "nunique"), Avg_Discount=("Discount", "mean"), Return_Sales=("Return Sales", "sum"))
)
category["Profit Margin"] = category["Profit"] / category["Sales"]

segment = (
    orders.groupby("Segment", as_index=False)
    .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique"), Customers=("Customer ID", "nunique"))
)
segment["Profit Margin"] = segment["Profit"] / segment["Sales"]

state = (
    orders.groupby(["State", "Region"], as_index=False)
    .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique"), Avg_Discount=("Discount", "mean"))
)
state["Profit Margin"] = state["Profit"] / state["Sales"]

top_products = (
    orders.groupby(["Product Name", "Category", "Sub-Category"], as_index=False)
    .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Quantity=("Quantity", "sum"), Orders=("Order ID", "nunique"))
    .sort_values("Sales", ascending=False)
    .head(25)
)
top_customers = (
    orders.groupby(["Customer Name", "Segment"], as_index=False)
    .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique"))
    .sort_values("Sales", ascending=False)
    .head(25)
)
discount = (
    orders.groupby("Discount Band", observed=False, as_index=False)
    .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique"), Avg_Discount=("Discount", "mean"))
)
discount["Profit Margin"] = discount["Profit"] / discount["Sales"]

insights = []
best_region = region.sort_values("Profit", ascending=False).iloc[0]
weak_subcat = category.sort_values("Profit").iloc[0]
best_subcat = category.sort_values("Profit", ascending=False).iloc[0]
worst_state = state.sort_values("Profit").iloc[0]
high_discount = discount.sort_values("Profit Margin").iloc[0]
insights.append(["Best profit region", f"{best_region['Region']} generated ${best_region['Profit']:,.0f} profit on ${best_region['Sales']:,.0f} sales."])
insights.append(["Strongest sub-category", f"{best_subcat['Sub-Category']} led profit with ${best_subcat['Profit']:,.0f}."])
insights.append(["Largest profit drag", f"{weak_subcat['Sub-Category']} lost ${abs(weak_subcat['Profit']):,.0f}, despite ${weak_subcat['Sales']:,.0f} in sales."])
insights.append(["Worst state profitability", f"{worst_state['State']} had ${worst_state['Profit']:,.0f} profit and {worst_state['Profit Margin']:.1%} margin."])
insights.append(["Discount risk", f"The {high_discount['Discount Band']} discount band had the weakest margin at {high_discount['Profit Margin']:.1%}."])
insights.append(["Returns", f"Returned orders represent {overview['return_rate']:.1%} of unique orders, with ${orders['Return Sales'].sum():,.0f} in returned line sales."])

def write_csv(df, name):
    path = OUT / name
    df.to_csv(path, index=False)
    json_path = path.with_suffix(".json")
    json_path.write_text(df.to_json(orient="records", date_format="iso"), encoding="utf-8")
    return str(path)

write_csv(orders, "cleaned_orders.csv")
write_csv(monthly, "monthly_summary.csv")
write_csv(region.sort_values("Sales", ascending=False), "region_summary.csv")
write_csv(category.sort_values("Sales", ascending=False), "category_summary.csv")
write_csv(segment.sort_values("Sales", ascending=False), "segment_summary.csv")
write_csv(state.sort_values("Profit", ascending=False), "state_summary.csv")
write_csv(top_products, "top_products.csv")
write_csv(top_customers, "top_customers.csv")
write_csv(discount, "discount_summary.csv")
pd.DataFrame(quality_rows, columns=["Check", "Result"]).to_csv(OUT / "data_quality.csv", index=False)
pd.DataFrame(insights, columns=["Insight", "Detail"]).to_csv(OUT / "insights.csv", index=False)
pd.DataFrame(quality_rows, columns=["Check", "Result"]).to_json(OUT / "data_quality.json", orient="records")
pd.DataFrame(insights, columns=["Insight", "Detail"]).to_json(OUT / "insights.json", orient="records")

summary = {
    "overview": overview,
    "quality": quality_rows,
    "insights": insights,
    "source_url": "https://github.com/PacktPublishing/Getting-Started-with-Tableau-2019.2/blob/master/Chapter03/Sample-Superstore.xlsx",
}
(OUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

print(json.dumps(summary, indent=2))
