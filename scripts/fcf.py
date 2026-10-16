"""Free-Cashflow-Check für alle Aktien der App.

Holt die Jahreszahlen (Cashflow, Bilanz, Erfolgsrechnung) von Yahoo Finance und
bewertet den Free Cashflow nach Pascals sechs Fragen:

1. Wächst er?                (Wachstum, 20 Punkte)
2. Wie viel vom Umsatz?      (FCF-Marge, 20 Punkte)
3. Wie viel vom Börsenwert?  (FCF-Rendite, 15 Punkte)
4. Wie schnell sind die Schulden weg? (Nettoschulden / FCF, 20 Punkte)
5. Wofür wird er genutzt?    (Rückkäufe, Schuldenabbau, Dividende, 15 Punkte)
6. Ist er nachhaltig?        (keine Verlustjahre, Aktienvergütung, Gewinn-Deckung, 10 Punkte)

Ergebnis: data/fcf.json
"""
import json, os, sys, time, math, datetime as dt
import urllib.request, urllib.parse, http.cookiejar

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"

TYPES = ["TotalRevenue", "FreeCashFlow", "OperatingCashFlow", "CapitalExpenditure", "StockBasedCompensation",
         "RepurchaseOfCapitalStock", "CashDividendsPaid", "RepaymentOfDebt", "IssuanceOfDebt", "NetIncome",
         "TotalDebt", "CashCashEquivalentsAndShortTermInvestments", "CashAndCashEquivalents",
         "DilutedAverageShares", "OrdinarySharesNumber", "ShareIssued"]

jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
CRUMB = None


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json,text/html"})
    with opener.open(req, timeout=30) as r:
        return r.read()


def crumb():
    global CRUMB
    if CRUMB is None:
        try:
            get("https://fc.yahoo.com/")
        except Exception:
            pass  # setzt trotzdem Cookies
        try:
            CRUMB = get("https://query2.finance.yahoo.com/v1/test/getcrumb").decode().strip()
        except Exception:
            CRUMB = ""
    return CRUMB


def timeseries(sym):
    now = int(time.time())
    types = ",".join(p + t for p in ("annual", "trailing") for t in TYPES)
    last = None
    for attempt in range(4):
        q = {"symbol": sym, "type": types, "period1": 1420070400, "period2": now, "merge": "false"}
        if attempt >= 1 and crumb():
            q["crumb"] = crumb()
        host = "query2" if attempt % 2 else "query1"
        url = f"https://{host}.finance.yahoo.com/ws/fundamentals-timeseries/v1/finance/timeseries/{urllib.parse.quote(sym)}?" + urllib.parse.urlencode(q)
        try:
            j = json.loads(get(url))
            out = {}
            for res in j["timeseries"]["result"]:
                key = res["meta"]["type"][0]
                vals = [v for v in (res.get(key) or []) if v and v.get("reportedValue")]
                out[key] = [(v["asOfDate"], v["reportedValue"]["raw"], v.get("currencyCode")) for v in vals]
            return out
        except Exception as e:  # noqa
            last = e
            time.sleep(2 + attempt * 2)
    raise RuntimeError(f"{sym}: {last}")


def price(sym):
    for host in ("query1", "query2"):
        try:
            j = json.loads(get(f"https://{host}.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(sym)}?range=5d&interval=1d"))
            m = j["chart"]["result"][0]["meta"]
            return m["regularMarketPrice"], m.get("currency")
        except Exception:
            time.sleep(2)
    return None, None


def series(ts, name):
    """Jahreswerte als {jahr: wert} plus Währung."""
    rows = ts.get("annual" + name) or []
    cur = rows[-1][2] if rows else None
    return {r[0][:4]: r[1] for r in rows}, cur


def trailing(ts, name):
    rows = ts.get("trailing" + name) or []
    return rows[-1][1] if rows else None


def to_chf(v, cur, fx):
    if v is None or cur is None:
        return None
    if cur == "GBp":
        return v / 100 * fx.get("GBP", 0)
    return v * fx[cur] if cur in fx else None


def pts(v, steps):
    """steps: Liste (grenze, punkte) absteigend; erste Grenze, die v erreicht, zählt."""
    if v is None:
        return 0
    for g, p in steps:
        if v >= g:
            return p
    return steps[-1][1] if steps and steps[-1][0] == -math.inf else 0


