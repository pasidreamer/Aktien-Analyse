"""Das Karussell von heute auf Instagram und TikTok posten.

Aufruf:
  python scripts/posten.py                 heute posten (Zeitzone Europe/Zurich)
  python scripts/posten.py --ab-7-uhr      nur posten, wenn es in Zürich zwischen 7 und 12 Uhr ist (für den Zeitplan)
  python scripts/posten.py --datum 2026-11-05 --trocken
                                           zeigt nur, was gesendet würde (prüft aber die Bilder im Netz)

Ablauf:
  1. Karussell von heute aus data/karussell/index.json holen und prüfen (Bilder erreichbar, Hinweis
     «keine Anlageberatung», höchstens 5 Hashtags, Offenlegung gesetzt). Fällt eine Prüfung durch,
     springt ein Reserve-Post aus karussell/reserve/ ein.
  2. Instagram: pro Bild ein Container, dann der Karussell-Container mit Caption, dann veröffentlichen.
  3. TikTok: Foto-Post über die Content Posting API (Entwurf im Posteingang oder Direkt-Post).
  4. Ergebnis in data/karussell/gepostet.json. Was dort für ein Datum steht, wird nie ein zweites Mal gepostet.
  5. Meldung per ntfy.

Umgebungsvariablen (GitHub-Secrets). Fehlt der Zugang einer Plattform, wird sie übersprungen:
  IG_USER_ID, IG_TOKEN                                      Instagram (Token des Systemnutzers, läuft nie ab)
  TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN
  TIKTOK_MODUS = entwurf (Standard) | direkt                direkt erst nach der TikTok-Prüfung
  GH_SECRETS_TOKEN                                          erlaubt, einen erneuerten TikTok-Token zu speichern
  NTFY_TOPIC
"""
import argparse, datetime as dt, json, os, re, subprocess, sys, time, urllib.error, urllib.parse, urllib.request
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASIS = "https://pasidreamer.github.io/Aktien-Analyse"
ZONE = ZoneInfo("Europe/Zurich")
IG_API = "https://graph.facebook.com/" + os.environ.get("IG_API_VERSION", "v25.0")  # Token des Systemnutzers (Meta Business)
TT_API = "https://open.tiktokapis.com/v2"
DISCLAIMER = "Persönliche Meinung, keine Anlageberatung. Mach deine eigene Recherche."
MAX_HASHTAGS = 5
FEED_FENSTER = 125  # so viele Zeichen zeigt Instagram vor «mehr»
LOG = os.path.join(ROOT, "data", "karussell", "gepostet.json")
TROCKEN = False


# ---------- Hilfen ----------

def http(methode, url, daten=None, json_body=None, kopf=None):
    """Kleiner HTTP-Aufruf ohne Fremdpakete. Gibt (status, json|text) zurück."""
    kopf = dict(kopf or {})
    body = None
    if json_body is not None:
        body = json.dumps(json_body).encode()
        kopf["Content-Type"] = "application/json; charset=UTF-8"
    elif daten is not None:
        body = urllib.parse.urlencode(daten).encode()
        kopf["Content-Type"] = "application/x-www-form-urlencoded"
    req = urllib.request.Request(url, data=body, headers=kopf, method=methode)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            roh, status, typ = r.read(), r.status, r.headers.get("Content-Type", "")
    except urllib.error.HTTPError as f:
        roh, status, typ = f.read(), f.code, f.headers.get("Content-Type", "")
    if "json" in typ:
        try:
            return status, json.loads(roh)
        except ValueError:
            pass
    return status, roh.decode("utf-8", "replace")[:500]


def ohne_token(text):
    """Zugangsdaten nie in Meldungen oder Logs schreiben."""
    for k in ("IG_TOKEN", "TIKTOK_CLIENT_SECRET", "TIKTOK_REFRESH_TOKEN"):
        v = os.environ.get(k)
        if v:
            text = text.replace(v, "***")
    return re.sub(r"access_token=[^&\s\"']+", "access_token=***", text)


def melden(titel, text, tags="camera"):
    print(f"[Meldung] {titel}: {text}")
    thema = os.environ.get("NTFY_TOPIC")
    if not thema or TROCKEN:
        return
    try:  # JSON-Variante, damit Umlaute im Titel ankommen
        http("POST", "https://ntfy.sh/", json_body={"topic": thema, "title": titel, "message": text, "tags": [tags],
                                                    "click": f"{BASIS}/#/karussell"})
    except Exception as f:  # Meldung darf das Posten nie verhindern
        print("ntfy fehlgeschlagen:", f)


