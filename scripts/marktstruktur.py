"""Marktstruktur aus Wochenkerzen: Wendepunkte, Trend, Strukturbruch, entscheidende Marke, Range.

Ergebnis (kompakt, die App macht daraus die Sätze):
{
 "tr": "auf" | "ab" | "seit",            Trend aus Hochs und Tiefs
 "ph": "aufwaerts" | "abwaerts" | "test_tief" | "test_hoch" | "range" | "ausbruch_oben" | "ausbruch_unten",
 "pv": [["H"|"T", "2026-04-27", 400.8], ...]   letzte bestätigte Wendepunkte (Wochen), alt nach neu
 "b":  {"r": "unten"|"oben", "d": Woche des Bruchs, "p": Marke, "pd": Datum des gebrochenen Punkts, "v": vorläufig?}
 "m":  {"p": Preis, "d": Datum, "t": "T"|"H", "a": Abstand Kurs in %}      entscheidende Marke
 "u":  [Preise darunter], "o": [Preise darüber]                             nächste Strukturmarken
 "r":  {"lo", "hi", "s": Start, "w": Wochen, "pos": 0..1, "vq": Volumen steigende/fallende Wochen,
        "sp": Datum Fehlausbruch unten (Spring) | null, "ut": Datum Fehlausbruch oben | null,
        "vt": "ab"|"auf"|null  (Trend vor der Range), "deu": "akku"|"dist"|"offen"}
 "k": letzter Wochenschluss, "wd": Datum der letzten Woche
}
"""
import statistics as stx


def _r(x):
    return round(x, 2 if x < 1000 else 0)


def zigzag(rows, th):
    """Wendepunkte, die mindestens th (z. B. 0.1 = 10 %) auseinanderliegen. Liefert bestätigte Punkte und den offenen Extrempunkt."""
    piv, up, hi_i, lo_i = [], None, 0, 0
    for i, r in enumerate(rows):
        if up is None:
            if r["h"] > rows[hi_i]["h"]:
                hi_i = i
            if r["l"] < rows[lo_i]["l"]:
                lo_i = i
            if r["h"] >= rows[lo_i]["l"] * (1 + th) and lo_i < i:
                piv.append(("T", lo_i)); up, hi_i = True, i
            elif r["l"] <= rows[hi_i]["h"] * (1 - th) and hi_i < i:
                piv.append(("H", hi_i)); up, lo_i = False, i
            continue
        if up:
            if r["h"] >= rows[hi_i]["h"]:
                hi_i = i
            elif r["l"] <= rows[hi_i]["h"] * (1 - th):
                piv.append(("H", hi_i)); up, lo_i = False, i
        else:
            if r["l"] <= rows[lo_i]["l"]:
                lo_i = i
            elif r["h"] >= rows[lo_i]["l"] * (1 + th):
                piv.append(("T", lo_i)); up, hi_i = True, i
    offen = None if up is None else (("H", hi_i) if up else ("T", lo_i))
    return piv, offen


def _range(rows, med):
    """Längste Seitwärtsphase der letzten 6 bis 40 Wochen (auf Schlusskursen)."""
    n_max = min(40, len(rows))
    for n in range(n_max, 5, -1):
        w = rows[-n:]
        cs = [x["c"] for x in w]
        lo, hi = min(cs), max(cs)
        if lo <= 0:
            continue
        breite = hi / lo - 1
        if breite > max(0.12, 3.2 * med) or breite < 1.2 * med:
            continue
        hoehe = hi - lo
        if abs(cs[-1] - cs[0]) > 0.7 * hoehe and n < 10:
            continue
        unten = sum(1 for c in cs if c <= lo + 0.25 * hoehe)
        oben = sum(1 for c in cs if c >= hi - 0.25 * hoehe)
        if unten < 2 or oben < 2:
            continue
        return n, lo, hi
    return None


def kisten(rows, band, ende):
    """Frühere kleine Ranges (Haltestellen): mindestens 4 Wochen, in denen die Schlusskurse in einem engen Band blieben.
    Liefert [(lo, hi, i0, i1)], zeitlich ohne Überlappung, die längsten zuerst ausgewählt."""
    cs = [x["c"] for x in rows]
    kand = []
    for i in range(0, ende):
        lo = hi = cs[i]
        j = i
        while j + 1 < ende:
            lo2, hi2 = min(lo, cs[j + 1]), max(hi, cs[j + 1])
            if hi2 / lo2 - 1 > band:
                break
            lo, hi, j = lo2, hi2, j + 1
        if j - i + 1 >= 4:
            kand.append((j - i + 1, lo, hi, i, j))
    kand.sort(key=lambda x: (-x[0], -x[3]))
    out, belegt = [], set()
    for n, lo, hi, i, j in kand:
        if any(t in belegt for t in range(i, j + 1)):
            continue
        belegt.update(range(i, j + 1))
        out.append((lo, hi, i, j))
    return out


