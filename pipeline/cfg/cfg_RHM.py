import json, os, sys
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, P)
from helpers import L, ADW, RSIW, SEAS
c = {
"ticker": "RHM", "name": "Rheinmetall", "datum": "23.10.2026", "waehrung": "EUR", "land": "Deutschland",
"meta": "Rheinmetall AG · Xetra: RHM · Rüstung: Panzer und Militärfahrzeuge, Munition, Flugabwehr, Elektronik, seit März 2026 auch Kriegsschiffe (NVL) · Düsseldorf, Deutschland",
"price": "1'019.00 €",
"pricemeta": "Schluss 23.10.2026 · 52 Wochen: 909 – 1'966 € · Allzeithoch rund 2'008 € (Wochenhoch Ende September 2025)",
"verdict": "Rheinmetall ist der grösste Rüstungskonzern Deutschlands und wächst so schnell wie nie: Auftragsbestand 80.5 Mrd. € (rund 6 Jahresumsätze), Umsatz im 2. Quartal 2026 +69 %, Ziel 2030 rund 50 Mrd. € Umsatz. Trotzdem hat sich der Kurs vom Hoch (rund 2'000 €) auf 1'019 € halbiert. Gründe: Friedensgespräche zur Ukraine, verfehlte Erwartungen, das gestoppte Fregattenprogramm F126 und ein tief negativer Free Cashflow im 1. Halbjahr (−1.6 Mrd. €). Qualität hellgrün (66), Timing gelb (48). Der Chef kauft seit Mai für rund 13.6 Mio. € eigene Aktien. Der grosse Prüfstein ist der Bundestag am 9.12.2026 zum Boxer-Auftrag (rund 12.4 Mrd. € für Rheinmetall).",
"about": "Rheinmetall baut Militärfahrzeuge (Boxer, Lynx, Panther, Teile des Leopard 2), Artillerie- und Panzermunition, Flugabwehr (Skynex), Elektronik und Digitalisierung für Armeen und seit März 2026 mit der Werft NVL auch Kriegsschiffe. 2025 kam rund die Hälfte des Umsatzes aus Fahrzeugen, gut ein Drittel aus Waffen und Munition, der Rest aus Elektronik. Die Munitionssparte ist am profitabelsten (29 % Marge). Das zivile Geschäft (Autoteile) wird verkauft und ist in den Zahlen ab 2024 herausgerechnet. Wichtigster Kunde ist Deutschland (38 % im 1. Halbjahr 2026), danach andere NATO-Länder und die Ukraine. Fast alle Aktien sind im Streubesitz.",
"why": "2025 stieg die Aktie um rund 119 %, Ende September 2025 kostete sie knapp 2'000 €. Seither fiel sie um rund die Hälfte. Am 18.11.2025 setzte Rheinmetall sehr hohe Ziele (2030: rund 50 Mrd. € Umsatz, Marge über 20 %). Am 11.3.2026 lagen die Jahreszahlen 2025 und die Prognose 2026 unter den Erwartungen (Aktie −6 %). Im April drückten Gespräche über einen Frieden in der Ukraine die ganze Branche. Am 7.5. verfehlte das 1. Quartal die Erwartungen (Gewinn pro Aktie 2.18 € statt 2.70 €), JPMorgan stufte auf Neutral ab. Am 24.6. stoppte der Bund die Fregatte F126, für die die neue Rheinmetall-Werft NVL verantwortlich war (Aktie bis −13 % an einem Tag). Am 6.8. senkte Rheinmetall die Umsatzprognose 2026 leicht auf 13.7 bis 14.2 Mrd. €, das 2. Quartal war aber stark (Marge 17.1 % statt erwarteter 14.9 %). Am 9.10. stufte Berenberg auf Halten ab (Ziel 1'020 €), Kurs 939 €. Seither erholte sich die Aktie leicht.",
"kpis": [
 ["g","Umsatzwachstum","+29 %","Jahr 2025 ohne Zivilgeschäft (9.9 Mrd. €). Für 2026 erwartet Rheinmetall 13.7 bis 14.2 Mrd. €, aus eigener Kraft +28 bis 31 %. Im 2. Quartal 2026 +69 % (mit der Werft NVL)."],
 ["g","Operative Marge","18.5 %","Laut Firma 2025, von 100 € Umsatz bleiben 18.50 € Betriebsgewinn. Ziel 2026 rund 19 %, 2030 über 20 %. Nach strengerer Rechnung (StockAnalysis) 16.9 %, 2021 waren es nur 11 %."],
 ["g","Gewinn pro Aktie (EPS)","26.47 €","Letzte 12 Monate, nur fortgeführtes Rüstungsgeschäft (selbst gerechnet aus Firmenzahlen). 2024: 17.19 €, 2025: 22.73 €. Mit dem Verlust aus dem Zivilgeschäft sind es nur 15.46 €."],
 ["g","ROIC","18.7 %","Auf 100 € investiertes Kapital rund 19 € Gewinn. Gut, seit 2021 zwischen 17 und 23 %."],
 ["r","Free Cashflow","0.4 Mrd. €","Letzte 12 Monate, nur 3 % vom Umsatz. Im 1. Halbjahr 2026 flossen 1.6 Mrd. € ab, weil Anzahlungen fehlten und Lager und Werke ausgebaut wurden. 2025 waren es noch +1.4 Mrd. €."],
 ["w","Nettoschulden","2.7 Mrd. €","Mitte 2026, Ende 2025 hatte Rheinmetall noch 0.4 Mrd. € mehr Geld als Schulden. Das sind rund 1.2 Jahresgewinne vor Abschreibungen (EBITDA 2.3 Mrd. €). Noch gut tragbar."],
 ["w","KGV","38.5","Du zahlst rund 38 Jahresgewinne. Eigener Schnitt 2021 bis 2025 rund 32 (stark steigend von 12 auf 70). Also rund 19 % teurer als der Schnitt. Auf die erwarteten Gewinne 2027 gerechnet rund 21."],
 ["w","Dividende","1.1 %","11.50 € pro Aktie, einmal im Jahr (bezahlt am 15.5.2026). +42 % zum Vorjahr, seit 2021 mehr als verdreifacht. Rheinmetall zahlt 35 bis 40 % des Gewinns aus."]
],
"revtitle": "Umsatz pro Halbjahr ohne Zivilgeschäft (Mio. €)", "revunit": "Mio. €", "epsunit": "€",
"revnote": "Nur Halbjahre, weil die Quartale 2025 ohne Zivilgeschäft nicht einzeln veröffentlicht sind. Das 1. Halbjahr 2026 lag 39 % über dem Vorjahr (ohne die Werft NVL +30 %). Das 2. Halbjahr ist bei Rheinmetall immer das stärkste.",
"marginnote": "Nach StockAnalysis gerechnet. Der Sprung 2024 kommt auch daher, dass das schwächere Zivilgeschäft herausgerechnet ist. Laut Firma: 18.0 % (2024) und 18.5 % (2025).",
"finnote": "<b>Hinweis:</b> Ab 2024 ohne das zivile Geschäft (Autoteile), das verkauft wird. Darum sind 2021 bis 2023 nicht ganz vergleichbar. Gewinn pro Aktie bis 2025 nach MarketScreener, letzte 12 Monate selbst gerechnet (fortgeführtes Geschäft). KGV = Jahresschlusskurs geteilt durch diesen Gewinn, Schnitt 2021 bis 2025: 32.4. Free Cashflow nach StockAnalysis (Firma 2025: 1.2 Mrd. € «operativer Free Cashflow»).",
"FIN": [["2021",5658,"+4.7 %","11.1 %",6.72,419,"21.3 %","12.3"],["2022",6410,"+13.3 %","11.5 %",10.82,-175,"19.3 %","17.4"],["2023",7176,"+12.0 %","12.0 %",12.07,345,"16.6 %","23.9"],["2024",7715,"+7.5 %","17.2 %",15.96,988,"18.6 %","38.6"],["2025",9935,"+28.8 %","16.8 %",22.29,1415,"23.1 %","69.7"],["Letzte 12 Mt.",11413,"+49 %","16.9 %",26.47,391,"18.7 %","38.5"]],
"QREV": [["H1 25",3749],["H2 25",6186],["H1 26",5227]],
"revdec": 0,
"MARGIN": [["2021",11.1],["2022",11.5],["2023",12.0],["2024",17.2],["2025",16.8],["12 Mt.",16.9]],
"Q": [
 ["Umsatztrend","Q1 2026 +8 %, Q2 2026 +69 %, Jahr 2025 +29 %. Die Quartale 2025 ohne Zivilgeschäft fehlen (Daten teils fehlen)",10,15],
 ["Wachstumstempo","Prognose 2026 aus eigener Kraft +28 bis 31 %",10,10],
 ["Operative Marge","18.5 % laut Firma (6 Pkt.), seit 2021 klar steigend (6 Pkt.)",12,15],
 ["Gewinnwachstum (EPS)","Fortgeführtes Geschäft 17.19 → 22.73 → 26.47 €, über 15 % pro Jahr",10,10],
 ["Free Cashflow","Meist positiv (2022 negativ), letzte 12 Monate stark gesunken auf 0.4 Mrd. €",3,10],
 ["ROIC","18.7 %, seit 2021 seitwärts zwischen 17 und 23 %",10,15],
 ["Schulden","Nettoschulden/EBITDA rund 1.2",7,10],
 ["Bewertung vs. eigene Historie","KGV 38.5 statt Ø 32.4 (2021–2025), rund 19 % teurer",4,15]
],
"adwnote": ADW + "Die Wochen-A/D fällt seit dem Hoch im Sommer 2025 langsam: Mitte September 2026 stand sie bei gleichem Kurs (1'012 €) bei 41.1, heute bei 40.6. Kein Zeichen, dass grosse Käufer zurückkommen.",
"rsiwnote": RSIW + "Im Juni bei 30 (überverkauft), beim tieferen Kurs-Tief im Oktober bei 36: leicht positive Abweichung. Heute 43, neutral.",
"addnote": "Neutral bis leicht negativ. Beim Tief vom 8.10. (909 €) lag die Tages-A/D bei 12.5, tiefer als beim Tief vom 11.9. (13.4). Mit der Erholung stieg sie auf 13.2, liegt aber unter dem Wert vom 15.9. (13.5) bei fast gleichem Kurs. Es fehlt eine klare Käufer-Spur.",
"ind": [
 ["Kurs vs. EMA 50","1'019 &lt; 1'030","1'019 &lt; 1'235","Knapp unter der Tageslinie, klar unter der Wochenlinie."],
 ["Kurs vs. EMA 200","1'019 &lt; 1'218","1'019 &gt; 963","Tag darunter, Woche noch darüber."],
 ["EMA 50 vs. EMA 200","50 unter 200 (seit 31.3.2026)","50 über 200, Abstand schrumpft","Tag im Abwärtstrend, Woche: Rücksetzer im langen Aufwärtstrend."],
 ["RSI (14)","51.9","42.6","Tag: Kurs-Tief im Oktober tiefer als im Juni, RSI höher (36 statt 24): bullische Divergenz."],
 ["A/D","leicht tiefer bei gleichem Kurs","fällt langsam","Keine Käufer-Spur, eher neutral bis negativ."],
 ["Volumen","Ø 20 Tage 0.19 Mio. vs. Ø 100 Tage 0.21 Mio. Aktien","Etwas weniger Handel als im Sommer."]
],
"smc": "Seit dem Wochenhoch von rund 2'008 € (Ende September 2025) macht Rheinmetall tiefere Hochs (1'966 € im Januar, 1'238 € im August 2026) und tiefere Tiefs (1'099 € im Mai, 929 € im Juni, 909 € am 8.10.2026). Das Juni- und das Oktober-Tief liegen nah beieinander, beide knapp unter der Wochen-EMA 200 (963 €): eine mögliche Bodenbildung, aber noch nicht bestätigt. Im Tageschart gab es seit August tiefere Hochs (1'238 → 1'185 → 1'045 → 987 €). Am 16.10. schloss der Kurs mit 1'090 € deutlich über dem letzten tieferen Hoch (1'045 € vom 16.9.): ein erster Change of Character im Tageschart. Seither kam der Kurs auf 1'019 € zurück. Darüber liegt der Widerstand 1'096 bis 1'146 € (Hoch vom 16.10. und vom 7.7.).",
"zones": [
 ["r","1'185–1'240 €","Widerstand: Hochs vom August (1'234 und 1'238 €) und Tages-EMA 200 (1'218 €)."],
 ["r","1'096–1'146 €","Widerstand: Hoch vom 16.10. (1'096.60 €) und vom 7.7. (1'146 €)."],
 ["t","1'097 €","<b>Trigger:</b> Tagesschluss über dem Hoch vom 16.10. Dann wäre aus dem ersten Change of Character ein höheres Hoch geworden."],
 ["s","910–962 €","<b>Kaufzone 1:</b> Doppelboden aus den Tiefs vom 26.6. (929 €) und 8.10. (909 €), Wochen-EMA 200 (963 €)."],
 ["s","820–895 €","<b>Kaufzone 2:</b> Kurslücke vom Februar 2025 (Wochenschluss 894 €), letzte grössere Unterstützung unter dem Doppelboden."],
 ["r","900 €","Abbruch: Wochenschluss unter dem Oktober-Tief (909 €). Dann wäre der Doppelboden gebrochen."]
],
"smart": [
 "<b>Insider-Käufe:</b> CEO Armin Papperger kaufte seit Mai 2026 für rund 13.6 Mio. € eigene Aktien, unter anderem 4'000 Stück zu 1'249.91 € am 1.6. (5.0 Mio. €), 3'188 Stück zu 954.62 € am 25.6. (3.0 Mio. €) und 525 Stück zu rund 950 € am 29.9. Auch Aufsichtsratschef Ulrich Grillo, Vorstand René Gansauge und eine Stiftung von Aufsichtsrat Andreas Georgi (2.10.) kauften. Verkäufe von Insidern: keine gefunden.",
 "<b>Rückkäufe:</b> Keine. Die Aktienzahl stieg 2025 um rund 4 % (Kapitalerhöhung für Zukäufe). Eine Wandelanleihe (500 Mio. €, Wandlungspreis 307.80 €) kann weitere rund 1.6 Mio. Aktien bringen.",
 "<b>Grosse Investoren:</b> 98 % Streubesitz. Bewegungen grosser Fonds 2026 nicht gefunden.",
 "<b>Analysten:</b> 21 Analysten, Mehrheit «Kaufen», Kursziel im Schnitt rund 1'560 € (StockAnalysis, MarketScreener). Spanne 1'020 € (Berenberg, Halten, 9.10.) bis 2'380 €. JPMorgan Neutral (1'500 €), Goldman Sachs Kaufen (2'300 €). Im April lag das Ziel im Schnitt noch bei 2'045 €."
],
"seasnote": SEAS + "Daten seit 1998. November schwach (−1.1 %, nur 39 % positive Jahre), Dezember (+4.5 %, 61 %) und Januar (+6.7 %, 79 %) sind die stärksten Monate. Der Oktober ist noch nicht abgeschlossen.",
"T": [
 ["Trend Woche (EMA 50/200)","Kurs über EMA 200 (963 €), unter EMA 50 (1'235 €): Rücksetzer im Aufwärtstrend, EMA 50 fällt aber",12,20],
 ["Trend Tag (EMA 50/200)","Kurs knapp unter beiden, EMA 50 unter 200, Abstand zur EMA 50 klein",2,10],
 ["Struktur (SMC)","Woche tiefere Tiefs, aber möglicher Doppelboden. Tag: erster CHoCH am 16.10., noch unbestätigt",8,20],
 ["RSI Tag/Woche","Bullische Divergenz Tag (Oktober-Tief tiefer, RSI höher), Woche ähnlich, Trend aber nicht intakt",12,15],
 ["A/D Tag/Woche","Beide neutral bis leicht fallend, keine Divergenz",4,20],
 ["Smart Money","Start 3, Insider-Käufe rund 14 Mio. € seit Mai +4, kein Rückkauf",7,10],
 ["Saisonalität","November schwach (39 %), Dezember und Januar stark (61 % und 79 %)",3,5]
],
"pro": [
 "Rekord-Auftragsbestand 80.5 Mrd. €, rund sechs Jahresumsätze. Das Wachstum ist für Jahre gesichert.",
 "Prognose 2026: +28 bis 31 % aus eigener Kraft, Marge rund 19 %, im 2. Quartal schon 17.1 %.",
 "Der CEO kauft massiv eigene Aktien (rund 13.6 Mio. € seit Mai), auch zu tiefen Kursen.",
 "Ein grosser Auslöser steht fest: Bundestag am 9.12.2026 zum Boxer-Auftrag Arminius, mit über 3 Mrd. € Anzahlung.",
 "Die Dividende stieg seit 2021 von 3.30 auf 11.50 €."
],
"con": [
 "Der Free Cashflow ist eingebrochen (1. Halbjahr −1.6 Mrd. €), die Firma hat jetzt Nettoschulden statt Netto-Cash.",
 "Die Erwartungen sind hoch: 2026 schon zweimal verfehlt, Umsatzprognose im August gesenkt.",
 "Die Werft NVL hat mit der gestrichenen Fregatte F126 ihren grössten Auftrag verloren.",
 "Ein Frieden in der Ukraine drückt jedes Mal stark auf den Kurs, und Deutschland ist ein Klumpenrisiko (38 % Umsatz).",
 "Die Bewertung ist trotz Halbierung nicht billig: KGV 38.5, teurer als der eigene Schnitt."
],
"todo": [
 ["t","Beobachten","Alarm bei 1'097 € (Trigger) und 962 € (oberes Ende Kaufzone 1)."],
 ["s","Timing grün","Tagesschluss über 1'097 € mit steigender A/D. Oder ein Test der Kaufzone 910 bis 962 €, der über 900 € hält. Fundamental: Q3-Zahlen am 5.11., Investorentag 26./27.11. und vor allem die Freigabe für Arminius am 9.12.2026."],
 ["r","Abbruch","Wochenschluss unter 900 €. Dann wäre die Kaufzone 2 (820 bis 895 €) das nächste Ziel."],
 ["","Nächste Zahlen","3. Quartal am 5. November 2026 (bestätigt). Erwartet: rund 3.2 Mrd. € Umsatz, 7.00 € Gewinn pro Aktie. Jahreszahlen am 11. März 2027."]
],
"bands": [{"from":1185,"to":1240,"type":"res"},{"from":1096,"to":1146,"type":"res"},{"from":910,"to":962,"type":"sup"},{"from":820,"to":895,"type":"sup"}],
"refs": [{"v":1097,"label":"Trigger 1'097"}],
"sources": L("https://stockanalysis.com/quote/etr/RHM/financials/","StockAnalysis.com") + " (Stand 25.10.2026), " + L("https://www.rheinmetall.com/de/media/news-watch/news/2026/03/2026-03-11-rheinmetall-bilanzvorlage-geschaeftsjahr-2025","Rheinmetall Geschäftsjahr 2025") + ", Rheinmetall Halbjahresbericht 6.8.2026, " + L("https://uk.marketscreener.com/quote/stock/RHEINMETALL-AG-436527/finances/","MarketScreener") + ", " + L("https://www.marketscreener.com/quote/stock/RHEINMETALL-AG-436527/company-insider-trading/","Insider (MarketScreener)") + ", " + L("https://ms-aktuell.de/finanzen/rheinmetall-aktie-berenberg-11-10-2026/","Berenberg-Abstufung (11.10.2026)") + ", " + L("https://www.boerse-global.de/rheinmetall-aktie-124-milliarden-fuer-boxer-radpanzer-angepeilt/827711","Boxer-Auftrag Arminius (18.9.2026)") + ", " + L("https://www.rheinmetall.com/de/investor-relations/aktie/dividende","Dividende (Rheinmetall)") + ". Branchenvergleich App: Note 2.2 von 5, fairer Wert nach Modellen deutlich unter dem Kurs, Unsicherheit hoch."
}
if __name__ == "__main__":
    json.dump(c, open(os.path.join(P, "config", "RHM.json"), "w"), ensure_ascii=False, indent=1)
    print("ok", sum(r[2] for r in c["Q"]), sum(r[2] for r in c["T"]))
