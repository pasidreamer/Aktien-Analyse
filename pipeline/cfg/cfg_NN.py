import json, os, sys
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, P)
from helpers import L, ADW, RSIW, SEAS
c = {
"ticker": "NN", "name": "NN Group", "datum": "29.10.2026", "waehrung": "EUR", "land": "Niederlande",
"meta": "NN Group N.V. · Euronext Amsterdam: NN (in Euro) · Lebens- und Sachversicherung, Pensionen, Bank · Den Haag, Niederlande",
"price": "78.26 €",
"pricemeta": "Schluss 29.10.2026 · 52 Wochen: 58.92 – 83.40 € · Rekordhoch 83.40 € (6.8.2026) · Börsenwert rund 20.3 Mrd. € (260 Mio. Aktien)",
"verdict": "NN Group ist der grösste Versicherer der Niederlande und verdient vor allem mit Pensionen und Lebensversicherungen. Für einen Versicherer zählt, wie viel freies Kapital entsteht: Die operative Kapitalgenerierung stieg im 1. Halbjahr 2026 um 5 % auf 1'073 Mio. €, die Solvency-II-Quote ist mit 224 % sehr hoch (Pflicht: 100 %). Davon gehen rund 5 % Dividende und 1.7 % Rückkäufe pro Jahr an die Aktionäre. Schwach sind Wachstum und Rendite: Die Prämien wachsen nicht (12 Monate −2 %), die Eigenkapitalrendite liegt unter 10 %, und mit einem KGV von 11.5 ist die Aktie nach dem Anstieg von 42 auf 78 € seit Ende 2024 teurer als im eigenen Schnitt (8.4). Unser Schema ist für Industriefirmen gebaut und passt nur teilweise auf Versicherer, darum Qualität orange (41). Timing hellgrün (72): Aufwärtstrend intakt, Rücksetzer seit August aufgefangen. Nächste Zahlen am 10.2.2027. Keine Anlageberatung.",
"about": "NN Group aus Den Haag entstand aus Nationale-Nederlanden (gegründet 1963 aus zwei Versicherern, einer davon von 1845). Bis 2014 gehörte die Firma zur Bank ING, seit 2014 ist sie an der Börse in Amsterdam. NN verkauft vor allem Pensionen und Lebensversicherungen in den Niederlanden (rund 55 % der Kapitalgenerierung im 1. Halbjahr 2026), dazu Sachversicherungen wie Auto, Haus und Haftpflicht (Niederlande Non-life), Versicherungen in anderen Ländern Europas (Insurance Europe, z. B. Polen, Rumänien, Griechenland, Belgien), Lebensversicherungen für Firmen in Japan und eine eigene Bank für Hypotheken (NN Bank). <b>So verdient ein Versicherer:</b> Kunden zahlen Prämien, NN legt das Geld an und zahlt später Renten und Schäden. Der Gewinn kommt aus der Differenz. Wichtigste Kennzahl ist darum nicht der Umsatz, sondern wie viel Kapital übrig bleibt, nachdem die Aufsicht genug Reserven verlangt hat (Kapitalgenerierung) und wie viel Geld die Töchter an die Holding überweisen (Free Cashflow der Holding). Daraus bezahlt NN Dividende und Rückkäufe.",
"why": "Die Aktie stieg von 42.54 € (Ende 2024) bis zum Rekord von 83.40 € am 6.8.2026, also fast auf das Doppelte. Gründe: Das operative Ergebnis stieg 2025 um 17 % auf 3'002 Mio. €, die Solvency-II-Quote kletterte von 194 % auf 220 %, und die Dividende wurde 2025 um 13 % erhöht. Nach den Halbjahreszahlen vom 6.8.2026 fiel der Kurs bis auf 75.16 € (9.10.2026), also rund 10 %. Eine schlechte Firmennachricht dazu habe ich nicht gefunden. Die Zahlen waren solide: Kapitalgenerierung +5 %, Free Cashflow der Holding +7 %, Wert des Neugeschäfts +16 %. Kleinere Dämpfer: Die Prämien sanken leicht (−0.2 %), die Solvency-Quote der grössten Tochter NN Life fiel von 223 % auf 213 %, und laut Firma wird der Verkauf über griechische Banken 2027 deutlich schwächer. Der Rücksetzer wirkt eher wie eine Verschnaufpause nach dem starken Anstieg als wie ein echtes Problem.",
"kpis": [
 ["r","Bruttoprämien","−1.9 %","Ersatz für den Umsatz. Prämien der letzten 12 Monate bis Juni 2026: 13'243 Mio. € (eigene Rechnung aus Halbjahren), ein Jahr davor 13'503 Mio. €. 2025: −5.2 %. Das Prämienvolumen wächst nicht."],
 ["w","Kapitalgenerierung (OCG)","2'142 Mio. €","Kapital, das in 12 Monaten bis Juni 2026 frei wurde (eigene Rechnung, +8 %). 2021: 1'584 Mio. €. Seit 2021 jedes Jahr gestiegen. Ziel für 2028: 2'200 Mio. €, also nur noch langsames Wachstum."],
 ["g","Free Cashflow Holding","1'679 Mio. €","Geld, das die Töchter in 12 Monaten bis Juni 2026 an die Holding überwiesen haben (eigene Rechnung). Damit zahlt NN Dividende (rund 1'050 Mio. €) und Rückkäufe (350 Mio. €). 2023 waren es wegen einer Sonderzahlung nur 470 Mio. €."],
 ["g","Solvency-II-Quote","224 %","Kapital im Verhältnis zum Minimum, das die Aufsicht verlangt (30.6.2026). 100 % ist Pflicht, über 150 % gilt als komfortabel. NN hat viel Puffer. Ende 2024 waren es 194 %."],
 ["r","Eigenkapitalrendite","9.7 %","Ersatz für den ROIC: Gewinn der letzten 12 Monate (1'863 Mio. €) geteilt durch Eigenkapital (19'254 Mio. €), eigene Rechnung. Auf 100 € Eigenkapital rund 10 € Gewinn. Für einen Versicherer mittelmässig."],
 ["g","Verschuldung","17.3 %","Ersatz für Nettoschulden/EBITDA: Anteil der Schulden am Kapital der Holding (Financial Leverage, 30.6.2026). Unter 25 % gilt als wenig. Die Zinsen sind 13.5-mal durch die Gewinne gedeckt."],
 ["r","KGV","11.5","Du zahlst rund 11.5 Jahresgewinne (Kurs 78.26 € geteilt durch 6.79 € Gewinn pro Aktie der letzten 12 Monate). Eigener Schnitt der letzten 5 Jahre: 8.4. Also rund 37 % teurer als üblich. Auf den erwarteten Gewinn wäre das KGV 8.3."],
 ["g","Dividende","5.0 %","Für 2025 total 3.88 € pro Aktie (+13 %), in 2 Zahlungen: Schlussdividende 2.50 € (Ex-Tag 25.5.2026, bezahlt 2.6.2026) und Zwischendividende 1.55 € für 2026 (Ex-Tag 10.8.2026, bezahlt 18.8.2026, +12 %). Bar in Euro, 15 % niederländische Quellensteuer."]
],
"revtitle": "Bruttoprämien pro Halbjahr (Mrd. €)", "revunit": "Prämien Mio. €", "epsunit": "€",
"revnote": "Ersatz für den Umsatz. Das 1. Halbjahr ist immer grösser, weil viele Prämien am Jahresanfang fällig werden. Darum nur gleiche Halbjahre vergleichen: Seit dem 1. Halbjahr 2025 liegen alle drei Halbjahre unter dem Vorjahr (−6.0 %, −4.1 %, −0.2 %).",
"margintitle": "Operatives Ergebnis pro 100 € Prämie",
"marginnote": "Ersatz für die operative Marge: operatives Ergebnis (Gewinn aus dem laufenden Geschäft, ohne Kursschwankungen der Kapitalanlagen) geteilt durch die Bruttoprämien, eigene Rechnung. Erst ab 2023 vergleichbar (neue Rechnungslegung IFRS 17). Von 19 % auf 23 % gestiegen.",
"finnote": "<b>Hinweis für Versicherer:</b> Die Spalten der Tabelle sind für Industriefirmen gemacht. Hier gilt: «Umsatz» = Bruttoprämien, «Op. Marge» = operatives Ergebnis geteilt durch Prämien, «Free Cashflow» = Free Cashflow an die Holding (Mio. €), «ROIC» = Eigenkapitalrendite. Zahlen in Euro. Seit 2023 gilt die neue Rechnungslegung IFRS 17, darum sind Prämien und operatives Ergebnis vor 2023 nicht vergleichbar (–). Gewinn pro Aktie laut StockAnalysis, er schwankt stark mit den Kapitalmärkten. Prämien, operatives Ergebnis und Free Cashflow laut Finanzberichten von NN, letzte 12 Monate eigene Rechnung aus den Halbjahren 2H25 und 1H26. KGV 2024 und 2025 eigene Rechnung mit dem Jahresendkurs.",
"FIN": [["2021","–","–","–",10.41,1232,"–","–"],["2022","–","–","–",5.33,"–","–","–"],["2023",13187,"–","19.2 %",4.04,470,"–","–"],["2024",13978,"+6.0 %","18.4 %",5.58,1519,"–","7.6"],["2025",13256,"−5.2 %","22.6 %",4.17,1620,"–","15.8"],["Letzte 12 Mt.",13243,"−1.9 %","23.2 %",6.79,1679,"9.7 %","11.5"]],
"QREV": [["1H 23",7.24],["2H 23",5.94],["1H 24",7.94],["2H 24",6.04],["1H 25",7.46],["2H 25",5.79],["1H 26",7.45]],
"revdec": 2,
"MARGIN": [["2023",19.2],["2024",18.4],["2025",22.6],["12 Mt.",23.2]],
"Q": [
 ["Umsatztrend","Ersatz Bruttoprämien, Halbjahre gegen Vorjahr: nur 1 von 4 höher (2H24 +1.6 %, dann −6.0 %, −4.1 %, −0.2 %). Das operative Ergebnis stieg dagegen 4 von 4 Halbjahren",0,15],
 ["Wachstumstempo","Firmenangabe: Kapitalgenerierung (OCG) als Wachstumsmass, 12 Monate bis Juni 2026 +8.0 % (eigene Rechnung), 1. Halbjahr 2026 +5.2 %",6,10],
 ["Operative Marge","Ersatz operatives Ergebnis pro Prämie: 23.2 % (6 Pkt.), seit 2023 von 19.2 % gestiegen (6 Pkt.)",12,15],
 ["Gewinnwachstum (EPS)","Ersatz operatives Ergebnis, weil der Reingewinn mit den Märkten schwankt: 2023 bis 2025 +9.0 % pro Jahr (2'528 auf 3'002 Mio. €)",5,10],
 ["Free Cashflow","Ersatz Free Cashflow der Holding: immer positiv, aber schwankend (2023 nur 470 Mio. €, 2025 1'620 Mio. €). Kapitalgenerierung seit 2021 jedes Jahr höher",6,10],
 ["ROIC","Ersatz Eigenkapitalrendite: 9.7 % in 12 Monaten (eigene Rechnung), unter 10 %. Trend nicht verlässlich messbar",2,15],
 ["Schulden","Ersatz Financial Leverage 17.3 % und Zinsdeckung 13.5-fach, dazu Solvency-II-Quote 224 %: sehr wenig Schulden, entspricht der Stufe unter 1",9,10],
 ["Bewertung vs. eigene Historie","KGV 11.5 statt Ø 8.4, rund 37 % teurer",1,15]
],
"adwnote": ADW + "Positiv: In der Woche ab 17.8. (Tief 75.36 €) stand die Wochen-A/D bei 115.4, in der fast gleich tiefen Woche ab 5.10. (Tief 75.16 €) bei 117.6. Beim zweiten Test wurde weniger verkauft, eine leichte bullische Divergenz. Seit dem Hoch im September (121.6) fiel die A/D mit dem Kurs, heute 118.2.",
"rsiwnote": RSIW + "Beim Rekordhoch im Juli 75 (überkauft), beim Rücksetzer im Oktober 50, heute 56. Neutral, der Aufwärtstrend hat sich abgekühlt.",
"addnote": "Gemischt: Die Tages-A/D fiel vom Rekordhoch am 6.8. (25.7) bis zum Tief vom 9.10. (20.3), stärker als der Kurs. Beim Tief vom 9.10. lag sie tiefer als beim Tief vom 20.8. (22.8) bei fast gleichem Kurs: noch keine Käufer-Divergenz. Seit dem 23.10. steigt sie wieder leicht (heute 21.4).",
"ind": [
 ["Kurs vs. EMA 50","78.26 &gt; 77.38","78.26 &gt; 72.06","Knapp über der mittelfristigen Linie (Tag), klar darüber (Woche)."],
 ["Kurs vs. EMA 200","78.26 &gt; 73.58","78.26 &gt; 55.99","Über der langfristigen Linie, in der Woche rund 40 % darüber."],
 ["EMA 50 vs. EMA 200","50 über 200 (Golden Cross am 4.3.2025)","50 über 200 (Golden Cross Woche 5.5.2024)","Aufwärtstrend auf beiden Zeitebenen."],
 ["RSI (14)","57.0","55.9","Neutral. Tag drehte aus 37 (8.10.) nach oben."],
 ["A/D","fiel bis 9.10., steigt seit 23.10. leicht","höher als im August bei gleichem Kurs","Woche leicht positiv, Tag noch schwach."],
 ["Volumen","Ø 20 Tage 0.53 Mio. vs. Ø 100 Tage 0.54 Mio. Aktien","Normaler Handel."]
],
"smc": "Seit Anfang 2026 steigt NN mit höheren Hochs und höheren Tiefen: Tiefs 63.70 (9.3.), 70.72 (4.6.) und 75.36 € (20.8.), Hochs 72.78 (12.2.), 77.22 (25.6.) und 83.40 € (6.8., Rekord). Danach bildete sich eine Seitwärtsspanne zwischen rund 75 und 81 €: Hochs 80.52 (4.9.), 81.28 (21.9.) und 76.98 € (15.10.), Tiefs 76.22 (9.9.), 75.16 (9.10.) und 75.20 € (23.10.). Die Tiefs halten bei 75 €. Am 27.10. schloss der Kurs mit 77.62 € über dem letzten tieferen Hoch (76.98 €), ein kleiner Change of Character nach oben auf Tagesbasis. Bestätigt wäre er mit einem Tagesschluss über 81.28 €.",
"zones": [
 ["r","82.50–83.40 €","Widerstand: Rekordhoch vom 6.8.2026 (83.40 €)."],
 ["r","80.50–81.30 €","Widerstand: Hochs vom 4.9. (80.52) und 21.9. (81.28 €), obere Grenze der Spanne."],
 ["t","81.30 €","<b>Trigger:</b> Tagesschluss über 81.30 € (Hoch vom 21.9.), damit wäre die Seitwärtsspanne nach oben verlassen. Der kleinere Trigger (76.98 €) wurde am 27.10. schon überschritten."],
 ["s","75.00–76.50 €","<b>Kaufzone 1:</b> Mehrfach gehaltene Tiefs vom 20.8. (75.36), 9.10. (75.16) und 23.10. (75.20 €), knapp unter der Tages-EMA 50 (77.38 €)."],
 ["s","70.70–73.60 €","<b>Kaufzone 2:</b> Tief vom 4.6. (70.72 €), Wochen-EMA 50 (72.06 €) und Tages-EMA 200 (73.58 €)."],
 ["r","70.00 €","Abbruch: Wochenschluss unter 70 €, also unter dem Juni-Tief und der Wochen-EMA 50."]
],
"smart": [
 "<b>Rückkäufe:</b> 350 Mio. € Rückkauf seit 2.3.2026 über 10 Monate, bis 31.7.2026 zu 46 % erledigt (161 Mio. €). Das sind rund 1.7 % des Börsenwerts pro Jahr (eigene Rechnung), knapp unter der Schwelle von 2 %. Ziel bis 2028: jedes Jahr mindestens 350 Mio. €.",
 "<b>Insider:</b> Käufe der Führung am Markt in den letzten 6 Monaten habe ich nicht gefunden. Chef David Knibbe verkaufte 2025 Aktien für rund 0.84 Mio. € zu 55.87 € (Simply Wall St, 21.11.2025). Im Mai 2026 erhielt er Aktien als Lohnbestandteil (AFM-Register).",
 "<b>Grosse Investoren:</b> Zu Käufen grosser Fonds 2026 habe ich keine verlässlichen Daten gefunden.",
 "<b>Analysten:</b> Kursziel im Schnitt 82.42 € (13 Analysten, Stand 5.10.2026), rund 5 % über dem Kurs. Mehrheitlich Kaufen (Daten der App)."
],
"seasnote": SEAS + "Daten seit 2014 (12 Jahre, Oktober nur 1 Jahr). November ist mit +4.6 % und 67 % positiven Jahren stark, Dezember +0.6 % (58 %), Januar +1.4 % (67 %). Juni ist der stärkste Monat (+4.9 %), April der schwächste (−1.3 %).",
"T": [
 ["Trend Woche (EMA 50/200)","Kurs über beiden, EMA 50 klar über EMA 200",18,20],
 ["Trend Tag (EMA 50/200)","Kurs knapp über beiden, EMA 50 über EMA 200, EMA 50 flacht ab",9,10],
 ["Struktur (SMC)","Höhere Hochs und Tiefs seit März, seit August Spanne 75 bis 81 € mit haltenden Tiefs, kleiner Change of Character am 27.10.",14,20],
 ["RSI Tag/Woche","Tag dreht aus 37 nach oben, beim Tief vom 23.10. höherer RSI (45) als beim gleich tiefen Kurs am 9.10. (37): bullische Divergenz, Woche neutral (56)",13,15],
 ["A/D Tag/Woche","Woche leicht bullische Divergenz, Tag noch tiefer als im August",10,20],
 ["Smart Money","Start 3, keine Insider-Käufe, Rückkauf mit rund 1.7 % unter der Schwelle von 2 %",3,10],
 ["Saisonalität","November 67 %, Dezember 58 %, Januar 67 % positive Jahre",5,5]
],
"pro": [
 "Sehr starkes Kapitalpolster: Solvency-II-Quote 224 % (30.6.2026), Schulden mit 17.3 % Financial Leverage tief.",
 "Kapitalgenerierung seit 2021 jedes Jahr höher (1'584 auf 2'089 Mio. € 2025), Free Cashflow der Holding 1H26 +7 %.",
 "Hohe Ausschüttung: Dividende rund 5 % (seit 2021 jedes Jahr erhöht) plus mindestens 350 Mio. € Rückkauf pro Jahr.",
 "Wert des Neugeschäfts 1H26 +16 %, Insurance Europe (Polen, Rumänien und weitere) mit +19 % Kapitalgenerierung.",
 "Aufwärtstrend im Chart intakt, Tiefs bei 75 € mehrfach gehalten."
],
"con": [
 "Kaum Wachstum: Bruttoprämien sinken leicht (12 Monate −1.9 %), Ziel für die Kapitalgenerierung 2028 (2'200 Mio. €) liegt nur rund 5 % über 2025.",
 "Mit KGV 11.5 rund 37 % teurer als der eigene Schnitt (8.4), die Aktie hat sich seit Ende 2024 fast verdoppelt.",
 "Eigenkapitalrendite unter 10 %, Gewinn schwankt stark mit Zinsen und Aktienmärkten.",
 "Abhängig von den Niederlanden (über die Hälfte der Kapitalgenerierung), Pensionsreform dort bringt Chancen, aber auch Unsicherheit.",
 "Laut Firma wird der Verkauf über griechische Banken 2027 deutlich schwächer, die Solvency-Quote von NN Life sank auf 213 %."
],
"todo": [
 ["t","Beobachten","Alarm bei 76.50 € (oberer Rand Kaufzone 1), 81.30 € (Trigger) und 70 € (Abbruch)."],
 ["s","Timing grün","Tagesschluss über 81.30 €, danach neues Hoch über 83.40 € mit steigender Tages-A/D. Fundamental: Kapitalgenerierung 2026 über 2'089 Mio. € und Solvency-II-Quote über 200 %."],
 ["r","Abbruch","Wochenschluss unter 70 €."],
 ["","Nächste Zahlen","10. Februar 2027 (Jahreszahlen 2026, mit Vorschlag zur Schlussdividende). NN veröffentlicht nur Halbjahreszahlen. Generalversammlung 12.5.2027."]
],
"bands": [{"from":82.5,"to":83.4,"type":"res"},{"from":80.5,"to":81.3,"type":"res"},{"from":75.0,"to":76.5,"type":"sup"},{"from":70.7,"to":73.6,"type":"sup"}],
"refs": [{"v":81.3,"label":"Trigger 81.30"}],
"sources": L("https://www.nn-group.com/site/binaries/content/assets/nn-group/financial-results/2026/nn-group-press-release-1h26.pdf","NN Group: Halbjahreszahlen 2026") + ", " + L("https://www.nn-group.com/site/binaries/content/assets/nn-group/financial-results/2026/nn-group-financial-supplement-1h26.pdf","Financial Supplement 1H26") + ", " + L("https://www.nn-group.com/site/binaries/content/assets/nn-group/financial-results/2025/nn-group-press-release-fy25.pdf","NN Group: Jahreszahlen 2025") + ", " + L("https://www.nn-group.com/site/binaries/content/assets/nn-group/financial-results/2025/nn-group-financial-supplement-fy25.pdf","Financial Supplement FY25") + ", " + L("https://www.nn-group.com/site/binaries/content/assets/nn-group/financial-results/2024/nn-group-financial-supplement-2h24.pdf","Financial Supplement FY24") + ", " + L("https://www.nn-group.com/site/binaries/content/assets/nn-group/financial-results/2025/nn-group-analyst-presentation-fy25.pdf","Analystenpräsentation FY25 (Ziele 2028)") + ", " + L("https://www.nn-group.com/news/strong-ocg-and-resilient-commercial-performance-for-second-half-and-full-year-2022/","Jahreszahlen 2022") + ", " + L("https://stockanalysis.com/quote/ams/NN/financials/","StockAnalysis.com (NN)") + " (Stand 29.10.2026), " + L("https://www.ad-hoc-news.de/boerse/news/corporate-news/nn-group-stock-thirteen-analysts-set-eur-82-42-target-for-nn-group-stock/70341966","Analysten-Kursziel (ad-hoc-news, 16.10.2026)") + ", " + L("https://simplywall.st/stocks/nl/insurance/ams-nn/nn-group-shares/news/23-of-this-nn-group-insiders-holdings-were-sold","Insider-Verkauf (Simply Wall St)") + ", " + L("https://www.afm.nl/en/sector/registers/meldingenregisters/bestuurders-commissarissen/details?id=194084","AFM-Register") + ". Branchenvergleich der App: Note 2.7 von 5, fairer Wert rund 106 € (36 % über dem Kurs), Unsicherheit hoch."
}
if __name__ == "__main__":
    json.dump(c, open(os.path.join(P, "config", "NN.json"), "w"), ensure_ascii=False, indent=1)
    print("ok", sum(r[2] for r in c["Q"]), sum(r[2] for r in c["T"]))
