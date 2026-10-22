import json, os, sys
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, P)
from helpers import L, ADW, RSIW, SEAS
ADWT = ADW.replace("Werte in Mio. Aktien.", "Werte in Tausend Aktien.")
c = {
"ticker": "UHR", "name": "Swatch Group", "datum": "22.10.2026", "waehrung": "CHF", "land": "Schweiz",
"meta": "The Swatch Group AG · SIX Swiss Exchange: UHR (Inhaberaktie), auch UHRN (Namenaktie) · Uhren und Schmuck (Omega, Longines, Tissot, Swatch) · Biel, Schweiz",
"price": "178.60 CHF",
"pricemeta": "Schluss 22.10.2026 · 52 Wochen: 159.80 – 223.10 CHF · Allzeithoch rund 606 CHF im November 2013",
"verdict": "Swatch verkauft wieder mehr Uhren (1. Halbjahr 2026: +8.5 % ohne Währungseffekte, USA +27 %), verdient aber fast nichts: Von 100 Franken Umsatz blieben im 1. Halbjahr nur 1.70 Franken Betriebsgewinn (2023 noch 15). Grund: Swatch behält alle Fabriken und Stellen, obwohl viel weniger verkauft wird. Dazu liegen Uhren für 7.3 Mrd. CHF im Lager, mehr als ein ganzer Jahresumsatz. Stark ist nur die Bilanz: 1.1 Mrd. CHF mehr Geld als Schulden, Börsenwert unter dem Buchwert (0.84). Qualität rot (25), Timing orange (39). Die Mehrheit der Analysten rät zum Verkaufen (Kursziel im Schnitt rund 170 CHF), der Branchenvergleich gibt nur 1.3 von 5 Punkten. Keine Anlageberatung.",
"about": "Swatch ist der grösste Uhrenkonzern der Schweiz mit rund 31'800 Mitarbeitenden. Zum Konzern gehören teure Marken wie Breguet, Blancpain, Harry Winston und Omega, mittlere wie Longines, Rado und Tissot und günstige wie Swatch und Hamilton. Swatch baut fast alle Teile selbst, auch Uhrwerke für andere Marken (ETA). Uhren und Schmuck bringen rund 94 % des Umsatzes, Elektronik (Batterien, Sport-Zeitmessung) rund 6 %. Regionen 2025: übriges Asien rund 25 %, Grosschina 23 %, übriges Europa 22 %, Amerika 21 %, Schweiz 8 %. Es gibt zwei Aktien: die Inhaberaktie UHR (hier analysiert) und die Namenaktie UHRN, die nur ein Fünftel kostet, aber gleich viel Stimmrecht hat. So kontrolliert die Familie Hayek mit rund 26 % des Kapitals 44.5 % der Stimmen. Nayla Hayek ist Präsidentin, ihr Bruder Nick Hayek Chef.",
"why": "Die Aktie stand im November 2013 bei rund 606 CHF und hat seither rund 70 % verloren. 2024 und 2025 brach China ein, früher über 40 % des Umsatzes (Grosschina 2021: 3.08 Mrd. CHF, 2025: 1.46 Mrd. CHF). Der Gewinn fiel von 16.75 CHF pro Aktie (2023) auf 0.06 CHF (2025), die Dividende wurde 2025 von 6.50 auf 4.50 CHF gekürzt. Im April 2025 fiel die Aktie wegen der US-Zölle auf rund 120 CHF (Zoll auf Schweizer Uhren zeitweise 39 %, seit 24.7.2026 12.5 %). Danach Erholung bis 223.10 CHF am 2.6.2026, getragen von der Uhr Royal Pop mit Audemars Piguet (Schlangen vor den Läden im Mai). Am 21.7.2026 kamen schwache Halbjahreszahlen: Betriebsgewinn 52 Mio. CHF statt rund 120 Mio. erwartet. Die Aktie fiel in einer Woche von 203 auf 166.50 CHF. An der Generalversammlung am 12.5.2026 lehnte die Familie Hayek den Aktivisten Steven Wood erneut ab, obwohl 80 % der Inhaberaktionäre für ihn stimmten. Rund 28 % der frei handelbaren Aktien sind leerverkauft (Wetten auf fallende Kurse, Stand Mai 2026).",
"kpis": [
 ["w","Umsatzwachstum","+8.5 %","1. Halbjahr 2026 ohne Währungseffekte. In Franken nur +2.0 %, weil der starke Franken die Auslandsumsätze kleiner macht. Das ganze Jahr 2025: −6.8 % in Franken."],
 ["r","Operative Marge","1.9 %","Von 100 Franken Umsatz bleiben 1.90 Franken Betriebsgewinn (letzte 12 Monate). 2023 waren es 15.1 %. Sehr schwach, weil die Fabriken halb leer laufen."],
 ["r","Gewinn pro Aktie (EPS)","0.18 CHF","Letzte 12 Monate, fast null. 2023 waren es 16.75 CHF. Analysten erwarten für 2027 wieder rund 7 CHF, das ist aber unsicher."],
 ["r","ROIC","0.2 %","Auf 100 Franken investiertes Kapital fast kein Gewinn. 2022 waren es 9.4 %. Sehr schwach."],
 ["w","Free Cashflow","270 Mio. CHF","Letzte 12 Monate. Geld, das nach Investitionen übrig bleibt. Positiv, aber klein: 2023 und 2024 war er negativ (−115 und −170 Mio.)."],
 ["g","Netto-Cash","1.13 Mrd. CHF","Swatch hat mehr Geld als Schulden (30.6.2026). Eigenkapitalquote 87 %. Sehr solide."],
 ["r","KGV erwartet","31.5","Du zahlst 31 erwartete Jahresgewinne. Das heutige KGV (über 1'000) ist wegen des Gewinns von fast null sinnlos. Eigener Schnitt (Median 2021–2025): 18.5. Teuer gemessen am Gewinn, günstig gemessen am Buchwert (0.84)."],
 ["w","Dividende","2.5 %","4.50 CHF pro Inhaberaktie, einmal im Jahr (Ex-Tag 15.5.2026, bezahlt am 19.5.2026). Nicht durch den Gewinn gedeckt (Gewinn 2025: 0.06 CHF pro Aktie). 2025 gekürzt."]
],
"revtitle": "Umsatz pro Halbjahr (Mio. CHF)", "revunit": "Mio. CHF", "epsunit": "CHF",
"revnote": "Swatch meldet nur halbjährlich. In Franken lag nur das 1. Halbjahr 2026 über dem Vorjahr (+2.0 %). Ohne Währungseffekte wuchs Swatch im 2. Halbjahr 2025 um 4.7 % und im 1. Halbjahr 2026 um 8.5 %. Das 2. Halbjahr ist aus Jahr minus 1. Halbjahr berechnet.",
"marginnote": "Betriebsgewinn pro 100 Franken Umsatz. Von 15.5 % (2022) auf 1.9 % gefallen. Swatch hält Fabriken und Stellen, obwohl weniger verkauft wird. Uhren und Schmuck allein (ohne Produktion) hatten im 1. Halbjahr 2026 eine Marge von 9.0 %.",
"finnote": "<b>Hinweis:</b> Das KGV 2025 (2'934) und heute (über 1'000) ist wegen des Gewinns von fast null nicht aussagekräftig. Free Cashflow je nach Quelle leicht anders (MarketScreener: 2024 −216, 2025 +56 Mio. CHF). Zahlen pro Inhaberaktie, Quelle StockAnalysis.",
"FIN": [["2021",7313,"+30.7 %","14.0 %",14.76,1047,"8.5 %","18.5"],["2022",7499,"+2.5 %","15.5 %",15.56,385,"9.4 %","16.2"],["2023",7888,"+5.2 %","15.1 %",16.75,-115,"9.3 %","13.4"],["2024",6735,"−14.6 %","4.5 %",3.73,-170,"1.8 %","43.8"],["2025",6280,"−6.8 %","2.2 %",0.06,98,"0.2 %","2'934"],["Letzte 12 Mt.",6342,"+1.0 %","1.9 %",0.18,270,"0.2 %","1'042"]],
"QREV": [["H1 23",4019],["H2 23",3869],["H1 24",3445],["H2 24",3290],["H1 25",3059],["H2 25",3221],["H1 26",3121]],
"revdec": 0,
"MARGIN": [["2021",14.0],["2022",15.5],["2023",15.1],["2024",4.5],["2025",2.2],["12 Mt.",1.9]],
"Q": [
 ["Umsatztrend","In Franken 1 von 4 Halbjahren höher, ohne Währungen 2 von 4 (mit steigendem Tempo)",4,15],
 ["Wachstumstempo","Ohne Währungseffekte rund +6.5 % in 12 Monaten (2. Halbjahr 2025 +4.7 %, 1. Halbjahr 2026 +8.5 %)",6,10],
 ["Operative Marge","1.9 % (0 Pkt.), seit 2022 stark gefallen (0 Pkt.)",0,15],
 ["Gewinnwachstum (EPS)","Von 16.75 CHF (2023) auf 0.18 CHF eingebrochen",0,10],
 ["Free Cashflow","Positiv (270 Mio. CHF), aber 2023 und 2024 negativ",3,10],
 ["ROIC","0.2 % (2 Pkt.), fallend (−1)",1,15],
 ["Schulden","Netto-Cash 1.13 Mrd. CHF",10,10],
 ["Bewertung vs. eigene Historie","Erw. KGV 31.5 statt Median 18.5, über 30 % teurer (Buchwert-Sicht günstig, KBV 0.84)",1,15]
],
"adwnote": ADWT + "Leicht positiv: Die Wochen-A/D stieg vom Tief im Juni 2025 (−20'212) auf −16'002. Seit März 2026 macht der Kurs höhere Tiefs (161 → 166.50 → 171.25 → 174.70 CHF) und die A/D steigt mit (−17'434 → −15'946).",
"rsiwnote": RSIW + "Im April 2025 bei 28 (überverkauft), im Juni 2026 bei 66, heute 46: neutral.",
"addnote": "Negativ: Die Tages-A/D fällt seit Mitte Juli von rund 1'980 auf 1'112. Beim Tief vom 13.10. (174.70 CHF) stand sie tiefer als beim tieferen Tief vom 16.9. (171.25 CHF). Grosse Anleger kaufen die Erholung nicht mit.",
"ind": [
 ["Kurs vs. EMA 50","178.6 &lt; 183.4","178.6 &lt; 182.7","Unter der mittelfristigen Linie, auf beiden Zeitebenen."],
 ["Kurs vs. EMA 200","178.6 &lt; 183.5","178.6 &lt; 196.3","Unter der langfristigen Linie."],
 ["EMA 50 vs. EMA 200","50 knapp unter 200 (Todeskreuz am 14.10.2026), fast gleich hoch","50 unter 200 (seit September 2023), Abstand schrumpft","Tag ohne Richtung, Woche noch abwärts, aber die EMA 50 steigt seit einem Jahr."],
 ["RSI (14)","44.0","45.9","Neutral, kein Signal."],
 ["A/D","fällt seit Juli","steigt seit Juni 2025","Woche positiv, Tag negativ."],
 ["Volumen","Ø 20 Tage 86'600 vs. Ø 100 Tage 93'000 Aktien","Etwas weniger Handel als üblich."]
],
"smc": "Seit dem Hoch vom 2.6.2026 (223.10 CHF) macht Swatch tiefere Hochs: 212.30 CHF (15.7.), 197.40 CHF (17.8.), 193 CHF (30.9.) und 186 CHF (16.10.). Gleichzeitig steigen die Tiefs: 161 CHF (19.3.), 166.50 CHF (28.7.), 171.25 CHF (16.9.), 174.70 CHF (13.10.). Der Kurs wird also in einem Dreieck zusammengedrückt. Ein Ausbruch nach oben wäre ein Tagesschluss über 186 CHF und danach über 193 CHF. Bricht der Kurs unter 171 CHF, ist die Reihe höherer Tiefs gebrochen. Über dem Kurs liegt die Wochen-EMA 200 bei 196 CHF als Widerstand.",
"zones": [
 ["r","212–223 CHF","Widerstand: Hochs von Juni und Juli 2026."],
 ["r","193–197.40 CHF","Widerstand: Hochs August und September, Wochen-EMA 200 (196.30 CHF)."],
 ["t","186 CHF","<b>Trigger:</b> Tagesschluss über 186 CHF (letztes tieferes Hoch vom 16.10.), besser mit steigender Tages-A/D."],
 ["s","166–171 CHF","<b>Kaufzone 1:</b> Tiefs vom Juli (166.50) und September (171.25 CHF)."],
 ["s","159.80–161 CHF","<b>Kaufzone 2:</b> Tiefs von Dezember 2025 (159.80) und März 2026 (161 CHF), 52-Wochen-Tief."],
 ["r","158 CHF","Abbruch: Wochenschluss unter 158 CHF, also unter dem 52-Wochen-Tief."]
],
"smart": [
 "<b>Familie Hayek:</b> Der Hayek-Pool kaufte 2025 laut Geschäftsbericht rund 193'000 Inhaberaktien und 440'000 Namenaktien dazu (Stimmanteil 44.1 → 44.5 %). Käufe aus den letzten 6 Monaten habe ich nicht gefunden.",
 "<b>Weitere Insider:</b> Eine Führungsperson verkaufte seit Oktober 2025 in 9 kleinen Tranchen Namenaktien für zusammen rund 0.9 Mio. CHF. Kleine Beträge, kein starkes Signal.",
 "<b>Rückkäufe:</b> Keine. 2025 und im 1. Halbjahr 2026 kaufte Swatch keine eigenen Aktien zurück.",
 "<b>Aktivist:</b> Steven Wood (GreenWood Investors) kämpft für bessere Führung, scheiterte aber zweimal an der Familie Hayek. Rund 28 % der frei handelbaren Aktien sind leerverkauft (Mai 2026).",
 "<b>Analysten:</b> 18 Analysten bei cash.ch: 2 Kaufen, 9 Neutral, 7 Verkaufen. Kursziel im Schnitt 169.70 CHF (Spanne 90 bis 225 CHF). Goldman Sachs: Verkaufen, Ziel 174 CHF (5.10.2026). Kepler Cheuvreux: Kaufen, Ziel 225 CHF (August 2026)."
],
"seasnote": SEAS + "28 Jahre Daten (seit 1998). Dezember (+3.0 %, 71 % positive Jahre), Februar (+3.2 %, 68 %) und November (+1.2 %, 61 %) sind stark, August (−3.2 %, 31 %) und Juni (−2.3 %, 29 %) schwach.",
"T": [
 ["Trend Woche (EMA 50/200)","Kurs unter beiden, EMA 50 unter 200, aber Abstand schrumpft (183 zu 196)",4,20],
 ["Trend Tag (EMA 50/200)","Kurs knapp unter beiden, Todeskreuz am 14.10., EMAs flach",2,10],
 ["Struktur (SMC)","Dreieck: tiefere Hochs, aber höhere Tiefs seit März",8,20],
 ["RSI Tag/Woche","Tag 44, Woche 46, kein Signal",7,15],
 ["A/D Tag/Woche","Woche steigt, Tag fällt seit Juli",10,20],
 ["Smart Money","Start 3, keine Rückkäufe, keine neuen Hayek-Käufe gefunden, kleine Verkäufe",3,10],
 ["Saisonalität","November 61 %, Dezember 71 % positive Jahre",5,5]
],
"pro": [
 "Umsatz wächst wieder: ohne Währungen +8.5 % im 1. Halbjahr 2026, USA +27 %, China im Laden +9 %.",
 "Sehr solide Bilanz: 1.13 Mrd. CHF Netto-Cash, Eigenkapitalquote 87 %, Börsenwert unter dem Buchwert.",
 "Grosser Gewinnhebel: Wenn die Fabriken wieder ausgelastet sind, steigt der Gewinn schnell. Nick Hayek nannte 500 bis 600 Mio. CHF Betriebsgewinn als möglich (keine offizielle Prognose).",
 "Royal Pop mit Audemars Piguet: Nachfrage laut Swatch weit über dem Angebot, hohe Marge.",
 "Starke Marken (Omega, Longines, Tissot) und eigene Uhrwerk-Produktion."
],
"con": [
 "Fast kein Gewinn: Marge 1.9 %, Gewinn pro Aktie 0.18 CHF. Die Dividende wird aus der Substanz bezahlt.",
 "Lager von 7.3 Mrd. CHF, mehr als ein Jahresumsatz. Das bindet viel Geld.",
 "Schwache Führung aus Sicht vieler Anleger: Die Familie Hayek kontrolliert mit 26 % Kapital 44.5 % der Stimmen.",
 "Abhängig von China und vom starken Franken. US-Zoll von 12.5 % auf Schweizer Uhren.",
 "Die meisten Analysten raten zum Verkaufen, viele Leerverkäufer. Keine Rückkäufe."
],
"todo": [
 ["t","Beobachten","Alarm bei 186 CHF (Trigger) und 171 CHF (oberes Ende Kaufzone 1). Erst einsteigen, wenn die Marge sichtbar steigt."],
 ["s","Timing grün","Tagesschluss über 186 CHF, danach Wochenschluss über 197 CHF (Wochen-EMA 200), mit drehender Tages-A/D. Fundamental: Betriebsmarge im 2. Halbjahr 2026 klar über 5 %."],
 ["r","Abbruch","Wochenschluss unter 158 CHF."],
 ["","Nächste Zahlen","Jahresumsatz 2026 voraussichtlich Ende Januar 2027 (Datum noch nicht bestätigt), Geschäftsbericht im März 2027. Monatlich: Uhrenexporte des Uhrenverbands."]
],
"bands": [{"from":212,"to":223,"type":"res"},{"from":193,"to":197.4,"type":"res"},{"from":166,"to":171,"type":"sup"},{"from":159.8,"to":161,"type":"sup"}],
"refs": [{"v":186,"label":"Trigger 186"}],
"sources": L("https://stockanalysis.com/quote/swx/UHR/financials/","StockAnalysis.com") + " (Stand 22.10.2026), " + L("https://mailing-ircockpit.eqs.com/crm-mailing/5b724614-ea7c-11e8-902f-2c44fd856d8c/848ccdaa-2561-4ad8-8a87-17034876eeb7/48b92baa-da0e-41be-85f7-ff8982cd305e/PR_Halfyear_Report_2026_en.pdf","Swatch Halbjahresbericht 2026") + ", " + L("https://www.swatchgroup.com/sites/default/files/annual_report/annual_report_corporate_governance_en.pdf","Swatch Geschäftsbericht 2025 (Corporate Governance)") + ", " + L("https://www.cash.ch/news/top-news/swatch-oder-richemont-fur-goldman-sachs-ist-die-wahl-klar-974141","cash.ch: Goldman Sachs (5.10.2026)") + ", " + L("https://www.swissinfo.ch/eng/swatch-quashes-activist-attempt-to-shake-up-hayek-stronghold/91402437","swissinfo: Generalversammlung 2026") + ", " + L("https://www.crownandcaliber.com/p/swiss-watch-tariffs-change-again-what-the-new-12-5-rate-means","US-Zölle (24.7.2026)") + ", " + L("https://www.cash.ch/aktien/the-swatch-grp-i-1225515","Kursziele (cash.ch)") + ". Branchenvergleich der App: Note 1.3 von 5, fairer Wert rund 44 % unter dem Kurs, Unsicherheit mittel."
}
if __name__ == "__main__":
    json.dump(c, open(os.path.join(P, "config", "UHR.json"), "w"), ensure_ascii=False, indent=1)
    print("ok", sum(r[2] for r in c["Q"]), sum(r[2] for r in c["T"]))
