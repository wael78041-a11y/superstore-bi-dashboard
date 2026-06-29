from pathlib import Path
import json
import shutil
import zipfile

import pandas as pd

ROOT = Path.cwd()
ANALYSIS = ROOT / "work" / "superstore_analysis"
OUT = ROOT / "outputs" / "superstore_powerbi_dashboard_pack"
DATA = OUT / "data"
DOCS = OUT / "docs"
PQ = OUT / "power_query"
DAX = OUT / "dax"
THEME = OUT / "theme"

if OUT.exists():
    shutil.rmtree(OUT)
for p in [DATA, DOCS, PQ, DAX, THEME]:
    p.mkdir(parents=True, exist_ok=True)

orders = pd.read_csv(ANALYSIS / "cleaned_orders.csv", parse_dates=["Order Date", "Ship Date"])

orders["DateKey"] = orders["Order Date"].dt.strftime("%Y%m%d").astype(int)
orders["ShipDateKey"] = orders["Ship Date"].dt.strftime("%Y%m%d").astype(int)
orders["ProductKey"] = pd.factorize(orders["Product ID"])[0] + 1
orders["CustomerKey"] = pd.factorize(orders["Customer ID"])[0] + 1
geo_cols = ["Country", "City", "State", "Postal Code", "Region"]
orders["GeographyKey"] = pd.factorize(orders[geo_cols].astype(str).agg("|".join, axis=1))[0] + 1
orders["ShipModeKey"] = pd.factorize(orders["Ship Mode"])[0] + 1

dim_product = (
    orders[["ProductKey", "Product ID", "Product Name", "Category", "Sub-Category"]]
    .drop_duplicates("ProductKey")
    .sort_values("ProductKey")
)
dim_customer = (
    orders[["CustomerKey", "Customer ID", "Customer Name", "Segment"]]
    .drop_duplicates("CustomerKey")
    .sort_values("CustomerKey")
)
dim_geo = (
    orders[["GeographyKey", *geo_cols, "Person"]]
    .drop_duplicates("GeographyKey")
    .sort_values("GeographyKey")
)
dim_ship = orders[["ShipModeKey", "Ship Mode"]].drop_duplicates("ShipModeKey").sort_values("ShipModeKey")

date_min = min(orders["Order Date"].min(), orders["Ship Date"].min())
date_max = max(orders["Order Date"].max(), orders["Ship Date"].max())
dates = pd.DataFrame({"Date": pd.date_range(date_min, date_max, freq="D")})
dates["DateKey"] = dates["Date"].dt.strftime("%Y%m%d").astype(int)
dates["Year"] = dates["Date"].dt.year
dates["Quarter"] = "Q" + dates["Date"].dt.quarter.astype(str)
dates["Month Number"] = dates["Date"].dt.month
dates["Month Name"] = dates["Date"].dt.strftime("%b")
dates["Year Month"] = dates["Date"].dt.strftime("%Y-%m")
dates["Weekday"] = dates["Date"].dt.strftime("%a")
dates["Is Weekend"] = dates["Date"].dt.weekday >= 5
dim_date = dates[["DateKey", "Date", "Year", "Quarter", "Month Number", "Month Name", "Year Month", "Weekday", "Is Weekend"]]

fact_cols = [
    "Row ID",
    "Order ID",
    "DateKey",
    "ShipDateKey",
    "ProductKey",
    "CustomerKey",
    "GeographyKey",
    "ShipModeKey",
    "Sales",
    "Quantity",
    "Discount",
    "Profit",
    "Ship Days",
    "Profit Margin",
    "Returned Flag",
    "Returned",
    "Net Sales After Returns",
    "Return Sales",
    "Loss Flag",
    "Discount Band",
]
fact_orders = orders[fact_cols].sort_values("Row ID")

for df in [fact_orders, dim_product, dim_customer, dim_geo, dim_ship, dim_date]:
    for col in df.select_dtypes(include=["datetime64[ns]"]).columns:
        df[col] = df[col].dt.strftime("%Y-%m-%d")

tables = {
    "FactOrders.csv": fact_orders,
    "DimProduct.csv": dim_product,
    "DimCustomer.csv": dim_customer,
    "DimGeography.csv": dim_geo,
    "DimShipMode.csv": dim_ship,
    "DimDate.csv": dim_date,
}
for name, df in tables.items():
    df.to_csv(DATA / name, index=False, encoding="utf-8-sig")

