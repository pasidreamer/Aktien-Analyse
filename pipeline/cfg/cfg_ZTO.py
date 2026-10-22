import json, os, sys
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, P)
from helpers import L, ADW, RSIW, SEAS
c = {
"ticker": "ZTO", "name": "ZTO Express", "datum": "22.10.2026", "waehrung": "USD", "land": "China",
"meta": "ZTO Express (Cayman) Inc. · NYSE: ZTO (ADR, 1 ADR = 1 Aktie), auch Hongkong: 2057 · Paketdienst · Shanghai, China",
"price": "20.06 USD",
"pricemeta": "Schluss 22.10.2026 · 52 Wochen: 18.11 – 26.20 USD · Allzeithoch rund 37 bis 39 USD (2020/21)",
"verdict": "ZTO ist Chinas grösster Paketdienst (38.5 Mrd. Pakete 2025, rund 20 % Marktanteil) und verdient gut: Umsatz +23 % im 2. Quartal 2026, Marge 21 %, mehr Geld als Schulden. Mit einem KGV von rund 10.6 ist die Aktie billig. Die Börse sorgt sich um die Menge: Am 18.8.2026 senkte ZTO das Ziel für 2026 auf +6 bis +10 % mehr Pakete, Konkurrent J&T wächst schneller, und der Onlinehandel in China wächst nur noch rund 5 %. Der Staat verbietet Preise unter den Kosten, das hebt den Preis pro Paket (+15.5 %), kostet aber Menge. Qualität grün (83), Timing orange (34): Der Abwärtstrend seit März ist intakt. ZTO kauft laufend eigene Aktien um 19.50 USD zurück. Zusätzliches Risiko: China-Aktie mit Firmensitz auf den Cayman Islands. Keine Anlageberatung.",
"about": "ZTO Express aus Shanghai ist nach Paketmenge seit rund 10 Jahren der grösste Paketdienst Chinas. ZTO besitzt das Rückgrat: 93 Sortierzentren, eine eigene Lastwagenflotte und die Software. Abholen und Ausliefern machen über 6'000 selbständige Partnerfirmen mit über 31'000 Abholstellen. ZTO verdient an jedem Paket, das durch sein Netz läuft. Vorteil: wenig eigenes Personal, hohe Marge. Nachteil: Geht es den Partnern schlecht, leidet die Qualität. 93 % des Umsatzes kommen aus dem Paketgeschäft, der Rest aus Verpackungsmaterial und Frachtvermittlung. Gründer und Chef Lai Meisong kontrolliert die Firma über Aktien mit Mehrfachstimmrecht (rund 26.5 % der Aktien, Stand Mai 2025), Alibaba hielt rund 8.4 %. Die Aktie wird in New York (ZTO, in Dollar) und in Hongkong (2057) gehandelt.",
"why": "Die Aktie stand 2020/21 bei rund 37 bis 39 USD. Danach drückten der Preiskampf unter Chinas Paketdiensten und die Angst vor einem Rauswurf chinesischer Firmen von der US-Börse (2022) den Kurs bis auf 16.34 USD (April 2025). 2025 sank der Preis pro Paket um 1.7 % und der Betriebsgewinn um 11 %. Im Juli 2025 begann die Regierung, gegen Dumpingpreise vorzugehen («Anti-Involution»). Die Preise stiegen wieder, die Aktie kletterte bis 26.20 USD (18.3.2026). Seither fällt sie: Am 18.8.2026 meldete ZTO zwar +50 % bereinigten Gewinn im 2. Quartal (darin 344 Mio. RMB einmalige Steuerrückzahlung), senkte aber das Mengenziel für 2026 von +10 bis +13 % auf +6 bis +10 %. JPMorgan (3.9.) und Goldman Sachs (14.10.) stuften auf Neutral ab, beide mit Ziel 22 USD. Am 21.9. fiel die Aktie um 8.6 % ohne neue Firmennachricht auf 18.95 USD. Teurer werden auch Sozialversicherung für Kuriere und Diesel.",
"kpis": [
 ["g","Umsatzwachstum","+17.0 %","Letzte 12 Monate. 2. Quartal 2026: +23 %. Die Paketmenge wuchs aber nur 6.5 %, der Rest kommt von höheren Preisen und Grosskunden, die ZTO selbst abrechnet."],
 ["g","Operative Marge","21.0 %","Von 100 Yuan Umsatz bleiben 21 Yuan Betriebsgewinn (letzte 12 Monate). Gut, aber tiefer als 2023/24 (26 bis 27 %), weil ZTO mehr eigene Grosskunden-Pakete abrechnet."],
 ["g","Gewinn pro Aktie (EPS)","12.82 RMB","Letzte 12 Monate, rund 1.89 USD pro ADR. 2022: 8.36 RMB. Im Schnitt rund +10 % pro Jahr. Enthält eine einmalige Steuerrückzahlung."],
 ["w","ROIC","16.5 %","Auf 100 Yuan investiertes Kapital rund 16.50 Yuan Gewinn. Ordentlich und seit 2021 (12.3 %) gestiegen."],
 ["g","Free Cashflow","9.8 Mrd. RMB","Letzte 12 Monate, rund 1.45 Mrd. USD. Seit 2022 jedes Jahr positiv (2024 leicht tiefer)."],
 ["g","Netto-Cash","9.5 Mrd. RMB","Mehr Geld als Schulden (30.6.2026, eigene Rechnung), rund 1.4 Mrd. USD. Mit langfristigen Anlagen sogar 16 Mrd. RMB."],
 ["g","KGV","10.6","Du zahlst rund 11 Jahresgewinne. Eigener Schnitt 2021–2025: 18.4 (2023–2025 nur 13.2). Also deutlich günstiger als üblich. China-Aktien sind generell tief bewertet."],
 ["w","Dividende","3.4 %","Zuletzt 0.39 USD (Ex-Tag 8.4.2026, bezahlt am 29.4.2026) und 0.30 USD (Oktober 2025). Für das 1. Halbjahr 2026 gibt es keine Zwischendividende, ZTO kauft stattdessen Aktien zurück."]
],
"revtitle": "Umsatz pro Quartal (Mrd. RMB)", "revunit": "Mrd. RMB", "epsunit": "RMB",
"revnote": "Alle 8 Quartale über dem Vorjahr, 2026 mit deutlich höherem Tempo (+22 % und +23 %). Das 4. Quartal ist wegen der Einkaufstage im November («Singles Day») immer das stärkste.",
"marginnote": "Betriebsgewinn pro 100 Yuan Umsatz. Von 18 % (2021) auf 27 % (2024) gestiegen, 2025 wegen des Preiskampfs auf 21 % gefallen.",
"finnote": "<b>Hinweis:</b> Zahlen in chinesischen Yuan (RMB), Kurs in Dollar. 1 USD = rund 6.79 RMB (30.6.2026). Umsatz, Marge und EPS aus den Firmenberichten, Free Cashflow, ROIC und KGV laut StockAnalysis (Hongkong-Linie 2057, gleiche Aktie). Das KGV 2021 und 2022 war wegen hoher China-Bewertungen ungewöhnlich hoch.",
"FIN": [["2021",30406,"+20.6 %","18.1 %",5.80,-1140,"12.3 %","30.5"],["2022",35377,"+16.3 %","21.9 %",8.36,4412,"13.8 %","22.0"],["2023",38419,"+8.6 %","26.0 %",10.60,6832,"15.6 %","13.9"],["2024",44281,"+15.3 %","26.6 %",10.70,6221,"15.8 %","12.9"],["2025",49099,"+10.9 %","21.3 %",11.19,6754,"15.8 %","12.7"],["Letzte 12 Mt.",54208,"+17.0 %","21.0 %",12.82,9839,"16.5 %","10.6"]],
"QREV": [["Q3 24",10.68],["Q4 24",12.92],["Q1 25",10.89],["Q2 25",11.83],["Q3 25",11.86],["Q4 25",14.51],["Q1 26",13.28],["Q2 26",14.55]],
"revdec": 1,
"MARGIN": [["2021",18.1],["2022",21.9],["2023",26.0],["2024",26.6],["2025",21.3],["12 Mt.",21.0]],
"Q": [
 ["Umsatztrend","4 von 4 Quartalen über Vorjahr, Tempo steigt (11 → 12 → 22 → 23 %)",15,15],
 ["Wachstumstempo","+17 % in 12 Monaten (Paketmenge nur +6 bis +10 % erwartet)",10,10],
 ["Operative Marge","21.0 % (6 Pkt.), über 5 Jahre gestiegen, seit 2024 gefallen: stabil (3 Pkt.)",9,15],
 ["Gewinnwachstum (EPS)","Rund +10 % pro Jahr seit 2022, zuletzt höher (mit Einmaleffekt)",8,10],
 ["Free Cashflow","Positiv, seit 2022 meist steigend, 2024 kurz tiefer",6,10],
 ["ROIC","16.5 % (10 Pkt.), steigend (+1)",11,15],
 ["Schulden","Netto-Cash rund 9.5 Mrd. RMB",10,10],
 ["Bewertung vs. eigene Historie","KGV 10.6 statt Ø 18.4, über 30 % günstiger (gegen 2023–2025 rund 20 %)",14,15]
],
"adwnote": ADW + "Positiv: Der Kurs fiel vom Tief im Juni (21.47 USD) bis zum Tief im September (18.95 USD) um 12 %, die Wochen-A/D blieb aber gleich (−131.5 → −132.9, heute −131.6). Es wird nicht mehr verkauft als vorher: eine bullische Divergenz.",
"rsiwnote": RSIW + "Im September bei 32 (fast überverkauft), heute 37: schwach, dreht leicht nach oben.",
"addnote": "Leicht negativ: Die Tages-A/D fällt seit dem Tief vom 21.9. weiter (−49.6 → −50.3), obwohl der Kurs leicht höher steht (18.95 → 20.06 USD). Die Erholung hat wenig Kraft.",
"ind": [
 ["Kurs vs. EMA 50","20.06 &lt; 20.72","20.06 &lt; 21.82","Unter der mittelfristigen Linie, auf beiden Zeitebenen."],
 ["Kurs vs. EMA 200","20.06 &lt; 21.91","20.06 &lt; 22.17","Unter der langfristigen Linie."],
 ["EMA 50 vs. EMA 200","50 unter 200 (Todeskreuz am 3.9.2026)","50 unter 200 (Todeskreuz am 7.9.2026), beide flach und nah beieinander","Abwärtstrend auf beiden Zeitebenen, in der Woche aber schwach."],
 ["RSI (14)","47.3","37.3","Tag neutral, Woche schwach."],
 ["A/D","fällt leicht","seitwärts trotz tieferem Kurs","Woche positiv (Divergenz), Tag leicht negativ."],
 ["Volumen","Ø 20 Tage 2.25 Mio. vs. Ø 100 Tage 2.02 Mio. Aktien","Etwas mehr Handel als üblich."]
],
"smc": "Seit dem Hoch vom 18.3.2026 (26.20 USD) fällt ZTO mit tieferen Hochs und tieferen Tiefen: Hochs 25.97 (24.4.), 24.78 (16.7.), 21.04 (18.9.) und 20.77 USD (13.10.), Tiefs 23.12 (8.4.), 21.47 (25.6.), 20.36 (3.9.) und 18.95 USD (21.9.). Seit dem 21.9. gibt es im Tageschart höhere Tiefs (19.33 USD am 29.9., 19.78 USD am 21.10.). Ein Change of Character nach oben wäre ein Tagesschluss über 21.05 USD (Hoch vom 18.9.). Darüber liegen die Wochen-EMAs bei 21.80 bis 22.20 USD.",
"zones": [
 ["r","23.10–24.80 USD","Widerstand: Hochs Juli und August, Tief vom April."],
 ["r","21.80–22.40 USD","Widerstand: Wochen-EMA 50 und 200, Hoch vom 3.6. und Tief vom 12.8."],
 ["t","21.05 USD","<b>Trigger:</b> Tagesschluss über 21.05 USD (letztes tieferes Hoch vom 18.9.), besser mit steigender Tages-A/D."],
 ["s","18.90–19.60 USD","<b>Kaufzone 1:</b> Tiefs vom 21.9. (18.95) und 29.9. (19.33 USD). Hier kaufte ZTO selbst Aktien zurück (19.44 bis 19.57 USD am 30.9.)."],
 ["s","16.30–17.90 USD","<b>Kaufzone 2:</b> Tiefs von Januar, April, Mai und September 2025 (16.34 bis 17.89 USD)."],
 ["r","18.10 USD","Abbruch: Wochenschluss unter 18.10 USD, also unter dem 52-Wochen-Tief."]
],
"smart": [
 "<b>Rückkäufe:</b> Neues Programm über 1.5 Mrd. USD bis März 2028, rund 10 % des Börsenwerts (also rund 5 % pro Jahr). 2026 bis Juni 31.8 Mio. Aktien für 740 Mio. USD zurückgekauft, im September weiter zu rund 19.50 USD.",
 "<b>Insider:</b> Gründer Lai Meisong hält rund 26.5 % der Aktien (Mai 2025), dazu Mehrfachstimmrechte. Käufe oder Verkäufe der Führung in den letzten 6 Monaten habe ich nicht gefunden. Alibaba (8.4 %) prüfte 2025 einen Teilverkauf.",
 "<b>Grosse Investoren (13F):</b> Gemischt. Im 1. Quartal 2026 reduzierten Pzena, Temasek und Goldman Sachs, Fisher und Marshall Wace stockten auf. Im 2. Quartal stockten JPMorgan und Point72 auf, Citigroup halbierte.",
 "<b>Analysten:</b> Kursziel im Schnitt 24.70 bis 26 USD (Spanne 22 bis 30.10 USD), mehrheitlich Halten. JPMorgan (3.9.) und Goldman Sachs (14.10.) stuften auf Neutral ab, Ziel je 22 USD."
],
"seasnote": SEAS + "Nur 10 Jahre Daten (seit 2016). Februar (+4.5 %, 80 %) und April (+5.0 %, 80 %) sind stark, Oktober (−2.9 %, 36 %), November (−1.6 %, 44 %) und Dezember (−2.0 %, 50 %) schwach.",
"T": [
 ["Trend Woche (EMA 50/200)","Kurs unter beiden, EMA 50 unter 200, aber flach und nah beieinander",4,20],
 ["Trend Tag (EMA 50/200)","Kurs unter beiden, EMA 50 unter 200",1,10],
 ["Struktur (SMC)","Tiefere Hochs und tiefere Tiefs, erste höhere Tiefe im Tageschart",4,20],
 ["RSI Tag/Woche","Tag 47, Woche 37, kein klares Signal",7,15],
 ["A/D Tag/Woche","Woche: bullische Divergenz, Tag leicht fallend",11,20],
 ["Smart Money","Start 3, grosser Rückkauf (+3), keine Insider-Daten",6,10],
 ["Saisonalität","November 44 %, Dezember 50 % positive Jahre",1,5]
],
"pro": [
 "Marktführer in China mit rund 20 % Anteil, Umsatz +23 % im 2. Quartal 2026.",
 "Staatliches Verbot von Preisen unter den Kosten hebt den Preis pro Paket (+15.5 % im 2. Quartal).",
 "Mehr Geld als Schulden, Free Cashflow von 9.8 Mrd. RMB in 12 Monaten.",
 "Günstig: KGV rund 10.6, grosser Rückkauf (rund 10 % des Börsenwerts bis 2028).",
 "Wochen-A/D zeigt eine bullische Divergenz: Beim tieferen Kurs wurde nicht mehr verkauft."
],
"con": [
 "Mengenziel 2026 gesenkt (+6 bis +10 %), Konkurrent J&T wächst schneller (+15 % im 3. Quartal).",
 "Chinas Onlinehandel wächst nur noch rund 5 %, der Preiskampf kann über Rabatte zurückkommen.",
 "Höhere Kosten für Sozialversicherung der Kuriere und Diesel.",
 "China-Risiko: Firmensitz auf den Cayman Islands, Gründer kontrolliert die Stimmen, US-Börsenregeln für chinesische Firmen.",
 "Keine Zwischendividende 2026, Abwärtstrend im Chart intakt."
],
"todo": [
 ["t","Beobachten","Alarm bei 21.05 USD (Trigger) und 19.60 USD (oberes Ende Kaufzone 1)."],
 ["s","Timing grün","Tagesschluss über 21.05 USD, danach Wochenschluss über 22.20 USD (Wochen-EMA 200) mit drehender Tages-A/D. Fundamental: Am 17.11. Paketmenge im 3. Quartal über +6 % und Preis pro Paket weiter höher."],
 ["r","Abbruch","Wochenschluss unter 18.10 USD."],
 ["","Nächste Zahlen","17. November 2026 nach US-Börsenschluss (3. Quartal, bestätigt). Jahreszahlen voraussichtlich Mitte März 2027."]
],
"bands": [{"from":23.1,"to":24.8,"type":"res"},{"from":21.8,"to":22.4,"type":"res"},{"from":18.9,"to":19.6,"type":"sup"},{"from":16.3,"to":17.9,"type":"sup"}],
"refs": [{"v":21.05,"label":"Trigger 21.05"}],
"sources": L("https://stockanalysis.com/quote/hkg/2057/financials/ratios/","StockAnalysis.com (2057)") + " (Stand 22.10.2026), " + L("https://www.sec.gov/Archives/edgar/data/0001677250/000110465926098506/tm2623526d1_ex99-1.htm","ZTO Zahlen 2. Quartal 2026") + ", " + L("https://www.sec.gov/Archives/edgar/data/1677250/000110465926030007/tm269230d1_ex99-1.htm","ZTO Jahreszahlen 2025") + ", " + L("https://thebambooworks.com/zto-lowers-annual-parcel-volume-guidance-as-industry-growth-slows/","Bamboo Works: Prognose gesenkt") + ", " + L("https://www.ad-hoc-news.de/boerse/news/nebenwerte/goldman-sachs-cuts-target-to-usd-22-00-for-zto-express-stock/70356426","Goldman Sachs (14.10.2026)") + ", " + L("https://technode.global/?p=995447","Termin 3. Quartal") + ", " + L("https://www.marketbeat.com/stocks/NYSE/ZTO/forecast","Kursziele (MarketBeat)") + ". Branchenvergleich der App (Hongkong-Linie): Note 2.9 von 5, fairer Wert rund 77 % über dem Kurs, Unsicherheit sehr hoch."
}
if __name__ == "__main__":
    json.dump(c, open(os.path.join(P, "config", "ZTO.json"), "w"), ensure_ascii=False, indent=1)
    print("ok", sum(r[2] for r in c["Q"]), sum(r[2] for r in c["T"]))
