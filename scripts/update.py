"""Aktien-Ampel: tägliches Update.

Holt Kursdaten von Yahoo Finance, berechnet EMA 50/200, RSI 14 und A/D-Linie
auf Tages- und Wochenbasis und rechnet daraus die automatischen Teile von
Timing (Trend Woche, Trend Tag, RSI, A/D, Saisonalität) und die Bewertung
in der Qualität neu. Struktur (SMC) und Smart Money bleiben aus der letzten
Analyse, Struktur wird nur bei ausgelöstem Trigger oder Abbruch angepasst.

Kalibrierung: Für jede automatische Komponente gilt
    heute = Analyse-Wert + (Regel heute - Regel am Analysetag)
So startet jede Aktie exakt bei den Punkten der letzten Analyse und bewegt
sich danach mit dem Chart.

Ergebnis: data/live.json und data/verlauf.json
"""
import json, math, os, sys, time, datetime as dt
import urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"


# ---------- Daten holen ----------
def fetch(symbol, query):
    last = None
    for host in ("query1", "query2"):
        url = f"https://{host}.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(symbol)}?{query}"
        for attempt in range(3):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
                with urllib.request.urlopen(req, timeout=30) as r:
                    j = json.load(r)
                res = j["chart"]["result"][0]
                q = res["indicators"]["quote"][0]
                off = res["meta"].get("gmtoffset", 0) or 0
                rows = []
                for i, t in enumerate(res.get("timestamp") or []):
                    c, h, l = q["close"][i], q["high"][i], q["low"][i]
                    if c is None or h is None or l is None:
                        continue
                    d = dt.datetime.utcfromtimestamp(t + off).date().isoformat()
                    rows.append({"d": d, "h": h, "l": l, "c": c, "v": q["volume"][i] or 0})
                return rows, res["meta"]
            except Exception as e:  # noqa
                last = e
                time.sleep(2 + attempt * 3)
    raise RuntimeError(f"{symbol}: {last}")


import urllib.parse  # noqa: E402


def weekly(rows):
    out, idx = [], {}
    for x in rows:
        d = dt.date.fromisoformat(x["d"])
        k = (d - dt.timedelta(days=d.weekday())).isoformat()
        if k in idx:
            p = out[idx[k]]
            p.update(h=max(p["h"], x["h"]), l=min(p["l"], x["l"]), c=x["c"], v=p["v"] + x["v"])
        else:
            idx[k] = len(out)
            out.append(dict(x, d=k))
    return out


# ---------- Indikatoren (identisch zur Browser-Version der Analysen) ----------
def ema(a, n):
    k = 2 / (n + 1)
    e, out = a[0], []
    for x in a:
        e = x * k + e * (1 - k)
        out.append(e)
    return out


def rsi(a, n=14):
    if len(a) <= n:
        return [50.0] * len(a)
    g = l = 0.0
    for i in range(1, n + 1):
        d = a[i] - a[i - 1]
        g += max(d, 0); l += max(-d, 0)
    g /= n; l /= n
    out = [50.0] * n + [100 - 100 / (1 + g / (l or 1e-9))]
    for i in range(n + 1, len(a)):
        d = a[i] - a[i - 1]
        g = (g * (n - 1) + max(d, 0)) / n
        l = (l * (n - 1) + max(-d, 0)) / n
        out.append(100 - 100 / (1 + g / (l or 1e-9)))
    return out


def adline(rows):
    s, out = 0.0, []
    for x in rows:
        r = x["h"] - x["l"]
        m = ((x["c"] - x["l"]) - (x["h"] - x["c"])) / r if r else 0
        s += m * x["v"]
        out.append(s)
    return out


class Series:
    def __init__(self, rows):
        self.rows = rows
        self.d = [x["d"] for x in rows]
        self.c = [x["c"] for x in rows]
        self.e50 = ema(self.c, 50)
        self.e200 = ema(self.c, 200)
        self.rsi = rsi(self.c)
        self.ad = adline(rows)

    def idx(self, date):
        """letzter Index mit Datum <= date"""
        i = len(self.d) - 1
        while i > 0 and self.d[i] > date:
            i -= 1
        return i


# ---------- Regeln (Bewertungsschema) ----------
def trend_pts(s, i):
    p, a, b = s.c[i], s.e50[i], s.e200[i]
    a_prev = s.e50[max(0, i - 5)]
    if p > a and p > b:
        if a > b:
            return 20 if a > a_prev else 18
        return 12
    if p >= b and p < a:
        return 13 if a > b else 10
    if p < b and p >= a:
        return 8
    if a >= b:
        return 6
    dist = abs(p / a - 1)
    flat = abs(a / a_prev - 1) < 0.01
    if dist < 0.05 and flat:
        return 4
    return 2 if dist < 0.12 else 0


