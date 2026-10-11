"""Rohdaten für neue Aktien-Checks (gleiches Format wie die Browser-Version).

Aufruf: python scripts/rohdaten.py ISRG BSX ABT
Ergebnis: rohdaten/<TICKER>_raw.txt mit Woche, Tag, Prüfsumme, Swings und Saisonalität.
"""
import os, sys, time, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from update import fetch, ema, rsi, adline  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "rohdaten")


def yd(d):
    return d[2:].replace("-", "")


def r2(x):
    return round(x, 2)


def fmt(x):
    return ("%.2f" % x).rstrip("0").rstrip(".")


def swings(rows, rs, ads, start, n, unit):
    out = []
    for i in range(max(start, n), len(rows) - 1):
        lo, hi = max(0, i - n), min(len(rows) - 1, i + n)
        H = all(rows[j]["h"] <= rows[i]["h"] for j in range(lo, hi + 1) if j != i)
        L = all(rows[j]["l"] >= rows[i]["l"] for j in range(lo, hi + 1) if j != i)
        if H:
            out.append(f"H,{yd(rows[i]['d'])},{fmt(rows[i]['h'])},{round(rs[i])},{fmt(ads[i] / unit)}")
        if L:
            out.append(f"L,{yd(rows[i]['d'])},{fmt(rows[i]['l'])},{round(rs[i])},{fmt(ads[i] / unit)}")
    return " ".join(out)


def cross(a, b):
    for i in range(len(a) - 1, 0, -1):
        if (a[i] > b[i]) != (a[i - 1] > b[i - 1]):
            return i
    return 0


def run(sym):
    D, _ = fetch(sym, "range=2y&interval=1d")
    W, _ = fetch(sym, "range=10y&interval=1wk")
    MO, _ = fetch(sym, f"period1=0&period2={int(time.time())}&interval=1mo")
    wkey = lambda d: (dt.date.fromisoformat(d) - dt.timedelta(days=dt.date.fromisoformat(d).weekday())).isoformat()
    W = [x for i, x in enumerate(W) if not (i < len(W) - 1 and wkey(W[i + 1]["d"]) == wkey(x["d"]))]
    vol = sum(x["v"] for x in D[-100:]) / 100
    unit = 1e6 if vol > 2e5 else 1e3
    uname = "Mio" if unit == 1e6 else "Tsd"
    wc = [x["c"] for x in W]; we50, we200, wr, wa = ema(wc, 50), ema(wc, 200), rsi(wc), adline(W)
    dc = [x["c"] for x in D]; de50, de200, dr, da = ema(dc, 50), ema(dc, 200), rsi(dc), adline(D)
    ws, ds = max(0, len(W) - 104), max(0, len(D) - 130)
    Wr = [[yd(x["d"]), r2(x["c"]), r2(we50[ws + i]), r2(we200[ws + i]), round(wr[ws + i]), round(wa[ws + i] / unit, 1)] for i, x in enumerate(W[ws:])]
    Dr = [[yd(x["d"]), r2(x["h"]), r2(x["l"]), r2(x["c"]), r2(de50[ds + i]), r2(de200[ds + i]), round(dr[ds + i], 1), round(da[ds + i] / unit, 1)] for i, x in enumerate(D[ds:])]
    sm = lambda a, i: "%.1f" % sum(float(r[i]) for r in a)
    y1 = D[-252:]
    cd, cw = cross(de50, de200), cross(we50, we200)
    mr = {}
    for i in range(1, len(MO)):
        m = int(MO[i]["d"][5:7]); r = MO[i]["c"] / MO[i - 1]["c"] - 1
        if abs(r) < 0.4:
            mr.setdefault(m, []).append(r)
    seas = " ".join("%.1f/%d/%d" % (sum(v) / len(v) * 100, round(sum(1 for x in v if x > 0) / len(v) * 100), len(v)) if v else "0/0/0"
                    for v in (mr.get(k, []) for k in range(1, 13)))
    j = lambda r: ",".join(fmt(x) if isinstance(x, float) else str(x) for x in r)
    last = D[-1]
    lines = [
        "W=" + ";".join(j(r) for r in Wr),
        "D=" + ";".join(j(r) for r in Dr),
        "CHK=" + " ".join([str(len(Wr)), str(len(Dr)), sm(Wr, 1), sm(Wr, 5), sm(Dr, 1), sm(Dr, 4)]),
        f"LAST={yd(last['d'])} {fmt(last['c'])} {fmt(last['l'])} {fmt(last['c'])} e50d {fmt(de50[-1])} e200d {fmt(de200[-1])} rsiD {dr[-1]:.1f} e50w {fmt(we50[-1])} e200w {fmt(we200[-1])} rsiW {wr[-1]:.1f}",
        f"INFO=hi52 {fmt(max(x['h'] for x in y1))} lo52 {fmt(min(x['l'] for x in y1))} athW {fmt(max(x['h'] for x in W))} crossD {yd(D[cd]['d'])} {'golden' if de50[-1] > de200[-1] else 'death'} crossW {yd(W[cw]['d'])} {'golden' if we50[-1] > we200[-1] else 'death'} vol {sum(x['v'] for x in D[-20:]) / 20 / unit:.2f}/{vol / unit:.2f} adunit {uname}",
        "SWD=" + swings(D, dr, da, len(D) - 200, 4, unit),
        "SWW=" + swings(W, wr, wa, len(W) - 110, 3, unit),
        f"SEAS={sym.split('.')[0]} {MO[0]['d'][:4]} {seas}",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for s in sys.argv[1:]:
        t = s.split(".")[0]
        txt = run(s)
        open(os.path.join(OUT, f"{t}_raw.txt"), "w").write(txt)
        print(t, [l for l in txt.split("\n") if l.startswith(("CHK", "LAST", "INFO"))])
