import json, os, sys
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, P)
from helpers import L, ADW, RSIW, SEAS
c = {
"ticker": "AMD", "name": "AMD", "datum": "10.11.2026", "waehrung": "USD", "land": "USA",
"meta": "Advanced Micro Devices, Inc. · NASDAQ: AMD · Prozessoren, Grafikchips und KI-Beschleuniger · Santa Clara, USA",
"price": "515.21 $",
"pricemeta": "Schluss 10.11.2026 · 52 Wochen: 188.22 – 658.52 $ · Allzeithoch: 658.52 $ am 6.10.2026",
"verdict": "AMD baut Prozessoren für Server und PCs und KI-Chips für Rechenzentren. Das Geschäft wächst sehr schnell: Im 3. Quartal 2026 stieg der Umsatz um 45 % auf 13.4 Mrd. $, das Rechenzentrum fast um das Doppelte (+97 %). Für das 4. Quartal erwartet AMD rund 17 Mrd. $ (+66 %), für 2027 mehr als 80 % Wachstum. Die Aktie ist aber sehr teuer: KGV 111.8 auf den ausgewiesenen Gewinn, rund 34 auf den erwarteten Gewinn der nächsten 12 Monate. Qualität hellgrün (71), Timing gelb (50): Nach dem Allzeithoch von 658.52 $ (6.10.) fiel der Kurs bis 402.10 $ (5.11.), seither stieg er wieder auf 515 $. Im Tageschart gibt es tiefere Hochs und tiefere Tiefs, der Wochentrend ist intakt. Insider verkaufen laufend, Rückkäufe gibt es kaum. Keine Anlageberatung.",
"about": "AMD (Advanced Micro Devices) aus Santa Clara (Kalifornien) entwickelt Chips, baut sie aber nicht selbst: Gefertigt wird vor allem bei TSMC in Taiwan. Es gibt drei Bereiche. Data Center: Server-Prozessoren (EPYC) und KI-Beschleuniger (Instinct, zum Beispiel MI450), die mit Nvidia konkurrieren. Im 3. Quartal 2026 waren das 8.5 Mrd. $ oder 64 % des Umsatzes. Client und Gaming: Prozessoren für PCs (Ryzen) und Grafikchips für Spielkonsolen und PCs, zusammen 3.7 Mrd. $. Embedded: Chips für Industrie, Autos und Netzwerke aus dem Kauf von Xilinx (2022), 1.1 Mrd. $. Chefin ist seit 2014 Lisa Su. Mit OpenAI (Oktober 2025) und Meta (Februar 2026) hat AMD je eine Vereinbarung über bis zu 6 Gigawatt KI-Rechenleistung. Mit dem Rack-System Helios verkauft AMD neu ganze Serverschränke statt nur einzelne Chips.",
"why": "Von Februar bis März 2026 lag AMD um 190 bis 220 $. Im April stieg der Kurs laut S&P Global um 74 %, getrieben vom Meta-Vertrag (24.2.2026) und der Aussage von Lisa Su, dass die KI-Nachfrage nach Prozessoren unterschätzt sei. Bis zum 6.10.2026 lief die Aktie auf 658.52 $. Danach kamen Gewinnmitnahmen. Die Zahlen vom 3.11.2026 waren klar besser als erwartet (Umsatz 13.38 statt 13.09 Mrd. $, Ziel 4. Quartal 17 statt 16.23 Mrd. $), nachbörslich stieg die Aktie um rund 8 %. Am 5.11. fiel sie aber um 17.3 % auf 404.40 $. Gründe laut Motley Fool und INDmoney: Nach den Zwischenwahlen in den USA fürchtet die Börse strengere Regeln für KI und Baustopps für Rechenzentren in Texas und Georgia, der ganze Halbleitersektor fiel. Dazu sinkt das PC- und Spielegeschäft (Gaming −40 %). Ein Auftrag wurde nicht storniert. Am 9.11. stieg AMD um 13.3 %. Die Sorge ist also vor allem Stimmung und Bewertung, das Geschäft wächst stark.",
"kpis": [
 ["g","Umsatzwachstum","+41.9 %","Letzte 12 Monate bis September 2026, eigene Rechnung (45.4 Mrd. $). Im 3. Quartal +45 %, für das 4. Quartal erwartet AMD rund +66 %. Getrieben fast nur vom Rechenzentrum."],
 ["w","Operative Marge","17.8 %","Von 100 $ Umsatz bleiben rund 18 $ Betriebsgewinn (12 Monate, StockAnalysis). Bereinigt um Abschreibungen auf den Xilinx-Kauf und Aktienlöhne waren es im 3. Quartal 29 %. 2021 lag die Marge noch bei 22.2 %, 2023 nur bei 1.8 %."],
 ["g","Gewinn pro Aktie (EPS)","4.61 $","Letzte 12 Monate, eigene Rechnung: 2025 waren es 2.65 $, 2024 nur 1.00 $. Bereinigt stieg der Gewinn im 3. Quartal um 74 % auf 2.09 $."],
 ["w","ROIC","12.8 %","Auf 100 $ investiertes Kapital rund 13 $ Gewinn (StockAnalysis). Mittelmässig, weil der Kauf von Xilinx viel Kapital gebunden hat. Klar steigend: 2023 waren es 0.8 %, 2025 6.7 %."],
 ["w","Free Cashflow","7.06 Mrd. $","Letzte 12 Monate (StockAnalysis). Im 3. Quartal 2026 aber nur 554 Mio. $, weil AMD für 3 Mrd. $ mehr Lager aufbaute (für den Start von Helios). 2023 waren es nur 1.12 Mrd. $, der Verlauf schwankt."],
 ["g","Schulden","Netto-Cash","15.8 Mrd. $ Bargeld und kurzfristige Anlagen gegen 9.2 Mrd. $ Schulden und Leasing (StockAnalysis). Es bleiben netto 6.6 Mrd. $ mehr Geld als Schulden."],
 ["r","KGV","111.8","Du zahlst rund 112 Jahresgewinne (515.21 $ / 4.61 $). Eigener Schnitt 2021 bis 2025: 123.7, aber nur wegen 2023 (278.9). Ohne 2023 liegt der Schnitt bei 84.9. Auf den erwarteten Gewinn der nächsten 12 Monate rund 34."],
 ["r","Dividende","keine","AMD zahlt keine Dividende. Aktien kaufte AMD 2026 bis September nur für 221 Mio. $ zurück. Die Aktienzahl stieg in 12 Monaten um 1.4 %, vor allem wegen Aktienlöhnen. Dein Anteil an der Firma wird kleiner."]
],
"revtitle": "Umsatz pro Quartal (Mio. $)", "revunit": "Mio. $", "epsunit": "$",
"revnote": "Die letzten 4 Quartale lagen alle deutlich über dem Vorjahr: +34 %, +38 %, +50 % und +45 %. Im 3. Quartal wuchs AMD etwas langsamer als im 2., das Ziel für das 4. Quartal (rund 17'000 Mio. $) wäre aber ein neuer Sprung.",
"marginnote": "Betriebsgewinn pro 100 $ Umsatz (ausgewiesen). Nach dem Xilinx-Kauf 2022 brach die Marge wegen hoher Abschreibungen ein, seit 2023 steigt sie jedes Jahr.",
"finnote": "<b>Hinweis:</b> Zahlen in Mio. $. Jahre 2021 bis 2025 laut StockAnalysis. Letzte 12 Monate bis September 2026: Umsatz und EPS eigene Rechnung mit den Zahlen vom 3.11.2026, Marge, ROIC und Free Cashflow laut StockAnalysis (Stand 7.11.2026). KGV pro Jahr laut StockAnalysis, heute eigene Rechnung (515.21 $ / 4.61 $). Schnitt 2021 bis 2025: 123.7. Das EPS seit 2022 ist durch hohe Abschreibungen auf den Xilinx-Kauf gedrückt, darum sind die KGV-Werte so hoch.",
"FIN": [["2021",16434,"+68.3 %","22.2 %",2.57,3220,"72.8 %","55.8"],["2022",23601,"+43.6 %","5.4 %",0.84,3115,"4.5 %","79.1"],["2023",22680,"−3.9 %","1.8 %",0.53,1121,"0.8 %","278.9"],["2024",25785,"+13.7 %","8.1 %",1.00,2405,"3.1 %","123.8"],["2025",34639,"+34.3 %","10.8 %",2.65,6735,"6.7 %","80.7"],["Letzte 12 Mt.",45436,"+41.9 %","17.8 %",4.61,7060,"12.8 %","111.8"]],
"QREV": [["Q4 24",7658],["Q1 25",7438],["Q2 25",7685],["Q3 25",9246],["Q4 25",10270],["Q1 26",10253],["Q2 26",11536],["Q3 26",13377]],
"revdec": 0,
"MARGIN": [["2021",22.2],["2022",5.4],["2023",1.8],["2024",8.1],["2025",10.8],["12 Mt.",17.8]],
"Q": [
 ["Umsatztrend","4 von 4 Quartalen klar über Vorjahr (+34 % bis +50 %), Ziel 4. Quartal +66 %. Das 3. Quartal wuchs aber etwas langsamer als das 2.",14,15],
 ["Wachstumstempo","12 Monate +41.9 %, für 2027 erwartet AMD mehr als 80 %",10,10],
 ["Operative Marge","17.8 % (6 Pkt.), seit 2023 jedes Jahr gestiegen, aber noch unter 2021 (22.2 %), darum nur 4 statt 6 Pkt. für den Trend",10,15],
 ["Gewinnwachstum (EPS)","2025 +165 %, 12 Monate rund +125 %, bereinigt im 3. Quartal +74 %",10,10],
 ["Free Cashflow","Positiv, aber schwankend (2023: 1.12 Mrd. $, 2025: 6.74 Mrd. $), im 3. Quartal 2026 nur 554 Mio. $",6,10],
 ["ROIC","12.8 % (6 Pkt.), klar steigend seit 2023 (+1)",7,15],
 ["Schulden","Netto-Cash 6.6 Mrd. $",10,10],
 ["Bewertung vs. eigene Historie","KGV 111.8 gegen Ø 123.7, rund 10 % günstiger. Der Schnitt ist aber vom Ausreisser 2023 (278.9) verzerrt. Ohne 2023 (Ø 84.9) wäre die Aktie 32 % teurer (1 Pkt.). Darum Mittelwert",4,15]
],
"adwnote": ADW + "Die Wochen-A/D stieg von 2'265 (Januar 2026, Kurs 260 $) auf 3'011 (Ende September, Kurs 634 $). Seither fiel sie auf 2'654. Im Juli stand sie bei 2'651, damals lag der Kurs bei 476 $. Heute ist der Kurs höher (515 $), die A/D aber gleich. Beim Rückgang wurde also nicht panisch verkauft, beim Anstieg seit dem 5.11. aber auch nicht stark gekauft.",
"rsiwnote": RSIW + "53, neutral. Ende September war er mit 71 überkauft, in der Woche vom 2.11. lag er bei 46.",
"addnote": "Die Tages-A/D stieg im Jahr 2026 stark, von −337 (5.2.) auf 541 (28.10.). Am 28.10. lag sie höher als beim Allzeithoch am 6.10. (528), obwohl der Kurs tiefer war: ein gutes Zeichen. Beim Einbruch am 5.11. fiel sie auf 415, heute steht sie bei 456. Das ist tiefer als beim Tief vom 22.10. (495), obwohl der Kurs ähnlich hoch ist. Kurzfristig fehlt also die Bestätigung durch Käufer.",
"ind": [
 ["Kurs vs. EMA 50","515.21 &lt; 531.46","515.21 &gt; 416.24","Im Tageschart knapp unter der mittelfristigen Linie, in der Woche klar darüber."],
 ["Kurs vs. EMA 200","515.21 &gt; 439.96","515.21 &gt; 237.50","Klar über der langfristigen Linie, in der Woche mehr als doppelt so hoch. Das zeigt, wie stark der Anstieg 2026 war."],
 ["EMA 50 vs. EMA 200","50 über 200 (Golden Cross am 8.7.2025)","50 über 200 (seit November 2016)","Tag und Woche im Aufwärtstrend."],
 ["RSI (14)","48.6","53.4","Neutral. Am 5.11. war der Tages-RSI mit 29.7 überverkauft, seither dreht er nach oben."],
 ["A/D","über das Jahr stark gestiegen, seit 28.10. gefallen","seit Ende September gefallen, über das Jahr gestiegen","Langfristig Käufer, kurzfristig fehlt die Bestätigung."],
 ["Volumen","Ø 20 Tage 30.8 Mio. vs. Ø 100 Tage 25.4 Mio. Aktien","Mehr Handel als üblich, vor allem am 5.11. beim Einbruch."]
],
"smc": "Im Tageschart gibt es seit dem Allzeithoch tiefere Hochs und tiefere Tiefs: Hoch 658.52 $ (6.10.), Tief 502.60 $ (22.10.), tieferes Hoch 579.18 $ (28.10.), tieferes Tief 402.10 $ (5.11.). Das ist eine Abwärtsstruktur. In der Woche sieht es besser aus: Die Tiefs vom Juli (424.03 $) und August (440.50 $) wurden am 5.11. zwar kurz unterschritten, die Woche schloss aber bei 449.04 $, also über 424 $. Seither stieg der Kurs um 28 % auf 515 $ und steht jetzt im Widerstand der Spanne vom Juni (511.57 bis 557.89 $) und unter der Tages-EMA 50 (531.46 $). Die Spanne 402.10 bis 658.52 $ hat ihre Mitte bei 530.31 $: Der Kurs steht knapp im unteren, günstigeren Teil. Bestätigt wäre eine Wende im Tageschart erst mit einem Schluss über 579.18 $.",
"zones": [
 ["r","639.00–659.00 $","Widerstand: Hochs vom 25.9. (639.00) und Allzeithoch vom 6.10.2026 (658.52 $)."],
 ["r","579.00–585.00 $","Widerstand: letztes tieferes Hoch vom 28.10. (579.18) und Hoch vom 30.6.2026 (584.73 $)."],
 ["r","531.00–558.00 $","Widerstand: Tages-EMA 50 (531.46 $) und Spanne vom Juni 2026 (Wochenschlüsse 511.57 bis 557.89 $)."],
 ["t","579.18 $","<b>Trigger:</b> Tagesschluss über 579.18 $ (letztes tieferes Hoch), besser mit steigender Tages-A/D."],
 ["s","440.00–465.00 $","<b>Kaufzone 1:</b> Tages-EMA 200 (439.96 $), Tiefs vom 3.9. (440.50), 24.8. (451.00) und 11.8. (463.21 $), Wochenschluss vom 6.11. (449.04 $)."],
 ["s","402.00–425.00 $","<b>Kaufzone 2:</b> Tief vom 5.11. (402.10 $), Wochen-EMA 50 (416.24 $) und Tief vom 29.7. (424.03 $)."],
 ["r","400.00 $","Abbruch: Wochenschluss unter 400 $, also unter dem Tief vom 5.11.2026 (402.10 $). Nächste grössere Marke wäre erst das alte Hoch vom Oktober 2025 bei 267 $."]
],
"smart": [
 "<b>Insider:</b> Chefin Lisa Su verkaufte 2026 laut MarketBeat und InsiderTrades mehrmals je 125'000 Aktien, zum Beispiel am 13.5. (Ø 445.51 $, 55.7 Mio. $) und am 10.6. (Ø 460.69 $, 57.6 Mio. $). Im August verkauften auch Finanzchefin Jean Hu (15'000 Aktien, 7.1 Mio. $) und Forrest Norrod (7.9 Mio. $). Alles über vorab festgelegte Verkaufspläne (10b5-1). Käufe von Insidern am Markt fand ich keine.",
 "<b>Rückkäufe:</b> 2026 bis September nur 221 Mio. $, im 2. und 3. Quartal gar keine. Das sind weniger als 0.1 % des Börsenwerts (rund 845 Mrd. $). Die Aktienzahl steigt sogar (+1.4 % in 12 Monaten).",
 "<b>OpenAI-Optionen:</b> OpenAI kann laut Vertrag vom Oktober 2025 rund 10 % der AMD-Aktien über Optionen erhalten, wenn Liefer- und Kursziele erreicht werden. Das würde den Anteil der heutigen Aktionäre verwässern.",
 "<b>Analysten:</b> 53 Analysten, Kursziel im Schnitt 656.24 $, Bewertung «Strong Buy» (StockAnalysis, 7.11.2026). Nach den Zahlen erhöhten zum Beispiel Stifel von 700 auf 725 $ und Truist von 594 auf 605 $ (Finbold, 4.11.2026). Institutionelle Anleger halten rund 71 % der Aktien (MarketBeat)."
],
"seasnote": SEAS + "Daten seit 1985 (Monate mit mehr als 40 % Bewegung nicht gezählt). Stark sind November (+6.6 %, 62 % positive Jahre), Oktober (+5.1 %, 53 %) und Januar (+3.6 %, 56 %). Schwach sind Mai (−3.6 %, 39 %), Juni (−4.0 %, 39 %) und August (−4.4 %, nur 32 %). Dezember +1.2 % (51 %). AMD schwankt sehr stark, die Durchschnitte sind darum wenig verlässlich.",
"T": [
 ["Trend Woche (EMA 50/200)","Kurs über beiden, EMA 50 über 200. Der Abstand zur EMA 200 ist aber sehr gross (Kurs mehr als doppelt so hoch)",18,20],
 ["Trend Tag (EMA 50/200)","Kurs über EMA 200, aber unter EMA 50: Rücksetzer im Aufwärtstrend",6,10],
 ["Struktur (SMC)","Tageschart mit tieferen Hochs und tieferen Tiefen seit 6.10., in der Woche hielt der Schluss über dem Juli-Tief (424.03 $). Kein Bruch nach oben",6,20],
 ["RSI Tag/Woche","Tages-RSI dreht aus 29.7 (5.11.) auf 48.6, Woche 53. Keine Divergenz, Trend Tag angeschlagen",11,15],
 ["A/D Tag/Woche","Über das Jahr auf beiden Zeitebenen gestiegen, seit Oktober fällt sie mit dem Kurs und bestätigt die Erholung noch nicht",6,20],
 ["Smart Money","Start 3, gehäufte Insider-Verkäufe (−3), kaum Rückkäufe, Aktienzahl steigt",0,10],
 ["Saisonalität","November 62 %, Dezember 51 %, Januar 56 % positive Jahre",3,5]
],
"pro": [
 "Sehr starkes Wachstum: 3. Quartal 2026 Umsatz +45 % auf 13.4 Mrd. $, Rechenzentrum +97 %, beides über den Erwartungen.",
 "Ziel 4. Quartal rund 17 Mrd. $ (+66 %), deutlich über den erwarteten 16.23 Mrd. $. Für 2027 erwartet AMD mehr als 80 % Wachstum.",
 "Grosse Verträge mit OpenAI und Meta über je bis zu 6 Gigawatt. Anthropic, Meta, Microsoft, OpenAI und Oracle testen die ersten Helios-Systeme.",
 "Netto mehr Bargeld als Schulden (6.6 Mrd. $), Margen und ROIC steigen seit 2023 jedes Jahr.",
 "Chart: Wochentrend intakt, der Einbruch am 5.11. wurde in der Woche schnell zurückgekauft, Analysten-Kursziel (656 $) weit über dem Kurs."
],
"con": [
 "Sehr teuer: KGV 111.8, Kurs-Umsatz-Verhältnis rund 19. Der faire Wert im Branchenvergleich der App liegt weit unter dem Kurs.",
 "Abhängig von wenigen KI-Kunden und deren Ausgaben für Rechenzentren. Nach den US-Wahlen drohen Baustopps für Rechenzentren in einzelnen Staaten.",
 "PC- und Spielegeschäft schwach: Gaming −40 % im 3. Quartal, für 2027 erwartet AMD einen zweistelligen Rückgang der PC-Verkäufe.",
 "Free Cashflow im 3. Quartal nur 554 Mio. $, Lager stieg auf 11.5 Mrd. $. Engpass bei Speicherchips (HBM) kann Lieferungen bremsen.",
 "Insider verkaufen laufend, keine Dividende, kaum Rückkäufe. Sehr hohe Schwankung (Beta 2.5): −17 % an einem Tag (5.11.2026)."
],
"todo": [
 ["t","Beobachten","Alarm bei 579.18 $ (Trigger) und 465 $ (oberes Ende Kaufzone 1)."],
 ["s","Timing grün","Rücksetzer in 440 bis 465 $, der hält und mit steigender Tages-A/D dreht. Oder Tagesschluss über 579.18 $ mit steigender A/D. Fundamental: Umsatz im 4. Quartal bei rund 17 Mrd. $ und Bestätigung der mehr als 80 % Wachstum für 2027."],
 ["r","Abbruch","Wochenschluss unter 400 $."],
 ["","Nächste Zahlen","4. Quartal 2026: voraussichtlich Anfang Februar 2027 (Wall Street Horizon schätzt den 2.2.2027, 2026 war es der 3.2., noch nicht bestätigt)."]
],
"bands": [{"from":639.0,"to":659.0,"type":"res"},{"from":579.0,"to":585.0,"type":"res"},{"from":531.0,"to":558.0,"type":"res"},{"from":440.0,"to":465.0,"type":"sup"},{"from":402.0,"to":425.0,"type":"sup"}],
"refs": [{"v":579.18,"label":"Trigger 579.18"},{"v":400.0,"label":"Abbruch 400"}],
"sources": L("https://ir.amd.com/news-events/press-releases/detail/1303/amd-reports-third-quarter-2026-financial-results","AMD: Zahlen 3. Quartal 2026 (3.11.2026)") + ", " + L("https://www.sec.gov/Archives/edgar/data/0000002488/000000248826000121/q22026991.htm","AMD: Zahlen 2. Quartal 2026 (SEC, 4.8.2026)") + ", " + L("https://www.thestar.com.my/tech/tech-news/2026/11/04/amd-forecasts-quarterly-revenue-above-estimates-as-data-center-growth-accelerates","Reuters: Ausblick über den Erwartungen (4.11.2026)") + ", " + L("https://www.newsquawk.com/headlines/advanced-micro-devices-inc-amd-q3-2026-usd-adj-eps-209-exp-195-revenue-134bln-exp-131bln","Newsquawk: Q3 gegen Erwartungen") + ", " + L("https://stockanalysis.com/stocks/amd/financials","StockAnalysis.com (AMD)") + " (Finanzen, Kennzahlen, Statistik, Stand 7.11.2026), " + L("https://www.fool.com/investing/2026/11/05/why-amd-stock-is-down-today/","Motley Fool: Kurssturz 5.11.2026") + ", " + L("https://www.indmoney.com/blog/us-stocks/qualcomm-amd-stock-falling","INDmoney: Gründe für den Einbruch") + ", " + L("https://www.tikr.com/blog/amd-stock-surged-74-in-april-q1-2026-earnings-could-tell-us-if-the-run-is-just-getting-started?","TIKR: Anstieg im April 2026") + ", " + L("https://www.marketbeat.com/instant-alerts/insider-selling-advanced-micro-devices-nasdaqamd-ceo-sells-125000-shares-of-stock-2026-06-12/","MarketBeat: Insider") + ", " + L("https://finbold.com/6-wall-street-analysts-set-amd-stock-price-target-after-q3-earnings/","Finbold: Kursziele nach Q3 (4.11.2026)") + ", " + L("https://wallstreethorizon.com/amd-earnings-calendar","Wall Street Horizon: Termine") + ". Branchenvergleich der App: Note 2.8 von 5, fairer Wert rund 199 $ (61 % unter dem heutigen Kurs), Unsicherheit hoch."
}
if __name__ == "__main__":
    json.dump(c, open(os.path.join(P, "config", "AMD.json"), "w"), ensure_ascii=False, indent=1)
    print("ok", sum(r[2] for r in c["Q"]), sum(r[2] for r in c["T"]))
