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
import re
import base64, json, math, os, sys, time, datetime as dt
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
                meta = dict(res["meta"])
                # Yahoo liefert die Tageskerze des letzten Handelstags manchmal erst Stunden später.
                # Dann den letzten Kurs aus den Metadaten als Kerze anhängen.
                try:
                    if "interval=1d" in query and rows and meta.get("regularMarketTime") and meta.get("regularMarketPrice"):
                        md = dt.datetime.utcfromtimestamp(meta["regularMarketTime"] + off).date().isoformat()
                        if md > rows[-1]["d"]:
                            px = meta["regularMarketPrice"]
                            rows.append({"d": md, "h": max(meta.get("regularMarketDayHigh") or px, px), "l": min(meta.get("regularMarketDayLow") or px, px),
                                         "c": px, "v": meta.get("regularMarketVolume") or 0})
                except Exception:
                    pass
                divs = (res.get("events") or {}).get("dividends") or {}
                meta["_div"] = sorted([dt.datetime.utcfromtimestamp(v["date"] + off).date().isoformat(), round(v["amount"], 4)]
                                      for v in divs.values() if v.get("amount"))
                return rows, meta
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
    k0 = max(0, n - 505)            # Tageschart: 2 Jahre (App zeigt 1 oder 2 Jahre)
    w0 = max(0, len(W.c) - 261)     # Wochenchart: 5 Jahre
    rd = lambda a: [round(x, 2 if abs(x) >= 1 else 4) for x in a]
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
        "chart": {"d": D.d[k0:], "c": rd(D.c[k0:]), "e50": rd(D.e50[k0:]), "e200": rd(D.e200[k0:])},
        "chartw": {"d": W.d[w0:], "c": rd(W.c[w0:]), "e50": rd(W.e50[w0:]), "e200": rd(W.e200[w0:])},
    }



# ---------- Benachrichtigungen (ntfy) ----------
APP_URL = os.environ.get("APP_URL", "https://pasidreamer.github.io/Aktien-Analyse/")


def money(v, w):
    if v is None:
        return "–"
    d = 1 if w == "GBp" else (0 if v >= 1000 else 2)
    s = f"{v:,.{d}f}".replace(",", "'")
    return {"USD": f"{s} $", "EUR": f"{s} €", "CHF": f"{s} CHF", "GBp": f"{s} p"}.get(w, f"{s} {w}")


