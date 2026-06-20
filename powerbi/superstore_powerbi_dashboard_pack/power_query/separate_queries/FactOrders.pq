let
    DataFolder = "C:\\Users\\risk_\\Documents\\Codex\\2026-06-21\\new-chat\\outputs\\superstore_powerbi_dashboard_pack\\data",
    Source = Csv.Document(File.Contents(DataFolder & "\\FactOrders.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangedTypes = Table.TransformColumnTypes(PromotedHeaders, {
        {"Row ID", Int64.Type}, {"Order ID", type text}, {"DateKey", Int64.Type}, {"ShipDateKey", Int64.Type},
        {"ProductKey", Int64.Type}, {"CustomerKey", Int64.Type}, {"GeographyKey", Int64.Type}, {"ShipModeKey", Int64.Type},
        {"Sales", Currency.Type}, {"Quantity", Int64.Type}, {"Discount", Percentage.Type}, {"Profit", Currency.Type},
        {"Ship Days", Int64.Type}, {"Profit Margin", Percentage.Type}, {"Returned Flag", type logical}, {"Returned", type text},
        {"Net Sales After Returns", Currency.Type}, {"Return Sales", Currency.Type}, {"Loss Flag", type logical}, {"Discount Band", type text}
    })
in
    ChangedTypes
