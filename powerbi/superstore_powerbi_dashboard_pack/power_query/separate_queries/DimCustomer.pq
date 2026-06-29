let
    DataFolder = "C:\\Users\\risk_\\Documents\\Codex\\2026-06-21\\new-chat\\outputs\\superstore_powerbi_dashboard_pack\\data",
    Source = Csv.Document(File.Contents(DataFolder & "\\DimCustomer.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangedTypes = Table.TransformColumnTypes(PromotedHeaders, {{"CustomerKey", Int64.Type}, {"Customer ID", type text}, {"Customer Name", type text}, {"Segment", type text}})
in
    ChangedTypes
