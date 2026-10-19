# Marktsymmetrie-Indikator für TradingView

Datei: [`marktsymmetrie.pine`](marktsymmetrie.pine) (Pine Script v6)

## Idee

Gesunde Trends laufen symmetrisch: Rücksetzer sind ungefähr gleich tief und gleich lang wie der letzte Rücksetzer, Anstiege ungefähr gleich gross wie der letzte Anstieg.
Der Indikator vergleicht deshalb jeden Kursschwung mit dem **letzten Schwung in die gleiche Richtung**, beim Preis und bei der Zeit, und zeichnet die Zone, in der der aktuelle Schwung symmetrisch enden würde.

- **Korrektur endet in der Symmetrie-Zone (Preis + Zeit):** möglicher Wendepunkt. Im Aufwärtstrend lohnt es sich, dort die Kaufzone und den Trigger zu prüfen.
- **Korrektur wird deutlich grösser als die letzte:** Symmetrie gebrochen, Warnung für den Trend.
- **Korrektur dauert gleich lang, ist aber flacher:** Zeichen von Stärke.
- **Bullen/Bären-Bilanz:** Sind die Anstiege im Schnitt grösser als die Rückgänge, dominieren die Käufer (asymmetrischer Markt nach oben) und umgekehrt.

## Korrektur-Filter: überhitzt oder schöne Korrektur?

Aktien am Allzeithoch, die überhitzt sind, sind uninteressant. Spannend sind schöne Korrekturen wie bei Google 2022/23.
Der Indikator bewertet das mit zwei Punkteskalen und fasst es in der Tabelle als **Fazit** zusammen.

**Überhitzung (0–100)**, je 25 Punkte:

| Teil | Volle Punkte bei |
|---|---|
| RSI 14 | 78 oder höher (ab 60 steigend) |
| Abstand über EMA 50 | 15 % oder mehr (ab 5 %) |
| Abstand über EMA 200 | 40 % oder mehr (ab 15 %) |
| Nähe zum Allzeithoch | weniger als 2 % darunter (ab 10 %) |

Ab **70 Punkten** gilt die Aktie als überhitzt: roter Hintergrund, Markierung «heiss», Fazit «nicht hinterherlaufen». Die Korrektur-Chance wird dann auf höchstens 20 begrenzt.

**Korrektur-Chance (0–100)**, je 25 Punkte:

| Teil | Volle Punkte bei |
|---|---|
| Tiefe | Rücksetzer vom 52-Wochen-Hoch zwischen 10 % und 45 % (einstellbar) |
| Abgekühlt | RSI war in den letzten 20 Kerzen bei 35 oder tiefer |
| Symmetrie | Die Korrektur ist so gross wie die letzte Korrektur (reif) |
| Wende | Höheres Tief bestätigt und Kurs darüber (15) plus Schluss über EMA 20 (10) |

Ohne echten Rücksetzer (unter 10 %) oder ohne abgekühlten RSI bleibt die Chance bei höchstens 40, also «beobachten».
Ab **60 Punkten** ist die Korrektur spannend: grüner Hintergrund.

| Markierung | Bedeutung |
|---|---|
| Kreis «Korrektur» (orange) | Eine schöne Korrektur beginnt, die Wende ist noch offen. Beobachten und den Trigger abwarten |
| Dreieck «Wende» (grün) | Schöne Korrektur und höheres Tief bestätigt. Setup prüfen (Kaufzone, Fundamentaldaten) |
| Kreuz «heiss» (rot) | Überhitzt am Hoch |

**Trigger** in der Tabelle ist das letzte bestätigte Hoch. Ein Schluss darüber bestätigt die Wende.
Mitten in einer langen Korrektur kann «Wende» auch mal ein Fehlstart sein (Zwischenerholung). Deshalb erst mit Trigger handeln.

Fällt eine Aktie deutlich tiefer als die eingestellte Grenze (Standard 45 % + 10 %), steht im Fazit «Sehr tiefer Absturz – Firma genau prüfen».
Ob die Firma gut ist, kann der Indikator nicht sehen. Das bleibt beim Aktien-Check (Qualitäts-Ampel).

## Einrichten

