/* Aktien-Ampel – Mein Depot: Journal der eigenen Käufe, Verkäufe und Dividenden.
   Jede Person hat ihr eigenes Journal in der Datenbank (Supabase). Niemand sonst kann es lesen,
   auch Pascal nicht. Auf dem Gerät liegt eine Kopie, damit die Seite auch ohne Netz öffnet. */
(() => {
"use strict";
const GRUENDE = ["Kaufzone", "Trigger ausgelöst", "Kontra-Signal", "Nachkauf (Tranche)", "Sparplan", "Übernahme", "Andere"];
const TYP = { kauf: "Kauf", verkauf: "Verkauf", dividende: "Dividende" };
const WAEHRUNGEN = ["CHF", "USD", "EUR", "GBP", "GBp", "JPY", "HKD", "AUD", "CAD", "SEK", "DKK", "NOK", "SGD"];
const A = () => window.AA;
const SB = () => window.SB;
let UI = { form: null, msg: "", konto: "Alle", info: "" };
let D = null, UID = null;

// ---------- Speicher ----------
const leer = () => ({ tx: [], manuell: {}, konten: [], ts: 0 });
const lkey = () => "depot_v2_" + (SB()?.ich()?.id || "gast");
function normal(d) {
  d = { ...leer(), ...(d || {}) };
  d.tx = Array.isArray(d.tx) ? d.tx : []; d.manuell = d.manuell || {}; d.konten = Array.isArray(d.konten) ? d.konten : []; d.merk = d.merk || {}; d.stil = d.stil || {};
  const ks = new Set(d.konten);
  d.tx.forEach(t => { if (t.konto && !ks.has(t.konto)) { d.konten.push(t.konto); ks.add(t.konto); } });
  if (!d.konten.length) d.konten = ["Hauptdepot"];
  // «Hauptdepot» ist nur der Platzhalter für neue Personen. Sobald eigene Konten da sind und es leer ist, fällt es weg.
  if (d.konten.length > 1 && !d.tx.some(t => (t.konto || "Hauptdepot") === "Hauptdepot")) d.konten = d.konten.filter(k => k !== "Hauptdepot");
  return d;
}
function lesen() {
  const id = SB()?.ich()?.id || "gast";
  if (D && UID === id) return D;
  try { D = normal(JSON.parse(localStorage.getItem(lkey()))); } catch { D = normal(null); }
  UID = id; return D;
}
function lokal(d) { try { localStorage.setItem(lkey(), JSON.stringify(d)); } catch {} }
async function schreiben(d) {
  d.ts = Date.now(); D = normal(d); lokal(D);
  try { await SB().journalSpeichern(D); UI.msg = ""; }
  catch { UI.msg = "Nur auf diesem Gerät gespeichert. Die App gleicht ab, sobald du wieder online bist."; }
}
async function laden() {
  if (!SB()?.ich()) return;
  const hier = lesen();
  try {
    const remote = await SB().journalLaden();
    if (remote && (remote.ts || 0) >= (hier.ts || 0)) { D = normal(remote); lokal(D); }
    else if (hier.ts && (!remote || hier.ts > (remote.ts || 0))) await SB().journalSpeichern(hier);
    UI.msg = "";
  } catch { UI.msg = "Keine Verbindung zur Datenbank. Du siehst den Stand auf diesem Gerät."; }
}
// Einträge aus der alten Version (nur auf diesem Gerät gespeichert)
function altDaten() { try { const o = JSON.parse(localStorage.getItem("depot_v1")); return o?.tx?.length ? o : null; } catch { return null; } }

// ---------- Rechnen ----------
const fxTab = () => { const st = A().STATE.strat?.fx || {}; return { ...st, ...(st.GBp && !st.GBP ? { GBP: st.GBp * 100 } : {}), CHF: 1, ...(A().STATE.live?.markt?.fx || {}) }; };
function fxCHF(w) { const t = fxTab(); if (w === "GBp") return t.GBP != null ? t.GBP / 100 : null; return t[w] ?? null; }
function umrechnen(v, von, nach) { if (v == null || von === nach) return v; const a = fxCHF(von), b = fxCHF(nach); return a != null && b ? v * a / b : null; }
function info(ticker, d) {
  const a = A(), enc = encodeURIComponent;
  const s = a.STATE.stocks.find(x => x.ticker === ticker);
  if (s) { const v = a.view(s); return { s, v, name: s.name, w: s.waehrung, kurs: v.kurs, q: v.q, t: v.t, link: "#/aktie/" + enc(ticker) }; }
  const x = a.STATE.scan?.aktien?.[ticker];
  if (x) { const am = a.STATE.alle?.aktien?.[ticker]; return { s: null, v: null, name: x.n || ticker, w: x.w, kurs: am?.kurs ?? x.p, q: am?.q ?? null, t: am?.t ?? null, link: "#/scan/" + enc(ticker) }; }
  const m = d.manuell[ticker] || {};
  return { s: null, v: null, name: m.name || ticker, w: m.waehrung || "USD", kurs: m.kurs ?? null, manuell: true, kursDatum: m.datum || null };
}
const imKonto = (t, k) => !k || k === "Alle" || (t.konto || "Hauptdepot") === k;
function positionen(d, konto) {
  const by = {};
  d.tx.filter(t => imKonto(t, konto)).sort((a, b) => a.datum.localeCompare(b.datum)).forEach(t => {
    const i = info(t.ticker, d);
    const p = by[t.ticker] ||= { ticker: t.ticker, w: t.w || i.w, stueck: 0, kostenW: 0, kostenCHF: 0, realCHF: 0, divCHF: 0, kaeufe: [], konten: new Set() };
    p.konten.add(t.konto || "Hauptdepot");
    const tw = t.w || p.w;
    const fx = t.fx || fxCHF(tw) || 0;
    const kurs = tw === p.w ? t.kurs : umrechnen(t.kurs, tw, p.w);
    if (t.typ === "kauf") {
      p.stueck += t.stueck; p.kostenW += t.stueck * (kurs || 0); p.kostenCHF += t.stueck * t.kurs * fx + (t.gebuehr || 0); p.kaeufe.push(t);
    } else if (t.typ === "verkauf" && p.stueck > 0) {
      const anteil = Math.min(1, t.stueck / p.stueck);
      const kW = p.kostenW * anteil, kC = p.kostenCHF * anteil;
      p.realCHF += t.stueck * t.kurs * fx - (t.gebuehr || 0) - kC;
      p.stueck -= Math.min(t.stueck, p.stueck); p.kostenW -= kW; p.kostenCHF -= kC;
    } else if (t.typ === "dividende") p.divCHF += (t.betrag || 0) * fx;
  });
  return Object.values(by).map(p => {
    const i = info(p.ticker, d), fx = fxCHF(p.w);
    const kurs = umrechnen(i.kurs, i.w, p.w);
    const wertCHF = kurs != null && fx != null ? p.stueck * kurs * fx : null;
    const dd = i.s ? A().divData(i.s, i.v.L) : null;
    return { ...p, ...i, w: p.w, kurs, fx, konten: [...p.konten], einstand: p.stueck ? p.kostenW / p.stueck : null, wertCHF,
      guvCHF: wertCHF != null ? wertCHF - p.kostenCHF : null, guvPct: wertCHF != null && p.kostenCHF ? (wertCHF / p.kostenCHF - 1) * 100 : null,
      divJahrCHF: dd?.zahlt && dd.summe && fxCHF(i.w) ? dd.summe * p.stueck * fxCHF(i.w) : 0 };
  });
}
function check(d, konto) {
  const a = A(), all = positionen(d, konto), offen = all.filter(p => p.stueck > 0.0000001);
  const wert = offen.reduce((s, p) => s + (p.wertCHF || 0), 0);
  const kosten = offen.filter(p => p.wertCHF != null).reduce((s, p) => s + p.kostenCHF, 0);
  const real = all.reduce((s, p) => s + p.realCHF, 0), div = all.reduce((s, p) => s + p.divCHF, 0);
  const divJahr = offen.reduce((s, p) => s + p.divJahrCHF, 0);
  const mitQ = offen.filter(p => p.q != null && p.wertCHF), wq = mitQ.reduce((s, p) => s + p.wertCHF, 0);
  const q = wq ? mitQ.reduce((s, p) => s + p.wertCHF * p.q, 0) / wq : null, t = wq ? mitQ.reduce((s, p) => s + p.wertCHF * p.t, 0) / wq : null;
  const vert = key => { const m = {}; offen.forEach(p => { const k = key(p) || "Andere"; m[k] = (m[k] || 0) + (p.wertCHF || 0); }); return Object.entries(m).sort((x, y) => y[1] - x[1]).map(([k, v]) => [k, wert ? v / wert * 100 : 0]); };
  const hinweise = [];
  const ohneKurs = offen.filter(p => p.wertCHF == null);
  if (ohneKurs.length) hinweise.push(["info", `Für ${ohneKurs.map(p => p.name).join(", ")} fehlt ein Kurs. Diese Positionen fehlen im Gesamtwert. Trage beim nächsten Kauf oder Verkauf den Kurs ein.`]);
  const alt = offen.filter(p => p.manuell && p.kursDatum && (Date.now() - new Date(p.kursDatum + "T12:00:00")) / 864e5 > 14);
  if (alt.length) hinweise.push(["info", `${alt.map(p => p.name).join(", ")}: Kurs von Hand eingetragen und älter als 2 Wochen. Diese Aktien sind nicht in der App, darum aktualisiert sich der Kurs nicht von selbst.`]);
  offen.forEach(p => {
    const anteil = wert ? (p.wertCHF || 0) / wert * 100 : 0;
    if (anteil > 20 && offen.length >= 5) hinweise.push(["warn", `${p.name} macht ${a.nf(anteil, 0)} % aus. Über 20 % in einer Aktie ist ein Klumpenrisiko.`]);
    if (p.q != null && p.q < 45) hinweise.push(["warn", `${p.name}: Qualität nur ${p.q}. Prüfe, ob dein Kaufgrund noch gilt.`]);
    if (p.v && (p.v.status === "abbruch" || p.v.status === "unter_abbruch")) hinweise.push(["bad", `${p.name} liegt unter der Abbruch-Marke. Entscheide nach deiner Regel, nicht nach Gefühl.`]);
    if (p.s && /^\d{4}-\d{2}-\d{2}$/.test(p.s.zahlen || "")) { const n = Math.round((new Date(p.s.zahlen + "T12:00:00") - new Date()) / 864e5); if (n >= 0 && n <= 14) hinweise.push(["info", `${p.name} meldet ${n === 0 ? "heute" : n === 1 ? "morgen" : "in " + n + " Tagen"} Zahlen (${a.fmtDate(p.s.zahlen)}).`]); }
  });
  const usd = vert(p => p.w === "GBp" ? "GBP" : p.w).find(x => x[0] === "USD")?.[1] || 0;
  if (usd > 60) hinweise.push(["info", `${a.nf(usd, 0)} % sind in US-Dollar. Fällt der Dollar gegenüber dem Franken, verlierst du auch bei gleichen Kursen.`]);
  // Nur Käufe, bei denen die App damals die Ampeln mitgespeichert hat (also in der App eingetragen)
  const kaeufe = d.tx.filter(x => x.typ === "kauf" && imKonto(x, konto) && x.grund !== "Übernahme" && x.signal);
  const imSystem = kaeufe.filter(x => x.signal && (["in_zone", "nahe_zone", "trigger"].includes(x.signal.status) || (x.signal.pess ?? 0) >= 60 || x.signal.t >= 60)).length;
  return { offen, wert, kosten, guv: wert - kosten, guvPct: kosten ? (wert / kosten - 1) * 100 : null, real, div, divJahr, q, t, hinweise, kaeufe: kaeufe.length, imSystem,
    region: vert(p => p.s?.region || A().STATE.scan?.aktien?.[p.ticker]?.reg), waehrung: vert(p => p.w === "GBp" ? "GBP" : p.w), stil: vert(p => p.s?.tags?.[0] || d.tx.find(t => t.ticker === p.ticker && t.stil)?.stil) };
}

// ---------- Darstellung ----------
const chf = v => v == null ? "–" : `${A().nf(v, Math.abs(v) >= 1000 ? 0 : 2)} CHF`;
const pctC = v => v == null ? "–" : `<span class="${v > 0 ? "up" : v < 0 ? "down" : ""}">${A().pct(v, 1)}</span>`;
const bars = rows => rows.map(([k, v]) => `<div class="dp-bar"><span>${A().esc(k)}</span><div><i style="width:${v.toFixed(1)}%"></i></div><b>${A().nf(v, 0)} %</b></div>`).join("");
const wName = w => w === "GBp" ? "Pence" : w;

let LISTE = null;
function sucheListe() {
  if (LISTE) return LISTE;
  const a = A(), seen = new Set(), out = [];
  a.STATE.stocks.forEach(s => { seen.add(s.ticker); out.push(`${s.name} (${s.ticker})`); });
  Object.entries(a.STATE.scan?.aktien || {}).forEach(([k, x]) => { if (!seen.has(k) && !x.app) out.push(`${x.n} (${k})`); });
  return (LISTE = out.sort((x, y) => x.localeCompare(y, "de")));
}
function findeTicker(text, d) {
  const a = A(), t = text.trim(); if (!t) return null;
  const m = t.match(/\(([^()]+)\)\s*$/); const sym = (m ? m[1] : t).trim();
  if (a.STATE.stocks.some(s => s.ticker === sym)) return sym;
  const sc = a.STATE.scan?.aktien || {};
  if (sc[sym]) return sc[sym].app || sym;
  const up = sym.toUpperCase(); if (sc[up]) return sc[up].app || up;
  const byName = Object.entries(sc).find(([, x]) => x.n?.toLowerCase() === t.toLowerCase()); if (byName) return byName[1].app || byName[0];
  const st = a.STATE.stocks.find(s => s.name.toLowerCase() === t.toLowerCase()); if (st) return st.ticker;
  if (d.manuell[up]) return up;
  return null;
}

function formHtml(d) {
  const f = UI.form, a = A(), heute = new Date().toISOString().slice(0, 10);
  const e = f.edit ? d.tx.find(x => x.id === f.edit) : null;
  const t = e?.ticker || f.ticker || "";
  const i = t ? info(t, d) : null;
  const w = e?.w || (i ? i.w : "USD");
  const val = (k, def) => a.esc(e?.[k] ?? def ?? "");
  const aktie = t ? `${i.name} (${t})` : "";
  const konto = e?.konto || f.konto || (UI.konto !== "Alle" ? UI.konto : d.konten[0]);
  return `<form class="card dp-form" id="dp-form" novalidate>
    <h3>${e ? "Eintrag ändern" : "Neuer Eintrag"}</h3>
    <div class="seg dp-seg" role="group" aria-label="Art">${Object.entries(TYP).map(([k, l]) => `<button type="button" data-typ="${k}" aria-pressed="${(e?.typ || f.typ || "kauf") === k}">${l}</button>`).join("")}</div>
    <div class="dp-grid">
      <label class="wide">Aktie<input id="dp-aktie" list="dp-liste" value="${a.esc(aktie)}" placeholder="Name oder Kürzel, z. B. Nestlé oder NESN.SW" autocomplete="off" required></label>
      <datalist id="dp-liste"></datalist>
      <p class="wide dp-found" id="dp-found"></p>
      <label>Konto (Bank oder App)<select id="dp-konto">${d.konten.map(k => `<option ${k === konto ? "selected" : ""}>${a.esc(k)}</option>`).join("")}<option value="__neu">Neues Konto …</option></select></label>
      <label>Datum<input id="dp-datum" type="date" value="${val("datum", heute)}" required></label>
      <label class="wide" id="dp-kneu" hidden>Name des neuen Kontos<input id="dp-kname" maxlength="30" placeholder="z. B. Swissquote, PostFinance, Neon, 3a"></label>
      <label class="dp-kauf">Stück<input id="dp-stueck" type="number" inputmode="decimal" step="any" min="0" value="${val("stueck")}"></label>
      <label class="dp-kauf">Kurs pro Stück<input id="dp-kurs" type="number" inputmode="decimal" step="any" min="0" value="${val("kurs", i?.kurs != null && !e ? +(+umrechnen(i.kurs, i.w, w)).toFixed(4) : "")}"></label>
      <label class="dp-div" hidden>Betrag total (nach Steuern)<input id="dp-betrag" type="number" inputmode="decimal" step="any" min="0" value="${val("betrag")}"></label>
      <label>Währung<select id="dp-w">${[...new Set([w, ...WAEHRUNGEN])].map(x => `<option value="${x}" ${x === w ? "selected" : ""}>${wName(x)}</option>`).join("")}</select></label>
      <label>Wechselkurs (CHF pro <span id="dp-wn">${a.esc(w === "GBp" ? "Penny" : w)}</span>)<input id="dp-fx" type="number" inputmode="decimal" step="any" min="0" value="${val("fx", fxCHF(w) != null ? +fxCHF(w).toFixed(5) : "")}"></label>
      <label class="dp-kauf">Gebühren (CHF)<input id="dp-geb" type="number" inputmode="decimal" step="any" min="0" value="${val("gebuehr", 0)}"></label>
      <label class="wide dp-nur-kauf">Warum kaufe ich?<select id="dp-grund">${GRUENDE.map(g => `<option ${e?.grund === g ? "selected" : ""}>${g}</option>`).join("")}</select></label>
      <label class="wide">Notiz für mein Journal<textarea id="dp-notiz" rows="3" placeholder="Zum Beispiel: Erste Tranche (1/3), Kaufzone hält, A/D dreht. Nächste Tranche über dem Trigger.">${val("notiz")}</textarea></label>
    </div>
    <p class="dp-err" id="dp-err" role="alert"></p>
    <div class="dp-actions"><button class="btn primary small" type="submit">${e ? "Änderung speichern" : "Speichern"}</button><button class="btn small" type="button" id="dp-cancel">Abbrechen</button>${e ? '<button class="btn small dp-del" type="button" id="dp-delete">Löschen</button>' : ""}</div>
  </form>`;
}

function render(root) {
  const a = A(), d = lesen(), konto = d.konten.includes(UI.konto) ? UI.konto : "Alle"; UI.konto = konto;
  const c = check(d, konto);
  const posRows = c.offen.sort((x, y) => (y.wertCHF || 0) - (x.wertCHF || 0)).map(p => {
    const anteil = c.wert ? (p.wertCHF || 0) / c.wert * 100 : 0;
    return `<a class="row dp-pos" ${p.link ? `href="${p.link}"` : ""}>
      ${p.q != null ? a.signal(p.q, p.t) : '<span class="signal dp-nosig" aria-hidden="true"></span>'}
      <div class="mid"><div class="nm">${a.esc(p.name)}</div><div class="sub">${a.nf(p.stueck, p.stueck % 1 ? 3 : 0)} Stk. · Einstand ${a.money(p.einstand, p.w)}${konto === "Alle" && d.konten.length > 1 ? " · " + a.esc(p.konten.join(", ")) : ""}</div><div class="sub">${a.nf(anteil, 0)} % vom Depot${p.manuell ? ` · Kurs von Hand${p.kursDatum ? " (" + a.fmtDate(p.kursDatum) + ")" : ""}` : ""}</div></div>
      <div class="right"><div class="px">${chf(p.wertCHF)}</div><div>${pctC(p.guvPct)}</div></div></a>`;
  }).join("");
  const journal = d.tx.filter(t => imKonto(t, konto)).sort((x, y) => y.datum.localeCompare(x.datum) || String(y.id).localeCompare(String(x.id))).slice(0, UI.alle ? 9999 : 40).map(t => {
    const i = info(t.ticker, d), w = t.w || i.w;
    const was = t.typ === "dividende" ? `${a.money(t.betrag, w)} erhalten` : `${a.nf(t.stueck, t.stueck % 1 ? 3 : 0)} × ${a.money(t.kurs, w)}`;
    const sig = t.signal ? `Damals Q ${t.signal.q} · T ${t.signal.t}${t.signal.status ? " · " + ((a.STATUS[t.signal.status] || [t.signal.status])[0]) : ""}` : "";
    return `<button type="button" class="dp-tx dp-${t.typ}" data-edit="${a.esc(t.id)}"><span class="dp-ic" aria-hidden="true">${t.typ === "verkauf" ? "↓" : t.typ === "dividende" ? "+" : "↑"}</span>
      <span class="dp-tx-m"><b>${TYP[t.typ]} ${a.esc(i.name)}</b><span>${a.fmtDate(t.datum)} · ${was}${t.grund && t.typ === "kauf" ? " · " + a.esc(t.grund) : ""}${konto === "Alle" && d.konten.length > 1 ? " · " + a.esc(t.konto || "Hauptdepot") : ""}</span>${sig ? `<em>${a.esc(sig)}</em>` : ""}${t.notiz ? `<i>${a.esc(t.notiz)}</i>` : ""}</span></button>`;
  }).join("");
  const anzahlTx = d.tx.filter(t => imKonto(t, konto)).length;
  const qC = c.q != null ? a.ampel(c.q) : null;
  const alt = altDaten();
  const chips = d.konten.length > 1 ? `<div class="chips dp-chips">${["Alle", ...d.konten].map(k => `<button class="chip" data-konto="${a.esc(k)}" aria-pressed="${k === konto}">${a.esc(k)}</button>`).join("")}</div>` : "";
  root.innerHTML = `<header class="top"><div><h1>Depot</h1><div class="stand">Nur für dich sichtbar</div></div></header>
    ${UI.msg ? `<div class="banner warn">${a.esc(UI.msg)}</div>` : ""}
    ${UI.info ? `<div class="banner ok">${a.esc(UI.info)}</div>` : ""}
    ${alt && !d.tx.length ? `<div class="banner info">Auf diesem Gerät liegen noch ${alt.tx.length} Einträge aus der alten Version. <button class="jump" id="dp-alt">Jetzt übernehmen</button></div>` : ""}
    ${chips}
    ${c.offen.length ? `
    <div class="dp-hero"><div class="dp-total">${a.nf(c.wert, 0)}<span>CHF</span></div>
      <div class="dp-line"><span class="${c.guv >= 0 ? "up" : "down"}">${c.guv >= 0 ? "+" : "−"}${a.nf(Math.abs(c.guv), 0)} CHF (${a.pct(c.guvPct, 1)})</span><span>investiert ${chf(c.kosten)}</span><span>${c.offen.length} Positionen</span></div></div>
    <div class="dp-kpis">
      <div><span>Dividenden pro Jahr</span><b>${chf(c.divJahr)}</b><em>${c.wert && c.divJahr ? a.nf(c.divJahr / c.wert * 100, 1) + " % Rendite" : "nur Aktien aus der App"}</em></div>
      <div><span>Erhalten und realisiert</span><b>${chf(c.div + c.real)}</b><em>Dividenden ${chf(c.div)} · Verkäufe ${chf(c.real)}</em></div>
      <div><span>Qualität im Depot</span><b>${c.q != null ? a.nf(c.q, 0) : "–"} <small class="${qC}-t">${qC ? a.ampelName[qC] : ""}</small></b><em>Timing ${c.t != null ? a.nf(c.t, 0) : "–"}, nach Wert gewichtet</em></div>
      <div><span>Käufe nach System</span><b>${c.kaeufe ? `${c.imSystem} von ${c.kaeufe}` : "–"}</b><em>Kaufzone, Trigger, Kontra oder Timing ab hellgrün</em></div>
    </div>` : `<div class="empty">Noch keine Einträge${konto !== "Alle" ? " in diesem Konto" : ""}. Trage deinen ersten Kauf ein: Die App rechnet danach Wert, Gewinn, Dividenden und die Verteilung selbst aus. Unter «Konto» kannst du «Neues Konto …» wählen und deine Bank oder App eintragen, zum Beispiel Swissquote oder PostFinance. Hast du mehrere, kannst du danach oben nach Konto filtern.</div>`}
    ${UI.form ? formHtml(d) : `<div class="dp-add"><button class="btn primary" id="dp-new">Kauf oder Verkauf</button><button class="btn" id="dp-new-div">Dividende</button></div>`}
    ${c.offen.length ? `
    ${c.hinweise.length ? `<div class="card dp-hints">${c.hinweise.map(([k, t]) => `<p class="dp-h dp-h-${k}">${a.esc(t)}</p>`).join("")}</div>` : ""}
    <div class="sec"><h2>Positionen</h2><p>Kurse vom letzten Update, alles in Franken.</p></div>
    <div class="list">${posRows}</div>
    <div class="two" style="margin-top:12px">
      <div class="card"><b>Regionen</b>${bars(c.region)}</div>
      <div class="card"><b>Währungen</b>${bars(c.waehrung)}</div>
    </div>` : ""}
    ${anzahlTx ? `<div class="sec"><h2>Journal</h2><p>${anzahlTx} Einträge. Tippe auf einen Eintrag, um ihn zu ändern.</p></div><div class="dp-journal">${journal}</div>${anzahlTx > 40 && !UI.alle ? '<button class="btn small" id="dp-mehr" style="margin-top:8px">Alle Einträge zeigen</button>' : ""}` : ""}
    <div class="sec"><h2>Sichern und bewerten lassen</h2></div>
    <div class="card prose">
      <p><b>Von Claude bewerten lassen:</b> «Bericht kopieren» und im Chat einfügen. Er enthält Positionen, Kaufgründe und den Depot-Check.</p>
      <div class="dp-actions"><button class="btn small" id="dp-report">Bericht kopieren</button><button class="btn small" id="dp-export">Sicherung herunterladen</button><label class="btn small dp-file">Datei einlesen<input type="file" id="dp-file" accept=".json,application/json" hidden></label></div>
      <textarea id="dp-area" rows="5" hidden aria-label="Depot-Daten"></textarea>
      <p id="dp-copy-state" class="dp-note" role="status"></p>
    </div>
    <p class="dp-note">Persönliches Journal, keine Anlageberatung.</p>`;
  bind(root, d);
}

function bericht(d) {
  const a = A(), c = check(d, UI.konto);
  const L = [`Mein Depot${UI.konto !== "Alle" ? " (" + UI.konto + ")" : ""}, Stand ${new Date().toLocaleDateString("de-CH")}, Kurse vom letzten Update`,
    `Wert ${chf(c.wert)}, investiert ${chf(c.kosten)}, Gewinn/Verlust ${c.guvPct != null ? a.nf(c.guvPct, 1) + " %" : "–"}, realisiert ${chf(c.real)}, Dividenden erhalten ${chf(c.div)}, pro Jahr ${chf(c.divJahr)}`,
    `Qualität gewichtet ${c.q != null ? a.nf(c.q, 0) : "–"}, Timing gewichtet ${c.t != null ? a.nf(c.t, 0) : "–"}, Käufe nach System: ${c.imSystem} von ${c.kaeufe}`,
    `Regionen: ${c.region.map(([k, v]) => `${k} ${a.nf(v, 0)} %`).join(", ")} | Währungen: ${c.waehrung.map(([k, v]) => `${k} ${a.nf(v, 0)} %`).join(", ")}`, "", "Positionen:"];
  c.offen.forEach(p => L.push(`- ${p.name} (${p.ticker}, ${p.konten.join("/")}): ${a.nf(p.stueck, 3)} Stück, Einstand ${a.money(p.einstand, p.w)}, Kurs ${a.money(p.kurs, p.w)}, Wert ${chf(p.wertCHF)}, ${p.guvPct != null ? a.nf(p.guvPct, 1) + " %" : ""}${p.q != null ? `, Q ${p.q}, T ${p.t}` : ""}${p.v?.status ? ", " + p.v.status : ""}`));
  L.push("", "Journal:");
  d.tx.filter(t => imKonto(t, UI.konto)).sort((x, y) => x.datum.localeCompare(y.datum)).forEach(t => L.push(`- ${t.datum} ${TYP[t.typ]} ${info(t.ticker, d).name} [${t.konto || "Hauptdepot"}]: ${t.typ === "dividende" ? t.betrag : `${t.stueck} × ${t.kurs}`} ${t.w || ""}${t.grund && t.typ === "kauf" ? `, Grund: ${t.grund}` : ""}${t.signal ? `, damals Q ${t.signal.q} T ${t.signal.t} ${t.signal.status || ""}` : ""}${t.notiz ? `, Notiz: ${t.notiz}` : ""}`));
  if (c.hinweise.length) { L.push("", "Hinweise der App:"); c.hinweise.forEach(h => L.push("- " + h[1])); }
  L.push("", "Bitte bewerte mein Depot nach unserem Schema.");
  return L.join("\n");
}

async function kopieren(text, el) {
  try { await navigator.clipboard.writeText(text); el.textContent = "Kopiert. Jetzt im Chat einfügen."; }
  catch { const ta = document.getElementById("dp-area"); ta.hidden = false; ta.value = text; ta.focus(); ta.select(); el.textContent = "Text markiert: jetzt kopieren."; }
}
function zusammenfuehren(d, neu) {
  const ids = new Set(d.tx.map(t => t.id));
  const tx = (neu.tx || []).filter(t => t && t.datum && t.ticker && TYP[t.typ] && !ids.has(t.id));
  d.tx = d.tx.concat(tx.map(t => ({ ...t, id: t.id || (Date.now().toString(36) + Math.random().toString(36).slice(2, 6)) })));
  d.manuell = { ...(neu.manuell || {}), ...d.manuell };
  d.konten = [...new Set([...(d.konten || []).filter(k => k !== "Hauptdepot" || d.tx.some(t => (t.konto || "Hauptdepot") === "Hauptdepot")), ...(neu.konten || [])])];
  return tx.length;
}

function bind(root, d) {
  const a = A(), $ = id => document.getElementById(id), rerender = () => render(root);
  root.querySelectorAll("[data-konto]").forEach(b => b.onclick = () => { UI.konto = b.dataset.konto; UI.info = ""; rerender(); });
  $("dp-new") && ($("dp-new").onclick = () => { UI.form = { typ: "kauf" }; UI.info = ""; rerender(); $("dp-aktie")?.focus(); });
  $("dp-new-div") && ($("dp-new-div").onclick = () => { UI.form = { typ: "dividende" }; UI.info = ""; rerender(); $("dp-aktie")?.focus(); });
  $("dp-mehr") && ($("dp-mehr").onclick = () => { UI.alle = true; rerender(); });
  $("dp-alt") && ($("dp-alt").onclick = async () => { const n = zusammenfuehren(d, altDaten()); await schreiben(d); try { localStorage.removeItem("depot_v1"); } catch {} UI.info = `${n} Einträge übernommen.`; rerender(); });
  root.querySelectorAll("[data-edit]").forEach(b => b.onclick = () => { const t = d.tx.find(x => x.id === b.dataset.edit); UI.form = { edit: t.id, ticker: t.ticker, typ: t.typ }; rerender(); $("dp-form")?.scrollIntoView({ block: "start" }); });
  const f = $("dp-form");
  if (f) {
    let typ = UI.form.edit ? d.tx.find(x => x.id === UI.form.edit).typ : UI.form.typ || "kauf";
    const dl = $("dp-liste"); setTimeout(() => { dl.innerHTML = sucheListe().map(x => `<option value="${a.esc(x)}"></option>`).join(""); }, 0);
    const sichtbar = () => {
      f.querySelectorAll("[data-typ]").forEach(b => b.setAttribute("aria-pressed", b.dataset.typ === typ));
      f.querySelectorAll(".dp-kauf").forEach(x => x.hidden = typ === "dividende");
      f.querySelectorAll(".dp-div").forEach(x => x.hidden = typ !== "dividende");
      f.querySelectorAll(".dp-nur-kauf").forEach(x => x.hidden = typ !== "kauf");
      $("dp-kneu").hidden = $("dp-konto").value !== "__neu";
    };
    const gefunden = () => {
      const tk = findeTicker($("dp-aktie").value, d), el = $("dp-found");
      if (!$("dp-aktie").value.trim()) { el.textContent = ""; return null; }
      if (tk) {
        const i = info(tk, d);
        el.innerHTML = `${a.esc(i.name)} · ${a.esc(tk)}${i.q != null ? ` · Qualität ${i.q}, Timing ${i.t}` : ""}${i.manuell ? " · nicht in der App, Kurs von Hand" : ""}`;
        if (!UI.form.edit && $("dp-w").dataset.touched !== "1" && i.w) { $("dp-w").value = i.w; wWechsel(); }
        if (!UI.form.edit && !$("dp-kurs").value && i.kurs != null) $("dp-kurs").value = +(+umrechnen(i.kurs, i.w, $("dp-w").value)).toFixed(4);
      } else el.textContent = "Nicht in der Liste. Die App speichert die Aktie so, wie du sie schreibst, den Kurs musst du selbst eintragen.";
      return tk;
    };
    const wWechsel = () => { const w = $("dp-w").value; $("dp-wn").textContent = w === "GBp" ? "Penny" : w; const fx = fxCHF(w); if (fx != null) $("dp-fx").value = +fx.toFixed(5); };
    sichtbar(); if ($("dp-aktie").value) gefunden();
    f.querySelectorAll("[data-typ]").forEach(b => b.onclick = () => { typ = b.dataset.typ; sichtbar(); });
    $("dp-konto").onchange = sichtbar;
    $("dp-aktie").onchange = gefunden;
    $("dp-w").onchange = () => { $("dp-w").dataset.touched = "1"; wWechsel(); };
    $("dp-cancel").onclick = () => { UI.form = null; rerender(); };
    if ($("dp-delete")) $("dp-delete").onclick = async () => {
      if ($("dp-delete").dataset.sure !== "1") { $("dp-delete").dataset.sure = "1"; $("dp-delete").textContent = "Wirklich löschen?"; return; }
      d.tx = d.tx.filter(x => x.id !== UI.form.edit); UI.form = null; await schreiben(d); rerender();
    };
    f.onsubmit = async e => {
      e.preventDefault();
      const num = id => { const v = parseFloat(String($(id).value).replace(",", ".")); return isNaN(v) ? null : v; };
      const err = m => { $("dp-err").textContent = m; };
      const roh = $("dp-aktie").value.trim(); if (!roh) return err("Bitte die Aktie eintragen.");
      let ticker = findeTicker(roh, d);
      const w = $("dp-w").value;
      if (!ticker) {
        ticker = (roh.match(/\(([^)]+)\)\s*$/)?.[1] || roh).toUpperCase().replace(/\s+/g, "").slice(0, 20);
        d.manuell[ticker] = { ...(d.manuell[ticker] || {}), name: roh.replace(/\s*\([^)]*\)\s*$/, "") || roh, waehrung: w };
      }
      let konto = $("dp-konto").value;
      if (konto === "__neu") { konto = $("dp-kname").value.trim(); if (!konto) return err("Bitte dem neuen Konto einen Namen geben."); if (!d.konten.includes(konto)) d.konten.push(konto); }
      const datum = $("dp-datum").value; if (!datum) return err("Bitte ein Datum wählen.");
      const tx = { id: UI.form.edit || (Date.now().toString(36) + Math.random().toString(36).slice(2, 6)), datum, ticker, typ, konto, w, fx: num("dp-fx"), notiz: $("dp-notiz").value.trim() };
      if (typ === "dividende") { tx.betrag = num("dp-betrag"); if (!tx.betrag) return err("Bitte den erhaltenen Betrag eintragen."); }
      else {
        tx.stueck = num("dp-stueck"); tx.kurs = num("dp-kurs"); tx.gebuehr = num("dp-geb") || 0;
        if (!tx.stueck || !tx.kurs) return err("Bitte Stückzahl und Kurs eintragen.");
        if (typ === "verkauf") { const p = positionen({ ...d, tx: d.tx.filter(x => x.id !== tx.id) }, konto).find(x => x.ticker === ticker); if (!p || p.stueck + 1e-9 < tx.stueck) return err("Du kannst nicht mehr verkaufen, als du in diesem Konto besitzt."); }
        if (typ === "kauf") tx.grund = $("dp-grund").value;
        const m = d.manuell[ticker]; if (m && (!m.datum || datum >= m.datum)) { m.kurs = umrechnen(tx.kurs, w, m.waehrung || w); m.datum = datum; }
      }
      const alt = UI.form.edit ? d.tx.find(x => x.id === UI.form.edit) : null;
      const i = info(ticker, d);
      tx.signal = alt?.signal || (i.q != null ? { q: i.q, t: i.t, status: i.v?.status || null, pess: i.v?.L?.pessimismus?.wert ?? null, kurs: i.kurs } : null);
      d.tx = d.tx.filter(x => x.id !== tx.id).concat(tx);
      UI.form = null; UI.info = "Gespeichert."; await schreiben(d); rerender(); scrollTo(0, 0);
    };
  }
  $("dp-report").onclick = () => kopieren(bericht(lesen()), $("dp-copy-state"));
  $("dp-export").onclick = () => {
    const blob = new Blob([JSON.stringify(lesen(), null, 1)], { type: "application/json" });
    const url = URL.createObjectURL(blob), l = document.createElement("a");
    l.href = url; l.download = `depot-${new Date().toISOString().slice(0, 10)}.json`; document.body.appendChild(l); l.click(); l.remove();
    setTimeout(() => URL.revokeObjectURL(url), 2000); $("dp-copy-state").textContent = "Sicherung heruntergeladen.";
  };
  $("dp-file").onchange = async ev => {
    const st = $("dp-copy-state"), file = ev.target.files?.[0]; if (!file) return;
    try {
      const obj = JSON.parse(await file.text()); if (!Array.isArray(obj.tx)) throw 0;
      const n = zusammenfuehren(d, obj); await schreiben(d);
      UI.info = n ? `${n} Einträge eingelesen.` : "Alle Einträge aus der Datei waren schon da."; rerender();
    } catch { st.textContent = "Das ist keine gültige Depot-Datei."; }
  };
}

