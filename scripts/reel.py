"""Motion-Reel aus der Karussell-Datei eines Tages (eigenständig, nicht die Folien).

Ablauf (je Szene 4 s = 8 Schläge bei 120 bpm, Musik aus scripts/klang.py läuft synchron):
  1 Einstieg  dunkel: Marke, Thema, Titel Wort für Wort, Kennzahlen zählen hoch
  2 Chart     hell: Kurs der letzten 12 Monate zeichnet sich, entscheidende Marke wird markiert
  3 Zahlen    die drei wichtigsten Zahlen fliegen rein
  4 Ampel     Qualität und Timing: Balken und Zeiger laufen auf den Wert
  5 Fazit     Frage an die Zuschauer, Hinweis aufs Karussell, Disclaimer
Fehlt etwas (z. B. keine Kursdaten), fällt die Szene weg.

  python scripts/reel.py 2026-11-10 [aus.mp4]     (Standard: karussell/2026-11-10/reel.mp4)

Braucht ffmpeg, numpy und Playwright (Chromium). Bilder werden Bild für Bild aufgenommen,
deshalb ist das Ergebnis immer gleich und unabhängig von der Rechnergeschwindigkeit.
"""
import json
import os
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(__file__))
import klang  # noqa: E402

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BREITE, HOEHE, FPS = 1080, 1920, 30
SZENE = 8 * klang.SCHLAG  # 4 s
DISCLAIMER = "Persönliche Meinung, keine Anlageberatung."

FARBE_HELL = {"gruen": "#1F6B45", "rot": "#B3261E", "orange": "#B9500E", "gelb": "#8A6D00", "": "#121212"}
FARBE_DUNKEL = {"gruen": "#3FD08A", "rot": "#FF5A47", "orange": "#FF9A3D", "gelb": "#F2C744", "": "#F4F1EA"}


def ampel(v):
    """Farbe und Stufe wie auf den Folien (scripts/karussell.py)."""
    if v >= 75:
        return "#2E8B57", "grün"
    if v >= 60:
        return "#5E9E2E", "hellgrün"
    if v >= 45:
        return "#8A6D00", "gelb"
    if v >= 30:
        return "#B9500E", "orange"
    return "#B3261E", "rot"


def zahl(s):
    """'+6.9 %' -> {vor:'+', wert:6.9, dez:1, nach:' %'} zum Hochzählen; None, wenn es keine Zahl ist."""
    m = re.match(r"^\s*([+\-−]?)(\d+(?:\.\d+)?)(.*)$", str(s or ""))
    if not m or m.group(3).startswith(".") or re.search(r"\d", m.group(3)):
        return None
    vor, num, nach = m.groups()
    return {"vor": vor, "wert": float(num), "dez": len(num.split(".")[1]) if "." in num else 0, "nach": nach}


def preis(s):
    m = re.search(r"\d+(?:\.\d+)?", str(s or "").replace("'", ""))
    return float(m.group()) if m else None


