"""Instagram-Karussell im Stil «Zeitung» (Vorlage B) aus einer Inhaltsdatei rendern.

Aufruf:
  python scripts/karussell.py data/karussell/2026-11-03.json
Ergebnis:
  karussell/<datum>/1.png … 7.png (1080×1350), caption.txt
  data/karussell/index.json (Liste aller Karussells für die App)

Inhaltsdatei (alle Texte Deutsch, Schweizer Schreibweise, keine Gedankenstriche):
{
 "datum": "2026-11-03", "ticker": "GOOGL", "name": "Alphabet", "thema": "Quartalszahlen",
 "stand": "30.10.2026",
 "slides": [
  {"typ": "hook", "kicker": "ALPHABET · QUARTALSZAHLEN", "titel": "...", "text": "...",
   "kpis": [{"label": "KURS", "wert": "279.84 $"}, {"label": "SEIT DEN ZAHLEN", "wert": "−13.9 %", "ton": "rot"}, ...3]},
  {"typ": "firma", "titel": "...", "text": "...", "fakten": [{"label": "Sitz", "wert": "USA"}, ...3]},
  {"typ": "zahlen", "titel": "...", "zeilen": [{"k": "Umsatz", "sub": "...", "wert": "+25 %", "ton": "gruen|orange|rot|"}, ...3-4], "erklaerung": "..."},
  {"typ": "skala", "titel": "...", "name": "Qualität", "wert": 85, "punkte": ["...", "...", "..."]},
  {"typ": "skala", "titel": "...", "name": "Timing", "wert": 43, "punkte": ["...", "..."]},
  {"typ": "marke", "titel": "...", "text": "...", "marke_label": "...", "marke": "270 $", "signal": "...",
   "szenarien": [{"art": "bruch", "titel": "Bricht sie", "text": "..."}, {"art": "halten", "titel": "Hält sie", "text": "..."}]},  (szenarien statt signal)
  {"typ": "fazit", "titel": "...", "absaetze": ["...", "..."], "frage": "..."}
 ],
 "caption": "...", "hashtags": ["#aktien", ...]
}
"""
import html, json, os, sys, asyncio

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = json.load(open(os.path.join(ROOT, "pipeline", "karussell.json"))) if os.path.exists(os.path.join(ROOT, "pipeline", "karussell.json")) else {}
MARKE = CFG.get("marke", "AKTIEN-AMPEL")
HANDLE = CFG.get("handle", "")
DISCLAIMER = "Persönliche Meinung, keine Anlageberatung. Mach deine eigene Recherche."
TON = {"gruen": "#1F6B45", "orange": "#B9500E", "rot": "#B3261E", "": "#121212", None: "#121212"}
MON = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]
TAGE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
e = lambda s: html.escape(str(s or ""))

CSS = """
*{box-sizing:border-box}body{margin:0;background:#F4F1EA}
.s{width:1080px;height:1350px;background:#F4F1EA;color:#121212;font-family:'Inter Tight',system-ui,sans-serif;padding:96px 88px 80px;display:flex;flex-direction:column;overflow:hidden}
.k{font-size:32px;font-weight:700;letter-spacing:.22em;color:#B9500E}
.h{margin:30px 0 0;font-size:96px;font-weight:800;letter-spacing:-.045em;line-height:1}
.serif{font-family:'Source Serif 4',Georgia,serif}
.p{font-family:'Source Serif 4',Georgia,serif;font-size:38px;line-height:1.45;color:#2A2620;margin:0}
.foot{margin-top:auto;display:flex;justify-content:space-between;font-size:26px;color:#4A4640}
.foot b{color:#121212}
.row{display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:baseline;gap:24px;padding:28px 0;border-bottom:1px solid #C9C3B8}
.row:last-child{border-bottom:3px solid #121212}
.rk{font-size:40px;font-weight:700}.rs{font-family:'Source Serif 4',Georgia,serif;font-size:30px;color:#4A4640}
.rv{font-size:64px;font-weight:800;letter-spacing:-.03em;white-space:nowrap}
.bar{position:relative;height:28px;display:grid;grid-template-columns:30fr 15fr 15fr 15fr 25fr;gap:4px}
.mark{position:absolute;top:-12px;width:8px;height:52px;margin-left:-4px;border-radius:4px;background:#121212}
ul.pt{margin:0;padding:0;list-style:none;display:flex;flex-direction:column;gap:36px}
ul.pt li{display:grid;grid-template-columns:52px minmax(0,1fr);gap:16px;font-family:'Source Serif 4',Georgia,serif;font-size:42px;line-height:1.4;color:#2A2620}
ul.pt li span{font-family:'Inter Tight',sans-serif;font-weight:800;color:#B9500E}
"""


def datum_lang(iso):
    import datetime as dt
    d = dt.date.fromisoformat(iso)
    return f"{TAGE[d.weekday()]}, {d.day}. {MON[d.month - 1]} {d.year}"


