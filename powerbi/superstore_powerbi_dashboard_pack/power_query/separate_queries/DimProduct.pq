let
    DataFolder = "C:\\Users\\risk_\\Documents\\Codex\\2026-06-21\\new-chat\\outputs\\superstore_powerbi_dashboard_pack\\data",
    Source = Csv.Document(File.Contents(DataFolder & "\\DimProduct.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangedTypes = Table.TransformColumnTypes(PromotedHeaders, {{"ProductKey", Int64.Type}, {"Product ID", type text}, {"Product Name", type text}, {"Category", type text}, {"Sub-Category", type text}})
in
    ChangedTypes
