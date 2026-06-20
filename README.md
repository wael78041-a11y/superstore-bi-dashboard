# Superstore BI Dashboard Project

End-to-end business intelligence project built from the public Sample Superstore dataset.

## What Is Included

- `dashboards/superstore_sales_analysis_dashboard.xlsx`  
  Excel workbook with cleaned data, analysis sheets, KPI dashboard, and charts.

- `dashboards/superstore_animated_dashboard.html`  
  Interactive animated dashboard that opens directly in a browser. It includes filters, animated KPI counters, charts, page navigation, and a profit heatmap.

- `dashboards/superstore_powerbi_preview.html`  
  Lightweight Power BI-style HTML preview.

- `powerbi/superstore_powerbi_dashboard_pack/`  
  Power BI-ready package with star-schema CSV files, Power Query scripts, DAX measures, theme JSON, and dashboard blueprint.

- `data/raw/Sample-Superstore.xlsx`  
  Original source dataset.

- `data/processed/`  
  Cleaned and summarized CSV outputs used by the dashboards.

- `scripts/`  
  Python scripts used to profile, clean, analyze, and generate the dashboard assets.

## Key Metrics

- Total sales: approximately `$2.30M`
- Total profit: approximately `$286K`
- Profit margin: approximately `12.5%`
- Unique orders: `5,009`
- Customers: `793`
- Return rate: approximately `5.9%`

## How To View

Open this file in your browser:

```text
dashboards/superstore_animated_dashboard.html
```

Open this workbook in Excel:

```text
dashboards/superstore_sales_analysis_dashboard.xlsx
```

## How To Use In Power BI

1. Open Power BI Desktop.
2. Import CSV files from:

```text
powerbi/superstore_powerbi_dashboard_pack/data/
```

3. Create the relationships listed in:

```text
docs/data_model.md
```

4. Add the measures from:

```text
powerbi/superstore_powerbi_dashboard_pack/dax/Superstore_Measures.dax
```

5. Import the theme:

```text
powerbi/superstore_powerbi_dashboard_pack/theme/superstore_powerbi_theme.json
```

6. Build the report pages using:

```text
docs/dashboard_blueprint.md
```

## Source

Dataset: Sample Superstore  
Source URL: https://github.com/PacktPublishing/Getting-Started-with-Tableau-2019.2/blob/master/Chapter03/Sample-Superstore.xlsx

## Notes

Power BI Desktop was not available in the local environment when this project was generated, so the repository includes a Power BI-ready build pack rather than a native `.pbix` file.