def build_alerts(stocks, out, old):
    msgs = []
    by = {s["ticker"]: s for s in stocks}
    for t, r in out.items():
        st, prev = by[t], old.get("aktien", {}).get(t)
        if not prev or prev.get("datum") == r.get("datum"):
            continue  # erstes Mal oder kein neuer Börsentag
        w, z, name = st["waehrung"], st["zonen"], st["name"]
        info = f"Kurs {money(r['kurs'], w)}, Qualität {r['q']}, Timing {r['t']}"
        ps, ns = prev.get("status"), r.get("status")
        if ns != ps:
            if ns == "in_zone":
                zone = next((f"{money(lo, w)} bis {money(hi, w)}" for lo, hi in z.get("kauf", []) if lo <= r["kurs"] <= hi), "")
                msgs.append((f"{name} ist in der Kaufzone", f"Zone {zone}. {info}. Jetzt auf die Wende im Tageschart achten.", "green_circle", 4, t))
            elif ns == "trigger":
                msgs.append((f"{name}: Trigger ausgelöst", f"Der Kurs hat den Trigger bei {money(z.get('trigger'), w)} auf Tagesschlussbasis überschritten. {info}.", "rocket", 4, t))
            elif ns == "abbruch":
                msgs.append((f"{name}: Abbruch-Marke gebrochen", f"Wochenschluss unter {money(z.get('abbruch'), w)}. Aktie neu bewerten. {info}.", "red_circle", 4, t))
            elif ns == "unter_abbruch" and ps != "abbruch":
                msgs.append((f"{name} unter der Abbruch-Marke", f"Tagesschluss unter {money(z.get('abbruch'), w)}. Entscheidend ist der Wochenschluss am Freitag. {info}.", "warning", 3, t))
            elif ns == "nahe_zone" and r["q"] >= 60 and ps not in ("in_zone",):
                msgs.append((f"{name} nähert sich der Kaufzone", f"Nur noch {r['dist_zone']:.1f} % darüber. {info}.", "eyes", 3, t))
        if r["t"] >= 60 > prev.get("t", 0) and r["q"] >= 45:
            msgs.append((f"{name}: Timing jetzt {r['t']}", f"Die Timing-Ampel ist auf hellgrün gesprungen. {info}.", "traffic_light", 3, t))
        # Zahlen sind raus: erste Meldung nach dem Zahlentag, mit der Kursreaktion seit dem Schluss vor den Zahlen
        zt = st.get("zahlen") or ""
        zahlen_neu = bool(re.match(r"\d{4}-\d{2}-\d{2}$", zt)) and prev.get("datum", "") <= zt < r.get("datum", "")
        if zahlen_neu:
            ch = r.get("chart") or {}
            vor = [c for d_, c in zip(ch.get("d", []), ch.get("c", [])) if d_ < zt]
            reak = (r["kurs"] / vor[-1] - 1) * 100 if vor and vor[-1] else r.get("chg1")
            stark = reak is not None and abs(reak) >= 5
            msgs.append((f"{name}: Zahlen sind raus ({reak:+.1f} %)" if reak is not None else f"{name}: Zahlen sind raus",
                         f"Kursreaktion seit dem Schluss vor den Zahlen: {reak:+.1f} %. {info}. "
                         + ("Starke Bewegung: Zahlen und Ausblick prüfen, bevor du handelst." if stark else "Ampeln und These kurz prüfen.")
                         + " Die kurze Auswertung erscheint am Abend in der App.",
                         "bar_chart", 4 if stark else 3, t))
        # Starke Tagesbewegung (ohne Zahlen): ab 7 % an einem Tag
        elif r.get("chg1") is not None and abs(r["chg1"]) >= 7:
            msgs.append((f"{name} {'fällt' if r['chg1'] < 0 else 'steigt'} {abs(r['chg1']):.1f} % an einem Tag",
                         f"{info}. Nachrichten prüfen: Panik oder echte Veränderung?", "zap", 4, t))
    # Zahlen morgen
    tomorrow = (dt.date.today() + dt.timedelta(days=1)).isoformat()
    for st in stocks:
        if st.get("zahlen") == tomorrow and (tomorrow + st["ticker"]) not in old.get("erinnert", []):
            msgs.append((f"Morgen Zahlen: {st['name']}", "Die Quartalszahlen kommen morgen. Danach prüfen wir die Ampeln.", "calendar", 3, st["ticker"]))
    return msgs


def send_alerts(msgs):
    topic = os.environ.get("NTFY_TOPIC", "").strip()
    if not topic or not msgs:
        print(f"{len(msgs)} Meldungen, gesendet: {'nein (kein NTFY_TOPIC)' if not topic else 'ja'}")
        return
    for title, body, tag, prio, t in msgs[:15]:
        req = urllib.request.Request(f"https://ntfy.sh/{topic}", data=body.encode("utf-8"), method="POST", headers={
            "Title": "=?UTF-8?B?" + base64.b64encode(title.encode("utf-8")).decode() + "?=",
            "Tags": tag, "Priority": str(prio), "Click": f"{APP_URL}#/aktie/{t}" if t else APP_URL})
        try:
            urllib.request.urlopen(req, timeout=20).read()
            print("Meldung gesendet:", title)
        except Exception as e:
            print("Meldung fehlgeschlagen:", title, e, file=sys.stderr)


# ---------- Stimmung (Kontra-Indikator) ----------
def pessimismus(daily, W):
    """0–100: wie viel Angst im Kurs steckt. Abstand zum 52-Wochen-Hoch, Wochen-RSI, Abstand unter der Wochen-EMA 200."""
    j = len(W.c) - 1
    p = daily[-1]["c"]
    hoch = max(x["h"] for x in daily[-252:])
    dd = (1 - p / hoch) * 100
    rw = W.rsi[j]
    unter = (1 - p / W.e200[j]) * 100
    t1 = clamp(dd / 40 * 40, 0, 40)                 # 40 % unter dem Hoch = volle 40 Punkte
    t2 = clamp((55 - rw) / 25 * 30, 0, 30)          # Wochen-RSI 30 oder tiefer = volle 30 Punkte
    t3 = clamp(unter / 20 * 30, 0, 30)              # 20 % unter der Wochen-EMA 200 = volle 30 Punkte
    s = round(t1 + t2 + t3)
    stufe = "hoch" if s >= 60 else "erhöht" if s >= 35 else "normal"
    return {"wert": s, "stufe": stufe, "abstand_hoch": round(dd, 1), "rsi_w": round(rw, 1), "unter_ema200w": round(unter, 1)}


