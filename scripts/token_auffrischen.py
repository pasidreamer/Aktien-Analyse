"""Zugänge für Instagram und TikTok erneuern, bevor sie ablaufen (läuft wöchentlich).

Instagram: Der lange Token gilt 60 Tage und lässt sich ab einem Tag Alter um weitere 60 Tage verlängern.
TikTok:    Der Refresh-Token gilt 365 Tage; jede Erneuerung kann einen neuen liefern.
Beide werden als GitHub-Secrets zurückgeschrieben (braucht GH_SECRETS_TOKEN).
"""
import os, sys, urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from posten import IG_API, http, melden, ohne_token, secret_speichern, tiktok_token


def main():
    probleme = []
    if os.environ.get("IG_TOKEN"):
        url = IG_API.rsplit("/", 1)[0] + "/refresh_access_token?" + urllib.parse.urlencode(
            {"grant_type": "ig_refresh_token", "access_token": os.environ["IG_TOKEN"]})
        status, antwort = http("GET", url)
        if status == 200 and isinstance(antwort, dict) and antwort.get("access_token"):
            tage = int(antwort.get("expires_in", 0)) // 86400
            if not secret_speichern("IG_TOKEN", antwort["access_token"]):
                probleme.append("Instagram-Token erneuert, aber nicht gespeichert")
            print(f"Instagram-Token erneuert, gültig {tage} Tage.")
        else:
            probleme.append(ohne_token(f"Instagram: {status} {antwort}")[:200])
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
