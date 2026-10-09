# Aktien-Ampel

Persönliche Watchlist als Web-App (läuft auf GitHub Pages, auf dem iPhone über «Zum Home-Bildschirm» installierbar).
Jede Aktie hat zwei Ampeln: **Qualität** (ist die Firma kaufenswert?) und **Timing** (ist jetzt der Zeitpunkt?).

## Was automatisch passiert

Die GitHub Action `Kurse aktualisieren` läuft Montag bis Freitag um 22:40 UTC (nach US-Börsenschluss):

1. `scripts/update.py` holt Tages-, Wochen- und Monatskurse von Yahoo Finance.
2. Daraus werden EMA 50/200, RSI 14 und A/D-Linie berechnet (gleiche Formeln wie in den Analysen).
3. Automatisch neu berechnet werden: Trend Woche, Trend Tag, RSI, A/D, Saisonalität (Timing) und die Bewertung (Qualität).
4. Kalibrierung: `heute = Analyse-Punkte + (Regel heute − Regel am Analysetag)`. Jede Aktie startet also exakt bei den Punkten der letzten Analyse.
5. Struktur (SMC) springt auf mindestens 16, wenn der Kurs über dem Trigger schliesst, und fällt auf 2, wenn ein Wochenschluss unter der Abbruch-Marke liegt.
6. Ergebnis: `data/live.json` (aktueller Stand) und `data/verlauf.json` (Verlauf der Ampeln), danach wird die Seite neu veröffentlicht.

Manuell starten: Reiter «Actions» → «Kurse aktualisieren» → «Run workflow».

## Eine Aktie hinzufügen oder nach neuer Analyse aktualisieren

1. Cheat Sheet als `analysen/<TICKER>.html` ablegen.
2. In `data/stocks.json` den Eintrag ergänzen oder ersetzen. Wichtige Felder:

| Feld | Bedeutung |
|---|---|
| `ticker`, `symbol` | Kürzel in der App und Yahoo-Symbol (z. B. `NESN.SW`, `ULVR.L`, `BN.PA`) |
| `tags` | Stil, erster Eintrag ist der Hauptstil: `Wachstum`, `Qualität`, `Dividende`, `Defensiv`, `ETF` |
| `land`, `region` | z. B. `USA`/`USA`, `Schweiz`/`Schweiz`, `Frankreich`/`Europa` |
| `status` | `depot`, `kaufliste`, `beobachten`, `archiv` |
| `waehrung` | `USD`, `CHF`, `EUR`, `GBp` (Pence) |
| `analyse` | `datenstand` (letzter Kurstag der Analyse), `kurs`, `q`, `t` |
| `qualitaet`, `timing` | Punkte pro Kriterium (`k`, `name`, `txt`, `p`, `max`, `auto`) |
| `bewertung` | `wert` (KGV oder KUV am Analysetag), `schnitt` (5-Jahres-Schnitt), `typ` |
| `zonen` | `kauf` und `widerstand` als `[[von, bis]]`, `trigger`, `abbruch` |
| `zahlen` | nächste Quartalszahlen als `JJJJ-MM-TT` |
| `fazit`, `kpis`, `pro`, `contra`, `zonen_text`, `smart_money` | Texte für die Detailansicht |
| `cheatsheet`, `claude` | Link zum Cheat Sheet und zur Analyse in Claude |

3. Hochladen. Die Action `App veröffentlichen` rechnet die Ampeln neu und stellt die Seite online.

## Hinweis

Persönliche Watchlist, keine Anlageberatung. Kursdaten von Yahoo Finance ohne Gewähr.