def fear_greed():
    """CNN Fear & Greed Index (0 = extreme Angst, 100 = extreme Gier)."""
    url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata/" + (dt.date.today() - dt.timedelta(days=370)).isoformat()
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json", "Referer": "https://edition.cnn.com/markets/fear-and-greed", "Origin": "https://edition.cnn.com"})
    with urllib.request.urlopen(req, timeout=30) as r:
        j = json.load(r)
    fg = j["fear_and_greed"]
    hist = j.get("fear_and_greed_historical", {}).get("data", [])
    verlauf, seen = [], set()
    for pnt in hist:
        d = dt.datetime.utcfromtimestamp(pnt["x"] / 1000).date().isoformat()
        if d not in seen:
            seen.add(d); verlauf.append([d, round(pnt["y"])])
    return {"wert": round(fg["score"]), "text": fg.get("rating"), "vortag": round(fg.get("previous_close") or 0),
            "woche": round(fg.get("previous_1_week") or 0), "monat": round(fg.get("previous_1_month") or 0),
            "jahr": round(fg.get("previous_1_year") or 0), "verlauf": verlauf[-260:]}


def markt():
    m = {}
    try:
        rows, _ = fetch("^GSPC", "range=2y&interval=1d")
        S = Series(rows)
        i = len(S.c) - 1
        hoch = max(x["h"] for x in rows[-252:])
        m["sp500"] = {"kurs": round(S.c[i], 2), "datum": S.d[i], "chg1": round((S.c[i] / S.c[i - 1] - 1) * 100, 2),
                      "hoch52": round(hoch, 2), "abstand_hoch": round((1 - S.c[i] / hoch) * 100, 1),
                      "ema200": round(S.e200[i], 2), "ueber_ema200": S.c[i] > S.e200[i], "rsi": round(S.rsi[i], 1),
                      "verlauf": [[S.d[k], round(S.c[k], 1)] for k in range(max(0, i - 251), i + 1)]}
    except Exception as e:
        print("S&P 500 nicht verfügbar:", e, file=sys.stderr)
    try:
        rows, _ = fetch("^VIX", "range=3mo&interval=1d")
        m["vix"] = {"kurs": round(rows[-1]["c"], 2), "datum": rows[-1]["d"]}
    except Exception as e:
        print("VIX nicht verfügbar:", e, file=sys.stderr)
    fx = {"CHF": 1.0}
    for cur, sym in (("USD", "USDCHF=X"), ("EUR", "EURCHF=X"), ("GBP", "GBPCHF=X")):
        try:
            rows, _ = fetch(sym, "range=5d&interval=1d")
            fx[cur] = round(rows[-1]["c"], 5)
        except Exception as e:
            print("Wechselkurs fehlt", sym, e, file=sys.stderr)
    m["fx"] = fx
    try:
        m["fear_greed"] = fear_greed()
    except Exception as e:
        print("Fear & Greed nicht verfügbar:", e, file=sys.stderr)
    return m


# ---------- Dividenden ----------
RHYTHMUS = {1: "jährlich", 2: "halbjährlich", 3: "dreimal pro Jahr", 4: "quartalsweise", 12: "monatlich"}


