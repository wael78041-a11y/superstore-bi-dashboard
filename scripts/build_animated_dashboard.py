from pathlib import Path
import json
import pandas as pd

ROOT = Path.cwd()
ANALYSIS = ROOT / "work" / "superstore_analysis"
OUT = ROOT / "outputs" / "superstore_animated_dashboard.html"

orders = pd.read_csv(ANALYSIS / "cleaned_orders.csv")
orders = orders[
    [
        "Order ID",
        "Order Date",
        "Year Month",
        "Order Year",
        "Region",
        "Segment",
        "Category",
        "Sub-Category",
        "State",
        "Customer Name",
        "Sales",
        "Profit",
        "Quantity",
        "Discount",
        "Ship Days",
        "Returned Flag",
        "Return Sales",
    ]
].copy()

orders["Returned Flag"] = orders["Returned Flag"].astype(str).str.lower().isin(["true", "1", "yes"])
orders["Sales"] = orders["Sales"].round(2)
orders["Profit"] = orders["Profit"].round(2)
orders["Discount"] = orders["Discount"].round(4)
orders["Return Sales"] = orders["Return Sales"].round(2)

payload = {
    "orders": orders.to_dict(orient="records"),
    "filters": {
        "years": sorted(orders["Order Year"].dropna().astype(int).unique().tolist()),
        "regions": sorted(orders["Region"].dropna().unique().tolist()),
        "segments": sorted(orders["Segment"].dropna().unique().tolist()),
        "categories": sorted(orders["Category"].dropna().unique().tolist()),
    },
}