def haltestellen(rows, P, F, k, band, ende):
    """Zonen unter und über dem Kurs: frühere Ranges (R), alte Hochs (H) und Tiefs (T).
    Ein Hoch unter dem Kurs wurde nach oben durchbrochen und wirkt oft als Unterstützung, ein Tief über dem Kurs umgekehrt."""
    zonen = [{"t": "R", "lo": _r(lo), "hi": _r(hi), "d": rows[i]["d"], "d2": rows[j]["d"], "w": j - i + 1} for lo, hi, i, j in kisten(rows, band, ende)]
    punkte = {}
    for t, d, p, i in P + F:
        punkte.setdefault((t, d), (t, d, p, i, (t, d) in {(q[0], q[1]) for q in P}))
    for t, d, p, i, gross in sorted(punkte.values(), key=lambda x: x[3]):
        kiste = next((z for z in zonen if z["t"] == "R" and z["lo"] * 0.985 <= p <= z["hi"] * 1.015), None)
        if kiste:
            # markanter Wendepunkt am Rand einer Range: wird zur Range vermerkt (z. B. das alte Hoch als Deckel)
            if gross and abs(i - next(j for j, r in enumerate(rows) if r["d"] == kiste["d"])) <= kiste["w"] + 8:
                kiste["x"] = [t, d, _r(p)]
            continue
        zonen.append({"t": t, "lo": _r(p), "hi": _r(p), "d": d, "g": gross})
    def nah(z, y, tol):
        return z["lo"] <= y["hi"] * (1 + tol) and z["hi"] >= y["lo"] * (1 - tol)

    def ausduennen(zs):
        # Ranges haben Vorrang (die längere gewinnt), dann grosse vor feinen Wendepunkten
        out = []
        for z in sorted(zs, key=lambda z: (z["t"] != "R", -z.get("w", 0), not z.get("g"))):
            nb = next((y for y in out if nah(z, y, 0.03 if z["t"] != "R" or y["t"] != "R" else 0.01)), None)
            if not nb:
                out.append(z)
            elif z.get("g") and nb["t"] == "R" and "x" not in nb:
                nb["x"] = [z["t"], z["d"], z["lo"]]
        return out
    unten = sorted(ausduennen([z for z in zonen if z["hi"] < k * 0.995]), key=lambda z: -z["hi"])
    oben = sorted(ausduennen([z for z in zonen if z["lo"] > k * 1.005]), key=lambda z: z["lo"])
    return unten, oben


