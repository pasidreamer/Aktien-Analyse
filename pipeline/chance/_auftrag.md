# Auftrag: Chancen-Profil pro Aktie (Unterbewertung + Wachstumsschub)

Leser: Pascal, Privatanleger in der Schweiz, Anfänger. Schreibe Deutsch mit Schweizer Schreibweise (kein ß, "ss"), einfach, kurze Sätze, keine Fachbegriffe ohne Erklärung. Keine Kaufempfehlung, nur Beobachtungen.

Pascals zwei Blickwinkel:
1. UNTERBEWERTUNG: Eine Aktie ist wegen Sorgen stark gefallen und günstig. Wenn die Sorgen verschwinden, kann sie stark steigen. Er will wissen: Welche Sorgen drücken den Kurs genau? Sind sie echt (Geschäft verschlechtert sich) oder vor allem Stimmung? Was müsste passieren, damit sie verschwinden, und wann könnte man das sehen (konkrete Termine/Ereignisse)?
2. WACHSTUMSSCHUB: Gibt es einen konkreten Grund, warum das Wachstum in den nächsten 1–3 Jahren deutlich anziehen könnte? Beispiel: Alphabet/Google 2023: Alle dachten, Google verschläft KI, aber Google hatte mit Gemini, eigenen KI-Chips (TPU) und Google Cloud längst die Basis. Danach stieg die Aktie stark. Gesucht sind solche Treiber: neue Produkte, Zulassungen, neue Märkte, Plattform-Effekte, Preiserhöhungsmacht, Margen-Hebel, Abspaltungen. Ehrlich bleiben: Wenn es keinen grossen Treiber gibt, "schwach" sagen.

Kontext: Lies zuerst die bestehende Analyse in /home/claude/aktien-ampel/data/stocks.json (Eintrag mit "ticker" = TICKER: fazit, about, kpis, pro, contra, bewertung {wert = KGV am Analysetag, schnitt = eigener 5-Jahres-Schnitt}). Recherchiere dann mit WebSearch/WebFetch aktuelle Fakten (Stand Oktober 2026: Quartalszahlen, Prognosen, Produkt-Pipeline, Zulassungen, Investorentage, Analysten). Nutze keine Shell für Webzugriffe. Heute ist der 11.10.2026.

Stufen Wachstumsschub (streng anwenden):
- "stark": Ein konkreter, schon sichtbarer Treiber (erste Umsätze, Zulassung, unterschriebene Verträge), der das Umsatz- oder Gewinnwachstum in 1–3 Jahren klar über das heutige Tempo heben kann.
- "mittel": Plausible Treiber, aber noch unbewiesen, klein im Verhältnis zur Firma oder zeitlich unsicher.
- "schwach": Reife Firma ohne grossen neuen Treiber; Wachstum bleibt etwa wie heute oder sinkt.

Stufen Sorgen-Charakter:
- "stimmung": Kurs vor allem wegen Stimmung/Bewertung gefallen, Geschäft weitgehend intakt.
- "gemischt": Echte Probleme, aber eher vorübergehend oder lösbar.
- "echt": Das Geschäft verschlechtert sich strukturell (Marktanteile, Nachfrage, Wettbewerb).

Schreibe pro Aktie eine Datei /home/claude/aktien/tools/chance/TICKER.json (UTF-8, gültiges JSON) mit genau diesem Schema:
{
 "ticker": "TICKER",
 "sorgen": ["2–4 kurze Sätze: Was die Börse gerade befürchtet (mit Zahl/Datum wo möglich)"],
 "sorgen_art": "stimmung | gemischt | echt",
 "sorgen_art_text": "1 Satz Begründung",
 "aufloeser": [{"was": "Was die Sorge beenden könnte", "wann": "Termin oder Zeitraum, z. B. 'Zahlen 28.10.2026' oder '2027'"}],   // 2–4 Einträge
 "schub_stufe": "stark | mittel | schwach",
 "schub_treiber": [{"titel": "kurzer Titel", "text": "2–3 Sätze: was es ist, warum es gross werden kann, wie gross (Zahlen)", "wann": "Zeitraum"}],   // 1–4 Einträge, bei "schwach" ehrlich 1–2 kleine
 "schub_beweis": "1–2 Sätze: Woran Pascal in den nächsten Quartalszahlen erkennt, dass der Schub kommt (konkrete Kennzahl)",
 "szenario": "2–3 Sätze im Stil 'Wie Google 2023': das Chancen-Szenario, falls es aufgeht, und das grösste Risiko, falls nicht",
 "quellen": [{"titel": "...", "url": "https://..."}]   // 2–5 echte Quellen, die du gelesen hast
}
Keine erfundenen Zahlen oder Quellen. Wo du unsicher bist, schreibe es vorsichtig ("laut Firma", "erwartet"). Antworte am Ende nur kurz, welche Dateien du geschrieben hast und was du nicht verifizieren konntest.
