"""Scanner: Branchenvergleich, fairer Wert und automatische Hinweise.

Für jede Aktie aus data/universum.json plus alle Aktien der App:
  1. Kennzahlen aus Yahoo Finance (Jahreszahlen, Kurs 5 Jahre, Analysten)
  2. Vergleich mit allen Firmen derselben Branche (Perzentil 0 bis 100)
     in fünf Bereichen: Bewertung, Wachstum, Profitabilität, Cashflow und Bilanz, Kursmomentum.
     Jeder Bereich 0 bis 5 Punkte, dazu eine Gesamtnote (wie die «Financial Health» bei InvestingPro).
  3. Fairer Wert aus bis zu 6 Modellen (DCF, eigenes KGV, Branchen-KGV, Branchen-EV/EBITDA,
     Dividendenmodell, Buchwert bei Banken). Ergebnis = Median, dazu die Unsicherheit.
  4. Automatische Hinweise (positiv und negativ), ähnlich den «ProTips».

Aufruf:
  python scripts/scan.py --teil 0 --von 4     (holt die Daten für einen Teil, schreibt data/scan_teile/teil_0.json)
  python scripts/scan.py --zusammen          (rechnet Vergleich, fairen Wert und Hinweise, schreibt data/scan.json)
  python scripts/scan.py --nur AAPL NESN.SW   (Test für einzelne Symbole, holt und rechnet direkt)
"""
import json, math, os, sys, time, statistics as stx, datetime as dt
import urllib.request, urllib.parse, http.cookiejar

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
TEILE = os.path.join(DATA, "scan_teile")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"

TYPES = ["TotalRevenue", "GrossProfit", "OperatingIncome", "EBITDA", "NetIncomeCommonStockholders", "NetIncome", "DilutedEPS",
         "FreeCashFlow", "OperatingCashFlow", "TotalDebt", "CashCashEquivalentsAndShortTermInvestments", "CashAndCashEquivalents",
         "StockholdersEquity", "InvestedCapital", "TaxRateForCalcs", "DilutedAverageShares", "OrdinarySharesNumber",
         "CashDividendsPaid", "RepurchaseOfCapitalStock", "StockBasedCompensation"]
MODULES = "assetProfile,financialData,defaultKeyStatistics,summaryDetail,earningsTrend,price"

jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
CRUMB = None


def get(url, tries=3):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json,text/html"})
            with opener.open(req, timeout=30) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            last = e
            if e.code in (404,):
                break
            time.sleep(1.5 + i * 2.5)
        except Exception as e:  # noqa
            last = e
            time.sleep(1.5 + i * 2.5)
    raise RuntimeError(str(last)[:120])


def crumb():
    global CRUMB
    if CRUMB is None:
        try:
            get("https://fc.yahoo.com/", 1)
        except Exception:
            pass
        try:
            CRUMB = get("https://query2.finance.yahoo.com/v1/test/getcrumb").decode().strip()
        except Exception:
            CRUMB = ""
    return CRUMB