theme = {
    "name": "Superstore Executive Teal",
    "dataColors": ["#0F766E", "#2563EB", "#F59E0B", "#16A34A", "#DC2626", "#7C3AED", "#0891B2", "#64748B"],
    "background": "#F8FAFC",
    "foreground": "#1F2937",
    "tableAccent": "#0F766E",
    "visualStyles": {
        "*": {
            "*": {
                "title": [{"fontFace": "Aptos Display", "fontSize": 12, "color": {"solid": {"color": "#1F2937"}}}],
                "labels": [{"fontFace": "Aptos", "color": {"solid": {"color": "#1F2937"}}}]
            }
        }
    }
}
(THEME / "superstore_powerbi_theme.json").write_text(json.dumps(theme, indent=2), encoding="utf-8")

data_folder = str(DATA).replace("\\", "\\\\")
pq_text = """
// Power BI Power Query M script
// Update DataFolder if you move this package.
let
    DataFolder = "__DATA_FOLDER__",
    LoadCsv = (FileName as text) as table =>
        Table.PromoteHeaders(
            Csv.Document(
                File.Contents(DataFolder & "\\\\" & FileName),
                [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
            ),
            [PromoteAllScalars=true]
        ),
    FactOrders = Table.TransformColumnTypes(LoadCsv("FactOrders.csv"), {{
        {{"Row ID", Int64.Type}}, {{"Order ID", type text}}, {{"DateKey", Int64.Type}}, {{"ShipDateKey", Int64.Type}},
        {{"ProductKey", Int64.Type}}, {{"CustomerKey", Int64.Type}}, {{"GeographyKey", Int64.Type}}, {{"ShipModeKey", Int64.Type}},
        {{"Sales", Currency.Type}}, {{"Quantity", Int64.Type}}, {{"Discount", Percentage.Type}}, {{"Profit", Currency.Type}},
        {{"Ship Days", Int64.Type}}, {{"Profit Margin", Percentage.Type}}, {{"Returned Flag", type logical}}, {{"Returned", type text}},
        {{"Net Sales After Returns", Currency.Type}}, {{"Return Sales", Currency.Type}}, {{"Loss Flag", type logical}}, {{"Discount Band", type text}}
    }}),
    DimProduct = Table.TransformColumnTypes(LoadCsv("DimProduct.csv"), {{{"ProductKey", Int64.Type}}, {{"Product ID", type text}}, {{"Product Name", type text}}, {{"Category", type text}}, {{"Sub-Category", type text}}}}),
    DimCustomer = Table.TransformColumnTypes(LoadCsv("DimCustomer.csv"), {{{"CustomerKey", Int64.Type}}, {{"Customer ID", type text}}, {{"Customer Name", type text}}, {{"Segment", type text}}}}),
    DimGeography = Table.TransformColumnTypes(LoadCsv("DimGeography.csv"), {{{"GeographyKey", Int64.Type}}, {{"Country", type text}}, {{"City", type text}}, {{"State", type text}}, {{"Postal Code", type text}}, {{"Region", type text}}, {{"Person", type text}}}}),
    DimShipMode = Table.TransformColumnTypes(LoadCsv("DimShipMode.csv"), {{{"ShipModeKey", Int64.Type}}, {{"Ship Mode", type text}}}),
    DimDate = Table.TransformColumnTypes(LoadCsv("DimDate.csv"), {{{"DateKey", Int64.Type}}, {{"Date", type date}}, {{"Year", Int64.Type}}, {{"Quarter", type text}}, {{"Month Number", Int64.Type}}, {{"Month Name", type text}}, {{"Year Month", type text}}, {{"Weekday", type text}}, {{"Is Weekend", type logical}}})
in
    [
        FactOrders = FactOrders,
        DimProduct = DimProduct,
        DimCustomer = DimCustomer,
        DimGeography = DimGeography,
        DimShipMode = DimShipMode,
        DimDate = DimDate
    ]
"""
pq_text = pq_text.replace("__DATA_FOLDER__", data_folder)
pq_text = pq_text.replace("{{", "{").replace("}}", "}")
(PQ / "Superstore_PowerBI_Queries.pq").write_text(pq_text.strip() + "\n", encoding="utf-8")