def analyse(wk, kurs=None):
    rows = [x for x in wk if x.get("c") and x.get("h") and x.get("l")][-160:]
    if len(rows) < 30:
        return None
    k = kurs or rows[-1]["c"]
    spannen = [(x["h"] - x["l"]) / x["c"] for x in rows[-52:] if x["c"]]
    med = stx.median(spannen) if spannen else 0.04
    th = min(0.25, max(0.08, 2.4 * med))
    piv, offen = zigzag(rows, th)
    P = [(t, rows[i]["d"], rows[i]["h"] if t == "H" else rows[i]["l"], i) for t, i in piv]
    H = [p for p in P if p[0] == "H"]
    T = [p for p in P if p[0] == "T"]
    last_i = len(rows) - 1

    # Strukturbruch: letzter Wochenschluss, der einen bestätigten Wendepunkt durchbricht (letzte 26 Wochen)
    bruch = None
    for j in range(last_i, max(last_i - 26, 1), -1):
        c0, c1 = rows[j - 1]["c"], rows[j]["c"]
        kand = [p for p in P if p[3] < j - 1 and ((p[0] == "T" and c0 >= p[2] > c1) or (p[0] == "H" and c0 <= p[2] < c1))]
        if kand:
            p = min(kand, key=lambda p: p[2]) if c1 < c0 else max(kand, key=lambda p: p[2])
            bruch = {"r": "unten" if p[0] == "T" else "oben", "d": rows[j]["d"], "p": _r(p[2]), "pd": p[1], "v": j == last_i}
            break

    # Trend aus den letzten zwei Hochs und Tiefs, plus Lage des Kurses
    tr = "seit"
    if len(H) >= 2 and len(T) >= 2:
        hh, hl = H[-1][2] > H[-2][2], T[-1][2] > T[-2][2]
        if hh and hl:
            tr = "auf"
        elif not hh and not hl:
            tr = "ab"
    if T and k < T[-1][2] * 0.995:
        tr = "ab"
    elif H and k > H[-1][2] * 1.005 and (not T or T[-1][2] > (T[-2][2] if len(T) > 1 else 0)):
        tr = "auf"

    # Feinere Wendepunkte für die nächsten Marken (alte Hochs können zur Unterstützung werden)
    fein, _ = zigzag(rows, max(0.05, th * 0.6))
    F = [(t, rows[i]["d"], rows[i]["h"] if t == "H" else rows[i]["l"], i) for t, i in fein]
    alle = sorted({_r(p[2]) for p in P + F})
    darunter = [x for x in alle if x < k * 0.995][::-1]
    darueber = [x for x in alle if x > k * 1.005]

    def entdoppeln(xs):
        out = []
        for x in xs:
            if all(abs(x / y - 1) > 0.03 for y in out):
                out.append(x)
        return out
    darunter, darueber = entdoppeln(darunter), entdoppeln(darueber)

    # Range (Umverteilung)
    rg = None
    rr = _range(rows, med)
    if rr:
        n, lo, hi = rr
        w = rows[-n:]
        up = sum(x["v"] for a, x in zip(w, w[1:]) if x["c"] > a["c"])
        dn = sum(x["v"] for a, x in zip(w, w[1:]) if x["c"] < a["c"])
        vq = round(up / dn, 2) if dn else None
        sp = next((x["d"] for x in w[2:] if x["l"] < lo * 0.98 and x["c"] >= lo), None)
        ut = next((x["d"] for x in w[2:] if x["h"] > hi * 1.02 and x["c"] <= hi), None)
        vor = [p for p in P if p[3] < len(rows) - n]
        # Trend vor der Range: kam der Kurs von einem Tief (also steigend) oder von einem Hoch (fallend)?
        vt = ("auf" if vor[-1][0] == "T" else "ab") if vor else None
        deu = "offen"
        if vt == "ab" and ((vq or 0) >= 1.15 or sp):
            deu = "akku"
        elif vt == "auf" and ((vq or 9) <= 0.87 or ut):
            deu = "dist"
        rg = {"lo": _r(lo), "hi": _r(hi), "s": w[0]["d"], "w": n, "pos": round((k - lo) / (hi - lo), 2) if hi > lo else 0.5,
              "vq": vq, "sp": sp, "ut": ut, "vt": vt, "deu": deu}
    in_range = bool(rg and rg["w"] >= 8 and rg["lo"] * 0.99 <= k <= rg["hi"] * 1.01)

    # Entscheidende Marke (immer eine Unterstützung unter dem Kurs):
    # in einer Range deren Untergrenze, im Abwärtstrend das nächste grosse Tief, im Aufwärtstrend das nächste Tief darunter
    m = None
    tiefs_gross = sorted([p for p in T if p[2] < k * 1.005], key=lambda p: -p[2])
    tiefs_fein = sorted([p for p in F if p[0] == "T" and p[2] < k * 1.005], key=lambda p: -p[2])
    if in_range:
        m = {"p": rg["lo"], "d": rg["s"], "t": "R", "a": round((k / rg["lo"] - 1) * 100, 1)}
    else:
        p = None
        if tr == "auf":
            p = next((q for q in tiefs_fein if k / q[2] - 1 <= 0.15), None) or (tiefs_gross[0] if tiefs_gross else None)
        else:
            p = tiefs_gross[0] if tiefs_gross and k / tiefs_gross[0][2] - 1 <= 0.2 else (tiefs_fein[0] if tiefs_fein else None)
        if p:
            m = {"p": _r(p[2]), "d": p[1], "t": "T", "a": round((k / p[2] - 1) * 100, 1)}
    # Haltestellen: frühere Ranges und alte Hochs/Tiefs (das laufende Geschehen der letzten Wochen zählt nicht)
    ende = len(rows) - max(4, rg["w"] if in_range else 0)
    zu, zo = haltestellen(rows, P, F, k, min(0.12, max(0.06, 1.8 * med)), ende)
    if m:
        zu = [z for z in zu if z["hi"] < m["p"] * 0.985]
    zu, zo = zu[:4], zo[:3]
    for z in zu + zo:
        z.pop("g", None)
    darunter = [z["hi"] for z in zu][:3] or (darunter[:3] if not m else [x for x in darunter if x < m["p"] * 0.97][:3])
    darueber = [z["lo"] for z in zo][:3] or darueber[:3]

    # Phase
    ph = "aufwaerts" if tr == "auf" else "abwaerts" if tr == "ab" else "seit"
    if in_range:
        ph = "range"
    if bruch and bruch["d"] >= rows[max(0, last_i - 2)]["d"]:
        ph = "ausbruch_oben" if bruch["r"] == "oben" else "ausbruch_unten"
    if m and m["t"] == "T" and 0 <= m["a"] <= 5 and ph != "range":
        ph = "test_tief"

    return {"tr": tr, "ph": ph, "pv": [[p[0], p[1], _r(p[2])] for p in P[-8:]], "b": bruch, "m": m,
            "u": darunter, "o": darueber, "zu": zu, "zo": zo, "r": rg, "k": _r(k), "wd": rows[-1]["d"], "th": round(th * 100, 1)}


def ereignisse(neu, alt):
    """Push-würdige Strukturereignisse gegenüber dem letzten Lauf (nur abgeschlossene Wochen)."""
    out = []
    if not neu:
        return out
    b, ba = neu.get("b"), (alt or {}).get("b")
    if b and not b.get("v") and (not ba or ba.get("d") != b["d"] or ba.get("v")):
        out.append(("bruch_" + b["r"], b))
    r, ra = neu.get("r"), (alt or {}).get("r")
    if ra and not r and alt.get("ph") == "range":
        k = neu.get("k")
        if k and k > ra["hi"]:
            out.append(("range_oben", ra))
        elif k and k < ra["lo"]:
            out.append(("range_unten", ra))
    return out
