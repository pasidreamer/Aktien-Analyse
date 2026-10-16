import json, re, sys
import os
P = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, P); import divsec
TPL = open(os.path.join(P, 'vorlage', 'beispielseite-relx.html')).read()
lines = TPL.split('\n')
HEAD = '\n'.join(lines[1:107])          # fonts + style (without title)
FUNCS = '\n'.join(lines[333:398])       # fmt helpers, scoreTable, lineChart, barChart

def xd(d):
    return d if '-' in d else f"20{d[0:2]}-{d[2:4]}-{d[4:6]}"

def load_raw(t):
    d = dict(l.split('=', 1) for l in open(os.path.join(P, 'raw', f'{t}_raw.txt')).read().strip().split('\n'))
    rows = lambda key: [r.split(',') for r in d[key].split(';')]
    W = ';'.join(','.join([xd(r[0])] + r[1:]) for r in rows('W'))
    DR = rows('D')
    if len(DR[0]) == 8:
        DD = ';'.join(','.join([xd(r[0]), r[3], r[4], r[5], r[7]]) for r in DR)
    else:
        DD = ';'.join(','.join([xd(r[0])] + r[1:]) for r in DR)
    return W, DD

def load_seas(t):
    for l in open(os.path.join(P, 'seas.txt')):
        p = l.split()
        if p and p[0] == t:
            return p[1], [[i+1] + [float(x) for x in v.split('/')] for i, v in enumerate(p[2:])]
    for l in open(os.path.join(P, 'raw', f'{t}_raw.txt')):
        if l.startswith('SEAS='):
            p = l[5:].split()
            return p[1], [[i+1] + [float(x) for x in v.split('/')] for i, v in enumerate(p[2:])]
    return None, None

def pill(v, kind):
    if kind == 'q':
        txt = 'Stark: Fundament intakt' if v >= 75 else 'Solide' if v >= 60 else 'Gemischt' if v >= 45 else 'Schwach'
    else:
        txt = ('Zone erreicht, Trend bestätigt' if v >= 75 else 'Einstieg in Zonen möglich' if v >= 60 else
               'Warten auf Bestätigung' if v >= 45 else 'Beobachten: Trigger noch nicht erreicht' if v >= 30 else 'Abwarten: Abwärtstrend intakt')
    cls = 'st-good' if v >= 60 else 'st-warn' if v >= 30 else 'st-bad'
    sym = '●' if v >= 60 else '▲'
    return f'<span class="state {cls}">{sym} {txt}</span>'

