import json, os, sys
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, P)
from helpers import L, ADW, RSIW, SEAS
c = {
"ticker": "1211", "name": "BYD", "datum": "28.10.2026", "waehrung": "HKD", "land": "China",
"meta": "BYD Company Limited · Hongkong: 1211 (H-Aktie, in Hongkong-Dollar), auch Shenzhen: 002594 · Elektroautos, Batterien, Elektronik · Shenzhen, China",
"price": "70.45 HKD",
"pricemeta": "Schluss 28.10.2026 · 52 Wochen: 67.10 – 113.40 HKD · Hoch Mai 2025: rund 159 HKD (umgerechnet auf heutige Aktienzahl) · 1 Lot = 100 Aktien = rund 7'045 HKD, etwa 700 CHF",
"verdict": "BYD ist der grösste Hersteller von Elektro- und Hybridautos der Welt und baut die Batterien selbst. Das Geschäft schrumpft aber gerade: Umsatz im 1. Halbjahr 2026 −7 %, Gewinn −21 %, in China fiel der Absatz im September um 13 %. Stark wächst nur das Ausland (+154 % im September). 2025 floss wegen hoher Investitionen rund 98 Mrd. Yuan mehr Geld ab als herein (Free Cashflow negativ). Die Marge ist mit rund 4 % dünn. Mit einem KGV von rund 19 ist die Aktie nicht mehr teuer, aber auch nicht billig gegen den eigenen Schnitt (20). Qualität rot (24), Timing orange (43): Der Abwärtstrend seit April ist intakt, erste Zeichen von Käufern gibt es (A/D steigt). Die Zahlen zum 3. Quartal kommen am 29.10.2026. Keine Anlageberatung.",
"about": "BYD («Build Your Dreams») aus Shenzhen begann 1995 mit Handy-Akkus. Allein im 1. Halbjahr 2026 verkaufte BYD rund 1.81 Mio. Autos, alle mit Elektro- oder Plug-in-Hybrid-Antrieb, unter den Marken BYD, Denza, Fang Cheng Bao und Yangwang. Rund 80 % des Umsatzes kommen aus Autos, rund 20 % aus Elektronik (Tochter BYD Electronic baut Teile für Handys und andere Geräte). Der grosse Vorteil: BYD macht fast alles selbst, von der Batterie («Blade Battery») über Chips bis zu Elektromotoren, und kann darum günstig bauen. Gründer und Chef Wang Chuanfu ist der grösste Einzelaktionär. Fabriken im Ausland laufen in Thailand an, Indonesien, Brasilien und Ungarn folgen (Stand Juni 2026). Die Aktie wird in Hongkong (1211, in HKD) und in Shenzhen (002594, in Yuan) gehandelt. In Hongkong kauft man in Lots: bei BYD seit 19.9.2025 100 Aktien pro Lot, also heute rund 7'045 HKD (etwa 700 CHF, mit 1 HKD = rund 0.10 CHF). Weniger als 1 Lot kannst du an der Börse Hongkong in der Regel nicht kaufen.",
"why": "Im Juli 2025 gab BYD pro 10 Aktien 20 neue Aktien gratis aus (8 als Gratisaktien und 12 aus Reserven, Juli 2025), die Zahl der Aktien hat sich also verdreifacht. Alle Kurse und Gewinne pro Aktie auf dieser Seite sind darauf umgerechnet. Die Aktie erreichte im Mai 2025 umgerechnet rund 159 HKD. Danach drückte der Preiskampf in China: BYD senkte die Preise, der Gewinn fiel 2025 um 19 % und im 4. Quartal 2025 um 38 %. Berkshire Hathaway von Warren Buffett hat seine Beteiligung bis 2025 ganz verkauft. Seit Januar 2026 gibt es in China nur noch die halbe Steuerbefreiung für Elektroautos, darum kauften viele Leute schon Ende 2025. Dazu kam ein Engpass bei der neuen Batterie (zweite Generation der Blade Battery), der die Auslieferungen bremste. Im 1. Quartal 2026 fiel der Gewinn um 55 %. Seit April (113.40 HKD) fällt die Aktie wieder, am 22.10.2026 auf 67.10 HKD, auch weil der ganze Automarkt in China schwach ist (Verkäufe an Kunden 1. bis 18.10. −26 %, ganze Branche). Gegenwind ist also echt, aber nicht nur Stimmung: Die Firma verdient weniger und investiert sehr viel.",
"kpis": [
 ["r","Umsatzwachstum","−8.2 %","Letzte 12 Monate bis Juni 2026, eigene Rechnung. 1. Halbjahr 2026: −7.1 %. In China sinkt der Absatz, im Ausland steigt er stark (Juli bis September jeden Monat zweistellig)."],
 ["r","Operative Marge","4.1 %","Von 100 Yuan Umsatz bleiben nur rund 4 Yuan Betriebsgewinn (12 Monate bis März 2026). 2024 waren es 6.4 %. Autobauer haben meist dünne Margen, BYD liegt im Mittelfeld."],
 ["r","Gewinn pro Aktie (EPS)","3.24 RMB","Letzte 12 Monate bis Juni 2026, eigene Rechnung. 2024: 4.61 RMB, 2025: 3.58 RMB. Der Gewinn sinkt seit zwei Jahren. Im 2. Quartal 2026 stieg er wieder um 30 %."],
 ["w","ROIC","rund 11 %","Auf 100 Yuan investiertes Kapital rund 11 Yuan Gewinn (Daten der App, TipRanks rechnet 7.4 %). Mittelmässig und sinkend."],
 ["r","Free Cashflow","−88 Mrd. RMB","Letzte 12 Monate bis März 2026. 2025: −98 Mrd. RMB, weil BYD sehr viel in Fabriken im Ausland investiert und Lieferanten schneller bezahlt. Bis 2024 war der Wert jedes Jahr positiv."],
 ["g","Schulden","gering","Laut App-Daten mehr Geld als Bankschulden. TipRanks rechnet mit Leasing rund 0.6 Jahres-EBITDA Nettoschulden. Beides ist wenig. Achtung: BYD schuldet den Lieferanten sehr viel Geld (offene Rechnungen)."],
 ["w","KGV","18.9","Du zahlst rund 19 Jahresgewinne. Eigener Schnitt der letzten 5 Jahre: 20.3. Also etwa normal bewertet. Auf den von Analysten erwarteten Gewinn wäre das KGV rund 10, das setzt aber eine starke Erholung voraus."],
 ["r","Dividende","0.6 %","Zuletzt 0.358 RMB pro Aktie, ausbezahlt als 0.411 HKD (Ex-Tag 11.6.2026, bezahlt am 31.7.2026). Nur 1 Zahlung pro Jahr, für 2025 um rund 73 % gekürzt (nur noch 10 % des Gewinns)."]
],
"revtitle": "Umsatz pro Quartal (Mrd. RMB)", "revunit": "Mrd. RMB", "epsunit": "RMB",
"revnote": "Seit dem 3. Quartal 2025 liegt jedes Quartal unter dem Vorjahr (−3 %, −14 %, −12 %, −3 %). Das 2. Quartal 2026 war fast wieder auf Vorjahreshöhe. Q1 26 und Q2 26: eigene Rechnung aus Halbjahres- und Quartalszahlen.",
"marginnote": "Betriebsgewinn pro 100 Yuan Umsatz. Von 3 % (2021) auf 6.4 % (2024) gestiegen, dann wegen des Preiskampfs auf rund 4 % gefallen.",
"finnote": "<b>Hinweis:</b> Zahlen in chinesischen Yuan (RMB, Umsatz und Free Cashflow in Mio.), Kurs in Hongkong-Dollar. 1 RMB = rund 1.15 HKD (Juni 2026). EPS auf die heutige Aktienzahl umgerechnet (Gratisaktien Juli 2025). Umsatz, Marge, EPS und Free Cashflow laut StockAnalysis, letzte 12 Monate eigene Rechnung mit den Halbjahreszahlen 2026 (Free Cashflow bis März 2026). ROIC pro Jahr nicht verfügbar. KGV: 2024 und 2025 eigene Rechnung mit dem Jahresendkurs, heute laut App-Daten. 2021 war das KGV über 100, weil der Gewinn fast null war.",
"FIN": [["2021",216142,"+38.0 %","3.0 %",0.35,28123,"–","über 100"],["2022",424061,"+96.2 %","5.0 %",1.90,43381,"–","–"],["2023",602315,"+42.0 %","5.7 %",3.44,47632,"–","–"],["2024",777102,"+29.0 %","6.4 %",4.61,36094,"–","17.5"],["2025",803965,"+3.5 %","4.2 %",3.58,-97672,"–","24.8"],["Letzte 12 Mt.",777499,"−8.2 %","4.1 %",3.24,-88249,"rund 11 %","18.9"]],
"QREV": [["Q3 24",201.1],["Q4 24",274.9],["Q1 25",170.4],["Q2 25",200.9],["Q3 25",195.0],["Q4 25",237.7],["Q1 26",150.2],["Q2 26",194.6]],
"revdec": 1,
"MARGIN": [["2021",3.0],["2022",5.0],["2023",5.7],["2024",6.4],["2025",4.2],["12 Mt.",4.1]],
"Q": [
 ["Umsatztrend","0 von 4 Quartalen über Vorjahr (−3 %, −14 %, −12 %, −3 %)",0,15],
 ["Wachstumstempo","−8 % in 12 Monaten bis Juni 2026",0,10],
 ["Operative Marge","4.1 % (0 Pkt.), über 5 Jahre gestiegen, seit 2024 gefallen: stabil (3 Pkt.)",3,15],
 ["Gewinnwachstum (EPS)","2025 −22 %, 1. Halbjahr 2026 −21 %. Der Schnitt seit 2022 (+24 % pro Jahr) ist überholt",0,10],
 ["Free Cashflow","2025 und letzte 12 Monate klar negativ (−98 und −88 Mrd. RMB)",0,10],
 ["ROIC","Rund 11 % (6 Pkt.), fallend (−1)",5,15],
 ["Schulden","Netto-Cash laut App, mit Leasing rund 0.6 × EBITDA (TipRanks)",9,10],
 ["Bewertung vs. eigene Historie","KGV 18.9 statt Ø 20.3, rund 7 % günstiger: im Bereich ±10 %",7,15]
],
"adwnote": ADW + "Positiv: Der Kurs schloss im Juni bei 72.65 HKD (Woche ab 22.6.), heute tiefer bei 70.45 HKD. Die Wochen-A/D steht heute aber höher (−275 statt −428). Beim tieferen Kurs wird weniger stark verkauft: eine bullische Divergenz. Seit August fällt die Wochen-A/D allerdings wieder.",
"rsiwnote": RSIW + "Im Juni bei 27 (überverkauft), heute 34 bei tieferem Kurs. Auch das ist eine bullische Divergenz, aber noch schwach.",
"addnote": "Positiv: Am 10.9. schloss BYD bei 79.55 HKD mit Tages-A/D 144, heute bei 70.45 HKD mit A/D 164. Seit dem Tief vom 22.10. (67.10 HKD) stieg die Tages-A/D von 122 auf 164. Käufer greifen bei diesen Kursen zu.",
"ind": [
 ["Kurs vs. EMA 50","70.45 &lt; 78.24","70.45 &lt; 90.23","Klar unter der mittelfristigen Linie, auf beiden Zeitebenen."],
 ["Kurs vs. EMA 200","70.45 &lt; 89.51","70.45 &lt; 89.10","Rund 21 % unter der langfristigen Linie."],
 ["EMA 50 vs. EMA 200","50 unter 200 (Todeskreuz am 10.9.2025)","50 noch knapp über 200 (90.23 zu 89.10), Abstand schrumpft","Tag im Abwärtstrend, in der Woche droht ein Todeskreuz."],
 ["RSI (14)","37.4","33.5","Beide schwach, nahe überverkauft. Tag drehte aus 23 nach oben."],
 ["A/D","steigt seit 22.10.","höher als im Juni trotz tieferem Kurs","Beide Zeitebenen mit bullischer Divergenz."],
 ["Volumen","Ø 20 Tage 19.3 Mio. vs. Ø 100 Tage 21.2 Mio. Aktien","Etwas weniger Handel als üblich."]
],
"smc": "Seit dem Hoch vom 16.4.2026 (113.40 HKD) fällt BYD mit tieferen Hochs und tieferen Tiefs: Hochs 109.10 (30.4.), 96.65 (3.8.), 94.85 (25.8.), 82.00 (22.9.) und 77.60 HKD (12.10.), Tiefs 88.80 (28.5.), 71.40 (30.6.), 77.80 (17.9.), 72.75 (5.10.) und 67.10 HKD (22.10.). Das Tief vom 22.10. liegt unter dem Juni-Tief, der Abwärtstrend ist also bestätigt. Ein Change of Character nach oben wäre ein Tagesschluss über 77.60 HKD (letztes tieferes Hoch). Knapp darüber liegt die Tages-EMA 50 (78.24 HKD).",
"zones": [
 ["r","86.60–91.00 HKD","Widerstand: Tages-EMA 200 (89.51), Wochen-EMAs (89.10 und 90.23) und Tief vom 23.7. (86.60 HKD)."],
 ["r","77.60–82.00 HKD","Widerstand: Hochs vom 12.10. und 22.9., Tages-EMA 50 (78.24 HKD)."],
 ["t","77.60 HKD","<b>Trigger:</b> Tagesschluss über 77.60 HKD (letztes tieferes Hoch vom 12.10.), besser mit weiter steigender Tages-A/D."],
 ["s","67.00–71.50 HKD","<b>Kaufzone 1:</b> 52-Wochen-Tief vom 22.10. (67.10) und Juni-Tief (71.40 HKD). Der Kurs steht heute darin, das Timing ist aber noch nicht bestätigt."],
 ["s","56.00–60.00 HKD","<b>Kaufzone 2:</b> KGV von rund 15 bis 16 auf den heutigen Gewinn (eigene Rechnung) und Bereich der Tiefs Anfang 2024 (umgerechnet rund 56 HKD, nicht in den Rohdaten, darum unsicher)."],
 ["r","66.00 HKD","Abbruch: Wochenschluss unter 66 HKD, also klar unter dem 52-Wochen-Tief."]
],
"smart": [
 "<b>Rückkäufe:</b> 2026 habe ich kein grösseres Rückkaufprogramm gefunden. Die Dividende für 2025 wurde um rund 73 % gekürzt.",
 "<b>Insider:</b> Gründer Wang Chuanfu ist der grösste Einzelaktionär. Käufe der Führung am Markt in den letzten 6 Monaten habe ich nicht gefunden. An der Generalversammlung vom 9.6.2026 sagte Wang, die Aktie sei unterbewertet.",
 "<b>Grosse Investoren:</b> Berkshire Hathaway (Warren Buffett) hat seine Beteiligung bis 2025 ganz verkauft. Zu Käufen grosser Fonds 2026 habe ich keine verlässlichen Daten gefunden.",
 "<b>Analysten:</b> Kursziel im Schnitt rund 123 HKD (26 Analysten, mehrheitlich Kaufen, Daten der App vom 24.10.2026). CLSA senkte am 23.10.2026 von 120 auf 104 HKD, Bernstein hält 130 HKD."
],
"seasnote": SEAS + "Daten seit 2002. Februar (+8.3 %, 75 %) und Juli (+4.8 %, 58 %) sind stark, August (−2.1 %, 44 %) und Dezember (−2.0 %, 50 %) schwach. November +0.7 % mit 54 % positiven Jahren.",
"T": [
 ["Trend Woche (EMA 50/200)","Kurs klar unter beiden, EMA 50 noch knapp über 200, die Linien laufen zusammen",4,20],
 ["Trend Tag (EMA 50/200)","Kurs unter beiden, EMA 50 unter 200",1,10],
 ["Struktur (SMC)","Tiefere Hochs und tiefere Tiefs, neues Tief am 22.10.",2,20],
 ["RSI Tag/Woche","Woche: bullische Divergenz (27 im Juni, heute 34 bei tieferem Kurs), Tag dreht aus 23 nach oben",12,15],
 ["A/D Tag/Woche","Bullische Divergenz auf beiden Zeitebenen",18,20],
 ["Smart Money","Start 3, keine Insider-Käufe, kein grosser Rückkauf gefunden",3,10],
 ["Saisonalität","November 54 %, Dezember 50 %, Januar 52 % positive Jahre",3,5]
],
"pro": [
 "Weltgrösster Hersteller von Elektro- und Hybridautos, baut Batterien, Chips und Motoren selbst und kann darum günstig produzieren.",
 "Ausland wächst stark: September 2026 +154 % (180'700 Autos), im 1. Halbjahr kam erstmals mehr als die Hälfte des Umsatzes aus dem Ausland.",
 "2. Quartal 2026: Gewinn wieder +30 %, Bruttomarge 18.9 % (höchster Wert seit einem Jahr).",
 "Kaum Bankschulden, die Aktie ist mit KGV 19 nicht mehr teuer.",
 "A/D und RSI zeigen auf beiden Zeitebenen erste Zeichen von Käufern."
],
"con": [
 "Umsatz und Gewinn sinken: 1. Halbjahr 2026 Umsatz −7 %, Gewinn −21 %, in China fällt der Absatz (September −13 %).",
 "Harter Preiskampf in China, der Automarkt dort ist schwach (Oktober bisher −26 % bei der ganzen Branche).",
 "Free Cashflow 2025 stark negativ (−98 Mrd. RMB), Dividende um 73 % gekürzt.",
 "Zölle und Handelsstreit: EU und USA erschweren den Verkauf chinesischer Elektroautos.",
 "China-Risiko und Hongkong-Lots: mindestens 100 Aktien (rund 700 CHF) pro Kauf, Abwärtstrend im Chart intakt."
],
"todo": [
 ["t","Beobachten","Alarm bei 77.60 HKD (Trigger) und 66 HKD (Abbruch)."],
 ["s","Timing grün","Tagesschluss über 77.60 HKD, danach über der Tages-EMA 50 halten und Wochenschluss über rund 90 HKD (Wochen-EMAs). Fundamental: Am 29.10. Umsatz im 3. Quartal über Vorjahr (195 Mrd. RMB) und Gewinn klar über 7.8 Mrd. RMB."],
 ["r","Abbruch","Wochenschluss unter 66 HKD."],
 ["","Nächste Zahlen","29. Oktober 2026 (9 Monate und 3. Quartal, Verwaltungsratssitzung bestätigt). Jahreszahlen voraussichtlich Ende März 2027."]
],
"bands": [{"from":86.6,"to":91.0,"type":"res"},{"from":77.6,"to":82.0,"type":"res"},{"from":67.0,"to":71.5,"type":"sup"},{"from":56.0,"to":60.0,"type":"sup"}],
"refs": [{"v":77.6,"label":"Trigger 77.60"}],
"sources": L("https://stockanalysis.com/quote/hkg/1211/financials/income-statement/","StockAnalysis.com (1211)") + " (Stand 28.10.2026), " + L("https://cnevpost.com/2026/08/28/byd-h1-2026-earnings/","CnEVPost: Halbjahreszahlen 2026") + ", " + L("https://cnevpost.com/2026/04/28/byd-reports-drop-in-q1-2026-net-profit/","CnEVPost: 1. Quartal 2026") + ", " + L("https://carnewschina.com/2026/08/29/byd-sees-export-surge-yet-h1-2026-sales-hit-by-second-gen-blade-battery-shortages/","CarNewsChina: Batterie-Engpass") + ", " + L("https://www.itiger.com/news/1130651831","Jahreszahlen 2025 (Tiger)") + ", " + L("https://www.ad-hoc-news.de/boerse/news/corporate-news/byd-company-schedules-october-29-results-byd-company-stock-is-valued-at-eur-74-7-billion/70413161","Termin 29.10. und Septemberzahlen") + ", " + L("https://www.ad-hoc-news.de/boerse/news/unternehmensnachrichten/byd-s-board-sets-october-29-verdict-as-a-26-prozent-retail-slide-tests-the-growth-story/70392902","Automarkt China Oktober") + ", " + L("https://filingreader.com/news-wire/hongkong/2026-06-09/byd-finalizes-2025-dividend-payment-of-rmb-0358-per-share","Dividende 2025") + ", " + L("https://cnevpost.com/2025/08/29/byd-to-change-h-share-lot-size-100/","Lot-Grösse 100 Aktien") + ", " + L("https://www.tipranks.com/stocks/hk:1211/statistics","TipRanks Kennzahlen") + ". Branchenvergleich der App: Note 2.1 von 5, fairer Wert rund 98 HKD (37 % über dem Kurs), Unsicherheit hoch."
}
if __name__ == "__main__":
    json.dump(c, open(os.path.join(P, "config", "1211.json"), "w"), ensure_ascii=False, indent=1)
    print("ok", sum(r[2] for r in c["Q"]), sum(r[2] for r in c["T"]))
