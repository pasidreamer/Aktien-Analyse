"""Aktien-Universum für den Branchenvergleich und die Entdecken-Liste.

Liest die Mitglieder grosser Börsenindizes aus Wikipedia und macht daraus
Yahoo-Symbole. Ergebnis: data/universum.json und data/universum_bericht.json.

Stufe 1 (heute): grosse und mittlere Firmen aus USA, Schweiz, Europa, UK, Kanada.
Weitere Stufen werden einfach unten in INDIZES ergänzt.
"""
import io, json, os, re, sys, time, urllib.request

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
W = "https://en.wikipedia.org/wiki/"

# Name, Seite, Yahoo-Endung, Region, Land, erwartete Anzahl, Stufe
INDIZES = [
    ("S&P 500", W + "List_of_S%26P_500_companies", "", "USA", "USA", 500, 1),
    ("Nasdaq-100", W + "Nasdaq-100", "", "USA", "USA", 100, 1),
    ("S&P 400", W + "List_of_S%26P_400_companies", "", "USA", "USA", 400, 2),
    ("SMI", W + "Swiss_Market_Index", ".SW", "Schweiz", "Schweiz", 20, 1),
    ("SMIM", W + "SMI_MID", ".SW", "Schweiz", "Schweiz", 30, 1),
    ("DAX", W + "DAX", ".DE", "Europa", "Deutschland", 40, 1),
    ("MDAX", W + "MDAX", ".DE", "Europa", "Deutschland", 50, 1),
    ("FTSE 100", W + "FTSE_100_Index", ".L", "Europa", "Grossbritannien", 100, 1),
    ("FTSE 250", W + "FTSE_250_Index", ".L", "Europa", "Grossbritannien", 250, 2),
    ("CAC 40", W + "CAC_40", ".PA", "Europa", "Frankreich", 40, 1),
    ("AEX", W + "AEX_index", ".AS", "Europa", "Niederlande", 25, 1),
    ("BEL 20", W + "BEL_20", ".BR", "Europa", "Belgien", 20, 2),
    ("FTSE MIB", W + "FTSE_MIB", ".MI", "Europa", "Italien", 40, 1),
    ("IBEX 35", W + "IBEX_35", ".MC", "Europa", "Spanien", 35, 1),
    ("OMX Stockholm 30", W + "OMX_Stockholm_30", ".ST", "Europa", "Schweden", 30, 1),
    ("OMX Copenhagen 25", W + "OMX_Copenhagen_25", ".CO", "Europa", "Dänemark", 25, 1),
    ("OMX Helsinki 25", W + "OMX_Helsinki_25", ".HE", "Europa", "Finnland", 25, 2),
    ("OBX", W + "OBX_Index", ".OL", "Europa", "Norwegen", 25, 2),
    ("S&P/TSX 60", W + "S%26P/TSX_60", ".TO", "Kanada", "Kanada", 60, 1),
    ("Nikkei 225", W + "Nikkei_225", ".T", "Asien", "Japan", 225, 2),
    ("Hang Seng", W + "Hang_Seng_Index", ".HK", "Asien", "Hongkong/China", 88, 2),
    ("Straits Times", W + "Straits_Times_Index", ".SI", "Asien", "Singapur", 30, 2),
    ("S&P/ASX 200", W + "S%26P/ASX_200", ".AX", "Australien", "Australien", 200, 2),
]
# Grosse asiatische Firmen, die in den USA als ADR gehandelt werden (Taiwan, Korea, Indien, China ohne Hongkong-Listing)
ADR = [("TSM", "Taiwan"), ("UMC", "Taiwan"), ("ASX", "Taiwan"), ("CHT", "Taiwan"), ("KB", "Südkorea"), ("SHG", "Südkorea"), ("PKX", "Südkorea"),
       ("KEP", "Südkorea"), ("INFY", "Indien"), ("WIT", "Indien"), ("HDB", "Indien"), ("IBN", "Indien"), ("RDY", "Indien"), ("MMYT", "Indien"),
       ("PDD", "China"), ("BABA", "China"), ("JD", "China"), ("BIDU", "China"), ("NTES", "China"), ("TCOM", "China"), ("BEKE", "China"),
       ("YUMC", "China"), ("TME", "China"), ("LI", "China"), ("NIO", "China"), ("XPEV", "China"), ("BILI", "China"), ("ZTO", "China"),
       ("VIPS", "China"), ("HTHT", "China"), ("SE", "Singapur"), ("GRAB", "Singapur"), ("TLK", "Indonesien"), ("CPNG", "Südkorea")]
SUFFIXE = (".SW", ".DE", ".L", ".PA", ".AS", ".MI", ".MC", ".ST", ".CO", ".TO", ".HE", ".OL", ".BR", ".VI", ".T", ".HK", ".AX", ".SI")


