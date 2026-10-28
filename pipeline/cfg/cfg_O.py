import json, os, sys
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, P)
from helpers import L, ADW, RSIW, SEAS
c = {
"ticker": "O", "name": "Realty Income", "datum": "28.10.2026", "waehrung": "USD", "land": "USA",
"meta": "Realty Income Corporation · NYSE: O · Immobilienfirma (REIT) mit Netto-Mietverträgen · San Diego, USA",
"price": "56.23 USD",
"pricemeta": "Schluss 28.10.2026 · 52 Wochen: 53.15 – 67.94 USD · Allzeithoch rund 82 USD (Wochenschluss)",
"verdict": "Realty Income vermietet über 15'500 Läden, Lager und andere Gebäude an rund 1'800 Firmen und zahlt jeden Monat eine Dividende (zurzeit 0.2715 USD, rund 5.8 % Rendite). Das Geschäft läuft stabil: 98.8 % der Gebäude sind vermietet, der Mittelzufluss pro Aktie (AFFO, siehe unten) soll 2026 um rund 3.7 % auf 4.44 bis 4.45 USD steigen. Die Aktie fiel trotzdem von 67.15 USD (Juli) auf 53.15 USD (8.10.2026), vor allem wegen der Zinsen: Die 10-jährige US-Staatsanleihe rentierte im September über 5 %. Dann werden Schulden teurer und Anleihen zur Konkurrenz für Dividendenaktien. Achtung: Bei einem REIT sagen Gewinn und KGV wenig aus, darum bewerte ich mit AFFO und Kurs/AFFO. Qualität gelb (52): sicherer Mieter-Mix, aber viele Schulden, tiefe Kapitalrendite und nur rund 3 bis 4 % Wachstum pro Aktie. Timing gelb (46): Der Kurs erholt sich vom Tief, der Abwärtstrend ist aber noch nicht gebrochen. Keine Anlageberatung.",
"about": "Realty Income (gegründet 1969, San Diego) ist ein REIT: eine Immobilienfirma, die mindestens 90 % ihres steuerbaren Gewinns ausschütten muss und dafür kaum Gewinnsteuern zahlt. Sie besitzt 15'588 Gebäude in den USA, Grossbritannien und acht weiteren Ländern Europas, vermietet an 1'798 Firmen aus 92 Branchen (30.6.2026). Typisch sind Läden von Supermärkten, Tankstellen-Shops, Baumärkten und Discountern, dazu Lager, Fabriken und neu Rechenzentren. Fast alles sind Netto-Mietverträge: Der Mieter zahlt Steuern, Versicherung und Unterhalt selbst. Die Verträge laufen im Schnitt noch 8.6 Jahre und haben meist eingebaute Mieterhöhungen. Realty Income nennt sich «The Monthly Dividend Company»: Die Dividende kommt jeden Monat und wurde seit dem Börsengang 1994 schon 136 Mal erhöht. Wachstum kommt vor allem durch den Kauf neuer Gebäude (2026 geplant: rund 10 Mrd. USD), bezahlt mit neuen Schulden und neuen Aktien.",
"why": "Wichtig zum Verständnis: Ein REIT schreibt seine Gebäude jedes Jahr ab (Q2 2026: 645 Mio. USD). Das drückt den Buchgewinn, obwohl kein Geld abfliesst. Darum schaut man auf AFFO (angepasster Mittelzufluss aus dem Geschäft): Gewinn plus Abschreibungen, minus laufende Unterhaltskosten. 2025 waren das 4.28 USD pro Aktie, der Buchgewinn nur 1.17 USD. Zum Kurs: Im Februar 2026 erreichte die Aktie 67.94 USD, im Juli nochmals 67.15 USD. Seither fällt sie: im September fünf Wochen in Folge, am 8.10.2026 bis 53.15 USD (Tief seit Frühling 2025). Gründe: Die Rendite der 10-jährigen US-Staatsanleihe stieg im September auf 5.01 bis 5.12 %, den höchsten Wert seit fast 20 Jahren (Benzinga, 27.9.). Die Zinskosten stiegen im 2. Quartal auf 312 Mio. USD (Vorjahr 284 Mio.), die Schulden auf das 5.4-fache des Betriebsgewinns vor Abschreibungen (vorher 5.2). Der Buchgewinn im 2. Quartal (0.37 USD je Aktie) lag wegen einer Wertberichtigung von 54 Mio. USD unter den Erwartungen. Scotiabank stufte auf «Sector Perform» ab (Kursziel 67 auf 58 USD), Evercore, Mizuho und Barclays senkten die Ziele. Das Geschäft selbst lief gut: Die Firma hob im August die AFFO-Prognose und das Kaufvolumen an. Es ist also vor allem ein Zins-Thema, aber höhere Zinsen machen Wachstum für Realty Income echt teurer.",
"kpis": [
 ["g","Umsatzwachstum","+10.7 %","Letzte 12 Monate (bis 30.6.2026). Das kommt vor allem aus Zukäufen. Gleiche Gebäude wie im Vorjahr bringen nur rund 1.1 % mehr Miete (Firmenprognose 2026)."],
 ["g","Operative Marge","46.0 %","Von 100 USD Miete bleiben 46 USD Betriebsgewinn, nach den hohen Abschreibungen. Ohne Abschreibungen bleibt fast alles, weil die Mieter die Nebenkosten zahlen."],
 ["w","AFFO pro Aktie","4.39 USD","Letzte 12 Monate, statt Gewinn pro Aktie (Buchgewinn nur 1.37 USD). Prognose 2026: 4.44 bis 4.45 USD, also rund +3.7 %. Seit 2022 nur rund +3 % pro Jahr."],
 ["r","ROIC","3.6 %","Kapitalrendite laut StockAnalysis. Sehr tief, aber typisch für Immobilien mit hohen Abschreibungen. Neue Käufe bringen laut Firma rund 7.3 % Anfangsrendite (2. Quartal 2026)."],
 ["g","Operativer Cashflow","4.17 Mrd. USD","Letzte 12 Monate. Seit 2021 jedes Jahr gestiegen (1.32 Mrd.). Klassischer Free Cashflow ist negativ, weil die Firma laufend Gebäude kauft."],
 ["r","Nettoschulden / EBITDAre","5.4","Schulden von 30.4 Mrd. USD entsprechen 5.4 Jahren Betriebsgewinn vor Abschreibungen (30.6.2026). Für einen REIT üblich, nach unserem Schema aber hoch. Zinskosten steigen."],
 ["g","Kurs / AFFO","12.8","Du zahlst rund 13 Jahre Mittelzufluss. Eigener Schnitt 2021 bis 2025: 15.3. Also rund 16 % günstiger als üblich. Das normale KGV (rund 41) ist bei REITs nicht aussagekräftig."],
 ["g","Dividende","5.8 %","0.2715 USD pro Monat, aufs Jahr 3.258 USD. Rund 73 % des AFFO werden ausgeschüttet: gedeckt. Zuletzt erhöht am 8.9.2026, aber nur um 0.2 %."]
],
"revtitle": "Umsatz pro Quartal (Mrd. $)", "revunit": "Mio. $", "epsunit": "(AFFO, $)", "pecol": "Kurs/AFFO",
"revnote": "Alle 8 Quartale über dem Vorjahr, zuletzt +10.5, +11.0, +12.2 und +9.7 %. Das Wachstum stammt fast ganz aus neu gekauften Gebäuden, nicht aus höheren Mieten.",
"marginnote": "Betriebsgewinn pro 100 USD Umsatz, nach Abschreibungen. 2022 tiefer wegen der Übernahme von VEREIT, seither wieder gestiegen. Über 5 Jahre etwa stabil.",
"finnote": "<b>Hinweis:</b> Bei einem REIT ersetze ich den Gewinn pro Aktie durch AFFO pro Aktie und das KGV durch Kurs/AFFO (Jahresschnitt laut Sure Dividend, heute eigene Rechnung mit 56.23 USD). In der Spalte «Free Cashflow» steht der operative Cashflow in Mio. USD, weil der Kauf neuer Gebäude der eigentliche Zweck der Firma ist. Umsatz, Marge, Cashflow und ROIC laut StockAnalysis. Grosse Sprünge 2022 und 2024 durch die Übernahmen von VEREIT (Ende 2021) und Spirit Realty (Januar 2024).",
"FIN": [["2021",2082,"+26.4 %","45.8 %",3.59,1322,"2.9 %","19.9"],["2022",3337,"+60.3 %","39.0 %",3.92,2564,"2.8 %","16.2"],["2023",4082,"+22.3 %","42.3 %",4.00,2959,"3.2 %","14.4"],["2024",5279,"+29.3 %","42.0 %",4.19,3573,"3.4 %","12.7"],["2025",5763,"+9.2 %","44.6 %",4.28,3995,"3.5 %","13.4"],["Letzte 12 Mt.",6066,"+10.7 %","46.0 %",4.39,4166,"3.6 %","12.8"]],
"QREV": [["Q3 24",1.33],["Q4 24",1.34],["Q1 25",1.38],["Q2 25",1.41],["Q3 25",1.47],["Q4 25",1.49],["Q1 26",1.55],["Q2 26",1.55]],
"revdec": 2,
"MARGIN": [["2021",45.8],["2022",39.0],["2023",42.3],["2024",42.0],["2025",44.6],["12 Mt.",46.0]],
"Q": [
 ["Umsatztrend","4 von 4 Quartalen über Vorjahr (+10.5, +11.0, +12.2, +9.7 %), Tempo nicht steigend",12,15],
 ["Wachstumstempo","Umsatz +10.7 %, aber fast nur durch Zukäufe. Pro Aktie (AFFO) rund +3.7 %, gleiche Gebäude rund +1.1 %. Gewertet: 3 bis 6 %",3,10],
 ["Operative Marge","46.0 % (9 Pkt.), über 5 Jahre etwa stabil (3 Pkt.)",12,15],
 ["Gewinnwachstum (EPS)","Mit AFFO pro Aktie statt Gewinn: 3.92 USD (2022) auf 4.28 USD (2025), rund +3 % pro Jahr, 2026 rund +3.7 %",2,10],
 ["Free Cashflow","Mit AFFO und operativem Cashflow: positiv und jedes Jahr seit 2021 gestiegen",10,10],
 ["ROIC","3.6 % (2 Pkt.), seit 2022 leicht steigend (+1). Für REITs typisch tief",3,15],
 ["Schulden","Nettoschulden / EBITDAre 5.4 (über 4)",0,10],
 ["Bewertung vs. eigene Historie","Kurs/AFFO 12.8 statt Ø 15.3 (2021 bis 2025), rund 16 % günstiger",10,15]
],
"adwnote": ADW + "Von Juli (347) bis Ende September (184) fiel die Wochen-A/D stark mit dem Kurs: Es wurde verkauft. Seit dem Tief steigt sie wieder auf 256, zusammen mit dem Kurs. Noch keine Divergenz, aber die Verkäufe haben nachgelassen.",
"rsiwnote": RSIW + "Ende September bei 29 (überverkauft), heute 39: dreht nach oben, ist aber noch schwach.",
"addnote": "Positiv: Beim neuen Kurstief am 8.10. (53.15 USD) stand die Tages-A/D höher (−142.6) als beim Tief vom 1.10. (53.33 USD, −154.8). Bullische Divergenz. Seit Mitte Oktober läuft sie seitwärts (−131 bis −138).",
"ind": [
 ["Kurs vs. EMA 50","56.23 &lt; 57.46","56.23 &lt; 60.06","Knapp unter der Tageslinie, deutlich unter der Wochenlinie."],
 ["Kurs vs. EMA 200","56.23 &lt; 60.06","56.23 &lt; 59.65","Unter der langfristigen Linie auf beiden Zeitebenen."],
 ["EMA 50 vs. EMA 200","50 unter 200 (Todeskreuz am 18.9.2026)","50 noch knapp über 200 (60.06 zu 59.65), Abstand schrumpft","Tag im Abwärtstrend, Woche kippt bald."],
 ["RSI (14)","49.5","38.8","Tag neutral nach Überverkauf (Tiefst 12 am 1.10.), Woche schwach."],
 ["A/D","bullische Divergenz am Tief, jetzt seitwärts","steigt seit Oktober mit dem Kurs","Verkaufsdruck hat nachgelassen."],
 ["Volumen","Ø 20 Tage 8.14 Mio. vs. Ø 100 Tage 6.73 Mio. Aktien","Mehr Handel als üblich, typisch nach einem starken Fall."]
],
"smc": "Im Wochenchart pendelte die Aktie 2026 zwischen 59.48 und 67.94 USD. Die Hochs 67.94 (23.2.), 65.35 (20.4.) und 67.15 USD (13.7.) und die Tiefs 59.85 (23.3.) und 59.48 USD (2.6.) bildeten eine Seitwärtsspanne. Im September brach der Kurs unter die Tiefs (Bruch der Struktur nach unten) und fiel bis 53.15 USD (8.10.). Seither im Tageschart erste höhere Hochs und Tiefs: Tief 53.15, Hoch 56.78 (15.10.), höheres Tief 55.28 (21.10.), höheres Hoch 57.42 USD (26.10.). Der Kurs liegt in der unteren Hälfte (Discount) der Spanne 53 bis 68 USD. Ein klarer Change of Character wäre ein Tagesschluss über 57.50 USD und danach über 60 USD (alle EMAs).",
"zones": [
 ["r","61.10–63.50 USD","Widerstand: Tiefs vom 15.5. und 10.8. (61.11, 61.27), Hoch vom 20.8. (63.54 USD)."],
 ["r","59.50–60.10 USD","Widerstand: Tages-EMA 200 (60.06), Wochen-EMA 50 und 200 (60.06, 59.65), Tief vom 2.6. (59.48 USD)."],
 ["t","57.50 USD","<b>Trigger:</b> Tagesschluss über 57.50 USD (Hoch vom 26.10. und Tages-EMA 50), besser mit steigender Tages-A/D."],
 ["s","53.15–54.40 USD","<b>Kaufzone 1:</b> Tief vom 8.10.2026 (53.15) und Wochentiefs von Februar und Mai 2025 (53.30, 54.38 USD)."],
 ["s","50.70–51.60 USD","<b>Kaufzone 2:</b> Wochentiefs vom Januar (51.60) und April 2025 (50.71 USD)."],
 ["r","52.80 USD","Abbruch: Wochenschluss unter 52.80 USD, also unter dem Tief vom Oktober."]
],
"smart": [
 "<b>Rückkäufe:</b> Keine. Realty Income gibt laufend neue Aktien aus, um Gebäude zu kaufen: 934.0 Mio. Aktien Ende 2025, 946.2 Mio. am 30.6.2026 (+1.3 % in einem Halbjahr). Das ist bei REITs normal, verwässert aber deinen Anteil.",
 "<b>Insider:</b> Keine Käufe in den letzten 12 Monaten. Ein Verkauf: Rechtschefin Michelle Bushore, 7'400 Aktien zu 62.42 USD am 2.4.2026 (rund 0.46 Mio. USD). Insider halten nur rund 0.1 % der Aktien.",
 "<b>Grosse Investoren (13F):</b> Gemischt. Im 2. Quartal 2026 stockten State Street (+3.4 %) und Citadel (+50 %, kleine Position) auf, Envestnet, Allianz und Neuberger Berman reduzierten um 5 bis 8 %.",
 "<b>Analysten:</b> Mehrheitlich Halten (25 Analysten), Kursziel im Schnitt 64.63 USD (StockAnalysis, 26.10.2026). Höchste Ziele 72 USD (Bank of America, UBS). Scotiabank stufte im September ab (Ziel 58 USD)."
],
"seasnote": SEAS + "Lange Datenreihe seit 1994. Die nächsten Monate sind historisch gut: November (+0.6 %, 62 %), Dezember (+1.3 %, 62 %) und Januar (+2.5 %, 72 %). Schwach sind Mai (44 %) und Oktober (45 %).",
"T": [
 ["Trend Woche (EMA 50/200)","Kurs unter beiden, EMA 50 nur noch knapp über EMA 200",5,20],
 ["Trend Tag (EMA 50/200)","Kurs unter beiden, Todeskreuz am 18.9., Kurs aber nur 2 % unter EMA 50",2,10],
 ["Struktur (SMC)","Bruch nach unten im September, seit dem Tief erste höhere Hochs und Tiefs im Tageschart, Kurs im Discount",8,20],
 ["RSI Tag/Woche","Tag: bullische Divergenz (Tief 8.10. bei RSI 31 statt 12), Woche dreht aus 29 nach oben",12,15],
 ["A/D Tag/Woche","Tag: bullische Divergenz am Tief. Woche: fiel mit dem Kurs, steigt jetzt wieder",11,20],
 ["Smart Money","Start 3, keine Insider-Käufe, kein Rückkauf, ein Insider-Verkauf (nicht gehäuft)",3,10],
 ["Saisonalität","November bis Januar überwiegend positiv (62 bis 72 %)",5,5]
],
"pro": [
 "Sehr breit gestreut: 15'588 Gebäude, 1'798 Mieter, 98.8 % vermietet, Verträge laufen im Schnitt noch 8.6 Jahre.",
 "Monatliche Dividende, seit 1994 136 Mal erhöht, mit rund 73 % des AFFO gut gedeckt.",
 "Prognose 2026 im August angehoben: AFFO 4.44 bis 4.45 USD, Kaufvolumen 10 Mrd. USD.",
 "Kurs/AFFO 12.8 statt üblich rund 15, Dividendenrendite 5.8 %.",
 "Am Tief vom 8.10. zeigen RSI und Tages-A/D eine bullische Divergenz."
],
"con": [
 "Hohe Zinsen: US-Staatsanleihen rentieren um 5 %, das verteuert Schulden und macht Anleihen zur Konkurrenz.",
 "Hohe Schulden (5.4-mal EBITDAre), Zinskosten steigen (312 statt 284 Mio. USD im Quartal).",
 "Wenig Wachstum pro Aktie (rund 3 bis 4 % pro Jahr), weil laufend neue Aktien ausgegeben werden.",
 "Rund zwei Drittel der Miete kommt von Mietern ohne gutes Bonitätsrating (Investment Grade), Ausfälle wären möglich.",
 "Chart: Abwärtstrend im Tag, Kurs unter allen Durchschnittslinien. Dividende kommt aus den USA (Quellensteuer)."
],
"todo": [
 ["t","Beobachten","Alarm bei 57.50 USD (Trigger) und 54.40 USD (oberes Ende Kaufzone 1)."],
 ["s","Timing grün","Tagesschluss über 57.50 USD, danach Wochenschluss über 60.10 USD (Wochen-EMAs) mit steigender A/D. Fundamental: Am 2.11. AFFO-Prognose 2026 bestätigt (4.44 bis 4.45 USD) und Vermietungsquote über 98.5 %. Hilfreich wären sinkende Zinsen."],
 ["r","Abbruch","Wochenschluss unter 52.80 USD."],
 ["","Nächste Zahlen","2. November 2026 nach US-Börsenschluss (3. Quartal, bestätigt), Telefonkonferenz 17 Uhr New York (23 Uhr Schweizer Zeit). Dazu die Prognose für 2027, voraussichtlich mit den Jahreszahlen im Februar 2027."]
],
"bands": [{"from":61.1,"to":63.5,"type":"res"},{"from":59.5,"to":60.1,"type":"res"},{"from":53.15,"to":54.4,"type":"sup"},{"from":50.7,"to":51.6,"type":"sup"}],
"refs": [{"v":57.5,"label":"Trigger 57.50"}],
"sources": L("https://stockanalysis.com/stocks/o/financials/income-statement/","StockAnalysis.com") + " (Stand 26.10.2026), " + L("https://www.sec.gov/Archives/edgar/data/0000726728/000072672826000044/o-991q22026.htm","Realty Income Zahlen 2. Quartal 2026") + ", " + L("https://www.sec.gov/Archives/edgar/data/0000726728/000072672826000028/o-991q12026.htm","Zahlen 1. Quartal 2026") + ", " + L("https://www.sec.gov/Archives/edgar/data/726728/000072672826000009/o-991q42025.htm","Jahreszahlen 2025") + ", " + L("https://www.suredividend.com/wp-content/uploads/2026/08/O-2026-08-11.pdf","Sure Dividend (AFFO-Historie, 11.8.2026)") + ", " + L("https://www.benzinga.com/markets/earnings/26/09/62012377/realty-income-stock-tumbles-as-dividend-giant-hits-rough-patch","Benzinga (27.9.2026)") + ", " + L("https://finviz.com/news/389807/136th-common-stock-monthly-dividend-increase-declared-by-realty-income","Dividendenerhöhung (8.9.2026)") + ", " + L("https://finviz.com/news/397989/realty-income-announces-third-quarter-2026-earnings-release-date","Termin 3. Quartal") + ", " + L("https://www.marketbeat.com/stocks/NYSE/O/insider-trades","Insider (MarketBeat)") + ". Branchenvergleich der App: Note 2.0 von 5, fairer Wert rund 11 % über dem Kurs (63.30 USD), Unsicherheit mittel."
}
if __name__ == "__main__":
    json.dump(c, open(os.path.join(P, "config", "O.json"), "w"), ensure_ascii=False, indent=1)
    print("ok", sum(r[2] for r in c["Q"]), sum(r[2] for r in c["T"]))
