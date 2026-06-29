from pathlib import Path
import json
import pandas as pd

ROOT = Path.cwd()
ANALYSIS = ROOT / "work" / "superstore_analysis"
OUT = ROOT / "outputs" / "superstore_powerbi_preview.html"

summary = json.loads((ANALYSIS / "summary.json").read_text(encoding="utf-8"))
monthly = pd.read_csv(ANALYSIS / "monthly_summary.csv").tail(18)
region = pd.read_csv(ANALYSIS / "region_summary.csv")
category = pd.read_csv(ANALYSIS / "category_summary.csv").sort_values("Sales", ascending=False).head(16)
state = pd.read_csv(ANALYSIS / "state_summary.csv").sort_values("Profit").head(10)
discount = pd.read_csv(ANALYSIS / "discount_summary.csv")
top_customers = pd.read_csv(ANALYSIS / "top_customers.csv").head(12)

data = {
    "summary": summary,
    "monthly": monthly.to_dict(orient="records"),
    "region": region.to_dict(orient="records"),
    "category": category.to_dict(orient="records"),
    "state": state.to_dict(orient="records"),
    "discount": discount.to_dict(orient="records"),
    "topCustomers": top_customers.to_dict(orient="records"),
}

html = f"""<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Superstore Power BI Preview</title>
<style>
  :root {{
    --bg:#f8fafc; --panel:#ffffff; --ink:#1f2937; --muted:#64748b; --teal:#0f766e;
    --teal2:#134e4a; --blue:#2563eb; --orange:#f97316; --green:#16a34a; --red:#dc2626;
    --line:#dbe3ef;
  }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; font-family: "Segoe UI", Tahoma, Arial, sans-serif; background:var(--bg); color:var(--ink); }}
  header {{ background:var(--teal2); color:white; padding:18px 28px 14px; position:sticky; top:0; z-index:5; box-shadow:0 8px 24px #0f172a20; }}
  header h1 {{ margin:0; font-size:24px; letter-spacing:0; }}
  header p {{ margin:6px 0 0; color:#ccfbf1; font-size:13px; }}
  main {{ padding:22px 28px 34px; max-width:1440px; margin:auto; }}
  .kpis {{ display:grid; grid-template-columns: repeat(6, minmax(140px, 1fr)); gap:14px; direction:ltr; }}
  .card {{ background:var(--panel); border:1px solid var(--line); border-radius:8px; box-shadow:0 8px 20px #0f172a0d; }}
  .kpi {{ padding:14px 16px; min-height:92px; }}
  .kpi .label {{ color:var(--muted); font-weight:700; font-size:12px; text-transform:uppercase; }}
  .kpi .value {{ margin-top:12px; font-weight:800; font-size:25px; color:var(--ink); }}
  .kpi.good .value {{ color:var(--green); }}
  .grid {{ display:grid; grid-template-columns: 1.25fr .95fr; gap:16px; margin-top:16px; direction:ltr; }}
  .panel {{ padding:16px; min-height:360px; overflow:hidden; }}
  .panel h2 {{ margin:0 0 12px; font-size:16px; }}
  .chart {{ width:100%; height:280px; direction:ltr; }}
  .wide {{ grid-column:1 / -1; }}
  .two {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-top:16px; direction:ltr; }}
  table {{ width:100%; border-collapse:collapse; font-size:12px; direction:ltr; }}
  th, td {{ padding:8px 9px; border-bottom:1px solid #edf2f7; text-align:left; white-space:nowrap; }}
  th {{ background:#e2e8f0; color:#334155; font-weight:800; }}
  .insights {{ display:grid; grid-template-columns:repeat(3, 1fr); gap:12px; margin-top:16px; direction:ltr; }}
  .insight {{ padding:12px 14px; border-right:4px solid var(--teal); background:#fffbeb; border-radius:8px; border:1px solid #fde68a; font-size:12px; line-height:1.45; }}
  .axis {{ stroke:#cbd5e1; stroke-width:1; }}
  .gridline {{ stroke:#e5e7eb; stroke-width:1; stroke-dasharray:4 4; }}
  .legend {{ display:flex; gap:14px; font-size:12px; color:var(--muted); align-items:center; }}
  .sw {{ width:10px; height:10px; display:inline-block; border-radius:2px; margin-right:5px; }}
  @media (max-width: 980px) {{
    .kpis {{ grid-template-columns:repeat(2,1fr); }}
    .grid, .two, .insights {{ grid-template-columns:1fr; }}
    main {{ padding:16px; }}
  }}
</style>
</head>
<body>
<header>
  <h1>Superstore Sales Performance Dashboard</h1>
  <p>Power BI-style preview | Cleaned retail orders analysis | 2015-01-03 to 2018-12-30</p>
</header>
<main>
  <section class="kpis" id="kpis"></section>
  <section class="insights" id="insights"></section>
  <section class="grid">
    <div class="card panel"><h2>Sales and Profit Trend</h2><div class="chart" id="trend"></div><div class="legend"><span><i class="sw" style="background:#0f766e"></i>Sales</span><span><i class="sw" style="background:#f97316"></i>Profit</span></div></div>
    <div class="card panel"><h2>Sales and Profit by Region</h2><div class="chart" id="regions"></div><div class="legend"><span><i class="sw" style="background:#2563eb"></i>Sales</span><span><i class="sw" style="background:#16a34a"></i>Profit</span></div></div>
  </section>
  <section class="two">
    <div class="card panel"><h2>Top Sub-Categories</h2><div class="chart" id="subcats"></div></div>
    <div class="card panel"><h2>Lowest Profit States</h2><div class="chart" id="states"></div></div>
  </section>
  <section class="two">
    <div class="card panel"><h2>Discount Impact</h2><div class="chart" id="discount"></div></div>
    <div class="card panel"><h2>Top Customers</h2><table id="customers"></table></div>
  </section>
</main>
<script>
const DATA = {json.dumps(data, ensure_ascii=False)};
const fmtMoney = n => new Intl.NumberFormat('en-US', {{ style:'currency', currency:'USD', maximumFractionDigits:0 }}).format(n || 0);
const fmtNum = n => new Intl.NumberFormat('en-US').format(n || 0);
const fmtPct = n => new Intl.NumberFormat('en-US', {{ style:'percent', maximumFractionDigits:1 }}).format(n || 0);

function kpis() {{
  const s = DATA.summary.overview;
  const rows = [
    ['Total Sales', fmtMoney(s.total_sales), ''],
    ['Total Profit', fmtMoney(s.total_profit), 'good'],
    ['Profit Margin', fmtPct(s.profit_margin), ''],
    ['Unique Orders', fmtNum(s.orders), ''],
    ['Customers', fmtNum(s.customers), ''],
    ['Return Rate', fmtPct(s.return_rate), ''],
  ];
  document.querySelector('#kpis').innerHTML = rows.map(([l,v,c]) => `<div class="card kpi ${{c}}"><div class="label">${{l}}</div><div class="value">${{v}}</div></div>`).join('');
  document.querySelector('#insights').innerHTML = DATA.summary.insights.map(x => `<div class="insight"><b>${{x[0]}}</b><br>${{x[1]}}</div>`).join('');
}}

function svg(tag, attrs='', body='') {{ return `<${{tag}} ${{attrs}}>${{body}}</${{tag}}>`; }}
function lineChart(el, rows, xKey, series) {{
  const w=720,h=280,p=42, iw=w-p*2, ih=h-p*1.6;
  const max = Math.max(...rows.flatMap(r => series.map(s => +r[s.key])));
  const x = i => p + (rows.length === 1 ? 0 : i*iw/(rows.length-1));
  const y = v => h-p - (+v/max)*ih;
  const grid = [0,.25,.5,.75,1].map(t => `<line class="gridline" x1="${{p}}" y1="${{h-p-t*ih}}" x2="${{w-p}}" y2="${{h-p-t*ih}}"/>`).join('');
  const paths = series.map(s => `<path d="${{rows.map((r,i)=>`${{i?'L':'M'}}${{x(i)}},${{y(r[s.key])}}`).join(' ')}}" fill="none" stroke="${{s.color}}" stroke-width="3"/>`).join('');
  const labels = rows.filter((_,i)=>i%3===0).map((r,i)=>`<text x="${{x(i*3)}}" y="${{h-10}}" font-size="10" text-anchor="middle" fill="#64748b">${{r[xKey]}}</text>`).join('');
  el.innerHTML = `<svg viewBox="0 0 ${{w}} ${{h}}" width="100%" height="100%">${{grid}}${{paths}}${{labels}}</svg>`;
}}
function barChart(el, rows, label, series, opts={{}}) {{
  const w=720,h=280,p=44, iw=w-p*2, ih=h-p*1.6;
  const max = Math.max(...rows.flatMap(r => series.map(s => Math.abs(+r[s.key]))));
  const groupW = iw/rows.length;
  let bars='', labels='';
  rows.forEach((r,i)=> {{
    series.forEach((s,j)=> {{
      const val = +r[s.key], bh = Math.abs(val)/max*ih;
      const bw = Math.max(6, groupW/(series.length+1));
      const x = p+i*groupW+j*bw+4;
      const y0 = val >= 0 ? h-p-bh : h-p;
      bars += `<rect x="${{x}}" y="${{y0}}" width="${{bw-2}}" height="${{bh}}" fill="${{s.color}}" rx="2"/>`;
    }});
    if (i % (opts.every || 1) === 0) labels += `<text transform="translate(${{p+i*groupW+groupW/2}},${{h-8}}) rotate(-45)" font-size="10" text-anchor="end" fill="#64748b">${{String(r[label]).slice(0,14)}}</text>`;
  }});
  el.innerHTML = `<svg viewBox="0 0 ${{w}} ${{h}}" width="100%" height="100%"><line class="axis" x1="${{p}}" y1="${{h-p}}" x2="${{w-p}}" y2="${{h-p}}"/>${{bars}}${{labels}}</svg>`;
}}
function table() {{
  const rows = DATA.topCustomers;
  document.querySelector('#customers').innerHTML = '<thead><tr><th>Customer</th><th>Segment</th><th>Sales</th><th>Profit</th><th>Orders</th></tr></thead><tbody>' +
    rows.map(r => `<tr><td>${{r['Customer Name']}}</td><td>${{r.Segment}}</td><td>${{fmtMoney(r.Sales)}}</td><td>${{fmtMoney(r.Profit)}}</td><td>${{r.Orders}}</td></tr>`).join('') + '</tbody>';
}}
kpis();
lineChart(document.querySelector('#trend'), DATA.monthly, 'Year Month', [{{key:'Sales', color:'#0f766e'}}, {{key:'Profit', color:'#f97316'}}]);
barChart(document.querySelector('#regions'), DATA.region, 'Region', [{{key:'Sales', color:'#2563eb'}}, {{key:'Profit', color:'#16a34a'}}]);
barChart(document.querySelector('#subcats'), DATA.category, 'Sub-Category', [{{key:'Sales', color:'#0f766e'}}, {{key:'Profit', color:'#f97316'}}], {{every:1}});
barChart(document.querySelector('#states'), DATA.state, 'State', [{{key:'Sales', color:'#2563eb'}}, {{key:'Profit', color:'#dc2626'}}]);
barChart(document.querySelector('#discount'), DATA.discount, 'Discount Band', [{{key:'Sales', color:'#0f766e'}}, {{key:'Profit', color:'#f97316'}}]);
table();
</script>
</body>
</html>
"""

OUT.write_text(html, encoding="utf-8")
print(OUT)