def fuss(i, n, extra=""):
    zusatz = extra or HANDLE
    return f'<div class="foot"><span>{e(MARKE)}{" · " + e(zusatz) if zusatz else ""}</span><b>{i} / {n}</b></div>'


def ampel_farbe(v):
    return "#2E8B57" if v >= 75 else "#5E9E2E" if v >= 60 else "#8A6D00" if v >= 45 else "#B9500E" if v >= 30 else "#B3261E"


def ampel_name(v):
    return "grün" if v >= 75 else "hellgrün" if v >= 60 else "gelb" if v >= 45 else "orange" if v >= 30 else "rot"


def szen(s):
    """Zwei Szenarien unter der Marke: Bruch (rot) und Halten (grün)."""
    farbe = {"bruch": "#B3261E", "halten": "#1F6B45"}
    teile = "".join(f'<div style="display:flex;flex-direction:column;gap:10px;padding:28px 0;border-bottom:1px solid #C9C3B8">'
                    f'<span style="font-size:30px;font-weight:800;letter-spacing:.14em;color:{farbe.get(x.get("art"), "#121212")}">{e(x["titel"]).upper()}</span>'
                    f'<span class="serif" style="font-size:36px;line-height:1.4;color:#2A2620">{e(x["text"])}</span></div>' for x in s["szenarien"][:2])
    return f'<div style="margin-top:24px">{teile}</div>'


def slide(d, s, i, n):
    t = s["typ"]
    k = f'<span class="k">{i:02d} · {e(s.get("kicker") or "")}</span>'
    if t == "hook":
        kp = "".join(f'<span style="display:flex;flex-direction:column;gap:6px"><span style="font-size:24px;font-weight:600;color:#4A4640">{e(x["label"])}</span>'
                     f'<span style="font-size:54px;font-weight:800;letter-spacing:-.03em;color:{TON.get(x.get("ton"), "#121212")}">{e(x["wert"])}</span></span>' for x in s.get("kpis", [])[:3])
        return f'''<div class="s">
<div style="display:flex;justify-content:space-between;align-items:baseline;border-bottom:3px solid #121212;padding-bottom:22px">
<span style="font-size:34px;font-weight:900;letter-spacing:-.02em">{e(MARKE)}</span><span style="font-size:26px;font-weight:500;color:#4A4640">{e(datum_lang(d["datum"]))}</span></div>
<span class="k" style="margin-top:72px">{e(s.get("kicker"))}</span>
<h1 class="h" style="margin-top:36px;font-size:{s.get("groesse", 112)}px;line-height:.98">{e(s["titel"])}</h1>
<p class="p" style="margin-top:44px;font-size:40px;color:#3A3630;max-width:880px">{e(s.get("text"))}</p>
<div style="margin-top:auto;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));border-top:2px solid #121212;padding-top:30px;gap:24px">{kp}</div>
<div style="margin-top:40px;display:flex;justify-content:space-between;font-size:26px;color:#4A4640"><span>Stand {e(d.get("stand"))}{" · " + e(HANDLE) if HANDLE else ""}</span><b style="color:#121212">Weiter wischen →</b></div></div>'''
    if t == "firma":
        fk = "".join(f'<div style="display:flex;justify-content:space-between;gap:24px;padding:32px 0;border-bottom:1px solid #C9C3B8"><span style="font-size:36px;color:#4A4640">{e(x["label"])}</span><span style="font-size:42px;font-weight:700;text-align:right">{e(x["wert"])}</span></div>' for x in s.get("fakten", []))
        return f'''<div class="s">{k}<h2 class="h">{e(s["titel"])}</h2>
<p class="p" style="margin-top:48px;font-size:46px">{e(s.get("text"))}</p>
<div style="margin-top:72px;border-top:3px solid #121212">{fk}</div>{fuss(i, n)}</div>'''
    if t == "zahlen":
        rows = "".join(f'<div class="row"><span style="display:flex;flex-direction:column;gap:4px"><span class="rk">{e(z["k"])}</span><span class="rs">{e(z.get("sub"))}</span></span>'
                       f'<span class="rv" style="color:{TON.get(z.get("ton"), "#121212")}">{e(z["wert"])}</span></div>' for z in s.get("zeilen", [])[:4])
        return f'''<div class="s">{k}<h2 class="h">{e(s["titel"])}</h2>
<div style="margin-top:52px;border-top:3px solid #121212">{rows}</div>
<p class="p" style="margin-top:44px;font-size:34px;color:#3A3630">{e(s.get("erklaerung"))}</p>{fuss(i, n, s.get("quelle", ""))}</div>'''
    if t == "skala":
        v = int(s["wert"])
        pt = "".join(f'<li><span>{j + 1}</span>{e(p)}</li>' for j, p in enumerate(s.get("punkte", [])[:3]))
        return f'''<div class="s">{k}<h2 class="h">{e(s["titel"])}</h2>
<div style="margin-top:60px;display:flex;justify-content:space-between;align-items:baseline"><span style="font-size:48px;font-weight:800">{e(s["name"])}</span>
<span style="font-size:110px;font-weight:900;letter-spacing:-.04em;color:{ampel_farbe(v)}">{v}<span style="font-size:40px;color:#4A4640;font-weight:600"> / 100 · {ampel_name(v)}</span></span></div>
<div class="bar" style="margin-top:18px"><span style="background:#D9483B;border-radius:6px 0 0 6px"></span><span style="background:#E8893A"></span><span style="background:#E9C046"></span><span style="background:#8DBE4E"></span><span style="background:#2E8B57;border-radius:0 6px 6px 0"></span><span class="mark" style="left:{v}%"></span></div>
<ul class="pt" style="margin-top:80px">{pt}</ul>{fuss(i, n)}</div>'''
    if t == "marke":
        return f'''<div class="s">{k}<h2 class="h">{e(s["titel"])}</h2>
<p class="p" style="margin-top:40px;font-size:{40 if s.get("szenarien") else 44}px">{e(s.get("text"))}</p>
<div style="margin-top:{40 if s.get("szenarien") else 64}px;border-top:3px solid #121212;border-bottom:3px solid #121212;padding:{26 if s.get("szenarien") else 36}px 0;display:flex;justify-content:space-between;align-items:baseline;gap:24px">
<span style="font-size:32px;font-weight:700;letter-spacing:.12em;color:#B9500E">{e(s.get("marke_label", "DIE MARKE, DIE ICH BEOBACHTE"))}</span><span style="font-size:96px;font-weight:900;letter-spacing:-.04em">{e(s.get("marke"))}</span></div>
{szen(s) if s.get("szenarien") else f'<p class="p" style="margin-top:56px;font-size:42px;color:#2A2620">{e(s.get("signal"))}</p>'}{fuss(i, n)}</div>'''
    if t == "fazit":
        ab = "".join(f'<p class="p" style="font-size:42px">{e(a)}</p>' for a in s.get("absaetze", [])[:3])
        return f'''<div class="s">{k}<h2 class="h">{e(s["titel"])}</h2>
<div style="margin-top:48px;display:flex;flex-direction:column;gap:32px;font-size:42px">{ab}</div>
<div style="margin-top:52px;background:#121212;color:#F4F1EA;padding:44px 48px"><span style="font-size:50px;font-weight:800;letter-spacing:-.02em;line-height:1.15">{e(s.get("frage"))}</span></div>
<p style="margin:auto 0 0;font-size:26px;line-height:1.4;color:#4A4640">{DISCLAIMER} Stand {e(d.get("stand"))}.</p>
<div style="margin-top:20px;display:flex;justify-content:space-between;font-size:26px;color:#4A4640;border-top:2px solid #121212;padding-top:22px"><span>{e(MARKE)}{" · " + e(HANDLE) if HANDLE else ""}</span><b style="color:#121212">{i} / {n}</b></div></div>'''
    raise ValueError("Unbekannter Slide-Typ: " + t)


