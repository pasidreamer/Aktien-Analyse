import sys, os
P = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, P); import divsec
import json, re, html as H, glob, os
REPO = os.path.dirname(P)
KEYS = ["symbol", "name", "tags", "land", "region", "branche", "status", "waehrung", "kurs", "datenstand", "kauf", "widerstand", "trigger", "abbruch", "pe", "pe_avg", "pe_typ", "zahlen", "artifact"]
RELX_SRC = os.path.join(P, "vorlage", "beispielseite-relx.html")
A = "https://claude.ai/artifact/"
QK = ["umsatz","wachstum","marge","eps","fcf","roic","schulden","bewertung"]
TK = ["trend_w","trend_d","smc","rsi","ad","smart","saison"]
AUTO_T = {"trend_w","trend_d","rsi","ad","saison"}
# ticker: symbol, name, tags, land, region, branche, status, waehrung, kurs, datenstand, kauf, widerstand, trigger, abbruch, pe, pe_avg, pe_typ, zahlen, artifact
M = {t: [a[k] for k in KEYS] for t, a in json.load(open(os.path.join(P, "aktien.json"))).items()}
strip = lambda s: H.unescape(re.sub("<[^>]+>","",s or "")).strip()

def relx_cfg():
    s = open(RELX_SRC).read()
    grab = lambda name: json.loads(re.search(rf"const {name}=(\[.*?\]);", s, re.S).group(1))
    c = {"Q": grab("Q"), "T": grab("T"), "name": "RELX"}
    c["verdict"] = strip(re.search(r'<p class="verdict"><b>Kurz gesagt:</b>(.*?)</p>', s).group(1))
    c["kpis"] = [[k, strip(a), strip(b), strip(e)] for k,a,b,e in re.findall(r'<div class="kpi (\w)"><span>(.*?)</span><b>(.*?)</b><em>(.*?)</em></div>', s)]
    c["zones"] = [[k, strip(a), strip(b)] for k,a,b in re.findall(r'<div class="zone (\w?)"><b>(.*?)</b><span>(.*?)</span></div>', s)]
    lists = re.findall(r"<ul[^>]*>(.*?)</ul>", s, re.S)
    li = lambda block: [strip(x) for x in re.findall(r"<li>(.*?)</li>", block, re.S)]
    c["pro"], c["con"] = (li(lists[-2]), li(lists[-1])) if len(lists) >= 2 else ([], [])
    c["about"] = strip(re.search(r'<p class="lead">(.*?)</p>', s, re.S).group(1))
    return c, s

stocks = []
for t, m in M.items():
    sym,name,tags,land,region,branche,status,cur,kurs,ds,kauf,wid,trig,abb,pe,pea,pet,zahlen,art = m
    if t == "RELX":
        c, page = relx_cfg()
    else:
        c = json.load(open(os.path.join(P, "config", f"{t}.json"))); page = open(os.path.join(P, "seiten", f"{t}_aktien-check.html")).read()
    q = [{"k":QK[i],"name":r[0],"txt":strip(r[1]),"p":r[2],"max":r[3],"auto":QK[i]=="bewertung" and pe is not None} for i,r in enumerate(c["Q"])]
    tt = [{"k":TK[i],"name":r[0],"txt":strip(r[1]),"p":r[2],"max":r[3],"auto":TK[i] in AUTO_T} for i,r in enumerate(c["T"])]
    div = next((k[2] for k in c["kpis"] if k[1].startswith("Dividende")), None)
    smart = [strip(x) for x in c.get("smart", [])]
    stocks.append({
      "ticker": t, "symbol": sym, "name": name, "tags": tags, "land": land, "region": region, "branche": branche,
      "status": status, "waehrung": cur, "analyse": {"datenstand": ds, "kurs": kurs, "q": sum(x["p"] for x in q), "t": sum(x["p"] for x in tt)},
      "qualitaet": q, "timing": tt,
      "bewertung": {"wert": pe, "schnitt": pea, "typ": pet} if pe else None,
      "zonen": {"kauf": kauf, "widerstand": wid, "trigger": trig, "abbruch": abb},
      "zahlen": zahlen, "dividende": div, "div_info": divsec.info(t), "chance": divsec.chance(t),
      "fazit": strip(c["verdict"]), "about": strip(c.get("about","")),
      "kpis": [{"ampel":k[0],"name":strip(k[1]),"wert":strip(k[2]),"text":strip(k[3])} for k in c["kpis"]],
      "zonen_text": [{"art":z[0],"wert":strip(z[1]),"text":strip(z[2])} for z in c["zones"]],
      "pro": [strip(x) for x in c.get("pro", [])], "contra": [strip(x) for x in c.get("con", [])],
      "smart_money": smart,
      "cheatsheet": f"analysen/{t}.html", "claude": A + art
    })
    # standalone cheat sheet page
    back = '<a href="../index.html#/aktie/%s" style="display:inline-block;margin:max(12px,env(safe-area-inset-top)) 0 0 16px;background:#1f3a5f;color:#fff;font:600 14px system-ui;padding:8px 12px;border-radius:20px;text-decoration:none;box-shadow:0 2px 8px rgba(0,0,0,.25)">Zurück zur App</a>' % t
    doc = '<!doctype html>\n<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n' + page.replace("</title>", "</title>", 1)
    # insert back link after first <div class="wrap">
    doc = doc.replace('<div class="wrap">', back + '\n<div class="wrap">', 1)
    doc = divsec.inject(doc, t, cur, div, land, {"wert": pe, "schnitt": pea, "typ": pet} if pe else None)
    open(f"{REPO}/analysen/{t}.html", "w").write(doc)
json.dump({"stand": __import__("datetime").date.today().isoformat(), "aktien": stocks}, open(f"{REPO}/data/stocks.json","w"), ensure_ascii=False, indent=1)
for s in stocks: print(s["ticker"], s["analyse"]["q"], s["analyse"]["t"], s["dividende"], len(s["kpis"]), len(s["pro"]))
