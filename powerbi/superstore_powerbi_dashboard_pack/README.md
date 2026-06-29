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
   `C:\Users\risk_\Documents\Codex\2026-06-21\new-chat\outputs\superstore_powerbi_dashboard_pack\data`
3. In Model view, create the relationships listed in `docs/data_model.md`.
4. Mark `DimDate[Date]` as the date table.
5. Add the measures from `dax/Superstore_Measures.dax`.
6. Import the theme: View > Themes > Browse for themes > `theme/superstore_powerbi_theme.json`.
7. Build the pages using `docs/dashboard_blueprint.md`.

Note: I checked this machine and did not find Power BI Desktop installed in the usual locations, so a native `.pbix` could not be generated directly here.
