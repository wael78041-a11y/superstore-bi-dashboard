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
