import json, os, sys
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, P)
from helpers import L, ADW, RSIW, SEAS
c = {
"ticker": "RSG", "name": "Republic Services", "datum": "29.10.2026", "waehrung": "USD", "land": "USA",
"meta": "Republic Services, Inc. · NYSE: RSG · Abfuhr, Recycling, Deponien und Sondermüll · Phoenix, USA",
"price": "236.28 $",
"pricemeta": "Schluss 29.10.2026 (vor den Zahlen am Abend) · 52 Wochen: 196.41 – 243.22 $ · Allzeithoch Woche: 258.75 $ im Juni 2025",
"verdict": "Republic Services holt in den USA Abfall ab, sortiert ihn und lagert ihn auf eigenen Deponien. Das Geschäft ist sehr stabil: Der Umsatz steigt seit Jahren, der Free Cashflow wuchs jedes Jahr seit 2021 auf zuletzt 2.65 Mrd. $. Das Wachstum kommt aber fast nur aus Preiserhöhungen und Zukäufen, die Mengen sinken leicht (3. Quartal 2026: −0.6 %). Mit einem KGV von 32.7 ist die Aktie etwas teurer als ihr eigener Schnitt (30.6). Qualität hellgrün (61), Timing hellgrün (64): Der Kurs ist im Oktober aus einer langen Seitwärtsphase nach oben ausgebrochen, Grossaktionär Cascade (Bill Gates) kaufte von Mai bis September für rund 1.6 Mrd. $ dazu. Warnzeichen: Die A/D-Linie steigt nicht mit. Die Zahlen zum 3. Quartal vom 29.10.2026 (Umsatz +8.2 %, Ziel 2026 erhöht) kamen erst nach Börsenschluss. Keine Anlageberatung.",
"about": "Republic Services aus Phoenix (Arizona) ist nach Waste Management die zweitgrösste Abfallfirma der USA. Sie leert Mülltonnen und Container bei Haushalten, Gemeinden und Firmen, betreibt Umladestationen, Recyclinganlagen und vor allem eigene Deponien. Deponien sind der Burggraben: Neue Bewilligungen sind in den USA sehr schwer zu bekommen, wer sie hat, kann die Preise jedes Jahr erhöhen. Seit dem Kauf von US Ecology (2022) gibt es den Bereich Environmental Solutions für Sondermüll und Industrieabfall. Im 3. Quartal 2026 machte Republic Services 4.56 Mrd. $ Umsatz. Chef ist Jon Vander Ark. Die Firma wächst stark über Zukäufe kleiner Abfallfirmen (2026 bis September rund 1.1 Mrd. $). Abfall fällt auch in einer Rezession an, darum gilt die Aktie als defensiv. Nur das Geschäft mit Bauschutt und Sondermüll schwankt mit der Konjunktur.",
"why": "Im Juni 2025 erreichte die Aktie ihr Hoch bei 258.75 $ (Wochenschluss). Danach fiel sie bis Mai 2026 auf 196.41 $ (−24 %). Gründe: Die Börse hatte Abfall-Aktien sehr hoch bewertet (KGV über 34), und das Wachstum liess nach: 2025 stieg der Umsatz nur noch um 3.5 %. Die Mengen sinken, weil weniger gebaut wird (Bauschutt auf Deponien im 2. Quartal 2026 −37 %) und Republic Services einige Verträge mit Gemeinden verloren hat (Haushaltsabfuhr −4.3 %). Seit Mai steigt der Kurs wieder: Grossaktionär Cascade Investment (die Beteiligungsfirma von Bill Gates) kaufte im Mai und von August bis September Aktien für rund 1.6 Mrd. $. Am 22.10.2026 stieg RSG um 5 %, weil Konkurrent Waste Connections gute Zahlen meldete. Am 23.10. erreichte die Aktie 243.22 $, das höchste seit Juli 2025. Die Sorgen sind also eher Bewertung und Stimmung, das Geschäft selbst läuft stabil.",
"kpis": [
 ["w","Umsatzwachstum","+4.5 %","Letzte 12 Monate bis September 2026, eigene Rechnung. Im 3. Quartal +8.2 %, davon kamen 1.3 Punkte aus Zukäufen und 1.8 Punkte aus Treibstoff-Zuschlägen. Die Mengen sanken um 0.6 %."],
 ["g","Operative Marge","20.1 %","Von 100 $ Umsatz bleiben rund 20 $ Betriebsgewinn (12 Monate, eigene Rechnung). Für eine Abfallfirma gut. 2021 waren es 18.7 %, seit 2024 stabil."],
 ["w","Gewinn pro Aktie (EPS)","7.22 $","Letzte 12 Monate bis September 2026, eigene Rechnung: +7.4 % zum Vorjahr. Bereinigt stieg der Gewinn im 3. Quartal nur um 2.1 % (1.94 $). Von 2022 bis 2024 waren es +16 bis +19 % pro Jahr."],
 ["w","ROIC","11.1 %","Auf 100 $ investiertes Kapital rund 11 $ Gewinn. Mittelmässig, weil Deponien und Lastwagen viel Kapital brauchen. Leicht steigend (2021: 9.5 %)."],
 ["g","Free Cashflow","2.65 Mrd. $","Letzte 12 Monate bis Juni 2026. Jedes Jahr seit 2021 gestiegen (damals 1.47 Mrd. $). Ziel 2026: 2.57 bis 2.59 Mrd. $ (bereinigt)."],
 ["w","Schulden","2.7 × EBITDA","Nettoschulden rund 14.0 Mrd. $. Mit dem Betriebsgewinn vor Abschreibungen (EBITDA) wären sie in rund 2.7 Jahren bezahlt. Für ein so stabiles Geschäft üblich, aber nicht wenig."],
 ["w","KGV","32.7","Du zahlst rund 33 Jahresgewinne. Eigener Schnitt 2021 bis 2025: 30.6. Also etwa 7 % teurer als üblich. Für eine Firma mit rund 5 % Wachstum ist das viel."],
 ["w","Dividende","1.1 %","0.67 $ pro Quartal, also 2.68 $ pro Jahr. 4 Zahlungen (15. Januar, April, Juli, Oktober). Im Juli 2026 um 7.2 % erhöht. Es fliessen nur rund 37 % des Gewinns in die Dividende."]
],
"revtitle": "Umsatz pro Quartal (Mio. $)", "revunit": "Mio. $", "epsunit": "$",
"revnote": "Die letzten 4 Quartale lagen alle über dem Vorjahr, und das Wachstum wurde schneller: +2.2 %, +2.6 %, +4.6 % und +8.2 %. Ein Teil davon kommt aus Zukäufen und höheren Treibstoff-Zuschlägen, nicht aus mehr Abfall.",
"marginnote": "Betriebsgewinn pro 100 $ Umsatz. Von 17.9 % (2022) auf rund 20 % gestiegen, seit 2024 stabil.",
"finnote": "<b>Hinweis:</b> Zahlen in Mio. $. Jahre 2021 bis 2025 laut StockAnalysis. Letzte 12 Monate: Umsatz, Marge und EPS eigene Rechnung bis September 2026 mit den Zahlen vom 29.10.2026, Free Cashflow bis Juni 2026. KGV pro Jahr laut StockAnalysis, heute eigene Rechnung (236.28 $ / 7.22 $). Schnitt 2021 bis 2025: 30.6.",
"FIN": [["2021",11295,"+11.2 %","18.7 %",4.04,1470,"9.5 %","34.3"],["2022",13511,"+19.6 %","17.9 %",4.69,1736,"9.7 %","27.4"],["2023",14965,"+10.8 %","18.8 %",5.47,1987,"9.8 %","30.0"],["2024",16032,"+7.1 %","20.1 %",6.49,2081,"11.4 %","30.8"],["2025",16591,"+3.5 %","20.0 %",6.85,2409,"11.0 %","30.7"],["Letzte 12 Mt.",17237,"+4.5 %","20.1 %",7.22,2653,"11.1 %","32.7"]],
"QREV": [["Q4 24",4046],["Q1 25",4009],["Q2 25",4235],["Q3 25",4212],["Q4 25",4135],["Q1 26",4113],["Q2 26",4430],["Q3 26",4559]],
"revdec": 0,
"MARGIN": [["2021",18.7],["2022",17.9],["2023",18.8],["2024",20.1],["2025",20.0],["12 Mt.",20.1]],
"Q": [
 ["Umsatztrend","4 von 4 Quartalen über Vorjahr, Wachstum beschleunigt (+2.2 % bis +8.2 %), aber teils durch Zukäufe und Treibstoff-Zuschläge",14,15],
 ["Wachstumstempo","Ziel 2026 rund +5 %, davon rund 1 Punkt aus Zukäufen: aus eigener Kraft rund 4 %",3,10],
 ["Operative Marge","20.1 % (6 Pkt.), seit 2021 leicht gestiegen, seit 2024 flach (4 Pkt.)",10,15],
 ["Gewinnwachstum (EPS)","12 Monate +7.4 %, bereinigt im 3. Quartal nur +2.1 %. Der Schnitt 2023 bis 2025 (+14 %) ist vorbei",5,10],
 ["Free Cashflow","Positiv und jedes Jahr seit 2021 gestiegen",10,10],
 ["ROIC","11.1 % (6 Pkt.), steigend seit 2021 (+1)",7,15],
 ["Schulden","Nettoschulden/EBITDA 2.7",5,10],
 ["Bewertung vs. eigene Historie","KGV 32.7 statt Ø 30.6, rund 7 % teurer: im Bereich ±10 %",7,15]
],
"adwnote": ADW + "Warnzeichen: Im März 2026 stand die Wochen-A/D bei 339 (Kurs 233 $). Heute ist der Kurs höher (236 $), die A/D aber tiefer (320). Beim Ausbruch im Oktober wird also weniger gekauft als im Frühling. Seit Ende September (305) steigt sie immerhin wieder.",
"rsiwnote": RSIW + "62, kräftig, aber noch nicht überkauft. Vor einem Monat 44.",
"addnote": "Die Tages-A/D fiel seit Januar 2026 von rund 28 auf rund 1, obwohl der Kurs von 220 auf 236 $ stieg. Das heisst: Über das Jahr wurde eher verkauft. Seit dem Tief vom 1.10. (−3.3) steigt sie wieder mit dem Kurs, am 22.10. auf 1.8, heute 0.7. Kurzfristig kaufen also wieder mehr Leute, die Bestätigung über das Jahr fehlt.",
"ind": [
 ["Kurs vs. EMA 50","236.28 &gt; 223.22","236.28 &gt; 218.99","Klar über der mittelfristigen Linie, auf beiden Zeitebenen."],
 ["Kurs vs. EMA 200","236.28 &gt; 218.51","236.28 &gt; 195.98","Über der langfristigen Linie, in der Woche rund 21 % darüber."],
 ["EMA 50 vs. EMA 200","50 über 200 (Golden Cross am 14.10.2026)","50 über 200 (seit November 2016)","Tag und Woche im Aufwärtstrend. Die Wochen-EMA 50 lief aber ein Jahr lang flach."],
 ["RSI (14)","62.5","62.3","Kräftig. Am 22.10. war der Tages-RSI mit 75.6 überkauft, jetzt hat er sich abgekühlt."],
 ["A/D","steigt seit 1.10., über das Jahr aber gefallen","tiefer als im März trotz höherem Kurs","Kurzfristig positiv, längerfristig Verteilung (Verkäufer)."],
 ["Volumen","Ø 20 Tage 1.27 Mio. vs. Ø 100 Tage 1.46 Mio. Aktien","Der Ausbruch kam mit eher wenig Handel."]
],
"smc": "Von Mai bis September 2026 lief RSG seitwärts zwischen rund 197 und 228 $: Tiefs 196.41 (11.5.), 197.62 (2.6.), 204.80 (5.8.) und 205.86 $ (2.10.), Hochs 228.22 (17.7.), 225.74 (3.9.) und 227.32 $ (14.9.). Die Tiefs wurden also höher. Am 15.10. schloss der Kurs mit 229.65 $ über dem Juli-Hoch (228.22 $): ein Break of Structure nach oben. Auch in der Woche ist das März-Hoch (233.42 $) überwunden. Neues Hoch am 23.10. bei 243.22 $. Der Kurs steht heute im oberen Teil der Spanne 205.86 bis 243.22 $ (Mitte bei 224.50 $), also eher teuer. Ein Rücksetzer an die Ausbruchszone um 224 bis 228 $ wäre normal.",
"zones": [
 ["r","249.00–259.00 $","Widerstand: Hoch vom März 2025 (249.73) und Allzeithoch vom Juni 2025 (258.75 $, Wochenschluss)."],
 ["r","240.00–243.50 $","Widerstand: 52-Wochen-Hoch vom 23.10.2026 (243.22 $)."],
 ["t","243.22 $","<b>Trigger:</b> Tagesschluss über 243.22 $ (neues Hoch), besser mit steigender Tages-A/D."],
 ["s","223.00–228.50 $","<b>Kaufzone 1:</b> Alte Hochs vom Juli und September (228.22 und 227.32 $), jetzt Unterstützung, dazu Tages-EMA 50 (223.22 $) und Mitte der Spanne (224.50 $)."],
 ["s","216.00–220.00 $","<b>Kaufzone 2:</b> Wochen-EMA 50 (218.99), Tages-EMA 200 (218.51) und Tief vom 9.9. (219.58 $)."],
 ["r","205.00 $","Abbruch: Wochenschluss unter 205 $, also unter dem letzten höheren Tief vom 2.10. (205.86 $)."]
],
"smart": [
 "<b>Grossaktionär:</b> Cascade Investment (Bill Gates) kaufte laut Pflichtmeldungen vom 11.5. bis 18.5. und vom 10.8. bis 11.9.2026 an fast jedem Börsentag Aktien, zusammen rund 7.2 Mio. Stück für rund 1.6 Mrd. $ zu 197 bis 225 $ (MarketBeat).",
 "<b>Insider:</b> Verwaltungsrätin Katharine Weymouth kaufte am 9.12.2025 Aktien für 100'000 $. Einziger Verkauf in 12 Monaten: Verwaltungsrätin Sandra Volpe, 1'800 Aktien für 380'000 $ (11.6.2026).",
 "<b>Rückkäufe:</b> 2026 bis September 848 Mio. $, das sind rund 1.2 % des Börsenwerts (rund 72 Mrd. $). Neu bewilligt: 5 Mrd. $ für 2027 bis 2029, also rund 1.7 Mrd. $ oder 2.3 % pro Jahr.",
 "<b>Analysten:</b> 22 Analysten, 13 Kaufen und 9 Halten, Kursziel im Schnitt 243.73 $ (MarketBeat, 26.10.2026), nur knapp über dem Kurs. Im Oktober senkten mehrere Banken ihr Ziel, zum Beispiel Morgan Stanley von 232 auf 219 $ (13.10.). Baird erhöhte von 242 auf 245 $ (22.10.)."
],
"seasnote": SEAS + "Daten seit 1998. Stark sind April (+4.8 %, 82 % positive Jahre), November (+2.7 %, 79 %) und Mai (+2.7 %, 68 %). Schwach ist September (−1.4 %, nur 34 %). Dezember +1.8 % (64 %), Januar −0.7 % (50 %).",
"T": [
 ["Trend Woche (EMA 50/200)","Kurs über beiden, EMA 50 über 200. Die EMA 50 lief aber lange flach",18,20],
 ["Trend Tag (EMA 50/200)","Kurs über beiden, Golden Cross am 14.10.2026",9,10],
 ["Struktur (SMC)","Break of Structure nach oben am 15.10. nach höheren Tiefs, Kurs aber im oberen, teuren Teil der Spanne",15,20],
 ["RSI Tag/Woche","62 und 62, kein Signal, kurz vorher überkauft (75.6)",6,15],
 ["A/D Tag/Woche","Über das Jahr Verteilung auf beiden Zeitebenen (A/D tiefer bei höherem Kurs), seit 1.10. steigt sie kurzfristig mit",3,20],
 ["Smart Money","Start 3, Käufe des Grossaktionärs Cascade am Markt (+4), bekannter Investor baut auf (+1, derselbe Käufer), Rückkauf unter 2 %",8,10],
 ["Saisonalität","November 79 %, Dezember 64 % positive Jahre, Januar 50 %",5,5]
],
"pro": [
 "Sehr stabiles Geschäft: Abfall fällt immer an, Deponien sind kaum zu ersetzen, Preise steigen jedes Jahr (3. Quartal 2026: +5.3 % Kernpreis).",
 "Free Cashflow seit 2021 jedes Jahr gestiegen, von 1.47 auf 2.65 Mrd. $.",
 "3. Quartal 2026: Umsatz +8.2 % (4.56 Mrd. $, über den Erwartungen), Jahresziel erhöht auf 17.43 bis 17.48 Mrd. $.",
 "Grossaktionär Cascade (Bill Gates) kaufte 2026 für rund 1.6 Mrd. $ dazu, neues Rückkaufprogramm 5 Mrd. $ ab 2027.",
 "Chart: Ausbruch aus der Seitwärtsphase, Golden Cross im Tageschart, Saisonalität November und Dezember gut."
],
"con": [
 "Wachstum fast nur über Preise und Zukäufe, die Abfallmengen sinken (3. Quartal −0.6 %, 9 Monate −1.0 %).",
 "Bereinigter Gewinn pro Aktie stieg im 3. Quartal nur um 2.1 %.",
 "Teuer: KGV 32.7 für rund 5 % Wachstum. Der faire Wert im Branchenvergleich der App liegt unter dem Kurs.",
 "Rund 14 Mrd. $ Schulden (2.7 × EBITDA), höhere Zinsen würden belasten.",
 "A/D-Linie bestätigt den Ausbruch nicht, Analysten-Kursziel (243.73 $) kaum über dem Kurs. Dividende nur 1.1 %."
],
"todo": [
 ["t","Beobachten","Alarm bei 243.22 $ (Trigger) und 228 $ (oberes Ende Kaufzone 1)."],
 ["s","Timing grün","Rücksetzer in 223 bis 228.50 $, der hält und mit steigender A/D dreht. Oder Tagesschluss über 243.22 $ mit steigender A/D. Fundamental: Mengen wieder positiv und Ziele für 2027 im Februar mit mehr als 5 % Umsatzwachstum."],
 ["r","Abbruch","Wochenschluss unter 205 $."],
 ["","Nächste Zahlen","4. Quartal und Ziele für 2027: voraussichtlich Mitte Februar 2027 (2026 war es der 17.2., noch nicht bestätigt). Die Zahlen zum 3. Quartal kamen am 29.10.2026 nach Börsenschluss, die Kursreaktion ist hier noch nicht drin."]
],
"bands": [{"from":249.0,"to":259.0,"type":"res"},{"from":240.0,"to":243.5,"type":"res"},{"from":223.0,"to":228.5,"type":"sup"},{"from":216.0,"to":220.0,"type":"sup"}],
"refs": [{"v":243.22,"label":"Trigger 243.22"}],
"sources": L("https://www.prnewswire.com/news-releases/republic-services-inc-reports-third-quarter-2026-results-302924227.html","Republic Services: Zahlen 3. Quartal 2026 (29.10.2026)") + ", " + L("https://stockstory.org/us/stocks/nyse/rsg/news/earnings/republic-servicess-nysersg-q3-2026-sales-top-estimates-full-year-outlook-slightly-exceeds-expectations","StockStory: Q3 gegen Erwartungen") + ", " + L("https://stockanalysis.com/stocks/rsg/financials/","StockAnalysis.com (RSG)") + " (Finanzen, Kennzahlen, Dividende, Stand 29.10.2026), " + L("https://www.tradingkey.com/news/earnings/262085755-tradingkey","TradingKey: Zahlen 2. Quartal 2026") + ", " + L("https://finance.yahoo.com/markets/stocks/articles/rsg-raises-2026-outlook-pricing-133100650.html","Zacks: Mengen und Preise 2. Quartal") + ", " + L("https://www.marketbeat.com/stocks/NYSE/RSG/insider-trades/","MarketBeat: Insider") + ", " + L("https://www.marketbeat.com/stocks/NYSE/RSG/forecast/","MarketBeat: Analysten") + ", " + L("https://weissratings.com/en/instant-news-alerts/republic-services-inc-rsg-up-5-0-should-i-acquire-shares-here","Weiss Ratings: Kurssprung 22.10.2026") + ". Branchenvergleich der App: Note 2.5 von 5, fairer Wert rund 182 $ (24 % unter dem Kurs), Unsicherheit sehr hoch."
}
if __name__ == "__main__":
    json.dump(c, open(os.path.join(P, "config", "RSG.json"), "w"), ensure_ascii=False, indent=1)
    print("ok", sum(r[2] for r in c["Q"]), sum(r[2] for r in c["T"]))