def daten(datum):
    with open(os.path.join(WURZEL, "data", "karussell", f"{datum}.json"), encoding="utf-8") as f:
        d = json.load(f)
    try:
        with open(os.path.join(WURZEL, "pipeline", "karussell.json"), encoding="utf-8") as f:
            cfg = json.load(f)
    except OSError:
        cfg = {}
    eigene = d.get("eigene_position")
    if eigene is None:
        try:
            with open(os.path.join(WURZEL, "data", "karussell", "index.json"), encoding="utf-8") as f:
                eigene = next((k.get("eigene_position") for k in json.load(f)["karussells"] if k["datum"] == datum), False)
        except (OSError, KeyError, ValueError):
            eigene = False

    stimmung = klang.stimmung_aus(d)
    akzent = {"gruen": "gruen", "gelb": "gelb", "rot": "rot"}[stimmung]
    sl = {}
    for s in d["slides"]:
        sl.setdefault(s["typ"], []).append(s)
    D = {"marke": cfg.get("marke", "AKTIEN-AMPEL"), "handle": cfg.get("handle", "@aktienampel26"),
         "akzent_dunkel": FARBE_DUNKEL[akzent], "akzent_hell": FARBE_HELL[akzent], "szenen": []}

    hook = (sl.get("hook") or [{}])[0]
    D["hook"] = {"kicker": hook.get("kicker", d.get("name", "")), "titel": hook.get("titel") or d.get("titel", ""),
                 "kpis": [{"label": k.get("label", ""), "wert": k.get("wert", ""), "z": zahl(k.get("wert")),
                           "farbe": FARBE_DUNKEL.get(k.get("ton") or "", FARBE_DUNKEL[""])} for k in hook.get("kpis", [])[:3]]}
    D["szenen"].append("hook")

    # Kursdaten aus der App (nur Watchlist-Aktien)
    try:
        with open(os.path.join(WURZEL, "data", "live.json"), encoding="utf-8") as f:
            live = json.load(f)["aktien"].get(d.get("ticker"), {})
        ch = live.get("chart") or {}
        # nur bis zum Datenstand des Karussells, damit Chart und Kennzahlen zusammenpassen
        m = re.match(r"(\d{1,2})\.(\d{1,2})\.(\d{4})", str(d.get("stand") or ""))
        bis = f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}" if m else "9999"
        kurse = [c for t, c in zip(ch.get("d", []), ch.get("c", [])) if t <= bis and isinstance(c, (int, float))][-252:]
    except (OSError, ValueError, KeyError):
        kurse = []
    mk = (sl.get("marke") or [{}])[0]
    if len(kurse) > 30:
        wtext = mk.get("marke") or next((k["wert"] for k in hook.get("kpis", []) if k.get("label") == "KURS"), "")
        w = re.search(r"\$|€|CHF|£|SEK|DKK|NOK", str(wtext))
        D["chart"] = {"name": d.get("name", ""), "kurse": kurse, "waehrung": w.group() if w else "",
                      "marke": preis(mk.get("marke")), "marke_label": mk.get("marke_label", ""),
                      "marke_text": (mk.get("marke") or "").replace("\xa0", " ")}
        D["szenen"].append("chart")

    za = (sl.get("zahlen") or [None])[0]
    if za and za.get("zeilen"):
        D["zahlen"] = {"kicker": za.get("kicker", ""), "titel": za.get("titel", ""),
                       "zeilen": [{"k": z.get("k", ""), "sub": z.get("sub", ""), "wert": z.get("wert", ""), "z": zahl(z.get("wert")),
                                   "farbe": FARBE_HELL.get(z.get("ton") or "", FARBE_HELL[""])} for z in za["zeilen"][:3]]}
        D["szenen"].append("zahlen")

    sk = [s for s in sl.get("skala", []) if isinstance(s.get("wert"), (int, float))][:2]
    if sk:
        D["ampel"] = {"skalen": [{"name": s.get("name", ""), "wert": s["wert"], "titel": s.get("titel", ""),
                                  "farbe": ampel(s["wert"])[0], "stufe": ampel(s["wert"])[1]} for s in sk]}
        D["szenen"].append("ampel")

    fz = (sl.get("fazit") or [{}])[0]
    D["fazit"] = {"titel": fz.get("titel", ""), "frage": fz.get("frage", ""),
                  "hinweis": DISCLAIMER + (" Offenlegung: Ich halte diese Aktie." if eigene else "")}
    D["szenen"].append("fazit")
    D["szenen"] = [{"typ": t, "s": i * SZENE} for i, t in enumerate(D["szenen"])]
    D["dauer"] = len(D["szenen"]) * SZENE
    return d, D, stimmung