def html(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read().decode("utf-8", "replace")


def flat(c):
    if isinstance(c, tuple):
        c = " ".join(str(x) for x in c if x and not str(x).startswith("Unnamed"))
    return str(c).strip().lower()


def pick(cols, words, avoid=()):
    for w in words:
        for c in cols:
            f = flat(c)
            if w in f and not any(a in f for a in avoid):
                return c
    return None


def clean(sym, suffix, land):
    s = str(sym).strip().upper()
    s = re.sub(r"\[.*?\]", "", s)
    s = re.sub(r"^(NYSE|NASDAQ|TSX|LSE|SIX|XETRA|EURONEXT|BIT|BME|SEHK|HKEX|SGX|ASX|TYO|TSE)\s*:\s*", "", s)
    s = s.split()[0] if s else s
    if not s or s in ("NAN", "—", "-"):
        return None
    if any(s.endswith(x) for x in SUFFIXE):
        return s
    if suffix == "":
        return s.replace(".", "-")
    if suffix == ".L":
        s = s.rstrip(".")
        return s.replace(".", "-") + ".L"
    if suffix == ".HK":
        return (s.zfill(4) if s.isdigit() else s) + ".HK"
    if suffix in (".T", ".AX", ".SI"):
        return s.split(".")[0] + suffix
    if suffix == ".TO":
        return s.replace(".", "-") + ".TO"
    if suffix in (".ST", ".CO"):
        return s.replace(" ", "-").replace(".", "-") + suffix
    return s.split(".")[0] + suffix


def nikkei(text):
    t = re.sub(r"<[^>]+>", "", text)
    rows = []
    for m in re.finditer(r"([^\n(]{2,80}?)\s*\(\s*TYO\s*:\s*([0-9A-Z]{4})\s*\)", t):
        rows.append({"symbol": m.group(2) + ".T", "name": m.group(1).strip(" •*-"), "sektor_quelle": None})
    return rows


DIAG = {}


def lese(name, url, suffix, region, land, n_soll):
    text = html(url)
    if name == "Nikkei 225":
        return nikkei(text)
    tabs = pd.read_html(io.StringIO(text))
    DIAG[name] = [[flat(c) for c in t.columns][:6] + [len(t)] for t in tabs[:12]]
    best = None
    for t in tabs:
        cols = list(t.columns)
        tc = pick(cols, ["ticker", "symbol", "epic", "code"], avoid=("isin",))
        if tc is None:
            continue
        nc = pick(cols, ["company", "security", "name", "constituent"], avoid=("ticker", "symbol"))
        sc = pick(cols, ["gics sector", "sector", "industry", "icb"])
        rows = []
        for _, r in t.iterrows():
            sym = clean(r[tc], suffix, land)
            if not sym or len(sym) > 14:
                continue
            rows.append({"symbol": sym, "name": str(r[nc]).strip() if nc is not None else sym,
                         "sektor_quelle": str(r[sc]).strip() if sc is not None else None})
        if len(rows) >= 0.5 * n_soll and (best is None or abs(len(rows) - n_soll) < abs(len(best) - n_soll)):
            best = rows
    return best or []


def main():
    stufe = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    alle, bericht = {}, []
    for name, url, suffix, region, land, n, st in INDIZES:
        if st > stufe:
            continue
        try:
            rows = lese(name, url, suffix, region, land, n)
        except Exception as e:  # noqa
            bericht.append({"index": name, "anzahl": 0, "fehler": str(e)[:200]})
            continue
        for r in rows:
            a = alle.setdefault(r["symbol"], {**r, "region": region, "land": land, "indizes": []})
            a["indizes"].append(name)
        bericht.append({"index": name, "anzahl": len(rows), "beispiele": [r["symbol"] for r in rows[:6]]})
        time.sleep(1)
    if stufe >= 2:
        for sym, land in ADR:
            alle.setdefault(sym, {"symbol": sym, "name": sym, "sektor_quelle": None, "region": "Asien", "land": land, "indizes": []})["indizes"].append("ADR Asien")
        bericht.append({"index": "ADR Asien", "anzahl": len(ADR)})
    out = {"stand": time.strftime("%Y-%m-%d"), "stufe": stufe, "anzahl": len(alle), "aktien": sorted(alle.values(), key=lambda x: x["symbol"])}
    json.dump(out, open(os.path.join(DATA, "universum.json"), "w"), ensure_ascii=False, indent=0)
    json.dump({"stand": out["stand"], "anzahl": len(alle), "indizes": bericht, "tabellen_leer": {k: v for k, v in DIAG.items() if not any(b["index"] == k and b["anzahl"] for b in bericht)}}, open(os.path.join(DATA, "universum_bericht.json"), "w"), ensure_ascii=False, indent=1)
    print(len(alle), "Aktien")
    for b in bericht:
        print(b)


if __name__ == "__main__":
    main()
