import json, os, sys
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, P)
from helpers import L, ADW, RSIW, SEAS
c = {
"ticker": "NFLX", "name": "Netflix", "datum": "16.10.2026", "waehrung": "USD", "land": "USA",
"meta": "Netflix, Inc. · NASDAQ: NFLX · Streaming von Serien, Filmen, Live-Sport und Spielen · Los Gatos, USA",
"price": "70.53 $",
"pricemeta": "Schluss 16.10.2026 · 52 Wochen: 65.08 – 124.86 $ · Allzeithoch 134.12 $ am 30.6.2025 (nach Aktiensplit 10:1)",
"verdict": "Netflix ist fundamental stark: Umsatz +16 %, operative Marge fast 30 % und steigend, 11 Mrd. $ Free Cashflow, der fast ganz in Aktienrückkäufe geht. Die Aktie hat sich aber seit dem Hoch fast halbiert (−47 %). Der Grund: Das Wachstum wird langsamer (Prognose 3. Quartal +11.7 % statt 17.6 % Ende 2025), die Zuschauer schauen kaum mehr (+2 %), und das gescheiterte Warner-Bros.-Gebot hat Vertrauen gekostet. Das KGV fiel von 36 auf 22 (ohne Einmalzahlung rund 28). Qualität grün (87), Timing orange (42). <b>Wichtig: Morgen, 20.10. nach US-Börsenschluss, kommen die Zahlen.</b> Die Optionen erwarten ±9.5 % Kursbewegung. Nach den Ampeln: Watchlist, Zahlen abwarten.",
"about": "Netflix ist der grösste Streaming-Dienst der Welt mit über 300 Mio. zahlenden Haushalten in über 190 Ländern. Rund 95 % des Umsatzes sind Abo-Gebühren, der Rest vor allem Werbung im günstigeren Abo mit Werbung (2026 rund 3 Mrd. $, doppelt so viel wie 2025). Dazu kommen Live-Sport (NFL-Spiele an Weihnachten, Baseball, Boxen, Frauen-Fussball-WM 2027) und Spiele. Umsatz nach Region (2. Quartal 2026): USA und Kanada 43 %, Europa/Naher Osten/Afrika 32 %, Lateinamerika 13 %, Asien 12 %. Netflix hat noch nie eine Dividende bezahlt.",
"why": "Am 30. Juni 2025 erreichte die Aktie ihr Allzeithoch (134.12 $). Im Oktober 2025 verfehlte Netflix die Gewinnerwartung wegen einer Steuernachzahlung in Brasilien (−10 % an einem Tag). Im Dezember 2025 bot Netflix 82.7 Mrd. $ für die Filmstudios und HBO Max von Warner Bros. Discovery, mit rund 50 Mrd. $ neuen Schulden. Anleger fürchteten Schulden und Integration, die Aktie fiel im Dezember um 13 %. Ende Februar 2026 gewann Paramount das Bieterrennen, Netflix bekam 2.8 Mrd. $ Entschädigung (Aktie +9 %). Danach enttäuschten die Ausblicke im April (−9.7 %) und Juli (−7.3 %, Jahrestief 65.08 $). Die Zuschauer schauen nur 2 % mehr als vor einem Jahr, das Umsatzwachstum in den USA fiel in zwei Quartalen von 18 % auf 10 %. Gründer Reed Hastings verliess im Juni den Verwaltungsrat und verkaufte für rund 309 Mio. $ Aktien. Im September stuften Wells Fargo (Kursziel 57 $) und HSBC ab. Letzte Woche: 1'000 Stellen gestrichen (6 %), neuer Content-Chef (Peter Rice ersetzt Bela Bajaria).",
"kpis": [
 ["g","Umsatzwachstum","+16 %","Letzte 12 Monate. Aber langsamer: 17.6 % (Ende 2025), 16.2 %, 13.4 %, Prognose 3. Quartal 11.7 %. Analysten erwarten 2027 nur noch +11 %."],
 ["w","Sehzeit","+2 %","So viel mehr Stunden schauten die Leute im 1. Halbjahr 2026 als im Vorjahr. Zu wenig: Das Wachstum kommt nur noch von Preiserhöhungen und Werbung. YouTube hat in den USA fast doppelt so viel TV-Sehzeit wie Netflix."],
 ["g","Operative Marge","29.7 %","Von 100 $ Umsatz bleiben rund 30 $ Betriebsgewinn. Sehr gut, und seit 2022 jedes Jahr gestiegen. Prognose 2026: 31.5 %."],
 ["g","Gewinn pro Aktie (EPS)","3.17 $","Letzte 12 Monate. Ohne die Warner-Entschädigung rund 2.53 $. 2023 bis 2025 wuchs der Gewinn pro Aktie um 28 % pro Jahr."],
 ["g","ROIC","32 %","Auf 100 $ investiertes Kapital rund 32 $ Gewinn. Sehr gut."],
 ["g","Free Cashflow","11.2 Mrd. $","Letzte 12 Monate (inkl. 2.8 Mrd. $ Einmalzahlung), 23 % vom Umsatz, 3.8 % des Börsenwerts (ohne Einmalzahlung rund 2.8 %). Nur 4 % davon sind Löhne in Aktien: echt."],
 ["g","KGV","22.2","Du zahlst 22 Jahresgewinne, ohne Einmalzahlung rund 28. Eigener Schnitt 2021–2025: rund 40. Also rund 30 % günstiger als üblich und erstmals günstiger als der US-Markt (S&P 500 rund 24)."],
 ["g","Aktienrückkäufe","−1.5 %","So viel weniger Aktien als vor einem Jahr. 2023 bis 2025 gingen 87 bis 97 % des Free Cashflows in Rückkäufe. Noch 27.1 Mrd. $ erlaubt (9 % des Börsenwerts). Keine Dividende."]
],
"revtitle": "Umsatz pro Quartal (Mio. $)", "revunit": "Mio. $", "epsunit": "$",
"revnote": "Alle 8 Quartale über dem Vorjahr, aber das Wachstum sinkt: +17.6 % im 4. Quartal 2025, +13.4 % im 2. Quartal 2026. Prognose 3. Quartal: 12'860 Mio. $ (+11.7 %).",
"marginnote": "Operative Marge pro Jahr. Seit 2022 jedes Jahr höher. Im 2. Quartal 2026 33.4 %, Prognose für das 3. Quartal 33.2 %.",
"finnote": "<b>Hinweis:</b> Aktiensplit 10:1 im November 2025, alle Werte pro Aktie sind angepasst. 2026 enthält eine Einmalzahlung von 2.8 Mrd. $ (Entschädigung für das geplatzte Warner-Geschäft), sie bläht Gewinn und Free Cashflow der letzten 12 Monate auf. Ohne sie: Gewinn pro Aktie rund 2.53 $, KGV rund 28.",
"FIN": [["2021",29698,"+18.8 %","20.9 %",1.12,-132,"22.0 %","52.2"],["2022",31616,"+6.5 %","17.8 %",0.99,1619,"16.1 %","29.2"],["2023",33723,"+6.7 %","20.6 %",1.20,6926,"19.5 %","39.4"],["2024",39001,"+15.6 %","26.7 %",1.98,6922,"28.7 %","43.7"],["2025",45183,"+15.9 %","29.5 %",2.53,9461,"34.0 %","36.2"],["Letzte 12 Mt.",48371,"+16.0 %","29.7 %",3.17,11152,"32.4 %","22.2"]],
"QREV": [["Q3 24",9825],["Q4 24",10247],["Q1 25",10543],["Q2 25",11079],["Q3 25",11510],["Q4 25",12051],["Q1 26",12250],["Q2 26",12560]],
"revdec": 0,
"MARGIN": [["2021",20.9],["2022",17.8],["2023",20.6],["2024",26.7],["2025",29.5],["Q2 26",33.4]],
"Q": [
 ["Umsatztrend","4 von 4 Quartalen über Vorjahr, aber Wachstum sinkt",13,15],
 ["Wachstumstempo","+16 % in 12 Monaten, Prognose 3. Quartal nur +11.7 %",8,10],
 ["Operative Marge","29.7 % (über 20 %), seit 2022 jedes Jahr gestiegen",14,15],
 ["Gewinnwachstum (EPS)","3 Jahre +28 % pro Jahr, ohne Einmalzahlung zuletzt flach",8,10],
 ["Free Cashflow","Positiv, in 3 von 4 Jahren gestiegen (2024 flach)",9,10],
 ["ROIC","32 % (15 Pkt.), leicht fallend (−1)",14,15],
 ["Schulden","Netto-Schulden 5.2 Mrd. $ = 0.47 Jahre Free Cashflow",9,10],
 ["Bewertung vs. eigene Historie","KGV 28 ohne Einmalzahlung statt Ø 40 (2021–2025), rund 30 % günstiger",12,15]
],
"adwnote": ADW + "Beim Tief im Juli (Wochenschluss 68.95 $) stand die Wochen-A/D bei 8'963, heute bei 8'939 bei leicht höherem Kurs (70.53 $). Etwa gleich: neutral.",
"rsiwnote": RSIW + "Im Februar bei 24, im Juli bei 31, heute 39 bei ähnlichem Kurs wie im Juli: leicht positive Divergenz.",
"addnote": "Positiv: Beim Tief vom 17.7. (65.08 $) stand die Tages-A/D bei 240, beim Tief vom 5.10. (66.54 $) bei 289, heute 333. Bei den Tiefs wurde weniger verkauft.",
"ind": [
 ["Kurs vs. EMA 50","70.5 &lt; 73.6","70.5 &lt; 84.4","Unter der mittelfristigen Linie, auf beiden Zeitebenen."],
 ["Kurs vs. EMA 200","70.5 &lt; 83.1","70.5 &lt; 77.2","Unter der langfristigen Linie, auf beiden Zeitebenen."],
 ["EMA 50 vs. EMA 200","50 unter 200 (seit 10.12.2025)","50 noch über 200","Tag im Abwärtstrend. Woche: Die EMA 50 fällt schnell, ein Todeskreuz droht bis Ende Jahr."],
 ["RSI (14)","45.5","39.1","Neutral bis schwach. Woche mit leicht positiver Divergenz."],
 ["A/D","höher als bei den Tiefs vom Juli und Oktober","etwa gleich wie beim Juli-Tief","Tag positiv, Woche neutral."],
 ["Volumen","Ø 20 Tage 35.2 Mio. vs. Ø 100 Tage 39.4 Mio. Aktien","Ruhiger Handel vor den Zahlen."]
],
"smc": "Netflix ist seit dem Allzeithoch (134.12 $, Juni 2025) im Abwärtstrend mit tieferen Hochs: 126.71 $ (September 2025), 124.86 $ (Oktober 2025), 108.95 $ (April 2026), 83.60 $ (September 2026). Die Tiefs: 75.01 $ (Februar), 65.08 $ (17. Juli), 66.54 $ (5. Oktober). Das Oktober-Tief liegt leicht über dem Juli-Tief: Ein möglicher doppelter Boden bei 65 bis 67 $. Bestätigt wäre er erst mit einem Tagesschluss über dem Hoch vom 15.10. (73.07 $) und der Tages-EMA 50 (73.60 $), danach über 78.50 $. Fällt die Aktie nach den Zahlen unter 65 $, ist der Boden gescheitert, die nächste Unterstützung liegt dann erst bei den Tiefs von 2024 (rund 60 $).",
"zones": [
 ["r","81–83.60 $","Widerstand: Hochs vom August und September."],
 ["r","77–78.50 $","Widerstand: Wochen-EMA 200 (77.20 $) und Hoch vom 2.7. (78.44 $)."],
 ["t","74 $","<b>Trigger:</b> Tagesschluss über dem Hoch vom 15.10. (73.07 $) und der Tages-EMA 50 (73.60 $)."],
 ["s","65–67 $","<b>Kaufzone:</b> Tiefs vom 17.7. (65.08 $) und 5.10. (66.54 $). Nur mit Wendesignal kaufen."],
 ["r","64.90 $","Abbruch: Wochenschluss unter dem Jahrestief."]
],
"smart": [
 "<b>Netflix selbst:</b> Grösster Käufer der eigenen Aktie: im 2. Quartal 2026 Rekord mit 4.7 Mrd. $, in 12 Monaten rund 10 Mrd. $ (3.4 % des Börsenwerts). Noch 27.1 Mrd. $ erlaubt, ohne Ablaufdatum.",
 "<b>Insider:</b> 0 Käufe in 12 Monaten, Verkäufe für 403 Mio. $. Davon Reed Hastings rund 309 Mio. $ (jeden Monat bis Juni). Auch die beiden Chefs Sarandos und Peters verkauften (je rund 15 bis 18 Mio. $). Wohl geplante Verkäufe, aber niemand kaufte bei 65 bis 75 $.",
 "<b>Analysten:</b> MarketBeat: 38× Kaufen, 15× Halten, 2× Verkaufen, Kursziel im Schnitt 93.82 $ (Spanne 57 bis 125 $). Die Ziele werden seit Juli laufend gesenkt (z. B. BMO 135→125 $, Wedbush 105→90 $, Barclays 80→70 $). Wells Fargo und Huber raten zum Verkauf.",
 "<b>Erwartung für die Zahlen:</b> Die Aktie fiel nach den letzten 6 Quartalszahlen jedes Mal. Die Prognose von Netflix (0.82 $ Gewinn pro Aktie) entspricht der Analysten-Erwartung."
],
"seasnote": SEAS + "24 Jahre Daten (seit 2002). Oktober bis Dezember leicht positiv (58 bis 62 % positive Jahre), Januar am stärksten (+7.6 %, 67 %).",
"T": [
 ["Trend Woche (EMA 50/200)","Kurs unter beiden, EMA 50 noch über 200",6,20],
 ["Trend Tag (EMA 50/200)","Kurs unter beiden, EMA 50 unter 200",1,10],
 ["Struktur (SMC)","Tiefere Hochs, aber Oktober-Tief über Juli-Tief (möglicher Boden)",7,20],
 ["RSI Tag/Woche","Tag 46, Woche 39, Woche mit leicht positiver Divergenz",8,15],
 ["A/D Tag/Woche","Tag höher als bei den Tiefs, Woche neutral",11,20],
 ["Smart Money","Start 3, Rückkauf 3.4 % pro Jahr +3, nur Insider-Verkäufe −1",5,10],
 ["Saisonalität","Oktober 62 %, November 58 %, Dezember 58 % positive Jahre",4,5]
],
"pro": [
 "Weltmarktführer im Streaming mit 30 % Marge, die weiter steigt (Prognose 31.5 %).",
 "11 Mrd. $ Free Cashflow, fast alles für Rückkäufe, wenig Schulden (0.47 Jahre Free Cashflow).",
 "Werbung verdoppelt sich 2026 auf rund 3 Mrd. $, ab 2027 in 15 weiteren Ländern (auch Schweiz).",
 "KGV rund 30 % unter dem eigenen Schnitt, erstmals unter dem US-Markt.",
 "Preiserhöhungen in den USA im März haben funktioniert."
],
"con": [
 "Als Wachstumsaktie ein Warnsignal: Wachstum sinkt von 17.6 % auf 11.7 %, in den USA von 18 % auf 10 %.",
 "Zuschauer schauen nur 2 % mehr. YouTube nimmt Sehzeit weg, Preiserhöhungen haben Grenzen.",
 "Inhalte werden teurer (+10 %), Live-Sport kostet 5 % des Budgets, bringt aber nur 1 % der Sehzeit.",
 "Unruhe in der Führung: Hastings weg, Content-Chefin weg, 1'000 Stellen gestrichen.",
 "Weniger Transparenz: Keine Abo-Zahlen mehr, Sehzeit-Bericht nur noch jährlich."
],
"todo": [
 ["t","Beobachten","Alarm bei 74 $ (Trigger) und 64.90 $ (Abbruch). Nicht vor den Zahlen kaufen: ±9.5 % Bewegung erwartet."],
 ["s","Timing grün","Tagesschluss über 74 $, danach über 78.50 $. Fundamental: Am 20.10. Marge 33 % bestätigt, Jahresziel 31.5 % gehalten und ein Ausblick für das 4. Quartal über +12 %."],
 ["r","Abbruch","Wochenschluss unter 64.90 $ oder Senkung des Margenziels von 31.5 %."],
 ["","Nächste Zahlen","Dienstag, 20. Oktober 2026 nach US-Börsenschluss (in der Schweiz rund 22 Uhr). Erwartet: Umsatz 12.86 Mrd. $, Gewinn pro Aktie 0.82 $."]
],
"bands": [{"from":81,"to":83.6,"type":"res"},{"from":77,"to":78.5,"type":"res"},{"from":65,"to":67,"type":"sup"}],
"refs": [{"v":74,"label":"Trigger 74"}],
"sources": L("https://stockanalysis.com/stocks/nflx/financials/","StockAnalysis.com") + " (Stand 16.10.2026), " + L("https://www.sec.gov/Archives/edgar/data/0001065280/000106528026000211/ex991_q226.htm","Netflix Aktionärsbrief Q2 2026") + ", " + L("https://www.sec.gov/Archives/edgar/data/1065280/000106528026000137/ex991_q126.htm","Aktionärsbrief Q1 2026") + ", " + L("https://www.nasdaq.com/articles/netflix-after-wbd-deal-collapse","Nasdaq: nach dem Warner-Deal") + ", " + L("https://247wallst.com/investing/2026/10/16/netflix-is-cutting-about-1000-jobs-and-its-content-chief-is-out-days-before-earnings/","24/7 Wall St (16.10.2026)") + ", " + L("https://www.marketbeat.com/stocks/NASDAQ/NFLX/forecast/","Analysten (MarketBeat)") + ", " + L("https://www.marketbeat.com/stocks/NASDAQ/NFLX/insider-trades/","Insider (MarketBeat)") + "."
}
if __name__ == "__main__":
    json.dump(c, open(os.path.join(P, "config", "NFLX.json"), "w"), ensure_ascii=False, indent=1)
    print("ok", sum(r[2] for r in c["Q"]), sum(r[2] for r in c["T"]))