SEITE = r"""<!doctype html><html lang="de"><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@500;600;700;800;900&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap">
<style>
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1080px;height:1920px;overflow:hidden;background:#0D0D0D}
.sz{position:absolute;inset:0;overflow:hidden;font-family:'Inter Tight',system-ui,sans-serif;visibility:hidden;will-change:transform}
.dunkel{background:#0D0D0D;color:#F4F1EA}
.hell{background:#F4F1EA;color:#121212}
.serif{font-family:'Source Serif 4',Georgia,serif}
.a{position:absolute;left:84px;right:84px}
.kicker{font-size:30px;font-weight:800;letter-spacing:.18em;text-transform:uppercase}
.titel{font-weight:900;letter-spacing:-.045em;line-height:.98}
.fuss{position:absolute;left:84px;right:84px;top:1450px;display:flex;align-items:center;gap:14px;font-size:24px;font-weight:700;letter-spacing:.16em;color:#6B655C}
.punkte{display:flex;gap:8px}.punkte i{display:block;width:14px;height:14px;border-radius:50%}
.wort{display:inline-block;margin-right:.22em;will-change:transform}
.bar{position:relative;height:34px;display:grid;grid-template-columns:30fr 15fr 15fr 15fr 25fr;gap:5px}
.zeiger{position:absolute;top:-16px;width:10px;height:66px;margin-left:-5px;border-radius:5px;background:#121212}
</style></head><body>
<script>
const D = __DATEN__;
const AMPEL = ["#E5533D", "#F2C744", "#3FD08A"];
const el = (tag, cls, eltern, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; if (eltern) eltern.appendChild(e); return e; };
const cl = x => x < 0 ? 0 : x > 1 ? 1 : x;
const pr = (t, a, d) => cl((t - a) / d);
const eo = x => 1 - Math.pow(1 - x, 3);
const ei = x => x * x * x;
const eio = x => x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
const eb = x => { const c1 = 1.7, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); };
const fmt = (z, x) => z.vor + x.toFixed(z.dez) + z.nach;
const zaehl = (e, z, roh, k) => { e.textContent = z ? fmt(z, z.wert * k) : roh; };
function rein(e, k, dy = 50, blur = 0) {  // Element einblenden, k von 0 bis 1
  e.style.opacity = cl(k * 1.4);
  e.style.transform = `translateY(${(1 - k) * dy}px)`;
  e.style.filter = blur ? `blur(${(1 - k) * blur}px)` : "";
}
function passen(e, max, min, maxH) {  // Schrift verkleinern, bis der Text in die Box passt
  let f = max; e.style.fontSize = f + "px";
  while (f > min && (e.scrollHeight > maxH || e.scrollWidth > e.clientWidth + 1)) { f -= 2; e.style.fontSize = f + "px"; }
}
function woerter(e, text) { e.textContent = ""; return text.split(/\s+/).filter(Boolean).map(w => el("span", "wort", e, w)); }
function fuss(sz) {
  const f = el("div", "fuss", sz); const p = el("div", "punkte", f);
  AMPEL.forEach(c => el("i", "", p).style.background = c);
  el("span", "", f, D.marke + " · " + D.handle);
}
const SZ = {};

function aufbauen() {
  for (const s of D.szenen) {
    const sz = el("div", "sz " + (s.typ === "hook" ? "dunkel" : "hell"), document.body);
    SZ[s.typ] = { el: sz, s: s.s };
    BAU[s.typ](sz, SZ[s.typ]);
  }
}

const BAU = {
  hook(sz, o) {
    o.glanz = el("div", "", sz);
    Object.assign(o.glanz.style, { position: "absolute", left: "-300px", top: "-100px", width: "1680px", height: "1680px",
      background: `radial-gradient(circle at 50% 50%, ${D.akzent_dunkel}55 0%, ${D.akzent_dunkel}14 35%, transparent 62%)` });
    o.gitter = el("div", "", sz);
    Object.assign(o.gitter.style, { position: "absolute", inset: "-200px",
      backgroundImage: "linear-gradient(rgba(244,241,234,.05) 2px, transparent 2px), linear-gradient(90deg, rgba(244,241,234,.05) 2px, transparent 2px)",
      backgroundSize: "120px 120px" });
    o.innen = el("div", "", sz); Object.assign(o.innen.style, { position: "absolute", inset: 0, transformOrigin: "50% 45%" });
    const logo = el("div", "a", o.innen); Object.assign(logo.style, { top: "250px", display: "flex", alignItems: "center", gap: "16px" });
    o.punkte = AMPEL.map(c => { const i = el("i", "", logo); Object.assign(i.style, { display: "block", width: "26px", height: "26px", borderRadius: "50%", background: c }); return i; });
    o.logo = el("span", "", logo, D.marke); Object.assign(o.logo.style, { marginLeft: "10px", fontSize: "30px", fontWeight: 800, letterSpacing: ".3em" });
    const k = el("div", "a", o.innen); k.style.top = "500px"; k.style.display = "flex"; k.style.alignItems = "center"; k.style.gap = "20px";
    o.strich = el("i", "", k); Object.assign(o.strich.style, { display: "block", width: "10px", height: "40px", background: D.akzent_dunkel, transformOrigin: "50% 100%" });
    o.kicker = el("span", "kicker", k, D.hook.kicker); o.kicker.style.color = D.akzent_dunkel;
    o.titel = el("div", "a titel", o.innen); o.titel.style.top = "580px"; o.titel.textContent = D.hook.titel;
    passen(o.titel, 132, 70, 640);
    o.woerter = woerter(o.titel, D.hook.titel);
    const reihe = el("div", "a", o.innen); Object.assign(reihe.style, { top: "1270px", display: "flex", gap: "28px" });
    o.kpis = D.hook.kpis.map(kp => {
      const c = el("div", "", reihe); Object.assign(c.style, { flex: 1, borderTop: "3px solid #3A3630", paddingTop: "22px" });
      const l = el("div", "", c, kp.label); Object.assign(l.style, { fontSize: "24px", fontWeight: 700, letterSpacing: ".14em", color: "#9C968C" });
      const w = el("div", "", c, kp.wert); Object.assign(w.style, { fontSize: "60px", fontWeight: 900, letterSpacing: "-.03em", marginTop: "10px", color: kp.farbe, whiteSpace: "nowrap" });
      return { c, w, kp };
    });
    o.kpis.forEach(x => passen(x.w, 60, 34, 80));
  },
  chart(sz, o) {
    const C = D.chart, s = o.s;
    o.kopf = el("div", "a", sz); o.kopf.style.top = "250px";
    el("div", "kicker", o.kopf, "KURS · 12 MONATE").style.color = D.akzent_hell;
    const n = el("div", "titel", o.kopf, C.name); n.style.marginTop = "18px"; passen(n, 104, 60, 120);
    const r = el("div", "", o.kopf); Object.assign(r.style, { marginTop: "26px", display: "flex", alignItems: "baseline", gap: "26px" });
    o.preis = el("div", "", r); Object.assign(o.preis.style, { fontSize: "92px", fontWeight: 900, letterSpacing: "-.04em" });
    o.chip = el("div", "", r); Object.assign(o.chip.style, { fontSize: "40px", fontWeight: 800, padding: "8px 18px", color: "#F4F1EA" });
    const W = 912, H = 640, X = 84, Y = 690;
    const ns = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(ns, "svg"); svg.setAttribute("width", W); svg.setAttribute("height", H + 40);
    Object.assign(svg.style, { position: "absolute", left: X + "px", top: Y + "px", overflow: "visible" });
    sz.appendChild(svg);
    const k = C.kurse, werte = k.concat(C.marke ? [C.marke] : []);
    let lo = Math.min(...werte), hi = Math.max(...werte); const pad = (hi - lo) * .08; lo -= pad; hi += pad;
    o.px = i => i / (k.length - 1) * (W - 40);
    o.py = v => H - (v - lo) / (hi - lo) * H;
    for (let g = 0; g <= 3; g++) {
      const v = lo + (hi - lo) * (g + .5) / 4, y = o.py(v);
      const l = document.createElementNS(ns, "line"); Object.assign(l, {}); l.setAttribute("x1", 0); l.setAttribute("x2", W); l.setAttribute("y1", y); l.setAttribute("y2", y);
      l.setAttribute("stroke", "#DDD7CB"); l.setAttribute("stroke-width", 2); svg.appendChild(l);
      const tx = document.createElementNS(ns, "text"); tx.setAttribute("x", W); tx.setAttribute("y", y - 10); tx.setAttribute("text-anchor", "end");
      tx.setAttribute("font-size", 24); tx.setAttribute("fill", "#8A847A"); tx.setAttribute("font-family", "Inter Tight"); tx.setAttribute("font-weight", 600);
      tx.textContent = v.toFixed(v < 100 ? 2 : 0); svg.appendChild(tx);
    }
    const defs = document.createElementNS(ns, "defs");
    defs.innerHTML = `<linearGradient id="fl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${D.akzent_hell}" stop-opacity=".28"/><stop offset="1" stop-color="${D.akzent_hell}" stop-opacity="0"/></linearGradient>`;
    svg.appendChild(defs);
    o.flaeche = document.createElementNS(ns, "path"); o.flaeche.setAttribute("fill", "url(#fl)"); svg.appendChild(o.flaeche);
    o.linie = document.createElementNS(ns, "path"); o.linie.setAttribute("fill", "none"); o.linie.setAttribute("stroke", "#121212");
    o.linie.setAttribute("stroke-width", 6); o.linie.setAttribute("stroke-linejoin", "round"); o.linie.setAttribute("stroke-linecap", "round"); svg.appendChild(o.linie);
    if (C.marke) {
      const y = o.py(C.marke);
      o.mlinie = document.createElementNS(ns, "line"); o.mlinie.setAttribute("x1", 0); o.mlinie.setAttribute("y1", y); o.mlinie.setAttribute("y2", y);
      o.mlinie.setAttribute("stroke", D.akzent_hell); o.mlinie.setAttribute("stroke-width", 5); o.mlinie.setAttribute("stroke-dasharray", "18 12"); svg.appendChild(o.mlinie);
      o.mlabel = el("div", "", sz, (C.marke_label ? C.marke_label + " · " : "") + C.marke_text);
      const oben = y > 120;
      Object.assign(o.mlabel.style, { position: "absolute", left: X + "px", top: (Y + y + (oben ? -86 : 22)) + "px", background: "#121212", color: "#F4F1EA",
        fontSize: "28px", fontWeight: 800, letterSpacing: ".08em", padding: "12px 20px", transformOrigin: "0 50%" });
    }
    o.kopfpunkt = document.createElementNS(ns, "circle"); o.kopfpunkt.setAttribute("r", 13); o.kopfpunkt.setAttribute("fill", D.akzent_hell); svg.appendChild(o.kopfpunkt);
    o.ring = document.createElementNS(ns, "circle"); o.ring.setAttribute("fill", "none"); o.ring.setAttribute("stroke", D.akzent_hell); o.ring.setAttribute("stroke-width", 4); svg.appendChild(o.ring);
    o.H = H;
    fuss(sz);
  },
  zahlen(sz, o) {
    const Z = D.zahlen;
    const kopf = el("div", "a", sz); kopf.style.top = "250px";
    el("div", "kicker", kopf, Z.kicker).style.color = D.akzent_hell;
    const t = el("div", "titel", kopf, Z.titel); t.style.marginTop = "18px"; passen(t, 100, 60, 220);
    o.zeilen = Z.zeilen.map((z, i) => {
      const r = el("div", "a", sz); Object.assign(r.style, { top: (600 + i * 250) + "px", height: "230px" });
      const linie = el("div", "", r); Object.assign(linie.style, { height: i ? "2px" : "4px", background: i ? "#CFC8BA" : "#121212", transformOrigin: "0 50%" });
      const box = el("div", "", r); Object.assign(box.style, { display: "flex", justifyContent: "space-between", alignItems: "center", gap: "30px", paddingTop: "40px" });
      const links = el("div", "", box); links.style.minWidth = 0;
      const k = el("div", "", links, z.k); Object.assign(k.style, { fontSize: "46px", fontWeight: 800, letterSpacing: "-.02em" });
      const sub = el("div", "serif", links, z.sub); Object.assign(sub.style, { fontSize: "30px", color: "#5A544B", marginTop: "8px" });
      const w = el("div", "", box, z.wert); Object.assign(w.style, { fontSize: "84px", fontWeight: 900, letterSpacing: "-.04em", color: z.farbe, whiteSpace: "nowrap" });
      passen(k, 46, 32, 60); passen(sub, 30, 22, 80);
      return { r, linie, box, w, z };
    });
    fuss(sz);
  },
  ampel(sz, o) {
    const kopf = el("div", "a", sz); kopf.style.top = "250px";
    el("div", "kicker", kopf, "DIE AMPEL").style.color = D.akzent_hell;
    const t = el("div", "titel", kopf, D.ampel.skalen.map(s => s.name).join(" und ")); t.style.marginTop = "18px"; passen(t, 100, 60, 220);
    o.bl = D.ampel.skalen.map((s, i) => {
      const b = el("div", "a", sz); b.style.top = (560 + i * 430) + "px";
      const zeile = el("div", "", b); Object.assign(zeile.style, { display: "flex", alignItems: "baseline", gap: "22px" });
      const name = el("div", "", zeile, s.name); Object.assign(name.style, { fontSize: "44px", fontWeight: 800, width: "260px" });
      const zahl = el("div", "", zeile, "0"); Object.assign(zahl.style, { fontSize: "150px", fontWeight: 900, letterSpacing: "-.05em", color: s.farbe, lineHeight: .9 });
      const rest = el("div", "", zeile, "/ 100 · " + s.stufe); Object.assign(rest.style, { fontSize: "36px", fontWeight: 700, color: "#4A4640" });
      const bar = el("div", "bar", b); bar.style.marginTop = "40px";
      ["#D9483B", "#E8893A", "#E9C046", "#8DBE4E", "#2E8B57"].forEach((c, j) => { const sp = el("span", "", bar); sp.style.background = c; sp.style.transformOrigin = "0 50%";
        if (j === 0) sp.style.borderRadius = "8px 0 0 8px"; if (j === 4) sp.style.borderRadius = "0 8px 8px 0"; });
      const z = el("span", "zeiger", bar);
      const tt = el("div", "serif", b, s.titel); Object.assign(tt.style, { fontSize: "36px", color: "#3A3630", marginTop: "36px" });
      return { b, zahl, bar, z, tt, s, teile: [...bar.children].slice(0, 5) };
    });
    fuss(sz);
  },
  fazit(sz, o) {
    const F = D.fazit;
    const kopf = el("div", "a", sz); kopf.style.top = "250px";
    el("div", "kicker", kopf, "MEIN FAZIT").style.color = D.akzent_hell;
    o.titel = el("div", "titel", kopf, F.titel); o.titel.style.marginTop = "18px"; passen(o.titel, 104, 60, 230);
    o.box = el("div", "a", sz); Object.assign(o.box.style, { top: "600px", background: "#121212", color: "#F4F1EA", padding: "50px 54px" });
    o.frage = el("div", "", o.box, F.frage); Object.assign(o.frage.style, { fontWeight: 800, letterSpacing: "-.02em", lineHeight: 1.15 });
    passen(o.frage, 62, 36, 380);
    o.woerter = woerter(o.frage, F.frage);
    o.cta = el("div", "a", sz); Object.assign(o.cta.style, { top: "1110px", transformOrigin: "0 50%" });
    const l1 = el("div", "", o.cta, "Alle Zahlen und beide Szenarien"); Object.assign(l1.style, { fontSize: "40px", fontWeight: 700, color: "#3A3630" });
    const l2 = el("div", "", o.cta); Object.assign(l2.style, { display: "flex", alignItems: "center", gap: "18px", marginTop: "10px" });
    el("span", "", l2, "im Karussell auf").style.cssText = "font-size:40px;font-weight:700;color:#3A3630";
    o.handle = el("span", "", l2, D.handle); Object.assign(o.handle.style, { fontSize: "48px", fontWeight: 900, color: D.akzent_hell });
    o.pfeil = el("span", "", l2, "→"); Object.assign(o.pfeil.style, { fontSize: "52px", fontWeight: 900, display: "inline-block" });
    o.hinweis = el("div", "a", sz, F.hinweis); Object.assign(o.hinweis.style, { top: "1370px", fontSize: "26px", color: "#5A544B", fontWeight: 600 });
    fuss(sz);
  },
};

const ZEIGE = {
  hook(o, t) {
    o.glanz.style.transform = `translate(${Math.sin(t * .7) * 60}px, ${t * 18}px) scale(${1 + t * .03})`;
    o.gitter.style.transform = `translateY(${-t * 30}px)`;
    o.innen.style.transform = `scale(${1 + .035 * eio(pr(t, 0, 4))})`;
    o.punkte.forEach((p, i) => { const k = eb(pr(t, i * .12, .3)); p.style.transform = `scale(${k})`; p.style.opacity = cl(k * 2); });
    rein(o.logo, eo(pr(t, .3, .4)), 0);
    o.strich.style.transform = `scaleY(${eo(pr(t, .5, .3))})`;
    const kk = eo(pr(t, .55, .45)); o.kicker.style.clipPath = `inset(0 ${(1 - kk) * 100}% 0 0)`;
    const nw = o.woerter.length, abst = Math.min(.17, 1.3 / Math.max(1, nw));
    o.woerter.forEach((w, i) => rein(w, eo(pr(t, .85 + i * abst, .38)), 90, 16));
    o.kpis.forEach((x, j) => { const k = eo(pr(t, 2.45 + j * .17, .4)); rein(x.c, k, 40); zaehl(x.w, x.kp.z, x.kp.wert, eo(pr(t, 2.45 + j * .17, .8))); });
  },
  chart(o, t) {
    const C = D.chart, k = C.kurse, n = k.length;
    const fort = eio(pr(t, .2, 2.0)), kopf = Math.max(1, Math.round(fort * (n - 1)));
    let d = "";
    for (let i = 0; i <= kopf; i++) d += (i ? "L" : "M") + o.px(i).toFixed(1) + " " + o.py(k[i]).toFixed(1);
    o.linie.setAttribute("d", d);
    o.flaeche.setAttribute("d", d + `L${o.px(kopf).toFixed(1)} ${o.H}L0 ${o.H}Z`);
    const hx = o.px(kopf), hy = o.py(k[kopf]);
    o.kopfpunkt.setAttribute("cx", hx); o.kopfpunkt.setAttribute("cy", hy);
    const puls = (t * 2) % 1; o.ring.setAttribute("cx", hx); o.ring.setAttribute("cy", hy); o.ring.setAttribute("r", 13 + puls * 30); o.ring.setAttribute("opacity", 1 - puls);
    const z = { vor: "", wert: k[kopf], dez: k[kopf] < 1000 ? 2 : 0, nach: C.waehrung ? " " + C.waehrung : "" };
    o.preis.textContent = fmt(z, k[kopf]);
    const ch = (k[kopf] / k[0] - 1) * 100;
    o.chip.textContent = (ch >= 0 ? "+" : "−") + Math.abs(ch).toFixed(0) + " %";
    o.chip.style.background = ch >= 0 ? "#1F6B45" : "#B3261E";
    o.chip.style.opacity = cl(fort * 3);
    if (o.mlinie) {
      o.mlinie.setAttribute("x2", 912 * eo(pr(t, 2.3, .45)));
      o.mlinie.style.opacity = pr(t, 2.3, .05);
      const m = eb(pr(t, 2.6, .4)); o.mlabel.style.transform = `scale(${m})`; o.mlabel.style.opacity = cl(m * 2);
    }
  },
  zahlen(o, t) {
    o.zeilen.forEach((x, i) => {
      const a = .35 + i * .5, k = eo(pr(t, a, .45));
      x.linie.style.transform = `scaleX(${eo(pr(t, a - .1, .5))})`;
      x.box.style.opacity = cl(k * 1.5); x.box.style.transform = `translateX(${(1 - k) * 160}px)`;
      zaehl(x.w, x.z.z, x.z.wert, eo(pr(t, a, .9)));
    });
  },
  ampel(o, t) {
    o.bl.forEach((x, i) => {
      const a = .3 + i * 1.1, k = eo(pr(t, a, .4));
      x.b.style.opacity = cl(k * 1.5); x.b.style.transform = `translateY(${(1 - k) * 40}px)`;
      x.teile.forEach((p, j) => p.style.transform = `scaleX(${eo(pr(t, a + j * .06, .3))})`);
      const w = eio(pr(t, a + .3, 1.0));
      x.z.style.left = (x.s.wert * w) + "%";
      x.zahl.textContent = Math.round(x.s.wert * w);
      rein(x.tt, eo(pr(t, a + 1.0, .4)), 20);
    });
  },
  fazit(o, t) {
    const k = eo(pr(t, .25, .45));
    o.box.style.transform = `translateX(${(k - 1) * 110}%)`;
    const nw = o.woerter.length, abst = Math.min(.09, .9 / Math.max(1, nw));
    o.woerter.forEach((w, i) => rein(w, eo(pr(t, .55 + i * abst, .3)), 30, 8));
    rein(o.cta, eo(pr(t, 1.8, .45)), 40);
    const schlag = pr(t, 3.0, .35); const pump = schlag > 0 && schlag < 1 ? Math.sin(schlag * Math.PI) * .06 : 0;
    o.cta.style.transform += ` scale(${1 + pump})`;
    o.pfeil.style.transform = `translateX(${Math.max(0, Math.sin((t - 1.8) * Math.PI * 2)) * 14}px)`;
    rein(o.hinweis, eo(pr(t, .4, .4)), 0);
  },
};

const UEBERGANG = .3;
function zeige(t) {
  const sz = D.szenen;
  sz.forEach((s, i) => {
    const o = SZ[s.typ], ende = i + 1 < sz.length ? sz[i + 1].s : D.dauer + 1;
    const sichtbar = t >= s.s - (i ? UEBERGANG : 0) && t < ende;
    o.el.style.visibility = sichtbar ? "visible" : "hidden";
    o.el.style.zIndex = i;
    if (!sichtbar) return;
    let tr = "";
    if (i && t < s.s) {  // Szene schiebt sich herein: Chart von unten, die anderen von rechts
      const k = ei(pr(t, s.s - UEBERGANG, UEBERGANG));
      tr = i === 1 ? `translateY(${(1 - k) * 100}%)` : `translateX(${(1 - k) * 100}%)`;
    } else if (i + 1 < sz.length && i + 1 > 1 && t >= ende - UEBERGANG) {
      tr = `translateX(${-ei(pr(t, ende - UEBERGANG, UEBERGANG)) * 30}%)`;
    }
    o.el.style.transform = tr;
    ZEIGE[s.typ](o, t - s.s);
  });
}

async function vorbereiten() {
  await Promise.all(["900 100px 'Inter Tight'", "800 40px 'Inter Tight'", "700 30px 'Inter Tight'", "600 30px 'Inter Tight'",
    "400 30px 'Source Serif 4'"].map(f => document.fonts.load(f)));
  await document.fonts.ready;
  aufbauen();
  zeige(0);
  return true;
}
</script></body></html>"""