def _bull_div(s, i, recent, back_from, back_to):
    lo_r = min(range(max(0, i - recent), i + 1), key=lambda k: s.c[k])
    lo_p_rng = range(max(0, i - back_to), max(1, i - back_from))
    if not len(lo_p_rng):
        return False
    lo_p = min(lo_p_rng, key=lambda k: s.c[k])
    return s.c[lo_r] < s.c[lo_p] and s.rsi[lo_r] > s.rsi[lo_p] + 2


def rsi_pts(D, i, W, j):
    rd, rw = D.rsi[i], W.rsi[j]
    if rd > 70 or rw > 70:
        return 3
    if rd < 50 and _bull_div(D, i, 10, 15, 60):
        return 13
    if rw < 50 and _bull_div(W, j, 4, 8, 30):
        return 12
    if 30 <= rd <= 45 and rd > D.rsi[max(0, i - 3)] and W.c[j] > W.e200[j]:
        return 12
    if rd < 30:
        return 5
    return 7


def _ad_tf(s, i, n):
    if i < n + 5:
        return 5
    dp = s.c[i] / s.c[i - n] - 1
    win = s.ad[max(0, i - 120): i + 1]
    rng = (max(win) - min(win)) or 1
    da = (s.ad[i] - s.ad[i - n]) / rng
    if dp <= 0.01 and da > 0.05:
        return 10
    if dp > 0 and da > 0.05:
        return 7
    if dp > 0.02 and da < -0.05:
        return 0
    if dp < 0 and da < -0.05:
        return 2
    return 5


def ad_pts(D, i, W, j):
    return min(20, _ad_tf(D, i, 20) + _ad_tf(W, j, 10))


def seasonality(monthly):
    mr = {}
    for k in range(1, len(monthly)):
        a, b = monthly[k - 1]["c"], monthly[k]["c"]
        if not a:
            continue
        q = b / a - 1
        if abs(q) > 0.6:  # Datenfehler (z. B. Pence/Pfund) überspringen
            continue
        m = int(monthly[k]["d"][5:7])
        mr.setdefault(m, []).append(q)
    table = {}
    for m in range(1, 13):
        v = mr.get(m, [])
        table[m] = (sum(v) / len(v) * 100 if v else 0, sum(1 for x in v if x > 0) / len(v) * 100 if v else 50, len(v))
    return table


def saison_pts(table, date):
    m = int(date[5:7])
    ms = [((m - 1 + k) % 12) + 1 for k in range(3)]
    avg = sum(table[x][0] for x in ms) / 3
    hit = sum(table[x][1] for x in ms) / 3
    if avg > 0 and hit >= 60:
        return 5
    if hit >= 50:
        return 3
    return 1


def bewertung_pts(ratio):
    r = ratio - 1
    if r <= -0.30: return 14
    if r <= -0.10: return 10
    if r < 0.10: return 7
    if r < 0.30: return 4
    return 1


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