1. In TradingView unten den **Pine-Editor** öffnen.
2. Inhalt von `marktsymmetrie.pine` komplett hineinkopieren (vorhandenen Code ersetzen).
3. **Speichern** und **Zum Chart hinzufügen**.
4. Optional: Über das Zahnrad die Einstellungen anpassen und unter «Vorlage speichern» als Standard sichern.

## Was im Chart erscheint

| Element | Bedeutung |
|---|---|
| Zickzack-Linien | Die erkannten Schwünge, grün aufwärts, rot abwärts |
| Beschriftung am Wendepunkt | Grösse in % und Länge in Kerzen (K), dazu **Symmetrie 0–100** im Vergleich zum letzten gleichen Schwung |
| Orange Box | **Symmetrie-Zone**: dort wäre der aktuelle Schwung so gross und so lang wie der letzte gleiche Schwung (± Toleranz) |
| Gepunktete Linie | Genaues Symmetrie-Ziel (100 %) |
| Tabelle | Trend, aktueller und letzter gleicher Schwung, Fortschritt Preis/Zeit, Ziel, Zeitziel, Status in Worten, Bullen/Bären-Bilanz |

Symmetrie-Wert: **70 oder mehr** = symmetrisch, **40–69** = teilweise, **unter 40** = asymmetrisch.
Fortschritt 100 % / 100 % heisst: der aktuelle Schwung ist genau so weit und so lang gelaufen wie der letzte gleiche Schwung.

## Einstellungen

| Einstellung | Standard | Hinweis |
|---|---|---|
| Pivot-Länge | 10 | Tageschart 8–12, Wochenchart 4–6. Grösser = nur grosse Schwünge |
| In Prozent rechnen | an | Für Aktien sinnvoll, aus = Kurspunkte |
| Toleranz der Symmetrie-Zone | 15 % | Breite der Zone in Preis und Zeit |
| Schwünge für die Bilanz | 6 | Wie viele der letzten Schwünge in die Bullen/Bären-Bilanz eingehen |
| Spannend ab Rücksetzer von | 10 % | Ab diesem Abstand zum 52-Wochen-Hoch zählt eine Korrektur |
| Normale Korrektur bis | 45 % | Tiefer wird es kritisch (Google 2022: rund 45 %) |
| Korrektur-Chance ab | 60 | Ab hier grüner Hintergrund |
| Überhitzt ab | 70 | Ab hier roter Hintergrund |
| Tabelle kompakt | aus | An = nur Fazit, Punkte, Abstand zum Hoch, RSI und Trigger (gut fürs Handy) |

## Alarme

Rechtsklick im Chart → «Alarm hinzufügen» → Bedingung «Marktsymmetrie» und dann:

- **Wende nach Korrektur** – schöne Korrektur und höheres Tief bestätigt (das wichtigste Signal)
- **Korrektur-Chance** – deutlicher Rücksetzer und RSI abgekühlt
- **Überhitzt** – am Hoch überhitzt, nicht hinterherlaufen
- **Symmetrie-Zone erreicht** – Preis und Zeit sind symmetrisch
- **Preis-Symmetrie erreicht** – der Schwung ist so gross wie der letzte gleiche
- **Symmetrie gebrochen** – der Schwung ist deutlich grösser als der letzte gleiche

## Wichtig zu wissen

- Ein Wendepunkt ist erst **Pivot-Länge Kerzen später** bestätigt. Der letzte Schwung im Chart kann sich deshalb noch verschieben.
- Sehr kleine Vergleichsschwünge führen zu grossen Prozentwerten beim Fortschritt. Dann hilft eine grössere Pivot-Länge.
- Korrektur-Chance, Überhitzung und Abstand zum 52-Wochen-Hoch stehen auch im Datenfenster. Mit TradingView Premium kann der Pine Screener damit die ganze Watchlist filtern (z. B. Korrektur-Chance ≥ 60).
- Am besten zusammen mit dem Aktien-Check nutzen (EMA 50/200, RSI, SMC-Zonen): Die Symmetrie-Zone ist am stärksten, wenn sie mit einer Kaufzone oder einer EMA zusammenfällt.

Persönliches Werkzeug, keine Anlageberatung.
