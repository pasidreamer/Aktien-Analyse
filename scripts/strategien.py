"""Eigene Strategie-Depots (wie ProPicks bei InvestingPro), gebaut aus unseren Daten.

Jede Strategie wählt 10 bis 25 Aktien aus «Entdecken» nach festen Regeln, gleich gewichtet.
Neu zusammengestellt am ersten Börsentag jedes Monats. Aktien, die noch gut genug sind,
bleiben drin (weniger Wechsel, weniger Gebühren). Jeden Börsentag wird die Wertentwicklung
gegen den passenden Index gerechnet.

Wichtig: Gemessen ab dem Starttag, in Lokalwährung, ohne Dividenden, Gebühren und Steuern.
Kein Rückblick in die Vergangenheit (das wäre geschönt, weil die heutigen Daten verwendet würden).

Aufruf: python scripts/strategien.py           (täglich nach alle.py)
        python scripts/strategien.py --neu     (sofort neu zusammenstellen)
"""
import json, os, sys, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import update as U  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")


def S(x, a):
    """Gesamtpunkte 0–100: Qualität, Timing, Bewertung, Momentum, dazu ein Bonus für den fairen Wert."""
    k = x.get("k") or {}
    q = a.get("q") if a and a.get("q") is not None else (x.get("g") or 0) * 20
    t = a.get("t", 40) if a else 40
    s = 0.4 * q + 0.2 * t + 0.2 * (k.get("bewertung") or 2.5) * 20 + 0.2 * (k.get("momentum") or 2.5) * 20
    fv = x.get("fv") or {}
    if fv.get("potenzial") is not None and fv.get("unsicher") in ("niedrig", "mittel", "hoch"):
        s += max(-8, min(8, fv["potenzial"] / 4))
    return s


d_ = lambda x, k, dflt=None: (x.get("d") or {}).get(k, dflt) if (x.get("d") or {}).get(k) is not None else dflt
k_ = lambda x, k: (x.get("k") or {}).get(k) or 0


