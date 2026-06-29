let
    DataFolder = "C:\\Users\\risk_\\Documents\\Codex\\2026-06-21\\new-chat\\outputs\\superstore_powerbi_dashboard_pack\\data",
    Source = Csv.Document(File.Contents(DataFolder & "\\DimGeography.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangedTypes = Table.TransformColumnTypes(PromotedHeaders, {{"GeographyKey", Int64.Type}, {"Country", type text}, {"City", type text}, {"State", type text}, {"Postal Code", type text}, {"Region", type text}, {"Person", type text}})
in
    ChangedTypes
