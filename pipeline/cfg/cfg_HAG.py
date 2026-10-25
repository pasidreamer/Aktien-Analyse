import json, os, sys
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, P)
from helpers import L, ADW, RSIW, SEAS
c = {
"ticker": "HAG", "name": "Hensoldt", "datum": "23.10.2026", "waehrung": "EUR", "land": "Deutschland",
"meta": "Hensoldt AG · Xetra: HAG · Rüstungselektronik: Radare, Optronik (Zielfernrohre, Periskope), Elektronische Kampfführung · Taufkirchen bei München, Deutschland",
"price": "84.02 €",
"pricemeta": "Schluss 23.10.2026 · 52 Wochen: 63.18 – 99.70 € · Allzeithoch 117.70 € am 6.10.2025",
"verdict": "Hensoldt baut die «Augen und Ohren» von Panzern, Flugzeugen und Schiffen: Radare, Zielgeräte und Sensoren. Das Geschäft läuft stark: Auftragsbestand Rekord 10.4 Mrd. € (fast 4 Jahresumsätze), Umsatz im 1. Halbjahr 2026 +24 %, Ziel 2030 rund 6 Mrd. € Umsatz. Aber die Aktie ist teuer (KGV 82) und die Firma verdient nach allen Kosten wenig: operative Marge nur 9 %, Kapitalrendite 8 %. Qualität gelb (51), Timing hellgrün (61). Der Kurs liegt über allen Durchschnittslinien und machte am 16.10. ein neues Hoch im Tageschart. Die Käufer-Spur (A/D) zieht aber nicht mit.",
"about": "Hensoldt entwickelt und baut Sensoren für Armeen: Radare zur Luftraumüberwachung (TRML-4D, im Einsatz in der Ukraine), das Radar im Eurofighter, Aufklärungstechnik für Flugzeuge (PEGASUS), Optronik wie Zielfernrohre und Periskope für Panzer (Puma, Leopard, Boxer) und Systeme zur Störung feindlicher Elektronik. Seit dem Kauf von ESG 2024 gehört auch Software und Wartung dazu. Die Firma ist 2017 aus Airbus abgespalten worden und seit 2020 an der Börse. Grösste Aktionäre sind der deutsche Staat (25.1 % über die KfW) und der italienische Rüstungskonzern Leonardo (22.8 %). Kunden sind vor allem Deutschland und andere NATO-Länder.",
"why": "2025 stieg die Aktie um über 150 % und erreichte am 6.10.2025 das Allzeithoch von 117.70 €. Am Kapitalmarkttag vom 11.11.2025 enttäuschten die Mittelfrist-Ziele (Aktie −8 %), danach drückte der US-Friedensplan für die Ukraine: Ende November lag der Kurs bei 69.90 €. Im Januar 2026 ging es wieder auf über 92 €. Am 29.6.2026 fiel die Aktie auf rund 66 €, weil Anleger auf grosse Aufträge warteten und der Bund am 30.6. die Fregatte F126 strich (Hensoldt hatte dafür Verträge über mehr als 200 Mio. €). Am 16.7. ging ein Sensor-Auftrag für die Ersatz-Fregatten an Saab. Die Halbjahreszahlen am 31.7. waren stark (Auftragseingang verdoppelt auf 2.8 Mrd. €), die Prognose wurde aber nur bestätigt (Aktie −5 %). Mitte August folgte das Hoch bei rund 96 €, Ende September ein Tief bei 74 €. Seit dem 9.10. stieg der Kurs von 74.64 auf 84.02 €, unter anderem nach einer Absichtserklärung der Ukraine für weitere Radare (4.10.) und einer Hochstufung durch Jefferies.",
"kpis": [
 ["g","Umsatzwachstum","+14.7 %","Letzte 12 Monate. Im 1. Halbjahr 2026 +24 %, aus eigener Kraft im 1. Quartal +15 %. Für 2026 erwartet Hensoldt rund 2.75 Mrd. € (+12 %)."],
 ["r","Operative Marge","9.3 %","Von 100 € Umsatz bleiben 9.30 € Betriebsgewinn nach allen Kosten. Seit 2021 seitwärts zwischen 8 und 10 %. Hensoldt selbst nennt die bereinigte Marge vor Abschreibungen: 18.4 % (2025), Ziel 2030 über 20 %."],
 ["w","Gewinn pro Aktie (EPS)","1.03 €","Letzte 12 Monate. Schwankt stark: 0.60 € (2021), 0.53 € (2023), 0.77 € (2025). Zinsen und Abschreibungen auf Zukäufe fressen viel Gewinn."],
 ["r","ROIC","8.2 %","Auf 100 € investiertes Kapital nur rund 8 € Gewinn. Tief und seit 2024 (14.2 %) gesunken, weil der Kauf von ESG viel Kapital gebunden hat."],
 ["g","Free Cashflow","567 Mio. €","Letzte 12 Monate nach StockAnalysis, 2021 waren es 299 Mio. €. Hensoldt rechnet strenger (bereinigt): 347 Mio. € für 2025, nach 249 Mio. € (2024)."],
 ["w","Nettoschulden","1.1 Mrd. €","Mitte 2026, mit Leasing. Das sind rund 2.3 bereinigte Jahresgewinne vor Abschreibungen. Hensoldt rechnet enger und meldet 1.6 (Ende 2025), Ziel 2026 rund 1.5."],
 ["r","KGV","82","Du zahlst rund 82 Jahresgewinne. Eigener Schnitt 2021 bis 2025 rund 47. Also rund 75 % teurer als üblich. Auf die erwarteten Gewinne für 2026 gerechnet rund 38."],
 ["w","Dividende","0.7 %","0.55 € pro Aktie, einmal im Jahr (bezahlt am 27.5.2026). Seit dem Börsengang jedes Jahr erhöht (2021: 0.25 €). Hensoldt zahlt 30 bis 40 % des bereinigten Gewinns aus."]
],
"revtitle": "Umsatz pro Quartal (Mio. €)", "revunit": "Mio. €", "epsunit": "€",
"revnote": "Alle Quartale über dem Vorjahr, zuletzt +26 % und +22 %. Das 4. Quartal ist immer das stärkste, weil viele Lieferungen zum Jahresende abgerechnet werden. Quartale aus den Halbjahres- und 9-Monats-Zahlen selbst gerechnet.",
"marginnote": "Nach allen Kosten (EBIT) seit 2021 stabil bei 8 bis 10 %. Die von Hensoldt gezeigte bereinigte Marge vor Abschreibungen liegt bei rund 18 %.",
"finnote": "<b>Hinweis:</b> Zahlen nach StockAnalysis. Der Free Cashflow dort ist höher als Hensoldts eigener «bereinigter Free Cashflow» (2025: 347 statt 450 Mio. €). Das KGV-Mittel ist über 2021 bis 2025 gerechnet (20.9, 29.8, 50.3, 36.9, 95.3) und wird durch 2025 stark nach oben gezogen. Der Mittelwert ohne 2025 wäre 34.5.",
"FIN": [["2021",1474,"+22.1 %","8.6 %",0.60,299,"10.1 %","20.9"],["2022",1707,"+15.8 %","9.7 %",0.75,244,"11.0 %","29.8"],["2023",1847,"+8.2 %","9.0 %",0.53,267,"10.9 %","50.3"],["2024",2240,"+21.3 %","8.3 %",0.93,311,"14.2 %","36.9"],["2025",2455,"+9.6 %","9.0 %",0.77,450,"9.6 %","95.3"],["Letzte 12 Mt.",2678,"+14.7 %","9.3 %",1.03,567,"8.2 %","81.6"]],
"QREV": [["Q3 24",528],["Q4 24",863],["Q1 25",395],["Q2 25",549],["Q3 25",592],["Q4 25",919],["Q1 26",496],["Q2 26",671]],
"revdec": 0,
"MARGIN": [["2021",8.6],["2022",9.7],["2023",9.0],["2024",8.3],["2025",9.0],["12 Mt.",9.3]],
"Q": [
 ["Umsatztrend","4 von 4 Quartalen über Vorjahr, Tempo steigt von +6 bis 12 % auf +22 bis 26 %",14,15],
 ["Wachstumstempo","Aus eigener Kraft rund 12 bis 15 %",8,10],
 ["Operative Marge","9.3 % (3 Pkt.), seit 5 Jahren stabil (3 Pkt.)",6,15],
 ["Gewinnwachstum (EPS)","Schwankend: 2022 bis 2025 kaum Wachstum, letzte 12 Monate +34 % zu 2025",5,10],
 ["Free Cashflow","Immer positiv, in 4 der letzten 5 Perioden gestiegen",10,10],
 ["ROIC","8.2 %, seit 2024 gesunken",1,15],
 ["Schulden","Firma: 1.5 bis 1.6, mit Leasing selbst gerechnet 2.3",6,10],
 ["Bewertung vs. eigene Historie","KGV 82 statt Ø 47 (2021–2025), rund 75 % teurer",1,15]
],
"adwnote": ADW + "Die Wochen-A/D fällt seit dem Frühling: Ende Mai stand sie bei 88 € Kurs bei +0.2, Mitte August bei 87 € bei −2.1, heute bei 84 € bei −3.8. Der Kurs hält sich, aber die Wochen schliessen eher schwach: leichte Verteilung.",
"rsiwnote": RSIW + "Im Juni bei 40, im August bei 62, heute 53: neutral, ohne Signal.",
"addnote": "Leicht negativ. Beim Tief vom 8.10. (73.70 €) lag die Tages-A/D bei 7.3, tiefer als beim Tief vom 15.9. (8.4). Mit dem Anstieg auf 84 € kam sie nur auf 8.2 zurück. Ende August stand sie bei 85.70 € Kurs bei 9.1. Der Anstieg kommt mit wenig Kaufdruck.",
"ind": [
 ["Kurs vs. EMA 50","84.0 &gt; 81.2","84.0 &gt; 79.8","Über der mittelfristigen Linie, auf beiden Zeitebenen."],
 ["Kurs vs. EMA 200","84.0 &gt; 80.3","84.0 &gt; 58.7","Über der langfristigen Linie, auf beiden Zeitebenen."],
 ["EMA 50 vs. EMA 200","50 über 200 (seit 16.10.2026)","50 über 200 (seit November 2023)","Woche klar aufwärts, Tag frisch gekreuzt, die Linien liegen aber eng beieinander."],
 ["RSI (14)","56.1","52.6","Tag aus 35 (Ende September) nach oben gedreht, Woche neutral."],
 ["A/D","tiefer als bei gleichem Kurs im August","fällt seit Mai","Kaufdruck fehlt auf beiden Zeitebenen."],
 ["Volumen","Ø 20 Tage 0.23 Mio. vs. Ø 100 Tage 0.28 Mio. Aktien","Weniger Handel als im Sommer."]
],
"smc": "Nach dem Allzeithoch von 117.70 € (Oktober 2025) fiel Hensoldt bis 64.80 € (Dezember 2025). Seither bewegt sich die Aktie in einer breiten Seitwärtsspanne zwischen rund 63 und 97 €: Hochs bei 96.70 € (Januar), 91.72 € (Mai) und 96.70 € (August), Tiefs bei 66.20 € (März), 63.18 € (Juni) und 73.70 € (Oktober). Das Oktober-Tief liegt klar über dem Juni-Tief: ein höheres Tief im Wochenchart. Im Tageschart machte der Kurs von August bis Oktober tiefere Hochs (96.70 → 90.24 → 85.04 €). Am 16.10. schloss er mit 87.86 € über dem Hoch vom 6.10. (85.04 €): ein Change of Character nach oben. Der Kurs liegt jetzt in der oberen Hälfte der Spanne, also eher im teuren Bereich.",
"zones": [
 ["r","95–97 €","Widerstand: Hochs vom Januar und August (96.70 €). Oberkante der Seitwärtsspanne."],
 ["r","89–90.5 €","Widerstand: Hoch vom 16.10. (89.02 €) und vom 27.8. (90.24 €)."],
 ["t","90.3 €","<b>Trigger:</b> Tagesschluss über dem Hoch vom 27.8. Dann wäre das tiefere Hoch vom Spätsommer überwunden."],
 ["s","77–80.5 €","<b>Kaufzone 1:</b> Tages-EMA 200 (80.30 €), Wochen-EMA 50 (79.80 €) und Bodenbildung von Mitte September (76 bis 79 €)."],
 ["s","69.5–74 €","<b>Kaufzone 2:</b> Tiefs vom 8.10. (73.70 €), 17.7. (71 €) und 12.5. (69.48 €)."],
 ["r","69 €","Abbruch: Wochenschluss unter dem Mai-Tief (69.48 €). Dann droht ein Rückfall Richtung Juni-Tief (63 €)."]
],
"smart": [
 "<b>Insider-Käufe:</b> CEO Oliver Dörre kaufte am 22./23.6.2026 rund 2'500 Aktien zu 67.98 und 69.50 € (rund 172'000 €), Vorständin Inka Tews rund 300 Aktien (rund 20'000 €), nahe am Jahrestief. Quelle sind Medienberichte, die Originalmeldungen sind nicht geprüft.",
 "<b>Insider-Verkauf:</b> Reiner Winkler verkaufte am 18.8.2026 10'000 Aktien zu 94.71 € (rund 947'000 €), nahe am Hoch.",
 "<b>Grossaktionäre:</b> Bund (KfW) 25.1 %, Leonardo 22.8 % (am 21.7.2026 bestätigt, kein Verkauf). BlackRock hielt im Februar rund 5 % inklusive Instrumente, im August meldete es die Schwelle von 3 %. Keine Rückkäufe.",
 "<b>Analysten:</b> 16 Analysten, Mehrheit «Kaufen», Kursziel im Schnitt 92 € (StockAnalysis). Spanne 62 € (mwb, Verkaufen) bis 105 € (Deutsche Bank). Jefferies stufte Anfang Oktober auf Kaufen hoch (98 €), Goldman Sachs Neutral (85 €)."
],
"seasnote": SEAS + "Nur 6 Jahre Daten (seit 2020), darum wenig aussagekräftig. November schwach (−2.2 %, 33 % positiv), Dezember gemischt (+2.3 %, 50 %), Januar stark (+9.9 %, 83 %).",
"T": [
 ["Trend Woche (EMA 50/200)","Kurs über beiden, EMA 50 klar über EMA 200",18,20],
 ["Trend Tag (EMA 50/200)","Kurs über beiden, Golden Cross am 16.10., Linien noch flach",8,10],
 ["Struktur (SMC)","Seitwärtsspanne mit höherem Tief (Woche), CHoCH im Tageschart am 16.10., Kurs eher im teuren Teil",12,20],
 ["RSI Tag/Woche","Tag aus 35 nach oben gedreht im intakten Wochentrend, keine Divergenz",11,15],
 ["A/D Tag/Woche","Beide fallen, obwohl der Kurs sich hält: leichte Verteilung",3,20],
 ["Smart Money","Start 3, Vorstand kaufte im Juni +4, Verkauf von Winkler im August −1, kein Rückkauf",6,10],
 ["Saisonalität","November schwach, Januar stark, nur 6 Jahre Daten",3,5]
],
"pro": [
 "Rekord-Auftragsbestand 10.4 Mrd. € und Auftragseingang im 1. Halbjahr verdoppelt (Book-to-Bill 2.4).",
 "Das Wachstum beschleunigt sich: +26 % und +22 % in den letzten zwei Quartalen.",
 "Wichtige Systeme sind Standard: Eurofighter-Radar, TRML-4D (im Einsatz in der Ukraine), Optik für Puma und Boxer.",
 "Ab 2027 liefert ein neues Radarwerk, die Kapazität steigt auf mehr als das Dreifache von 2021.",
 "Starke Ankeraktionäre (Bund, Leonardo) und Insider-Käufe am Juni-Tief."
],
"con": [
 "Sehr teuer: KGV 82, auf die Gewinne 2026 rund 38. Viel Erfolg ist schon im Kurs.",
 "Nach allen Kosten verdient Hensoldt wenig: 9 % Marge, 8 % Kapitalrendite.",
 "Der Gewinn hängt stark am 4. Quartal, das 1. Halbjahr bringt nur 12 % bereinigte Marge.",
 "Rückschläge bei Schiffen (F126 gestrichen, MEKO-Sensoren an Saab) und rund 40 % Abhängigkeit von Landfahrzeugen.",
 "Die A/D-Linie fällt: Der jüngste Anstieg hat wenig Kaufdruck."
],
"todo": [
 ["t","Beobachten","Alarm bei 90.30 € (Trigger) und 80.50 € (oberes Ende Kaufzone 1)."],
 ["s","Timing grün","Tagesschluss über 90.30 € mit wieder steigender A/D. Oder ein Rücksetzer in 77 bis 80.50 €, der über der Tages-EMA 200 dreht. Fundamental: Q3-Zahlen am 5.11. (Prognose erhöht?) und Investorentag am 10.11. (höhere Ziele 2030?)."],
 ["r","Abbruch","Wochenschluss unter 69 €. Dann ist das Juni-Tief (63 €) wieder im Spiel."],
 ["","Nächste Zahlen","9 Monate 2026 am 5. November 2026, Investorentag am 10. November 2026. Erwartet (mwb): Umsatz rund 695 Mio. € im 3. Quartal (+17 %)."]
],
"bands": [{"from":95,"to":97,"type":"res"},{"from":89,"to":90.5,"type":"res"},{"from":77,"to":80.5,"type":"sup"},{"from":69.5,"to":74,"type":"sup"}],
"refs": [{"v":90.3,"label":"Trigger 90.3"}],
"sources": L("https://stockanalysis.com/quote/etr/HAG/financials/income-statement/","StockAnalysis.com") + " (Stand 25.10.2026), " + L("https://www.hensoldt.net/news/hensoldt-doubles-order-intake-in-the-first-half-of-2026-%E2%80%93-revenue-and-earnings-rise-significantly","Hensoldt H1 2026") + ", " + L("https://www.hensoldt.net/news/hensoldt-raises-adjusted-free-cash-flow-guidance-for-2026-and-confirms-net-leverage-target","Hensoldt Cashflow-Prognose (1.6.2026)") + ", " + L("https://www.hensoldt.net/news/capital-markets-day-hensoldt-makes-significant-progress-in-capacity-expansion-and-software-defined-defence","Kapitalmarkttag 2025") + ", " + L("https://investors.hensoldt.net/share","Hensoldt Aktie und Konsens") + ", " + L("https://quwa.org/europe/defence-news-eu/hensoldt-doubles-order-intake-as-backlog-passes-e10-billion-but-middle-east-business-stays-marginal/","Quwa zu H1 2026") + ", " + L("https://esut.de/2026/10/meldungen/75661/mehr-hensoldt-weitbereichsradare-fuer-die-ukrainische-luftraumueberwachung/","ESUT: Ukraine-Radare (Oktober 2026)") + ", " + L("https://stockanalysis.com/quote/etr/HAG/dividend/","Dividende (StockAnalysis)") + ". Branchenvergleich App: Note 2.2 von 5, fairer Wert nach Modellen deutlich unter dem Kurs, Unsicherheit sehr hoch."
}
if __name__ == "__main__":
    json.dump(c, open(os.path.join(P, "config", "HAG.json"), "w"), ensure_ascii=False, indent=1)
    print("ok", sum(r[2] for r in c["Q"]), sum(r[2] for r in c["T"]))