single_query_specs = {
    "FactOrders.pq": ("FactOrders.csv", """{
        {"Row ID", Int64.Type}, {"Order ID", type text}, {"DateKey", Int64.Type}, {"ShipDateKey", Int64.Type},
        {"ProductKey", Int64.Type}, {"CustomerKey", Int64.Type}, {"GeographyKey", Int64.Type}, {"ShipModeKey", Int64.Type},
        {"Sales", Currency.Type}, {"Quantity", Int64.Type}, {"Discount", Percentage.Type}, {"Profit", Currency.Type},
        {"Ship Days", Int64.Type}, {"Profit Margin", Percentage.Type}, {"Returned Flag", type logical}, {"Returned", type text},
        {"Net Sales After Returns", Currency.Type}, {"Return Sales", Currency.Type}, {"Loss Flag", type logical}, {"Discount Band", type text}
    }"""),
    "DimProduct.pq": ("DimProduct.csv", '{{"ProductKey", Int64.Type}, {"Product ID", type text}, {"Product Name", type text}, {"Category", type text}, {"Sub-Category", type text}}'),
    "DimCustomer.pq": ("DimCustomer.csv", '{{"CustomerKey", Int64.Type}, {"Customer ID", type text}, {"Customer Name", type text}, {"Segment", type text}}'),
    "DimGeography.pq": ("DimGeography.csv", '{{"GeographyKey", Int64.Type}, {"Country", type text}, {"City", type text}, {"State", type text}, {"Postal Code", type text}, {"Region", type text}, {"Person", type text}}'),
    "DimShipMode.pq": ("DimShipMode.csv", '{{"ShipModeKey", Int64.Type}, {"Ship Mode", type text}}'),
    "DimDate.pq": ("DimDate.csv", '{{"DateKey", Int64.Type}, {"Date", type date}, {"Year", Int64.Type}, {"Quarter", type text}, {"Month Number", Int64.Type}, {"Month Name", type text}, {"Year Month", type text}, {"Weekday", type text}, {"Is Weekend", type logical}}'),
}

queries_dir = PQ / "separate_queries"
queries_dir.mkdir(exist_ok=True)
for file_name, (csv_name, type_block) in single_query_specs.items():
    query = f"""
let
    DataFolder = "{data_folder}",
    Source = Csv.Document(File.Contents(DataFolder & "\\\\{csv_name}"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangedTypes = Table.TransformColumnTypes(PromotedHeaders, {type_block})
in
    ChangedTypes
"""
    (queries_dir / file_name).write_text(query.strip() + "\n", encoding="utf-8")

dax_text = """
-- Core measures
Total Sales = SUM ( FactOrders[Sales] )
Total Profit = SUM ( FactOrders[Profit] )
Total Quantity = SUM ( FactOrders[Quantity] )
Total Orders = DISTINCTCOUNT ( FactOrders[Order ID] )
Total Customers = DISTINCTCOUNT ( DimCustomer[Customer ID] )
Profit Margin % = DIVIDE ( [Total Profit], [Total Sales] )
Average Discount % = AVERAGE ( FactOrders[Discount] )
Average Ship Days = AVERAGE ( FactOrders[Ship Days] )

-- Returns and risk
Returned Orders = CALCULATE ( DISTINCTCOUNT ( FactOrders[Order ID] ), FactOrders[Returned Flag] = TRUE () )
Return Rate % = DIVIDE ( [Returned Orders], [Total Orders] )
Return Sales = SUM ( FactOrders[Return Sales] )
Net Sales After Returns = SUM ( FactOrders[Net Sales After Returns] )
Loss Lines = CALCULATE ( COUNTROWS ( FactOrders ), FactOrders[Loss Flag] = TRUE () )
Loss Sales = CALCULATE ( [Total Sales], FactOrders[Loss Flag] = TRUE () )

-- Time intelligence
Sales YTD = TOTALYTD ( [Total Sales], DimDate[Date] )
Profit YTD = TOTALYTD ( [Total Profit], DimDate[Date] )
Sales LY = CALCULATE ( [Total Sales], SAMEPERIODLASTYEAR ( DimDate[Date] ) )
Profit LY = CALCULATE ( [Total Profit], SAMEPERIODLASTYEAR ( DimDate[Date] ) )
Sales YoY % = DIVIDE ( [Total Sales] - [Sales LY], [Sales LY] )
Profit YoY % = DIVIDE ( [Total Profit] - [Profit LY], [Profit LY] )

-- Ranking
Product Rank by Sales = RANKX ( ALLSELECTED ( DimProduct[Product Name] ), [Total Sales], , DESC, Dense )
Customer Rank by Sales = RANKX ( ALLSELECTED ( DimCustomer[Customer Name] ), [Total Sales], , DESC, Dense )
State Rank by Profit = RANKX ( ALLSELECTED ( DimGeography[State] ), [Total Profit], , ASC, Dense )

-- Dashboard labels
Sales Label = FORMAT ( [Total Sales], "$#,0" )
Profit Label = FORMAT ( [Total Profit], "$#,0" )
Margin Label = FORMAT ( [Profit Margin %], "0.0%" )
Return Rate Label = FORMAT ( [Return Rate %], "0.0%" )
"""
(DAX / "Superstore_Measures.dax").write_text(dax_text.strip() + "\n", encoding="utf-8")

