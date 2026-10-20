/* Aktien-Ampel – App-Logik (ohne Framework, läuft direkt auf GitHub Pages) */
(() => {
"use strict";

const REPO = "pasidreamer/Aktien-Analyse";
const NOTES_PATH = "data/notizen.json";
const STATE = { chartRange: (() => { try { return JSON.parse(localStorage.getItem("chartRange")) || "1J"; } catch { return "1J"; } })(), stocks: [], live: null, verlauf: {}, notes: {}, filter: { q: "", stil: "Alle", region: "Alle", status: "Alle", nurGut: false, sort: "chance" } };
const $view = document.getElementById("view");

// ---------- Hilfen ----------
const store = {
  get(k, d) { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch { return d; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch {} }
};
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const ampel = v => v >= 75 ? "gruen" : v >= 60 ? "hellgruen" : v >= 45 ? "gelb" : v >= 30 ? "orange" : "rot";
const ampelName = { gruen: "grün", hellgruen: "hellgrün", gelb: "gelb", orange: "orange", rot: "rot" };
const ampelVar = c => `var(--${c})`;
const nf = (v, d = 2) => v == null || isNaN(v) ? "–" : Number(v).toLocaleString("de-CH", { minimumFractionDigits: d, maximumFractionDigits: d });
const cur = w => ({ USD: "$", CHF: "CHF", EUR: "€", GBp: "p", GBP: "£" }[w] || w);
const money = (v, w) => {
  if (v == null) return "–";
  const d = w === "GBp" ? 1 : v >= 1000 ? 0 : 2;
  const s = nf(v, d);
  return w === "USD" ? `${s} $` : w === "EUR" ? `${s} €` : `${s} ${cur(w)}`;
};
const pct = (v, d = 1) => v == null ? "–" : `${v > 0 ? "+" : v < 0 ? "−" : ""}${nf(Math.abs(v), d)} %`;
const fmtDate = iso => { if (!iso || !/^\d{4}-\d{2}-\d{2}/.test(iso)) return iso || "–"; const [y, m, d] = iso.slice(0, 10).split("-"); return `${d}.${m}.${y}`; };
const daysUntil = iso => { const t = new Date(iso + "T12:00:00"); return Math.round((t - new Date()) / 864e5); };
const regionCode = { "USA": "US", "Schweiz": "CH", "Grossbritannien": "UK", "Frankreich": "FR", "Deutschland": "DE", "Niederlande": "NL", "Italien": "IT", "Japan": "JP" };
const STATUS = {
  in_zone: ["In Kaufzone", "b-zone"], nahe_zone: ["Nahe Kaufzone", "b-nahe"], trigger: ["Trigger ausgelöst", "b-trig"],
  ueber_trigger: ["Über Trigger", "b-trig"], abbruch: ["Abbruch-Marke gebrochen", "b-abb"], unter_abbruch: ["Unter Abbruch-Marke", "b-warn"]
};
const LISTE = { depot: "Im Depot", kaufliste: "Kaufliste", beobachten: "Beobachten", archiv: "Archiv" };
const MON = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"];
const todayIso = () => new Date().toISOString().slice(0, 10);
const addDays = (iso, n) => { const d = new Date(iso + "T12:00:00"); d.setDate(d.getDate() + n); return d.toISOString().slice(0, 10); };

// Dividende: feste Angaben aus der Analyse (div_info) plus automatisch geholte Historie (live.div)
function divData(s, L) {
  const d = s.div_info || {}, a = L?.div || null;
  if (d.zahlt === false || (!a && !d.betrag)) return { zahlt: false, text: d.text };
  const heute = todayIso();
  const betrag = a?.letzte?.[1] ?? d.betrag;
  const rendite = a?.rendite ?? (parseFloat(String(s.dividende || "").replace(",", ".")) || null);
  let next = null;
  const ang = d.angekuendigt;
  if (ang && (ang.zahltag || ang.ex) >= heute) next = { ex: ang.ex, pay: ang.zahltag, betrag: ang.betrag ?? betrag, sicher: true };
  else if (a?.naechste_ex_erwartet) next = { ex: a.naechste_ex_erwartet, pay: d.abstand_tage != null ? addDays(a.naechste_ex_erwartet, d.abstand_tage) : null, betrag, sicher: false };
  return {
    zahlt: true, betrag, rendite, next,
    rhythmus: d.rhythmus || a?.rhythmus, proJahr: d.pro_jahr || a?.pro_jahr,
    system: d.system, exM: d.ex_monate || a?.ex_monate || [], payM: d.zahl_monate || [],
    zahlText: d.zahl_text, serie: d.serie, text: d.text, summe: a?.summe_12m,
    hist: (a?.historie || []).slice(-8).reverse()
  };
}
const renditeOf = v => { const r = divData(v.s, v.L); return r.zahlt ? (r.rendite || 0) : 0; };

// Form der Ausschüttung (Währung, Steuern) nach Land
function divForm(s) {
  const d = s.div_info || {};
  if (d.form) return d.form;
  if (s.land === "USA") return "Bar in US-Dollar aufs Konto. Die USA ziehen Quellensteuer ab, mit dem Formular W-8BEN bei Saxo in der Regel 15 %.";
  if (s.land === "Schweiz") return "Bar in Franken aufs Konto. Abzug von 35 % Verrechnungssteuer, die du mit der Steuererklärung zurückbekommst.";
  if (s.land === "Grossbritannien") return s.waehrung === "USD"
    ? "Bar in US-Dollar (über die US-Variante der Aktie, ADR). Grossbritannien zieht keine Quellensteuer ab, die ADR-Bank behält eine kleine Gebühr."
    : "Bar in Pfund aufs Konto. Grossbritannien zieht keine Quellensteuer ab.";
  if (s.land === "Frankreich") return "Bar in Euro aufs Konto. Frankreich zieht Quellensteuer ab (je nach Bank 12.8 bis 25 %), einen Teil kannst du über die Steuererklärung anrechnen lassen.";
  return `Bar in ${s.waehrung} aufs Konto, abzüglich Quellensteuer.`;
}

// Unterbewertung: heutiges KGV (mit dem Kurs mitgerechnet) gegen den eigenen 5-Jahres-Schnitt
function bewertungOf(s, kurs) {
  const b = s.bewertung;
  if (!b || !b.wert || !b.schnitt || !s.analyse.kurs) return null;
  const jetzt = b.wert * kurs / s.analyse.kurs;
  const abschlag = (1 - jetzt / b.schnitt) * 100;
  const stufe = abschlag >= 30 ? "stark unterbewertet" : abschlag >= 15 ? "unterbewertet" : abschlag > -10 ? "etwa fair bewertet" : "teurer als üblich";
  return { jetzt, schnitt: b.schnitt, typ: b.typ || "KGV", abschlag, stufe, unter: abschlag >= 20 };
}
const SCHUB = { stark: ["Starker Wachstumsschub möglich", "gruen"], mittel: ["Wachstumsschub möglich", "gelb"], schwach: ["Kein grosser Schub in Sicht", "orange"] };
const SORGE = { stimmung: "Vor allem Stimmung", gemischt: "Echte Probleme, eher lösbar", echt: "Das Geschäft verschlechtert sich" };
const FG = v => v < 25 ? ["Extreme Angst", "fg-0", "Viele verkaufen aus Angst. Solche Phasen waren in der Vergangenheit oft gute Zeitpunkte, um gute Aktien in kleinen Tranchen zu kaufen. Den genauen Tiefpunkt kennt aber niemand."]
  : v < 45 ? ["Angst", "fg-1", "Der Markt ist vorsichtig. Erste Gelegenheiten bei guten Firmen, aber noch keine Panik."]
  : v <= 55 ? ["Neutral", "fg-2", "Weder Angst noch Euphorie. Die einzelne Aktie und ihre Zonen sind wichtiger als der Gesamtmarkt."]
  : v <= 75 ? ["Gier", "fg-3", "Viel Optimismus. Nicht hinterherlaufen, lieber auf Rücksetzer in die Kaufzonen warten."]
  : ["Extreme Gier", "fg-4", "Euphorie. Rücksetzer werden wahrscheinlicher, darum beim Nachkaufen vorsichtig sein."];
const PESS = { hoch: ["Hoher Pessimismus", "fg-0"], "erhöht": ["Erhöhte Sorge", "fg-1"], normal: ["Normale Stimmung", "p-neutral"] };
const kontra = v => (v.L?.pessimismus?.wert ?? 0) >= 60 && v.q >= 50;

function marktHtml() {
  const m = STATE.live?.markt;
  if (!m || (!m.fear_greed && !m.sp500)) return "";
  const fg = m.fear_greed, sp = m.sp500, vix = m.vix;
  let gauge = "";
  if (fg) {
    const f = FG(fg.wert);
    const spark = (() => {
      const h = fg.verlauf || []; if (h.length < 10) return "";
      const W = 300, H = 46, X = i => i / (h.length - 1) * W, Y = v => H - v / 100 * H;
      return `<svg class="fg-spark" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none" role="img" aria-label="Fear and Greed Index im letzten Jahr">
        <rect x="0" y="${Y(25)}" width="${W}" height="${H - Y(25)}" fill="var(--accent-soft)"/><rect x="0" y="0" width="${W}" height="${Y(75)}" fill="var(--orange-soft)"/>
        <path d="${h.map((p, i) => `${i ? "L" : "M"}${X(i).toFixed(1)} ${Y(p[1]).toFixed(1)}`).join("")}" fill="none" stroke="var(--ink)" stroke-width="1.4" vector-effect="non-scaling-stroke"/></svg>
        <div class="fg-spark-leg"><span>vor 1 Jahr</span><span>blau: extreme Angst · orange: extreme Gier</span><span>heute</span></div>`;
    })();
    gauge = `<div class="fg-top"><div><span class="fg-lbl">Fear &amp; Greed Index</span><b class="fg-val">${fg.wert}</b><span class="pill ${f[1]}">${f[0]}</span></div>
      <div class="fg-cmp">Vortag ${fg.vortag} · vor 1 Woche ${fg.woche} · vor 1 Monat ${fg.monat}</div></div>
      <div class="fg-bar"><span></span><span></span><span></span><span></span><span></span><i style="left:${fg.wert}%"></i></div>
      <div class="fg-ticks"><span>Extreme Angst</span><span>Neutral</span><span>Extreme Gier</span></div>
      <p class="fg-txt">${esc(f[2])}</p>${spark}`;
  }
  const spTxt = sp ? `<div class="mk-row"><span><b>S&amp;P 500</b> ${nf(sp.kurs, 0)} ${chgHtml(sp.chg1)}</span><span>${sp.abstand_hoch > 0.5 ? nf(sp.abstand_hoch, 1) + " % unter dem Jahreshoch" : "nahe am Jahreshoch"}</span>
    <span>${sp.ueber_ema200 ? "über der EMA 200 (Aufwärtstrend)" : "unter der EMA 200 (Abwärtstrend)"}</span>${vix ? `<span>VIX ${nf(vix.kurs, 1)} ${vix.kurs >= 30 ? "(Panik)" : vix.kurs >= 20 ? "(nervös)" : "(ruhig)"}</span>` : ""}</div>` : "";
  return `<div class="sec"><h2>Marktstimmung</h2><p>Wie viel Angst oder Gier gerade im Gesamtmarkt steckt. Als Gegenspiegel: Extreme Angst kann eine Chance sein.</p></div>
    <div class="card markt">${gauge}${spTxt}</div>`;
}

// ---------- Daten ----------
async function getJSON(url) {
  const r = await fetch(url + (url.includes("?") ? "&" : "?") + "t=" + Date.now(), { cache: "no-store" });
  if (!r.ok) throw new Error(url + " " + r.status);
  return r.json();
}
async function load(force) {
  const [s, l, v, n, f, wu] = await Promise.allSettled([getJSON("data/stocks.json"), getJSON("data/live.json"), getJSON("data/verlauf.json"), loadNotes(), getJSON("data/fcf.json"), getJSON("data/wuensche.json")]);
  STATE.fcf = f.status === "fulfilled" ? f.value : null;
  STATE.wuensche = wu.status === "fulfilled" ? wu.value.wuensche || [] : [];
  if (s.status !== "fulfilled") throw new Error("stocks.json fehlt");
  STATE.stocks = s.value.aktien;
  STATE.stand = s.value.stand;
  STATE.live = l.status === "fulfilled" ? l.value : null;
  STATE.verlauf = v.status === "fulfilled" ? v.value : {};
  // Notizen: die neueste Fassung gewinnt (Gerät oder GitHub)
  const remote = n.status === "fulfilled" ? n.value : {};
  const local = store.get("notes_local", {});
  const all = { ...remote };
  for (const [k, x] of Object.entries(local)) if (!all[k] || (x.ts || 0) > (all[k].ts || 0)) all[k] = x;
  STATE.notes = all;
}

// ---------- Notizen (auf dem Gerät, mit GitHub-Schlüssel auf allen Geräten) ----------
const token = () => store.get("gh_token", "");
const b64 = str => btoa(unescape(encodeURIComponent(str)));
const unb64 = str => decodeURIComponent(escape(atob(str.replace(/\n/g, ""))));
async function ghGet() {
  const r = await fetch(`https://api.github.com/repos/${REPO}/contents/${NOTES_PATH}?t=${Date.now()}`, { headers: { Authorization: "Bearer " + token(), Accept: "application/vnd.github+json" }, cache: "no-store" });
  if (r.status === 404) return { sha: null, data: {} };
  if (!r.ok) throw new Error("GitHub " + r.status);
  const j = await r.json();
  return { sha: j.sha, data: JSON.parse(unb64(j.content) || "{}") };
}
async function loadNotes() {
  if (token()) { try { return (await ghGet()).data; } catch (e) { console.warn(e); } }
  try { return await getJSON(NOTES_PATH); } catch { return {}; }
}
async function syncNote(ticker) {
  if (!token()) return "local";
  for (let i = 0; i < 2; i++) {
    const cur = await ghGet();
    const merged = { ...cur.data };
    const mine = STATE.notes[ticker];
    if (mine && mine.text.trim()) merged[ticker] = mine; else delete merged[ticker];
    const body = { message: `Notiz ${ticker}`, content: b64(JSON.stringify(merged, null, 1)), ...(cur.sha ? { sha: cur.sha } : {}) };
    const r = await fetch(`https://api.github.com/repos/${REPO}/contents/${NOTES_PATH}`, { method: "PUT", headers: { Authorization: "Bearer " + token(), Accept: "application/vnd.github+json", "Content-Type": "application/json" }, body: JSON.stringify(body) });
    if (r.ok) { const local = store.get("notes_local", {}); delete local[ticker]; store.set("notes_local", local); return "github"; }
    if (r.status !== 409 && r.status !== 422) throw new Error("GitHub " + r.status);
  }
  throw new Error("Konflikt beim Speichern");
}

// Zonenstatus aus einem Kurs ableiten (falls noch keine Live-Daten da sind)
function zoneStatus(s, p) {
  const z = s.zonen || {}; let status = null, dist = null;
  const kauf = z.kauf || [];
  if (kauf.some(([lo, hi]) => p >= lo && p <= hi)) status = "in_zone";
  const below = kauf.filter(([lo]) => lo <= p);
  if (below.length) { const top = Math.max(...below.map(x => x[1])); dist = p > top ? (p / top - 1) * 100 : 0; }
  else if (kauf.length) dist = (p / Math.min(...kauf.map(x => x[0])) - 1) * 100;
  if (!status && dist != null && dist > 0 && dist <= 3) status = "nahe_zone";
  if (z.abbruch && p < z.abbruch) status = "unter_abbruch";
  return { status, dist };
}

// Eine Aktie mit Analyse- und Live-Daten zusammenführen
function view(s) {
  const L = STATE.live?.aktien?.[s.ticker];
  const qParts = s.qualitaet.map(p => ({ ...p, p0: p.p, p: L?.qteile?.find(x => x.k === p.k)?.p ?? p.p }));
  const tParts = s.timing.map(p => { const lp = L?.tteile?.find(x => x.k === p.k); return { ...p, p0: p.p, p: lp?.p ?? p.p, note: lp?.note || null }; });
  const q = qParts.reduce((a, b) => a + b.p, 0), t = tParts.reduce((a, b) => a + b.p, 0);
  const kurs = L?.kurs ?? s.analyse.kurs;
  const zs = L ? { status: L.status, dist: L.dist_zone } : zoneStatus(s, kurs);
  const chance = q >= 60 && (["in_zone", "nahe_zone", "trigger"].includes(zs.status) || t >= 60);
  const hist = STATE.verlauf[s.ticker] || [];
  const ref = hist.length > 5 ? hist[hist.length - 6] : null;
  return {
    s, L, q, t, qParts, tParts, kurs, chg1: L?.chg1 ?? null, datum: L?.datum ?? s.analyse.datenstand,
    status: zs.status, dist: zs.dist, chance, neu: !!L?.neu,
    dq: q - s.analyse.q, dt: t - s.analyse.t,
    trendT: ref ? t - ref[2] : 0,
    gesamt: Math.round((q + t) / 2),
    bew: bewertungOf(s, kurs), schub: s.chance?.schub_stufe === "stark",
    fcf: fcfAdj(STATE.fcf?.aktien?.[s.ticker], L)
  };
}

function reason(v) {
  const r = [];
  if (v.status === "in_zone") r.push("Kurs in der Kaufzone");
  if (v.status === "nahe_zone") r.push(`nur ${nf(v.dist, 1)} % über der Kaufzone`);
  if (v.status === "trigger") r.push("Trigger ausgelöst");
  if (v.t >= 60) r.push(`Timing ${ampelName[ampel(v.t)]}`);
  return r.join(", ");
}

// ---------- Bausteine ----------
const signal = (q, t, big) => `<span class="signal${big ? " big" : ""}" role="img" aria-label="Qualität ${q}, Timing ${t}">
  <span class="lamp ${ampel(q)}">${q}<small>Q</small></span><span class="lamp ${ampel(t)}">${t}<small>T</small></span></span>`;
const badge = st => st && STATUS[st] ? `<span class="badge ${STATUS[st][1]}">${STATUS[st][0]}</span>` : "";
const chgHtml = v => v == null ? "" : `<span class="chg ${v > 0 ? "up" : v < 0 ? "down" : ""}">${pct(v, 2)}</span>`;
const trendArrow = d => d >= 3 ? `<span class="trend up" title="Timing steigt">▲${d}</span>` : d <= -3 ? `<span class="trend down" title="Timing fällt">▼${-d}</span>` : "";

function rowHtml(v) {
  const s = v.s;
  return `<a class="row" href="#/aktie/${encodeURIComponent(s.ticker)}">
    ${signal(v.q, v.t)}
    <div class="mid"><div class="nm">${esc(s.name)}</div>
      <div class="sub">${esc(s.ticker)} · ${esc(regionCode[s.land] || s.land)} · ${esc(s.tags[0])}${window.Depot?.bestand(s.ticker) ? " · Im Depot" : s.status !== "beobachten" ? " · " + LISTE[s.status] : ""}${STATE.notes[s.ticker]?.text?.trim() ? " · Notiz" : ""}</div>
      ${v.bew?.unter || v.schub || kontra(v) ? `<div class="tags">${v.bew?.unter ? `<span class="tg tg-unter">${nf(v.bew.abschlag, 0)} % günstiger als üblich</span>` : ""}${v.schub ? '<span class="tg tg-schub">Wachstumsschub</span>' : ""}${kontra(v) ? '<span class="tg tg-kontra">Kontra-Signal</span>' : ""}</div>` : ""}</div>
    <div class="right"><div class="px">${money(v.kurs, s.waehrung)}</div><div>${chgHtml(v.chg1)}${trendArrow(v.trendT)}</div>
      ${badge(v.status)}${v.neu ? '<span class="badge b-neu">neu</span>' : ""}</div>
  </a>`;
}

// Chancen-Karte: Qualität (x) gegen Timing (y)
function mapHtml(list) {
  const W = 320, H = 236, P = { l: 26, r: 8, t: 10, b: 24 };
  const X = v => P.l + (v / 100) * (W - P.l - P.r), Y = v => H - P.b - (v / 100) * (H - P.t - P.b);
  const x60 = X(60), y60 = Y(60);
  const pts = list.map(v => ({ v, x: X(v.q), y: Y(v.t) }));
  // Beschriftungen so setzen, dass sie sich nicht überdecken
  const boxes = pts.map(p => ({ x0: p.x - 6, y0: p.y - 6, x1: p.x + 6, y1: p.y + 6 }));
  const hit = (a, b) => a.x0 < b.x1 && a.x1 > b.x0 && a.y0 < b.y1 && a.y1 > b.y0;
  const labels = [];
  [...pts].sort((a, b) => b.v.gesamt - a.v.gesamt).forEach(p => {
    const w = p.v.s.ticker.length * 5.4 + 2, h = 10;
    const cand = [
      { x: p.x + 8, y: p.y + 3.5, a: "start", b: { x0: p.x + 7, y0: p.y - 5, x1: p.x + 8 + w, y1: p.y + 5 } },
      { x: p.x - 8, y: p.y + 3.5, a: "end", b: { x0: p.x - 8 - w, y0: p.y - 5, x1: p.x - 7, y1: p.y + 5 } },
      { x: p.x, y: p.y - 8, a: "middle", b: { x0: p.x - w / 2, y0: p.y - 8 - h + 1, x1: p.x + w / 2, y1: p.y - 7 } },
      { x: p.x, y: p.y + 15, a: "middle", b: { x0: p.x - w / 2, y0: p.y + 6, x1: p.x + w / 2, y1: p.y + 16 } }
    ];
    const ok = cand.find(c => c.b.x0 >= P.l && c.b.x1 <= W - P.r && c.b.y0 >= P.t && c.b.y1 <= H - P.b
      && !boxes.some((bx, i) => pts[i] !== p && hit(bx, c.b)) && !labels.some(l => hit(l.b, c.b)));
    if (ok) labels.push({ ...ok, t: p.v.s.ticker });
  });
  const dots = pts.map(p => `<g class="dot" tabindex="0" role="link" data-t="${esc(p.v.s.ticker)}" aria-label="${esc(p.v.s.name)}: Qualität ${p.v.q}, Timing ${p.v.t}">
      <circle cx="${p.x.toFixed(1)}" cy="${p.y.toFixed(1)}" r="5.5" fill="${ampelVar(ampel(p.v.gesamt))}" stroke="var(--surface)" stroke-width="1.5"/>
      <circle cx="${p.x.toFixed(1)}" cy="${p.y.toFixed(1)}" r="13" fill="transparent"/></g>`).join("");
  const texts = labels.map(l => `<text class="lbl" x="${l.x.toFixed(1)}" y="${l.y.toFixed(1)}" text-anchor="${l.a}">${esc(l.t)}</text>`).join("");
  return `<div class="card map"><svg viewBox="0 0 ${W} ${H}" role="group" aria-label="Chancen-Karte: Qualität gegen Timing">
    <rect x="${x60}" y="${P.t}" width="${W - P.r - x60}" height="${y60 - P.t}" fill="var(--gruen-soft)"/>
    <rect x="${x60}" y="${y60}" width="${W - P.r - x60}" height="${H - P.b - y60}" fill="var(--gelb-soft)" opacity=".7"/>
    <rect x="${P.l}" y="${P.t}" width="${W - P.l - P.r}" height="${H - P.t - P.b}" fill="none" stroke="var(--line)"/>
    <line x1="${x60}" x2="${x60}" y1="${P.t}" y2="${H - P.b}" stroke="var(--line)" stroke-dasharray="3 3"/>
    <line x1="${P.l}" x2="${W - P.r}" y1="${y60}" y2="${y60}" stroke="var(--line)" stroke-dasharray="3 3"/>
    ${[0, 30, 60, 100].map(v => `<text class="axis" x="${X(v)}" y="${H - 8}" text-anchor="middle">${v}</text><text class="axis" x="${P.l - 5}" y="${Y(v) + 3}" text-anchor="end">${v}</text>`).join("")}
    ${dots}${texts}
  </svg><div class="map-legend"><span>Qualität nach rechts, Timing nach oben</span></div>
  <div class="map-key"><span><i style="background:var(--gruen-soft)"></i>Gute Firma, guter Zeitpunkt</span><span><i style="background:var(--gelb-soft)"></i>Gute Firma, Timing abwarten</span></div></div>`;
}

// Kurs-Chart mit EMA und Zonen (1 Jahr, 2 Jahre oder 5 Jahre)
const RANGES = { "1J": ["1 Jahr", "Tageskurse"], "2J": ["2 Jahre", "Tageskurse"], "5J": ["5 Jahre", "Wochenkurse"] };
function chartData(v, r) {
  const d = v.L?.chart, w = v.L?.chartw;
  if (r === "5J" && w?.c?.length) return { ch: w, woche: true };
  if (!d?.c?.length) return null;
  const k = r === "2J" ? 0 : Math.max(0, d.c.length - 252);
  const cut = a => a.slice(k);
  return { ch: { d: cut(d.d), c: cut(d.c), e50: cut(d.e50), e200: cut(d.e200) }, woche: false };
}
function chartHtml(v) {
  const s = v.s;
  const r = STATE.chartRange || "1J";
  const cd = chartData(v, r);
  const btns = `<div class="seg" role="group" aria-label="Zeitraum">${Object.keys(RANGES).map(k => `<button type="button" data-range="${k}" aria-pressed="${k === r}">${RANGES[k][0]}</button>`).join("")}</div>`;
  if (!cd) return btns + `<div class="empty">Der Chart erscheint nach dem nächsten automatischen Update der Kurse.</div>`;
  const ch = cd.ch;
  const W = 340, H = 200, P = { l: 6, r: 44, t: 8, b: 20 };
  const all = [...ch.c, ...ch.e50, ...ch.e200].filter(x => x != null);
  let lo = Math.min(...ch.c), hi = Math.max(...ch.c);
  const zl = [...(s.zonen.kauf || []), ...(s.zonen.widerstand || [])];
  zl.forEach(([a, b]) => { if (a > lo * 0.85 && a < hi * 1.15) { lo = Math.min(lo, a); hi = Math.max(hi, b); } });
  [s.zonen.trigger, s.zonen.abbruch].forEach(x => { if (x && x > lo * 0.85 && x < hi * 1.15) { lo = Math.min(lo, x); hi = Math.max(hi, x); } });
  all.forEach(x => { if (x > lo * 0.9 && x < hi * 1.1) { lo = Math.min(lo, x); hi = Math.max(hi, x); } });
  const pad = (hi - lo) * 0.05; lo -= pad; hi += pad;
  const n = ch.c.length, X = i => P.l + i / (n - 1) * (W - P.l - P.r), Y = y => P.t + (1 - (y - lo) / (hi - lo)) * (H - P.t - P.b);
  const path = arr => arr.map((y, i) => `${i ? "L" : "M"}${X(i).toFixed(1)} ${Y(Math.max(lo, Math.min(hi, y))).toFixed(1)}`).join("");
  const band = ([a, b], col) => { const y1 = Y(Math.min(hi, b)), y2 = Y(Math.max(lo, a)); return y2 > y1 ? `<rect x="${P.l}" y="${y1}" width="${W - P.l - P.r}" height="${y2 - y1}" fill="${col}" opacity=".55"/>` : ""; };
  const hline = (y, col, lab, dy = 0) => y && y >= lo && y <= hi ? `<line x1="${P.l}" x2="${W - P.r}" y1="${Y(y)}" y2="${Y(y)}" stroke="${col}" stroke-dasharray="4 3" stroke-width="1.2"/><text class="ax" x="${W - P.r + 3}" y="${Y(y) + 3 + dy}" fill="${col}">${lab}</text>` : "";
  const marks = [s.zonen.trigger, s.zonen.abbruch].filter(x => x && x >= lo && x <= hi).map(Y);
  const ticks = [lo + pad, (lo + hi) / 2, hi - pad].filter(y => marks.every(m => Math.abs(m - Y(y)) > 11)).map(y => `<text class="ax" x="${W - P.r + 3}" y="${Y(y) + 3}">${nf(y, y >= 100 ? 0 : 1)}</text>`).join("");
  // Zeitachse: 1 Jahr jeden 2. Monat, 2 Jahre jedes Quartal, 5 Jahre jedes Jahr
  const labels = []; let last = "";
  ch.d.forEach((d, i) => {
    const y = d.slice(0, 4), m = +d.slice(5, 7), key = r === "5J" ? y : d.slice(0, 7);
    if (key === last) return; last = key;
    if (i < 4 || i > n - 4) return;
    let txt = null;
    if (r === "5J") txt = y;
    else if (r === "2J") { if (m % 3 === 1) txt = m === 1 ? y : MON[m - 1]; }
    else if (m % 2 === 1) txt = m === 1 ? y : MON[m - 1];
    if (txt) labels.push(`<line x1="${X(i).toFixed(1)}" x2="${X(i).toFixed(1)}" y1="${P.t}" y2="${H - P.b}" stroke="var(--line)" stroke-width=".6"/><text class="ax" x="${X(i).toFixed(1)}" y="${H - 5}" text-anchor="middle">${txt}</text>`);
  });
  const e = cd.woche ? " Woche" : "";
  return `${btns}<div class="card chart"><svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Kursverlauf ${RANGES[r][0]} mit Zonen">
    ${(s.zonen.kauf || []).map(z => band(z, "var(--gruen-soft)")).join("")}
    ${(s.zonen.widerstand || []).map(z => band(z, "var(--rot-soft)")).join("")}
    ${labels.join("")}
    ${(() => { const tY = s.zonen.trigger && s.zonen.trigger >= lo && s.zonen.trigger <= hi ? Y(s.zonen.trigger) : null, aY = s.zonen.abbruch && s.zonen.abbruch >= lo && s.zonen.abbruch <= hi ? Y(s.zonen.abbruch) : null; const close = tY != null && aY != null && Math.abs(tY - aY) < 11; return hline(s.zonen.trigger, "var(--accent)", "Trigger", close ? -5 : 0) + hline(s.zonen.abbruch, "var(--rot)", "Abbruch", close ? 6 : 0); })()}
    <path d="${path(ch.e200)}" fill="none" stroke="var(--orange)" stroke-width="1.4"/>
    <path d="${path(ch.e50)}" fill="none" stroke="var(--gelb)" stroke-width="1.4"/>
    <path d="${path(ch.c)}" fill="none" stroke="var(--ink)" stroke-width="${r === "1J" ? 1.8 : 1.4}"/>
    ${ticks}
  </svg>
  <div class="legend"><span><i style="background:var(--ink)"></i>Kurs</span><span><i style="background:var(--gelb)"></i>EMA 50${e}</span><span><i style="background:var(--orange)"></i>EMA 200${e}</span><span><i style="background:var(--gruen-soft);height:9px"></i>Kaufzone</span><span><i style="background:var(--rot-soft);height:9px"></i>Widerstand</span></div></div>`;
}

function partsHtml(parts) {
  return `<div class="parts">${parts.map(p => {
    const c = ampel(p.p / p.max * 100);
    return `<div class="part"><span>${esc(p.name)}${p.auto ? '<span class="auto">automatisch</span>' : ""}</span><span class="p">${p.p} / ${p.max}</span>
      <div class="bar"><i style="width:${(p.p / p.max * 100).toFixed(0)}%;background:${ampelVar(c)}"></i></div>
      <div class="t">${esc(p.note || p.txt)}${!p.note && p.p0 != null && p.p0 !== p.p ? ` <b>(bei der Analyse ${p.p0}, seither automatisch angepasst)</b>` : ""}</div></div>`;
  }).join("")}</div>`;
}

// ---------- Ansichten ----------
function filtered() {
  const f = STATE.filter, q = f.q.trim().toLowerCase();
  let list = STATE.stocks.map(view).filter(v => {
    const s = v.s;
    if (f.stil !== "Alle" && !s.tags.includes(f.stil)) return false;
    if (f.region !== "Alle" && s.region !== f.region) return false;
    if (f.status !== "Alle" && !(f.status === "depot" ? (s.status === "depot" || window.Depot?.bestand(s.ticker)) : s.status === f.status)) return false;
    if (f.nurGut && v.q < 60) return false;
    const fk = f.fokus || "Alle";
    if (fk === "unter" && !v.bew?.unter) return false;
    if (fk === "schub" && !v.schub) return false;
    if (fk === "beides" && !(v.bew?.unter && v.schub)) return false;
    if (fk === "kontra" && !kontra(v)) return false;
    if (fk === "cash" && !((v.fcf?.score ?? 0) >= 70)) return false;
    if (q && !(`${s.name} ${s.ticker} ${s.branche} ${s.land}`.toLowerCase().includes(q))) return false;
    return true;
  });
  const by = {
    chance: (a, b) => (b.chance - a.chance) || (b.gesamt - a.gesamt),
    qualitaet: (a, b) => b.q - a.q || b.t - a.t,
    timing: (a, b) => b.t - a.t || b.q - a.q,
    zone: (a, b) => (a.dist ?? 999) - (b.dist ?? 999),
    tag: (a, b) => (b.chg1 ?? -999) - (a.chg1 ?? -999),
    zahlen: (a, b) => (a.s.zahlen || "9999").localeCompare(b.s.zahlen || "9999"),
    dividende: (a, b) => renditeOf(b) - renditeOf(a),
    unterbewertung: (a, b) => (b.bew?.abschlag ?? -999) - (a.bew?.abschlag ?? -999),
    cashflow: (a, b) => (b.fcf?.score ?? -1) - (a.fcf?.score ?? -1),
    name: (a, b) => a.s.name.localeCompare(b.s.name, "de")
  };
  return list.sort(by[f.sort] || by.chance);
}

function chipRow(key, values, counts) {
  return values.map(([val, label]) => `<button class="chip" data-f="${key}" data-v="${esc(val)}" aria-pressed="${STATE.filter[key] === val}">${esc(label)}${counts && counts[val] != null ? `<span class="n">${counts[val]}</span>` : ""}</button>`).join("");
}

function renderHome() {
  const all = STATE.stocks.map(view);
  const list = filtered();
  const hot = all.filter(v => v.chance).sort((a, b) => b.gesamt - a.gesamt);
  const warn = all.filter(v => v.status === "abbruch" || v.status === "unter_abbruch");
  const tags = ["Wachstum", "Qualität", "Dividende", "Cashflow", "Defensiv", "ETF"].filter(t => (t === "ETF" || t === "Cashflow") ? STATE.stocks.some(s => s.tags.includes(t)) : true);
  const cnt = k => Object.fromEntries([["Alle", STATE.stocks.length], ...[...new Set(STATE.stocks.flatMap(s => k === "stil" ? s.tags : [s[k]]))].map(x => [x, STATE.stocks.filter(s => k === "stil" ? s.tags.includes(x) : s[k] === x).length])]);
  const regions = ["USA", "Europa", "Schweiz", "Asien", "Welt"].filter(r => STATE.stocks.some(s => s.region === r));
  const stand = STATE.live?.aktualisiert ? new Date(STATE.live.aktualisiert) : null;
  $view.innerHTML = `
    <header class="top"><div><h1>Aktien-Ampel</h1>
      <div class="stand">${stand ? `Kurse vom ${stand.toLocaleDateString("de-CH")}, ${stand.toLocaleTimeString("de-CH", { hour: "2-digit", minute: "2-digit" })} Uhr` : "Werte der letzten Analysen, Kurse folgen nach dem ersten Update"}</div></div>
      <button class="iconbtn" id="reload" aria-label="Daten neu laden"><svg viewBox="0 0 24 24"><path d="M20 12a8 8 0 1 1-2.3-5.6M20 4v5h-5"/></svg></button></header>

    ${marktHtml()}

    <div class="sec"><h2>Jetzt interessant</h2><p>Qualität mindestens hellgrün und Kurs in der Zone, Trigger ausgelöst oder Timing mindestens hellgrün.</p></div>
    ${hot.length ? `<div class="hot">${hot.map(v => `<a class="hotcard" href="#/aktie/${encodeURIComponent(v.s.ticker)}">${signal(v.q, v.t)}<div><div class="nm">${esc(v.s.name)}</div><div class="tk">${esc(v.s.ticker)} · ${money(v.kurs, v.s.waehrung)}</div></div><div class="why">${esc(reason(v))}</div></a>`).join("")}</div>`
      : `<div class="empty">Gerade erfüllt keine Aktie diese Bedingungen. Die Karte unten zeigt, wer am nächsten dran ist.</div>`}
    ${warn.length ? `<div class="banner bad" style="margin-top:10px"><b>Achtung:</b> ${warn.map(v => `<a href="#/aktie/${encodeURIComponent(v.s.ticker)}">${esc(v.s.name)}</a>`).join(", ")} ${warn.length > 1 ? "liegen" : "liegt"} unter der Abbruch-Marke.</div>` : ""}

    <div class="sec"><h2>Chancen-Karte</h2><p>Jeder Punkt ist eine Aktie. Je weiter rechts oben, desto besser Firma und Zeitpunkt. Tippe auf einen Punkt.</p></div>
    ${mapHtml(list)}

    <div class="sec"><h2>Alle Aktien</h2></div>
    <div class="controls" id="controls">
      <div class="search"><input id="q" type="search" placeholder="Name, Ticker oder Branche" value="${esc(STATE.filter.q)}" aria-label="Suche">
        <select id="sort" aria-label="Sortierung">
          ${[["chance", "Beste Chance"], ["qualitaet", "Qualität"], ["timing", "Timing"], ["unterbewertung", "Am stärksten unterbewertet"], ["cashflow", "Free Cashflow"], ["zone", "Nähe zur Kaufzone"], ["tag", "Tagesveränderung"], ["zahlen", "Nächste Zahlen"], ["dividende", "Dividende"], ["name", "Name"]].map(([k, l]) => `<option value="${k}" ${STATE.filter.sort === k ? "selected" : ""}>${l}</option>`).join("")}
        </select></div>
      <div class="chips" role="group" aria-label="Chancen">${chipRow("fokus", [["Alle", "Alle Chancen"], ["unter", "Unterbewertet"], ["schub", "Wachstumsschub"], ["beides", "Beides"], ["kontra", "Kontra-Signal"], ["cash", "Starker Cashflow"]],
        { Alle: all.length, unter: all.filter(v => v.bew?.unter).length, schub: all.filter(v => v.schub).length, beides: all.filter(v => v.bew?.unter && v.schub).length, kontra: all.filter(kontra).length, cash: all.filter(v => (v.fcf?.score ?? 0) >= 70).length })}</div>
      <div class="chips" role="group" aria-label="Stil">${chipRow("stil", [["Alle", "Alle"], ...tags.map(t => [t, t])], cnt("stil"))}</div>
      <div class="chips" role="group" aria-label="Region und Liste">${chipRow("region", [["Alle", "Alle Regionen"], ...regions.map(r => [r, r])], cnt("region"))}<span class="sep"></span>
        ${chipRow("status", [["Alle", "Alle Listen"], ...["depot", "kaufliste", "beobachten"].filter(x => STATE.stocks.some(s => s.status === x || (x === "depot" && window.Depot?.bestand(s.ticker)))).map(x => [x, LISTE[x]])])}<span class="sep"></span>
        <button class="chip" id="nurGut" aria-pressed="${STATE.filter.nurGut}">Nur Qualität ab 60</button></div>
    </div>
    <div class="count">${list.length} von ${STATE.stocks.length} Aktien</div>
    <div class="list">${list.map(rowHtml).join("") || `<div class="empty">Keine Aktie passt zu diesen Filtern. Setze einen Filter auf «Alle» zurück.</div>`}</div>
    <div id="wunsch">${wunschHtml()}</div>
  `;
  bindHome();
}

function bindHome() {
  const save = () => store.set("filter", STATE.filter);
  $view.querySelectorAll(".chip[data-f]").forEach(b => b.onclick = () => { STATE.filter[b.dataset.f] = b.dataset.v; save(); renderKeepScroll(); });
  const ng = document.getElementById("nurGut"); ng.onclick = () => { STATE.filter.nurGut = !STATE.filter.nurGut; save(); renderKeepScroll(); };
  const q = document.getElementById("q");
  q.oninput = () => { STATE.filter.q = q.value; save(); updateList(); };
  document.getElementById("sort").onchange = e => { STATE.filter.sort = e.target.value; save(); renderKeepScroll(); };
  document.getElementById("reload").onclick = refresh;
  bindWunsch();
  $view.querySelectorAll(".dot").forEach(g => {
    const go = () => location.hash = "#/aktie/" + encodeURIComponent(g.dataset.t);
    g.onclick = go; g.onkeydown = e => { if (e.key === "Enter") go(); };
  });
  const ctr = document.getElementById("controls");
  const obs = new IntersectionObserver(([e]) => ctr.classList.toggle("stuck", e.intersectionRatio < 1), { threshold: [1], rootMargin: "-1px 0px 0px 0px" });
  obs.observe(ctr);
}
function updateList() {
  const list = filtered();
  $view.querySelector(".list").innerHTML = list.map(rowHtml).join("") || `<div class="empty">Keine Aktie passt zur Suche.</div>`;
  $view.querySelector(".count").textContent = `${list.length} von ${STATE.stocks.length} Aktien`;
  const wi = document.getElementById("wunsch-in");
  if (!list.length && STATE.filter.q.trim() && wi && !wi.value) wi.placeholder = `Zum Beispiel «${STATE.filter.q.trim()}»`;
}
function renderKeepScroll() { const y = scrollY; renderHome(); scrollTo(0, y); }

function divHtml(s, v) {
  const d = divData(s, v.L), w = s.waehrung;
  if (!d.zahlt) return `<div class="card prose div-none"><p><b>Zahlt keine Dividende.</b> ${esc(d.text || "Die Firma behält den Gewinn und steckt ihn ins Wachstum oder in Aktienrückkäufe.")}</p></div>`;
  const n = d.proJahr;
  const cells = MON.map((m, i) => {
    const ex = d.exM.includes(i + 1), pay = d.payM.includes(i + 1);
    const t = [ex ? "Ex-Tag" : "", pay ? "Auszahlung" : ""].filter(Boolean).join(" und ");
    return `<div class="${ex ? "ex " : ""}${pay ? "pay" : ""}"${t ? ` title="${MON[i]}: ${t}"` : ""}><i></i><span>${m}</span></div>`;
  }).join("");
  const nx = d.next;
  return `<div class="card div">
    <div class="div-top">
      <div><span>Rendite</span><b>${d.rendite ? nf(d.rendite, 1) + " %" : "–"}</b><em>letzte 12 Monate</em></div>
      <div><span>Pro Zahlung</span><b>${money(d.betrag, w)}</b><em>${d.summe ? "12 Monate: " + money(d.summe, w) : "pro Aktie"}</em></div>
      <div><span>Wie oft</span><b>${n ? n + "× pro Jahr" : "–"}</b><em>${esc(d.rhythmus || "")}</em></div>
    </div>
    ${d.system ? `<p class="div-sys"><b>System:</b> ${esc(d.system)}</p>` : ""}
    <p class="div-sys"><b>Form:</b> ${esc(divForm(s))}</p>
    <div class="div-months" role="img" aria-label="Monate mit Ex-Tag ${d.exM.map(x => MON[x - 1]).join(", ")}; Auszahlung ${d.payM.map(x => MON[x - 1]).join(", ")}">${cells}</div>
    <div class="legend"><span><i class="lg-ex"></i>Ex-Tag</span><span><i class="lg-pay"></i>Geld auf dem Konto</span></div>
    ${d.zahlText ? `<p class="div-sys"><b>Zahltage:</b> ${esc(d.zahlText)}</p>` : ""}
    ${nx ? `<div class="div-next"><b>Nächste Dividende${nx.sicher ? "" : " (geschätzt)"}</b>
      <span>Ex-Tag ${fmtDate(nx.ex)}${nx.pay ? ` · Zahltag ${fmtDate(nx.pay)}` : ""} · ${money(nx.betrag, w)} pro Aktie</span>
      <em>${nx.sicher ? "Von der Firma angekündigt." : "Nach dem Muster der letzten Jahre geschätzt, das genaue Datum gibt die Firma später bekannt."}</em></div>` : ""}
    ${d.serie ? `<p class="div-sys">${esc(d.serie)}</p>` : ""}
    <details class="more"><summary>Letzte Zahlungen und was die Begriffe bedeuten</summary>
      ${d.hist.length ? `<table class="divtab"><thead><tr><th>Ex-Tag</th><th>Betrag</th></tr></thead><tbody>${d.hist.map(([dd, b]) => `<tr><td>${fmtDate(dd)}</td><td>${money(b, w)}</td></tr>`).join("")}</tbody></table>` : ""}
      <ul class="plain">
        <li><b>Ex-Tag:</b> Ab diesem Tag wird die Aktie ohne Dividende gehandelt. Du bekommst die Dividende nur, wenn du die Aktie am Abend vor dem Ex-Tag besitzt. Der Kurs fällt am Ex-Tag meist etwa um den Dividendenbetrag.</li>
        <li><b>Zahltag:</b> An diesem Tag überweist die Firma das Geld. Bei Saxo kommt es in der Währung der Aktie aufs Konto, abzüglich Quellensteuer.</li>
        <li><b>Rendite:</b> Dividenden der letzten 12 Monate geteilt durch den heutigen Kurs.</li>
      </ul></details>
  </div>`;
}

// Dividende als Kennzahl-Kachel: alles auf einen Blick
function divKpi(s, v) {
  const d = divData(s, v.L), w = s.waehrung;
  if (!d.zahlt) return `<div class="kpi"><span>Dividende</span><b>keine</b><em>${esc(d.text || "Die Firma zahlt keine Dividende.")}</em></div>`;
  const nx = d.next;
  const mon = a => a.length ? a.map(x => MON[x - 1]).join(", ") : "–";
  return `<div class="kpi kpi-div ${d.rendite >= 2.5 ? "g" : "w"}"><span>Dividende</span><b>${d.rendite ? nf(d.rendite, 1) + " %" : money(d.betrag, w)}</b>
    <em><b>${d.proJahr ? d.proJahr + "× pro Jahr" : ""}</b> (${esc(d.rhythmus || "")}), je ${money(d.betrag, w)}.<br>
    Ex-Tag im ${mon(d.exM)}, Geld im ${mon(d.payM)}.<br>
    ${nx ? `Nächste: Ex-Tag ${fmtDate(nx.ex)}${nx.pay ? `, Zahltag ${fmtDate(nx.pay)}` : ""} (${nx.sicher ? "angekündigt" : "geschätzt"}).<br>` : ""}
    ${esc(divForm(s))} <button type="button" class="jump" data-jump="div-${esc(s.ticker)}">Alle Details</button></em></div>`;
}

function chanceHtml(v) {
  const s = v.s, c = s.chance, b = v.bew;
  if (!c && !b) return "";
  const meter = b ? (() => {
    const max = Math.max(b.schnitt, b.jetzt) * 1.15, pos = x => (x / max * 100).toFixed(1);
    const col = b.abschlag >= 15 ? "gruen" : b.abschlag > -10 ? "gelb" : "orange";
    return `<div class="bew">
      <div class="bew-top"><b class="${col}-t">${b.abschlag >= 0 ? nf(b.abschlag, 0) + " % günstiger" : nf(-b.abschlag, 0) + " % teurer"}</b><span>als im eigenen 5-Jahres-Schnitt · ${esc(b.stufe)}</span></div>
      <div class="bew-bar"><i class="now" style="left:${pos(b.jetzt)}%"></i><i class="avg" style="left:${pos(b.schnitt)}%"></i></div>
      <div class="bew-leg"><span><i class="now"></i>${esc(b.typ)} heute ${nf(b.jetzt, 1)}</span><span><i class="avg"></i>Schnitt ${nf(b.schnitt, 1)}</span></div>
    </div>`;
  })() : "";
  const pe = v.L?.pessimismus;
  const pess = pe ? `<div class="pess"><div class="pess-top"><span>Stimmung bei dieser Aktie</span><span class="pill ${PESS[pe.stufe]?.[1] || ""}">${PESS[pe.stufe]?.[0] || pe.stufe} · ${pe.wert} von 100</span></div>
    <div class="bar"><i style="width:${pe.wert}%;background:var(--accent)"></i></div>
    <p class="pill-line">${nf(pe.abstand_hoch, 0)} % unter dem Jahreshoch · Wochen-RSI ${nf(pe.rsi_w, 0)} · ${pe.unter_ema200w > 0 ? nf(pe.unter_ema200w, 0) + " % unter" : nf(-pe.unter_ema200w, 0) + " % über"} der Wochen-EMA 200.
    ${pe.wert >= 60 ? (v.q >= 50 ? " <b>Kontra-Signal:</b> Viel Angst bei einer ordentlichen Firma. Wenn die Sorgen unten nicht das Geschäft zerstören, kann hier eine Gelegenheit entstehen." : " Viel Angst, aber auch die Qualität ist schwach: Vorsicht vor einer Value-Falle.") : ""}</p></div>` : "";
  const sg = c?.sorgen?.length ? `<h3>Was die Börse befürchtet</h3>${c.sorgen_art ? `<p class="pill-line"><span class="pill p-${esc(c.sorgen_art)}">${esc(SORGE[c.sorgen_art] || c.sorgen_art)}</span> ${esc(c.sorgen_art_text || "")}</p>` : ""}<ul class="plain">${c.sorgen.map(x => `<li>${esc(x)}</li>`).join("")}</ul>` : "";
  const au = c?.aufloeser?.length ? `<h3>Was die Sorgen beenden könnte</h3><ul class="plain when">${c.aufloeser.map(x => `<li><span>${esc(x.was)}</span><em>${esc(x.wann || "")}</em></li>`).join("")}</ul>` : "";
  const sb = c ? (SCHUB[c.schub_stufe] || SCHUB.mittel) : null;
  const schub = c ? `<div class="card ch-card"><div class="ch-head"><h3>Wachstumsschub</h3><span class="pill p-${sb[1]}">${sb[0]}</span></div>
    <ol class="treiber">${(c.schub_treiber || []).map(x => `<li><b>${esc(x.titel)}</b><span>${esc(x.text)}</span>${x.wann ? `<em>${esc(x.wann)}</em>` : ""}</li>`).join("")}</ol>
    ${c.schub_beweis ? `<p class="beweis"><b>Woran du es erkennst:</b> ${esc(c.schub_beweis)}</p>` : ""}</div>` : "";
  return `<div class="sec"><h2>Worauf du achten solltest</h2><p>Deine zwei Blickwinkel: Ist die Aktie wegen Sorgen zu günstig, und gibt es einen grossen Wachstumsschub?</p></div>
    <div class="card ch-card"><div class="ch-head"><h3>Unterbewertung</h3></div>${meter}${pess}${sg}${au}${!c ? '<p class="pill-line" style="margin-top:10px">Die Recherche zu Sorgen und Wachstumsschub folgt.</p>' : ""}</div>
    ${schub}
    ${c?.szenario ? `<div class="banner plain szen"><b>Das Chancen-Szenario:</b> ${esc(c.szenario)}</div>` : ""}
    ${c?.quellen?.length ? `<details class="more"><summary>Quellen zu Sorgen und Wachstum</summary><ul class="plain">${c.quellen.map(q => `<li><a href="${esc(q.url)}" target="_blank" rel="noopener">${esc(q.titel)}</a></li>`).join("")}</ul></details>` : ""}`;
}



// ---------- Neue Aktie wünschen ----------
// Der Wunsch geht als Nachricht an ein ntfy-Thema. GitHub holt ihn alle 3 Stunden ab,
// Claude analysiert offene Wünsche einmal täglich am Abend und meldet sich per Push.
const WUNSCH_TOPIC = "aa-wunsch-et886oec5xtc";
const WSTAT = {
  gesendet: ["Gesendet", "b-trig", "Wird in den nächsten 3 Stunden abgeholt."],
  offen: ["Wartet", "b-trig", "Claude analysiert sie heute Abend (ab 22:50 Uhr)."],
  in_arbeit: ["In Arbeit", "b-trig", "Claude analysiert sie gerade."],
  fertig: ["Fertig", "b-zone", "Die Analyse ist in der App."],
  schon_da: ["Schon da", "b-zone", "Diese Aktie ist schon in der App."],
  abgelehnt: ["Nicht möglich", "b-warn", ""]
};
function wunschListe() {
  const remote = (STATE.wuensche || []).slice().reverse();
  const seen = new Set(remote.map(x => x.text.toLowerCase()));
  const local = store.get("wuensche_local", []).filter(x => Date.now() - x.ts < 2 * 864e5 && !seen.has(x.text.toLowerCase()))
    .map(x => ({ text: x.text, status: "gesendet", eingang: new Date(x.ts).toISOString() }));
  return [...local, ...remote].filter(x => Date.now() - new Date(x.eingang).getTime() < 14 * 864e5).slice(0, 6);
}
function wunschHtml(msg) {
  const li = wunschListe();
  return `<div class="sec"><h2>Aktie fehlt?</h2><p>Schreib den Namen oder das Kürzel. Claude macht einmal täglich am Abend die ganze Analyse und nimmt die Aktie in die App auf. Du bekommst eine Push-Nachricht.</p></div>
    <div class="card wunsch"><form id="wunsch-form" class="tokenrow"><input id="wunsch-in" type="text" maxlength="60" autocomplete="off" placeholder="Zum Beispiel «Adobe» oder «ADBE»" aria-label="Aktie wünschen">
      <button class="btn small primary" type="submit">Analysieren lassen</button></form>
      ${msg ? `<p class="w-msg">${esc(msg)}</p>` : ""}
      ${li.length ? `<ul class="w-list">${li.map(x => { const st = WSTAT[x.status] || WSTAT.offen; const t = x.ticker && STATE.stocks.some(s => s.ticker === x.ticker) ? x.ticker : null;
        return `<li><span class="badge ${st[1]}">${st[0]}</span><span class="w-t">${t ? `<a href="#/aktie/${encodeURIComponent(t)}">${esc(x.text)}</a>` : esc(x.text)}<em>${esc(x.hinweis || st[2])}</em></span></li>`; }).join("")}</ul>` : ""}
    </div>`;
}
function bindWunsch() {
  const f = document.getElementById("wunsch-form"); if (!f) return;
  f.onsubmit = async e => {
    e.preventDefault();
    const inp = document.getElementById("wunsch-in"), text = inp.value.trim();
    if (!text) return;
    const hit = STATE.stocks.find(s => [s.ticker, s.symbol, s.name].some(x => x.toLowerCase() === text.toLowerCase()));
    if (hit) { document.getElementById("wunsch").innerHTML = wunschHtml(`${hit.name} ist schon in der App.`); bindWunsch(); return; }
    let msg;
    try {
      const r = await fetch(`https://ntfy.sh/${WUNSCH_TOPIC}`, { method: "POST", body: text });
      if (!r.ok) throw new Error(r.status);
      store.set("wuensche_local", [...store.get("wuensche_local", []), { text, ts: Date.now() }]);
      msg = `«${text}» ist gesendet. Die Analyse kommt heute Abend.`;
    } catch { msg = "Senden hat nicht geklappt. Bist du online? Versuche es nochmals."; }
    document.getElementById("wunsch").innerHTML = wunschHtml(msg); bindWunsch();
  };
}

// ---------- Free Cashflow ----------
// Geld, das nach allen Kosten und Investitionen übrig bleibt. Sechs Fragen, zusammen 100 Punkte.
const FCF_MAX = { wachstum: 20, marge: 20, rendite: 15, schulden: 20, verwendung: 15, nachhaltig: 10 };
const mrd = (v, w) => v == null ? "–" : `${nf(v, Math.abs(v) >= 10 ? 1 : 2)} Mrd. ${w === "GBp" ? "GBP" : w}`;
function fcfWarn(v) {
  const pe = v.L?.pessimismus;
  return !!(pe && pe.abstand_hoch >= 30 && pe.unter_ema200w > 0);
}
// Fällt die Aktie stark (über 30 % unter dem Jahreshoch und unter der Wochen-EMA 200), zweifelt die Börse
// an der Zukunft des Free Cashflows: 5 Punkte Abzug bei der Nachhaltigkeit.
function fcfAdj(f, L) {
  if (!f) return null;
  if (!fcfWarn({ L })) return f;
  const abzug = Math.min(5, f.p.nachhaltig);
  return { ...f, p: { ...f.p, nachhaltig: f.p.nachhaltig - abzug }, score: f.score - abzug, abzug };
}
function fcfText(v) {
  const f = v.fcf, k = f.k, w = f.waehrung, j = f.jahre;
  const span = `${j[0]}–${j[j.length - 1]}`;
  const rows = [];
  rows.push(["wachstum", "1. Wächst der Free Cashflow?",
    k.wachstum == null ? `Von ${mrd(f.fcf[0], w)} auf ${mrd(f.fcf[f.fcf.length - 1], w)} (${span}). Ein Jahr war negativ, darum kein sauberes Wachstum.`
      : `${k.wachstum >= 0 ? "+" : "−"}${nf(Math.abs(k.wachstum), 1)} % pro Jahr (${span}), in ${k.steigende_jahre} von ${k.jahre_n} Jahren gestiegen. ${k.wachstum >= 10 ? "Stark." : k.wachstum >= 3 ? "Ordentlich." : "Schwach."}`]);
  rows.push(["marge", "2. Wie viel vom Umsatz bleibt übrig?",
    `FCF-Marge ${nf(k.marge, 1)} %: Von 100 Umsatz bleiben ${nf(k.marge, 0)} als freies Geld. ${k.marge >= 25 ? "Sehr gut, typisch für Firmen mit Preismacht." : k.marge >= 15 ? "Gut." : k.marge >= 8 ? "Mittel." : "Tief: Viel Umsatz, aber wenig bleibt hängen (oder grosse Investitionen)."}`]);
  rows.push(["rendite", "3. Wie viel im Verhältnis zum Börsenwert?",
    k.rendite == null ? "Börsenwert nicht verfügbar." : `FCF-Rendite ${nf(k.rendite, 1)} %: Für 100 CHF Aktie erwirtschaftet die Firma ${nf(k.rendite, 1)} CHF freies Geld pro Jahr. ${k.rendite >= 5 ? "Günstig bewertet." : k.rendite >= 3 ? "Fair." : "Teuer: Die Börse zahlt viel für künftiges Wachstum."}`]);
  rows.push(["schulden", "4. Wie schnell wären die Schulden bezahlt?",
    f.netto_schulden <= 0 ? `Mehr Geld als Schulden (${mrd(-f.netto_schulden, w)} Netto-Cash). Sehr stark.`
      : k.schulden_jahre == null ? `Nettoschulden ${mrd(f.netto_schulden, w)}, aber kein positiver Free Cashflow zum Abzahlen.`
      : `Nettoschulden ${mrd(f.netto_schulden, w)}. Mit dem Free Cashflow in ${k.schulden_jahre < 0.1 ? "weniger als 6 Wochen" : nf(k.schulden_jahre, 1) + " Jahren"} bezahlt. ${k.schulden_jahre <= 0.5 ? "Sehr stark: Der halbe FCF eines Jahres reicht." : k.schulden_jahre <= 2 ? "Gut." : k.schulden_jahre <= 4 ? "Mittel." : "Hoch: Viel Geld geht an die Banken."}`]);
  const use = (f.verwendung || []).map(([n, x]) => `${n} ${x} %`).join(", ");
  rows.push(["verwendung", "5. Wofür wird das Geld genutzt?",
    `${k.aktien_pa == null ? "" : k.aktien_pa < -0.3 ? `Die Aktienzahl sinkt um ${nf(-k.aktien_pa, 1)} % pro Jahr: Jede deiner Aktien gehört ein grösseres Stück der Firma. ` : k.aktien_pa > 0.3 ? `Achtung: Die Aktienzahl steigt um ${nf(k.aktien_pa, 1)} % pro Jahr (neue Aktien für Mitarbeiter). Dein Anteil wird kleiner. ` : "Die Aktienzahl bleibt etwa gleich. "}${use ? `Vom Free Cashflow ${span} ging: ${use}.` : ""}`]);
  rows.push(["nachhaltig", "6. Ist der Free Cashflow echt und nachhaltig?",
    `${k.verlustjahre ? `${k.verlustjahre} Jahr(e) mit negativem FCF. ` : "Kein Jahr mit negativem FCF. "}Aktien-Vergütung für Mitarbeiter: ${nf(k.sbc, 0)} % des FCF${k.sbc >= 25 ? " (hoch: Ein Teil des FCF ist «geschönt», weil Löhne in Aktien bezahlt werden)" : k.sbc >= 10 ? " (mittel)" : " (tief, gut)"}. ${k.deckung != null ? `Der FCF ist ${nf(k.deckung, 1)}-mal so gross wie der Gewinn${k.deckung < 0.8 ? " (wenig Cash aus dem Gewinn, oft wegen hoher Investitionen)" : k.deckung > 1.6 ? " (deutlich mehr Cash als Gewinn, z. B. wegen Abschreibungen)" : " (passt gut zusammen)"}.` : ""}`]);
  return rows;
}
function fcfChart(f) {
  const w = 300, h = 120, n = f.fcf.length, max = Math.max(...f.fcf.map(Math.abs), 0.001), bw = w / n * 0.56;
  const hasNeg = f.fcf.some(x => x < 0), base = hasNeg ? h * 0.62 : h - 18;
  const bars = f.fcf.map((x, i) => {
    const bh = Math.abs(x) / max * (hasNeg ? base - 18 : base - 18), cx = (i + 0.5) * w / n;
    const y = x >= 0 ? base - bh : base;
    const m = f.umsatz[i] ? x / f.umsatz[i] * 100 : null;
    return `<rect x="${(cx - bw / 2).toFixed(1)}" y="${y.toFixed(1)}" width="${bw.toFixed(1)}" height="${Math.max(bh, 1).toFixed(1)}" rx="3" fill="${x >= 0 ? "var(--accent)" : "var(--rot)"}"><title>${f.jahre[i]}: ${mrd(x, f.waehrung)}${m != null ? `, Marge ${nf(m, 0)} %` : ""}</title></rect>
      <text x="${cx.toFixed(1)}" y="${(x >= 0 ? y - 4 : y + bh + 11).toFixed(1)}" text-anchor="middle" class="fc-v">${nf(x, Math.abs(x) >= 10 ? 0 : 1)}</text>
      <text x="${cx.toFixed(1)}" y="${h - 3}" text-anchor="middle" class="fc-y">${f.jahre[i]}</text>`;
  }).join("");
  return `<svg class="fc-chart" viewBox="0 0 ${w} ${h}" role="img" aria-label="Free Cashflow pro Jahr in Mrd. ${esc(f.waehrung)}: ${f.jahre.map((y, i) => `${y} ${nf(f.fcf[i], 1)}`).join(", ")}">${bars}</svg>`;
}
function fcfHtml(v) {
  const f = v.fcf;
  if (!f) return `<div class="sec"><h2>Free Cashflow</h2></div><div class="card prose"><p>Die Free-Cashflow-Daten für diese Aktie werden beim nächsten Update geholt.</p></div>`;
  const c = ampel(f.score);
  const verdict = f.score >= 75 ? "Sehr starker Free Cashflow" : f.score >= 60 ? "Guter Free Cashflow" : f.score >= 45 ? "Gemischt" : f.score >= 30 ? "Schwach" : "Kaum freies Geld";
  const parts = fcfText(v).map(([k, name, txt]) => ({ name, txt, p: f.p[k], max: FCF_MAX[k] }));
  return `<div class="sec" id="fcf"><h2>Free Cashflow ${f.score} von 100</h2><p>Free Cashflow ist das Geld, das nach allen Kosten und Investitionen übrig bleibt. Damit kann die Firma Aktien zurückkaufen, Schulden abzahlen oder Dividenden zahlen.</p></div>
    <div class="card fc">
      <div class="fc-top"><span class="pill p-${c === "hellgruen" ? "gruen" : c === "rot" ? "orange" : c}">${verdict}</span>
        <span class="fc-now">Letzte 12 Monate: <b>${mrd(f.fcf_ttm, f.waehrung)}</b> bei ${mrd(f.umsatz_ttm, f.waehrung)} Umsatz</span></div>
      ${fcfChart(f)}
      <p class="fc-cap">Free Cashflow pro Geschäftsjahr in Mrd. ${esc(f.waehrung === "GBp" ? "GBP" : f.waehrung)}</p>
      ${fcfWarn(v) ? `<div class="banner warn"><b>Achtung Nachhaltigkeit:</b> Der Kurs liegt ${nf(v.L.pessimismus.abstand_hoch, 0)} % unter dem Jahreshoch und unter der Wochen-EMA 200, obwohl die Firma Geld verdient. Die Börse zweifelt, ob der Free Cashflow in Zukunft hält (${f.abzug || 0} Punkte Abzug bei der Nachhaltigkeit). Warum, steht weiter oben bei «Was die Börse befürchtet».</div>` : ""}
      ${partsHtml(parts)}
      <details class="more"><summary>So rechnet die App</summary><ul class="plain">
        <li><b>Wachstum (20):</b> Durchschnittliches Wachstum pro Jahr und wie oft der FCF gestiegen ist.</li>
        <li><b>Marge (20):</b> FCF geteilt durch Umsatz. Ab 30 % volle Punkte.</li>
        <li><b>Rendite (15):</b> FCF geteilt durch den Börsenwert. 100 Mrd. Börsenwert und 10 Mrd. FCF sind 10 %. Ab 7 % volle Punkte.</li>
        <li><b>Schulden (20):</b> Nettoschulden (Schulden minus Bargeld) geteilt durch den FCF. Netto-Cash oder unter einem halben Jahr: fast volle Punkte.</li>
        <li><b>Verwendung (15):</b> Sinkende Aktienzahl durch Rückkäufe und wie viel vom FCF an die Aktionäre geht oder Schulden tilgt.</li>
        <li><b>Nachhaltigkeit (10):</b> Keine negativen Jahre, wenig Aktien-Vergütung, FCF passt zum Gewinn. Liegt die Aktie über 30 % unter dem Jahreshoch und unter der Wochen-EMA 200, zieht die App 5 Punkte ab und zeigt eine Warnung (Beispiel Adobe).</li>
        <li>Daten: Jahreszahlen von Yahoo Finance, Stand ${fmtDate(STATE.fcf?.stand)}. Bei Firmen mit Kundenkrediten (z. B. Ferrari) oder Banken ist der FCF nur eingeschränkt vergleichbar.</li>
      </ul></details>
    </div>`;
}

function renderDetail(ticker) {
  const s = STATE.stocks.find(x => x.ticker === ticker);
  if (!s) { $view.innerHTML = `<a class="back" href="#/">Zurück</a><div class="empty">Diese Aktie ist nicht in der Liste.</div>`; return; }
  const v = view(s), z = s.zonen, w = s.waehrung, p = v.kurs;
  const dl = (d, lbl) => d === 0 ? "" : `<span class="delta ${d > 0 ? "up" : "down"}">${d > 0 ? "+" : "−"}${Math.abs(d)} ${lbl}</span>`;
  const st = v.status;
  const bannerTxt = {
    in_zone: ["ok", "Der Kurs liegt in einer Kaufzone. Jetzt auf die Bestätigung im Tageschart achten (siehe Cheat Sheet)."],
    nahe_zone: ["ok", `Der Kurs ist nur noch ${nf(v.dist, 1)} % über der Kaufzone.`],
    trigger: ["info", `Trigger ausgelöst${v.L?.trigger_am ? " am " + fmtDate(v.L.trigger_am) : ""}: Tagesschluss über ${money(z.trigger, w)}.`],
    ueber_trigger: ["info", `Der Kurs ist über dem Trigger (${money(z.trigger, w)}).`],
    abbruch: ["bad", `Wochenschluss unter der Abbruch-Marke ${money(z.abbruch, w)}. Die Bodenbildung ist gescheitert, die Aktie sollte neu bewertet werden.`],
    unter_abbruch: ["warn", `Der Kurs ist unter der Abbruch-Marke ${money(z.abbruch, w)}. Entscheidend ist der Wochenschluss.`]
  }[st];
  const zoneRows = [];
  (z.widerstand || []).forEach(([a, b]) => zoneRows.push({ lo: a, hi: b, txt: "Widerstand", c: "var(--rot)" }));
  if (z.trigger) zoneRows.push({ lo: z.trigger, hi: z.trigger, txt: "Trigger", c: "var(--accent)" });
  (z.kauf || []).forEach(([a, b], i) => zoneRows.push({ lo: a, hi: b, txt: i ? `Kaufzone ${i + 1}` : "Kaufzone", c: "var(--gruen)" }));
  if (z.abbruch) zoneRows.push({ lo: z.abbruch, hi: z.abbruch, txt: "Abbruch (Wochenschluss)", c: "var(--rot)" });
  zoneRows.sort((a, b) => b.hi - a.hi);
  const rng = (lo, hi) => lo === hi ? money(lo, w) : `${nf(lo, lo >= 1000 ? 0 : 2)}–${money(hi, w)}`;
  const distTo = r => p >= r.lo && p <= r.hi ? "hier" : pct(((p > r.hi ? r.hi : r.lo) / p - 1) * 100, 1);
  const zahlenTage = /^\d{4}-\d{2}-\d{2}$/.test(s.zahlen || "") ? daysUntil(s.zahlen) : null;
  const hist = STATE.verlauf[s.ticker] || [];

  $view.innerHTML = `
    <a class="back" href="#/"><svg viewBox="0 0 24 24"><path d="M15 5l-7 7 7 7"/></svg>Übersicht</a>
    <div class="dhead"><h1>${esc(s.name)}</h1>
      <div class="meta">${esc(s.ticker)} · ${esc(s.land)} · ${esc(s.branche)} · ${esc(s.tags.join(", "))}</div>
      <div class="dprice"><span class="px">${money(p, w)}</span>${chgHtml(v.chg1)}<span class="badge b-list">${LISTE[s.status]}</span></div>
      <div class="meta">Stand ${fmtDate(v.datum)}${v.L ? `, seit der Analyse ${pct(v.L.chg_analyse, 1)}` : ""}</div></div>

    <div class="scores">${signal(v.q, v.t, true)}
      <div class="lbl"><div><b>Qualität ${v.q} (${ampelName[ampel(v.q)]}) ${dl(v.dq, "seit Analyse")}</b>Ist die Firma kaufenswert?</div>
        <div><b>Timing ${v.t} (${ampelName[ampel(v.t)]}) ${dl(v.dt, "seit Analyse")}</b>Ist jetzt der Zeitpunkt?</div></div></div>
    ${bannerTxt ? `<div class="banner ${bannerTxt[0]}">${esc(bannerTxt[1])}</div>` : ""}

    <div class="sec"><h2>Kurz gesagt</h2></div>
    <p class="fazit">${esc(s.fazit)}</p>
    <div class="actions">
      <a class="btn primary" href="${esc(s.cheatsheet)}">Cheat Sheet öffnen</a>
      <a class="btn" href="${esc(s.claude)}" target="_blank" rel="noopener">Analyse in Claude öffnen</a>
    </div>
    ${(() => { const b = window.Depot?.bestand(s.ticker); return b ? `<div class="banner plain dp-held"><b>Im Depot:</b> ${nf(b.stueck, b.stueck % 1 ? 3 : 0)} Stück, Einstand ${money(b.einstand, w)}, ${b.guvPct != null ? `${b.guvPct >= 0 ? "+" : "−"}${nf(Math.abs(b.guvPct), 1)} %` : ""} <a href="#/depot/neu/${encodeURIComponent(s.ticker)}">Kauf oder Verkauf eintragen</a></div>` : `<p class="dp-link"><a href="#/depot/neu/${encodeURIComponent(s.ticker)}">Gekauft? Im Depot-Journal eintragen</a></p>`; })()}

    ${chanceHtml(v)}

    <div class="sec"><h2>Meine Notiz</h2><p>${token() ? "Wird auf allen Geräten gespeichert." : "Wird auf diesem Gerät gespeichert. Für alle Geräte unter «So funktioniert's» den GitHub-Schlüssel eintragen."}</p></div>
    <div class="note"><textarea id="note" rows="4" placeholder="Zum Beispiel: Warum ich sie beobachte, mein Kaufplan, was ich nach den Zahlen prüfen will">${esc(STATE.notes[s.ticker]?.text || "")}</textarea>
      <div class="note-bar"><span id="note-state">${STATE.notes[s.ticker]?.ts ? "Zuletzt geändert " + new Date(STATE.notes[s.ticker].ts).toLocaleString("de-CH", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" }) : ""}</span>
      <button class="btn small" id="note-save">Notiz speichern</button></div></div>

    <div class="sec"><h2>Chart und Zonen</h2><p>Standard ist 1 Jahr. Für den grossen Trend auf 2 oder 5 Jahre umschalten.</p></div>
    <div id="chartbox">${chartHtml(v)}</div>
    <div class="zones" style="margin-top:10px">${zoneRows.map(r => `<div class="zone${p >= r.lo && p <= r.hi && r.lo !== r.hi ? " here" : ""}"><i class="k" style="background:${r.c}"></i><span><b>${rng(r.lo, r.hi)}</b> ${esc(r.txt)}</span><span class="dist">${distTo(r)}</span></div>`).join("")}</div>
    ${s.zonen_text?.length ? `<details class="more"><summary>Was die Zonen bedeuten</summary><ul class="plain">${s.zonen_text.map(x => `<li><b>${esc(x.wert)}</b>: ${esc(x.text)}</li>`).join("")}</ul></details>` : ""}

    <div class="sec"><h2>Timing ${v.t} von 100</h2><p>Teile mit «automatisch» rechnet die App jeden Börsentag neu.</p></div>
    <div class="card">${partsHtml(v.tParts)}</div>

    <div class="sec"><h2>Qualität ${v.q} von 100</h2><p>Aus der letzten Analyse. Die Bewertung passt sich dem Kurs an.</p></div>
    <div class="card">${partsHtml(v.qParts)}</div>

    ${scanSlot(s)}

    <div class="sec"><h2>Wichtige Kennzahlen</h2></div>
    <div class="kpis">${s.kpis.filter(k => !/^Dividende/.test(k.name)).map(k => `<div class="kpi ${esc(k.ampel)}"><span>${esc(k.name)}</span><b>${esc(k.wert)}</b><em>${esc(k.text)}</em></div>`).join("")}${divKpi(s, v)}</div>

    ${fcfHtml(v)}

    <div class="sec" id="div-${esc(s.ticker)}"><h2>Dividende</h2><p>Wann, wie oft und in welcher Form ausbezahlt wird.</p></div>
    ${divHtml(s, v)}

    <div class="sec"><h2>Für und gegen</h2></div>
    <div class="two"><div class="card"><b>Dafür</b><ul class="plain">${s.pro.map(x => `<li>${esc(x)}</li>`).join("")}</ul></div>
      <div class="card"><b>Dagegen</b><ul class="plain">${s.contra.map(x => `<li>${esc(x)}</li>`).join("")}</ul></div></div>

    <div class="sec"><h2>Eckdaten</h2></div>
    <div class="card"><dl class="facts">
      <dt>Nächste Zahlen</dt><dd>${fmtDate(s.zahlen)}${zahlenTage != null && zahlenTage >= 0 ? ` (in ${zahlenTage} Tagen)` : ""}</dd>
      <dt>Dividende</dt><dd>${(() => { const d = divData(s, v.L); return d.zahlt ? `${d.rendite ? nf(d.rendite, 1) + " %" : "–"}, ${esc(d.rhythmus || "")}` : "keine"; })()}</dd>
      ${v.L ? `<dt>52 Wochen</dt><dd>${money(v.L.tief52, w)} bis ${money(v.L.hoch52, w)}</dd>
      <dt>EMA 50 / 200 Tag</dt><dd>${nf(v.L.ind.ema50d)} / ${nf(v.L.ind.ema200d)}</dd>
      <dt>EMA 50 / 200 Woche</dt><dd>${nf(v.L.ind.ema50w)} / ${nf(v.L.ind.ema200w)}</dd>
      <dt>RSI Tag / Woche</dt><dd>${nf(v.L.ind.rsid, 0)} / ${nf(v.L.ind.rsiw, 0)}</dd>` : ""}
      <dt>Letzte Analyse</dt><dd>${fmtDate(s.analyse.datenstand)}, Qualität ${s.analyse.q}, Timing ${s.analyse.t}</dd>
      <dt>Währung</dt><dd>${esc(s.waehrung === "GBp" ? "Pence (100 p = 1 £)" : s.waehrung)}</dd>
    </dl></div>
    ${hist.length > 1 ? `<div class="sec"><h2>Verlauf der Ampeln</h2></div>${histHtml(hist)}` : ""}
    ${s.smart_money?.length ? `<details class="more"><summary>Insider und Smart Money</summary><ul class="plain">${s.smart_money.map(x => `<li>${esc(x)}</li>`).join("")}</ul></details>` : ""}
  `;
  bindNote(s.ticker);
  const bindChart = () => document.querySelectorAll("#chartbox [data-range]").forEach(b => b.onclick = () => {
    STATE.chartRange = b.dataset.range; store.set("chartRange", b.dataset.range);
    document.getElementById("chartbox").innerHTML = chartHtml(v); bindChart();
  });
  bindChart();
  $view.querySelectorAll("[data-jump]").forEach(b => b.onclick = () => document.getElementById(b.dataset.jump)?.scrollIntoView({ behavior: "smooth", block: "start" }));
  scrollTo(0, 0);
}

function bindNote(ticker) {
  const ta = document.getElementById("note"), st = document.getElementById("note-state"), btn = document.getElementById("note-save");
  let timer;
  const keepLocal = () => {
    STATE.notes[ticker] = { text: ta.value, ts: Date.now() };
    const local = store.get("notes_local", {}); local[ticker] = STATE.notes[ticker]; store.set("notes_local", local);
  };
  ta.oninput = () => { clearTimeout(timer); timer = setTimeout(() => { keepLocal(); st.textContent = "Auf diesem Gerät gespeichert"; }, 600); };
  btn.onclick = async () => {
    keepLocal(); btn.disabled = true; st.textContent = "Speichere …";
    try { const where = await syncNote(ticker); st.textContent = where === "github" ? "Gespeichert, auf allen Geräten sichtbar" : "Auf diesem Gerät gespeichert"; }
    catch (e) { st.textContent = "Nur auf diesem Gerät gespeichert. GitHub hat nicht geantwortet, später nochmals tippen."; }
    btn.disabled = false;
  };
}

function histHtml(h) {
  const W = 340, H = 110, P = { l: 6, r: 30, t: 8, b: 18 }, n = h.length;
  const X = i => P.l + (n === 1 ? 0 : i / (n - 1)) * (W - P.l - P.r), Y = v => P.t + (1 - v / 100) * (H - P.t - P.b);
  const path = k => h.map((r, i) => `${i ? "L" : "M"}${X(i).toFixed(1)} ${Y(r[k]).toFixed(1)}`).join("");
  return `<div class="card chart"><svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Verlauf von Qualität und Timing">
    <line x1="${P.l}" x2="${W - P.r}" y1="${Y(60)}" y2="${Y(60)}" stroke="var(--line)" stroke-dasharray="3 3"/>
    <path d="${path(1)}" fill="none" stroke="var(--accent)" stroke-width="2"/><path d="${path(2)}" fill="none" stroke="var(--orange)" stroke-width="2"/>
    <text class="ax" x="${W - P.r + 4}" y="${Y(60) + 3}">60</text>
    <text class="ax" x="${P.l}" y="${H - 4}">${fmtDate(h[0][0])}</text><text class="ax" x="${W - P.r}" y="${H - 4}" text-anchor="end">${fmtDate(h[n - 1][0])}</text>
  </svg><div class="legend"><span><i style="background:var(--accent)"></i>Qualität</span><span><i style="background:var(--orange)"></i>Timing</span></div></div>`;
}

function renderTermine() {
  const evs = STATE.stocks.filter(s => /^\d{4}-\d{2}-\d{2}$/.test(s.zahlen || "")).map(s => ({ s, d: s.zahlen, typ: "Zahlen" }));
  STATE.stocks.forEach(s => {
    const dv = divData(s, STATE.live?.aktien?.[s.ticker]);
    if (!dv.zahlt || !dv.next) return;
    const geschaetzt = dv.next.sicher ? "" : " (geschätzt)";
    if (dv.next.ex) evs.push({ s, d: dv.next.ex, typ: "Ex-Tag", txt: `Ex-Tag Dividende${geschaetzt}, ${money(dv.next.betrag, s.waehrung)}` });
    if (dv.next.pay) evs.push({ s, d: dv.next.pay, typ: "Zahltag", txt: `Dividende wird ausbezahlt${geschaetzt}` });
  });
  evs.forEach(e => { e.n = daysUntil(e.d); });
  const filt = STATE.filter.termine || "Alle";
  const list = evs.filter(e => e.n >= -1 && e.n <= 200 && (filt === "Alle" || (filt === "Zahlen" ? e.typ === "Zahlen" : e.typ !== "Zahlen"))).sort((a, b) => a.d.localeCompare(b.d));
  let html = `<header class="top"><div><h1>Termine</h1><div class="stand">Quartalszahlen und Dividenden deiner Aktien</div></div></header>
    <div class="chips" role="group" aria-label="Termine filtern">${["Alle", "Zahlen", "Dividenden"].map(x => `<button class="chip" data-tf="${x}" aria-pressed="${filt === x}">${x}</button>`).join("")}</div>`;
  let m = "";
  const mn = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"];
  const wd = ["So", "Mo", "Di", "Mi", "Do", "Fr", "Sa"];
  list.forEach(e => {
    const dd = new Date(e.d + "T12:00:00"); const key = mn[dd.getMonth()] + " " + dd.getFullYear();
    if (key !== m) { html += `<div class="month">${key}</div>`; m = key; }
    const v = view(e.s);
    const was = e.typ === "Zahlen" ? "Quartalszahlen" : e.txt;
    html += `<a class="ev${e.n <= 7 ? " soon" : ""}${e.typ !== "Zahlen" ? " ev-div" : ""}" href="#/aktie/${encodeURIComponent(e.s.ticker)}"><div class="day">${dd.getDate()}<small>${wd[dd.getDay()]}</small></div>
      <div><div style="font-weight:600">${esc(e.s.name)}</div><div class="sub" style="font-size:13px;color:var(--muted)">${esc(was)} · ${e.n === 0 ? "heute" : e.n === 1 ? "morgen" : e.n < 0 ? "gestern" : "in " + e.n + " Tagen"}</div></div>${signal(v.q, v.t)}</a>`;
  });
  if (!list.length) html += `<div class="empty">Keine Termine in den nächsten Monaten.</div>`;
  $view.innerHTML = html;
  $view.querySelectorAll("[data-tf]").forEach(b => b.onclick = () => { STATE.filter.termine = b.dataset.tf; renderTermine(); });
  scrollTo(0, 0);
}

function renderInfo() {
  const L = STATE.live;
  $view.innerHTML = `<header class="top"><div><h1>So funktioniert's</h1></div></header>
  <div class="card prose">
    <h3>Zwei Ampeln pro Aktie</h3>
    <p><b>Q = Qualität:</b> Ist die Firma kaufenswert? 8 Kriterien: Umsatz, Wachstum, Marge, Gewinn, Free Cashflow, ROIC, Schulden und Bewertung.</p>
    <p><b>T = Timing:</b> Ist jetzt der Zeitpunkt? 7 Kriterien: Trend auf Woche und Tag, Struktur (Smart Money Concept), RSI, A/D-Linie, Smart Money und Saisonalität.</p>
    <div class="scale">${[["gruen", "grün", "75–100"], ["hellgruen", "hellgrün", "60–74"], ["gelb", "gelb", "45–59"], ["orange", "orange", "30–44"], ["rot", "rot", "0–29"]].map(([c, n, r]) => `<i class="sw ${c}"></i><span>${n}</span><span>${r}</span>`).join("")}</div>
    <h3>Worauf du bei einer Aktie achten solltest</h3>
    <p>Gute Zahlen allein reichen nicht. Die grössten Kursgewinne entstehen oft, wenn zwei Dinge zusammenkommen:</p>
    <p><b>1. Unterbewertung.</b> Eine gute Firma fällt wegen Sorgen stark, und die Aktie wird viel günstiger als üblich. Das misst die App mit dem <b>KGV</b> (Kurs geteilt durch den Gewinn pro Aktie, also wie viele Jahresgewinne du für die Aktie bezahlst) im Vergleich zum eigenen 5-Jahres-Schnitt. Beispiel: KGV heute 15, Schnitt 25, dann ist die Aktie 40 % günstiger als üblich. Wichtig ist, warum sie günstig ist: Ist es vor allem Stimmung oder ein vorübergehendes Problem, kann der Kurs stark steigen, sobald die Sorgen weg sind. Verschlechtert sich das Geschäft dauerhaft, ist die Aktie zu Recht günstig (eine «Value-Falle»). Darum zeigt die App bei jeder Aktie, was die Börse befürchtet und was diese Sorgen beenden könnte.</p>
    <p><b>2. Wachstumsschub.</b> Gibt es einen konkreten Grund, warum das Wachstum in den nächsten Jahren deutlich anziehen kann? Zum Beispiel ein neues Produkt, eine Zulassung oder ein neuer Markt. Beispiel Alphabet (Google) 2023: Alle dachten, Google verschläft die KI. Dabei hatte Google mit eigener KI, eigenen KI-Chips und Google Cloud längst die Basis. Als das sichtbar wurde, stieg die Aktie stark. Die App bewertet den Wachstumsschub mit «stark», «möglich» oder «kein grosser Schub in Sicht» und sagt dir, an welcher Kennzahl du früh siehst, ob er kommt.</p>
    <p><b>So passt das zusammen:</b> Die besten Kandidaten sind unterbewertet, haben einen Wachstumsschub und eine Qualität ab hellgrün. Gekauft wird erst, wenn auch das Timing dreht, also der Trigger ausgelöst ist oder der Kurs in einer Kaufzone hält. Die Filter «Unterbewertet», «Wachstumsschub» und «Beides» in der Übersicht helfen dir, diese Aktien zu finden. «Unterbewertet» heisst dort: mindestens 20 % günstiger als im eigenen 5-Jahres-Schnitt.</p>
    <h3>Deine Strategien</h3>
    <p>Jede Aktie hat einen oder mehrere Stile, nach denen du sie beurteilst. Du findest sie als Filter in der Übersicht.</p>
    <p><b>Dividende:</b> Wichtig sind eine sichere, steigende Ausschüttung, die vom Free Cashflow gedeckt ist, und wann und wie oft sie bezahlt wird. <b>Wachstum:</b> Wichtig sind Umsatz- und Gewinnwachstum, ob es sich beschleunigt und ob die Bewertung das schon vorwegnimmt. <b>Cashflow:</b> Wichtig ist, wie viel freies Geld die Firma im Verhältnis zum Börsenwert verdient und wofür sie es nutzt (Rückkäufe, Schuldenabbau, Dividende). <b>Qualität</b> und <b>Defensiv</b> stehen für stabile Firmen, die auch in schwachen Jahren gut verdienen.</p>
    <h3>Free Cashflow: das Geld, das wirklich übrig bleibt</h3>
    <p><b>Free Cashflow (FCF)</b> ist das Geld, das nach allen Kosten und Investitionen in der Kasse bleibt. Eine Firma, deren FCF Jahr für Jahr wächst, kann Aktien zurückkaufen (dann gehört jeder Aktie ein grösseres Stück der Firma), Schulden abzahlen oder Dividenden zahlen. Die App prüft sechs Fragen und vergibt bis 100 Punkte:</p>
    <p><b>1. Wächst er?</b> <b>2. Wie viel vom Umsatz bleibt?</b> (FCF-Marge: 10 Mrd. FCF bei 50 Mrd. Umsatz sind 20 %.) <b>3. Wie viel im Verhältnis zum Börsenwert?</b> (FCF-Rendite: 10 Mrd. FCF bei 100 Mrd. Börsenwert sind 10 %.) <b>4. Wie schnell wären die Schulden bezahlt?</b> (Stark ist, wenn der halbe FCF eines Jahres reicht.) <b>5. Wofür wird er genutzt?</b> (Rückkäufe, Schuldenabbau, Dividende. Steigt die Aktienzahl, wird dein Anteil kleiner.) <b>6. Ist er nachhaltig?</b> (Keine Verlustjahre, wenig Löhne in Aktien, und kein starker Kurszerfall, der zeigt, dass die Börse am künftigen FCF zweifelt.)</p>
    <p>Der Filter «Starker Cashflow» zeigt alle Aktien ab 70 Punkten. Die Sortierung «Free Cashflow» ordnet alle Aktien danach.</p>
    <h3>Branchenvergleich, fairer Wert und Hinweise</h3>
    <p>Diese drei Teile sind von InvestingPro inspiriert und werden jeden Samstag für über 1'000 Aktien aus grossen Indizes neu gerechnet (USA, Schweiz, Europa, UK, Kanada).</p>
    <p><b>Branchenvergleich:</b> Jede Firma wird mit ihrer eigenen Branche verglichen, in fünf Bereichen: Bewertung, Wachstum, Profitabilität, Cashflow und Bilanz, Kursmomentum. Je Bereich 0 bis 5 Punkte. Beispiel: Ist die Marge besser als bei 80 % der Branche, gibt das 4 Punkte. Die Gesamtnote ist der Schnitt, ab 2.75 gut, ab 3.5 sehr gut. Das ergänzt deine Qualitäts-Ampel: Die Ampel nutzt feste Grenzen, der Vergleich zeigt, ob die Firma in ihrer Branche vorne ist.</p>
    <p><b>Fairer Wert:</b> Bis zu sechs Modelle (DCF mit dem Free Cashflow, eigenes KGV, Branchen-KGV, Branchen-EV/EBITDA, Dividendenmodell, Buchwert bei Banken). Der faire Wert ist der Median. Liegen die Modelle weit auseinander, ist die Unsicherheit hoch. Das Analysten-Kursziel steht daneben, zählt aber nicht mit.</p>
    <p><b>Hinweise:</b> Bis zu acht kurze Sätze, was in den Zahlen auffällt, zum Beispiel «Dividende 12 Jahre in Folge erhöht» oder «Analysten haben die Gewinnschätzung in 90 Tagen gesenkt».</p>
    <p><b>Entdecken:</b> Im Tab «Entdecken» siehst du alle Aktien der Liste, filterbar nach deinen Strategien. Tippe eine an und fordere die ganze Analyse an.</p>
    <h3>Gegen den Strom: Angst als Chance</h3>
    <p>Wenn alle verkaufen und die Schlagzeilen nur noch schwarz malen, ist oft schon viel schlechte Nachricht im Kurs. Darum zeigt die App zwei Stimmungs-Anzeiger:</p>
    <p><b>Marktstimmung (Gesamtmarkt).</b> Der <b>Fear &amp; Greed Index</b> von CNN misst von 0 bis 100, wie ängstlich oder gierig die Anleger in den USA sind (aus sieben Werten wie Kursschwung, Absicherungen und Schwankung). Unter 25 heisst «Extreme Angst», über 75 «Extreme Gier». Dazu zeigt die App den S&amp;P 500 (Abstand zum Jahreshoch, Trend über oder unter der EMA 200) und den <b>VIX</b>, das «Angstbarometer» der Börse: über 20 nervös, über 30 Panik. Fällt der Index unter 25, bekommst du eine Push-Nachricht.</p>
    <p><b>Pessimismus pro Aktie (0 bis 100).</b> Setzt sich aus drei Teilen zusammen: wie weit die Aktie unter dem Jahreshoch steht, wie tief der Wochen-RSI ist und wie weit sie unter der Wochen-EMA 200 liegt. Ab 60 ist die Angst gross. Ist die Qualität dabei mindestens 50, zeigt die App ein <b>Kontra-Signal</b>. Bei Qualität ab 60 kommt zusätzlich eine Push-Nachricht.</p>
    <p><b>Wichtig:</b> Angst allein ist kein Kaufsignal. Manchmal ist eine Aktie zu Recht billig, weil das Geschäft schlechter wird. Darum immer zusammen lesen: Was befürchtet die Börse? Ist es Stimmung oder ein echtes Problem? Und dreht das Timing? Wer gegen den Strom kauft, kauft am besten gestaffelt, zum Beispiel ein Drittel beim Kontra-Signal in der Kaufzone, ein Drittel bei bestätigter Wende (Trigger) und ein Drittel nach den nächsten Zahlen. So musst du den Tiefpunkt nicht genau treffen.</p>
    <h3>Was sich automatisch aktualisiert</h3>
    <p>Jeden Börsentag nach US-Börsenschluss holt GitHub die neuen Kurse. Daraus rechnet die App EMA 50/200, RSI und A/D-Linie neu und passt die Timing-Punkte für Trend, RSI, A/D und Saisonalität an. In der Qualität wird die Bewertung mit dem Kurs neu gerechnet: Fällt der Kurs, wird die Aktie günstiger und bekommt eher mehr Punkte.</p>
    <p>Struktur (SMC) und Smart Money bleiben aus der letzten Analyse. Schliesst der Kurs über dem Trigger, springt die Struktur auf mindestens 16 von 20. Bricht der Wochenschluss die Abbruch-Marke, fällt sie auf 2.</p>
    <p>Auch die Dividenden holt die App jeden Tag neu: letzte Zahlungen, Rendite und der nächste erwartete Ex-Tag. Alles Fundamentale (Umsatz, Marge, Gewinn, Schulden) ändert sich erst mit neuen Quartalszahlen. Das aktualisieren wir zusammen im Monats-Check oder nach den Zahlen.</p>
    <h3>Jetzt interessant</h3>
    <p>Hier landet eine Aktie, wenn die Qualität mindestens 60 ist und zusätzlich der Kurs in oder knapp über einer Kaufzone liegt, der Trigger ausgelöst wurde oder das Timing mindestens 60 ist.</p>
    <h3>Auf dem iPhone installieren</h3>
    <p>In Safari öffnen, unten auf «Teilen» tippen und «Zum Home-Bildschirm» wählen. Die App startet dann ohne Browser-Leiste und funktioniert auch offline mit dem letzten Stand.</p>
    <h3>Benachrichtigungen aufs iPhone</h3>
    <p>Die App meldet sich über die kostenlose App «ntfy», wenn eine Aktie in die Kaufzone läuft, einen Trigger auslöst, unter die Abbruch-Marke fällt, das Timing auf hellgrün springt oder am nächsten Tag Zahlen kommen. Einrichtung: ntfy aus dem App Store laden, das persönliche Thema abonnieren und dasselbe Thema in GitHub als Secret <b>NTFY_TOPIC</b> eintragen.</p>
    <h3>Notizen auf allen Geräten</h3>
    <p>Ohne Schlüssel bleiben Notizen auf dem Gerät, auf dem du sie schreibst. Mit einem GitHub-Schlüssel (Fine-grained Token nur für dieses Repository, Recht «Contents: Read and write») landen sie in deinem Repository und sind auf iPhone und PC gleich.</p>
    <div class="tokenrow"><input id="tok" type="password" autocomplete="off" placeholder="${token() ? "Schlüssel ist gespeichert" : "GitHub-Schlüssel einfügen"}" aria-label="GitHub-Schlüssel">
      <button class="btn small" id="tok-save">${token() ? "Ersetzen" : "Speichern"}</button>${token() ? '<button class="btn small" id="tok-del">Entfernen</button>' : ""}</div>
    <p id="tok-state" style="font-size:13.5px;color:var(--muted)"></p>
    <h3>Stand der Daten</h3>
    <p>${L?.aktualisiert ? "Letztes Kurs-Update: " + new Date(L.aktualisiert).toLocaleString("de-CH") : "Noch kein automatisches Kurs-Update. Angezeigt werden die Werte der letzten Analysen."}${L?.fehler?.length ? "<br>Ohne neue Kurse: " + esc(L.fehler.map(x => x.split(":")[0]).join(", ")) : ""}</p>
    <p style="color:var(--muted);font-size:13.5px">Persönliche Watchlist, keine Anlageberatung.</p>
  </div>`;
  const ts = document.getElementById("tok-state");
  document.getElementById("tok-save").onclick = async () => {
    const v = document.getElementById("tok").value.trim(); if (!v) { ts.textContent = "Bitte zuerst den Schlüssel einfügen."; return; }
    ts.textContent = "Prüfe den Schlüssel …";
    const r = await fetch(`https://api.github.com/repos/${REPO}`, { headers: { Authorization: "Bearer " + v } }).catch(() => null);
    if (r && r.ok) { store.set("gh_token", v); ts.textContent = "Gespeichert. Notizen werden jetzt auf allen Geräten abgeglichen."; await load(); setTimeout(renderInfo, 900); }
    else ts.textContent = "Der Schlüssel funktioniert nicht. Prüfe, ob er für das Repository Aktien-Analyse gilt und «Contents: Read and write» erlaubt.";
  };
  const del = document.getElementById("tok-del"); if (del) del.onclick = () => { store.set("gh_token", ""); renderInfo(); };
  scrollTo(0, 0);
}

// ---------- Branchenvergleich, fairer Wert, Hinweise (Scanner) ----------
// Daten: data/scan.json, einmal pro Woche von GitHub gerechnet. Wird erst geladen, wenn man es braucht.
const SEK_DE = { "Technology": "Technologie", "Healthcare": "Gesundheit", "Financial Services": "Finanzen", "Consumer Cyclical": "Zyklischer Konsum",
  "Consumer Defensive": "Basiskonsum", "Industrials": "Industrie", "Energy": "Energie", "Basic Materials": "Rohstoffe", "Communication Services": "Kommunikation",
  "Utilities": "Versorger", "Real Estate": "Immobilien", "Andere": "Andere" };
const BER = [["bewertung", "Bewertung", "Wie günstig im Vergleich zum Gewinn, Free Cashflow und EBITDA"], ["wachstum", "Wachstum", "Umsatz-, Gewinn- und Cashflow-Wachstum, erwartetes Gewinnwachstum"],
  ["profit", "Profitabilität", "Bruttomarge, operative Marge, ROIC, Eigenkapitalrendite, Margen-Trend"], ["cashflow", "Cashflow und Bilanz", "FCF-Marge, Cash im Verhältnis zum Gewinn, Schulden, Aktienzahl"],
  ["momentum", "Kursmomentum", "Kursentwicklung 6 und 12 Monate, Trend, Änderung der Gewinnschätzungen"]];
const noteName = g => g == null ? "keine Note" : g >= 3.5 ? "sehr gut" : g >= 2.75 ? "gut" : g >= 2 ? "mittel" : g >= 1.25 ? "schwach" : "kritisch";
const noteAmpel = g => ampel((g ?? 0) * 20);
let scanPromise = null;
function ensureScan(force) {
  if (STATE.scan && !force) return Promise.resolve(STATE.scan);
  if (!scanPromise || force) scanPromise = getJSON("data/scan.json").then(j => (STATE.scan = j)).catch(() => (STATE.scan = { aktien: {}, sektoren: {}, fehlt: true }));
  return scanPromise;
}
const scanOf = s => STATE.scan?.aktien?.[s.symbol] || null;

function fvHtml(x) {
  const f = x.fv, w = x.w;
  if (!f || f.zu_wenig || f.wert == null) return `<div class="card prose"><p>Für einen fairen Wert gibt es zu wenig verlässliche Modelle. Das ist oft bei Firmen mit Verlust, stark schwankendem Cashflow oder wenig Daten der Fall.</p></div>`;
  const ok = f.modelle.filter(m => m[3]), vals = [...ok.map(m => m[1]), x.p, f.wert, ...(x.an?.ziel ? [x.an.ziel] : [])];
  const lo = Math.min(...vals) * 0.92, hi = Math.max(...vals) * 1.05, pos = v => ((v - lo) / (hi - lo) * 100).toFixed(1);
  const col = f.potenzial >= 15 ? "gruen" : f.potenzial > -15 ? "gelb" : "orange";
  const urteil = f.potenzial >= 30 ? "deutlich unterbewertet" : f.potenzial >= 15 ? "unterbewertet" : f.potenzial > -15 ? "etwa fair bewertet" : f.potenzial > -30 ? "überbewertet" : "deutlich überbewertet";
  const lo2 = Math.min(...ok.map(m => m[1])), hi2 = Math.max(...ok.map(m => m[1]));
  return `<div class="card fv">
    <div class="fv-top"><div><span>Fairer Wert</span><b>${money(f.wert, w)}</b></div><div><span>Kurs</span><b>${money(x.p, w)}</b></div>
      <div><span>Potenzial</span><b class="${col}-t">${pct(f.potenzial, 0)}</b></div></div>
    <p class="pill-line"><span class="pill p-${col}">${urteil}</span> Unsicherheit <b>${esc(f.unsicher)}</b> (${ok.length} Modelle${ok.length < f.modelle.length ? `, ${f.modelle.length - ok.length} unplausibel und weggelassen` : ""})</p>
    <div class="fv-bar" role="img" aria-label="Spanne der Modelle ${money(lo2, w)} bis ${money(hi2, w)}, fairer Wert ${money(f.wert, w)}, Kurs ${money(x.p, w)}">
      <span class="fv-rng" style="left:${pos(lo2)}%;width:${(pos(hi2) - pos(lo2)).toFixed(1)}%"></span>
      <i class="fv-fv" style="left:${pos(f.wert)}%"></i><i class="fv-px" style="left:${pos(x.p)}%"></i>${x.an?.ziel ? `<i class="fv-an" style="left:${pos(x.an.ziel)}%"></i>` : ""}</div>
    <div class="legend"><span><i style="background:var(--accent-soft);height:9px"></i>Spanne der Modelle</span><span><i style="background:var(--accent)"></i>Fairer Wert</span><span><i style="background:var(--ink)"></i>Kurs</span>${x.an?.ziel ? `<span><i style="background:var(--orange)"></i>Analysten-Ziel</span>` : ""}</div>
    <table class="fv-tab"><tbody>${f.modelle.map(m => `<tr class="${m[3] ? "" : "off"}"><td>${esc(m[0])}<small>${esc(m[2])}${m[3] ? "" : " · unplausibel, nicht gezählt"}</small></td><td class="n">${money(m[1], w)}</td><td class="n">${pct((m[1] / x.p - 1) * 100, 0)}</td></tr>`).join("")}
      ${x.an?.ziel ? `<tr class="an"><td>Analysten-Kursziel<small>Schnitt von ${x.an.n || "?"} Analysten, nicht im fairen Wert enthalten</small></td><td class="n">${money(x.an.ziel, w)}</td><td class="n">${pct((x.an.ziel / x.p - 1) * 100, 0)}</td></tr>` : ""}</tbody></table>
    <details class="more"><summary>So rechnet die App den fairen Wert</summary><ul class="plain">
      <li><b>DCF Free Cashflow:</b> Der Free Cashflow pro Aktie wächst 5 Jahre mit dem erwarteten Tempo, danach langsamer, ab Jahr 10 mit 2.5 % pro Jahr. Alles wird auf heute abgezinst (je schwankungsreicher die Aktie, desto höher der Zins).</li>
      <li><b>Eigenes KGV:</b> Gewinn pro Aktie mal das mittlere KGV der letzten Jahre.</li>
      <li><b>Branchen-KGV:</b> Erwarteter Gewinn pro Aktie mal das mittlere KGV der Branche.</li>
      <li><b>Branchen-EV/EBITDA:</b> Betriebsgewinn vor Abschreibungen mal das Branchen-Multiple, minus Nettoschulden.</li>
      <li><b>Dividendenmodell:</b> Nur bei Dividendenzahlern: Was sind alle künftigen Dividenden heute wert?</li>
      <li><b>Kurs/Buchwert:</b> Nur bei Banken, Versicherungen und Immobilien.</li>
      <li>Der faire Wert ist der <b>Median</b> der plausiblen Modelle. Liegen sie weit auseinander, ist die Unsicherheit hoch. Dann ist die Zahl nur ein grober Anhaltspunkt.</li>
    </ul></details></div>`;
}
function vergleichHtml(x) {
  const sek = STATE.scan?.sektoren?.[x.sek] || {};
  const rows = BER.map(([k, name, txt]) => {
    const n = x.k?.[k], r = x.rg?.[k];
    return `<div class="part"><span>${name}</span><span class="p">${n == null ? "–" : nf(n, 1) + " / 5"}</span>
      <div class="bar"><i style="width:${r ?? 0}%;background:${ampelVar(noteAmpel(n))}"></i></div>
      <div class="t">${r == null ? "Zu wenig Daten." : `Besser als ${nf(r, 0)} % der Branche.`} ${txt}.</div></div>`;
  }).join("");
  const d = x.d || {};
  const vgl = [["KGV", d.kgv, sek.kgv, false], ["Erwartetes KGV", d.kgv_f, sek.kgv_f, false], ["Operative Marge", d.op_marge, sek.op_marge, true, " %"],
    ["Umsatzwachstum", d.umsatz_wachstum, sek.umsatz_wachstum, true, " %"], ["FCF-Rendite", d.fcf_rendite, sek.fcf_rendite, true, " %"]].filter(r => r[1] != null && r[2] != null);
  return `<div class="card">
    <div class="vg-top"><span class="lamp ${noteAmpel(x.g)} vg-l">${x.g == null ? "–" : nf(x.g, 1)}</span>
      <div><b>Gesamtnote ${x.g == null ? "–" : nf(x.g, 1) + " von 5"} (${noteName(x.g)})</b><span>${x.grang != null ? `Besser als ${x.grang} % von ${x.gn} Firmen der Branche ${esc(SEK_DE[x.sek] || x.sek)}` : `Branche ${esc(SEK_DE[x.sek] || x.sek)}`}</span></div></div>
    ${partsHtml0(rows)}
    ${vgl.length ? `<table class="fv-tab vg-tab"><thead><tr><th>Kennzahl</th><th class="n">Firma</th><th class="n">Branche (Mitte)</th></tr></thead><tbody>${vgl.map(([n, a, b, hoch, u = ""]) => {
      const gut = hoch ? a > b : a < b; return `<tr><td>${n}</td><td class="n ${gut ? "up" : "down"}">${nf(a, 1)}${u}</td><td class="n">${nf(b, 1)}${u}</td></tr>`; }).join("")}</tbody></table>
      <p class="fc-cap">Grün: besser als die Mitte der Branche. Beim KGV ist tiefer besser (günstiger).</p>` : ""}
    <details class="more"><summary>So funktioniert der Branchenvergleich</summary><ul class="plain">
      <li>Die App vergleicht die Firma mit allen Firmen derselben Branche aus den grossen Indizes (aktuell ${STATE.scan?.anzahl || "viele"} Firmen). Eine Marge von 15 % ist bei einem Restaurant stark, bei einer Software-Firma schwach. Darum zählt der Rang in der Branche, keine feste Grenze.</li>
      <li>Pro Bereich werden mehrere Kennzahlen verglichen. «Besser als 80 %» heisst: nur 20 % der Branche sind besser. Daraus werden 0 bis 5 Punkte (80 % = 4 Punkte).</li>
      <li>Ab 2.75 gilt die Note als gut, ab 3.5 als sehr gut. Gleiche Idee wie die «Financial Health» bei InvestingPro.</li>
      <li>Bei Banken und Versicherungen zählen Free Cashflow und EBITDA nicht, weil sie dort wenig aussagen.</li>
      <li>Daten von Yahoo Finance, Stand ${fmtDate(STATE.scan?.stand)}. Neu gerechnet jeden Samstag.</li></ul></details></div>`;
}
const partsHtml0 = rows => `<div class="parts" style="margin-top:12px">${rows}</div>`;
function hinweisHtml(x) {
  if (!x.h?.length) return `<div class="card prose"><p>Keine auffälligen Hinweise.</p></div>`;
  return `<div class="card"><ul class="hw">${x.h.map(([a, t]) => `<li class="hw-${a}"><i aria-hidden="true">${a === "g" ? "+" : "!"}</i><span>${esc(t)}</span></li>`).join("")}</ul>
    <p class="fc-cap">Automatisch aus den Zahlen erzeugt, ähnlich den «ProTips» bei InvestingPro. Grün spricht für die Aktie, rot ist ein Warnsignal.</p></div>`;
}
function scanBlock(x) {
  return `<div class="sec" id="vergleich"><h2>Branchenvergleich</h2><p>Wie gut ist die Firma im Vergleich mit ihrer eigenen Branche?</p></div>${vergleichHtml(x)}
    <div class="sec"><h2>Fairer Wert</h2><p>Was die Aktie nach mehreren Bewertungsmodellen wert sein könnte.</p></div>${fvHtml(x)}
    <div class="sec"><h2>Hinweise</h2><p>Was aus den Zahlen auffällt.</p></div>${hinweisHtml(x)}`;
}
function scanSlot(s) {
  // Platzhalter im Detail, wird gefüllt, sobald scan.json geladen ist
  setTimeout(() => ensureScan().then(() => {
    const el = document.getElementById("scanslot"); if (!el) return;
    const x = scanOf(s);
    el.innerHTML = x ? scanBlock(x) : `<div class="sec"><h2>Branchenvergleich und fairer Wert</h2></div><div class="empty">${STATE.scan?.fehlt ? "Die Vergleichsdaten werden am Samstag zum ersten Mal gerechnet." : "Für diese Aktie fehlen noch Vergleichsdaten. Sie kommen mit dem nächsten Wochenlauf."}</div>`;
  }), 0);
  return `<div id="scanslot"><div class="sec"><h2>Branchenvergleich und fairer Wert</h2></div><div class="empty">Lade Vergleichsdaten …</div></div>`;
}

// ---------- Entdecken: alle Aktien aus dem Universum ----------
const LINSEN = [["alle", "Alle"], ["unter", "Unterbewertet"], ["dividende", "Dividende"], ["cashflow", "Cashflow"], ["wachstum", "Wachstum"], ["qualitaet", "Qualität"]];
const linseOk = (x, l) => {
  const d = x.d || {}, k = x.k || {}, f = x.fv || {};
  if (l === "unter") return f.potenzial >= 20 && ["niedrig", "mittel"].includes(f.unsicher) && (x.g ?? 0) >= 2.5;
  if (l === "dividende") return d.div_rendite >= 2.5 && (d.ausschuettung ?? 999) < 85 && (d.div_serie ?? 0) >= 3;
  if (l === "cashflow") return d.fcf_rendite >= 5 && (d.netto_cash || (d.schulden_fcf ?? 99) <= 3) && (k.cashflow ?? 0) >= 3;
  if (l === "wachstum") return (d.umsatz_cagr3 ?? 0) >= 10 && (k.wachstum ?? 0) >= 3.5;
  if (l === "qualitaet") return (k.profit ?? 0) >= 3.5 && (x.g ?? 0) >= 3;
  return true;
};
const SORTS = [["note", "Gesamtnote"], ["fv", "Fairer Wert (Potenzial)"], ["fcf", "FCF-Rendite"], ["div", "Dividendenrendite"], ["wachs", "Umsatzwachstum 3 Jahre"], ["mom", "Kursmomentum"], ["mc", "Börsenwert"], ["name", "Name"]];
const sortFn = {
  note: (a, b) => (b.g ?? -1) - (a.g ?? -1), fv: (a, b) => (b.fv?.potenzial ?? -999) - (a.fv?.potenzial ?? -999),
  fcf: (a, b) => (b.d?.fcf_rendite ?? -999) - (a.d?.fcf_rendite ?? -999), div: (a, b) => (b.d?.div_rendite ?? -1) - (a.d?.div_rendite ?? -1),
  wachs: (a, b) => (b.d?.umsatz_cagr3 ?? -999) - (a.d?.umsatz_cagr3 ?? -999), mom: (a, b) => (b.d?.mom_12_1 ?? -999) - (a.d?.mom_12_1 ?? -999),
  mc: (a, b) => (b.mc ?? 0) - (a.mc ?? 0), name: (a, b) => (a.n || "").localeCompare(b.n || "", "de")
};
function entRow(x) {
  const f = x.fv;
  const href = x.app ? `#/aktie/${encodeURIComponent(x.app)}` : `#/scan/${encodeURIComponent(x.sym)}`;
  return `<a class="row er" href="${href}"><span class="lamp ${noteAmpel(x.g)} er-l" title="Gesamtnote">${x.g == null ? "–" : nf(x.g, 1)}</span>
    <div class="mid"><div class="nm">${esc(x.n || x.sym)}</div><div class="sub">${esc(x.sym)} · ${esc(x.land || x.reg || "")} · ${esc(SEK_DE[x.sek] || x.sek)}${x.app ? " · in der App" : ""}</div>
      <div class="er-k">${BER.map(([k, n]) => `<i title="${n} ${x.k?.[k] ?? "–"}" style="background:${x.k?.[k] == null ? "var(--surface2)" : ampelVar(noteAmpel(x.k[k]))}"></i>`).join("")}</div></div>
    <div class="right"><div class="px">${money(x.p, x.w)}</div>${f?.potenzial != null ? `<div class="er-fv ${f.potenzial >= 15 ? "up" : f.potenzial <= -15 ? "down" : ""}">Fair ${pct(f.potenzial, 0)}</div>` : ""}</div></a>`;
}
function renderEntdecken() {
  $view.innerHTML = `<header class="top"><div><h1>Entdecken</h1><div class="stand">Lade die Liste …</div></div></header><div class="empty">Einen Moment.</div>`;
  ensureScan().then(() => drawEntdecken());
}
function drawEntdecken() {
  const S = STATE.scan, F = STATE.ent || (STATE.ent = store.get("ent", { linse: "alle", reg: "Alle", sek: "Alle", sort: "note", q: "", n: 40 }));
  if (!S || S.fehlt || !Object.keys(S.aktien || {}).length) {
    $view.innerHTML = `<header class="top"><div><h1>Entdecken</h1></div></header><div class="empty">Die Liste wird gerade zum ersten Mal gerechnet. Schau in einer Stunde wieder rein.</div>`; return;
  }
  const all = Object.values(S.aktien);
  const regs = ["Alle", ...["USA", "Schweiz", "Europa", "Kanada", "Asien"].filter(r => all.some(x => x.reg === r))];
  const seks = ["Alle", ...Object.keys(S.sektoren || {}).filter(k => k !== "Andere").sort((a, b) => (SEK_DE[a] || a).localeCompare(SEK_DE[b] || b, "de"))];
  const q = F.q.trim().toLowerCase();
  const base = all.filter(x => (F.reg === "Alle" || x.reg === F.reg) && (F.sek === "Alle" || x.sek === F.sek) && (!q || `${x.n} ${x.sym} ${x.br || ""}`.toLowerCase().includes(q)));
  const list = base.filter(x => linseOk(x, F.linse)).sort(sortFn[F.sort] || sortFn.note);
  const cnt = Object.fromEntries(LINSEN.map(([k]) => [k, base.filter(x => linseOk(x, k)).length]));
  const save = () => store.set("ent", F);
  $view.innerHTML = `<header class="top"><div><h1>Entdecken</h1><div class="stand">${S.anzahl} Aktien aus grossen Indizes · Stand ${fmtDate(S.stand)}</div></div></header>
    <p class="intro">Alle Aktien mit Branchenvergleich, fairem Wert und Hinweisen. Gefällt dir eine, tippe sie an und lass die ganze Analyse machen.</p>
    <div class="controls" id="controls">
      <div class="search"><input id="eq" type="search" placeholder="Name oder Kürzel" value="${esc(F.q)}" aria-label="Suche">
        <select id="esort" aria-label="Sortierung">${SORTS.map(([k, l]) => `<option value="${k}" ${F.sort === k ? "selected" : ""}>${l}</option>`).join("")}</select></div>
      <div class="chips" role="group" aria-label="Strategie">${LINSEN.map(([k, l]) => `<button class="chip" data-el="${k}" aria-pressed="${F.linse === k}">${l}<span class="n">${cnt[k]}</span></button>`).join("")}</div>
      <div class="chips" role="group" aria-label="Region">${regs.map(r => `<button class="chip" data-er="${esc(r)}" aria-pressed="${F.reg === r}">${r === "Alle" ? "Alle Regionen" : r}</button>`).join("")}
        <select id="esek" class="chip" aria-label="Branche">${seks.map(k => `<option value="${esc(k)}" ${F.sek === k ? "selected" : ""}>${k === "Alle" ? "Alle Branchen" : esc(SEK_DE[k] || k)}</option>`).join("")}</select></div>
    </div>
    <div class="count">${list.length} Aktien${F.linse !== "alle" ? ` · Filter «${LINSEN.find(l => l[0] === F.linse)[1]}»` : ""}</div>
    <div class="list">${list.slice(0, F.n).map(entRow).join("") || `<div class="empty">Keine Aktie passt zu diesen Filtern.</div>`}</div>
    ${list.length > F.n ? `<button class="btn" id="emore" style="margin-top:12px;width:100%">${Math.min(40, list.length - F.n)} weitere zeigen</button>` : ""}
    <details class="more"><summary>Was die Filter bedeuten</summary><ul class="plain">
      <li><b>Unterbewertet:</b> Fairer Wert mindestens 20 % über dem Kurs, Unsicherheit höchstens mittel, Gesamtnote ab 2.5.</li>
      <li><b>Dividende:</b> Rendite ab 2.5 %, höchstens 85 % des Gewinns ausgeschüttet, mindestens 3 Erhöhungen in Folge.</li>
      <li><b>Cashflow:</b> FCF-Rendite ab 5 %, Schulden in höchstens 3 Jahren aus dem Free Cashflow bezahlt (oder Netto-Cash), Cashflow-Note ab 3.</li>
      <li><b>Wachstum:</b> Umsatz wächst seit 3 Jahren um mindestens 10 % pro Jahr, Wachstumsnote ab 3.5.</li>
      <li><b>Qualität:</b> Profitabilität ab 3.5 und Gesamtnote ab 3.</li>
      <li>Die fünf Striche zeigen die Noten für Bewertung, Wachstum, Profitabilität, Cashflow und Momentum.</li></ul></details>`;
  const re = () => { save(); const y = scrollY; drawEntdecken(); scrollTo(0, y); };
  $view.querySelectorAll("[data-el]").forEach(b => b.onclick = () => { F.linse = b.dataset.el; F.n = 40; re(); });
  $view.querySelectorAll("[data-er]").forEach(b => b.onclick = () => { F.reg = b.dataset.er; F.n = 40; re(); });
  document.getElementById("esek").onchange = e => { F.sek = e.target.value; F.n = 40; re(); };
  document.getElementById("esort").onchange = e => { F.sort = e.target.value; re(); };
  let t; document.getElementById("eq").oninput = e => { clearTimeout(t); t = setTimeout(() => { F.q = e.target.value; F.n = 40; save(); drawEntdecken(); const i = document.getElementById("eq"); i.focus(); i.setSelectionRange(i.value.length, i.value.length); }, 250); };
  const m = document.getElementById("emore"); if (m) m.onclick = () => { F.n += 40; re(); };
}
function renderScanDetail(sym) {
  $view.innerHTML = `<a class="back" href="#/entdecken"><svg viewBox="0 0 24 24"><path d="M15 5l-7 7 7 7"/></svg>Entdecken</a><div class="empty">Lade …</div>`;
  ensureScan().then(() => {
    const x = STATE.scan?.aktien?.[sym];
    if (!x) { $view.innerHTML = `<a class="back" href="#/entdecken">Zurück</a><div class="empty">Diese Aktie ist nicht in der Liste.</div>`; return; }
    if (x.app) { location.replace("#/aktie/" + encodeURIComponent(x.app)); return; }
    const d = x.d || {};
    const fact = (n, v, u = "") => v == null ? "" : `<dt>${n}</dt><dd>${nf(v, 1)}${u}</dd>`;
    $view.innerHTML = `<a class="back" href="#/entdecken"><svg viewBox="0 0 24 24"><path d="M15 5l-7 7 7 7"/></svg>Entdecken</a>
      <div class="dhead"><h1>${esc(x.n || x.sym)}</h1><div class="meta">${esc(x.sym)} · ${esc(x.land || x.reg || "")} · ${esc(SEK_DE[x.sek] || x.sek)}${x.br ? " · " + esc(x.br) : ""}</div>
        <div class="dprice"><span class="px">${money(x.p, x.w)}</span></div><div class="meta">${x.idx?.length ? "Im Index " + esc(x.idx.join(", ")) + " · " : ""}Börsenwert ${nf(x.mc, x.mc >= 10 ? 0 : 1)} Mrd. CHF</div></div>
      <div class="banner info">Automatische Kurzbewertung. Für Qualitäts- und Timing-Ampel, Zonen, Sorgen und Wachstumsschub braucht es die ganze Analyse.</div>
      <div class="card wunsch"><form id="wunsch-form" class="tokenrow"><input id="wunsch-in" type="text" value="${esc(x.n || x.sym)} (${esc(x.sym)})" aria-label="Aktie">
        <button class="btn small primary" type="submit">Ganze Analyse anfordern</button></form><p class="w-msg" id="wmsg" hidden></p></div>
      ${scanBlock(x)}
      <div class="sec"><h2>Kennzahlen</h2></div>
      <div class="card"><dl class="facts">${fact("KGV", d.kgv)}${fact("Erwartetes KGV", d.kgv_f)}${fact("KGV-Schnitt eigene Jahre", d.kgv_hist)}${fact("FCF-Rendite", d.fcf_rendite, " %")}${fact("Dividendenrendite", d.div_rendite, " %")}
        ${d.div_serie ? `<dt>Dividende erhöht</dt><dd>${d.div_serie_max ? "seit mindestens " + d.div_serie + " Jahren jedes Jahr" : d.div_serie + " Jahre in Folge"}</dd>` : ""}${fact("Umsatzwachstum letztes Jahr", d.umsatz_wachstum, " %")}${fact("Umsatzwachstum 3 Jahre (pro Jahr)", d.umsatz_cagr3, " %")}
        ${fact("Operative Marge", d.op_marge, " %")}${fact("ROIC", d.roic, " %")}${fact("Free-Cashflow-Marge", d.fcf_marge, " %")}${d.netto_cash ? "<dt>Schulden</dt><dd>Mehr Cash als Schulden</dd>" : fact("Schulden in Jahren FCF", d.schulden_fcf)}
        ${fact("Aktienzahl pro Jahr", d.aktien_pa, " %")}${fact("Kurs 12 Monate", d.mom_12_1, " %")}${fact("Unter dem Jahreshoch", d.unter_hoch, " %")}</dl></div>
      <p class="fc-cap">Keine Anlageberatung.</p>`;
    const f = document.getElementById("wunsch-form");
    f.onsubmit = async e => { e.preventDefault(); const msg = document.getElementById("wmsg"); msg.hidden = false;
      const text = document.getElementById("wunsch-in").value.trim();
      try { const r = await fetch(`https://ntfy.sh/${WUNSCH_TOPIC}`, { method: "POST", body: text }); if (!r.ok) throw 0;
        store.set("wuensche_local", [...store.get("wuensche_local", []), { text, ts: Date.now() }]); msg.textContent = "Gesendet. Claude macht die ganze Analyse heute Abend, du bekommst eine Push-Nachricht."; }
      catch { msg.textContent = "Senden hat nicht geklappt. Bist du online?"; } };
    scrollTo(0, 0);
  });
}

// ---------- Routing ----------
function route() {
  const h = location.hash || "#/";
  const tab = h.startsWith("#/termine") ? "termine" : h.startsWith("#/info") ? "info" : h.startsWith("#/depot") ? "depot" : h.startsWith("#/entdecken") || h.startsWith("#/scan/") ? "entdecken" : "home";
  document.querySelectorAll(".tabs a").forEach(a => a.dataset.tab === tab ? a.setAttribute("aria-current", "page") : a.removeAttribute("aria-current"));
  if (h.startsWith("#/aktie/")) renderDetail(decodeURIComponent(h.slice(8)));
  else if (h.startsWith("#/scan/")) renderScanDetail(decodeURIComponent(h.slice(7)));
  else if (tab === "entdecken") renderEntdecken();
  else if (tab === "termine") renderTermine();
  else if (tab === "info") renderInfo();
  else if (tab === "depot") window.Depot ? window.Depot.render($view, h.startsWith("#/depot/neu/") ? decodeURIComponent(h.slice(12)) : null) : ($view.innerHTML = '<div class="empty">Das Depot konnte nicht geladen werden.</div>');
  else { renderHome(); const y = store.get("homeScroll", 0); if (y) scrollTo(0, y); }
}
let lastHash = location.hash;
addEventListener("hashchange", () => {
  if (!lastHash.startsWith("#/aktie/") && !lastHash.startsWith("#/termine") && !lastHash.startsWith("#/info") && !lastHash.startsWith("#/depot") && !lastHash.startsWith("#/entdecken") && !lastHash.startsWith("#/scan/")) store.set("homeScroll", scrollY);
  lastHash = location.hash; route();
});

async function refresh() {
  const b = document.getElementById("reload"); b?.classList.add("spin");
  try { await load(true); if (STATE.scan) await ensureScan(true); } catch (e) { console.warn(e); }
  b?.classList.remove("spin"); route();
}

async function start() {
  STATE.filter = { ...STATE.filter, ...store.get("filter", {}) };
  try { await load(); route(); }
  catch (e) { $view.innerHTML = `<div class="empty">Die Daten konnten nicht geladen werden. Prüfe die Internetverbindung und lade die Seite neu.</div>`; }
  if ("serviceWorker" in navigator && location.protocol === "https:") navigator.serviceWorker.register("sw.js").catch(() => {});
  document.addEventListener("visibilitychange", async () => {
    if (document.visibilityState !== "visible") return;
    const before = STATE.live?.aktualisiert;
    try { await load(); } catch { return; }
    if (STATE.live?.aktualisiert !== before) route();
  });
}
window.AA = { STATE, view, money, nf, pct, esc, fmtDate, ampel, ampelName, signal, divData, token, b64, unb64, REPO, STATUS };
start();
})();