def secret_speichern(name, wert):
    """Erneuerten Token als GitHub-Secret zurückschreiben (braucht GH_SECRETS_TOKEN)."""
    tok = os.environ.get("GH_SECRETS_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not tok or not repo:
        print(f"Hinweis: {name} wurde erneuert, kann aber nicht gespeichert werden (GH_SECRETS_TOKEN fehlt).")
        return False
    if TROCKEN:
        print(f"[trocken] würde Secret {name} speichern")
        return True
    r = subprocess.run(["gh", "secret", "set", name, "--repo", repo, "--body", wert],
                       env={**os.environ, "GH_TOKEN": tok}, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"Secret {name} speichern fehlgeschlagen:", r.stderr.strip())
    return r.returncode == 0


def log_laden():
    if os.path.exists(LOG):
        return json.load(open(LOG, encoding="utf-8"))
    return {"posts": {}, "reserve_benutzt": []}


def log_speichern(log):
    if TROCKEN:
        print("[trocken] gepostet.json bleibt unverändert")
        return
    json.dump(log, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


# ---------- Inhalt holen und prüfen ----------

def hashtags_kuerzen(caption):
    """Nur die ersten MAX_HASHTAGS Hashtags behalten."""
    gesehen = 0

    def ersetzen(m):
        nonlocal gesehen
        gesehen += 1
        return m.group(0) if gesehen <= MAX_HASHTAGS else ""
    neu = re.sub(r"(?<!\w)#[\wäöüÄÖÜß]+", ersetzen, caption)
    return re.sub(r"[ \t]+\n", "\n", re.sub(r"[ \t]{2,}", " ", neu)).strip()


def karussell_holen(datum):
    """Eintrag aus index.json plus die Inhaltsdatei (für eigene_position)."""
    idx = json.load(open(os.path.join(ROOT, "data", "karussell", "index.json"), encoding="utf-8"))
    eintrag = next((x for x in idx["karussells"] if x["datum"] == datum), None)
    if not eintrag:
        return None
    quelle = os.path.join(ROOT, "data", "karussell", f"{datum}.json")
    inhalt = json.load(open(quelle, encoding="utf-8")) if os.path.exists(quelle) else {}
    return {
        "art": "karussell", "datum": datum, "name": eintrag.get("name") or "", "titel": eintrag.get("titel") or "",
        "caption": eintrag.get("caption") or "", "bilder": int(eintrag.get("bilder") or 0),
        "ordner": f"karussell/{datum}", "eigene_position": inhalt.get("eigene_position", eintrag.get("eigene_position")),
    }


def reserve_holen(log, nur=None):
    """Nächster unbenutzter Reserve-Post aus karussell/reserve/<nr>/ (caption.txt, titel.txt, 1.jpg …).
    Mit nur=<nr> genau dieser, auch wenn er schon benutzt ist."""
    wurzel = os.path.join(ROOT, "karussell", "reserve")
    if not os.path.isdir(wurzel):
        return None
    for nr in sorted(os.listdir(wurzel)):
        ordner = os.path.join(wurzel, nr)
        if nur is not None and nr != nur:
            continue
        if (nur is None and nr in log.get("reserve_benutzt", [])) or not os.path.isfile(os.path.join(ordner, "caption.txt")):
            continue
        bilder = len([f for f in os.listdir(ordner) if re.fullmatch(r"\d+\.jpg", f)])
        titel_datei = os.path.join(ordner, "titel.txt")
        return {
            "art": "reserve", "nr": nr, "name": "Reserve " + nr, "bilder": bilder, "ordner": f"karussell/reserve/{nr}",
            "titel": open(titel_datei, encoding="utf-8").read().strip() if os.path.exists(titel_datei) else "Aktien-Ampel",
            "caption": open(os.path.join(ordner, "caption.txt"), encoding="utf-8").read().strip(),
            "eigene_position": False,
        }
    return None


def bild_urls(post):
    return [f"{BASIS}/{post['ordner']}/{i}.jpg" for i in range(1, post["bilder"] + 1)]


def pruefen(post, heute):
    """Gibt (fehler, warnungen) zurück. Bei Fehlern wird nicht gepostet."""
    fehler, warn = [], []
    if post["art"] == "karussell" and post["datum"] != heute:
        fehler.append(f"Karussell ist vom {post['datum']}, nicht von heute ({heute})")
    if not 2 <= post["bilder"] <= 10:
        fehler.append(f"{post['bilder']} Bilder (Instagram braucht 2 bis 10)")
    cap = post["caption"]
    if DISCLAIMER not in cap:
        fehler.append("Hinweis «keine Anlageberatung» fehlt in der Caption")
    if len(cap) > 2200:
        fehler.append(f"Caption hat {len(cap)} Zeichen (höchstens 2200)")
    if post["eigene_position"] is None:
        fehler.append("Feld eigene_position fehlt (Offenlegung unklar)")
    if post["eigene_position"] and "Ich halte diese Aktie" not in cap:
        fehler.append("Aktie liegt im Depot, aber die Offenlegung fehlt in der Caption")
    erster = cap.split("\n", 1)[0]
    if len(erster) > FEED_FENSTER:
        warn.append(f"Erste Zeile hat {len(erster)} Zeichen, der Feed zeigt nur {FEED_FENSTER}")
    fehlend = [url for url in bild_urls(post) if http("HEAD", url)[0] != 200]
    if fehlend:
        fehler.append(f"{len(fehlend)} von {post['bilder']} Bildern nicht erreichbar, z. B. {fehlend[0]}")
    return fehler, warn


# ---------- Instagram ----------

def ig_aufruf(methode, pfad, **daten):
    daten["access_token"] = os.environ["IG_TOKEN"]
    if methode == "GET":
        status, antwort = http("GET", f"{IG_API}/{pfad}?" + urllib.parse.urlencode(daten))
    else:
        status, antwort = http("POST", f"{IG_API}/{pfad}", daten=daten)
    if status != 200 or not isinstance(antwort, dict) or "error" in antwort:
        raise RuntimeError(ohne_token(f"Instagram {pfad}: {status} {antwort}"))
    return antwort


def ig_warten(container_id, versuche=30):
    for _ in range(versuche):
        status = ig_aufruf("GET", container_id, fields="status_code").get("status_code")
        if status == "FINISHED":
            return
        if status in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"Instagram-Container {container_id}: {status}")
        time.sleep(5)
    raise RuntimeError(f"Instagram-Container {container_id} nach {versuche * 5} s nicht fertig")


def instagram_posten(post):
    nutzer = os.environ["IG_USER_ID"]
    urls = bild_urls(post)
    if TROCKEN:
        print(f"[trocken] Instagram: {len(urls)} Bild-Container, dann Karussell mit {len(post['caption'])} Zeichen Caption")
        return "trocken"
    kinder = []
    for url in urls:
        kinder.append(ig_aufruf("POST", f"{nutzer}/media", image_url=url, is_carousel_item="true")["id"])
    for k in kinder:
        ig_warten(k)
    karussell = ig_aufruf("POST", f"{nutzer}/media", media_type="CAROUSEL", children=",".join(kinder),
                          caption=post["caption"])["id"]
    ig_warten(karussell)
    return ig_aufruf("POST", f"{nutzer}/media_publish", creation_id=karussell)["id"]


# ---------- TikTok ----------

def tiktok_token():
    """Kurzlebigen Zugang aus dem Refresh-Token holen. Ein neuer Refresh-Token wird gespeichert."""
    status, antwort = http("POST", f"{TT_API}/oauth/token/", daten={
        "client_key": os.environ["TIKTOK_CLIENT_KEY"], "client_secret": os.environ["TIKTOK_CLIENT_SECRET"],
        "grant_type": "refresh_token", "refresh_token": os.environ["TIKTOK_REFRESH_TOKEN"]})
    if status != 200 or not isinstance(antwort, dict) or not antwort.get("access_token"):
        raise RuntimeError(ohne_token(f"TikTok-Token: {status} {antwort}"))
    neu = antwort.get("refresh_token")
    if neu and neu != os.environ["TIKTOK_REFRESH_TOKEN"]:
        secret_speichern("TIKTOK_REFRESH_TOKEN", neu)
    return antwort["access_token"]


def tiktok_posten(post):
    direkt = os.environ.get("TIKTOK_MODUS", "entwurf") == "direkt"
    beschreibung = post["caption"][:4000]
    info = {"title": (post["titel"] or post["name"])[:90], "description": beschreibung}
    if direkt:
        info.update({"privacy_level": "PUBLIC_TO_EVERYONE", "disable_comment": False, "auto_add_music": True})
    body = {
        "post_info": info,
        "source_info": {"source": "PULL_FROM_URL", "photo_cover_index": 0, "photo_images": bild_urls(post)},
        "post_mode": "DIRECT_POST" if direkt else "MEDIA_UPLOAD",
        "media_type": "PHOTO",
    }
    if TROCKEN:
        print(f"[trocken] TikTok ({'Direkt-Post' if direkt else 'Entwurf'}): {len(body['source_info']['photo_images'])} Fotos, Titel «{info['title']}»")
        return "trocken"
    token = tiktok_token()
    status, antwort = http("POST", f"{TT_API}/post/publish/content/init/", json_body=body,
                           kopf={"Authorization": f"Bearer {token}"})
    fehler = (antwort.get("error") or {}) if isinstance(antwort, dict) else {}
    if status != 200 or fehler.get("code") not in (None, "ok"):
        raise RuntimeError(ohne_token(f"TikTok: {status} {antwort}"))
    return antwort["data"]["publish_id"]


# ---------- Ablauf ----------

NAMEN = {"instagram": "Instagram", "tiktok": "TikTok"}
PLATTFORMEN = {
    "instagram": (("IG_USER_ID", "IG_TOKEN"), instagram_posten),
    "tiktok": (("TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET", "TIKTOK_REFRESH_TOKEN"), tiktok_posten),
}


def main():
    global TROCKEN
    ap = argparse.ArgumentParser()
    ap.add_argument("--datum", help="JJJJ-MM-TT, Standard: heute in Zürich")
    ap.add_argument("--trocken", action="store_true")
    ap.add_argument("--ab-7-uhr", action="store_true")
    a = ap.parse_args()
    TROCKEN = a.trocken
    jetzt = dt.datetime.now(ZONE)
    if a.ab_7_uhr and not 7 <= jetzt.hour < 12:
        print(f"In Zürich ist es {jetzt:%H:%M}, gepostet wird zwischen 07:00 und 12:00. Nichts zu tun.")
        return 0
    heute = a.datum or jetzt.date().isoformat()
    log = log_laden()
    erledigt = log["posts"].setdefault(heute, {}) if not TROCKEN else dict(log["posts"].get(heute, {}))

    offen = [p for p, (keys, _) in PLATTFORMEN.items() if "id" not in erledigt.get(p, {})]
    if not offen:
        print(f"Für {heute} ist schon alles gepostet.")
        return 0
    eingerichtet = [p for p in offen if all(os.environ.get(k) for k in PLATTFORMEN[p][0])]
    if not eingerichtet and not TROCKEN:
        print("Noch keine Plattform eingerichtet (Secrets fehlen). Nichts zu tun.")
        return 0

    # Hat eine Plattform heute schon einen Reserve-Post bekommen, bekommen die übrigen denselben
    frueher = erledigt.get("quelle", "")
    if frueher.startswith("karussell/reserve/"):
        post = reserve_holen(log, nur=frueher.rsplit("/", 1)[1])
    else:
        post = karussell_holen(heute)
    fehler, warn = pruefen(post, heute) if post else ([f"Kein Inhalt für {heute} gefunden"], [])
    for w in warn:
        print("Warnung:", w)
    if fehler:
        print("Prüfung nicht bestanden:\n- " + "\n- ".join(fehler))
        if frueher:
            # Eine Plattform hat heute schon etwas: keinen anderen Inhalt nachschieben
            melden("Karussell: Posten abgebrochen", f"{heute}: " + "; ".join(fehler), "warning")
            return 1
        reserve = reserve_holen(log)
        if not reserve:
            melden("Karussell fällt heute aus", f"{heute}: " + "; ".join(fehler) + ". Kein Reserve-Post vorhanden.", "warning")
            return 1
        reserve_fehler, _ = pruefen(reserve, heute)
        if reserve_fehler:
            melden("Karussell fällt heute aus", f"{heute}: Auch der Reserve-Post {reserve['nr']} ist fehlerhaft: " + "; ".join(reserve_fehler), "warning")
            return 1
        print(f"Reserve-Post {reserve['nr']} springt ein.")
        grund = "; ".join(fehler)
        post = reserve
    else:
        grund = ""
    post["caption"] = hashtags_kuerzen(post["caption"])
    erledigt["quelle"] = post["ordner"]

    ergebnisse, probleme = [], []
    for plattform in offen:
        keys, funktion = PLATTFORMEN[plattform]
        if not all(os.environ.get(k) for k in keys):
            print(f"{plattform}: noch nicht eingerichtet, übersprungen.")
            continue
        try:
            pid = funktion(post)
            erledigt[plattform] = {"id": pid, "zeit": dt.datetime.now(ZONE).isoformat(timespec="seconds")}
            ergebnisse.append(plattform)
            print(f"{plattform}: gepostet ({pid})")
        except Exception as f:
            erledigt[plattform] = {"fehler": ohne_token(str(f))[:400], "zeit": dt.datetime.now(ZONE).isoformat(timespec="seconds")}
            probleme.append(f"{plattform}: {ohne_token(str(f))[:200]}")
            print(f"{plattform}: FEHLER {ohne_token(str(f))}")
        log_speichern(log)  # nach jeder Plattform sichern, damit ein Abbruch keinen Doppelpost auslöst

    if post["art"] == "reserve" and ergebnisse and not TROCKEN:
        log.setdefault("reserve_benutzt", []).append(post["nr"])
        log_speichern(log)

    teile = []
    if ergebnisse:
        teile.append(f"{post['name']} auf {' und '.join(NAMEN[x] for x in ergebnisse)} gepostet.")
    if grund:
        teile.append(f"Reserve, weil: {grund}.")
    if probleme:
        teile.append("Fehler: " + "; ".join(probleme))
    if teile:
        melden("Karussell gepostet" if ergebnisse and not probleme else "Karussell: Problem beim Posten",
               " ".join(teile), "camera" if not probleme else "warning")
    return 1 if probleme else 0


if __name__ == "__main__":
    sys.exit(main())
