/* Aktien-Ampel – App-Logik (ohne Framework, läuft direkt auf GitHub Pages) */
(() => {
"use strict";

const REPO = "pasidreamer/Aktien-Analyse";
const NOTES_PATH = "data/notizen.json";
const STATE = { stocks: [], live: null, verlauf: {}, notes: {}, filter: { q: "", stil: "Alle", region: "Alle", status: "Alle", nurGut: false, sort: "chance" } };
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
const regionCode = { "USA": "US", "Schweiz": "CH", "Grossbritannien": "UK", "Frankreich": "FR", "Deutschland": "DE", "Niederlande": "NL" };
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

// ---------- Daten ----------
async function getJSON(url) {
  const r = await fetch(url + (url.includes("?") ? "&" : "?") + "t=" + Date.now(), { cache: "no-store" });
  if (!r.ok) throw new Error(url + " " + r.status);
  return r.json();
}
async function load(force) {
  const [s, l, v, n] = await Promise.allSettled([getJSON("data/stocks.json"), getJSON("data/live.json"), getJSON("data/verlauf.json"), loadNotes()]);
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
    bew: bewertungOf(s, kurs), schub: s.chance?.schub_stufe === "stark"
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
      <div class="sub">${esc(s.ticker)} · ${esc(regionCode[s.land] || s.land)} · ${esc(s.tags[0])}${s.status !== "beobachten" ? " · " + LISTE[s.status] : ""}${STATE.notes[s.ticker]?.text?.trim() ? " · Notiz" : ""}</div>
      ${v.bew?.unter || v.schub ? `<div class="tags">${v.bew?.unter ? `<span class="tg tg-unter">${nf(v.bew.abschlag, 0)} % günstiger als üblich</span>` : ""}${v.schub ? '<span class="tg tg-schub">Wachstumsschub</span>' : ""}</div>` : ""}</div>
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

// Kurs-Chart mit EMA und Zonen
function chartHtml(v) {
  const ch = v.L?.chart; const s = v.s;
  if (!ch || !ch.c?.length) return `<div class="empty">Der Chart erscheint nach dem ersten automatischen Update der Kurse.</div>`;
  const W = 340, H = 190, P = { l: 6, r: 44, t: 8, b: 20 };
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
  const hline = (y, col, lab) => y && y >= lo && y <= hi ? `<line x1="${P.l}" x2="${W - P.r}" y1="${Y(y)}" y2="${Y(y)}" stroke="${col}" stroke-dasharray="4 3" stroke-width="1.2"/><text class="ax" x="${W - P.r + 3}" y="${Y(y) + 3}" fill="${col}">${lab}</text>` : "";
  const ticks = [lo + pad, (lo + hi) / 2, hi - pad].map(y => `<text class="ax" x="${W - P.r + 3}" y="${Y(y) + 3}">${nf(y, y >= 1000 ? 0 : y >= 100 ? 0 : 1)}</text>`).join("");
  const months = []; let last = "";
  ch.d.forEach((d, i) => { const m = d.slice(5, 7); if (m !== last && i > 3) { months.push(`<text class="ax" x="${X(i)}" y="${H - 5}" text-anchor="middle">${["Jan","Feb","Mär","Apr","Mai","Jun","Jul","Aug","Sep","Okt","Nov","Dez"][+m - 1]}</text>`); } last = m; });
  return `<div class="card chart"><svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Kursverlauf der letzten 6 Monate mit Zonen">
    ${(s.zonen.kauf || []).map(z => band(z, "var(--gruen-soft)")).join("")}
    ${(s.zonen.widerstand || []).map(z => band(z, "var(--rot-soft)")).join("")}
    ${hline(s.zonen.trigger, "var(--accent)", "Trigger")}${hline(s.zonen.abbruch, "var(--rot)", "Abbruch")}
    <path d="${path(ch.e200)}" fill="none" stroke="var(--orange)" stroke-width="1.4"/>
    <path d="${path(ch.e50)}" fill="none" stroke="var(--gelb)" stroke-width="1.4"/>
    <path d="${path(ch.c)}" fill="none" stroke="var(--ink)" stroke-width="2"/>
    ${ticks}${months.join("")}
  </svg>
  <div class="legend"><span><i style="background:var(--ink)"></i>Kurs</span><span><i style="background:var(--gelb)"></i>EMA 50</span><span><i style="background:var(--orange)"></i>EMA 200</span><span><i style="background:var(--gruen-soft);height:9px"></i>Kaufzone</span><span><i style="background:var(--rot-soft);height:9px"></i>Widerstand</span></div></div>`;
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
    if (f.status !== "Alle" && s.status !== f.status) return false;
    if (f.nurGut && v.q < 60) return false;
    const fk = f.fokus || "Alle";
    if (fk === "unter" && !v.bew?.unter) return false;
    if (fk === "schub" && !v.schub) return false;
    if (fk === "beides" && !(v.bew?.unter && v.schub)) return false;
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
  const tags = ["Wachstum", "Qualität", "Dividende", "Defensiv", "ETF"].filter(t => t === "ETF" ? STATE.stocks.some(s => s.tags.includes("ETF")) : true);
  const cnt = k => Object.fromEntries([["Alle", STATE.stocks.length], ...[...new Set(STATE.stocks.flatMap(s => k === "stil" ? s.tags : [s[k]]))].map(x => [x, STATE.stocks.filter(s => k === "stil" ? s.tags.includes(x) : s[k] === x).length])]);
  const regions = ["USA", "Europa", "Schweiz", "Asien", "Welt"].filter(r => STATE.stocks.some(s => s.region === r));
  const stand = STATE.live?.aktualisiert ? new Date(STATE.live.aktualisiert) : null;
  $view.innerHTML = `
    <header class="top"><div><h1>Aktien-Ampel</h1>
      <div class="stand">${stand ? `Kurse vom ${stand.toLocaleDateString("de-CH")}, ${stand.toLocaleTimeString("de-CH", { hour: "2-digit", minute: "2-digit" })} Uhr` : "Werte der letzten Analysen, Kurse folgen nach dem ersten Update"}</div></div>
      <button class="iconbtn" id="reload" aria-label="Daten neu laden"><svg viewBox="0 0 24 24"><path d="M20 12a8 8 0 1 1-2.3-5.6M20 4v5h-5"/></svg></button></header>

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
          ${[["chance", "Beste Chance"], ["qualitaet", "Qualität"], ["timing", "Timing"], ["unterbewertung", "Am stärksten unterbewertet"], ["zone", "Nähe zur Kaufzone"], ["tag", "Tagesveränderung"], ["zahlen", "Nächste Zahlen"], ["dividende", "Dividende"], ["name", "Name"]].map(([k, l]) => `<option value="${k}" ${STATE.filter.sort === k ? "selected" : ""}>${l}</option>`).join("")}
        </select></div>
      <div class="chips" role="group" aria-label="Chancen">${chipRow("fokus", [["Alle", "Alle Chancen"], ["unter", "Unterbewertet"], ["schub", "Wachstumsschub"], ["beides", "Beides"]],
        { Alle: all.length, unter: all.filter(v => v.bew?.unter).length, schub: all.filter(v => v.schub).length, beides: all.filter(v => v.bew?.unter && v.schub).length })}</div>
      <div class="chips" role="group" aria-label="Stil">${chipRow("stil", [["Alle", "Alle"], ...tags.map(t => [t, t])], cnt("stil"))}</div>
      <div class="chips" role="group" aria-label="Region und Liste">${chipRow("region", [["Alle", "Alle Regionen"], ...regions.map(r => [r, r])], cnt("region"))}<span class="sep"></span>
        ${chipRow("status", [["Alle", "Alle Listen"], ...["depot", "kaufliste", "beobachten"].filter(x => STATE.stocks.some(s => s.status === x)).map(x => [x, LISTE[x]])])}<span class="sep"></span>
        <button class="chip" id="nurGut" aria-pressed="${STATE.filter.nurGut}">Nur Qualität ab 60</button></div>
    </div>
    <div class="count">${list.length} von ${STATE.stocks.length} Aktien</div>
    <div class="list">${list.map(rowHtml).join("") || `<div class="empty">Keine Aktie passt zu diesen Filtern. Setze einen Filter auf «Alle» zurück.</div>`}</div>
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
  const sg = c?.sorgen?.length ? `<h3>Was die Börse befürchtet</h3>${c.sorgen_art ? `<p class="pill-line"><span class="pill p-${esc(c.sorgen_art)}">${esc(SORGE[c.sorgen_art] || c.sorgen_art)}</span> ${esc(c.sorgen_art_text || "")}</p>` : ""}<ul class="plain">${c.sorgen.map(x => `<li>${esc(x)}</li>`).join("")}</ul>` : "";
  const au = c?.aufloeser?.length ? `<h3>Was die Sorgen beenden könnte</h3><ul class="plain when">${c.aufloeser.map(x => `<li><span>${esc(x.was)}</span><em>${esc(x.wann || "")}</em></li>`).join("")}</ul>` : "";
  const sb = c ? (SCHUB[c.schub_stufe] || SCHUB.mittel) : null;
  const schub = c ? `<div class="card ch-card"><div class="ch-head"><h3>Wachstumsschub</h3><span class="pill p-${sb[1]}">${sb[0]}</span></div>
    <ol class="treiber">${(c.schub_treiber || []).map(x => `<li><b>${esc(x.titel)}</b><span>${esc(x.text)}</span>${x.wann ? `<em>${esc(x.wann)}</em>` : ""}</li>`).join("")}</ol>
    ${c.schub_beweis ? `<p class="beweis"><b>Woran du es erkennst:</b> ${esc(c.schub_beweis)}</p>` : ""}</div>` : "";
  return `<div class="sec"><h2>Worauf du achten solltest</h2><p>Deine zwei Blickwinkel: Ist die Aktie wegen Sorgen zu günstig, und gibt es einen grossen Wachstumsschub?</p></div>
    <div class="card ch-card"><div class="ch-head"><h3>Unterbewertung</h3></div>${meter}${sg}${au}${!c ? '<p class="pill-line" style="margin-top:10px">Die Recherche zu Sorgen und Wachstumsschub folgt.</p>' : ""}</div>
    ${schub}
    ${c?.szenario ? `<div class="banner plain szen"><b>Das Chancen-Szenario:</b> ${esc(c.szenario)}</div>` : ""}
    ${c?.quellen?.length ? `<details class="more"><summary>Quellen zu Sorgen und Wachstum</summary><ul class="plain">${c.quellen.map(q => `<li><a href="${esc(q.url)}" target="_blank" rel="noopener">${esc(q.titel)}</a></li>`).join("")}</ul></details>` : ""}`;
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

    ${chanceHtml(v)}

    <div class="sec"><h2>Meine Notiz</h2><p>${token() ? "Wird auf allen Geräten gespeichert." : "Wird auf diesem Gerät gespeichert. Für alle Geräte unter «So funktioniert's» den GitHub-Schlüssel eintragen."}</p></div>
    <div class="note"><textarea id="note" rows="4" placeholder="Zum Beispiel: Warum ich sie beobachte, mein Kaufplan, was ich nach den Zahlen prüfen will">${esc(STATE.notes[s.ticker]?.text || "")}</textarea>
      <div class="note-bar"><span id="note-state">${STATE.notes[s.ticker]?.ts ? "Zuletzt geändert " + new Date(STATE.notes[s.ticker].ts).toLocaleString("de-CH", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" }) : ""}</span>
      <button class="btn small" id="note-save">Notiz speichern</button></div></div>

    <div class="sec"><h2>Chart und Zonen</h2><p>Letzte 6 Monate, Tageskurse.</p></div>
    ${chartHtml(v)}
    <div class="zones" style="margin-top:10px">${zoneRows.map(r => `<div class="zone${p >= r.lo && p <= r.hi && r.lo !== r.hi ? " here" : ""}"><i class="k" style="background:${r.c}"></i><span><b>${rng(r.lo, r.hi)}</b> ${esc(r.txt)}</span><span class="dist">${distTo(r)}</span></div>`).join("")}</div>
    ${s.zonen_text?.length ? `<details class="more"><summary>Was die Zonen bedeuten</summary><ul class="plain">${s.zonen_text.map(x => `<li><b>${esc(x.wert)}</b>: ${esc(x.text)}</li>`).join("")}</ul></details>` : ""}

    <div class="sec"><h2>Timing ${v.t} von 100</h2><p>Teile mit «automatisch» rechnet die App jeden Börsentag neu.</p></div>
    <div class="card">${partsHtml(v.tParts)}</div>

    <div class="sec"><h2>Qualität ${v.q} von 100</h2><p>Aus der letzten Analyse. Die Bewertung passt sich dem Kurs an.</p></div>
    <div class="card">${partsHtml(v.qParts)}</div>

    <div class="sec"><h2>Wichtige Kennzahlen</h2></div>
    <div class="kpis">${s.kpis.filter(k => !/^Dividende/.test(k.name)).map(k => `<div class="kpi ${esc(k.ampel)}"><span>${esc(k.name)}</span><b>${esc(k.wert)}</b><em>${esc(k.text)}</em></div>`).join("")}${divKpi(s, v)}</div>

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

// ---------- Routing ----------
function route() {
  const h = location.hash || "#/";
  const tab = h.startsWith("#/termine") ? "termine" : h.startsWith("#/info") ? "info" : "home";
  document.querySelectorAll(".tabs a").forEach(a => a.dataset.tab === tab ? a.setAttribute("aria-current", "page") : a.removeAttribute("aria-current"));
  if (h.startsWith("#/aktie/")) renderDetail(decodeURIComponent(h.slice(8)));
  else if (tab === "termine") renderTermine();
  else if (tab === "info") renderInfo();
  else { renderHome(); const y = store.get("homeScroll", 0); if (y) scrollTo(0, y); }
}
let lastHash = location.hash;
addEventListener("hashchange", () => {
  if (!lastHash.startsWith("#/aktie/") && !lastHash.startsWith("#/termine") && !lastHash.startsWith("#/info")) store.set("homeScroll", scrollY);
  lastHash = location.hash; route();
});

async function refresh() {
  const b = document.getElementById("reload"); b?.classList.add("spin");
  try { await load(true); } catch (e) { console.warn(e); }
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
start();
})();