# ---------- Hauptlogik ----------
def evaluate(st, daily, wk, monthly):
    D, W = Series(daily), Series(wk)
    i, j = len(D.c) - 1, len(W.c) - 1
    ds = st["analyse"]["datenstand"]
    ia, ja = D.idx(ds), W.idx(ds)
    seas = seasonality(monthly) if monthly else None
    today = D.d[i]

    rules = {
        "trend_w": lambda di, wj: trend_pts(W, wj),
        "trend_d": lambda di, wj: round(trend_pts(D, di) / 2),
        "rsi": lambda di, wj: rsi_pts(D, di, W, wj),
        "ad": lambda di, wj: ad_pts(D, di, W, wj),
        "saison": lambda di, wj: saison_pts(seas, D.d[di]) if seas else None,
    }

    z = st["zonen"]
    events = []
    trig, abb = z.get("trigger"), z.get("abbruch")
    trig_hit = None
    if trig and D.c[ia] <= trig:
        trig_hit = next((D.d[k] for k in range(ia + 1, i + 1) if D.c[k] > trig), None)
    abb_hit = next((W.d[k] for k in range(ja + 1, j + 1) if abb and W.c[k] < abb), None)

    teile = []
    for part in st["timing"]:
        k, base, mx = part["k"], part["p"], part["max"]
        val, note = base, None
        if k in rules and part.get("auto"):
            now, then = rules[k](i, j), rules[k](ia, ja)
            if now is not None and then is not None:
                val = clamp(base + now - then, 0, mx)
        if k == "smc":
            if trig_hit and (not abb_hit or trig_hit > abb_hit):
                val, note = max(val, 16), f"Trigger am {trig_hit} ausgelöst"
            elif abb_hit:
                val, note = min(val, 2), f"Abbruch-Marke am {abb_hit} unterschritten"
        teile.append({"k": k, "p": int(round(val)), "note": note})
    t_total = sum(x["p"] for x in teile)

    qteile, kurs_rel = [], D.c[i] / st["analyse"]["kurs"] if st["analyse"]["kurs"] else 1
    bew = st.get("bewertung")
    for part in st["qualitaet"]:
        val = part["p"]
        if part["k"] == "bewertung" and bew and bew.get("wert") and bew.get("schnitt"):
            then = bewertung_pts(bew["wert"] / bew["schnitt"])
            now = bewertung_pts(bew["wert"] * kurs_rel / bew["schnitt"])
            val = clamp(val + now - then, 0, part["max"])
        qteile.append({"k": part["k"], "p": int(round(val))})
    q_total = sum(x["p"] for x in qteile)

    # Zonenstatus
    p = D.c[i]
    zone, dist = None, None
    below = [zz for zz in z.get("kauf", []) if zz[0] <= p]
    for lo, hi in z.get("kauf", []):
        if lo <= p <= hi:
            zone = "in_zone"
    if below:
        top = max(hi for lo, hi in below)
        dist = (p / top - 1) * 100 if p > top else 0.0
    elif z.get("kauf"):
        dist = (p / min(lo for lo, hi in z["kauf"]) - 1) * 100
    if zone is None and dist is not None and 0 < dist <= 3:
        zone = "nahe_zone"
    status = zone
    if abb and W.c[j] < abb:
        status = "abbruch"
    elif abb and p < abb:
        status = "unter_abbruch"
    elif trig_hit:
        status = "trigger" if (dt.date.fromisoformat(today) - dt.date.fromisoformat(trig_hit)).days <= 21 else (zone or "ueber_trigger")
    n = len(D.c)
    k0 = max(0, n - 130)
    return {
        "datum": today,
        "kurs": round(p, 4),
        "chg1": round((D.c[i] / D.c[i - 1] - 1) * 100, 2) if i else 0,
        "chg5": round((D.c[i] / D.c[max(0, i - 5)] - 1) * 100, 2),
        "chg_analyse": round((kurs_rel - 1) * 100, 2),
        "hoch52": round(max(x["h"] for x in daily[-252:]), 4),
        "tief52": round(min(x["l"] for x in daily[-252:]), 4),
        "ind": {
            "ema50d": round(D.e50[i], 2), "ema200d": round(D.e200[i], 2), "rsid": round(D.rsi[i], 1),
            "ema50w": round(W.e50[j], 2), "ema200w": round(W.e200[j], 2), "rsiw": round(W.rsi[j], 1),
        },
        "q": q_total, "qteile": qteile,
        "t": t_total, "tteile": teile,
        "status": status, "dist_zone": None if dist is None else round(dist, 2),
        "trigger_am": trig_hit, "abbruch_am": abb_hit,
        "chart": {
            "d": D.d[k0:], "c": [round(x, 3) for x in D.c[k0:]],
            "e50": [round(x, 3) for x in D.e50[k0:]], "e200": [round(x, 3) for x in D.e200[k0:]],
        },
    }


def main():
    stocks = json.load(open(os.path.join(DATA, "stocks.json")))["aktien"]
    live_path, hist_path = os.path.join(DATA, "live.json"), os.path.join(DATA, "verlauf.json")
    old = json.load(open(live_path)) if os.path.exists(live_path) else {"aktien": {}}
    hist = json.load(open(hist_path)) if os.path.exists(hist_path) else {}
    out, errors = {}, []
    for st in stocks:
        sym = st["symbol"]
        try:
            daily, _ = fetch(sym, "range=2y&interval=1d")
            wk = weekly(fetch(sym, "range=10y&interval=1wk")[0])
            try:
                monthly = fetch(sym, f"period1=0&period2={int(time.time())}&interval=1mo")[0]
            except Exception:
                monthly = None
            r = evaluate(st, daily, wk, monthly)
            prev = old.get("aktien", {}).get(st["ticker"], {})
            r["status_vorher"] = prev.get("status")
            r["neu"] = r["status"] in ("in_zone", "nahe_zone", "trigger", "abbruch", "unter_abbruch") and prev.get("status") != r["status"]
            out[st["ticker"]] = r
            h = hist.setdefault(st["ticker"], [])
            if not h or h[-1][0] != r["datum"]:
                h.append([r["datum"], r["q"], r["t"], r["kurs"]])
            else:
                h[-1] = [r["datum"], r["q"], r["t"], r["kurs"]]
            hist[st["ticker"]] = h[-120:]
            print(f"{st['ticker']:6} Q {r['q']:3}  T {r['t']:3}  {r['kurs']:>10}  {r['status']}")
        except Exception as e:
            errors.append(f"{st['ticker']}: {e}")
            if st["ticker"] in old.get("aktien", {}):
                out[st["ticker"]] = old["aktien"][st["ticker"]]
            print("FEHLER", st["ticker"], e, file=sys.stderr)
        time.sleep(0.6)
    live = {"aktualisiert": dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z", "fehler": errors, "aktien": out}
    json.dump(live, open(live_path, "w"), ensure_ascii=False, separators=(",", ":"))
    json.dump(hist, open(hist_path, "w"), ensure_ascii=False, separators=(",", ":"))
    if len(errors) == len(stocks):
        sys.exit("Keine Kursdaten erhalten")


if __name__ == "__main__":
    main()