def seite(inhalt):
    return f'''<!doctype html><html lang="de"><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@500;600;700;800;900&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap">
<style>{CSS}</style></head><body>{inhalt}</body></html>'''


async def rendern(d, aus):
    from playwright.async_api import async_playwright
    n = len(d["slides"])
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
        for i, s in enumerate(d["slides"], 1):
            await pg.set_content(seite(slide(d, s, i, n)), wait_until="networkidle")
            await pg.evaluate("document.fonts.ready")
            await pg.screenshot(path=os.path.join(aus, f"{i}.png"), clip={"x": 0, "y": 0, "width": 1080, "height": 1350})
        await b.close()


def main(pfad):
    d = json.load(open(pfad))
    aus = os.path.join(ROOT, "karussell", d["datum"])
    os.makedirs(aus, exist_ok=True)
    asyncio.run(rendern(d, aus))
    cap = (d.get("caption", "").strip() + "\n\n" + DISCLAIMER + "\n\n" + " ".join(d.get("hashtags", []))).strip()
    open(os.path.join(aus, "caption.txt"), "w").write(cap + "\n")
    ip = os.path.join(ROOT, "data", "karussell", "index.json")
    idx = json.load(open(ip)) if os.path.exists(ip) else {"karussells": []}
    idx["karussells"] = [x for x in idx["karussells"] if x["datum"] != d["datum"]] + [{
        "datum": d["datum"], "ticker": d.get("ticker"), "name": d.get("name"), "thema": d.get("thema"),
        "titel": d["slides"][0].get("titel"), "bilder": len(d["slides"]), "caption": cap}]
    idx["karussells"].sort(key=lambda x: x["datum"], reverse=True)
    idx["karussells"] = idx["karussells"][:60]
    json.dump(idx, open(ip, "w"), ensure_ascii=False, indent=1)
    print("fertig:", aus)


if __name__ == "__main__":
    main(sys.argv[1])