// ---------- Schnittstelle zur App ----------
window.Depot = {
  async render(root, ticker) {
    root.innerHTML = `<header class="top"><div><h1>Depot</h1><div class="stand">Lade …</div></div></header>`;
    await Promise.all([laden(), A().ensureScan().catch(() => {})]);
    LISTE = null;
    if (ticker) UI.form = { typ: "kauf", ticker };
    render(root); if (!ticker) scrollTo(0, 0); else document.getElementById("dp-form")?.scrollIntoView({ block: "start" });
  },
  laden,
  bestand(ticker) { try { const p = positionen(lesen()).find(x => x.ticker === ticker && x.stueck > 0); return p || null; } catch { return null; } },
  vergessen() { D = null; UID = null; },
  // Merkliste und eigene Stil-Einordnung: gehören zur Person, liegen mit im privaten Journal
  merk(key) { return lesen().merk[key]?.s || null; },
  merkListe() { return Object.entries(lesen().merk).map(([key, v]) => ({ key, ...v })).sort((a, b) => (a.s === "eng" ? 0 : 1) - (b.s === "eng" ? 0 : 1) || b.ts - a.ts); },
  async setMerk(key, s) { const d = lesen(); if (s) d.merk[key] = { s, ts: Date.now() }; else delete d.merk[key]; await schreiben(d); },
  stil(key) { return lesen().stil[key] || null; },
  async setStil(key, arr) { const d = lesen(); if (arr) d.stil[key] = arr; else delete d.stil[key]; await schreiben(d); }
};
})();
