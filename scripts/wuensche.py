"""Aktien-Wünsche aus der App einsammeln.

Die App schickt jeden Wunsch (z. B. "Adobe" oder "ADBE") als Nachricht an ein
ntfy-Thema. Dieses Skript holt die Nachrichten der letzten 13 Stunden ab und
trägt neue Wünsche in data/wuensche.json ein. Claude arbeitet die offenen
Wünsche einmal täglich ab (siehe pipeline/ANLEITUNG.md).

Aufruf:
  python scripts/wuensche.py                 Wünsche abholen
  python scripts/wuensche.py --melden "Text"  Push-Nachricht an Pascal (NTFY_TOPIC)
"""
import json, os, re, sys, time, datetime as dt
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "data", "wuensche.json")
TOPIC = "aa-wunsch-et886oec5xtc"
APP_URL = "https://pasidreamer.github.io/Aktien-Analyse/"
MAX_NEU_PRO_TAG = 5


def laden():
    if os.path.exists(PATH):
        return json.load(open(PATH))
    return {"wuensche": []}


def melden(text):
    topic = os.environ.get("NTFY_TOPIC")
    if not topic:
        print("Kein NTFY_TOPIC gesetzt")
        return
    req = urllib.request.Request(f"https://ntfy.sh/{topic}", data=text.encode("utf-8"), method="POST",
                                 headers={"Title": "Neue Analyse in der App", "Tags": "chart_with_upwards_trend", "Click": APP_URL})
    urllib.request.urlopen(req, timeout=20)
    print("gemeldet:", text)


def abholen():
    data = laden()
    w = data["wuensche"]
    vorher = len(w)
    ids = {x.get("id") for x in w}
    stocks = json.load(open(os.path.join(ROOT, "data", "stocks.json")))["aktien"]
    bekannt = {s["ticker"].lower() for s in stocks} | {s["symbol"].lower() for s in stocks} | {s["name"].lower() for s in stocks}
    heute = dt.date.today().isoformat()
    neu_heute = sum(1 for x in w if x.get("eingang", "").startswith(heute))
    url = f"https://ntfy.sh/{TOPIC}/json?poll=1&since=13h"
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "aktien-ampel"}), timeout=30) as r:
        lines = r.read().decode("utf-8").splitlines()
    neu = 0
    for line in lines:
        try:
            m = json.loads(line)
        except Exception:
            continue
        if m.get("event") != "message" or m.get("id") in ids:
            continue
        text = re.sub(r"[^\w .,&'()\-äöüÄÖÜéèàç]", "", (m.get("message") or "")).strip()[:60]
        if not text:
            continue
        offen = [x for x in w if x["status"] in ("offen", "in_arbeit") and x["text"].lower() == text.lower()]
        if offen:
            continue
        eintrag = {"id": m["id"], "text": text, "eingang": dt.datetime.utcfromtimestamp(m.get("time", time.time())).isoformat(timespec="minutes") + "Z"}
        if text.lower() in bekannt:
            eintrag.update(status="schon_da", hinweis="Diese Aktie ist schon in der App.")
        elif neu_heute + neu >= MAX_NEU_PRO_TAG:
            eintrag.update(status="abgelehnt", hinweis=f"Mehr als {MAX_NEU_PRO_TAG} Wünsche an einem Tag. Bitte morgen nochmals senden.")
        else:
            eintrag["status"] = "offen"
            neu += 1
        w.append(eintrag)
        ids.add(m["id"])
        print("Wunsch:", eintrag)
    if len(w) != vorher or not os.path.exists(PATH):
        data["wuensche"] = w[-100:]
        data["stand"] = dt.datetime.utcnow().isoformat(timespec="minutes") + "Z"
        json.dump(data, open(PATH, "w"), ensure_ascii=False, indent=1)
    print(neu, "neue Wünsche")


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--melden":
        melden(sys.argv[2])
    else:
        abholen()
