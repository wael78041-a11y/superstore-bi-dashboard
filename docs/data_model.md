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