html = f"""<!doctype html>
<html lang="ar" dir="ltr">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Animated Superstore BI Dashboard</title>
<style>
:root {{
  --bg:#f4f7fb; --panel:#ffffff; --ink:#182230; --muted:#667085; --line:#d9e2ec;
  --teal:#0f766e; --teal2:#115e59; --cyan:#0891b2; --blue:#2563eb; --green:#16a34a;
  --orange:#f97316; --red:#dc2626; --violet:#7c3aed; --shadow:0 18px 45px rgba(15,23,42,.10);
}}
* {{ box-sizing:border-box; }}
body {{
  margin:0; background:var(--bg); color:var(--ink);
  font-family:"Segoe UI", Tahoma, Arial, sans-serif;
  overflow-x:hidden;
}}
.shell {{ min-height:100vh; display:grid; grid-template-columns:260px minmax(0,1fr); direction:ltr; width:100%; max-width:100vw; }}
aside {{
  background:#0f172a; color:white; padding:22px 18px; position:sticky; top:0; height:100vh;
  box-shadow:10px 0 30px rgba(15,23,42,.15);
}}
.brand {{ font-weight:850; font-size:20px; line-height:1.1; margin-bottom:24px; }}
.brand span {{ display:block; color:#99f6e4; font-size:12px; font-weight:600; margin-top:7px; }}
.nav button {{
  width:100%; border:0; background:transparent; color:#cbd5e1; display:flex; align-items:center; gap:10px;
  padding:12px 11px; border-radius:8px; cursor:pointer; font-weight:700; text-align:left; margin-bottom:6px;
}}
.nav button.active, .nav button:hover {{ background:#164e63; color:white; }}
.filter-title {{ margin:22px 0 8px; color:#94a3b8; font-size:11px; text-transform:uppercase; font-weight:800; }}
select {{
  width:100%; border:1px solid #334155; background:#111827; color:white; border-radius:8px;
  padding:10px; margin-bottom:10px; outline:none;
}}
.content {{ padding:20px 24px 32px; overflow-x:hidden; min-width:0; }}
header {{
  display:flex; justify-content:space-between; align-items:flex-start; gap:18px; margin-bottom:16px; direction:ltr;
}}
h1 {{ margin:0; font-size:26px; letter-spacing:0; }}
.subtitle {{ margin-top:6px; color:var(--muted); font-size:13px; }}
.actions {{ display:flex; gap:10px; }}
.ghost {{
  border:1px solid var(--line); background:white; color:var(--ink); border-radius:8px; padding:10px 13px;
  font-weight:800; cursor:pointer;
}}
.kpis {{ display:grid; grid-template-columns:repeat(6,minmax(0,1fr)); gap:14px; margin-bottom:14px; direction:ltr; min-width:0; }}
.kpi {{
  background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:14px 15px;
  box-shadow:var(--shadow); min-height:98px; transform:translateY(8px); opacity:0; animation:rise .55s ease forwards;
}}
.kpi:nth-child(2) {{ animation-delay:.05s }} .kpi:nth-child(3) {{ animation-delay:.1s }}
.kpi:nth-child(4) {{ animation-delay:.15s }} .kpi:nth-child(5) {{ animation-delay:.2s }} .kpi:nth-child(6) {{ animation-delay:.25s }}
@keyframes rise {{ to {{ transform:none; opacity:1; }} }}
.label {{ color:var(--muted); font-size:11px; font-weight:850; text-transform:uppercase; }}
.value {{ font-size:25px; font-weight:900; margin-top:13px; }}
.delta {{ margin-top:7px; color:var(--muted); font-size:11px; }}
.page {{ display:none; }}
.page.active {{ display:block; animation:fade .35s ease; }}
@keyframes fade {{ from {{ opacity:.4; transform:translateY(6px); }} to {{ opacity:1; transform:none; }} }}
.grid {{ display:grid; grid-template-columns:minmax(0,1.25fr) minmax(0,.85fr); gap:14px; direction:ltr; min-width:0; }}
.grid3 {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:14px; direction:ltr; min-width:0; }}
.panel {{
  background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:15px;
  box-shadow:var(--shadow); min-height:340px; overflow:hidden; min-width:0;
}}
.panel h2 {{ margin:0 0 12px; font-size:15px; }}
.chart {{ height:280px; position:relative; direction:ltr; }}
.chart svg {{ width:100%; height:100%; overflow:hidden; }}
.legend {{ display:flex; gap:14px; color:var(--muted); font-size:12px; margin-top:8px; }}
.sw {{ width:10px; height:10px; border-radius:3px; display:inline-block; margin-right:5px; }}
.tooltip {{
  position:fixed; pointer-events:none; background:#111827; color:white; border-radius:8px; padding:8px 10px;
  font-size:12px; opacity:0; transform:translate(-50%,-120%); transition:opacity .12s ease; z-index:20;
  box-shadow:0 14px 35px rgba(15,23,42,.25);
}}
table {{ width:100%; border-collapse:collapse; font-size:12px; direction:ltr; }}
th,td {{ padding:9px 8px; border-bottom:1px solid #edf2f7; text-align:left; white-space:nowrap; }}
th {{ background:#e2e8f0; color:#334155; font-size:11px; text-transform:uppercase; }}
.heat {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(120px,1fr)); gap:10px; direction:ltr; min-width:0; }}
.tile {{ border-radius:8px; padding:11px; color:white; min-height:82px; display:flex; flex-direction:column; justify-content:space-between; }}
.tile b {{ font-size:12px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
.tile span {{ font-size:clamp(15px,2vw,22px); font-weight:900; white-space:nowrap; }}
@media(max-width:1100px) {{
  .shell {{ grid-template-columns:1fr; }}
  aside {{ position:relative; height:auto; }}
  .kpis {{ grid-template-columns:repeat(2,1fr); }}
  .grid,.grid3 {{ grid-template-columns:1fr; }}
}}
</style>
</head>
<body>
<div class="shell">
  <aside>
    <div class="brand">Superstore BI<span>Animated executive dashboard</span></div>
    <div class="nav">
      <button class="active" data-page="overview">Overview</button>
      <button data-page="products">Products</button>
      <button data-page="geo">Geography</button>
      <button data-page="customers">Customers</button>
    </div>
    <div class="filter-title">Filters</div>
    <select id="year"></select>
    <select id="region"></select>
    <select id="segment"></select>
    <select id="category"></select>
  </aside>
  <main class="content">
    <header>
      <div>
        <h1>Sales Performance Dashboard</h1>
        <div class="subtitle">Interactive Power BI-style dashboard built from cleaned Sample Superstore data</div>
      </div>
      <div class="actions">
        <button class="ghost" id="reset">Reset Filters</button>
      </div>
    </header>
    <section class="kpis" id="kpis"></section>
    <section class="page active" id="overview">
      <div class="grid">
        <div class="panel"><h2>Sales and Profit Trend</h2><div class="chart" id="trend"></div><div class="legend"><span><i class="sw" style="background:#0f766e"></i>Sales</span><span><i class="sw" style="background:#f97316"></i>Profit</span></div></div>
        <div class="panel"><h2>Region Performance</h2><div class="chart" id="regionChart"></div><div class="legend"><span><i class="sw" style="background:#2563eb"></i>Sales</span><span><i class="sw" style="background:#16a34a"></i>Profit</span></div></div>
      </div>
      <div class="grid3" style="margin-top:14px">
        <div class="panel"><h2>Discount Risk</h2><div class="chart" id="discountChart"></div></div>
        <div class="panel"><h2>Lowest Profit States</h2><div class="chart" id="stateChart"></div></div>
        <div class="panel"><h2>Profit Heatmap</h2><div class="heat" id="heat"></div></div>
      </div>
    </section>
    <section class="page" id="products">
      <div class="grid">
        <div class="panel"><h2>Sub-Category Sales vs Profit</h2><div class="chart" id="subcatChart"></div></div>
        <div class="panel"><h2>Category Mix</h2><div class="chart" id="categoryMix"></div></div>
      </div>
    </section>
    <section class="page" id="geo">
      <div class="grid">
        <div class="panel"><h2>State Sales Ranking</h2><div class="chart" id="stateSales"></div></div>
        <div class="panel"><h2>Returns by Region</h2><div class="chart" id="returns"></div></div>
      </div>
    </section>
    <section class="page" id="customers">
      <div class="grid">
        <div class="panel"><h2>Top Customers</h2><table id="customerTable"></table></div>
        <div class="panel"><h2>Segment Mix</h2><div class="chart" id="segmentMix"></div></div>
      </div>
    </section>
  </main>
</div>
<div class="tooltip" id="tip"></div>
<script>
const RAW = {json.dumps(payload, ensure_ascii=False)};
const $ = s => document.querySelector(s);
const fmtMoney = n => new Intl.NumberFormat('en-US', {{style:'currency', currency:'USD', maximumFractionDigits:0}}).format(n||0);
const fmtNum = n => new Intl.NumberFormat('en-US').format(Math.round(n||0));
const fmtPct = n => new Intl.NumberFormat('en-US', {{style:'percent', maximumFractionDigits:1}}).format(n||0);
const colors = ['#0f766e','#2563eb','#f97316','#16a34a','#dc2626','#7c3aed','#0891b2','#64748b'];
const tip = $('#tip');

function opt(id, all, values) {{
  const el = $(id);
  el.innerHTML = `<option value="">${{all}}</option>` + values.map(v=>`<option value="${{v}}">${{v}}</option>`).join('');
}}
opt('#year','All Years',RAW.filters.years);
opt('#region','All Regions',RAW.filters.regions);
opt('#segment','All Segments',RAW.filters.segments);
opt('#category','All Categories',RAW.filters.categories);

function filtered() {{
  const y = $('#year').value, r = $('#region').value, s = $('#segment').value, c = $('#category').value;
  return RAW.orders.filter(d => (!y || String(d['Order Year'])===y) && (!r || d.Region===r) && (!s || d.Segment===s) && (!c || d.Category===c));
}}
function group(rows, key, reducers) {{
  const m = new Map();
  for (const row of rows) {{
    const k = row[key] ?? 'Unknown';
    if (!m.has(k)) m.set(k, {{label:k, Sales:0, Profit:0, Quantity:0, ReturnSales:0, Orders:new Set(), Customers:new Set(), Count:0, Discount:0, ShipDays:0}});
    const x = m.get(k);
    x.Sales += +row.Sales; x.Profit += +row.Profit; x.Quantity += +row.Quantity; x.ReturnSales += +row['Return Sales'];
    x.Orders.add(row['Order ID']); x.Customers.add(row['Customer Name']); x.Count++; x.Discount += +row.Discount; x.ShipDays += +row['Ship Days'];
  }}
  return [...m.values()].map(x => ({{...x, Orders:x.Orders.size, Customers:x.Customers.size, Margin:x.Sales?x.Profit/x.Sales:0, AvgDiscount:x.Count?x.Discount/x.Count:0, AvgShip:x.Count?x.ShipDays/x.Count:0}}));
}}
function animateNum(el, to, formatter) {{
  const start = performance.now(), dur = 700;
  function step(t) {{
    const p = Math.min(1,(t-start)/dur), e = 1-Math.pow(1-p,3);
    el.textContent = formatter(to*e);
    if (p<1) requestAnimationFrame(step);
  }}
  requestAnimationFrame(step);
}}
function renderKpis(rows) {{
  const orders = new Set(rows.map(r=>r['Order ID'])).size;
  const customers = new Set(rows.map(r=>r['Customer Name'])).size;
  const sales = rows.reduce((a,b)=>a+ +b.Sales,0), profit = rows.reduce((a,b)=>a+ +b.Profit,0);
  const returned = new Set(rows.filter(r=>r['Returned Flag']).map(r=>r['Order ID'])).size;
  const ship = rows.reduce((a,b)=>a+ +b['Ship Days'],0) / Math.max(1,rows.length);
  const k = [
    ['Total Sales', sales, fmtMoney], ['Total Profit', profit, fmtMoney], ['Profit Margin', sales?profit/sales:0, fmtPct],
    ['Orders', orders, fmtNum], ['Customers', customers, fmtNum], ['Return Rate', orders?returned/orders:0, fmtPct]
  ];
  $('#kpis').innerHTML = k.map(x=>`<div class="kpi"><div class="label">${{x[0]}}</div><div class="value">0</div><div class="delta">Avg ship days: ${{ship.toFixed(1)}}</div></div>`).join('');
  document.querySelectorAll('.kpi .value').forEach((el,i)=>animateNum(el,k[i][1],k[i][2]));
}}
function showTip(e, html) {{ tip.innerHTML=html; tip.style.left=e.clientX+'px'; tip.style.top=e.clientY+'px'; tip.style.opacity=1; }}
function hideTip() {{ tip.style.opacity=0; }}
function barChart(el, rows, label, series, opts={{}}) {{
  rows = rows.slice(0, opts.limit || rows.length);
  const w=760,h=300,p=46, iw=w-p*2, ih=h-p*1.55;
  const max = Math.max(1,...rows.flatMap(r=>series.map(s=>Math.abs(+r[s.key]))));
  const groupW = iw/Math.max(1,rows.length);
  let body=`<line x1="${{p}}" y1="${{h-p}}" x2="${{w-p}}" y2="${{h-p}}" stroke="#cbd5e1"/>`;
  rows.forEach((r,i)=> {{
    series.forEach((s,j)=> {{
      const val=+r[s.key], bh=Math.abs(val)/max*ih, bw=Math.max(7, groupW/(series.length+1.2));
      const x=p+i*groupW+j*bw+5, y=val>=0?h-p-bh:h-p;
      body += `<rect class="bar" x="${{x}}" y="${{y}}" width="${{bw-2}}" height="0" data-h="${{bh}}" data-y="${{y}}" fill="${{s.color}}" rx="3"><title>${{r[label]}} | ${{s.name}}: ${{fmtMoney(val)}}</title></rect>`;
    }});
    if(i%(opts.every||1)===0) body += `<text transform="translate(${{p+i*groupW+groupW/2}},${{h-8}}) rotate(-45)" font-size="10" text-anchor="end" fill="#667085">${{String(r[label]).slice(0,14)}}</text>`;
  }});
  el.innerHTML = `<svg viewBox="0 0 ${{w}} ${{h}}">${{body}}</svg>`;
  el.querySelectorAll('.bar').forEach((b,i)=>setTimeout(()=>{{ b.setAttribute('height',b.dataset.h); b.setAttribute('y',b.dataset.y); b.style.transition='height .7s ease, y .7s ease'; }},i*18));
}}
function lineChart(el, rows, xKey, series) {{
  const w=760,h=300,p=46, iw=w-p*2, ih=h-p*1.6, max=Math.max(1,...rows.flatMap(r=>series.map(s=>+r[s.key])));
  const x=i=>p+(rows.length===1?0:i*iw/(rows.length-1)), y=v=>h-p-(+v/max)*ih;
  let grid=[0,.25,.5,.75,1].map(t=>`<line x1="${{p}}" y1="${{h-p-t*ih}}" x2="${{w-p}}" y2="${{h-p-t*ih}}" stroke="#e5e7eb" stroke-dasharray="4 4"/>`).join('');
  let paths=series.map(s=>`<path class="line" d="${{rows.map((r,i)=>`${{i?'L':'M'}}${{x(i)}},${{y(r[s.key])}}`).join(' ')}}" fill="none" stroke="${{s.color}}" stroke-width="3" stroke-linecap="round"/>`).join('');
  let labels=rows.filter((_,i)=>i%3===0).map((r,idx)=>`<text x="${{x(idx*3)}}" y="${{h-9}}" font-size="10" text-anchor="middle" fill="#667085">${{r[xKey]}}</text>`).join('');
  el.innerHTML=`<svg viewBox="0 0 ${{w}} ${{h}}">${{grid}}${{paths}}${{labels}}</svg>`;
  el.querySelectorAll('.line').forEach(p=>{{ const l=p.getTotalLength(); p.style.strokeDasharray=l; p.style.strokeDashoffset=l; p.getBoundingClientRect(); p.style.transition='stroke-dashoffset 1.1s ease'; p.style.strokeDashoffset=0; }});
}}
function donut(el, rows, label, valueKey) {{
  const total=rows.reduce((a,b)=>a+ +b[valueKey],0)||1, r=92, cx=150, cy=138, c=2*Math.PI*r;
  let off=0, seg='';
  rows.forEach((x,i)=>{{ const v=+x[valueKey]/total*c; seg += `<circle cx="${{cx}}" cy="${{cy}}" r="${{r}}" fill="none" stroke="${{colors[i%colors.length]}}" stroke-width="34" stroke-dasharray="${{v}} ${{c-v}}" stroke-dashoffset="${{-off}}" transform="rotate(-90 ${{cx}} ${{cy}})" opacity=".95"/>`; off+=v; }});
  const legend=rows.map((x,i)=>`<div><span class="sw" style="background:${{colors[i%colors.length]}}"></span>${{x[label]}}: ${{fmtMoney(x[valueKey])}}</div>`).join('');
  el.innerHTML=`<svg viewBox="0 0 520 290"><g class="donut">${{seg}}</g><text x="${{cx}}" y="${{cy}}" text-anchor="middle" font-size="22" font-weight="900">${{fmtMoney(total)}}</text><foreignObject x="300" y="55" width="210" height="190"><div xmlns="http://www.w3.org/1999/xhtml" style="font-size:12px;color:#667085;line-height:1.8">${{legend}}</div></foreignObject></svg>`;
}}
function renderTable(rows) {{
  const g = group(rows,'Customer Name').sort((a,b)=>b.Sales-a.Sales).slice(0,12);
  $('#customerTable').innerHTML='<thead><tr><th>Customer</th><th>Sales</th><th>Profit</th><th>Orders</th><th>Margin</th></tr></thead><tbody>'+
    g.map(r=>`<tr><td>${{r.label}}</td><td>${{fmtMoney(r.Sales)}}</td><td>${{fmtMoney(r.Profit)}}</td><td>${{r.Orders}}</td><td>${{fmtPct(r.Margin)}}</td></tr>`).join('')+'</tbody>';
}}
function heat(rows) {{
  const g=group(rows,'State').sort((a,b)=>a.Profit-b.Profit).slice(0,10);
  const max=Math.max(...g.map(x=>Math.abs(x.Profit)),1);
  $('#heat').innerHTML=g.map(x=>{{ const neg=x.Profit<0, alpha=.35+Math.abs(x.Profit)/max*.65; return `<div class="tile" style="background:${{neg?`rgba(220,38,38,${{alpha}})`:`rgba(15,118,110,${{alpha}})`}}"><b>${{x.label}}</b><span>${{fmtMoney(x.Profit)}}</span></div>`; }}).join('');
}}
function discountBand(d) {{ if(d===0)return '0%'; if(d<=.1)return '0-10%'; if(d<=.2)return '10-20%'; if(d<=.4)return '20-40%'; return '40%+'; }}
function render() {{
  const rows=filtered(); renderKpis(rows);
  const monthly=group(rows,'Year Month').sort((a,b)=>a.label.localeCompare(b.label));
  lineChart($('#trend'),monthly,'label',[{{key:'Sales',color:'#0f766e'}},{{key:'Profit',color:'#f97316'}}]);
  barChart($('#regionChart'),group(rows,'Region').sort((a,b)=>b.Sales-a.Sales),'label',[{{key:'Sales',name:'Sales',color:'#2563eb'}},{{key:'Profit',name:'Profit',color:'#16a34a'}}]);
  const discMap=new Map(); rows.forEach(r=>{{ const b=discountBand(+r.Discount); if(!discMap.has(b))discMap.set(b,[]); discMap.get(b).push(r); }});
  barChart($('#discountChart'),[...discMap].map(([label,arr])=>group(arr,'Category')[0]||{{label,Sales:0,Profit:0}}).map((x,i)=>({{...x,label:[...discMap.keys()][i]}})),'label',[{{key:'Sales',name:'Sales',color:'#0f766e'}},{{key:'Profit',name:'Profit',color:'#f97316'}}]);
  barChart($('#stateChart'),group(rows,'State').sort((a,b)=>a.Profit-b.Profit).slice(0,10),'label',[{{key:'Sales',name:'Sales',color:'#2563eb'}},{{key:'Profit',name:'Profit',color:'#dc2626'}}]);
  heat(rows);
  barChart($('#subcatChart'),group(rows,'Sub-Category').sort((a,b)=>b.Sales-a.Sales),'label',[{{key:'Sales',name:'Sales',color:'#0f766e'}},{{key:'Profit',name:'Profit',color:'#f97316'}}],{{limit:16}});
  donut($('#categoryMix'),group(rows,'Category').sort((a,b)=>b.Sales-a.Sales),'label','Sales');
  barChart($('#stateSales'),group(rows,'State').sort((a,b)=>b.Sales-a.Sales).slice(0,15),'label',[{{key:'Sales',name:'Sales',color:'#2563eb'}}]);
  barChart($('#returns'),group(rows,'Region').sort((a,b)=>b.ReturnSales-a.ReturnSales),'label',[{{key:'ReturnSales',name:'Return Sales',color:'#dc2626'}}]);
  renderTable(rows);
  donut($('#segmentMix'),group(rows,'Segment').sort((a,b)=>b.Sales-a.Sales),'label','Sales');
}}
document.querySelectorAll('select').forEach(s=>s.addEventListener('change',render));
$('#reset').addEventListener('click',()=>{{ document.querySelectorAll('select').forEach(s=>s.value=''); render(); }});
document.querySelectorAll('.nav button').forEach(btn=>btn.addEventListener('click',()=>{{
  document.querySelectorAll('.nav button').forEach(b=>b.classList.remove('active')); btn.classList.add('active');
  document.querySelectorAll('.page').forEach(p=>p.classList.remove('active')); $('#'+btn.dataset.page).classList.add('active');
}}));
render();
</script>
</body>
</html>"""

OUT.write_text(html, encoding="utf-8")
print(OUT)
