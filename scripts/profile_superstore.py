import pandas as pd

path = "work/Sample-Superstore.xlsx"
xl = pd.ExcelFile(path)
print("Sheets:", xl.sheet_names)

for sheet in xl.sheet_names:
    df = pd.read_excel(path, sheet_name=sheet)
    print(f"\n{sheet} {df.shape}")
    print(df.dtypes.astype(str).to_string())
    print("missing total", int(df.isna().sum().sum()))
    print("duplicates", int(df.duplicated().sum()))
    print(df.head(2).to_string())
