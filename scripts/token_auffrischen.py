"""Zugänge für Instagram und TikTok prüfen und erneuern (läuft wöchentlich).

Instagram: Der Token des Systemnutzers läuft nie ab. Geprüft wird nur, ob er noch gilt
           (er kann in der Meta Business Suite widerrufen werden).
TikTok:    Der Refresh-Token gilt 365 Tage; jede Erneuerung kann einen neuen liefern,
           der als GitHub-Secret zurückgeschrieben wird (braucht GH_SECRETS_TOKEN).
"""
import os, sys, urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from posten import IG_API, http, melden, ohne_token, tiktok_token


def main():
    probleme = []
    if os.environ.get("IG_TOKEN"):
        status, antwort = http("GET", f"{IG_API}/me?" + urllib.parse.urlencode(
            {"fields": "id,name", "access_token": os.environ["IG_TOKEN"]}))
        if status == 200 and isinstance(antwort, dict) and antwort.get("id"):
            print("Instagram-Zugang gilt noch.")
        else:
            probleme.append(ohne_token(f"Instagram-Zugang ungültig: {status} {antwort}")[:200])
    if all(os.environ.get(k) for k in ("TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET", "TIKTOK_REFRESH_TOKEN")):
        try:
            tiktok_token()  # speichert einen neuen Refresh-Token selbst
            print("TikTok-Zugang geprüft und erneuert.")
        except Exception as f:
            probleme.append(ohne_token(str(f))[:200])
    if probleme:
        melden("Social-Media-Zugang: bitte prüfen", "; ".join(probleme), "warning")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