def dividenden(divs, kurs, heute=None):
    """Dividenden-Historie (Ex-Tage) zu Rhythmus, Jahressumme, Rendite und nächstem erwartetem Ex-Tag."""
    heute = heute or dt.date.today()
    if not divs:
        return None
    hist = [[d, a] for d, a in divs if d >= (heute - dt.timedelta(days=3 * 366)).isoformat()]
    if not hist:
        return None
    jahr = [a for d, a in hist if d > (heute - dt.timedelta(days=372)).isoformat()]
    # Sonderdividenden ausblenden: Beträge über dem 2.5-fachen des Medians
    beträge = sorted(a for _, a in hist)
    median = beträge[len(beträge) // 2]
    regulär = [[d, a] for d, a in hist if a <= 2.5 * median]
    letzte = regulär[-1] if regulär else hist[-1]
    n = len([a for a in jahr if a <= 2.5 * median]) or 1
    daten = [dt.date.fromisoformat(d) for d, _ in regulär[-5:]]
    abst = sorted((b - a).days for a, b in zip(daten, daten[1:])) or [365 // n]
    schritt = abst[len(abst) // 2]
    naechste = dt.date.fromisoformat(letzte[0])
    while naechste <= heute:
        naechste += dt.timedelta(days=schritt)
    # Vorjahrestermin als genauere Schätzung, falls vorhanden
    vorjahr = [d for d, _ in regulär if abs((dt.date.fromisoformat(d) + dt.timedelta(days=365) - naechste).days) <= 25]
    if vorjahr:
        naechste = dt.date.fromisoformat(vorjahr[-1]) + dt.timedelta(days=364)
        while naechste <= heute:
            naechste += dt.timedelta(days=7)
    summe = round(sum(jahr), 4)
    return {
        "historie": hist,
        "pro_jahr": n,
        "rhythmus": RHYTHMUS.get(n, f"{n}-mal pro Jahr"),
        "letzte": letzte,
        "summe_12m": summe,
        "rendite": round(summe / kurs * 100, 2) if kurs else None,
        "naechste_ex_erwartet": naechste.isoformat(),
        "ex_monate": sorted({int(d[5:7]) for d, _ in regulär[-n:]}),
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
            divs = []
            try:
                monthly, mmeta = fetch(sym, f"period1=0&period2={int(time.time())}&interval=1mo&events=div")
                divs = mmeta.get("_div", [])
            except Exception:
                monthly = None
            r = evaluate(st, daily, wk, monthly)
            try:
                r["pessimismus"] = pessimismus(daily, Series(wk))
            except Exception as e:
                print("Pessimismus übersprungen", st["ticker"], e, file=sys.stderr)
            try:
                r["div"] = dividenden(divs, r["kurs"])
            except Exception as e:
                print("Dividenden übersprungen", st["ticker"], e, file=sys.stderr)
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
    tomorrow = (dt.date.today() + dt.timedelta(days=1)).isoformat()
    live["erinnert"] = [k for k in old.get("erinnert", []) if k[:10] >= dt.date.today().isoformat()] + \
        [tomorrow + s["ticker"] for s in stocks if s.get("zahlen") == tomorrow and (tomorrow + s["ticker"]) not in old.get("erinnert", [])]
    live["markt"] = markt()
    extra = []
    try:
        fg_neu = live["markt"].get("fear_greed", {}).get("wert")
        fg_alt = old.get("markt", {}).get("fear_greed", {}).get("wert")
        if fg_neu is not None and fg_alt is not None:
            if fg_alt >= 25 > fg_neu:
                extra.append(("Gesamtmarkt: Extreme Angst", f"Der Fear & Greed Index ist auf {fg_neu} gefallen. Historisch oft eine gute Phase, um gute Aktien in kleinen Tranchen zu prüfen. Nicht alles auf einmal.", "warning", 4, None))
            elif fg_alt <= 75 < fg_neu:
                extra.append(("Gesamtmarkt: Extreme Gier", f"Der Fear & Greed Index ist auf {fg_neu} gestiegen. Vorsicht beim Nachkaufen, Rücksetzer werden wahrscheinlicher.", "fire", 3, None))
        for st in stocks:
            r = out.get(st["ticker"], {}); pv = old.get("aktien", {}).get(st["ticker"], {}).get("pessimismus", {})
            pn = r.get("pessimismus") or {}
            if pn.get("wert", 0) >= 60 and pv.get("wert", 100) < 60 and r.get("q", 0) >= 60:
                extra.append((f"{st['name']}: Kontra-Signal", f"Pessimismus {pn['wert']} von 100 ({pn['abstand_hoch']} % unter dem Jahreshoch) bei Qualität {r['q']}. Die Angst ist gross, die Firma gut.", "eyes", 3, st["ticker"]))
    except Exception as e:
        print("Stimmungs-Meldungen übersprungen:", e, file=sys.stderr)
    try:
        send_alerts(build_alerts(stocks, out, old) + extra)
    except Exception as e:
        print("Benachrichtigungen übersprungen:", e, file=sys.stderr)
    json.dump(live, open(live_path, "w"), ensure_ascii=False, separators=(",", ":"))
    json.dump(hist, open(hist_path, "w"), ensure_ascii=False, separators=(",", ":"))
    if len(errors) == len(stocks):
        sys.exit("Keine Kursdaten erhalten")


if __name__ == "__main__":
    main()