STRATEGIEN = [
    {"id": "sp500", "name": "S&P 500 Plus", "n": 25, "max_sektor": 4, "benchmark": "^GSPC", "bname": "S&P 500",
     "text": "Die 25 besten Firmen aus dem S&P 500 nach Qualität, Timing, Bewertung und Momentum. Höchstens 4 pro Branche.",
     "filter": lambda x, a: "S&P 500" in (x.get("idx") or []) and (x.get("g") or 0) >= 2.75,
     "score": S},
    {"id": "tech", "name": "US-Technologie Plus", "n": 15, "max_sektor": 15, "benchmark": "^NDX", "bname": "Nasdaq-100",
     "text": "15 starke US-Firmen aus Technologie und Kommunikation, gemessen am Nasdaq-100.",
     "filter": lambda x, a: x.get("reg") == "USA" and x.get("sek") in ("Technology", "Communication Services") and (x.get("g") or 0) >= 2.75,
     "score": S},
    {"id": "dow", "name": "Blue Chips Plus", "n": 20, "max_sektor": 3, "benchmark": "^DJI", "bname": "Dow Jones",
     "text": "20 US-Riesen ab 100 Mrd. CHF Börsenwert, ausgewählt nach Qualität und Timing. Höchstens 3 pro Branche.",
     "filter": lambda x, a: x.get("reg") == "USA" and (x.get("mc") or 0) >= 100,
     "score": lambda x, a: 0.6 * ((a or {}).get("q") or (x.get("g") or 0) * 20) + 0.4 * ((a or {}).get("t") or 40)},
    {"id": "dividende", "name": "Dividenden-Strategie", "n": 20, "max_sektor": 4, "benchmark": "URTH", "bname": "MSCI World",
     "text": "20 Firmen weltweit mit mindestens 2.5 % Dividende, höchstens 80 % vom Gewinn ausgeschüttet, steigender Dividende und starkem Cashflow.",
     "filter": lambda x, a: d_(x, "div_rendite", 0) >= 2.5 and d_(x, "ausschuettung", 999) < 80 and d_(x, "div_serie", 0) >= 3
                            and k_(x, "cashflow") >= 2.5 and ((a or {}).get("q") or 0) >= 50,
     "score": lambda x, a: 0.35 * min(d_(x, "div_rendite", 0), 7) / 7 * 100 + 0.35 * ((a or {}).get("q") or 0) + 0.15 * k_(x, "cashflow") * 20 + 0.15 * ((a or {}).get("t") or 40)},
    {"id": "wachstum", "name": "Wachstums-Strategie", "n": 20, "max_sektor": 5, "benchmark": "^NDX", "bname": "Nasdaq-100",
     "text": "20 Firmen weltweit, deren Umsatz seit 3 Jahren um mindestens 10 % pro Jahr wächst, profitabel und mit intaktem Trend.",
     "filter": lambda x, a: d_(x, "umsatz_cagr3", 0) >= 10 and k_(x, "wachstum") >= 3.5 and k_(x, "profit") >= 2.5 and d_(x, "kgv") is not None,
     "score": lambda x, a: 0.4 * k_(x, "wachstum") * 20 + 0.3 * ((a or {}).get("q") or 0) + 0.3 * ((a or {}).get("t") or 40)},
    {"id": "cashflow", "name": "Cashflow-Strategie", "n": 20, "max_sektor": 4, "benchmark": "URTH", "bname": "MSCI World",
     "text": "20 Firmen weltweit mit mindestens 5 % Free-Cashflow-Rendite, wenig Schulden und guter Cashflow-Note.",
     "filter": lambda x, a: d_(x, "fcf_rendite", 0) >= 5 and (d_(x, "netto_cash", False) or d_(x, "schulden_fcf", 99) <= 3) and k_(x, "cashflow") >= 3,
     "score": lambda x, a: 0.4 * min(d_(x, "fcf_rendite", 0), 12) / 12 * 100 + 0.3 * k_(x, "cashflow") * 20 + 0.3 * ((a or {}).get("q") or 0)},
    {"id": "schweiz", "name": "Schweiz Plus", "n": 10, "max_sektor": 3, "benchmark": "^SSMI", "bname": "SMI",
     "text": "Die 10 besten Schweizer Firmen nach Qualität, Timing, Bewertung und Momentum.",
     "filter": lambda x, a: x.get("reg") == "Schweiz", "score": S},
    {"id": "asien", "name": "Asien Plus", "n": 20, "max_sektor": 4, "benchmark": "AAXJ", "bname": "MSCI Asien ohne Japan",
     "text": "20 starke Firmen aus Japan, China, Hongkong, Taiwan, Korea, Indien und Singapur.",
     "filter": lambda x, a: x.get("reg") == "Asien" and (x.get("g") or 0) >= 2.5, "score": S},
    {"id": "kontra", "name": "Unterbewertet mit Wende", "n": 15, "max_sektor": 3, "benchmark": "URTH", "bname": "MSCI World",
     "text": "15 gute Firmen, deren fairer Wert mindestens 25 % über dem Kurs liegt und deren Timing sich bessert.",
     "filter": lambda x, a: ((x.get("fv") or {}).get("potenzial") or 0) >= 25 and (x.get("fv") or {}).get("unsicher") in ("niedrig", "mittel")
                            and ((a or {}).get("q") or 0) >= 60 and ((a or {}).get("t") or 0) >= 45,
     "score": lambda x, a: 0.4 * min((x.get("fv") or {}).get("potenzial") or 0, 80) / 80 * 100 + 0.35 * ((a or {}).get("q") or 0) + 0.25 * ((a or {}).get("t") or 0)},
]


def auswahl(st, scan, alle, alt_pos):
    kand = []
    for s, x in scan.items():
        a = alle.get(s)
        if not a or a.get("kurs") is None:
            continue
        try:
            if st["filter"](x, a):
                kand.append((st["score"](x, a), s, x))
        except Exception:
            continue
    kand.sort(key=lambda t: -t[0])
    rang = {s: i for i, (_, s, _) in enumerate(kand)}
    n, cap = st["n"], st["max_sektor"]
    gew, sek = [], {}
    # Wer schon drin ist und noch unter den besten 1.5 × n liegt, bleibt
    for s in alt_pos:
        if s in rang and rang[s] < n * 1.5 and len(gew) < n and sek.get(scan[s].get("sek"), 0) < cap:
            gew.append(s); sek[scan[s].get("sek")] = sek.get(scan[s].get("sek"), 0) + 1
    for _, s, x in kand:
        if len(gew) >= n:
            break
        if s in gew or sek.get(x.get("sek"), 0) >= cap:
            continue
        gew.append(s); sek[x.get("sek")] = sek.get(x.get("sek"), 0) + 1
    return gew, len(kand), {s: round(sc, 1) for sc, s, _ in kand}


