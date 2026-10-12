/* Aktien-Ampel – Mein Depot: Journal der eigenen Käufe, Positionen und Depot-Check.
   Die Daten bleiben auf dem Gerät. Auf Wunsch werden sie verschlüsselt (AES-GCM, eigenes Passwort)
   im GitHub-Repository gespeichert, damit iPhone und PC denselben Stand haben. */
(() => {
"use strict";
const KEY = "depot_v1", PW = "depot_pw", FILE = "data/depot.enc.json";
const GRUENDE = ["Kaufzone", "Trigger ausgelöst", "Kontra-Signal", "Nachkauf (Tranche)", "Sparplan", "Andere"];
const TYP = { kauf: "Kauf", verkauf: "Verkauf", dividende: "Dividende" };
const A = () => window.AA;
let UI = { form: null, msg: "" };

// ---------- Speicher ----------
const leer = () => ({ tx: [], manuell: {}, ts: 0 });
function lesen() { try { return JSON.parse(localStorage.getItem(KEY)) || leer(); } catch { return leer(); } }
function schreiben(d) { d.ts = Date.now(); try { localStorage.setItem(KEY, JSON.stringify(d)); } catch {} sync(d).catch(e => { UI.msg = "Nur auf diesem Gerät gespeichert: " + e.message; }); }
const pw = () => { try { return localStorage.getItem(PW) || ""; } catch { return ""; } };

// ---------- Verschlüsselung ----------
const enc = new TextEncoder(), dec = new TextDecoder();
const b64e = buf => btoa(String.fromCharCode(...new Uint8Array(buf)));
const b64d = s => Uint8Array.from(atob(s), c => c.charCodeAt(0));
async function schluessel(pass, salt) {
  const base = await crypto.subtle.importKey("raw", enc.encode(pass), "PBKDF2", false, ["deriveKey"]);
  return crypto.subtle.deriveKey({ name: "PBKDF2", salt, iterations: 200000, hash: "SHA-256" }, base, { name: "AES-GCM", length: 256 }, false, ["encrypt", "decrypt"]);
}
async function verschluesseln(obj, pass) {
  const salt = crypto.getRandomValues(new Uint8Array(16)), iv = crypto.getRandomValues(new Uint8Array(12));
  const k = await schluessel(pass, salt);
  const data = await crypto.subtle.encrypt({ name: "AES-GCM", iv }, k, enc.encode(JSON.stringify(obj)));
  return { v: 1, salt: b64e(salt), iv: b64e(iv), data: b64e(data) };
}
async function entschluesseln(box, pass) {
  const k = await schluessel(pass, b64d(box.salt));
  const plain = await crypto.subtle.decrypt({ name: "AES-GCM", iv: b64d(box.iv) }, k, b64d(box.data));
  return JSON.parse(dec.decode(plain));
}

// ---------- GitHub (nur verschlüsselt) ----------
async function ghDatei() {
  const r = await fetch(`https://api.github.com/repos/${A().REPO}/contents/${FILE}?t=${Date.now()}`, { headers: { Authorization: "Bearer " + A().token(), Accept: "application/vnd.github+json" }, cache: "no-store" });
  if (r.status === 404) return { sha: null, box: null };
  if (!r.ok) throw new Error("GitHub " + r.status);
  const j = await r.json();
  return { sha: j.sha, box: JSON.parse(A().unb64(j.content)) };
}
async function sync(d) {
  if (!A().token() || !pw()) return "lokal";
  const cur = await ghDatei();
  const box = await verschluesseln(d, pw());
  const body = { message: "Depot (verschlüsselt)", content: A().b64(JSON.stringify(box)), ...(cur.sha ? { sha: cur.sha } : {}) };
  const r = await fetch(`https://api.github.com/repos/${A().REPO}/contents/${FILE}`, { method: "PUT", headers: { Authorization: "Bearer " + A().token(), Accept: "application/vnd.github+json", "Content-Type": "application/json" }, body: JSON.stringify(body) });
  if (!r.ok) throw new Error("GitHub " + r.status);
  return "github";
}
async function laden() {
  if (!A().token() || !pw()) return;
  try {
    const { box } = await ghDatei();
    if (!box) return;
    const remote = await entschluesseln(box, pw());
    if ((remote.ts || 0) > (lesen().ts || 0)) { try { localStorage.setItem(KEY, JSON.stringify(remote)); } catch {} }
  } catch (e) { UI.msg = e.name === "OperationError" ? "Das Passwort passt nicht zur gespeicherten Depot-Datei." : "Depot konnte nicht von GitHub geladen werden."; }
}

// ---------- Rechnen ----------
const fxTab = () => ({ CHF: 1, ...(A().STATE.live?.markt?.fx || {}) });
function fxCHF(w) { const t = fxTab(); if (w === "GBp") return (t.GBP || 0) / 100; return t[w] ?? null; }
function info(ticker, d) {
  const s = A().STATE.stocks.find(x => x.ticker === ticker);
  if (s) { const v = A().view(s); return { s, v, name: s.name, w: s.waehrung, kurs: v.kurs }; }
  const m = d.manuell[ticker] || {};
  return { s: null, v: null, name: m.name || ticker, w: m.waehrung || "USD", kurs: m.kurs ?? null };
}
function positionen(d) {
  const by = {};
  [...d.tx].sort((a, b) => a.datum.localeCompare(b.datum)).forEach(t => {
    const p = by[t.ticker] ||= { ticker: t.ticker, stueck: 0, kostenW: 0, kostenCHF: 0, realCHF: 0, divCHF: 0, kaeufe: [] };
    const fx = t.fx || fxCHF(info(t.ticker, d).w) || 0;
    if (t.typ === "kauf") {
      p.stueck += t.stueck; p.kostenW += t.stueck * t.kurs; p.kostenCHF += t.stueck * t.kurs * fx + (t.gebuehr || 0); p.kaeufe.push(t);
    } else if (t.typ === "verkauf" && p.stueck > 0) {
      const anteil = Math.min(1, t.stueck / p.stueck);
      const kW = p.kostenW * anteil, kC = p.kostenCHF * anteil;
      p.realCHF += t.stueck * t.kurs * fx - (t.gebuehr || 0) - kC;
      p.stueck -= Math.min(t.stueck, p.stueck); p.kostenW -= kW; p.kostenCHF -= kC;
    } else if (t.typ === "dividende") p.divCHF += (t.betrag || 0) * fx;
  });
  return Object.values(by).map(p => {
    const i = info(p.ticker, d), fx = fxCHF(i.w);
    const wertCHF = i.kurs != null && fx != null ? p.stueck * i.kurs * fx : null;
    const dd = i.s ? A().divData(i.s, i.v.L) : null;
    return { ...p, ...i, fx, einstand: p.stueck ? p.kostenW / p.stueck : null, wertCHF,
      guvCHF: wertCHF != null ? wertCHF - p.kostenCHF : null, guvPct: wertCHF != null && p.kostenCHF ? (wertCHF / p.kostenCHF - 1) * 100 : null,
      divJahrCHF: dd?.zahlt && dd.summe && fx ? dd.summe * p.stueck * fx : 0 };
  });
}
function check(d) {
  const all = positionen(d), offen = all.filter(p => p.stueck > 0.0000001);
  const wert = offen.reduce((a, p) => a + (p.wertCHF || 0), 0);
  const kosten = offen.reduce((a, p) => a + p.kostenCHF, 0);
  const real = all.reduce((a, p) => a + p.realCHF, 0), div = all.reduce((a, p) => a + p.divCHF, 0);
  const divJahr = offen.reduce((a, p) => a + p.divJahrCHF, 0);
  const gew = f => wert ? offen.reduce((a, p) => a + (p.wertCHF || 0) * f(p), 0) / wert : null;
  const q = gew(p => p.v?.q ?? 0), t = gew(p => p.v?.t ?? 0);
  const vert = key => { const m = {}; offen.forEach(p => { const k = key(p) || "Andere"; m[k] = (m[k] || 0) + (p.wertCHF || 0); }); return Object.entries(m).sort((a, b) => b[1] - a[1]).map(([k, v]) => [k, wert ? v / wert * 100 : 0]); };
  const hinweise = [];
  if (offen.some(p => p.fx == null)) hinweise.push(["info", "Einige Wechselkurse fehlen noch. Sie kommen mit dem nächsten automatischen Update, bis dahin fehlen diese Positionen im Gesamtwert."]);
  offen.forEach(p => {
    const anteil = wert ? (p.wertCHF || 0) / wert * 100 : 0;
    if (anteil > 20 && offen.length >= 5) hinweise.push(["warn", `${p.name} macht ${A().nf(anteil, 0)} % deines Depots aus. Über 20 % in einer Aktie ist ein Klumpenrisiko.`]);
    if (p.v && p.v.q < 45) hinweise.push(["warn", `${p.name}: Qualität nur ${p.v.q}. Prüfe, ob dein Kaufgrund noch gilt.`]);
    if (p.v && (p.v.status === "abbruch" || p.v.status === "unter_abbruch")) hinweise.push(["bad", `${p.name} liegt unter der Abbruch-Marke. Entscheide nach deiner Regel, nicht nach Gefühl.`]);
    if (p.s && /^\d{4}-\d{2}-\d{2}$/.test(p.s.zahlen || "")) { const n = Math.round((new Date(p.s.zahlen + "T12:00:00") - new Date()) / 864e5); if (n >= 0 && n <= 14) hinweise.push(["info", `${p.name} meldet in ${n} Tagen Zahlen (${A().fmtDate(p.s.zahlen)}).`]); }
  });
  const usd = vert(p => p.w === "GBp" ? "GBP" : p.w).find(x => x[0] === "USD")?.[1] || 0;
  if (usd > 60) hinweise.push(["info", `${A().nf(usd, 0)} % deines Depots sind in US-Dollar. Fällt der Dollar gegenüber dem Franken, verlierst du auch bei gleichen Kursen.`]);
  if (offen.length && offen.length < 5) hinweise.push(["info", `Erst ${offen.length} ${offen.length === 1 ? "Aktie" : "Aktien"} im Depot. Als Ergänzung zu deinen ETFs ist das in Ordnung, einzelne Ausreisser wirken aber stark.`]);
  const kaeufe = d.tx.filter(x => x.typ === "kauf");
  const imSystem = kaeufe.filter(x => x.signal && (["in_zone", "nahe_zone", "trigger"].includes(x.signal.status) || (x.signal.pess ?? 0) >= 60 || x.signal.t >= 60)).length;
  return { offen, wert, kosten, guv: wert - kosten, guvPct: kosten ? (wert / kosten - 1) * 100 : null, real, div, divJahr, q, t, hinweise, kaeufe: kaeufe.length, imSystem,
    region: vert(p => p.s?.region), waehrung: vert(p => p.w === "GBp" ? "GBP" : p.w), stil: vert(p => p.s?.tags?.[0]) };
}

// ---------- Darstellung ----------
const chf = v => v == null ? "–" : `${A().nf(v, Math.abs(v) >= 1000 ? 0 : 2)} CHF`;
const pctC = v => v == null ? "–" : `<span class="${v > 0 ? "up" : v < 0 ? "down" : ""}">${A().pct(v, 1)}</span>`;
const bars = rows => rows.map(([k, v]) => `<div class="dp-bar"><span>${A().esc(k)}</span><div><i style="width:${v.toFixed(1)}%"></i></div><b>${A().nf(v, 0)} %</b></div>`).join("");

function formHtml(d) {
  const f = UI.form, a = A(), heute = new Date().toISOString().slice(0, 10);
  const t = f.ticker || a.STATE.stocks[0]?.ticker;
  const i = info(t, d);
  const opts = a.STATE.stocks.slice().sort((x, y) => x.name.localeCompare(y.name, "de")).map(s => `<option value="${a.esc(s.ticker)}" ${s.ticker === t ? "selected" : ""}>${a.esc(s.name)} (${a.esc(s.ticker)})</option>`).join("");
  const e = f.edit ? d.tx.find(x => x.id === f.edit) : null;
  const val = (k, def) => a.esc(e?.[k] ?? def ?? "");
  return `<form class="card dp-form" id="dp-form" novalidate>
    <h3>${e ? "Eintrag ändern" : "Neuer Eintrag"}</h3>
    <div class="dp-grid">
      <label>Art<select id="dp-typ">${Object.entries(TYP).map(([k, l]) => `<option value="${k}" ${(e?.typ || f.typ || "kauf") === k ? "selected" : ""}>${l}</option>`).join("")}</select></label>
      <label>Datum<input id="dp-datum" type="date" value="${val("datum", heute)}" required></label>
      <label class="wide">Aktie<select id="dp-ticker">${opts}<option value="__andere" ${t === "__andere" ? "selected" : ""}>Andere Aktie oder ETF …</option></select></label>
      <label class="wide" id="dp-andere" hidden>Name und Kürzel der anderen Aktie<input id="dp-aname" placeholder="z. B. iShares Core S&P 500 (CSSPX)"></label>
      <label class="dp-kauf">Stück<input id="dp-stueck" type="number" inputmode="decimal" step="any" min="0" value="${val("stueck")}"></label>
      <label class="dp-kauf">Kurs pro Stück (${a.esc(i.w === "GBp" ? "Pence" : i.w)})<input id="dp-kurs" type="number" inputmode="decimal" step="any" min="0" value="${val("kurs", i.kurs != null ? +(+i.kurs).toFixed(2) : "")}"></label>
      <label class="dp-div" hidden>Betrag total (${a.esc(i.w === "GBp" ? "Pence" : i.w)}, nach Steuern)<input id="dp-betrag" type="number" inputmode="decimal" step="any" min="0" value="${val("betrag")}"></label>
      <label>Wechselkurs (CHF pro ${a.esc(i.w === "GBp" ? "Penny" : i.w)})<input id="dp-fx" type="number" inputmode="decimal" step="any" min="0" value="${val("fx", fxCHF(i.w) != null ? +fxCHF(i.w).toFixed(5) : "")}"></label>
      <label class="dp-kauf">Gebühren (CHF)<input id="dp-geb" type="number" inputmode="decimal" step="any" min="0" value="${val("gebuehr", 0)}"></label>
      <label class="wide dp-nur-kauf">Warum kaufe ich?<select id="dp-grund">${GRUENDE.map(g => `<option ${e?.grund === g ? "selected" : ""}>${g}</option>`).join("")}</select></label>
      <label class="wide">Notiz für mein Journal<textarea id="dp-notiz" rows="3" placeholder="Zum Beispiel: Erste Tranche (1/3), Kaufzone hält, A/D dreht. Nächste Tranche über dem Trigger.">${val("notiz")}</textarea></label>
    </div>
    ${t !== "__andere" && i.v ? `<p class="dp-snap">Wird mitgespeichert: Qualität ${i.v.q}, Timing ${i.v.t}${i.v.status ? ", " + a.esc((a.STATUS[i.v.status] || [i.v.status])[0]) : ""}${i.v.L?.pessimismus ? `, Pessimismus ${i.v.L.pessimismus.wert}` : ""}. So siehst du später, ob du nach deinem System gekauft hast.</p>` : ""}
    <p class="dp-err" id="dp-err" role="alert"></p>
    <div class="dp-actions"><button class="btn primary small" type="submit">${e ? "Änderung speichern" : "Eintragen"}</button><button class="btn small" type="button" id="dp-cancel">Abbrechen</button>${e ? '<button class="btn small dp-del" type="button" id="dp-delete">Löschen</button>' : ""}</div>
  </form>`;
}

function render(root) {
  const a = A(), d = lesen(), c = check(d);
  const posRows = c.offen.sort((x, y) => (y.wertCHF || 0) - (x.wertCHF || 0)).map(p => {
    const anteil = c.wert ? (p.wertCHF || 0) / c.wert * 100 : 0;
    return `<a class="row dp-pos" ${p.s ? `href="#/aktie/${encodeURIComponent(p.ticker)}"` : ""}>
      ${p.v ? a.signal(p.v.q, p.v.t) : '<span class="signal"></span>'}
      <div class="mid"><div class="nm">${a.esc(p.name)}</div><div class="sub">${a.nf(p.stueck, p.stueck % 1 ? 3 : 0)} Stück · Einstand ${a.money(p.einstand, p.w)} · ${a.nf(anteil, 0)} % vom Depot</div></div>
      <div class="right"><div class="px">${chf(p.wertCHF)}</div><div>${pctC(p.guvPct)}</div></div></a>`;
  }).join("");
  const journal = [...d.tx].sort((x, y) => y.datum.localeCompare(x.datum)).map(t => {
    const i = info(t.ticker, d);
    const was = t.typ === "dividende" ? `${a.money(t.betrag, i.w)} erhalten` : `${a.nf(t.stueck, t.stueck % 1 ? 3 : 0)} × ${a.money(t.kurs, i.w)}`;
    const sig = t.signal ? `Q ${t.signal.q} · T ${t.signal.t}${t.signal.status ? " · " + ((a.STATUS[t.signal.status] || [t.signal.status])[0]) : ""}` : "";
    return `<button type="button" class="dp-tx" data-edit="${a.esc(t.id)}"><span class="dp-tx-d">${a.fmtDate(t.datum)}</span>
      <span class="dp-tx-m"><b>${TYP[t.typ]} ${a.esc(i.name)}</b><span>${was}${t.grund && t.typ === "kauf" ? " · " + a.esc(t.grund) : ""}</span>${sig ? `<em>${a.esc(sig)}</em>` : ""}${t.notiz ? `<i>${a.esc(t.notiz)}</i>` : ""}</span></button>`;
  }).join("");
  const qC = c.q != null ? a.ampel(c.q) : null;
  const leerTxt = `<div class="empty">Noch keine Einträge. Trage deinen ersten Kauf ein: Die App rechnet danach Wert, Gewinn, Dividenden und die Verteilung deines Depots selbst aus.</div>`;
  root.innerHTML = `<header class="top"><div><h1>Mein Depot</h1><div class="stand">Dein Journal: Käufe, Verkäufe und Dividenden</div></div></header>
    ${UI.msg ? `<div class="banner warn">${a.esc(UI.msg)}</div>` : ""}
    ${UI.form ? formHtml(d) : `<div class="actions"><button class="btn primary" id="dp-new">Kauf eintragen</button><button class="btn" id="dp-new-div">Dividende eintragen</button></div>`}
    ${c.offen.length ? `
    <div class="sec"><h2>Depot-Check</h2><p>Automatisch berechnet, Kurse vom letzten Update, alles in Franken.</p></div>
    <div class="dp-kpis">
      <div><span>Wert heute</span><b>${chf(c.wert)}</b><em>investiert ${chf(c.kosten)}</em></div>
      <div><span>Gewinn / Verlust</span><b class="${c.guv >= 0 ? "up" : "down"}">${c.guv >= 0 ? "+" : "−"}${chf(Math.abs(c.guv))}</b><em>${pctC(c.guvPct)}${c.real ? ` · realisiert ${chf(c.real)}` : ""}</em></div>
      <div><span>Dividenden pro Jahr</span><b>${chf(c.divJahr)}</b><em>${c.wert ? a.nf(c.divJahr / c.wert * 100, 1) + " % Rendite" : ""}${c.div ? ` · erhalten ${chf(c.div)}` : ""}</em></div>
      <div><span>Qualität im Depot</span><b>${c.q != null ? a.nf(c.q, 0) : "–"} <small class="${qC}-t">${qC ? a.ampelName[qC] : ""}</small></b><em>Timing ${c.t != null ? a.nf(c.t, 0) : "–"}, nach Wert gewichtet</em></div>
    </div>
    ${c.kaeufe ? `<div class="banner ${c.imSystem / c.kaeufe >= 0.7 ? "ok" : "info"}"><b>Kauf-Disziplin:</b> ${c.imSystem} von ${c.kaeufe} Käufen waren nach deinem System (Kaufzone, Trigger, Kontra-Signal oder Timing ab hellgrün).</div>` : ""}
    ${c.hinweise.length ? `<div class="card dp-hints">${c.hinweise.map(([k, t]) => `<p class="dp-h dp-h-${k}">${a.esc(t)}</p>`).join("")}</div>` : ""}
    <div class="two">
      <div class="card"><b>Regionen</b>${bars(c.region)}</div>
      <div class="card"><b>Währungen</b>${bars(c.waehrung)}</div>
    </div>
    <div class="card" style="margin-top:10px"><b>Stil</b>${bars(c.stil)}</div>
    <div class="sec"><h2>Positionen</h2></div>
    <div class="list">${posRows}</div>` : leerTxt}
    ${d.tx.length ? `<div class="sec"><h2>Journal</h2><p>Tippe auf einen Eintrag, um ihn zu ändern.</p></div><div class="dp-journal">${journal}</div>` : ""}
    <div class="sec"><h2>Speichern und Bewerten lassen</h2></div>
    <div class="card prose">
      <p>Deine Einträge sind auf diesem Gerät gespeichert. Für iPhone und PC zusammen: unten ein eigenes Depot-Passwort festlegen (der GitHub-Schlüssel unter «So funktioniert's» muss eingetragen sein). Dein Depot wird dann <b>verschlüsselt</b> gespeichert. Ohne Passwort kann es niemand lesen, auch nicht im öffentlichen Repository. Vergisst du das Passwort, sind die gespeicherten Daten verloren.</p>
      <div class="tokenrow"><input id="dp-pw" type="password" autocomplete="new-password" placeholder="${pw() ? "Depot-Passwort ist gespeichert" : "Depot-Passwort festlegen"}" aria-label="Depot-Passwort"><button class="btn small" id="dp-pw-save">${pw() ? "Ersetzen" : "Speichern"}</button></div>
      <p id="dp-pw-state" class="dp-note">${a.token() ? (pw() ? "Abgleich mit GitHub ist aktiv (verschlüsselt)." : "GitHub-Schlüssel vorhanden, Depot-Passwort fehlt noch.") : "Ohne GitHub-Schlüssel bleibt das Depot auf diesem Gerät."}</p>
      <p><b>Von Claude bewerten lassen:</b> Tippe auf «Bericht kopieren» und füge ihn im Chat ein. Der Bericht enthält Positionen, Kaufgründe und den Depot-Check.</p>
      <div class="actions"><button class="btn small" id="dp-report">Bericht kopieren</button><button class="btn small" id="dp-export">Daten sichern (kopieren)</button><button class="btn small" id="dp-import">Daten einfügen</button></div>
      <textarea id="dp-area" rows="5" hidden aria-label="Depot-Daten"></textarea>
      <p id="dp-copy-state" class="dp-note" role="status"></p>
    </div>
    <p class="dp-note">Persönliches Journal, keine Anlageberatung. Werte mit Kursen und Wechselkursen vom letzten automatischen Update.</p>`;
  bind(root, d);
}

function bericht(d) {
  const a = A(), c = check(d);
  const L = [`Mein Depot (Stand ${new Date().toLocaleDateString("de-CH")}, Kurse vom letzten Update)`,
    `Wert ${chf(c.wert)}, investiert ${chf(c.kosten)}, Gewinn/Verlust ${c.guvPct != null ? a.nf(c.guvPct, 1) + " %" : "–"}, realisiert ${chf(c.real)}, Dividenden pro Jahr ${chf(c.divJahr)}`,
    `Qualität gewichtet ${c.q != null ? a.nf(c.q, 0) : "–"}, Timing gewichtet ${c.t != null ? a.nf(c.t, 0) : "–"}, Käufe nach System: ${c.imSystem} von ${c.kaeufe}`,
    `Regionen: ${c.region.map(([k, v]) => `${k} ${a.nf(v, 0)} %`).join(", ")} | Währungen: ${c.waehrung.map(([k, v]) => `${k} ${a.nf(v, 0)} %`).join(", ")}`, "", "Positionen:"];
  c.offen.forEach(p => L.push(`- ${p.name} (${p.ticker}): ${a.nf(p.stueck, 3)} Stück, Einstand ${a.money(p.einstand, p.w)}, Kurs ${a.money(p.kurs, p.w)}, Wert ${chf(p.wertCHF)}, ${p.guvPct != null ? a.nf(p.guvPct, 1) + " %" : ""}${p.v ? `, Q ${p.v.q}, T ${p.v.t}${p.v.status ? ", " + p.v.status : ""}` : ""}`));
  L.push("", "Journal:");
  [...d.tx].sort((x, y) => x.datum.localeCompare(y.datum)).forEach(t => L.push(`- ${t.datum} ${TYP[t.typ]} ${info(t.ticker, d).name}: ${t.typ === "dividende" ? t.betrag : `${t.stueck} × ${t.kurs}`}${t.grund && t.typ === "kauf" ? `, Grund: ${t.grund}` : ""}${t.signal ? `, damals Q ${t.signal.q} T ${t.signal.t} ${t.signal.status || ""}` : ""}${t.notiz ? `, Notiz: ${t.notiz}` : ""}`));
  if (c.hinweise.length) { L.push("", "Hinweise der App:"); c.hinweise.forEach(h => L.push("- " + h[1])); }
  L.push("", "Bitte bewerte mein Depot nach unserem Schema.");
  return L.join("\n");
}

async function kopieren(text, el) {
  try { await navigator.clipboard.writeText(text); el.textContent = "Kopiert. Jetzt im Chat einfügen."; }
  catch { const ta = document.getElementById("dp-area"); ta.hidden = false; ta.value = text; ta.focus(); ta.select(); el.textContent = "Text markiert: jetzt kopieren (Teilen oder Strg/Cmd+C)."; }
}

function bind(root, d) {
  const a = A(), $ = id => document.getElementById(id), rerender = () => render(root);
  $("dp-new") && ($("dp-new").onclick = () => { UI.form = { typ: "kauf" }; rerender(); });
  $("dp-new-div") && ($("dp-new-div").onclick = () => { UI.form = { typ: "dividende" }; rerender(); });
  root.querySelectorAll("[data-edit]").forEach(b => b.onclick = () => { const t = d.tx.find(x => x.id === b.dataset.edit); UI.form = { edit: t.id, ticker: t.ticker, typ: t.typ }; rerender(); scrollTo(0, 0); });
  const f = $("dp-form");
  if (f) {
    const art = () => $("dp-typ").value;
    const sichtbar = () => {
      const t = art();
      f.querySelectorAll(".dp-kauf").forEach(x => x.hidden = t === "dividende");
      f.querySelectorAll(".dp-div").forEach(x => x.hidden = t !== "dividende");
      f.querySelectorAll(".dp-nur-kauf").forEach(x => x.hidden = t !== "kauf");
      $("dp-andere").hidden = $("dp-ticker").value !== "__andere";
    };
    sichtbar();
    $("dp-typ").onchange = sichtbar;
    $("dp-ticker").onchange = () => { UI.form = { ...UI.form, ticker: $("dp-ticker").value, typ: art() }; rerender(); };
    $("dp-cancel").onclick = () => { UI.form = null; rerender(); };
    if ($("dp-delete")) $("dp-delete").onclick = () => {
      if ($("dp-delete").dataset.sure !== "1") { $("dp-delete").dataset.sure = "1"; $("dp-delete").textContent = "Wirklich löschen?"; return; }
      d.tx = d.tx.filter(x => x.id !== UI.form.edit); schreiben(d); UI.form = null; rerender();
    };
    f.onsubmit = e => {
      e.preventDefault();
      const num = id => { const v = parseFloat(String($(id).value).replace(",", ".")); return isNaN(v) ? null : v; };
      const typ = art(); let ticker = $("dp-ticker").value;
      const err = m => { $("dp-err").textContent = m; };
      if (ticker === "__andere") {
        const n = $("dp-aname").value.trim(); if (!n) return err("Bitte Name und Kürzel der anderen Aktie eintragen.");
        ticker = (n.match(/\(([^)]+)\)/)?.[1] || n).toUpperCase().replace(/\s+/g, "");
        d.manuell[ticker] = { name: n.replace(/\s*\([^)]*\)\s*/, "") || n, waehrung: "USD", kurs: num("dp-kurs") };
      }
      const datum = $("dp-datum").value; if (!datum) return err("Bitte ein Datum wählen.");
      const tx = { id: UI.form.edit || (Date.now().toString(36) + Math.random().toString(36).slice(2, 6)), datum, ticker, typ, fx: num("dp-fx"), notiz: $("dp-notiz").value.trim() };
      if (typ === "dividende") { tx.betrag = num("dp-betrag"); if (!tx.betrag) return err("Bitte den erhaltenen Betrag eintragen."); }
      else {
        tx.stueck = num("dp-stueck"); tx.kurs = num("dp-kurs"); tx.gebuehr = num("dp-geb") || 0;
        if (!tx.stueck || !tx.kurs) return err("Bitte Stückzahl und Kurs eintragen.");
        if (typ === "verkauf") { const p = positionen(d).find(x => x.ticker === ticker); if (!p || p.stueck + 1e-9 < tx.stueck - (UI.form.edit ? (d.tx.find(x => x.id === UI.form.edit)?.stueck || 0) : 0)) return err("Du kannst nicht mehr verkaufen, als du im Journal besitzt."); }
        if (typ === "kauf") tx.grund = $("dp-grund").value;
      }
      const alt = UI.form.edit ? d.tx.find(x => x.id === UI.form.edit) : null;
      const i = info(ticker, d);
      tx.signal = alt?.signal || (i.v ? { q: i.v.q, t: i.v.t, status: i.v.status || null, pess: i.v.L?.pessimismus?.wert ?? null, kurs: i.v.kurs } : null);
      d.tx = d.tx.filter(x => x.id !== tx.id).concat(tx);
      schreiben(d); UI.form = null; UI.msg = ""; rerender(); scrollTo(0, 0);
    };
  }
  $("dp-pw-save").onclick = async () => {
    const v = $("dp-pw").value; const st = $("dp-pw-state");
    if (v.length < 8) { st.textContent = "Bitte mindestens 8 Zeichen verwenden."; return; }
    try { localStorage.setItem(PW, v); } catch {}
    if (!a.token()) { st.textContent = "Passwort gespeichert. Für den Abgleich fehlt noch der GitHub-Schlüssel unter «So funktioniert's»."; return; }
    st.textContent = "Prüfe …";
    try {
      const { box } = await ghDatei();
      if (box) { const remote = await entschluesseln(box, v); if ((remote.ts || 0) > (lesen().ts || 0)) localStorage.setItem(KEY, JSON.stringify(remote)); }
      await sync(lesen()); st.textContent = "Abgleich aktiv. Dein Depot ist verschlüsselt auf GitHub gespeichert."; setTimeout(rerender, 900);
    } catch (e) { st.textContent = e.name === "OperationError" ? "Dieses Passwort passt nicht zum gespeicherten Depot. Nimm dasselbe Passwort wie auf dem anderen Gerät." : "GitHub hat nicht geantwortet. Später nochmals versuchen."; }
  };
  $("dp-report").onclick = () => kopieren(bericht(lesen()), $("dp-copy-state"));
  $("dp-export").onclick = () => kopieren(JSON.stringify(lesen()), $("dp-copy-state"));
  $("dp-import").onclick = () => {
    const ta = $("dp-area"), st = $("dp-copy-state");
    if (ta.hidden || !ta.value.trim().startsWith("{")) { ta.hidden = false; ta.value = ""; ta.placeholder = "Gesicherte Depot-Daten hier einfügen und nochmals auf «Daten einfügen» tippen"; ta.focus(); st.textContent = ""; return; }
    try { const obj = JSON.parse(ta.value); if (!Array.isArray(obj.tx)) throw 0; schreiben({ ...leer(), ...obj }); st.textContent = "Daten übernommen."; setTimeout(rerender, 400); }
    catch { st.textContent = "Das sind keine gültigen Depot-Daten."; }
  };
}

// ---------- Schnittstelle zur App ----------
window.Depot = {
  async render(root, ticker) {
    await laden();
    if (ticker) UI.form = { typ: "kauf", ticker };
    render(root); scrollTo(0, 0);
  },
  bestand(ticker) { try { const p = positionen(lesen()).find(x => x.ticker === ticker && x.stueck > 0); return p || null; } catch { return null; } }
};
})();
