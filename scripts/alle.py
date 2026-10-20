"""Automatische Ampeln und Alarme für alle Firmen aus «Entdecken».

Jeden Börsentag nach US-Schluss:
  Qualität (Q): aus dem Branchenvergleich (scan.json), Schnitt aus Bewertung, Wachstum, Profitabilität,
                Cashflow, umgerechnet auf 0 bis 100.
  Timing (T):   gleiche Regeln wie die App-Ampel (Trend Woche 20, Trend Tag 10, RSI 15, A/D 20, Saison 5),
                dazu automatische Näherungen für Struktur (20) und Smart Money (10).
  Alarme:       nur bei neuen Signalen (Vergleich mit dem Vortag) und nur bei guter Qualität.

Aufruf:
  python scripts/alle.py --teil 0 --von 6   (rechnet einen Teil, schreibt data/alle_teile/teil_0.json)
  python scripts/alle.py --zusammen         (Alarme, schreibt data/alle.json und sendet Push-Nachrichten)
"""
import base64, json, os, sys, time, datetime as dt, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import update as U  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
TEILE = os.path.join(DATA, "alle_teile")
TOPIC = os.environ.get("NTFY_TOPIC", "").strip()
APP = U.APP_URL


def monatlich(wk):
    out, last = [], None
    for x in wk:
        m = x["d"][:7]
        if m != last:
            out.append(dict(x))
            last = m
        else:
            out[-1] = dict(x, d=out[-1]["d"])
    return out


def struktur(W, j):
    c = W.c
    if j < 30:
        return 8, "zu wenig Daten"
    if c[j] > max(c[j - 20:j]):
        return 16, "Ausbruch über das 20-Wochen-Hoch"
    if c[j] < min(c[j - 26:j]):
        return 2, "neues 26-Wochen-Tief"
    if min(c[j - 8:j + 1]) > min(c[j - 26:j - 8]) and c[j] > W.e50[j]:
        return 12, "höhere Tiefs, über der Wochen-EMA 50"
    if c[j] < W.e50[j] < W.e200[j]:
        return 5, "Abwärtstrend, unter beiden Wochen-EMAs"
    return 8, "Seitwärts"


def smart(x):
    d = (x or {}).get("d", {})
    p, txt = 3, []
    if (d.get("aktien_pa") or 0) <= -1:
        p += 3; txt.append("Rückkäufe")
    if (d.get("schaetzung_90t") or 0) >= 2:
        p += 2; txt.append("Gewinnschätzungen steigen")
    if (d.get("schaetzung_90t") or 0) <= -3:
        p -= 2; txt.append("Gewinnschätzungen sinken")
    if (d.get("aktien_pa") or 0) >= 2:
        p -= 1; txt.append("Verwässerung")
    return max(0, min(10, p)), ", ".join(txt) or "neutral"


def qualitaet(x):
    k = (x or {}).get("k") or {}
    v = [k.get(b) for b in ("bewertung", "wachstum", "profit", "cashflow") if k.get(b) is not None]
    return round(sum(v) / len(v) * 20) if len(v) >= 3 else None


def rechne(sym, x):
    daily, _ = U.fetch(sym, "range=2y&interval=1d")
    wk = U.weekly(U.fetch(sym, "range=10y&interval=1wk")[0])
    if len(daily) < 120 or len(wk) < 60:
        raise RuntimeError("zu wenig Kursdaten")
    D, W = U.Series(daily), U.Series(wk)
    i, j = len(D.c) - 1, len(W.c) - 1
    seas = U.seasonality(monatlich(wk))
    st_p, st_t = struktur(W, j)
    sm_p, sm_t = smart(x)
    teile = [U.trend_pts(W, j), round(U.trend_pts(D, i) / 2), st_p, U.rsi_pts(D, i, W, j), U.ad_pts(D, i, W, j), sm_p, U.saison_pts(seas, D.d[i])]
    pess = U.pessimismus(daily, W)
    return {
        "d": D.d[i], "kurs": round(D.c[i], 4), "c1": round((D.c[i] / D.c[i - 1] - 1) * 100, 2),
        "q": qualitaet(x), "t": sum(teile), "tt": teile, "st": st_t, "sm": sm_t,
        "p": pess["wert"], "gcw": W.e50[j] > W.e200[j], "ue50": D.c[i] > D.e50[i], "ue200w": W.c[j] > W.e200[j],
        "rsid": round(D.rsi[i]), "rsiw": round(W.rsi[j]), "hoch": pess["abstand_hoch"],
    }


def teil(i, n):
    scan = json.load(open(os.path.join(DATA, "scan.json")))["aktien"]
    syms = sorted(scan)[i::n]
    out, fehler = {}, {}
    for k, s in enumerate(syms):
        try:
            out[s] = rechne(s, scan[s])
        except Exception as e:  # noqa
            fehler[s] = str(e)[:120]
        time.sleep(0.25)
        if k % 50 == 0:
            print(k, len(syms), len(fehler), flush=True)
    os.makedirs(TEILE, exist_ok=True)
    json.dump({"aktien": out, "fehler": fehler}, open(os.path.join(TEILE, f"teil_{i}.json"), "w"))
    print("fertig", len(out), "fehler", len(fehler))


