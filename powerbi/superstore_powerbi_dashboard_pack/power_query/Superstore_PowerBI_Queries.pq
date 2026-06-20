// Power BI Power Query M script
// Update DataFolder if you move this package.
let
    DataFolder = "C:\\Users\\risk_\\Documents\\Codex\\2026-06-21\\new-chat\\outputs\\superstore_powerbi_dashboard_pack\\data",
    LoadCsv = (FileName as text) as table =>
        Table.PromoteHeaders(
            Csv.Document(
                File.Contents(DataFolder & "\\" & FileName),
                [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
            ),
            [PromoteAllScalars=true]
        ),
    FactOrders = Table.TransformColumnTypes(LoadCsv("FactOrders.csv"), {
        {"Row ID", Int64.Type}, {"Order ID", type text}, {"DateKey", Int64.Type}, {"ShipDateKey", Int64.Type},
        {"ProductKey", Int64.Type}, {"CustomerKey", Int64.Type}, {"GeographyKey", Int64.Type}, {"ShipModeKey", Int64.Type},
        {"Sales", Currency.Type}, {"Quantity", Int64.Type}, {"Discount", Percentage.Type}, {"Profit", Currency.Type},
        {"Ship Days", Int64.Type}, {"Profit Margin", Percentage.Type}, {"Returned Flag", type logical}, {"Returned", type text},
        {"Net Sales After Returns", Currency.Type}, {"Return Sales", Currency.Type}, {"Loss Flag", type logical}, {"Discount Band", type text}
    }),
    DimProduct = Table.TransformColumnTypes(LoadCsv("DimProduct.csv"), {{"ProductKey", Int64.Type}, {"Product ID", type text}, {"Product Name", type text}, {"Category", type text}, {"Sub-Category", type text}}),
    DimCustomer = Table.TransformColumnTypes(LoadCsv("DimCustomer.csv"), {{"CustomerKey", Int64.Type}, {"Customer ID", type text}, {"Customer Name", type text}, {"Segment", type text}}),
    DimGeography = Table.TransformColumnTypes(LoadCsv("DimGeography.csv"), {{"GeographyKey", Int64.Type}, {"Country", type text}, {"City", type text}, {"State", type text}, {"Postal Code", type text}, {"Region", type text}, {"Person", type text}}),
    DimShipMode = Table.TransformColumnTypes(LoadCsv("DimShipMode.csv"), {{"ShipModeKey", Int64.Type}, {"Ship Mode", type text}}),
    DimDate = Table.TransformColumnTypes(LoadCsv("DimDate.csv"), {{"DateKey", Int64.Type}, {"Date", type date}, {"Year", Int64.Type}, {"Quarter", type text}, {"Month Number", Int64.Type}, {"Month Name", type text}, {"Year Month", type text}, {"Weekday", type text}, {"Is Weekend", type logical}})
in
    [
        FactOrders = FactOrders,
        DimProduct = DimProduct,
        DimCustomer = DimCustomer,
        DimGeography = DimGeography,
        DimShipMode = DimShipMode,
        DimDate = DimDate
    ]
