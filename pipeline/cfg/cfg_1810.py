import json, os, sys
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, P)
from helpers import L, ADW, RSIW, SEAS
c = {
"ticker": "1810", "name": "Xiaomi", "datum": "29.10.2026", "waehrung": "HKD", "land": "China",
"meta": "Xiaomi Corporation · Hongkong: 1810 (B-Aktie, in Hongkong-Dollar) · Smartphones, Haushaltsgeräte, Elektroautos, Internetdienste · Peking, China",
"price": "25.68 HKD",
"pricemeta": "Schluss 29.10.2026 · 52 Wochen: 21.30 – 48.14 HKD · Hoch Juni 2025: 61.45 HKD · 1 Lot = 200 Aktien = rund 5'136 HKD, etwa 540 CHF",
"verdict": "Xiaomi ist einer der grössten Handy-Hersteller der Welt und baut seit 2024 auch Elektroautos. Das Geschäft läuft gerade schlecht: Im 1. Halbjahr 2026 fiel der Umsatz um 8.4 %, der bereinigte Gewinn um 43 %. Hauptgrund sind Speicherchips: Sie kosten laut Firma rund fünfmal so viel wie Anfang 2025, das drückt die Handy-Marge. Dazu kommen weniger verkaufte Handys (China im 3. Quartal −20 % laut IDC) und schwächere Auto-Auslieferungen (3. Quartal −7 %). Positiv: Xiaomi hat mehr Bargeld als Schulden und kauft eigene Aktien zurück. Das KGV von rund 18 liegt unter dem eigenen Schnitt, aber der Gewinn sinkt weiter. Qualität rot (25), Timing orange (37): Der Kurs hat sich seit Juni über dem Tief von 21.30 HKD gefangen, ein Aufwärtstrend fehlt aber. Die Zahlen zum 3. Quartal kommen voraussichtlich am 24.11.2026. Keine Anlageberatung.",
"about": "Xiaomi aus Peking wurde 2010 von Lei Jun gegründet. Er ist bis heute Chef und hält rund 23 % der Aktien (Stand November 2025). Xiaomi verkauft Smartphones, dazu Fernseher, Staubsauger-Roboter, Klimageräte und viele andere vernetzte Geräte («IoT»). Auf den Geräten verdient Xiaomi zusätzlich mit Werbung und Apps (Internetdienste, Bruttomarge rund 77 %). Seit 2024 baut Xiaomi eigene Elektroautos (SU7, YU7 und seit September 2026 die SUV-Reihe SkyNomad). Bis Ende September 2026 wurden rund 838'000 Autos ausgeliefert, ein Verkauf in Europa ist ab dem 2. Halbjahr 2027 geplant. Dazu entwickelt Xiaomi eigene KI-Modelle (MiMo). Die Aktie wird in Hongkong gehandelt (1810 in HKD, 81810 in Yuan). Du kaufst in Lots von 200 Aktien, heute rund 5'136 HKD (etwa 540 CHF, mit 1 HKD = rund 0.105 CHF). Weniger als 1 Lot kannst du an der Börse Hongkong in der Regel nicht kaufen.",
"why": "Im Juni 2025 erreichte die Aktie 61.45 HKD (Wochenhoch), getragen von der Freude über die Elektroautos. Seither ist sie um rund 58 % gefallen. Drei Gründe: Erstens sind Speicherchips (DRAM und NAND) extrem teuer geworden. Laut Xiaomi kosten sie rund fünfmal so viel wie Anfang 2025, die Marge der Handy-Sparte fiel im 1. Quartal 2026 auf 10.1 %. Die Firma erwartet, dass die Branche 2026 mindestens 10 % weniger Handys verkauft. Zweitens wächst die Auto-Sparte langsamer als erhofft: Im September lieferte Xiaomi 40'015 Autos aus, 4.6 % weniger als ein Jahr zuvor, das 3. Quartal lag 6.8 % unter Vorjahr. Für das Jahresziel von 550'000 Autos fehlen noch rund 264'000 im 4. Quartal. Drittens ist der ganze Automarkt in China schwach (Elektroautos im September −16.7 %). Im 1. Quartal 2026 machte die Sparte Autos, KI und Neues 3.1 Mrd. Yuan Betriebsverlust. Die Sorgen sind also echt, ein Teil (Chippreise) kann aber vorübergehend sein. Am 9.10.2026 stufte China Renaissance die Aktie auf Verkaufen ab (Ziel 20.50 HKD).",
"kpis": [
 ["r","Umsatzwachstum","+2.2 %","Letzte 12 Monate bis Juni 2026 (StockAnalysis). Das täuscht: Im 1. Halbjahr 2026 fiel der Umsatz um 8.4 %. 2025 war mit +25 % noch ein starkes Jahr."],
 ["r","Operative Marge","4.8 %","Von 100 Yuan Umsatz bleiben knapp 5 Yuan Betriebsgewinn (12 Monate bis Juni 2026). 2025 waren es 7.1 %. Grund: teure Speicherchips und Verluste bei den neuen Geschäften."],
 ["r","Gewinn pro Aktie (EPS)","1.23 RMB","Letzte 12 Monate bis Juni 2026. 2025: 1.56 RMB. Der Gewinn sinkt seit Ende 2025. Bereinigter Gewinn im 1. Halbjahr 2026: −43 %."],
 ["r","ROIC","9.0 %","Auf 100 Yuan investiertes Kapital rund 9 Yuan Gewinn (StockAnalysis, Stand September 2026). 2025 waren es 16.7 %. Unter 10 % ist schwach."],
 ["r","Free Cashflow","−4.6 Mrd. RMB","Letzte 12 Monate bis Juni 2026. Es floss etwas mehr Geld ab als herein, vor allem wegen Investitionen in Autos und KI. 2023 bis 2025 war der Wert jedes Jahr klar positiv (21 bis 35 Mrd. RMB)."],
 ["g","Schulden","Netto-Cash","Mehr Bargeld als Schulden: rund 89 Mrd. HKD netto (StockAnalysis, 15.10.2026). Total verfügbare Mittel laut Firma 219 Mrd. RMB (Juni 2026). Sehr solide."],
 ["w","KGV","17.6","Du zahlst rund 18 Jahresgewinne. Eigener Schnitt der letzten 5 Jahre ohne das Ausreisserjahr 2022: 24.1. Also rund 27 % günstiger. Aber: Analysten erwarten weniger Gewinn, auf den erwarteten Gewinn ist das KGV rund 21 bis 22."],
 ["w","Dividende","keine","Xiaomi hat noch nie eine Dividende bezahlt. Das Geld fliesst in Autos, KI und in Aktienrückkäufe (Programm bis 20 Mrd. HKD seit Mai 2026)."]
],
"revtitle": "Umsatz pro Quartal (Mrd. RMB)", "revunit": "Mrd. RMB", "epsunit": "RMB",
"revnote": "Bis zum 3. Quartal 2025 wuchs jedes Quartal stark (bis +47 %). Danach brach das Tempo ein: Q4 25 +7 %, Q1 26 −11 %, Q2 26 −6 % gegenüber Vorjahr.",
"marginnote": "Betriebsgewinn pro 100 Yuan Umsatz. 2022 nur 2.2 %, dann bis 2025 auf 7.1 % gestiegen und seither wegen teurer Speicherchips auf 4.8 % gefallen.",
"finnote": "<b>Hinweis:</b> Zahlen in chinesischen Yuan (RMB, Umsatz und Free Cashflow in Mio.), Kurs in Hongkong-Dollar. 1 RMB = rund 1.09 HKD. Umsatz, Marge, EPS, Free Cashflow, ROIC und KGV laut StockAnalysis (KGV am Jahresende). Die operative Marge ist ohne Anlagegewinne gerechnet. Xiaomi selbst meldet einen höheren Betriebsgewinn (2. Quartal 2026: 10.9 Mrd. RMB statt 4.4 Mrd. RMB), weil dort Gewinne aus Beteiligungen mitgezählt sind. KGV heute: eigene Rechnung mit dem Kurs vom 29.10.2026. 2022 war das KGV fast 98, weil der Gewinn fast null war.",
"FIN": [["2021",328309,"+33.5 %","6.1 %",0.76,2616,"24.5 %","19.9"],["2022",280044,"−14.7 %","2.2 %",0.10,-10189,"4.2 %","97.6"],["2023",270970,"−3.2 %","5.5 %",0.69,35032,"12.4 %","20.3"],["2024",365906,"+35.0 %","6.2 %",0.93,31998,"18.0 %","34.4"],["2025",457287,"+25.0 %","7.1 %",1.56,21373,"16.7 %","22.0"],["Letzte 12 Mt.",438100,"+2.2 %","4.8 %",1.23,-4631,"9.0 %","17.6"]],
"QREV": [["Q3 24",92.5],["Q4 24",109.0],["Q1 25",111.3],["Q2 25",116.0],["Q3 25",113.1],["Q4 25",116.9],["Q1 26",99.1],["Q2 26",108.9]],
"revdec": 1,
"MARGIN": [["2021",6.1],["2022",2.2],["2023",5.5],["2024",6.2],["2025",7.1],["12 Mt.",4.8]],
"Q": [
 ["Umsatztrend","2 von 4 Quartalen über Vorjahr (+22 %, +7 %, −11 %, −6 %), Tempo bricht ein",4,15],
 ["Wachstumstempo","+2.2 % in 12 Monaten bis Juni 2026, 1. Halbjahr 2026 sogar −8.4 %",0,10],
 ["Operative Marge","4.8 % (0 Pkt.), heute tiefer als 2021 (6.1 %) und seit 2025 fallend (0 Pkt.)",0,15],
 ["Gewinnwachstum (EPS)","Aktuell klar negativ: bereinigter Gewinn 1. Halbjahr 2026 −43 %, EPS 12 Monate −21 % gegen 2025",0,10],
 ["Free Cashflow","Letzte 12 Monate negativ (−4.6 Mrd. RMB), vorher 3 Jahre positiv",0,10],
 ["ROIC","9.0 % (2 Pkt.), klar fallend von 16.7 % (−1)",1,15],
 ["Schulden","Netto-Cash, rund 89 Mrd. HKD mehr Bargeld als Schulden",10,10],
 ["Bewertung vs. eigene Historie","KGV 17.6 statt Ø 24.1 (ohne Ausreisser 2022), rund 27 % günstiger",10,15]
],
"adwnote": ADW + "Positiv: In der Woche ab 10.8. schloss Xiaomi bei 25.62 HKD mit Wochen-A/D 3'066, heute bei 25.68 HKD mit 4'196. Beim gleichen Kurs steht die A/D höher: eine bullische Divergenz. Seit dem Tief im Juni (3'230) steigt die Wochen-A/D wieder. Werte in Mio. Aktien.",
"rsiwnote": RSIW + "Im Juni bei 20 (stark überverkauft), heute 43. Kein Signal, der RSI erholt sich mit dem Kurs.",
"addnote": "Neutral: Am 18.8. stand die Tages-A/D bei −2'294 (Kurs 25.22 HKD), am 8.10. beim tieferen Tief von 23.58 HKD bei −2'555, sie fiel also mit dem Kurs. Seither stieg sie auf −2'146 (21.10.) und liegt heute bei −2'292. Kein klares Kaufsignal auf Tagesbasis.",
"ind": [
 ["Kurs vs. EMA 50","25.68 &lt; 26.26","25.68 &lt; 31.03","Knapp unter der Tageslinie, klar unter der Wochenlinie."],
 ["Kurs vs. EMA 200","25.68 &lt; 30.36","25.68 &lt; 29.70","Rund 14 bis 15 % unter der langfristigen Linie."],
 ["EMA 50 vs. EMA 200","50 unter 200 (Todeskreuz am 18.11.2025)","50 noch über 200 (31.03 zu 29.70), Abstand schrumpft","Tag im Abwärtstrend, in der Woche droht ein Todeskreuz."],
 ["RSI (14)","47.8","42.9","Beide neutral, kein Signal."],
 ["A/D","seit 8.10. leicht gestiegen, heute wieder tiefer","höher als im August beim gleichen Kurs","Woche positiv, Tag neutral."],
 ["Volumen","Ø 20 Tage 143 Mio. vs. Ø 100 Tage 166 Mio. Aktien","Etwas weniger Handel als üblich."]
],
"smc": "Seit dem Hoch vom Juni 2025 (61.45 HKD) fällt Xiaomi mit tieferen Hochs und tieferen Tiefs. Das Tief kam am 26.6.2026 bei 21.30 HKD. Danach folgte eine Erholung bis 32.40 HKD (30.7.). Seither wieder tiefere Hochs: 29.14 (26.8.), 28.76 (4.9.), 28.22 (22.9.) und 27.76 HKD (21.10.). Die Tiefe lagen bei 25.22 (18.8.), 25.44 (11.9.), 23.58 (8.10.) und 25.40 HKD (28.10.). Das Tief vom Juni wurde nicht mehr erreicht, der kurzfristige Abwärtstrend seit Juli ist aber intakt. Ein Change of Character nach oben wäre ein Tagesschluss über 27.76 HKD (letztes tieferes Hoch).",
"zones": [
 ["r","31.00–32.40 HKD","Widerstand: Wochen-EMA 50 (31.03) und Hoch vom 30.7. (32.40 HKD)."],
 ["r","29.10–30.40 HKD","Widerstand: Hoch vom 26.8. (29.14), Wochen-EMA 200 (29.70) und Tages-EMA 200 (30.36 HKD)."],
 ["r","26.30–28.20 HKD","Widerstand: Tages-EMA 50 (26.26) und die Hochs vom 21.10. (27.76) und 22.9. (28.22 HKD)."],
 ["t","27.76 HKD","<b>Trigger:</b> Tagesschluss über 27.76 HKD (letztes tieferes Hoch vom 21.10.), besser mit steigender Tages-A/D."],
 ["s","23.50–25.40 HKD","<b>Kaufzone 1:</b> Tiefs vom 8.10. (23.58), 18.8. (25.22) und 28.10. (25.40 HKD). Hier kaufte auch Xiaomi selbst Aktien zurück (Schnitt Juli bis Oktober rund 26.47 HKD)."],
 ["s","21.30–22.50 HKD","<b>Kaufzone 2:</b> 52-Wochen-Tief vom 26.6.2026 (21.30 HKD). Ein KGV von rund 15 auf den heutigen Gewinn (eigene Rechnung)."],
 ["r","21.00 HKD","Abbruch: Wochenschluss unter 21 HKD, also unter dem 52-Wochen-Tief."]
],
"smart": [
 "<b>Rückkäufe:</b> Seit 26.5.2026 läuft ein Rückkaufprogramm über bis zu 20 Mrd. HKD, rund 2.9 % des Börsenwerts. Laut Halbjahresbericht kaufte Xiaomi 2026 bis 13.8. rund 377 Mio. Aktien für 11.7 Mrd. HKD zurück. Zuletzt kaufte die Firma noch am 5.10.2026 (2 Mio. Aktien zu rund 23.80 HKD).",
 "<b>Insider:</b> Gründer Lei Jun kaufte im November 2025 rund 2.6 Mio. Aktien für über 100 Mio. HKD (rund 38 HKD pro Aktie). In den letzten 6 Monaten habe ich keine Insider-Käufe am Markt gefunden.",
 "<b>Grosse Investoren:</b> Zu Käufen oder Verkäufen grosser Fonds 2026 habe ich keine verlässlichen Daten gefunden.",
 "<b>Analysten:</b> Kursziel im Schnitt rund 34 HKD (27 Analysten, mehrheitlich Kaufen, Daten der App). Die Meinungen gehen weit auseinander: Goldman Sachs 41 HKD (Kaufen, April 2026), UOB Kay Hian 27.60 HKD (Halten, Oktober 2026), China Renaissance 20.50 HKD (Verkaufen, 9.10.2026)."
],
"seasnote": SEAS + "Daten erst seit 2018 (8 Jahre), darum wenig aussagekräftig. November (+7.0 %, 75 %) war bisher stark, Dezember (+7.5 %, 50 %) gemischt, Januar (−5.5 %, 38 %) und September (−5.1 %, 33 %) schwach.",
"T": [
 ["Trend Woche (EMA 50/200)","Kurs klar unter beiden, EMA 50 noch über 200, die Linien laufen zusammen",4,20],
 ["Trend Tag (EMA 50/200)","Kurs knapp unter beiden, EMA 50 unter 200, EMA 50 flacht ab",2,10],
 ["Struktur (SMC)","Seit Juli tiefere Hochs und tiefere Tiefs, das Juni-Tief (21.30) hält aber",4,20],
 ["RSI Tag/Woche","Tag 48, Woche 43: neutral ohne Signal",7,15],
 ["A/D Tag/Woche","Woche: bullische Divergenz (höhere A/D beim gleichen Kurs), Tag neutral",11,20],
 ["Smart Money","Start 3, grosser laufender Rückkauf (rund 2.9 % des Börsenwerts, +3), keine Insider-Käufe in 6 Monaten",6,10],
 ["Saisonalität","November 75 %, Dezember 50 %, Januar 38 % positive Jahre: Schnitt rund 54 %",3,5]
],
"pro": [
 "Starke Marke mit riesiger Kundenbasis: Handys, Haushaltsgeräte und Autos sind miteinander vernetzt, das bindet Kunden.",
 "Sehr solide Bilanz: rund 89 Mrd. HKD mehr Bargeld als Schulden.",
 "Grosser Aktienrückkauf (bis 20 Mrd. HKD) bei tiefen Kursen.",
 "Neue Auto-Reihe SkyNomad: laut Firma über 70'000 feste Bestellungen in 30 Tagen. Europa ab 2027 geplant.",
 "KGV von rund 18 deutlich unter dem eigenen Schnitt, Wochen-A/D zeigt erste Käufer."
],
"con": [
 "Umsatz und Gewinn sinken: 1. Halbjahr 2026 Umsatz −8.4 %, bereinigter Gewinn −43 %.",
 "Teure Speicherchips drücken die Handy-Marge, die Knappheit könnte laut Counterpoint bis Ende 2027 dauern.",
 "Weniger Handys: China im 3. Quartal −20 % (IDC), Branche 2026 laut Firma mindestens −10 %.",
 "Auto-Auslieferungen im 3. Quartal −7 %, das Jahresziel von 550'000 Autos ist kaum zu schaffen. Die Auto-Sparte kostet viel Geld.",
 "China-Risiko und Hongkong-Lots: mindestens 200 Aktien (rund 540 CHF) pro Kauf, keine Dividende, Abwärtstrend im Chart."
],
"todo": [
 ["t","Beobachten","Alarm bei 27.76 HKD (Trigger) und 21 HKD (Abbruch)."],
 ["s","Timing grün","Tagesschluss über 27.76 HKD, danach Wochenschluss über rund 30 HKD (Wochen-EMA 200). Fundamental: Am 24.11. Bruttomarge wieder über 20 % (2. Quartal 2026: 19.8 %) und Umsatz nahe am Vorjahr (113.1 Mrd. RMB)."],
 ["r","Abbruch","Wochenschluss unter 21 HKD."],
 ["","Nächste Zahlen","Voraussichtlich 24. November 2026 (3. Quartal, laut MarketScreener, von Xiaomi noch nicht bestätigt). Jahreszahlen voraussichtlich Ende März 2027."]
],
"bands": [{"from":31.0,"to":32.4,"type":"res"},{"from":29.1,"to":30.4,"type":"res"},{"from":26.3,"to":28.2,"type":"res"},{"from":23.5,"to":25.4,"type":"sup"},{"from":21.3,"to":22.5,"type":"sup"}],
"refs": [{"v":27.76,"label":"Trigger 27.76"}],
"sources": L("https://stockanalysis.com/quote/hkg/1810/financials/","StockAnalysis.com (1810)") + " (Stand 29.10.2026), " + L("https://www.itiger.com/news/1131990081","Tiger: Zahlen 2. Quartal 2026") + ", " + L("https://www.thestandard.com.hk/innovation/article/332994/Chinas-Xiaomi-Q1-profit-sinks-43pc-on-higher-memory-chip-costs-launches-20-billion-buyback","The Standard: 1. Quartal und Rückkauf") + ", " + L("https://www.itiger.com/news/1163617478","Tiger: Investorentag April 2026") + ", " + L("https://cnevpost.com/2026/10/13/xiaomi-auto-sept-2026-deliveries-2/","CnEVPost: Auslieferungen September") + ", " + L("https://www.ad-hoc-news.de/boerse/news/unternehmensnachrichten/xiaomi-s-twin-engines-auto-deliveries-hit-a-2026-peak-while-phone-shipments-skid-20-4-prozent/70326644","ad-hoc-news: Handys 3. Quartal und Analysten") + ", " + L("https://www.itiger.com/news/1155202620","Tiger: Rückkäufe bis 5.10.2026") + ", " + L("https://www.itiger.com/news/1159694790","Tiger: Kauf von Lei Jun (November 2025)") + ", " + L("https://www.marketscreener.com/quote/stock/XIAOMI-CORPORATION-45271958/calendar/","MarketScreener: Termine") + ", " + L("https://simplywall.st/stocks/hk/tech/hkg-1810/xiaomi-shares/dividend","Simply Wall St: Dividende") + ". Branchenvergleich der App: Note 1.9 von 5, fairer Wert rund 36 HKD (35 % über dem Kurs), Unsicherheit mittel."
}
if __name__ == "__main__":
    json.dump(c, open(os.path.join(P, "config", "1810.json"), "w"), ensure_ascii=False, indent=1)
    print("ok", sum(r[2] for r in c["Q"]), sum(r[2] for r in c["T"]))