model_doc = """
# Power BI Data Model

Use these relationships in Model view:

| From table | From column | To table | To column | Cardinality | Cross-filter |
|---|---|---|---|---|---|
| FactOrders | DateKey | DimDate | DateKey | Many-to-one | Single |
| FactOrders | ShipDateKey | DimDate | DateKey | Many-to-one inactive | Single |
| FactOrders | ProductKey | DimProduct | ProductKey | Many-to-one | Single |
| FactOrders | CustomerKey | DimCustomer | CustomerKey | Many-to-one | Single |
| FactOrders | GeographyKey | DimGeography | GeographyKey | Many-to-one | Single |
| FactOrders | ShipModeKey | DimShipMode | ShipModeKey | Many-to-one | Single |

Recommended formatting:

- Currency: `Total Sales`, `Total Profit`, `Return Sales`, `Net Sales After Returns`, `Loss Sales`.
- Percentage: `Profit Margin %`, `Average Discount %`, `Return Rate %`, YoY measures.
- Sort `DimDate[Month Name]` by `DimDate[Month Number]`.
- Mark `DimDate` as the date table using `DimDate[Date]`.
"""
(DOCS / "data_model.md").write_text(model_doc.strip() + "\n", encoding="utf-8")

dashboard_doc = """
# Power BI Dashboard Blueprint

## Page 1: Executive Overview

Slicers: Year, Region, Segment, Category.

Cards:
- Total Sales
- Total Profit
- Profit Margin %
- Total Orders
- Total Customers
- Return Rate %

Visuals:
- Line chart: Axis `DimDate[Year Month]`; Values `Total Sales`, `Total Profit`.
- Clustered column chart: Axis `DimGeography[Region]`; Values `Total Sales`, `Total Profit`.
- Bar chart: Axis `DimProduct[Sub-Category]`; Values `Total Sales`, `Total Profit`; sort by `Total Sales` descending.
- Table: State, Region, Total Sales, Total Profit, Profit Margin %; sort Total Profit ascending.

## Page 2: Product and Discount Performance

Slicers: Category, Sub-Category, Discount Band.

Visuals:
- Matrix: Category > Sub-Category with Total Sales, Total Profit, Profit Margin %, Average Discount %.
- Scatter: X Average Discount %, Y Profit Margin %, Size Total Sales, Details Sub-Category.
- Bar chart: Discount Band by Total Sales and Total Profit.
- Top N table: Product Name, Category, Sub-Category, Total Sales, Total Profit, Product Rank by Sales.

## Page 3: Geography and Returns

Slicers: Year, Region, Ship Mode.

Visuals:
- Filled map or shape map: State colored by Total Profit and sized by Total Sales.
- Bar chart: Return Sales by Region.
- Table: State, City, Total Sales, Total Profit, Return Rate %, Average Ship Days.
- Card group: Returned Orders, Return Sales, Average Ship Days.

## Page 4: Customers

Slicers: Segment, Region, Year.

Visuals:
- Bar chart: Top 15 customers by Total Sales.
- Scatter: Total Sales vs Total Profit, Details Customer Name, Legend Segment.
- Matrix: Segment > Customer Name with Orders, Sales, Profit, Margin.
"""
(DOCS / "dashboard_blueprint.md").write_text(dashboard_doc.strip() + "\n", encoding="utf-8")

readme = f"""
# Superstore Power BI Dashboard Pack

This pack is built from the public Sample Superstore dataset and the cleaned analysis already prepared in this workspace.

## Contents

- `data/`: Power BI-ready star-schema CSV files.
- `power_query/Superstore_PowerBI_Queries.pq`: M script with typed queries.
- `dax/Superstore_Measures.dax`: measures for sales, profit, margin, returns, time intelligence, and ranking.
- `theme/superstore_powerbi_theme.json`: Power BI theme.
- `docs/data_model.md`: relationship model.
- `docs/dashboard_blueprint.md`: dashboard pages and visuals.

## Fast Build in Power BI Desktop

1. Open Power BI Desktop.
2. Get Data > Text/CSV and load every CSV from:
   `{DATA}`
3. In Model view, create the relationships listed in `docs/data_model.md`.
4. Mark `DimDate[Date]` as the date table.
5. Add the measures from `dax/Superstore_Measures.dax`.
6. Import the theme: View > Themes > Browse for themes > `theme/superstore_powerbi_theme.json`.
7. Build the pages using `docs/dashboard_blueprint.md`.

Note: I checked this machine and did not find Power BI Desktop installed in the usual locations, so a native `.pbix` could not be generated directly here.
"""
(OUT / "README.md").write_text(readme.strip() + "\n", encoding="utf-8")

zip_path = ROOT / "outputs" / "superstore_powerbi_dashboard_pack.zip"
manifest = {
    "output_folder": str(OUT),
    "zip": str(zip_path),
    "tables": {name: {"rows": int(len(df)), "columns": list(df.columns)} for name, df in tables.items()},
}
(OUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
if zip_path.exists():
    zip_path.unlink()
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    for file in OUT.rglob("*"):
        z.write(file, file.relative_to(OUT.parent))
print(json.dumps(manifest, indent=2))