def build(c):
    W, DD = load_raw(c['ticker'])
    if 'SEAS' not in c:
        c['seasfrom'], c['SEAS'] = load_seas(c['ticker'])
    qs = sum(r[2] for r in c['Q']); ts = sum(r[2] for r in c['T'])
    kpis = '\n'.join(f'<div class="kpi {k[0]}"><span>{k[1]}</span><b>{k[2]}</b><em>{k[3]}</em></div>' for k in c['kpis'])
    zones = '\n'.join(f'<div class="zone {z[0]}"><b>{z[1]}</b><span>{z[2]}</span></div>' for z in c['zones'])
    todo = '\n'.join(f'<div class="zone {z[0]}"><b>{z[1]}</b><span>{z[2]}</span></div>' for z in c['todo'])
    ind = '\n'.join(f'<tr><td>{r[0]}</td><td class="pts">{r[1]}</td><td class="pts">{r[2]}</td><td>{r[3]}</td></tr>' if len(r) == 4 else f'<tr><td>{r[0]}</td><td colspan="2">{r[1]}</td><td>{r[2]}</td></tr>' for r in c['ind'])
    li = lambda xs: '\n'.join(f'<li>{x}</li>' for x in xs)
    bands = json.dumps(c['bands']); refs = json.dumps(c['refs'])
    html = f'''<title>{c['name']} Aktien-Check</title>
{HEAD}

<div class="wrap">

<header class="hero">
  <div class="card id">
    <div>
      <div class="eyebrow">Aktien-Check · {c.get('datum','29.09.2026')}</div>
      <h1>{c['name']}</h1>
      <p class="meta">{c['meta']}</p>
    </div>
    <div class="price"><b>{c['price']}</b><span class="meta">{c['pricemeta']}</span></div>
    <p class="verdict"><b>Kurz gesagt:</b> {c['verdict']}</p>
  </div>
  <div class="card scales">
    <div>
      <div class="scale-h"><span>Qualität · Ist die Firma kaufenswert?</span><b id="q-val">{qs}</b></div>
      <div class="track"><i class="pin" id="q-pin"></i></div>
      <div class="ticks"><span>0</span><span>30</span><span>45</span><span>60</span><span>75</span><span>100</span></div>
      {pill(qs,'q')}
    </div>
    <div>
      <div class="scale-h"><span>Timing · Ist jetzt der Zeitpunkt?</span><b id="t-val">{ts}</b></div>
      <div class="track"><i class="pin" id="t-pin"></i></div>
      <div class="ticks"><span>0</span><span>30</span><span>45</span><span>60</span><span>75</span><span>100</span></div>
      {pill(ts,'t')}
    </div>
    <p class="note">Skala: unter 30 rot · 30–45 orange · 45–60 gelb · 60–75 hellgrün · ab 75 grün. Beide Werte setzen sich aus festen Kriterien zusammen, siehe unten.</p>
  </div>
</header>

<section>
  <h2>Was die Firma macht</h2>
  <p class="lead">{c['about']}</p>
  <p class="lead">{c['why']}</p>
</section>

<section>
  <h2>Fundamental: die Zahlen</h2>
  <div class="kpis">
{kpis}
  </div>
  <div class="two">
    <div class="card">
      <h3>{c.get('revtitle','Umsatz pro Quartal (Mrd. $)')}</h3>
      <p class="note">{c['revnote']}</p>
      <div class="chart" id="c-rev"></div>
    </div>
    <div class="card">
      <h3>{c.get('margintitle','Operative Marge pro Jahr')}</h3>
      <p class="note">{c['marginnote']}</p>
      <div class="chart" id="c-margin"></div>
    </div>
  </div>
  <div class="card tbl">
    <table>
      <thead><tr><th>Jahr</th><th class="num">Umsatz {c.get('revunit','Mio. $')}</th><th class="num">Wachstum</th><th class="num">Op. Marge</th><th class="num">EPS {c.get('epsunit','$')}</th><th class="num">Free Cashflow</th><th class="num">ROIC</th><th class="num">{c.get('pecol','KGV')}</th></tr></thead>
      <tbody id="fin-rows"></tbody>
    </table>
  </div>
  <p class="note">{c['finnote']}</p>
</section>

<section>
  <h2>Qualität: {qs} von 100</h2>
  <div class="card tbl"><table id="q-tbl"></table></div>
</section>

<section>
  <h2>Technik: Wochenchart (2 Jahre)</h2>
  <div class="card">
    <div class="legend"><span><i class="sw" style="background:var(--s1)"></i>Kurs</span><span><i class="sw" style="background:var(--s2)"></i>EMA 50</span><span><i class="sw" style="background:var(--s3)"></i>EMA 200</span><span><i class="swb" style="background:var(--zone-sup);border:1px solid var(--good)"></i>Unterstützung</span><span><i class="swb" style="background:var(--zone-res);border:1px solid var(--bad)"></i>Widerstand</span></div>
    <div class="chart" id="c-week"></div>
  </div>
  <div class="two">
    <div class="card">
      <h3>A/D-Linie, Woche</h3>
      <p class="note">{c['adwnote']}</p>
      <div class="chart" id="c-adw"></div>
    </div>
    <div class="card">
      <h3>RSI, Woche</h3>
      <p class="note">{c['rsiwnote']}</p>
      <div class="chart" id="c-rsiw"></div>
    </div>
  </div>

  <h2>Technik: Tageschart ({"1 Jahr" if len(DD.split(";")) > 200 else "6 Monate"})</h2>
  <div class="two">
    <div class="card">
      <h3>Kurs, Tag</h3>
      <div class="legend"><span><i class="sw" style="background:var(--s1)"></i>Kurs</span><span><i class="sw" style="background:var(--s2)"></i>EMA 50</span><span><i class="sw" style="background:var(--s3)"></i>EMA 200</span></div>
      <div class="chart" id="c-day"></div>
    </div>
    <div class="card">
      <h3>A/D-Linie, Tag</h3>
      <p class="note">{c['addnote']}</p>
      <div class="chart" id="c-add"></div>
    </div>
  </div>

  <div class="card tbl">
    <table>
      <thead><tr><th>Indikator</th><th>Tag</th><th>Woche</th><th>Bedeutung</th></tr></thead>
      <tbody>
{ind}
      </tbody>
    </table>
  </div>
</section>

<section>
  <h2>Struktur und Zonen (Smart Money Concept)</h2>
  <p class="lead">{c['smc']}</p>
  <div class="zones">
{zones}
  </div>
</section>

<section>
  <h2>Smart Money, Insider und Saisonalität</h2>
  <div class="two">
    <div class="card">
      <h3>Wer kauft, wer verkauft?</h3>
      <ul class="clean" style="margin-top:8px">
{li(c['smart'])}
      </ul>
    </div>
    <div class="card">
      <h3>Saisonalität seit {c['seasfrom']}</h3>
      <p class="note">{c['seasnote']}</p>
      <div class="chart" id="c-seas"></div>
    </div>
  </div>
</section>

<section>
  <h2>Timing: {ts} von 100</h2>
  <div class="card tbl"><table id="t-tbl"></table></div>
</section>

<section>
  <h2>Pro und Contra</h2>
  <div class="two">
    <div class="card pro"><h3>Spricht dafür</h3><ul class="clean" style="margin-top:8px">
{li(c['pro'])}
    </ul></div>
    <div class="card con"><h3>Spricht dagegen</h3><ul class="clean" style="margin-top:8px">
{li(c['con'])}
    </ul></div>
  </div>
</section>

<section>
  <h2>Was jetzt zu tun ist</h2>
  <div class="zones">
{todo}
  </div>
</section>

<footer>
  <span>Kursdaten und Indikatoren (EMA, RSI 14, A/D) selbst berechnet aus Yahoo-Finance-Tages-, Wochen- und Monatsdaten, Stand {c.get('datum','29.09.2026')}. {c['sources']}</span>
  <span>Persönliche Analyse, keine Anlageberatung. Vergangene Kurse und Saisonalität sagen nichts Sicheres über die Zukunft.</span>
</footer>
</div>

<script>
const Q={json.dumps(c['Q'], ensure_ascii=False)};
const T={json.dumps(c['T'], ensure_ascii=False)};
const FIN={json.dumps(c['FIN'], ensure_ascii=False)};
const HALF={json.dumps(c['QREV'], ensure_ascii=False)};
const MARGIN={json.dumps(c['MARGIN'], ensure_ascii=False)};
const SEAS={json.dumps([s[1] for s in c['SEAS']])};
const SEASHIT={json.dumps([s[2] for s in c['SEAS']])};
const MON=["Jan","Feb","Mär","Apr","Mai","Jun","Jul","Aug","Sep","Okt","Nov","Dez"];
const W=`{W}`.split(";").map(r=>{{const a=r.split(",");return [a[0],...a.slice(1).map(Number)]}});
const DD=`{DD}`.split(";").map(r=>{{const a=r.split(",");return [a[0],...a.slice(1).map(Number)]}});

{FUNCS}
barChart(document.getElementById("c-rev"),{{labels:HALF.map(r=>r[0]),values:HALF.map(r=>r[1]),fmt:v=>fmtN(v,{c.get("revdec",1)}),h:200}});
barChart(document.getElementById("c-margin"),{{labels:MARGIN.map(r=>r[0]),values:MARGIN.map(r=>r[1]),fmt:v=>fmtN(v,1)+" %",h:200}});
barChart(document.getElementById("c-seas"),{{labels:MON,values:SEAS,fmt:v=>(v>0?"+":"")+fmtN(v,1),h:220,tipExtra:i=>`<div>${{SEASHIT[i]}} % der Jahre positiv</div>`}});
const BANDS={bands}, REFS={refs};
const wd=W.map(r=>r[0]);
lineChart(document.getElementById("c-week"),{{dates:wd,series:[{{name:"Kurs",values:W.map(r=>r[1]),color:"var(--s1)",w:2.5}},{{name:"EMA 50",values:W.map(r=>r[2]),color:"var(--s2)"}},{{name:"EMA 200",values:W.map(r=>r[3]),color:"var(--s3)"}}],bands:BANDS,yFmt:v=>fmtN(v,0),h:320}});
lineChart(document.getElementById("c-adw"),{{dates:wd,series:[{{name:"A/D Woche",values:W.map(r=>r[5]),color:"var(--s1)"}}],yFmt:v=>fmtN(v,0),h:220,zero:true}});
lineChart(document.getElementById("c-rsiw"),{{dates:wd,series:[{{name:"RSI Woche",values:W.map(r=>r[4]),color:"var(--s1)"}}],yFmt:v=>fmtN(v,0),h:220,refs:[{{v:70,label:"70 überkauft"}},{{v:30,label:"30 überverkauft"}}],pad:[10,90]}});
const dd=DD.map(r=>r[0]);
lineChart(document.getElementById("c-day"),{{dates:dd,series:[{{name:"Kurs",values:DD.map(r=>r[1]),color:"var(--s1)",w:2.5}},{{name:"EMA 50",values:DD.map(r=>r[2]),color:"var(--s2)"}},{{name:"EMA 200",values:DD.map(r=>r[3]),color:"var(--s3)"}}],bands:BANDS,refs:REFS,yFmt:v=>fmtN(v,0),h:260}});
lineChart(document.getElementById("c-add"),{{dates:dd,series:[{{name:"A/D Tag",values:DD.map(r=>r[4]),color:"var(--s1)"}}],yFmt:v=>fmtN(v,0),h:260,zero:true}});
</script>
'''
    rend = next((k[2] for k in c['kpis'] if k[1].startswith('Dividende')), None)
    html = divsec.inject(html, c['ticker'], c.get('waehrung', 'CHF' if 'CHF' in c['price'] else 'EUR' if '€' in c['price'] else 'GBp' if c['price'].endswith('p') else 'USD'), rend)
    open(os.path.join(P, "seiten", f"{c['ticker']}_aktien-check.html"), "w").write(html)
    return qs, ts

if __name__ == '__main__':
    for t in sys.argv[1:]:
        c = json.load(open(os.path.join(P, 'config', f'{t}.json')))
        print(t, build(c))