def analyse(sym, ts, fx):
    fcf, cur = series(ts, "FreeCashFlow")
    rev, _ = series(ts, "TotalRevenue")
    years = sorted(y for y in fcf if y in rev)[-5:]
    if len(years) < 2:
        return None
    sbc, _ = series(ts, "StockBasedCompensation")
    buy, _ = series(ts, "RepurchaseOfCapitalStock")
    div, _ = series(ts, "CashDividendsPaid")
    rep, _ = series(ts, "RepaymentOfDebt")
    iss, _ = series(ts, "IssuanceOfDebt")
    ni, _ = series(ts, "NetIncome")
    debt, _ = series(ts, "TotalDebt")
    cash, _ = series(ts, "CashCashEquivalentsAndShortTermInvestments")
    cash2, _ = series(ts, "CashAndCashEquivalents")
    sh, _ = series(ts, "DilutedAverageShares")
    shi, _ = series(ts, "OrdinarySharesNumber")

    f_ttm = trailing(ts, "FreeCashFlow") or fcf[years[-1]]
    r_ttm = trailing(ts, "TotalRevenue") or rev[years[-1]]
    ly = years[-1]
    d_now = debt.get(ly) or 0
    c_now = cash.get(ly) if cash.get(ly) is not None else (cash2.get(ly) or 0)
    netdebt = d_now - c_now

    # 1 Wachstum
    first, lastv = fcf[years[0]], fcf[years[-1]]
    n = len(years) - 1
    cagr = ((lastv / first) ** (1 / n) - 1) * 100 if first > 0 and lastv > 0 else None
    ups = sum(1 for a, b in zip(years, years[1:]) if fcf[b] > fcf[a])
    p_wachs = pts(cagr, [(15, 14), (10, 12), (6, 9), (3, 6), (0, 3), (-math.inf, 0)]) + round(6 * ups / n)

    # 2 Marge
    marge = f_ttm / r_ttm * 100 if r_ttm else None
    p_marge = pts(marge, [(30, 20), (22, 17), (15, 14), (10, 10), (5, 5), (0, 2), (-math.inf, 0)])

    # 3 Rendite (FCF / Börsenwert)
    px, pcur = price(sym)
    shares = shi.get(ly) or (sh.get(ly) if sh else None)
    mcap_chf = to_chf(px * shares, pcur, fx) if px and shares else None
    fcf_chf = to_chf(f_ttm, cur, fx)
    rendite = fcf_chf / mcap_chf * 100 if mcap_chf and fcf_chf is not None else None
    p_rend = pts(rendite, [(7, 15), (5, 13), (4, 11), (3, 8), (2, 5), (1, 2), (-math.inf, 0)])

    # 4 Schulden: Jahre, bis die Nettoschulden mit dem FCF bezahlt wären
    jahre = netdebt / f_ttm if f_ttm > 0 else None
    if f_ttm <= 0:
        p_sch = 0
    elif netdebt <= 0:
        p_sch = 20
    else:
        p_sch = pts(-jahre, [(-0.5, 18), (-1, 16), (-2, 12), (-3, 8), (-5, 4), (-math.inf, 0)])

    # 5 Verwendung: Aktienzahl, Rückgabe, Schuldenabbau
    sh_years = [y for y in years if sh.get(y)]
    sh_chg = None
    if len(sh_years) >= 2:
        a, b = sh[sh_years[0]], sh[sh_years[-1]]
        sh_chg = ((b / a) ** (1 / (len(sh_years) - 1)) - 1) * 100
    p_sh = pts(-sh_chg if sh_chg is not None else None, [(2, 8), (1, 7), (0.3, 5), (-0.3, 3), (-1, 1), (-math.inf, 0)])
    sum_f = sum(fcf[y] for y in years if fcf[y] > 0) or 1
    sum_buy = sum(-(buy.get(y) or 0) for y in years)
    sum_div = sum(-(div.get(y) or 0) for y in years)
    sum_netrep = sum(-(rep.get(y) or 0) - (iss.get(y) or 0) for y in years)
    rueck = (sum_buy + sum_div) / sum_f * 100
    abbau = max(0, sum_netrep) / sum_f * 100
    p_use = p_sh + pts(rueck + abbau, [(80, 7), (60, 6), (40, 4), (20, 2), (-math.inf, 0)])

    # 6 Nachhaltigkeit
    neg = sum(1 for y in years if fcf[y] <= 0)
    sbc_q = sum(sbc.get(y) or 0 for y in years) / sum_f * 100
    sum_ni = sum(ni.get(y) or 0 for y in years)
    deck = sum(fcf[y] for y in years) / sum_ni if sum_ni > 0 else None
    p_nach = (4 if neg == 0 else 1 if neg == 1 else 0) \
        + (3 if sbc_q < 10 else 2 if sbc_q < 20 else 1 if sbc_q < 35 else 0) \
        + (3 if deck and 0.8 <= deck <= 1.6 else 2 if deck and 0.6 <= deck <= 2.2 else 0)

    total = p_wachs + p_marge + p_rend + p_sch + p_use + p_nach
    verw = []
    if sum_buy > 0:
        verw.append(["Aktienrückkäufe", round(sum_buy / sum_f * 100)])
    if sum_div > 0:
        verw.append(["Dividenden", round(sum_div / sum_f * 100)])
    if sum_netrep > 0:
        verw.append(["Schuldenabbau", round(sum_netrep / sum_f * 100)])
    elif sum_netrep < 0:
        verw.append(["Neue Schulden", round(sum_netrep / sum_f * 100)])
    r = lambda v, k=1: None if v is None else round(v, k)
    return {
        "waehrung": cur, "jahre": years,
        "fcf": [r(fcf[y] / 1e9, 2) for y in years],
        "umsatz": [r(rev[y] / 1e9, 2) for y in years],
        "fcf_ttm": r(f_ttm / 1e9, 2), "umsatz_ttm": r(r_ttm / 1e9, 2),
        "aktien_mio": [r(sh[y] / 1e6, 1) if sh.get(y) else None for y in years],
        "netto_schulden": r(netdebt / 1e9, 2), "schulden": r(d_now / 1e9, 2), "cash": r(c_now / 1e9, 2),
        "boersenwert_chf": r(mcap_chf / 1e9, 1) if mcap_chf else None,
        "k": {"wachstum": r(cagr), "steigende_jahre": ups, "jahre_n": n, "marge": r(marge), "rendite": r(rendite, 2),
              "schulden_jahre": r(jahre, 2) if netdebt > 0 else 0, "aktien_pa": r(sh_chg, 2), "rueckgabe": r(rueck, 0),
              "abbau": r(abbau, 0), "verlustjahre": neg, "sbc": r(sbc_q, 0), "deckung": r(deck, 2)},
        "verwendung": verw,
        "p": {"wachstum": p_wachs, "marge": p_marge, "rendite": p_rend, "schulden": p_sch, "verwendung": p_use, "nachhaltig": p_nach},
        "score": total,
    }


def main():
    stocks = json.load(open(os.path.join(DATA, "stocks.json")))["aktien"]
    live = json.load(open(os.path.join(DATA, "live.json")))
    fx = live.get("markt", {}).get("fx") or {"CHF": 1.0}
    args = sys.argv[1:]
    path = os.path.join(DATA, "fcf.json")
    out = json.load(open(path)) if os.path.exists(path) else {"aktien": {}}
    only = set(a for a in args if not a.startswith("--"))
    if "--fehlende" in args:
        only = {s["ticker"] for s in stocks if s["ticker"] not in out["aktien"]}
        if not only:
            print("Alle Aktien haben schon FCF-Daten")
            return
    for s in stocks:
        if only and s["ticker"] not in only:
            continue
        try:
            ts = timeseries(s["symbol"])
            a = analyse(s["symbol"], ts, fx)
            if a:
                out["aktien"][s["ticker"]] = a
                print(s["ticker"], a["score"], a["p"], a["k"])
            else:
                print(s["ticker"], "zu wenig Daten", list(ts)[:5])
        except Exception as e:  # noqa
            print(s["ticker"], "FEHLER", e)
        time.sleep(0.6)
    out["stand"] = dt.date.today().isoformat()
    json.dump(out, open(path, "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
