"""Holt die Firmenbeschreibung (englisch, von Yahoo) für alle Firmen im Scan.
Ergebnis: data/profile_en.json. Wird nicht veröffentlicht, nur als Vorlage für die
kurzen deutschen Beschreibungen in data/beschreibung.json.
Aufruf: python scripts/profile.py [--nur-neue]"""
import json, os, sys, time, urllib.parse
sys.path.insert(0, os.path.dirname(__file__))
import scan  # noqa: E402

DATA = os.path.join(os.path.dirname(__file__), "..", "data")


def profil(sym):
    c = scan.crumb()
    url = f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{urllib.parse.quote(sym)}?modules=assetProfile" + (f"&crumb={urllib.parse.quote(c)}" if c else "")
    j = json.loads(scan.get(url, 2))
    p = j["quoteSummary"]["result"][0].get("assetProfile") or {}
    return {"txt": p.get("longBusinessSummary") or "", "web": p.get("website") or "", "ma": p.get("fullTimeEmployees"),
            "ort": ", ".join(x for x in (p.get("city"), p.get("country")) if x), "branche": p.get("industry") or ""}


def main():
    sc = json.load(open(os.path.join(DATA, "scan.json")))["aktien"]
    alt = {}
    bes = os.path.join(DATA, "beschreibung.json")
    fertig = set(json.load(open(bes)).get("firmen", {})) if os.path.exists(bes) else set()
    syms = sorted(s for s in sc if not ("--nur-neue" in sys.argv and s in fertig))
    out, fehler = {}, {}
    for i, s in enumerate(syms):
        try:
            out[s] = {"n": sc[s].get("n"), **profil(s)}
        except Exception as e:  # noqa
            fehler[s] = str(e)[:100]
        time.sleep(0.3)
        if i % 50 == 0:
            print(i, len(syms), len(fehler), flush=True)
    json.dump({"anzahl": len(out), "fehler": fehler, "firmen": out}, open(os.path.join(DATA, "profile_en.json"), "w"), ensure_ascii=False)
    print("fertig", len(out), "fehler", len(fehler))


if __name__ == "__main__":
    main()
