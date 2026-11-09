"""Instagram-Zugang testen, ohne etwas zu posten.

Prüft den Token (IG_TOKEN) und sucht die Konto-ID, die für das Posten nötig ist (IG_USER_ID).
Gibt nur IDs und Benutzernamen aus, nie den Token.

Aufruf: python scripts/verbindung_testen.py [weitere Kandidaten-IDs ...]
"""
import os, sys, urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from posten import IG_API, http, ohne_token

BUSINESS_ID = "1447604860076442"  # Business-Portfolio «Aktien-Ampel»
SEITE_ID = "1345119882027935"  # Facebook-Seite «Aktien-Ampel», verknüpft mit @aktienampel26


def abfragen(pfad, **felder):
    felder["access_token"] = os.environ["IG_TOKEN"]
    status, antwort = http("GET", f"{IG_API}/{pfad}?" + urllib.parse.urlencode(felder))
    print(ohne_token(f"GET {pfad} -> {status} {antwort}")[:600])
    return antwort if status == 200 and isinstance(antwort, dict) else None


def main():
    if not os.environ.get("IG_TOKEN"):
        print("IG_TOKEN fehlt.")
        return 1
    me = abfragen("me", fields="id,name")
    # Welche Rechte hat der Token, und für welche Konten (target_ids)?
    info = abfragen("debug_token", input_token=os.environ["IG_TOKEN"]) or {}
    ziele = [t for g in (info.get("data") or {}).get("granular_scopes", []) for t in g.get("target_ids", [])]
    # Instagram-Konto über die verknüpfte Facebook-Seite «Aktien-Ampel»
    seite = abfragen(SEITE_ID, fields="instagram_business_account{id,username}") or {}
    ziele += [(seite.get("instagram_business_account") or {}).get("id", "")]
    abfragen("me/accounts", fields="id,name,instagram_business_account")
    kandidaten = [os.environ.get("IG_USER_ID", "")] + ziele + sys.argv[1:]
    gefunden = None
    for k in filter(None, kandidaten):
        a = abfragen(k, fields="id,username")
        if a and a.get("username"):
            gefunden = a
    if gefunden:
        print(f"OK: Konto @{gefunden['username']} hat die ID {gefunden['id']}")
    return 0 if me and gefunden else 1


if __name__ == "__main__":
    sys.exit(main())
