import json, os, sys
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, P)
from helpers import L, ADW, RSIW, SEAS
c = {
"ticker": "NOVN", "name": "Novartis", "datum": "22.10.2026", "waehrung": "CHF", "land": "Schweiz",
"meta": "Novartis AG · SIX Swiss Exchange: NOVN, in New York als ADR: NVS · Medikamente (Kisqali, Cosentyx, Kesimpta, Entresto, Pluvicto) · Basel, Schweiz",
"price": "128.88 CHF",
"pricemeta": "Schluss 22.10.2026 · 52 Wochen: rund 97 – 132.68 CHF · Allzeithoch 132.68 CHF (Tageshoch 3.9.2026)",
"verdict": "Novartis steckt 2026 in einem Patent-Loch: Entresto (2025 noch 7.7 Mrd. USD Umsatz) hat in den USA Nachahmer bekommen und verliert die Hälfte. Darum wächst der Umsatz kaum (ohne Währungen: 1. Quartal −5 %, 2. Quartal +1 %) und der Kerngewinn sinkt 2026 leicht. Neue Mittel wachsen aber stark: Kisqali +44 %, Scemblix +89 %, Pluvicto +43 % (2. Quartal). Ab 2027 erwartet Novartis wieder Gewinnwachstum. Die Aktie steht trotzdem fast am Allzeithoch und ist nicht mehr günstig (KGV 24, auf Kerngewinn 18). Qualität gelb (51), Timing hellgrün (62), aber der Kurs ist weit weg von den Kaufzonen. Nächste Zahlen am 27.10.2026. Keine Anlageberatung.",
"about": "Novartis aus Basel stellt nur noch neue, patentgeschützte Medikamente her. Die Generika-Sparte Sandoz wurde im Oktober 2023 abgespalten. Vier Schwerpunkte: Herz und Stoffwechsel (Entresto, Leqvio), Immunologie (Cosentyx, Rhapsido), Nervensystem (Kesimpta, Zolgensma) und Krebs (Kisqali, Pluvicto, Scemblix). Die grössten Medikamente 2025: Entresto 7.7 Mrd. USD, Cosentyx 6.7 Mrd., Kisqali 4.8 Mrd., Kesimpta 4.4 Mrd. Die USA bringen rund 40 % des Umsatzes, Europa rund 31 %, Wachstumsmärkte rund 28 % (China 2.5 Mrd. USD im 1. Halbjahr 2026). Novartis berichtet in US-Dollar, die Aktie wird in Franken gehandelt. Im Februar 2026 kaufte Novartis die US-Firma Avidity für rund 12 Mrd. USD (Medikamente für seltene Muskelkrankheiten). Chef ist Vas Narasimhan.",
"why": "Die Aktie stieg von 82.96 CHF (9.4.2025, Zollschock) auf ein Allzeithoch von 132.68 CHF (3.9.2026). Treiber: starke neue Medikamente, Rückkäufe von 8.9 Mrd. USD im Jahr 2025 und ein Abkommen mit der US-Regierung (19.12.2025): Novartis senkt einige US-Preise, investiert 23 Mrd. USD in den USA und erwartet dafür 3 Jahre ohne Pharma-Zölle. Am 28.4.2026 enttäuschten die Zahlen zum 1. Quartal (Kerngewinn pro Aktie −13 %), die Aktie fiel auf rund 110 CHF. Das 2. Quartal (21.7.) war 12 % besser als erwartet. Im September kamen zwei Rückschläge: Pelacarsen (Herz, 4.9.) und Del-desiran aus dem Avidity-Kauf (8.9.) verfehlten ihr Studienziel. Das ADR fiel an einem Tag um 13.9 %, der Kurs in Franken bis 110.30 CHF. Positiv: Remibrutinib war am 1.9. in zwei grossen Studien gegen Multiple Sklerose erfolgreich. Seither hat sich die Aktie fast ganz erholt.",
"kpis": [
 ["w","Umsatzwachstum","+2.7 %","Letzte 12 Monate in Dollar. Ohne Währungseffekte etwa 0 %: 1. Quartal 2026 −5 %, 2. Quartal +1 %. Grund: Nachahmer für Entresto, Promacta, Tasigna kosten 2026 rund 4 Mrd. USD Umsatz."],
 ["g","Kern-Marge","38.8 %","Von 100 Dollar Umsatz bleiben 38.80 Dollar Kern-Betriebsgewinn (ohne Abschreibungen auf Zukäufe, letzte 12 Monate). Ausgewiesen: 32.8 %. Sehr hoch. 2025: 40.1 %."],
 ["w","Kerngewinn pro Aktie","8.68 USD","Letzte 12 Monate (eigene Rechnung), 2025: 8.98 USD. 2026 leicht sinkend erwartet, ab 2027 wieder Wachstum laut Novartis. Ausgewiesen: 6.61 USD."],
 ["g","ROIC","18.8 %","Auf 100 Dollar investiertes Kapital rund 19 Dollar Gewinn. Gut. 2025 waren es 24.5 %, gesunken durch den Avidity-Kauf."],
 ["g","Free Cashflow","16.8 Mrd. USD","Letzte 12 Monate. Sehr hoch und seit 2022 (13.3 Mrd.) gestiegen, im 1. Halbjahr 2026 aber −9 %."],
 ["w","Nettoschulden / EBITDA","1.7","Nettoschulden 39.4 Mrd. USD (30.6.2026, nach dem Avidity-Kauf), rund 1.7 Jahresgewinne vor Abschreibungen. Gut tragbar, aber stark gestiegen (Ende 2025: 21.9 Mrd.)."],
 ["r","KGV","24","Du zahlst 24 Jahresgewinne (ausgewiesen). Eigener Schnitt 2021–2025: 17.1. Rund 40 % teurer als üblich. Auf den Kerngewinn rund 18, erwartet 2026 rund 17.7."],
 ["w","Dividende","2.9 %","3.70 CHF pro Aktie, einmal im Jahr (Ex-Tag 10.3.2026, bezahlt am 12.3.2026). 29 Erhöhungen in Folge seit 1996."]
],
"revtitle": "Umsatz pro Quartal (Mrd. USD)", "revunit": "Mrd. USD", "epsunit": "USD",
"margintitle": "Kern-Marge (%)",
"revnote": "Nettoumsatz laut Novartis. 3 der letzten 4 Quartale über dem Vorjahr (Q3 25 +8 %, Q4 25 +1 %, Q1 26 −1 %, Q2 26 +3 %). Q4 24 und Q1 26 sind gerundete Firmenangaben.",
"marginnote": "Kern-Betriebsgewinn pro 100 Dollar Umsatz, wie Novartis ihn meldet. 2021 mit Sandoz, ab 2022 ohne. Von 35 % auf 40 % gestiegen, 2026 wegen der Nachahmer-Medikamente leicht tiefer.",
"finnote": "<b>Hinweis:</b> Umsatz, Marge, EPS, FCF, ROIC und KGV in der Tabelle laut StockAnalysis, ausgewiesen in USD (Umsatz inkl. Lizenzerlöse, darum höher als der Nettoumsatz). EPS 2021 ist durch den Verkauf der Roche-Beteiligung aufgebläht, 2023 durch die Sandoz-Abspaltung (ohne sie 4.13 USD). Darum schwankt das KGV stark. Kerngewinn pro Aktie: 6.47 (2023), 7.81 (2024), 8.98 USD (2025).",
"FIN": [["2021",43974,"−11.9 %","24.9 %",10.63,14005,"13.3 %","8.2"],["2022",43461,"−1.2 %","21.2 %",3.17,13320,"11.1 %","28.0"],["2023",46660,"+7.4 %","21.9 %",7.10,13398,"15.1 %","14.0"],["2024",51722,"+10.9 %","31.6 %",5.87,16253,"23.6 %","16.4"],["2025",56674,"+9.6 %","33.5 %",7.15,17596,"24.5 %","19.0"],["Letzte 12 Mt.",56693,"+2.7 %","32.8 %",6.61,16763,"18.8 %","24.0"]],
"QREV": [["Q3 24",12.82],["Q4 24",13.2],["Q1 25",13.23],["Q2 25",14.05],["Q3 25",13.91],["Q4 25",13.34],["Q1 26",13.1],["Q2 26",14.41]],
"revdec": 1,
"MARGIN": [["2021",32.1],["2022",35.1],["2023",36.0],["2024",38.7],["2025",40.1],["12 Mt.",38.8]],
"Q": [
 ["Umsatztrend","3 von 4 Quartalen über Vorjahr, Tempo zuletzt tief",8,15],
 ["Wachstumstempo","+2.7 % in 12 Monaten, ohne Währungen rund 0 % (Generika)",0,10],
 ["Operative Marge","Kern 38.8 %, ausgewiesen 32.8 % (9 Pkt.), 5 Jahre steigend, 2026 leicht tiefer (5 Pkt.)",14,15],
 ["Gewinnwachstum (EPS)","Kerngewinn 2023–2025 stark gestiegen, 2026 leicht rückläufig erwartet",5,10],
 ["Free Cashflow","Hoch, meist steigend, 1. Halbjahr 2026 aber −9 %",6,10],
 ["ROIC","18.8 % (10 Pkt.), nach Anstieg wieder gesunken (±0)",10,15],
 ["Schulden","Nettoschulden/EBITDA rund 1.7",7,10],
 ["Bewertung vs. eigene Historie","KGV 24 statt Ø 17.1, über 30 % teurer (auf Kerngewinn rund 18)",1,15]
],
"adwnote": ADW + "Positiv: Die Wochen-A/D steigt seit Ende 2024 mit dem Kurs (452 → 573) und steht heute höher als bei den Hochs im Februar (570) und August (568).",
"rsiwnote": RSIW + "Im Februar 2026 bei 81 (überkauft), im September nach den Studien-Rückschlägen bei 42, heute 57: neutral bis stark.",
"addnote": "Warnung: Die Tages-A/D fällt seit Februar (114 → 79), obwohl der Kurs heute fast so hoch steht wie damals. Beim Allzeithoch am 3.9. stand sie bei 93, heute bei 79. Der Anstieg seit dem 5.10. wird von weniger Käufern getragen.",
"ind": [
 ["Kurs vs. EMA 50","128.9 &gt; 121.6","128.9 &gt; 117.5","Über der mittelfristigen Linie, auf beiden Zeitebenen."],
 ["Kurs vs. EMA 200","128.9 &gt; 118.7","128.9 &gt; 101.0","Deutlich über der langfristigen Linie, besonders in der Woche (+28 %)."],
 ["EMA 50 vs. EMA 200","50 über 200 (goldenes Kreuz seit 15.8.2025)","50 über 200 (seit Dezember 2016)","Aufwärtstrend auf beiden Zeitebenen."],
 ["RSI (14)","67.5","57.4","Tag nahe überkauft, Woche neutral."],
 ["A/D","fällt seit Februar","steigt seit Ende 2024","Woche positiv, Tag negativ."],
 ["Volumen","Ø 20 Tage 3.09 Mio. vs. Ø 100 Tage 2.87 Mio. Aktien","Etwas mehr Handel als üblich."]
],
"smc": "Novartis läuft seit Februar 2026 in einer breiten Spanne zwischen rund 108 und 133 CHF. Hochs: 131 CHF (27.2.), 128.92 CHF (2.7.), 131.50 CHF (29.7.) und 132.68 CHF (3.9., Allzeithoch). Tiefs: 113.64 CHF (23.3.), 108.24 CHF (28.4.), 111.48 CHF (3.6.), 121.02 CHF (14.8.) und nach den Studien-Rückschlägen 110.30 CHF (9.9.). Seit diesem Tief steigt der Kurs mit höheren Tiefs (115.94 CHF am 5.10.) und schloss am 15.10. über dem Hoch vom 30.9. (122.54 CHF): ein Break of Structure nach oben im Tageschart. Der Kurs steht jetzt aber im teuren oberen Teil der Spanne, direkt unter dem Allzeithoch. Ein echter Ausbruch wäre ein Wochenschluss über 133 CHF.",
"zones": [
 ["r","131–132.70 CHF","Widerstand: Allzeithochs von Februar, Juli und September."],
 ["t","133 CHF","<b>Trigger:</b> Tagesschluss über 133 CHF (neues Allzeithoch), besser mit steigender Tages-A/D. Oder ein Rücksetzer in Kaufzone 1 mit höherem Tief."],
 ["s","116–121 CHF","<b>Kaufzone 1:</b> Tiefs August (121.02) und Oktober (115.94 CHF), Tages-EMA 200 (118.70 CHF)."],
 ["s","108–111.50 CHF","<b>Kaufzone 2:</b> Tiefs April (108.24), Juni (111.48) und September (110.30 CHF)."],
 ["r","107 CHF","Abbruch: Wochenschluss unter 107 CHF, also unter dem Tief vom April. Dann wäre die Spanne nach unten gebrochen."]
],
"smart": [
 "<b>Rückkäufe:</b> Programm über bis 10 Mrd. USD, davon Ende Juni 2026 noch 5.6 Mrd. offen. 2025 kaufte Novartis Aktien für 8.9 Mrd. USD zurück (rund 3 % des Börsenwerts). Die Aktienzahl sank seit 2021 von 2.24 auf 1.91 Mrd.",
 "<b>Insider:</b> Manager verkauften von Oktober 2025 bis Oktober 2026 rund 271'500 Aktien für rund 31.9 Mio. CHF, vor allem im Februar 2026 (117 bis 124 CHF). Nur ein kleiner Kauf (3'112 Aktien zu 114.20 CHF am 30.1.2026). Manager erhalten Aktien als Lohn und verkaufen oft, das Signal ist trotzdem negativ.",
 "<b>Analysten:</b> 21 Analysten bei cash.ch: 6 Kaufen, 13 Neutral, 2 Verkaufen. Kursziel im Schnitt 125 CHF (Spanne 95 bis 150 CHF), also unter dem Kurs. Morgan Stanley senkte am 6.10. von 135 auf 130 CHF, Goldman Sachs: Verkaufen, Ziel 113 CHF (1.10.)."
],
"seasnote": SEAS + "31 Jahre Daten (seit 1995). Juni (+1.7 %, 69 %), April (+1.3 %, 65 %) und November (+1.9 %, 61 %) sind stark, Januar (−0.8 %, 39 %) und Oktober (+0.1 %, 42 %) schwach. Dezember gemischt (58 %).",
"T": [
 ["Trend Woche (EMA 50/200)","Kurs über beiden, EMA 50 deutlich über 200",19,20],
 ["Trend Tag (EMA 50/200)","Kurs über beiden, EMA 50 über 200",9,10],
 ["Struktur (SMC)","Break of Structure nach oben am 15.10., aber Kurs im teuren Teil der Spanne",12,20],
 ["RSI Tag/Woche","Tag 67.5 (nahe überkauft), Woche 57",6,15],
 ["A/D Tag/Woche","Woche steigt, Tag fällt seit Februar",10,20],
 ["Smart Money","Start 3, grosser Rückkauf (+3), gehäufte Insider-Verkäufe (−3)",3,10],
 ["Saisonalität","November 61 %, Dezember 58 %, Januar 39 % positive Jahre",3,5]
],
"pro": [
 "Starke neue Medikamente: Kisqali +44 %, Kesimpta +32 %, Pluvicto +43 %, Scemblix +89 % (2. Quartal 2026).",
 "Remibrutinib (Rhapsido) war im September in zwei grossen Studien gegen Multiple Sklerose erfolgreich. Analysten sehen bis 9 Mrd. USD Spitzenumsatz.",
 "Sehr hohe Marge (Kern 38.8 %) und Free Cashflow von 16.8 Mrd. USD pro Jahr.",
 "Grosse Rückkäufe und 29 Dividendenerhöhungen in Folge.",
 "Abkommen mit der US-Regierung bringt laut Novartis 3 Jahre ohne Pharma-Zölle."
],
"con": [
 "Patent-Loch: Entresto, Promacta, Tasigna verlieren 2026 zusammen rund 4 Mrd. USD Umsatz, der Kerngewinn sinkt 2026 leicht.",
 "Zwei Studien-Rückschläge im September, darunter das wichtigste Mittel aus dem 12-Mrd.-Kauf von Avidity. Anwälte prüfen Sammelklagen.",
 "Nicht mehr günstig: KGV 24 gegen eigenen Schnitt von 17, Kurs über dem mittleren Kursziel der Analysten.",
 "Druck auf US-Preise (rund 40 % des Umsatzes): Preise drücken das Wachstum um 3 bis 4 Prozentpunkte.",
 "Manager verkauften für rund 32 Mio. CHF Aktien, Tages-A/D fällt."
],
"todo": [
 ["t","Beobachten","Alarm bei 121 CHF (oberes Ende Kaufzone 1) und 133 CHF (Trigger). Am 27.10. auf die Zahlen achten."],
 ["s","Timing grün","Rücksetzer in Kaufzone 1 (116 bis 121 CHF) mit höherem Tief und drehender Tages-A/D, oder Wochenschluss über 133 CHF. Fundamental: Ohne Währungen wieder Umsatzwachstum und Bestätigung der Prognose 2026."],
 ["r","Abbruch","Wochenschluss unter 107 CHF."],
 ["","Nächste Zahlen","27. Oktober 2026 (3. Quartal, bestätigt). Jahreszahlen am 3. Februar 2027."]
],
"bands": [{"from":131,"to":132.7,"type":"res"},{"from":116,"to":121,"type":"sup"},{"from":108,"to":111.5,"type":"sup"}],
"refs": [{"v":133,"label":"Trigger 133"}],
"sources": L("https://stockanalysis.com/stocks/nvs/financials/ratios/","StockAnalysis.com") + " (Stand 22.10.2026), " + L("https://www.sec.gov/Archives/edgar/data/0001114448/000111444826000012/nvs-20260630-99_1.htm","Novartis Zahlen 2. Quartal 2026") + ", " + L("https://www.sec.gov/Archives/edgar/data/1114448/000111444826000007/a260204-99_1.htm","Novartis Jahreszahlen 2025") + ", " + L("https://www.novartis.com/us-en/news/media-releases/novartis-and-us-government-reach-agreement-lowering-drug-prices-us","Abkommen mit der US-Regierung") + ", " + L("https://www.vermoegenszentrum.ch/en/stock-exchange-and-markets/news/novartis-misses-primary-endpoint-myotonic-dystrophy-study","Del-desiran (8.9.2026)") + ", " + L("https://ch.marketscreener.com/kurs/aktie/NOVARTIS-AG-9364983/unternehmen-insider-transaktionen/","Insider (MarketScreener)") + ", " + L("https://www.cash.ch/aktien/novartis-n-1200526","Kursziele (cash.ch)") + ". Branchenvergleich der App: Note 3.3 von 5, fairer Wert rund 5 % über dem Kurs, Unsicherheit hoch."
}
if __name__ == "__main__":
    json.dump(c, open(os.path.join(P, "config", "NOVN.json"), "w"), ensure_ascii=False, indent=1)
    print("ok", sum(r[2] for r in c["Q"]), sum(r[2] for r in c["T"]))
