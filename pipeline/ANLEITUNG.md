# Anleitung: Neue Aktie in die Aktien-Ampel aufnehmen

Diese Anleitung ist für Claude. Sie beschreibt Schritt für Schritt, wie eine neue Aktie
analysiert und in Pascals App (https://pasidreamer.github.io/Aktien-Analyse/) aufgenommen wird.
Sie gilt für Wünsche aus der App (data/wuensche.json) und für Aufträge im Chat.

Leser der Analysen: Pascal, Privatanleger in der Schweiz, Anfänger, handelt bei Saxo.

## Schreibregeln (immer)

- Deutsch mit Schweizer Schreibweise: kein ß, immer ss. Zahlen mit Punkt als Dezimalzeichen, Tausender mit ' (z. B. 13'600).
- Anfängerniveau. Jede Kennzahl erklären: was sie ist, was der konkrete Wert bedeutet, ob er gut oder schlecht ist.
- Keine Gedankenstriche als Satzzeichen, keine Floskeln, kurze Sätze, konkrete Zahlen mit Datum. Ehrlich und kritisch, nichts schönreden.
- Keine Kaufempfehlung. Immer «keine Anlageberatung».
- Dividende immer mit: Betrag, wie oft pro Jahr, wann (Ex-Tag und Zahltag), nach welchem System, in welcher Form (Währung, Quellensteuer).
- Nur Zahlen verwenden, die du gelesen oder selbst gerechnet hast. Quellen mit Datum nennen.

## Ablauf für jede neue Aktie

Arbeitsordner: das geklonte Repo (z. B. /home/claude/aktien-ampel). Alle Pfade unten sind relativ dazu.

1. **Symbol klären.** Firma und Yahoo-Symbol bestimmen (US ohne Endung, Schweiz `.SW`, London `.L`, Paris `.PA`,
   Xetra `.DE`, Mailand `.MI`, Amsterdam `.AS`). Bei Firmen mit US-Notierung (ADR) die US-Notierung nehmen,
   ausser es gibt einen guten Grund (z. B. Schweizer Firmen an der SIX). Ticker in der App = Symbol ohne Endung.
   Ist der Wunsch keine Aktie, unklar oder ein ETF ohne Firma dahinter: Wunsch auf `abgelehnt` setzen mit kurzem `hinweis`.
2. **Kursdaten holen** (der Container erreicht Yahoo nicht, darum über GitHub Actions):
   `gh api -X POST repos/pasidreamer/Aktien-Analyse/actions/workflows/rohdaten.yml/dispatches -f ref=main -f 'inputs[symbole]=SYMBOL1 SYMBOL2'`
   Warten, bis der Lauf fertig ist (`gh api 'repos/pasidreamer/Aktien-Analyse/actions/runs?per_page=3'`), dann `git pull`.
   Ergebnis: `pipeline/raw/TICKER_raw.txt` (W = Woche: Datum, Schluss, EMA50, EMA200, RSI, A/D; D = Tag: Datum, Hoch, Tief,
   Schluss, EMA50, EMA200, RSI, A/D; SWD/SWW = Swing-Hochs und -Tiefs; SEAS = Saisonalität). `python3 pipeline/check.py TICKER`
   prüft die Datei (FEHLER bei 8 Feldern pro Tageszeile ist harmlos, wenn die Prüfsummen gleich sind).
3. **Fundamentaldaten und News recherchieren** (WebSearch/WebFetch): stockanalysis.com
   (`/stocks/<ticker>/financials/`, `?p=quarterly`, `/financials/ratios/`, `/statistics/`, `/financials/cash-flow-statement/`),
   Firmenmeldungen, Reuters/CNBC, MarketBeat (Insider, Analysten). Warum steht der Kurs dort? Stimmung oder echtes Problem?
   Nächster Zahlen-Termin. Dividende mit Terminen.
4. **Punkte vergeben** strikt nach `pipeline/vorlage/bewertungsschema.md` (Qualität 8 Kriterien, Timing 7 Kriterien,
   immer in dieser Reihenfolge). Jede Punktzahl mit einem kurzen Satz begründen.
