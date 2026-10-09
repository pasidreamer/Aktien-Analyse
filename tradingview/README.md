# Marktsymmetrie-Indikator für TradingView

Datei: [`marktsymmetrie.pine`](marktsymmetrie.pine) (Pine Script v6)

## Idee

Gesunde Trends laufen symmetrisch: Rücksetzer sind ungefähr gleich tief und gleich lang wie der letzte Rücksetzer, Anstiege ungefähr gleich gross wie der letzte Anstieg.
Der Indikator vergleicht deshalb jeden Kursschwung mit dem **letzten Schwung in die gleiche Richtung**, beim Preis und bei der Zeit, und zeichnet die Zone, in der der aktuelle Schwung symmetrisch enden würde.

- **Korrektur endet in der Symmetrie-Zone (Preis + Zeit):** möglicher Wendepunkt. Im Aufwärtstrend lohnt es sich, dort die Kaufzone und den Trigger zu prüfen.
- **Korrektur wird deutlich grösser als die letzte:** Symmetrie gebrochen, Warnung für den Trend.
- **Korrektur dauert gleich lang, ist aber flacher:** Zeichen von Stärke.
- **Bullen/Bären-Bilanz:** Sind die Anstiege im Schnitt grösser als die Rückgänge, dominieren die Käufer (asymmetrischer Markt nach oben) und umgekehrt.

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

## Alarme

Rechtsklick im Chart → «Alarm hinzufügen» → Bedingung «Marktsymmetrie» und dann:

- **Symmetrie-Zone erreicht** – Preis und Zeit sind symmetrisch
- **Preis-Symmetrie erreicht** – der Schwung ist so gross wie der letzte gleiche
- **Symmetrie gebrochen** – der Schwung ist deutlich grösser als der letzte gleiche

## Wichtig zu wissen

- Ein Wendepunkt ist erst **Pivot-Länge Kerzen später** bestätigt. Der letzte Schwung im Chart kann sich deshalb noch verschieben.
- Sehr kleine Vergleichsschwünge führen zu grossen Prozentwerten beim Fortschritt. Dann hilft eine grössere Pivot-Länge.
- Am besten zusammen mit dem Aktien-Check nutzen (EMA 50/200, RSI, SMC-Zonen): Die Symmetrie-Zone ist am stärksten, wenn sie mit einer Kaufzone oder einer EMA zusammenfällt.

Persönliches Werkzeug, keine Anlageberatung.