def bench_kurs(sym):
    try:
        rows, _ = U.fetch(sym, "range=5d&interval=1d")
        return rows[-1]["d"], rows[-1]["c"]
    except Exception as e:  # noqa
        print("Index nicht erreichbar", sym, e)
        return None, None


def main():
    neu_erzwingen = "--neu" in sys.argv
    scan = json.load(open(os.path.join(DATA, "scan.json")))["aktien"]
    alle = json.load(open(os.path.join(DATA, "alle.json")))["aktien"]
    p = os.path.join(DATA, "strategien.json")
    alt = json.load(open(p)) if os.path.exists(p) else {"strategien": {}}
    heute = max((a.get("d") or "") for a in alle.values())
    out = {"stand": heute, "hinweis": "Ab Starttag gemessen, gleich gewichtet, Lokalwährung, ohne Dividenden, Gebühren und Steuern.", "strategien": {}}
    for st in STRATEGIEN:
        o = alt["strategien"].get(st["id"]) or {}
        hist = o.get("historie", [])
        pos = o.get("positionen", [])
        bd, bk = bench_kurs(st["benchmark"])
        # Wert heute
        if pos and hist:
            v_reb = o["wert_reb"]
            v = v_reb * sum(x["gewicht"] * (alle.get(x["sym"], {}).get("kurs") or x["einstieg"]) / x["einstieg"] for x in pos)
            b = 100 * bk / o["bench_start"] if bk and o.get("bench_start") else (hist[-1][2] if hist else 100)
        else:
            v, b = 100.0, 100.0
        neu_monat = not pos or (o.get("rebalance", "")[:7] != heute[:7]) or neu_erzwingen
        wechsel = o.get("wechsel", [])
        if neu_monat:
            alt_syms = [x["sym"] for x in pos]
            syms, n_kand, scores = auswahl(st, scan, alle, alt_syms)
            if syms:
                rein = [s for s in syms if s not in alt_syms]
                raus = [s for s in alt_syms if s not in syms]
                if pos:
                    wechsel = ([{"datum": heute, "rein": [[s, scan[s].get("n")] for s in rein], "raus": [[s, scan.get(s, {}).get("n") or s] for s in raus]}] + wechsel)[:24]
                pos = [{"sym": s, "name": scan[s].get("n"), "sek": scan[s].get("sek"), "land": scan[s].get("land"), "app": scan[s].get("app"),
                        "gewicht": round(1 / len(syms), 5), "einstieg": alle[s]["kurs"], "seit": next((x["seit"] for x in o.get("positionen", []) if x["sym"] == s), heute),
                        "score": scores.get(s)} for s in syms]
                o["wert_reb"], o["rebalance"], o["kandidaten"] = v, heute, n_kand
        if not o.get("start"):
            o["start"], o["bench_start"] = heute, bk
            b = 100.0
        if not hist or hist[-1][0] != heute:
            hist.append([heute, round(v, 2), round(b, 2)])
        else:
            hist[-1] = [heute, round(v, 2), round(b, 2)]
        for x in pos:
            k = alle.get(x["sym"], {}).get("kurs")
            x["kurs"] = k
            x["perf"] = round((k / x["einstieg"] - 1) * 100, 1) if k else None
        out["strategien"][st["id"]] = {
            "id": st["id"], "name": st["name"], "text": st["text"], "benchmark": st["benchmark"], "bname": st["bname"],
            "start": o["start"], "bench_start": o.get("bench_start"), "rebalance": o.get("rebalance"), "wert_reb": o.get("wert_reb", 100),
            "kandidaten": o.get("kandidaten"), "positionen": pos, "historie": hist[-800:], "wechsel": wechsel}
        print(st["name"], len(pos), "Aktien,", o.get("kandidaten"), "Kandidaten, Wert", round(v, 2), "Index", round(b, 2))
    json.dump(out, open(p, "w"), ensure_ascii=False, separators=(",", ":"))


if __name__ == "__main__":
    main()