def aufnehmen(D, wav, aus):
    from playwright.sync_api import sync_playwright
    html = SEITE.replace("__DATEN__", json.dumps(D, ensure_ascii=False))
    bilder = int(round(D["dauer"] * FPS))
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "-",
           "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-r", str(FPS),
           "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-ac", "2", "-shortest", "-movflags", "+faststart", aus]
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": BREITE, "height": HOEHE}, device_scale_factor=1)
        pg.set_content(html, wait_until="networkidle")
        pg.evaluate("vorbereiten()")
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        try:
            for i in range(bilder):
                pg.evaluate(f"zeige({i / FPS:.4f})")
                proc.stdin.write(pg.screenshot(type="jpeg", quality=92))
        finally:
            proc.stdin.close()
            proc.wait()
        b.close()
    if proc.returncode:
        raise SystemExit(f"ffmpeg Fehler {proc.returncode}")


def bauen(datum, aus=None):
    d, D, stimmung = daten(datum)
    aus = aus or os.path.join(WURZEL, "karussell", datum, "reel.mp4")
    os.makedirs(os.path.dirname(aus), exist_ok=True)
    schnitte = [s["s"] for s in D["szenen"][1:]]
    mix, info = klang.erzeugen(stimmung, D["dauer"], seed=datum, schnitte=schnitte)
    with tempfile.TemporaryDirectory() as tmp:
        wav = os.path.join(tmp, "klang.wav")
        klang.speichern(mix, wav)
        aufnehmen(D, wav, aus)
    print(f"{aus}: {D['dauer']:.0f} s, {os.path.getsize(aus) / 1e6:.1f} MB, Stimmung {stimmung}, "
          f"Szenen {', '.join(s['typ'] for s in D['szenen'])}")
    return aus, D


if __name__ == "__main__":
    bauen(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