# ---------- Daten holen ----------
def chart(sym):
    j = json.loads(get(f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(sym)}?range=6y&interval=1wk&events=div"))
    res = j["chart"]["result"][0]
    q = res["indicators"]["quote"][0]
    rows = [(dt.datetime.utcfromtimestamp(t).date().isoformat(), c) for t, c in zip(res.get("timestamp") or [], q["close"]) if c]
    divs = sorted((dt.datetime.utcfromtimestamp(v["date"]).date().isoformat(), v["amount"]) for v in ((res.get("events") or {}).get("dividends") or {}).values() if v.get("amount"))
    return rows, divs, res["meta"]


def timeseries(sym):
    types = ",".join(p + t for p in ("annual", "trailing") for t in TYPES)
    q = {"symbol": sym, "type": types, "period1": 1420070400, "period2": int(time.time()), "merge": "false"}
    if crumb():
        q["crumb"] = crumb()
    j = json.loads(get(f"https://query2.finance.yahoo.com/ws/fundamentals-timeseries/v1/finance/timeseries/{urllib.parse.quote(sym)}?" + urllib.parse.urlencode(q)))
    out = {}
    for res in j["timeseries"]["result"]:
        key = res["meta"]["type"][0]
        vals = [v for v in (res.get(key) or []) if v and v.get("reportedValue")]
        out[key] = [(v["asOfDate"], v["reportedValue"]["raw"], v.get("currencyCode")) for v in vals]
    return out


def summary(sym):
    if not crumb():
        return {}
    url = f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{urllib.parse.quote(sym)}?modules={MODULES}&crumb={urllib.parse.quote(crumb())}"
    try:
        j = json.loads(get(url, 2))
        return j["quoteSummary"]["result"][0]
    except Exception:
        return {}


def raw(d, *path):
    for p in path:
        if not isinstance(d, dict):
            return None
        d = d.get(p)
    if isinstance(d, dict):
        return d.get("raw")
    return d


FX = {}


def fx(a, b):
    """Kurs von Währung a in Währung b (GBp wird als GBP/100 behandelt)."""
    if not a or not b:
        return None
    fa = 0.01 if a == "GBp" else 0.01 if a == "ZAc" else 1
    fb = 0.01 if b == "GBp" else 0.01 if b == "ZAc" else 1
    a2, b2 = {"GBp": "GBP", "ZAc": "ZAR"}.get(a, a), {"GBp": "GBP", "ZAc": "ZAR"}.get(b, b)
    if a2 == b2:
        return fa / fb
    k = a2 + b2
    if k not in FX:
        try:
            j = json.loads(get(f"https://query1.finance.yahoo.com/v8/finance/chart/{k}=X?range=5d&interval=1d"))
            FX[k] = j["chart"]["result"][0]["meta"]["regularMarketPrice"]
        except Exception:
            FX[k] = None
    return FX[k] * fa / fb if FX[k] else None


# ---------- Kennzahlen einer Aktie ----------
def ann(ts, name):
    rows = ts.get("annual" + name) or []
    return [(d, v) for d, v, _ in rows]


def ttm(ts, name):
    rows = ts.get("trailing" + name) or []
    return rows[-1][1] if rows else None


def last(series):
    return series[-1][1] if series else None


def cagr(a, b, n):
    if a is None or b is None or n <= 0 or a <= 0 or b <= 0:
        return None
    return ((b / a) ** (1 / n) - 1) * 100


def kennzahlen(sym, extra):
    rows, divs, meta = chart(sym)
    if len(rows) < 30:
        raise RuntimeError("zu wenig Kursdaten")
    ts = timeseries(sym)
    qs = summary(sym)
    pc = meta.get("currency")
    p = meta.get("regularMarketPrice") or rows[-1][1]
    fc = raw(qs, "financialData", "financialCurrency")
    if not fc:
        for v in ts.values():
            if v and v[-1][2]:
                fc = v[-1][2]
                break
    fc = fc or pc
    k = fx(fc, pc)  # Finanzzahlen -> Kurswährung
    if k is None:
        raise RuntimeError(f"kein Wechselkurs {fc}->{pc}")
    m = {"symbol": sym, "w": pc, "p": p, "name": raw(qs, "price", "longName") or raw(qs, "price", "shortName") or meta.get("longName") or meta.get("shortName") or extra.get("name"),
         "sektor": raw(qs, "assetProfile", "sector") or None, "branche": raw(qs, "assetProfile", "industry") or None,
         "land_y": raw(qs, "assetProfile", "country")}
    rev, op, gp = ann(ts, "TotalRevenue"), ann(ts, "OperatingIncome"), ann(ts, "GrossProfit")
    ni = ann(ts, "NetIncomeCommonStockholders") or ann(ts, "NetIncome")
    fcf, ebitda, eps = ann(ts, "FreeCashFlow"), ann(ts, "EBITDA"), ann(ts, "DilutedEPS")
    debt, eq, ic = ann(ts, "TotalDebt"), ann(ts, "StockholdersEquity"), ann(ts, "InvestedCapital")
    cash = ann(ts, "CashCashEquivalentsAndShortTermInvestments") or ann(ts, "CashAndCashEquivalents")
    sh_avg, sh_n, tax = ann(ts, "DilutedAverageShares"), ann(ts, "OrdinarySharesNumber"), ann(ts, "TaxRateForCalcs")
    buy, sbc = ann(ts, "RepurchaseOfCapitalStock"), ann(ts, "StockBasedCompensation")
    R = lambda s: ttm(ts, s)
    rev_t = R("TotalRevenue") or last(rev)
    op_t = R("OperatingIncome") or last(op)
    ni_t = R("NetIncomeCommonStockholders") or R("NetIncome") or last(ni)
    fcf_t = R("FreeCashFlow") or last(fcf)
    ebitda_t = R("EBITDA") or last(ebitda)
    gp_t = R("GrossProfit") or last(gp)
    mcap = raw(qs, "summaryDetail", "marketCap") or raw(qs, "price", "marketCap")
    shares_rep = last(sh_n) or last(sh_avg)
    if not mcap and shares_rep:
        mcap = p * shares_rep * k
    if not mcap:
        raise RuntimeError("kein Börsenwert")
    impl = mcap / p                      # Anzahl Handelseinheiten (ADR berücksichtigt)
    ratio = shares_rep / impl if shares_rep else 1
    if 0.8 < ratio < 1.25:
        ratio = 1
    m["mcap"] = mcap
    m["mcap_chf"] = mcap * (fx(pc, "CHF") or 0) or None
    nd = ((last(debt) or 0) - (last(cash) or 0)) * k
    m["nettoschulden"] = nd
    # Bewertung
    # Gewinn pro Handelseinheit immer selbst rechnen (gleiche Währung wie der Kurs, ADR berücksichtigt)
    eps_t = ni_t * k / impl if ni_t is not None else None
    ye_t, ye_f = raw(qs, "defaultKeyStatistics", "trailingEps"), raw(qs, "defaultKeyStatistics", "forwardEps")
    eps_f = eps_t * ye_f / ye_t if eps_t and eps_t > 0 and ye_t and ye_t > 0 and ye_f else None
    m["eps"], m["eps_f"] = eps_t, eps_f
    m["kgv"] = p / eps_t if eps_t and eps_t > 0 else None
    m["kgv_f"] = p / eps_f if eps_f and eps_f > 0 else None
    m["fcf_rendite"] = fcf_t * k / mcap * 100 if fcf_t is not None else None
    ev = mcap + nd
    m["ev_ebitda"] = ev / (ebitda_t * k) if ebitda_t and ebitda_t > 0 else None
    bv = last(eq)
    m["kbv"] = mcap / (bv * k) if bv and bv > 0 else None
    m["bvps"] = bv * k / impl if bv else None
    m["ebitda"] = ebitda_t * k if ebitda_t else None
    m["impl"] = impl
    # historisches KGV: Jahresend-Kurs / Gewinn pro Aktie des Geschäftsjahrs
    hist = []
    for d, e in eps[-6:]:
        if e and e > 0:
            px = [c for dd, c in rows if dd <= d]
            if px:
                v = px[-1] / (e * k * ratio)
                if 0 < v < 150:
                    hist.append(v)
    m["kgv_hist"] = stx.median(hist) if len(hist) >= 3 else None
    m["kgv_hist_n"] = len(hist)
    # Wachstum
    rv = [v for _, v in rev]
    m["umsatz_wachstum"] = (rv[-1] / rv[-2] - 1) * 100 if len(rv) >= 2 and rv[-2] > 0 else None
    m["umsatz_cagr3"] = cagr(rv[-4], rv[-1], 3) if len(rv) >= 4 else cagr(rv[0], rv[-1], len(rv) - 1) if len(rv) >= 2 else None
    m["umsatz_serie"] = sum(1 for a, b in zip(rv, rv[1:]) if b > a) if len(rv) >= 2 else None
    m["umsatz_steigt_jahre"] = next((i for i in range(len(rv) - 1) if not rv[-1 - i] > rv[-2 - i]), len(rv) - 1) if len(rv) >= 2 else 0
    ev_ = [v for _, v in eps]
    m["eps_cagr3"] = cagr(ev_[-4], ev_[-1], 3) if len(ev_) >= 4 else None
    fv_ = [v for _, v in fcf]
    m["fcf_cagr3"] = cagr(fv_[-4], fv_[-1], 3) if len(fv_) >= 4 else None
    m["eps_f_wachstum"] = (eps_f / eps_t - 1) * 100 if eps_f and eps_t and eps_t > 0 else None
    # Gewinnschätzungen: heute gegen vor 90 Tagen (laufendes Jahr)
    rev90 = g5 = None
    for t in (raw(qs, "earningsTrend", "trend") or []):
        if t.get("period") == "0y":
            cur_, old = raw(t, "epsTrend", "current"), raw(t, "epsTrend", "90daysAgo")
            if cur_ is not None and old and abs(old) > 1e-9:
                rev90 = (cur_ / old - 1) * 100 * (1 if old > 0 else -1)
        if t.get("period") in ("+1y",):
            g5 = raw(t, "growth")
    m["schaetzung_90t"] = rev90
    m["wachstum_naechstes_jahr"] = g5 * 100 if g5 is not None else None
    # Profitabilität
    m["bruttomarge"] = gp_t / rev_t * 100 if gp_t and rev_t else None
    m["op_marge"] = op_t / rev_t * 100 if op_t is not None and rev_t else None
    om = [(o / r * 100) for (_, o), (_, r) in zip(op[-3:], rev[-3:]) if r] if len(op) >= 3 and len(rev) >= 3 else []
    m["marge_trend"] = om[-1] - om[0] if len(om) == 3 else None
    m["marge_sinkt"] = len(om) == 3 and om[2] < om[1] < om[0]
    tr = last(tax)
    tr = tr if tr is not None and 0 <= tr <= 0.5 else 0.21
    icv = last(ic)
    m["roic"] = op_t * (1 - tr) / icv * 100 if op_t is not None and icv and icv > 0 else None
    m["roe"] = ni_t / bv * 100 if ni_t is not None and bv and bv > 0 else None
    m["verlust"] = ni_t is not None and ni_t < 0
    # Cashflow und Bilanz
    m["fcf_marge"] = fcf_t / rev_t * 100 if fcf_t is not None and rev_t else None
    m["fcf_deckung"] = fcf_t / ni_t if fcf_t is not None and ni_t and ni_t > 0 else None
    m["schulden_fcf"] = (nd / (fcf_t * k)) if fcf_t and fcf_t > 0 else None
    m["netto_cash"] = nd < 0
    m["fcf_neg_jahre"] = sum(1 for v in fv_[-5:] if v <= 0)
    sa = [v for _, v in sh_avg]
    m["aktien_pa"] = cagr(sa[-4], sa[-1], 3) if len(sa) >= 4 else cagr(sa[0], sa[-1], len(sa) - 1) if len(sa) >= 2 else None
    if m["aktien_pa"] is None and len(sa) >= 2 and sa[0] > 0:
        m["aktien_pa"] = ((sa[-1] / sa[0]) ** (1 / (len(sa) - 1)) - 1) * 100
    m["fcf"] = fcf_t * k if fcf_t is not None else None
    # Kursmomentum
    c = [x for _, x in rows]
    m["mom_12_1"] = (c[-5] / c[-53] - 1) * 100 if len(c) >= 53 else None
    m["mom_6"] = (c[-1] / c[-27] - 1) * 100 if len(c) >= 27 else None
    e = c[0]
    kk = 2 / 201
    for x in c:
        e = x * kk + e * (1 - kk)
    m["ema200w_abstand"] = (c[-1] / e - 1) * 100 if len(c) >= 150 else None
    hi52 = max(c[-52:])
    m["unter_hoch"] = (1 - c[-1] / hi52) * 100
    m["beta"] = raw(qs, "defaultKeyStatistics", "beta")
    # Dividende
    one_y = (dt.date.today() - dt.timedelta(days=365)).isoformat()
    d12 = sum(a for d, a in divs if d >= one_y)
    m["div_rendite"] = d12 / p * 100 if d12 else 0
    m["div_ps"] = d12
    jahr = {}
    for d, a in divs:
        jahr[int(d[:4])] = jahr.get(int(d[:4]), 0) + a
    y0 = dt.date.today().year - 1
    serie = 0
    while (y0 - serie) in jahr and (y0 - serie - 1) in jahr and jahr[y0 - serie] > jahr[y0 - serie - 1] * 1.001:
        serie += 1
    m["div_serie"] = serie
    m["div_cagr5"] = cagr(jahr.get(y0 - 5), jahr.get(y0), 5)
    m["ausschuettung"] = d12 / eps_t * 100 if d12 and eps_t and eps_t > 0 else None
    # Analysten
    z, zp = raw(qs, "financialData", "targetMeanPrice"), raw(qs, "financialData", "currentPrice")
    m["ziel"] = z * p / zp if z and zp else None
    m["ziel_n"] = raw(qs, "financialData", "numberOfAnalystOpinions")
    m["empfehlung"] = raw(qs, "financialData", "recommendationKey")
    # Datenqualität
    m["jahre"] = len(rev)
    return m


# ---------- Vergleich, fairer Wert, Hinweise ----------
BEREICHE = {
    "bewertung": [("ertragsrendite", 1), ("ertragsrendite_f", 1), ("fcf_rendite", 1), ("ebitda_rendite", 1)],
    "wachstum": [("umsatz_wachstum", 1), ("umsatz_cagr3", 1), ("eps_cagr3", 1), ("fcf_cagr3", 1), ("eps_f_wachstum", 1)],
    "profit": [("bruttomarge", 1), ("op_marge", 1), ("roic", 1), ("roe", 1), ("marge_trend", 1)],
    "cashflow": [("fcf_marge", 1), ("fcf_deckung_q", 1), ("schulden_fcf_q", -1), ("aktien_pa", -1), ("fcf_neg_jahre", -1)],
    "momentum": [("mom_12_1", 1), ("mom_6", 1), ("ema200w_abstand", 1), ("schaetzung_90t", 1)],
}
FIN_SEKTOREN = ("Financial Services", "Real Estate")


def abgeleitet(m):
    m["ertragsrendite"] = 100 / m["kgv"] if m.get("kgv") else (-5 if m.get("verlust") else None)
    m["ertragsrendite_f"] = 100 / m["kgv_f"] if m.get("kgv_f") else None
    m["ebitda_rendite"] = 100 / m["ev_ebitda"] if m.get("ev_ebitda") and m["ev_ebitda"] > 0 else None
    d = m.get("fcf_deckung")
    m["fcf_deckung_q"] = None if d is None else -abs(min(d, 2.5) - 1.1)
    s = m.get("schulden_fcf")
    m["schulden_fcf_q"] = -1 if m.get("netto_cash") else (s if s is not None else (12 if (m.get("nettoschulden") or 0) > 0 else None))
    if m.get("sektor") in FIN_SEKTOREN:
        for x in ("fcf_rendite", "ebitda_rendite", "fcf_marge", "fcf_deckung_q", "schulden_fcf_q", "fcf_cagr3", "fcf_neg_jahre", "bruttomarge", "roic"):
            m[x] = None


def perzentile(werte):
    """{symbol: wert} -> {symbol: perzentil 0..100}"""
    xs = sorted((v, s) for s, v in werte.items() if v is not None and not (isinstance(v, float) and math.isnan(v)))
    n = len(xs)
    out = {}
    if n < 2:
        return {s: 50.0 for _, s in xs}
    i = 0
    while i < n:
        j = i
        while j + 1 < n and xs[j + 1][0] == xs[i][0]:
            j += 1
        p = ((i + j) / 2) / (n - 1) * 100
        for t in range(i, j + 1):
            out[xs[t][1]] = p
        i = j + 1
    return out


def med(xs):
    xs = [x for x in xs if x is not None]
    return stx.median(xs) if xs else None


def fairer_wert(m, sek):
    p = m["p"]
    if not p:
        return None
    modelle = []
    beta = m.get("beta") or 1.0
    r = min(0.12, max(0.075, 0.045 + max(0.4, min(2.0, beta)) * 0.05))
    fin = m.get("sektor") in FIN_SEKTOREN
    # 1 DCF mit dem Free Cashflow (10 Jahre, dann ewiges Wachstum 2.5 %)
    if not fin and m.get("fcf") and m["fcf"] > 0 and m.get("impl"):
        f0 = m["fcf"] / m["impl"]
        gs = [x for x in (m.get("wachstum_naechstes_jahr"), m.get("umsatz_cagr3"), m.get("fcf_cagr3")) if x is not None]
        g1 = max(-2.0, min(18.0, med(gs) if gs else 4.0)) / 100
        v, f = 0, f0
        for t in range(1, 11):
            g = g1 if t <= 5 else g1 + (0.03 - g1) * (t - 5) / 5
            f *= 1 + g
            v += f / (1 + r) ** t
        v += f * 1.025 / (r - 0.025) / (1 + r) ** 10
        modelle.append(["DCF Free Cashflow", v, f"{nf(g1 * 100)} % Wachstum 5 Jahre, Abzinsung {nf(r * 100)} %"])
    # 2 eigenes historisches KGV
    if m.get("eps") and m["eps"] > 0 and m.get("kgv_hist"):
        modelle.append(["Eigenes KGV (5 Jahre)", m["eps"] * min(m["kgv_hist"], 60), f"KGV-Schnitt {nf(m['kgv_hist'])}"])
    # 3 Branchen-KGV (erwarteter Gewinn)
    e = m.get("eps_f") if m.get("eps_f") and m["eps_f"] > 0 else m.get("eps")
    if e and e > 0 and sek.get("kgv_f"):
        modelle.append(["Branchen-KGV", e * sek["kgv_f"], f"Branche {nf(sek['kgv_f'])}"])
    # 4 Branchen-EV/EBITDA
    if not fin and m.get("ebitda") and m["ebitda"] > 0 and sek.get("ev_ebitda") and m.get("impl"):
        v = (sek["ev_ebitda"] * m["ebitda"] - (m.get("nettoschulden") or 0)) / m["impl"]
        if v > 0:
            modelle.append(["Branchen-EV/EBITDA", v, f"Branche {nf(sek['ev_ebitda'])}"])
    # 5 Dividendenmodell
    if m.get("div_rendite", 0) >= 1 and (m.get("ausschuettung") or 999) < 100:
        gd = max(0.0, min(0.07, (m.get("div_cagr5") or 3) / 100))
        rr = max(r, gd + 0.03)
        modelle.append(["Dividendenmodell", m["div_ps"] * (1 + gd) / (rr - gd), f"Dividendenwachstum {nf(gd * 100)} %"])
    # 6 Buchwert (Banken, Versicherungen, Immobilien)
    if fin and m.get("bvps") and m["bvps"] > 0 and sek.get("kbv"):
        modelle.append(["Branchen-Kurs/Buchwert", m["bvps"] * sek["kbv"], f"Branche {nf(sek['kbv'])}"])
    ok = [x for x in modelle if 0.25 * p < x[1] < 4 * p]
    if len(ok) < 2:
        return {"modelle": [[a, round(b, 4), c] for a, b, c in modelle], "zu_wenig": True}
    w = stx.median([x[1] for x in ok])
    spread = (max(x[1] for x in ok) - min(x[1] for x in ok)) / w
    stufe = 0 if spread < 0.35 else 1 if spread < 0.7 else 2 if spread < 1.2 else 3
    if len(ok) == 2:
        stufe = min(3, stufe + 1)
    return {"wert": round(w, 4), "potenzial": round((w / p - 1) * 100, 1), "unsicher": ["niedrig", "mittel", "hoch", "sehr hoch"][stufe],
            "modelle": [[a, round(b, 4), c, 0.25 * p < b < 4 * p] for a, b, c in modelle]}


def nf(x, d=1):
    return f"{x:.{d}f}".replace(".", ",") if x is not None else "–"


def hinweise(m, rang, fv):
    h = []
    add = lambda art, txt, gewicht: h.append([art, txt, gewicht])
    if m.get("div_serie", 0) >= 5:
        add("g", f"Dividende {m['div_serie']} Jahre in Folge erhöht.", 3 + m["div_serie"] / 10)
    if m.get("aktien_pa") is not None and m["aktien_pa"] <= -1:
        add("g", f"Aktienzahl sinkt um {nf(-m['aktien_pa'])} % pro Jahr (Rückkäufe).", 2.5)
    if m.get("aktien_pa") is not None and m["aktien_pa"] >= 2:
        add("r", f"Aktienzahl steigt um {nf(m['aktien_pa'])} % pro Jahr: Dein Anteil wird kleiner.", 3)
    if m.get("netto_cash") and m.get("sektor") not in FIN_SEKTOREN:
        add("g", "Mehr Bargeld als Schulden.", 2)
    if m.get("schulden_fcf") is not None and m["schulden_fcf"] > 4:
        add("r", f"Nettoschulden entsprechen {nf(m['schulden_fcf'])} Jahren Free Cashflow.", 3)
    if m.get("fcf_rendite") is not None and m["fcf_rendite"] >= 5 and m.get("sektor") not in FIN_SEKTOREN:
        add("g", f"Free-Cashflow-Rendite {nf(m['fcf_rendite'])} % (günstig).", 2.5)
    if m.get("kgv") and m.get("kgv_hist") and m["kgv"] < 0.8 * m["kgv_hist"]:
        add("g", f"KGV {nf(m['kgv'])} liegt {nf((1 - m['kgv'] / m['kgv_hist']) * 100, 0)} % unter dem eigenen Schnitt ({nf(m['kgv_hist'])}).", 3)
    if m.get("kgv") and m.get("kgv_hist") and m["kgv"] > 1.3 * m["kgv_hist"]:
        add("r", f"KGV {nf(m['kgv'])} liegt {nf((m['kgv'] / m['kgv_hist'] - 1) * 100, 0)} % über dem eigenen Schnitt ({nf(m['kgv_hist'])}).", 2)
    if m.get("umsatz_steigt_jahre", 0) >= 4:
        add("g", f"Umsatz {m['umsatz_steigt_jahre']} Jahre in Folge gestiegen.", 2)
    if m.get("umsatz_wachstum") is not None and m["umsatz_wachstum"] < -3:
        add("r", f"Umsatz im letzten Geschäftsjahr {nf(m['umsatz_wachstum'])} %.", 3)
    if m.get("schaetzung_90t") is not None and m["schaetzung_90t"] >= 3:
        add("g", f"Analysten haben die Gewinnschätzung fürs laufende Jahr in 90 Tagen um {nf(m['schaetzung_90t'])} % erhöht.", 3.5)
    if m.get("schaetzung_90t") is not None and m["schaetzung_90t"] <= -3:
        add("r", f"Analysten haben die Gewinnschätzung fürs laufende Jahr in 90 Tagen um {nf(-m['schaetzung_90t'])} % gesenkt.", 4)
    if m.get("marge_sinkt"):
        add("r", "Die operative Marge sinkt seit zwei Jahren.", 3)
    if m.get("verlust"):
        add("r", "Verlust in den letzten 12 Monaten.", 4)
    if m.get("ausschuettung") and m["ausschuettung"] > 100:
        add("r", f"Die Dividende ist höher als der Gewinn ({nf(m['ausschuettung'], 0)} % Ausschüttung).", 3)
    if (m.get("unter_hoch") or 0) >= 30 and (m.get("ema200w_abstand") or 0) < 0:
        add("r", f"{nf(m['unter_hoch'], 0)} % unter dem Jahreshoch und unter der Wochen-EMA 200 (Abwärtstrend).", 2.5)
    if rang.get("profit") is not None and rang["profit"] >= 90:
        add("g", "Profitabilität unter den besten 10 % der Branche.", 2.5)
    if rang.get("wachstum") is not None and rang["wachstum"] >= 90:
        add("g", "Wachstum unter den besten 10 % der Branche.", 2.5)
    if m.get("ziel") and m.get("ziel_n") and m["ziel_n"] >= 5:
        pot = (m["ziel"] / m["p"] - 1) * 100
        if pot >= 20:
            add("g", f"Analysten-Kursziel {nf(pot, 0)} % über dem Kurs ({m['ziel_n']} Analysten).", 1.5)
        elif pot <= -5:
            add("r", f"Analysten-Kursziel {nf(-pot, 0)} % unter dem Kurs ({m['ziel_n']} Analysten).", 2)
    if fv and fv.get("potenzial") is not None and fv["unsicher"] in ("niedrig", "mittel"):
        if fv["potenzial"] >= 25:
            add("g", f"Fairer Wert {nf(fv['potenzial'], 0)} % über dem Kurs (Unsicherheit {fv['unsicher']}).", 2.5)
        elif fv["potenzial"] <= -25:
            add("r", f"Fairer Wert {nf(-fv['potenzial'], 0)} % unter dem Kurs (Unsicherheit {fv['unsicher']}).", 2.5)
    h.sort(key=lambda x: -x[2])
    return [[a, t] for a, t, _ in h[:8]]


def zusammen(teile):
    alle = {}
    for t in teile:
        alle.update(t["aktien"])
    fehler = {s: x["fehler"] for t in teile for s, x in t.get("fehler", {}).items()}
    for m in alle.values():
        m["sektor"] = m.get("sektor") or SEKTOR_MAP.get((m.get("sektor_quelle") or "").strip()) or "Andere"
        abgeleitet(m)
    # Branchen-Gruppen (kleine Gruppen mit der ganzen Liste vergleichen)
    gruppen = {}
    for s, m in alle.items():
        gruppen.setdefault(m["sektor"], []).append(s)
    sek_info = {}
    raenge = {s: {} for s in alle}
    for sek, syms in gruppen.items():
        basis = syms if len(syms) >= 12 else list(alle)
        sek_info[sek] = {"n": len(syms),
                         "kgv_f": med([alle[s].get("kgv_f") for s in basis if alle[s].get("kgv_f") and alle[s]["kgv_f"] < 80]),
                         "kgv": med([alle[s].get("kgv") for s in basis if alle[s].get("kgv") and alle[s]["kgv"] < 80]),
                         "ev_ebitda": med([alle[s].get("ev_ebitda") for s in basis if alle[s].get("ev_ebitda") and 0 < alle[s]["ev_ebitda"] < 60]),
                         "kbv": med([alle[s].get("kbv") for s in basis if alle[s].get("kbv") and alle[s]["kbv"] < 20]),
                         "fcf_rendite": med([alle[s].get("fcf_rendite") for s in basis]),
                         "op_marge": med([alle[s].get("op_marge") for s in basis]),
                         "umsatz_wachstum": med([alle[s].get("umsatz_wachstum") for s in basis])}
        for ber, metr in BEREICHE.items():
            teil = {s: [] for s in syms}
            for key, richtung in metr:
                pz = perzentile({s: (alle[s].get(key) * richtung if alle[s].get(key) is not None else None) for s in basis})
                for s in syms:
                    if s in pz:
                        teil[s].append(pz[s])
            for s in syms:
                raenge[s][ber] = round(sum(teil[s]) / len(teil[s]), 1) if len(teil[s]) >= 2 else None
    out = {}
    for s, m in alle.items():
        rg = raenge[s]
        noten = {b: (round(rg[b] / 20, 1) if rg.get(b) is not None else None) for b in BEREICHE}
        vorh = [v for v in noten.values() if v is not None]
        gesamt = round(sum(vorh) / len(vorh), 2) if len(vorh) >= 3 else None
        fv = fairer_wert(m, sek_info.get(m["sektor"], {}))
        r1 = lambda x, d=1: None if x is None or isinstance(x, bool) or not math.isfinite(x) else round(x, d)
        out[s] = {
            "n": m.get("name"), "sym": s, "app": m.get("app"), "sek": m["sektor"], "br": m.get("branche"), "land": m.get("land"), "reg": m.get("region"),
            "idx": m.get("indizes", []), "w": m["w"], "p": r1(m["p"], 4), "mc": r1((m.get("mcap_chf") or 0) / 1e9, 1),
            "g": gesamt, "k": noten, "rg": rg,
            "fv": fv, "an": {"ziel": r1(m.get("ziel"), 2), "n": m.get("ziel_n"), "e": m.get("empfehlung")},
            "h": hinweise(m, rg, fv),
            "d": {x: r1(m.get(x)) for x in ("kgv", "kgv_f", "kgv_hist", "ev_ebitda", "kbv", "fcf_rendite", "div_rendite", "div_serie", "ausschuettung",
                                            "umsatz_wachstum", "umsatz_cagr3", "eps_cagr3", "fcf_cagr3", "eps_f_wachstum", "bruttomarge", "op_marge",
                                            "roic", "roe", "fcf_marge", "schulden_fcf", "aktien_pa", "mom_12_1", "mom_6", "unter_hoch", "schaetzung_90t", "beta")},
        }
        out[s]["d"]["netto_cash"] = bool(m.get("netto_cash"))
    # Gesamt-Rang innerhalb der Branche
    for sek, syms in gruppen.items():
        pz = perzentile({s: out[s]["g"] for s in syms})
        for s in syms:
            out[s]["grang"] = round(pz[s]) if s in pz else None
            out[s]["gn"] = len([x for x in syms if out[x]["g"] is not None])
    return out, sek_info, fehler


SEKTOR_MAP = {  # GICS (Wikipedia) -> Yahoo-Sektoren
    "Information Technology": "Technology", "Health Care": "Healthcare", "Financials": "Financial Services",
    "Consumer Discretionary": "Consumer Cyclical", "Consumer Staples": "Consumer Defensive", "Industrials": "Industrials",
    "Energy": "Energy", "Materials": "Basic Materials", "Communication Services": "Communication Services",
    "Utilities": "Utilities", "Real Estate": "Real Estate"}


def liste():
    u = json.load(open(os.path.join(DATA, "universum.json")))["aktien"] if os.path.exists(os.path.join(DATA, "universum.json")) else []
    alle = {x["symbol"]: dict(x) for x in u}
    st = json.load(open(os.path.join(DATA, "stocks.json")))["aktien"]
    for s in st:
        a = alle.setdefault(s["symbol"], {"symbol": s["symbol"], "name": s["name"], "region": s.get("region"), "land": s.get("land"), "indizes": []})
        a["app"] = s["ticker"]
    return [alle[k] for k in sorted(alle)]


def hole(items):
    aktien, fehler = {}, {}
    for i, x in enumerate(items):
        try:
            m = kennzahlen(x["symbol"], x)
            m.update({k: x.get(k) for k in ("app", "region", "land", "indizes", "sektor_quelle")})
            aktien[x["symbol"]] = m
        except Exception as e:  # noqa
            fehler[x["symbol"]] = {"fehler": str(e)[:150]}
        time.sleep(0.35)
        if i % 25 == 0:
            print(i, len(items), len(fehler), flush=True)
    return {"aktien": aktien, "fehler": fehler}


def main():
    a = sys.argv[1:]
    if "--teil" in a:
        i, n = int(a[a.index("--teil") + 1]), int(a[a.index("--von") + 1])
        items = liste()[i::n]
        os.makedirs(TEILE, exist_ok=True)
        r = hole(items)
        json.dump(r, open(os.path.join(TEILE, f"teil_{i}.json"), "w"), ensure_ascii=False)
        print("fertig", len(r["aktien"]), "fehler", len(r["fehler"]))
        return
    if "--nur" in a:
        syms = a[a.index("--nur") + 1:]
        teile = [hole([{"symbol": s, "indizes": []} for s in syms])]
    else:
        teile = [json.load(open(os.path.join(TEILE, f))) for f in sorted(os.listdir(TEILE)) if f.endswith(".json")]
    out, sek, fehler = zusammen(teile)
    res = {"stand": dt.date.today().isoformat(), "anzahl": len(out), "sektoren": sek, "aktien": out}
    json.dump(res, open(os.path.join(DATA, "scan.json"), "w"), ensure_ascii=False, separators=(",", ":"))
    json.dump({"stand": res["stand"], "anzahl": len(out), "fehler_anzahl": len(fehler), "fehler": fehler,
               "ohne_note": [s for s, x in out.items() if x["g"] is None],
               "ohne_fv": [s for s, x in out.items() if not (x["fv"] or {}).get("wert")],
               "sektoren": {k: v["n"] for k, v in sek.items()}}, open(os.path.join(DATA, "scan_bericht.json"), "w"), ensure_ascii=False, indent=1)
    print(len(out), "Aktien,", len(fehler), "Fehler")


if __name__ == "__main__":
    main()