5. **Zonen bestimmen** aus den Swing-Daten: Struktur (höhere/tiefere Hochs und Tiefs), Kaufzone 1 und 2 (Unterstützungen,
   EMAs, Kurslücken), Trigger (Tagesschluss über dem letzten tieferen Hoch), Abbruch (Wochenschluss unter ...), Widerstände.
   Charts zeigen mindestens 1 Jahr.
6. **Konfiguration schreiben:** `pipeline/config/TICKER.json`. Vorlage: `pipeline/config/RACE.json` (gleiche Felder, gleiche
   Struktur). Am einfachsten mit einem kleinen Skript wie `pipeline/cfg/cfg_ADBE.py`, das die JSON-Datei schreibt.
   Hilfstexte für A/D, RSI und Saisonalität: `pipeline/helpers.py`. Wichtig:
   - `Q` und `T`: Listen [Name, Begründung, Punkte, Max] in der Reihenfolge des Schemas.
   - `kpis`: 8 Kacheln [Farbe g/w/r, Name, Wert, Erklärung], die letzte heisst «Dividende».
   - `FIN`: 5 Jahre plus «Letzte 12 Mt.» [Jahr, Umsatz, Wachstum, Marge, EPS, FCF, ROIC, KGV]. `QREV`: 8 Quartale.
   - `bands`/`refs`: Zonen für den Chart. `waehrung` (USD, CHF, EUR, GBp) und `land` setzen.
7. **Seite bauen:** `python3 pipeline/gen.py TICKER` schreibt `pipeline/seiten/TICKER_aktien-check.html`.
   Mit Playwright (Chromium unter /opt/pw-browsers/chromium) öffnen und prüfen: keine JS-Fehler, kein horizontales Scrollen.
8. **Veröffentlichen:** Seite mit dem Artifact-Tool veröffentlichen (Icon «chart», Titel steht in der Datei).
   Die Artifact-ID (letzter Teil der URL) merken. Bei einer bestehenden Aktie dieselbe Seite aktualisieren (ID steht in
   `pipeline/aktien.json`).
9. **In die App aufnehmen:**
   - `pipeline/aktien.json`: neuer Eintrag mit symbol, name, tags (Wachstum/Qualität/Dividende/Defensiv), land, region
     (USA/Europa/Schweiz/Asien), branche, status (`beobachten`), waehrung, kurs, datenstand (JJJJ-MM-TT), kauf, widerstand,
     trigger, abbruch, pe (KGV heute), pe_avg (eigener 5-Jahres-Schnitt), pe_typ («KGV» oder «KUV»), zahlen (JJJJ-MM-TT), artifact.
   - `pipeline/div_info.json`: Dividendenangaben (Vorlage: Eintrag RACE oder V). Zahlt die Firma keine Dividende:
     `{"zahlt": false, "text": "..."}`.
   - `pipeline/chance/TICKER.json`: Unterbewertung und Wachstumsschub nach `pipeline/chance/_auftrag.md`.
   - Neue Länder: in `app.js` bei `regionCode` ergänzen.
   - `python3 pipeline/build_data.py` schreibt `data/stocks.json` und `analysen/TICKER.html`.
10. **Wunsch abschliessen:** In `data/wuensche.json` beim Wunsch `status` auf `fertig` und `ticker` setzen.
11. **Hochladen:** `git add -A && git commit -m "..." && git pull --rebase && git push`. Der Push startet «App veröffentlichen»:
    Kurse, Ampeln und Free-Cashflow-Daten der neuen Aktie werden automatisch geholt.
12. **Pascal melden:**
    `gh api -X POST repos/pasidreamer/Aktien-Analyse/actions/workflows/wuensche.yml/dispatches -f ref=main -f 'inputs[melden]=Neu in der App: Adobe (ADBE). Qualität 70, Timing 40. Kaufzone 300–320 $.'`

## Tägliche Abarbeitung der Wünsche

1. Repo klonen oder aktualisieren, dann den Workflow «Aktien-Wünsche einsammeln» starten
   (`.../workflows/wuensche.yml/dispatches -f ref=main`), warten, `git pull`.
2. In `data/wuensche.json` alle Einträge mit `status: "offen"` nehmen (höchstens 3 pro Tag, älteste zuerst).
3. Für jeden Wunsch den Ablauf oben durchgehen. Mehrere Symbole kannst du in einem Rohdaten-Lauf holen.
4. Gibt es keine offenen Wünsche, nichts tun und kurz beenden.
