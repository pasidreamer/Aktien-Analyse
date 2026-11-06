# Cowork-Auftrag: Tägliches Karussell für @aktienampel26

Diesen Text als Auftrag des geplanten Cowork-Tasks einsetzen (ersetzt den bisherigen).
**Zeitplan in Cowork: jeden Tag, auch Samstag und Sonntag, 05:30 Uhr.**

---

Erstelle das heutige Instagram-Karussell für den Account @aktienampel26 (Aktien-Ampel).
Es wird um 07:30 Uhr **automatisch und ohne Vorschau** gepostet. Arbeite deshalb sorgfältig und prüfe jede Zahl.

## 1. Thema wählen

Schau zuerst in `data/karussell/index.json` im Repo `pasidreamer/Aktien-Analyse`. Eine Aktie, die in den letzten 21 Tagen dran war, nimmst du nicht noch einmal.

- **Montag bis Freitag:**
  1. Hat gestern nach Börsenschluss oder heute vor Börsenbeginn eine bekannte Firma Quartalszahlen gemeldet (Watchlist oder grosse Namen aus S&P 500, SMI, DAX)? Dann diese Firma, `thema: "Quartalszahlen"`.
  2. Sonst: die grösste Tagesbewegung (mindestens ±5 %) unter den Aktien in `C:\Users\pasca\Documents\Aktienanalyse\register.json`, `thema: "Kursbewegung"`.
  3. Sonst: die nächste Aktie aus `register.json` (Kaufliste zuerst, dann die am längsten nicht geprüfte), `thema: "Ampel-Check"`.
- **Samstag:** Die Aktie aus `register.json` mit der grössten Wochenbewegung, `thema: "Wochenrückblick"`. Die Folie 1 greift die Bewegung der Woche auf.
- **Sonntag:** Eine Qualitätsaktie (Qualität mindestens 75) aus `register.json`, ruhig erklärt und ohne Tagesereignis, `thema: "Ampel-Check"`.

## 2. Analysieren

Wie bisher mit der Aktien-Ampel-Methode (Skill aktien-check):
- Qualität und Timing je 0–100
- Struktur im Wochenchart
- die entscheidende Marke mit den Szenarien «Bricht sie» und «Hält sie»

Zahlen nur aus Primärquellen (Quartalsbericht, Schlusskurs vom letzten Handelstag). Die Quelle kommt auf Folie 3 ins Feld `quelle`.

## 3. Inhaltsdatei schreiben

Datei `data/karussell/JJJJ-MM-TT.json`, Datum = **heute** (Zeitzone Zürich). Genau dieser Aufbau, 7 Folien in dieser Reihenfolge:

```json
{
 "datum": "2026-11-06", "ticker": "GOOGL", "name": "Alphabet", "thema": "Quartalszahlen",
 "stand": "05.11.2026",
 "slides": [
  {"typ": "hook", "kicker": "ALPHABET · QUARTALSZAHLEN", "titel": "...", "text": "...",
   "kpis": [{"label": "KURS", "wert": "279.84 $"}, {"label": "SEIT DEN ZAHLEN", "wert": "−13.9 %", "ton": "rot"}, {"label": "...", "wert": "..."}]},
  {"typ": "firma", "kicker": "WAS DIE FIRMA MACHT", "titel": "...", "text": "...", "fakten": [{"label": "Sitz", "wert": "..."}, {"label": "...", "wert": "..."}, {"label": "...", "wert": "..."}]},
  {"typ": "zahlen", "kicker": "WAS DIE ZAHLEN ZEIGEN", "titel": "...", "quelle": "Quelle: ...", "zeilen": [{"k": "Umsatz", "sub": "...", "wert": "+25 %", "ton": "gruen"}], "erklaerung": "..."},
  {"typ": "skala", "kicker": "AMPEL 1: QUALITÄT", "titel": "...", "name": "Qualität", "wert": 85, "punkte": ["...", "...", "..."]},
  {"typ": "skala", "kicker": "STRUKTUR IM WOCHENCHART", "titel": "...", "name": "Timing", "wert": 43, "punkte": ["...", "...", "..."]},
  {"typ": "marke", "kicker": "DIE ENTSCHEIDENDE MARKE", "titel": "...", "text": "...", "marke_label": "...", "marke": "270.70 $",
   "szenarien": [{"art": "bruch", "titel": "Bricht sie", "text": "..."}, {"art": "halten", "titel": "Hält sie", "text": "..."}]},
  {"typ": "fazit", "kicker": "MEIN FAZIT", "titel": "...", "absaetze": ["...", "..."], "frage": "... Deine Meinung in die Kommentare."}
 ],
 "caption": "...",
 "hashtags": ["#alphabet", "#aktien", "#börse", "#quartalszahlen", "#googl"]
}
```

**Regeln:**
- **Kein Feld `eigene_position` setzen:** Ob Pascal die Aktie hält, liest GitHub beim Rendern selbst aus dem Depot der App. Stückzahlen, Beträge und Kaufkurse kommen nie in die Texte.
- **ticker** genau so schreiben wie in der App (z. B. `GOOGL`, `NESN`), sonst klappt der Abgleich mit dem Depot nicht.
- **caption:** 2–4 Sätze. Der **erste Satz höchstens 120 Zeichen**, ein Aufhänger mit einer Zahl, denn so viel zeigt Instagram vor «mehr». **Ohne** Hinweis «keine Anlageberatung» und **ohne** Hashtags, die fügt der Generator selbst an.
- **hashtags:** **genau 5**, die wichtigsten zuerst: Firmenname, `#aktien`, `#börse`, das Thema, der Ticker.
- **ton** für Farben: `gruen`, `orange`, `rot` oder leer.
- **Titel** der Hook-Folie höchstens etwa 60 Zeichen.
- **Sprache:** Deutsch mit Schweizer Schreibweise (ss statt ß), Punkt als Dezimaltrenner, keine Gedankenstriche.
- **Inhalt:**
  - Keine Kauf- oder Verkaufsaufforderung.
  - «Mein Fazit» ist eine persönliche Einschätzung.
  - Am Schluss steht eine Frage an die Community.

## 4. Hochladen

Nur diese eine Datei auf dem gleichen Weg wie bisher in `main` von `pasidreamer/Aktien-Analyse` committen, mit der Nachricht `Karussell JJJJ-MM-TT: <Name>`.

Den Rest erledigt GitHub automatisch: Bilder rendern, Caption bauen, um 07:30 Uhr posten.

## 5. Im Zweifel nichts hochladen

Sind Zahlen widersprüchlich oder fehlen Daten, lieber **keine** Datei hochladen. Dann springt ein Reserve-Post ein, und Pascal bekommt eine Meldung.
