/* Aktien-Ampel: Login und gemeinsame Datenbank (Supabase).
   Der Schlüssel unten ist der öffentliche «publishable key». Er darf in der App stehen:
   Was jemand lesen oder schreiben darf, regeln die Regeln (RLS) in der Datenbank. */
(() => {
"use strict";
const URL = "https://qqtwodmsyhmaevhruobe.supabase.co";
const KEY = "sb_publishable_cBVf-ej-KelP_KNwjGLWlw_pyl_peF5";
// Push an Pascal, wenn jemand eine Aktie vorschlägt (in der App «ntfy» abonnieren)
const VORSCHLAG_TOPIC = "aa-vorschlag-q7m2xk9fwp4h";
const APP_URL = "https://pasidreamer.github.io/Aktien-Analyse/";

let sb = null, ich = null;
try { sb = window.supabase.createClient(URL, KEY, { auth: { persistSession: true, autoRefreshToken: true, storageKey: "aa-login" } }); } catch (e) { console.warn("Supabase fehlt", e); }

const fehler = e => {
  const m = (e && (e.message || e.error_description)) || String(e || "");
  if (/invalid login credentials/i.test(m)) return "E-Mail oder Passwort stimmt nicht.";
  if (/failed to fetch|network/i.test(m)) return "Keine Verbindung. Bist du online?";
  if (/password should be at least|weak/i.test(m)) return "Das Passwort ist zu kurz oder zu einfach. Nimm mindestens 8 Zeichen.";
  if (/same_password|different from the old/i.test(m)) return "Das neue Passwort muss anders sein als das alte.";
  return m || "Etwas hat nicht geklappt.";
};
const pruefe = r => { if (r.error) throw r.error; return r.data; };

async function profilLaden(user) {
  const data = pruefe(await sb.from("profile").select("id,name,rolle").eq("id", user.id).maybeSingle());
  ich = { id: user.id, email: user.email, name: data?.name || "", rolle: data?.rolle || "mitglied" };
  try { localStorage.setItem("aa-ich", JSON.stringify(ich)); } catch {}
  return ich;
}

window.SB = {
  bereit: () => !!sb,
  ich: () => ich,
  admin: () => ich?.rolle === "admin",
  // Beim Start: gespeicherte Anmeldung prüfen. Offline gilt das zuletzt bekannte Profil.
  async start() {
    if (!sb) return null;
    const { data } = await sb.auth.getSession();
    const user = data?.session?.user;
    if (!user) { ich = null; return null; }
    try { return await profilLaden(user); }
    catch { try { const alt = JSON.parse(localStorage.getItem("aa-ich")); if (alt?.id === user.id) return (ich = alt); } catch {} ich = { id: user.id, email: user.email, name: "", rolle: "mitglied" }; return ich; }
  },
  async anmelden(email, passwort) {
    try {
      const d = pruefe(await sb.auth.signInWithPassword({ email: email.trim(), password: passwort }));
      return await profilLaden(d.user);
    } catch (e) { throw new Error(fehler(e)); }
  },
  async abmelden() { try { await sb.auth.signOut(); } catch {} ich = null; try { localStorage.removeItem("aa-ich"); } catch {} },
  async passwort(neu) { try { pruefe(await sb.auth.updateUser({ password: neu })); } catch (e) { throw new Error(fehler(e)); } },
  async name(neu) {
    try { pruefe(await sb.from("profile").update({ name: neu.trim().slice(0, 40) }).eq("id", ich.id)); ich.name = neu.trim().slice(0, 40); }
    catch (e) { throw new Error(fehler(e)); }
  },

  // ---------- Journal (eine Zeile pro Person) ----------
  async journalLaden() {
    const d = pruefe(await sb.from("journale").select("daten,geaendert").eq("user_id", ich.id).maybeSingle());
    return d ? d.daten : null;
  },
  async journalSpeichern(daten) {
    pruefe(await sb.from("journale").upsert({ user_id: ich.id, daten, geaendert: new Date().toISOString() }));
  },

  // ---------- Vorschläge ----------
  async vorschlagen({ symbol, name, notiz }) {
    try {
      pruefe(await sb.from("vorschlaege").insert({ user_id: ich.id, symbol: String(symbol).slice(0, 60), name: String(name || "").slice(0, 120), notiz: String(notiz || "").slice(0, 300) }));
    } catch (e) { throw new Error(fehler(e)); }
    // Push an Pascal (nur Info, kostet nichts)
    try {
      const q = new URLSearchParams({ title: "Neuer Aktien-Vorschlag", tags: "bulb", click: APP_URL + "#/profil" });
      await fetch(`https://ntfy.sh/${VORSCHLAG_TOPIC}?${q}`, { method: "POST",
        body: `${ich.name || "Jemand"} schlägt ${name || symbol}${name && symbol && name !== symbol ? " (" + symbol + ")" : ""} vor.${notiz ? "\n«" + notiz + "»" : ""}` });
    } catch {}
  },
  async vorschlaege() {
    const rows = pruefe(await sb.from("vorschlaege").select("id,user_id,symbol,name,notiz,status,erstellt,entschieden").order("erstellt", { ascending: false }).limit(60));
    if (!rows.length) return rows;
    const leute = await window.SB.mitglieder().catch(() => []);
    const nm = Object.fromEntries(leute.map(p => [p.id, p.name]));
    return rows.map(r => ({ ...r, von: nm[r.user_id] || "" }));
  },
  async entscheiden(id, status) { pruefe(await sb.from("vorschlaege").update({ status, entschieden: new Date().toISOString() }).eq("id", id)); },
  async zurueckziehen(id) { pruefe(await sb.from("vorschlaege").delete().eq("id", id)); },
  async mitglieder() { return pruefe(await sb.from("profile").select("id,name,rolle,erstellt").order("erstellt", { ascending: true })); },
  VORSCHLAG_TOPIC
};
})();
