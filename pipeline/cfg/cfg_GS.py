import json, os, sys
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, P)
from helpers import L, ADW, RSIW, SEAS
c = {
"ticker": "GS", "name": "Goldman Sachs", "datum": "11.11.2026", "waehrung": "USD", "land": "USA",
"meta": "The Goldman Sachs Group, Inc. · NYSE: GS · Investmentbank, Wertschriftenhandel und Vermögensverwaltung · New York, USA",
"price": "926.81 $",
"pricemeta": "Schluss 11.11.2026 · 52 Wochen: 754.00 – 1'153.99 $ · Allzeithoch 1'153.99 $ am 15.7.2026 · Börsenwert rund 278 Mrd. $",
"verdict": "Goldman Sachs ist eine der grössten Investmentbanken der Welt. 2026 läuft das Geschäft sehr gut: Umsatz in 12 Monaten rund +19 %, Gewinn pro Aktie 69.49 $ (2025: 51.32 $), Eigenkapitalrendite 18.7 % im letzten Quartal. Trotzdem liegt die Aktie 20 % unter dem Allzeithoch vom Juli. Gründe: steigende Zinsen, Sorgen um Inflation und der Börsenrutsch vom 5.11. Qualität hellgrün (68): stark im Moment, aber das Geschäft schwankt mit den Börsen, und der Kapitalpuffer ist zuletzt kleiner geworden. Timing gelb (51): Seit Oktober pendelt der Kurs zwischen 854 und 940 $. Ein Tagesschluss über 940 $ wäre das erste Zeichen für eine Wende.",
"about": "Goldman Sachs verdient auf drei Arten. Global Banking & Markets (rund 74 % des Umsatzes 2026): Beratung bei Firmenkäufen und Börsengängen (Investment Banking), dazu der Handel mit Aktien, Anleihen, Währungen und Rohstoffen für grosse Kunden wie Pensionskassen und Hedgefonds. Asset & Wealth Management (rund 24 %): Verwaltung von Vermögen für reiche Privatkunden und Institutionen sowie eigene Beteiligungen. Platform Solutions (rund 1 %): das frühere Konsumentengeschäft (Kreditkarten), das Goldman abbaut. Wichtig für Anfänger: Bei einer Bank sind Kennzahlen wie Free Cashflow oder Nettoschulden kaum aussagekräftig, weil Schulden und Kundengelder das Rohmaterial des Geschäfts sind. Wichtiger sind die Eigenkapitalrendite (ROE) und das harte Kernkapital (CET1).",
"why": "2025 stieg die Aktie um rund 56 %. Am 15.7.2026 erreichte sie das Allzeithoch von 1'153.99 $, getragen von einem Boom bei Firmenkäufen und im Aktienhandel (Umsatz im Quartal bis Juni +39.5 %). Danach fiel sie: Die Zinsen für 10-jährige US-Staatsanleihen stiegen auf rund 5.3 %, die US-Notenbank erhöht die Zinsen wieder. Am 8.10. lag die Aktie über 20 % unter dem Hoch, nachdem sie in 10 von 12 Wochen gefallen war. Am 13.10. meldete Goldman starke Zahlen (Gewinn pro Aktie 17.01 $ statt rund 13 $ erwartet, Aktienhandel +72 %). Am Tag danach fiel der Kurs trotzdem um 2.1 %, weil die Inflation mit 3.7 % höher als erwartet war. Der Auftragsbestand im Investment Banking lag unter dem Stand vom Juni. Am 5.11. fiel Goldman in einem breiten Börsenrutsch um 6.1 % bis 854.45 $. Seither erholte sich der Kurs auf 926.81 $.",
"kpis": [
 ["g","Umsatzwachstum","+18.7 %","Letzte 12 Monate (bis September 2026), selbst gerechnet aus den Firmenzahlen. 3 der letzten 4 Quartale über dem Vorjahr. Achtung: Bankumsätze schwanken mit der Börse, 2022 fiel der Umsatz um 24 %."],
 ["g","Vorsteuermarge","39.3 %","Von 100 $ Umsatz bleiben 39 $ Gewinn vor Steuern (letzte 12 Monate). Für eine Bank sehr gut. 2023 waren es nur 24 %."],
 ["g","Gewinn pro Aktie (EPS)","69.49 $","Letzte 12 Monate. 2025 waren es 51.32 $ (+35 %), 2023 nur 22.87 $. Im letzten Quartal 17.01 $, ohne eine Spende von rund 450 Mio. $ laut Finanzchef rund 18 $."],
 ["g","Eigenkapitalrendite (ROE)","17.7 %","Auf 100 $ Eigenkapital der Aktionäre verdient Goldman knapp 18 $ pro Jahr (letzte 12 Monate, im letzten Quartal 18.7 %). Für eine Bank stark, 2025 waren es 15.0 %. Bei Banken ersetzt die ROE den ROIC."],
 ["w","Kernkapital (CET1)","12.4 %","Das harte Eigenkapital im Verhältnis zu den Risiken. Vorgeschrieben sind 11.4 %. Der Puffer ist mit 1 Prozentpunkt eher knapp und seit Ende 2025 (14.4 %) gesunken, weil Goldman viel zurückkauft und mehr Risiko nimmt."],
 ["w","Free Cashflow","nicht aussagekräftig","Bei Banken schwankt der Cashflow mit den Handelsbeständen und Kundengeldern (2025: −47 Mrd. $). Er sagt wenig über die Qualität aus."],
 ["w","KGV","13.3","Du zahlst gut 13 Jahresgewinne. Eigener Schnitt 2021 bis 2025: rund 12.7. Also etwa normal bewertet. Kurs-Buchwert-Verhältnis 2.5: Du zahlst das 2.5-Fache des Eigenkapitals."],
 ["g","Dividende","2.2 %","5.00 $ pro Quartal, 4× pro Jahr. Nächster Ex-Tag 2.12.2026, Zahltag 30.12.2026. Nach dem Stresstest im Sommer 2026 um 11 % erhöht (von 4.50 $). In USD, 15 % US-Quellensteuer (mit W-8BEN), in der Steuererklärung anrechenbar."]
],
"revtitle": "Nettoumsatz pro Quartal (Mio. $)", "revunit": "Mio. $", "epsunit": "$",
"revnote": "3 der letzten 4 Quartale über dem Vorjahr: −3.0 % (Dez 25), +14.4 % (Mär 26), +39.5 % (Jun 26), +23.0 % (Sep 26). Das Quartal bis Juni 2026 war das beste der Firmengeschichte.",
"marginnote": "Vorsteuermarge pro Jahr (Banken haben keine klassische operative Marge). Stark von der Börse abhängig: 2021 Boom, 2023 Tief, seither wieder steigend.",
"finnote": "<b>Hinweis für Banken:</b> Die Spalte «Op. Marge» zeigt die Vorsteuermarge, die Spalte «ROIC» die Eigenkapitalrendite (ROE, nur wo von Goldman bestätigt). Der Free Cashflow ist bei Banken nicht aussagekräftig. Umsätze laut StockAnalysis, sie weichen leicht von Goldmans eigenem Nettoumsatz ab (2025: 58.28 Mrd. $). KGV zum Jahresende, 2025 selbst gerechnet, letzte Zeile mit dem Kurs vom 11.11.2026.",
"FIN": [["2021",58982,"+42.3 %","45.9 %",59.45,1631,"–","5.9"],["2022",44650,"−24.3 %","30.2 %",30.06,4960,"–","10.7"],["2023",45226,"+1.3 %","23.8 %",22.87,-14903,"–","16.3"],["2024",52164,"+15.3 %","35.3 %",40.54,-15303,"–","13.9"],["2025",59396,"+13.9 %","36.8 %",51.32,-47218,"15.0 %","17.1"],["Letzte 12 Mt.",71036,"+23.9 %","39.3 %",69.49,"–","17.7 %","13.3"]],
"QREV": [["Dez 24",13869],["Mär 25",15062],["Jun 25",14583],["Sep 25",15184],["Dez 25",13450],["Mär 26",17227],["Jun 26",20338],["Sep 26",18679]],
"revdec": 0,
"MARGIN": [["2021",45.9],["2022",30.2],["2023",23.8],["2024",35.3],["2025",36.8],["12 Mt.",39.3]],
"Q": [
 ["Umsatztrend","3 von 4 Quartalen über Vorjahr",8,15],
 ["Wachstumstempo","+18.7 % in 12 Monaten (Boomphase, schwankt stark)",10,10],
 ["Operative Marge","Vorsteuermarge 39.3 % (9 Pkt.), über 5 Jahre schwankend (3 Pkt.)",12,15],
 ["Gewinnwachstum (EPS)","2025 +27 %, letzte 12 Monate +35 % zu 2025",10,10],
 ["Free Cashflow","Bei Banken nicht aussagekräftig (Daten fehlen: halbe Punkte)",5,10],
 ["ROIC","Bei Banken ROE: 17.7 % (10 Pkt.), steigend (+1)",11,15],
 ["Schulden","Nettoschulden/EBITDA bei Banken nicht anwendbar. CET1 12.4 % bei 11.4 % Pflicht: halbe Punkte",5,10],
 ["Bewertung vs. eigene Historie","KGV 13.3 statt Ø 12.7, im Bereich ±10 %",7,15]
],
"adwnote": ADW + "Negativ: Im Juni 2026 stand die Wochen-A/D bei 245, heute bei 195. Sie fällt seit dem Sommer mit dem Kurs. In der Erholung der letzten Tage stieg sie kaum (194.4 → 195.0). Grosse Käufe sind noch nicht zu sehen.",
"rsiwnote": RSIW + "Im Oktober bis 34 gefallen, heute 46.7: neutral, kein Signal.",
"addnote": "Leicht negativ: Am 29.10. schloss der Kurs bei 927.73 $ mit einer Tages-A/D von 48.2. Heute schliesst er gleich hoch (926.81 $), die A/D liegt aber tiefer bei 45.9. Im Oktober-Tief (8.10.) lag sie noch bei 51.3.",
"ind": [
 ["Kurs vs. EMA 50","926.8 ≈ 926.8 (genau darauf)","926.8 &gt; 917.0","Kurs testet die mittelfristige Linie von unten."],
 ["Kurs vs. EMA 200","926.8 &lt; 935.4","926.8 &gt; 670.7","Im Tageschart knapp unter der langfristigen Linie, im Wochenchart weit darüber."],
 ["EMA 50 vs. EMA 200","50 unter 200 (seit 28.10.2026)","50 über 200 (seit Dezember 2020)","Tag: frisches Abwärtssignal. Woche: langfristiger Aufwärtstrend intakt."],
 ["RSI (14)","54.6","46.7","Neutral, im Tageschart steigend."],
 ["A/D","tiefer bei gleichem Kurs","fällt seit Juni","Auf beiden Zeitebenen eher Verkäufe."],
 ["Volumen","Ø 20 Tage 2.14 Mio. vs. Ø 100 Tage 2.09 Mio. Aktien","Normaler Handel."]
],
"smc": "Vom Allzeithoch 1'153.99 $ (15.7.) fiel Goldman mit tieferen Hochs (1'077.21 → 1'063.52 → 1'043.84 $) und tieferen Tiefen (977.70 → 996.97 → 922.00 $). Seit Oktober läuft der Kurs seitwärts zwischen rund 854 und 940 $: Tiefs bei 868.52 $ (7.10.), 859.03 $ (15.10.) und 854.45 $ (5.11.), Hochs bei 931.00 $ (13.10.), 939.38 $ (29.10.) und 934.00 $ (5.11.). Das Tief vom 5.11. lag nur wenig unter den früheren Tiefs und wurde noch am selben Tag zurückgekauft (Fehlausbruch nach unten). Im Tages-RSI ist das Tief vom 5.11. höher als am 15.10. (41 gegen 37): eine bullische Divergenz. Ein Tagesschluss über 940 $ wäre ein Change of Character nach oben.",
"zones": [
 ["r","997–1'045 $","Widerstand: Tiefs vom August und September (996.97 bis 1'001.68 $) und Hoch vom 8.9. (1'043.84 $)."],
 ["r","935–940 $","Widerstand: Obergrenze der Seitwärtsspanne (939.38 $) und Tages-EMA 200 (935.39 $)."],
 ["t","940 $","<b>Trigger:</b> Tagesschluss über 940 $ (Hoch vom 29.10.). Bestätigung über 1'000 $."],
 ["s","854–870 $","<b>Kaufzone 1:</b> Untergrenze der Seitwärtsspanne, Tiefs vom 7.10., 15.10. und 5.11. (854.45 bis 868.52 $)."],
 ["s","780–825 $","<b>Kaufzone 2:</b> Tief vom März 2026 (780.50 $) und altes Hoch vom September 2025 (825.25 $)."],
 ["r","850 $","Abbruch: Wochenschluss unter 850 $. Dann wäre die Seitwärtsspanne nach unten gebrochen."]
],
"smart": [
 "<b>Goldman selbst:</b> Grosse Rückkäufe. In 12 Monaten rund 15 Mrd. $ (rund 5.4 % des Börsenwerts), im 3. Quartal 3 Mrd. $ zu durchschnittlich 1'048.73 $. Die Aktienzahl sank in einem Jahr um 4.6 %. Programm bis 40 Mrd. $ (seit 2025).",
 "<b>Insider:</b> Keine Käufe. In 12 Monaten Verkäufe für rund 158 Mio. $ (GuruFocus). CEO David Solomon verkaufte am 27.10.2026 für rund 11 Mio. $, ohne festen Verkaufsplan. Laut GuruFocus haben 3 bekannte Investoren aufgestockt, 11 reduziert.",
 "<b>Analysten:</b> Eher vorsichtig. StockAnalysis: 26 Analysten, 9× Kaufen, 15× Halten, 2× Verkaufen, Kursziel im Schnitt 1'031 $ (730 bis 1'250 $). Nach den Zahlen meist gesenkte Ziele: RBC 1'220 → 1'010 $, KBW 1'130 → 1'100 $, BMO 970 → 950 $."
],
"seasnote": SEAS + "Seit 1999. November im Schnitt +3.0 % (89 % positive Jahre, nur 9 Jahre auswertbar), Dezember +3.1 % (63 %), Januar +1.7 % (52 %). Stärkster Monat September (+4.2 %, 75 %).",
"T": [
 ["Trend Woche (EMA 50/200)","Kurs knapp über beiden, EMA 50 über 200",18,20],
 ["Trend Tag (EMA 50/200)","Kurs auf EMA 50, unter EMA 200, EMA 50 unter 200 (mögliche Wende)",4,10],
 ["Struktur (SMC)","Seitwärts 854–940 $ nach Abwärtstrend, Tiefs nicht höher, Fehlausbruch am 5.11.",6,20],
 ["RSI Tag/Woche","Bullische Divergenz im Tag (Tief 5.11. mit höherem RSI), Woche neutral",11,15],
 ["A/D Tag/Woche","Beide fallen mit dem Kurs",4,20],
 ["Smart Money","Start 3, Rückkäufe 5.4 % +3, gehäufte Insider-Verkäufe −3",3,10],
 ["Saisonalität","November und Dezember überwiegend positiv (89 % und 63 %)",5,5]
],
"pro": [
 "Seit Jahren einer der führenden Berater bei Firmenkäufen, Rekord bei den Beratungsgebühren im letzten Quartal.",
 "Rekordnahe Zahlen: Gewinn pro Aktie +35 %, Aktienhandel im letzten Quartal +72 %, ROE 18.7 %.",
 "Vermögensverwaltung (rund ein Viertel des Umsatzes) bringt stabilere Einnahmen.",
 "Grosse Rückkäufe (rund 5 % pro Jahr) und Dividende 2.2 %, im Sommer um 11 % erhöht.",
 "Bullische RSI-Divergenz, Fehlausbruch unter die Spanne am 5.11., gute Saisonalität im November und Dezember."
],
"con": [
 "Das Geschäft hängt stark von der Börse ab. In schwachen Jahren fällt der Gewinn schnell (2022 −49 %, 2023 −24 %).",
 "Kapitalpuffer knapp: CET1 12.4 % bei 11.4 % Pflicht, gesunken von 14.4 %.",
 "Steigende Zinsen und Inflation belasten, Auftragsbestand im Investment Banking unter dem Stand vom Juni.",
 "Kosten im letzten Quartal rund +20 %, Kreditrückstellungen deutlich höher.",
 "Insider verkaufen, A/D fällt auf beiden Zeitebenen, Abwärtstrend seit Juli."
],
"todo": [
 ["t","Beobachten","Alarm bei 940 $ (Trigger) und bei 870 $ (oberes Ende Kaufzone 1)."],
 ["s","Timing grün","Tagesschluss über 940 $ mit steigender A/D, danach über 1'000 $. Fundamental: Investment-Banking-Auftragsbestand steigt wieder, CET1 bleibt über 12 %."],
 ["r","Abbruch","Wochenschluss unter 850 $. Dann Kaufzone 2 (780–825 $) beobachten."],
 ["","Nächste Zahlen","19. Januar 2027 vor US-Börsenbeginn (rund 13:30 Uhr Schweizer Zeit), 4. Quartal 2026."]
],
"bands": [{"from":997,"to":1045,"type":"res"},{"from":935,"to":940,"type":"res"},{"from":854,"to":870,"type":"sup"},{"from":780,"to":825,"type":"sup"}],
"refs": [{"v":940,"label":"Trigger 940"}],
"sources": L("https://stockanalysis.com/stocks/gs/financials/","StockAnalysis.com") + " (Stand 11.11.2026), " + L("https://www.sec.gov/Archives/edgar/data/0000886982/000088698226000529/a3q26gsearningsresults.htm","Goldman Sachs Q3 2026") + ", " + L("https://goldmansachs.com/pressroom/press-releases/2026/2026-01-15-q4-results","Goldman Sachs Q4 2025") + ", " + L("https://www.goldmansachs.com/pressroom/press-releases/2026/gs-statement-on-comprehensive-capital-analysis-and-review-2026-results","Stresstest 2026") + ", " + L("https://stockanalysis.com/stocks/gs/dividend/","Dividende") + ", " + L("https://finance.yahoo.com/markets/article/goldman-sachs-stock-loses-nearly-all-year-to-date-gains-as-bond-yields-rise-141150928.html","Yahoo: Zinsen belasten") + ", " + L("https://www.tikr.com/blog/goldman-sachs-stock-q3-2026-earnings-beat-equities-surge","TIKR: Q3 2026") + ", " + L("https://stockanalysis.com/stocks/gs/forecast/","Analysten") + ", " + L("https://secure.macrotrends.net/stocks/charts/GS/goldman-sachs/pe-ratio","Macrotrends: KGV") + "."
}
if __name__ == "__main__":
    json.dump(c, open(os.path.join(P, "config", "GS.json"), "w"), ensure_ascii=False, indent=1)
    print("ok", sum(r[2] for r in c["Q"]), sum(r[2] for r in c["T"]))