def signale(s, r, alt, x):
    """Neue Signale gegen den Vortag. Nur bei guter Qualität."""
    if not alt or alt.get("d") == r["d"] or r["q"] is None:
        return []
    q, t, out = r["q"], r["t"], []
    fv = (x or {}).get("fv") or {}
    name = (x or {}).get("n") or s
    if t >= 60 > (alt.get("t") or 0) and q >= 60:
        out.append(("timing", f"{name}: Timing springt auf {t}", f"Qualität {q}, Timing {t}. Trend, RSI und A/D drehen positiv.", 5 + q / 100))
    if r["gcw"] and not alt.get("gcw") and q >= 50:
        out.append(("golden", f"{name}: Golden Cross im Wochenchart", f"Die Wochen-EMA 50 steigt über die EMA 200: langfristiger Aufwärtstrend. Qualität {q}, Timing {t}.", 4 + q / 100))
    if r["p"] >= 60 > (alt.get("p") or 0) and q >= 65:
        out.append(("kontra", f"{name}: viel Angst bei guter Firma", f"Pessimismus {r['p']} von 100, {r['hoch']:.0f} % unter dem Jahreshoch. Qualität {q}. Prüfen, ob die Sorgen echt sind.", 4 + q / 100))
    pot = fv.get("potenzial")
    if pot is not None and pot >= 25 and fv.get("unsicher") in ("niedrig", "mittel") and q >= 60 and r["ue50"] and not alt.get("ue50"):
        out.append(("fairwende", f"{name}: unterbewertet und Kurs dreht", f"Fairer Wert {pot:.0f} % über dem Kurs, Tagesschluss jetzt über der EMA 50. Qualität {q}, Timing {t}.", 4.5 + q / 100))
    return out


def push(title, body, tag, prio, click):
    req = urllib.request.Request(f"https://ntfy.sh/{TOPIC}", data=body.encode("utf-8"), method="POST", headers={
        "Title": "=?UTF-8?B?" + base64.b64encode(title.encode("utf-8")).decode() + "?=",
        "Tags": tag, "Priority": str(prio), "Click": click})
    try:
        urllib.request.urlopen(req, timeout=20).read()
        print("gesendet:", title)
    except Exception as e:  # noqa
        print("nicht gesendet:", title, e, file=sys.stderr)


TAG = {"timing": "traffic_light", "golden": "chart_with_upwards_trend", "kontra": "eyes", "fairwende": "moneybag"}


def zusammen():
    scan = json.load(open(os.path.join(DATA, "scan.json")))["aktien"]
    p = os.path.join(DATA, "alle.json")
    alt = json.load(open(p)) if os.path.exists(p) else {"aktien": {}, "alarme": []}
    neu, fehler = {}, {}
    for f in sorted(os.listdir(TEILE)):
        t = json.load(open(os.path.join(TEILE, f)))
        neu.update(t["aktien"]); fehler.update(t["fehler"])
    heute = dt.date.today().isoformat()
    alarme = [a for a in alt.get("alarme", []) if a["datum"] >= (dt.date.today() - dt.timedelta(days=30)).isoformat()]
    frische = []
    for s, r in neu.items():
        x = scan.get(s)
        if x and x.get("app"):
            continue  # App-Aktien haben eigene Alarme mit Zonen und Trigger
        for typ, titel, text, gewicht in signale(s, r, alt["aktien"].get(s), x):
            a = {"datum": r["d"], "sym": s, "name": (x or {}).get("n") or s, "typ": typ, "titel": titel, "text": text, "q": r["q"], "t": r["t"], "w": gewicht}
            if not any(b["sym"] == s and b["typ"] == typ and b["datum"] == a["datum"] for b in alarme):
                alarme.append(a); frische.append(a)
    # alte Werte behalten, wenn eine Aktie heute fehlt
    for s, r in alt["aktien"].items():
        if s not in neu and s in scan:
            neu[s] = r
    frische.sort(key=lambda a: -a["w"])
    alarme.sort(key=lambda a: (a["datum"], a["w"]), reverse=True)
    json.dump({"stand": heute, "anzahl": len(neu), "fehler": len(fehler), "aktien": neu, "alarme": alarme},
              open(p, "w"), ensure_ascii=False, separators=(",", ":"))
    print(len(neu), "Aktien,", len(frische), "neue Alarme,", len(fehler), "Fehler")
    if not TOPIC or not frische:
        return
    for a in frische[:3]:
        push(a["titel"], a["text"], TAG[a["typ"]], 3, f"{APP}#/scan/{a['sym']}")
    if len(frische) > 3:
        rest = "\n".join(f"• {a['name']}: {a['titel'].split(': ', 1)[-1]} (Q {a['q']}, T {a['t']})" for a in frische[3:12])
        push(f"{len(frische)} neue Signale bei Entdecken", rest + ("\n…" if len(frische) > 12 else ""), "bell", 2, f"{APP}#/alarme")


if __name__ == "__main__":
    a = sys.argv[1:]
    if "--teil" in a:
        teil(int(a[a.index("--teil") + 1]), int(a[a.index("--von") + 1]))
    else:
        zusammen()
