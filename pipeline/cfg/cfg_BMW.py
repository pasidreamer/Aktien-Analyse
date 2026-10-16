import json, os, sys
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, P)
from helpers import L, ADW, RSIW, SEAS
c = {
"ticker": "BMW", "name": "BMW", "datum": "16.10.2026", "waehrung": "EUR", "land": "Deutschland",
"meta": "Bayerische Motoren Werke AG · Xetra: BMW · Autos (BMW, MINI, Rolls-Royce), Motorräder, Finanzdienstleistungen · München, Deutschland",
"price": "57.14 €",
"pricemeta": "Stand 16.10.2026 · 52 Wochen: 51.98 – 97.92 € · Allzeithoch 123.75 € im März 2015",
"verdict": "BMW ist an der Börse so billig wie selten: Der ganze Börsenwert (33 Mrd. €) liegt unter dem Netto-Bargeld der Autosparte (über 44 Mrd. € Ende 2025). Aber das Geschäft wird wirklich schlechter: Umsatz −6 %, die Auto-Marge fällt von 10 % (2021) auf 1 bis 3 % (Prognose 2026), in China verkauft BMW ein Viertel weniger Autos. Der Free Cashflow der Autosparte sinkt seit 2022 jedes Jahr, und Dividende plus Rückkäufe sind grösser als er. Qualität rot (15), Timing orange (32). Das ist ein klassischer Value-Falle-Kandidat: billig, aber noch ohne Wende.",
"about": "BMW baut Autos der Marken BMW, MINI und Rolls-Royce sowie Motorräder und verkauft rund 2.4 Mio. Autos pro Jahr. Dazu kommt eine eigene Bank (Financial Services), die Kunden Autos finanziert und least. Diese Bank macht die grossen Schulden im Konzern aus (rund 117 Mrd. €). Die Autosparte selbst hat mehr Geld als Schulden. Die wichtigsten Märkte sind Europa, China und die USA. Seit 2025 baut BMW die «Neue Klasse», eine neue Generation Elektroautos, als erstes den iX3 in Debrecen (Ungarn). Die Familie Quandt (Stefan Quandt und Susanne Klatten) besitzt rund die Hälfte der Aktien.",
"why": "Schon im Oktober 2025 senkte BMW die Prognose (Aktie −8 %), im Dezember stand sie aber noch bei 97.92 €. 2026 folgte der Absturz: Am 16. Juni kam die Gewinnwarnung. Die Auto-Marge für 2026 sinkt von 4–6 % auf nur noch 1–3 %, der Free Cashflow der Autosparte von über 4.5 auf über 2.5 Mrd. €. Gründe: In China brechen die Verkäufe ein (2. Quartal −30 %, 3. Quartal −25 %), weil chinesische Elektroautos günstiger und moderner sind. Dazu kommen US-Zölle, hohe Energiepreise wegen des Kriegs im Nahen Osten und Kosten für den Stellenabbau (rund 8'000 Stellen). Am 29./30. September sagte BMW am Investorentag, dass die Marge erst 2028 auf 3–5 % und erst Anfang der 2030er-Jahre wieder auf 8–10 % steigt. Am 8. Oktober fiel die Aktie auf 51.98 €, das tiefste seit 2020. Seit 2026 minus rund 40 %.",
"kpis": [
 ["r","Umsatzwachstum","−6.2 %","Letzte 12 Monate. Seit 2024 sinkt der Umsatz jedes Jahr. Im 3. Quartal 2026 lieferte BMW 6.3 % weniger Autos aus, in China 24.8 % weniger."],
 ["r","Operative Marge (Autos)","3.6 %","1. Halbjahr 2026: Von 100 € Autoumsatz bleiben 3.60 € Gewinn. 2021 waren es 10.3 %. Für 2026 erwartet BMW nur 1 bis 3 %. Schwach."],
 ["r","Gewinn pro Aktie (EPS)","10.52 €","Letzte 12 Monate. Für 2026 erwarten Analysten nur 6.70 € (−44 %). 2022 waren es 27.31 €."],
 ["r","ROIC","2.9 %","Auf 100 € investiertes Kapital nur rund 3 € Gewinn. Sehr schwach und seit 2023 (7.6 %) fallend."],
 ["w","Free Cashflow (Autos)","3.2 Mrd. €","2025, nur die Autosparte. Fällt seit 2022 jedes Jahr (11.1 → 6.9 → 4.9 → 3.2 Mrd. €). Prognose 2026: über 2.5 Mrd. €. Dividende und Rückkäufe (3.9 Mrd. €) waren 2025 grösser als der FCF."],
 ["g","Netto-Cash (Autos)","über 44 Mrd. €","Ende 2025. Die Autosparte hat viel mehr Geld als Schulden. Die 117 Mrd. € Schulden im Konzern gehören zur Autobank (Leasing und Kredite an Kunden)."],
 ["w","KGV","8.2","Auf den erwarteten Gewinn 2026 gerechnet. Auf die letzten 12 Monate nur 5.2. Eigener Schnitt 2021–2025: rund 5.6. Autobauer sind immer tief bewertet. Kurs-Buchwert nur 0.35: Die Börse bezahlt ein Drittel des Buchwerts."],
 ["w","Dividende","7.7 %","4.40 € pro Aktie, einmal im Jahr (bezahlt am 19.5.2026). Diese Rendite schaut zurück: BMW zahlt 30 bis 40 % des Gewinns aus. Bei 6.70 € Gewinn 2026 wären es nur rund 2.00 bis 2.70 € im Mai 2027."]
],
"revtitle": "Umsatz pro Quartal (Mio. €)", "revunit": "Mio. €", "epsunit": "€",
"revnote": "Nur eines von 8 Quartalen über dem Vorjahr. Seit Mitte 2024 sinkt der Umsatz fast jedes Quartal um rund 8 %.",
"marginnote": "EBIT-Marge der Autosparte (laut BMW). Von 10.3 % (2021) auf 3.6 % im 1. Halbjahr 2026 gefallen, im 2. Quartal sogar 2.3 %.",
"finnote": "<b>Hinweis:</b> Operative Marge in der Tabelle für den ganzen Konzern (mit Autobank), Free Cashflow nur für die Autosparte (laut BMW), weil der Konzern-FCF durch das Leasinggeschäft verzerrt ist. 2022 enthält einen Einmaleffekt von rund 5 Mrd. € aus China (BMW Brilliance). Seit 30.6.2026 gibt es nur noch Stammaktien.",
"FIN": [["2021",111239,"+12.4 %","12.1 %",18.77,6354,"6.5 %","4.6"],["2022",142610,"+28.2 %","9.9 %",27.31,11071,"6.6 %","3.0"],["2023",155498,"+9.0 %","11.8 %",17.68,6942,"7.6 %","5.7"],["2024",142380,"−8.4 %","8.0 %",11.62,4900,"4.4 %","6.8"],["2025",133453,"−6.3 %","7.4 %",11.89,3240,"3.8 %","7.9"],["Letzte 12 Mt.",128034,"−6.2 %","6.1 %",10.52,2185,"2.9 %","5.2"]],
"QREV": [["Q3 24",32406],["Q4 24",36416],["Q1 25",33758],["Q2 25",33927],["Q3 25",32314],["Q4 25",33454],["Q1 26",31007],["Q2 26",31259]],
"revdec": 0,
"MARGIN": [["2021",10.3],["2022",8.6],["2023",9.8],["2024",6.3],["2025",5.3],["H1 26",3.6]],
"Q": [
 ["Umsatztrend","0 von 4 Quartalen über Vorjahr",0,15],
 ["Wachstumstempo","Umsatz −6.2 % in 12 Monaten",0,10],
 ["Operative Marge","Autos 3.6 % (unter 8 %: 0 Pkt.), seit 2021 fallend (0 Pkt.)",0,15],
 ["Gewinnwachstum (EPS)","Für 2026 rund −44 % erwartet",0,10],
 ["Free Cashflow","Autosparte positiv, aber seit 2022 jedes Jahr gesunken",3,10],
 ["ROIC","2.9 % (2 Pkt.), fallend (−1)",1,15],
 ["Schulden","Autosparte mit Netto-Cash über 44 Mrd. €",10,10],
 ["Bewertung vs. eigene Historie","KGV 2026e 8.2 statt Ø 5.6 (2021–2025), rund 46 % teurer, weil der Gewinn einbricht",1,15]
],
"adwnote": ADW + "Negativ: Die Wochen-A/D fällt mit dem Kurs. Im Juni (Kurs um 59 €) stand sie bei −30, heute bei −40.6 bei 57 €. Es wird weiter verkauft.",
"rsiwnote": RSIW + "Im Juni und Juli um 27 (überverkauft), Anfang Oktober 29, heute 38: schwach, aber leicht steigend.",
"addnote": "Auch die Tages-A/D fällt seit September stark (−40 → −58.7 am 8.10.) und erholt sich seither nur leicht auf −56.6. Kein Zeichen, dass grosse Käufer einsteigen.",
"ind": [
 ["Kurs vs. EMA 50","57.1 &lt; 58.0","57.1 &lt; 70.0","Knapp unter der mittelfristigen Linie im Tageschart, weit darunter im Wochenchart."],
 ["Kurs vs. EMA 200","57.1 &lt; 67.9","57.1 &lt; 80.2","Weit unter der langfristigen Linie."],
 ["EMA 50 vs. EMA 200","50 unter 200 (seit 23.3.2026)","50 unter 200 (seit 16.3.2026)","Abwärtstrend auf beiden Zeitebenen."],
 ["RSI (14)","53.4","37.8","Tag: bullische Divergenz. Kurs am 8.10. tiefer (51.98 €) als im Juni (57.02 €), der RSI aber höher (25 statt 19)."],
 ["A/D","fällt mit dem Kurs","fällt mit dem Kurs","Auf beiden Zeitebenen negativ."],
 ["Volumen","Ø 20 Tage 1.78 Mio. vs. Ø 100 Tage 1.64 Mio. Aktien","Etwas mehr Handel als üblich."]
],
"smc": "BMW ist seit dem Hoch vom Dezember 2025 (97.92 €) in einem klaren Abwärtstrend mit tieferen Hochs (91.92 → 85.16 → 84.02 → 77.70 → 64.46 €) und tieferen Tiefs (73.38 → 72.40 → 57.02 → 51.98 €). Nach der Gewinnwarnung im Juni lief der Kurs drei Monate seitwärts zwischen 56 und 64.50 €, Ende September brach er nach unten aus. Am 8.10. lag das Tief bei 51.98 €. Am 16.10. stieg der Kurs auf 57.14 € und schloss über dem kleinen Hoch vom 7.10. (55.66 €): ein erster kleiner Change of Character im Tageschart, aber noch keine Wende. Darüber liegt viel Widerstand: 60 bis 64.50 € (Hochs vom September) und 68 bis 70 € (Tages-EMA 200 und Wochen-EMA 50). Unter 51.98 € gibt es im Chart der letzten zwei Jahre keine Unterstützung mehr.",
"zones": [
 ["r","68–70 €","Widerstand: Tages-EMA 200 (67.90 €) und Wochen-EMA 50 (70 €)."],
 ["r","60–64.50 €","Widerstand: Seitwärtsspanne Juli bis September, Hochs 64.22 und 64.46 €."],
 ["t","61 €","<b>Trigger:</b> Tagesschluss über 61 € (Beginn des Kursrutsches am 18.9. und über der Tages-EMA 50). Erst dann wäre die Wende bestätigt."],
 ["s","52–55 €","<b>Kaufzone:</b> Tiefs vom Oktober (51.98 bis 54.12 €). Nur für eine kleine Spekulation."],
 ["r","51.90 €","Abbruch: Wochenschluss unter dem Tief vom 8.10. Darunter keine Unterstützung in den letzten zwei Jahren."]
],
"smart": [
 "<b>BMW selbst:</b> Rückkaufprogramm bis 2 Mrd. €, 2026 rund 1.25 Mrd. € (rund 3.8 % des Börsenwerts). Die letzte Tranche endet am 30.11.2026, ein neues Programm ist nicht angekündigt. Im Juli kaufte BMW zu 56.76 bis 58.43 €.",
 "<b>Vorstand:</b> Am 29.5.2026 kauften sechs Vorstände zusammen für rund 2 Mio. € zu 76.16 €. Das hängt mit dem Aktienprogramm für Manager zusammen und ist kein freier Kauf. Nach der Gewinnwarnung keine freien Käufe gefunden.",
 "<b>Familie Quandt:</b> Stefan Quandt und Susanne Klatten halten rund 50.2 %. 2026 keine Käufe oder Verkäufe bekannt.",
 "<b>Analysten:</b> Mehrheit «Halten». StockAnalysis: 21 Analysten, 8× Kaufen, 10× Halten, 3× Verkaufen, Kursziel im Schnitt 70 € (58 bis 82.50 €). Zuletzt gesenkt: UBS 60 € (9.10.), Jefferies 60 € (5.10.), JPMorgan 82 € (vorher 100 €)."
],
"seasnote": SEAS + "30 Jahre Daten (seit 1996). Oktober (+2.4 %, 68 %) und Dezember (+2.3 %, 67 %) sind stark, August (−3.7 %, 33 %) ist der schwächste Monat.",
"T": [
 ["Trend Woche (EMA 50/200)","Kurs weit unter beiden, EMA 50 unter 200 und fallend",1,20],
 ["Trend Tag (EMA 50/200)","Kurs knapp unter EMA 50, weit unter EMA 200, EMA 50 unter 200",1,10],
 ["Struktur (SMC)","Tiefere Hochs und Tiefs, erster kleiner CHoCH am 16.10.",4,20],
 ["RSI Tag/Woche","Bullische Divergenz im Tageschart (Kurs tiefer, RSI höher)",12,15],
 ["A/D Tag/Woche","Beide fallen mit dem Kurs",4,20],
 ["Smart Money","Start 3, Rückkauf 3.8 % pro Jahr +3, keine freien Insider-Käufe",6,10],
 ["Saisonalität","Oktober 68 %, November 55 %, Dezember 67 % positive Jahre",4,5]
],
"pro": [
 "Extrem tief bewertet: Börsenwert (33 Mrd. €) unter dem Netto-Cash der Autosparte (über 44 Mrd. €), Kurs-Buchwert 0.35.",
 "Neue Klasse kommt gut an: über 100'000 Bestellungen für den iX3 in Europa in einem Jahr.",
 "Sparprogramm: 20 % weniger Management, rund 8'000 Stellen, Investitionen sinken unter 10 % vom Umsatz.",
 "Familie Quandt als stabiler Grossaktionär, Rückkäufe laufen bis Ende November.",
 "Bullische RSI-Divergenz im Tageschart, starke Saison Oktober bis Dezember."
],
"con": [
 "China bricht weg (−25 bis −30 %): Chinesische Elektroautos sind günstiger und moderner.",
 "Lange Durststrecke: Marge erst 2028 bei 3–5 %, 8–10 % erst Anfang der 2030er-Jahre.",
 "Free Cashflow sinkt seit 2022 jedes Jahr, die Ausschüttungen sind grösser als er.",
 "Dividende 2027 wird voraussichtlich deutlich gekürzt (Politik: 30–40 % vom Gewinn).",
 "Klarer Abwärtstrend, A/D fällt: Grosse Anleger verkaufen weiter. Value-Falle möglich."
],
"todo": [
 ["t","Beobachten","Alarm bei 61 € (Trigger) und 51.90 € (Abbruch). Kein Kauf, solange der Abwärtstrend läuft."],
 ["s","Timing grün","Tagesschluss über 61 € mit steigender A/D und danach ein höheres Tief über 52 €. Fundamental: Die Auto-Marge muss im 3. Quartal bei mindestens 1 % halten und China sich stabilisieren."],
 ["r","Abbruch","Wochenschluss unter 51.90 €."],
 ["","Nächste Zahlen","4. November 2026 (3. Quartal, bestätigt). Jahreszahlen und Dividende: 11. März 2027. Generalversammlung: 12. Mai 2027."]
],
"bands": [{"from":68,"to":70,"type":"res"},{"from":60,"to":64.5,"type":"res"},{"from":52,"to":55,"type":"sup"}],
"refs": [{"v":61,"label":"Trigger 61"}],
"sources": L("https://stockanalysis.com/quote/etr/BMW/financials/","StockAnalysis.com") + " (Stand 16.10.2026), " + L("https://www.press.bmwgroup.com/global/article/detail/T0458585EN/bmw-group-adjusts-guidance-for-2026","BMW Gewinnwarnung (16.6.2026)") + ", " + L("https://www.bmwgroup.com/en/news/general/2026/capital-market-day.html","BMW Investorentag 2026") + ", " + L("https://www.boersen-zeitung.de/unternehmen-branchen/bmw-schwoert-boerse-auf-durststrecke-ein","Börsen-Zeitung: Durststrecke") + ", " + L("https://www.just-auto.com/newsletters/bmw-deliveries-decline-6-3","Just Auto: Auslieferungen Q3") + ", " + L("https://stockanalysis.com/quote/etr/BMW/forecast/","Analysten (StockAnalysis)") + ", " + L("https://www.vermoegenszentrum.ch/wissen/auslaendische-dividenden-so-holen-sich-anleger-die-quellensteuer-zurueck","VZ: Quellensteuer") + "."
}
if __name__ == "__main__":
    json.dump(c, open(os.path.join(P, "config", "BMW.json"), "w"), ensure_ascii=False, indent=1)
    print("ok", sum(r[2] for r in c["Q"]), sum(r[2] for r in c["T"]))
