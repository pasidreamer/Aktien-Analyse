import json, os, sys
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, P)
from helpers import L, ADW, RSIW, SEAS
c = {
"ticker": "ADBE", "name": "Adobe", "datum": "15.10.2026", "waehrung": "USD", "land": "USA",
"meta": "Adobe Inc. · NASDAQ: ADBE · Software für Kreative (Photoshop, Illustrator, Premiere), PDF (Acrobat) und Marketing · San José, USA",
"price": "251.67 $",
"pricemeta": "Schluss 15.10.2026 · 52 Wochen: 190.12 – 363.70 $ · Allzeithoch 699.54 $ im November 2021",
"verdict": "Adobe ist ein Free-Cashflow-Monster: 10.6 Mrd. $ freies Geld pro Jahr, 41 % vom Umsatz, und damit kauft Adobe jedes Jahr rund 7 % der eigenen Aktien zurück. Die Börse glaubt aber, dass KI-Werkzeuge Adobe das Geschäft wegnehmen. Darum fiel die Aktie vom Allzeithoch 699.54 $ auf 251.67 $ (−64 %), das KGV liegt bei 14 statt rund 41. Qualität grün (88), Timing gelb (53). Seit dem Tief vom Juni (190.12 $) macht die Aktie höhere Tiefs, heute schloss sie erstmals über dem letzten tieferen Hoch. Das grosse Risiko: Wenn die KI-Sorge stimmt, ist der heutige Free Cashflow nicht nachhaltig.",
"about": "Adobe verkauft Software im Abo: Creative Cloud (Photoshop, Illustrator, Premiere, Lightroom, Firefly) für Designer, Fotografen und Videomacher, Acrobat und Adobe Express für PDF und einfache Grafiken, und Marketing-Software für grosse Firmen (Experience Cloud, GenStudio, seit April 2026 auch Semrush für Suchmaschinen). Rund drei Viertel des Umsatzes kommen aus dem Bereich Digital Media. Weil fast alles im Abo läuft, sind die Einnahmen gut planbar: Der jährlich wiederkehrende Umsatz (ARR) lag Ende August 2026 bei 27.5 Mrd. $. Die Produkte sind in vielen Firmen und Schulen Standard.",
"why": "Seit 2025 fürchtet die Börse, dass KI-Werkzeuge (Canva, Figma, Midjourney, OpenAI, Claude Design und neu auch kostenlose KI-Kopien von Photoshop wie ArtCraft) Adobe-Kunden abwerben. Im Januar und Februar 2026 verkauften Anleger viele Software-Aktien aus KI-Angst. Am 12. März kündigte CEO Shantanu Narayen seinen Rücktritt an, die Aktie fiel um rund 8 %. Am 11. Juni folgte trotz guter Zahlen ein Minus von 6 %: Ein Teil des Wachstums kam vom Zukauf Semrush, das Wachstum aus eigener Kraft wurde langsamer, und Finanzchef Dan Durn ging. Am 18. Juni stand die Aktie bei 190.12 $ (Jahrestief). Seither erholt sie sich, aber im September und Oktober drückten Herabstufungen: Wells Fargo am 12.10. auf Untergewichten (Ziel 225 $), HSBC am 13.10. auf Halten (Ziel 267 $). Das Geschäft selbst wächst weiter: Umsatz +13 % im 3. Quartal, achtmal in Folge besser als erwartet, Prognose zweimal erhöht. Am 15.10. stieg die Aktie um 4.6 % nach einer erweiterten Zusammenarbeit mit NVIDIA.",
"kpis": [
 ["g","Umsatzwachstum","+12.0 %","Letzte 12 Monate. Ohne den Zukauf Semrush rund 11 %. Seit 2022 stabil zwischen 10 und 13 % pro Jahr."],
 ["g","Operative Marge","36.3 %","Von 100 $ Umsatz bleiben rund 36 $ Betriebsgewinn. Sehr hoch und seit 5 Jahren stabil zwischen 34 und 37 %."],
 ["g","Gewinn pro Aktie (EPS)","17.92 $","Letzte 12 Monate nach offiziellen Regeln (GAAP). Bereinigt 23.65 $, das sind +15 bis +19 % pro Quartal zum Vorjahr. 2021 waren es 10.02 $."],
 ["g","ROIC","57 %","Auf 100 $ investiertes Kapital rund 57 $ Gewinn. Ausgezeichnet und seit 2021 (38 %) stark gestiegen."],
 ["g","Free Cashflow","10.6 Mrd. $","Letzte 12 Monate. 41 % vom Umsatz bleiben als freies Geld. 2021 waren es 6.9 Mrd. $. Achtung: 2.1 Mrd. $ davon sind Löhne in Aktien, die den FCF schöner machen."],
 ["g","Nettoschulden","1.1 Mrd. $","Mit einem Zehntel des Jahres-FCF bezahlt. Früher hatte Adobe mehr Geld als Schulden, die Rückkäufe waren 2024 und 2025 grösser als der FCF."],
 ["g","KGV","14.1","Du zahlst 14 Jahresgewinne. Eigener Schnitt 2021–2025: rund 41. Also rund zwei Drittel günstiger als üblich. Die Börse bewertet Adobe wie eine schrumpfende Firma."],
 ["g","Aktienrückkäufe","−7.5 %","So viel weniger Aktien gibt es im 3. Quartal 2026 als im Schnitt 2025. Seit 2021 minus 18 %. Neues Programm: 25 Mrd. $ bis 2030, rund ein Viertel des Börsenwerts. Keine Dividende."]
],
"revtitle": "Umsatz pro Quartal (Mio. $)", "revunit": "Mio. $", "epsunit": "$",
"revnote": "Alle 8 Quartale über dem Vorjahr, das Wachstum stieg zuletzt von 10.5 auf 12.9 %. Seit Mai 2026 ist Semrush dabei (rund 120 Mio. $ pro Quartal).",
"marginnote": "Seit 2021 stabil zwischen 34 und 37 %. Bereinigt (ohne Aktienvergütung und Zukäufe) rund 44 %.",
"finnote": "<b>Hinweis:</b> Adobe hat ein Geschäftsjahr bis Ende November. Q3 26 = Juni bis August 2026. Das KGV-Mittel ist über 2021–2025 gerechnet (60.8, 33.4, 51.4, 40.9, 18.8). Keine Dividende, Adobe gibt das Geld über Aktienrückkäufe zurück.",
"FIN": [["2021",15785,"+22.7 %","36.8 %",10.02,6882,"38.2 %","60.8"],["2022",17606,"+11.5 %","34.6 %",10.10,7396,"36.8 %","33.4"],["2023",19409,"+10.2 %","34.3 %",11.82,6942,"41.9 %","51.4"],["2024",21505,"+10.8 %","36.4 %",12.36,7873,"50.1 %","40.9"],["2025",23769,"+10.5 %","36.6 %",16.70,9852,"59.3 %","18.8"],["Letzte 12 Mt.",25970,"+12.0 %","36.3 %",17.92,10592,"57.2 %","14.1"]],
"QREV": [["Q4 24",5606],["Q1 25",5714],["Q2 25",5873],["Q3 25",5988],["Q4 25",6194],["Q1 26",6398],["Q2 26",6618],["Q3 26",6760]],
"revdec": 0,
"MARGIN": [["2021",36.8],["2022",34.6],["2023",34.3],["2024",36.4],["2025",36.6],["12 Mt.",36.3]],
"Q": [
 ["Umsatztrend","4 von 4 Quartalen über Vorjahr, Wachstum steigt von 10.5 auf 12.9 % (teils durch Semrush)",13,15],
 ["Wachstumstempo","Rund 11 % ohne Zukauf, 12 % mit Semrush",8,10],
 ["Operative Marge","36.3 % (9 Pkt.), seit 5 Jahren stabil (3 Pkt.)",12,15],
 ["Gewinnwachstum (EPS)","GAAP 2022–2025 rund +18 % pro Jahr, bereinigt aktuell +15 bis +19 %",10,10],
 ["Free Cashflow","Immer positiv, 3 von 4 Jahren gestiegen (Delle 2023)",6,10],
 ["ROIC","57 %, seit 2021 klar steigend",15,15],
 ["Schulden","Nettoschulden/EBITDA 0.12",9,10],
 ["Bewertung vs. eigene Historie","KGV 14.1 statt Ø 41 (2021–2025), rund 66 % günstiger",15,15]
],
"adwnote": ADW + "Seit dem Tief im Juni (374.8) stieg die Wochen-A/D bis Ende August auf 510.7 und liegt heute bei 469.9. Im Mai stand sie bei gleichem Kurs (253 $) bei 458.8: leicht mehr Kaufdruck als damals.",
"rsiwnote": RSIW + "Im Februar, April und Juni unter 30 (überverkauft), heute 49.5: neutral, steigend.",
"addnote": "Klar positiv: Am 11.9. schloss der Kurs bei 252.23 $ und die A/D stand bei −33.6. Heute fast gleicher Kurs (251.67 $), A/D −23.1. Bei gleichem Preis wurde deutlich mehr gekauft (bullische Divergenz). Auch beim Tief vom 7.10. (227 $) lag die A/D höher als beim Tief vom 28.9.",
"ind": [
 ["Kurs vs. EMA 50","251.7 &gt; 247.6","251.7 &lt; 274.0","Tag knapp darüber, Woche darunter."],
 ["Kurs vs. EMA 200","251.7 &lt; 265.6","251.7 &lt; 369.1","Unter der langfristigen Linie, auf beiden Zeitebenen."],
 ["EMA 50 vs. EMA 200","50 unter 200 (seit 19.12.2025)","50 unter 200 (seit April 2025)","Der grosse Trend ist abwärts."],
 ["RSI (14)","55.4","49.5","Tag aus 34 (28.9.) nach oben gedreht, Woche neutral."],
 ["A/D","höher bei gleichem Kurs (bullische Divergenz)","seit Juni gestiegen, leicht positiv","Tag klar positiv, Woche leicht positiv."],
 ["Volumen","Ø 20 Tage 4.8 Mio. vs. Ø 100 Tage 5.9 Mio. Aktien","Weniger Handel als im Sommer: Der Verkaufsdruck lässt nach."]
],
"smc": "Vom Allzeithoch 699.54 $ (November 2021) fiel Adobe in einem langen Abwärtstrend mit tieferen Hochs und Tiefs bis auf 190.12 $ am 18. Juni 2026. Danach stieg die Aktie bis 294.53 $ (1.9.) und damit über die Hochs vom März (285.36 $) und Juni (275.44 $): Im Wochenchart ist das ein erster Change of Character nach oben. Der Rücksetzer endete am 28.9. bei 224.67 $, deutlich über dem Juni-Tief (höheres Tief). Im Tageschart gab es seit September tiefere Hochs (294.53 → 266.10 → 248.30 $). Am 7.10. hielt das Tief bei 227 $ über dem vom 28.9., und am 15.10. schloss der Kurs mit 251.67 $ erstmals über dem Hoch vom 1.10. (248.30 $): ein erster kleiner Change of Character im Tageschart. Darüber liegt der Widerstand 265–275 $ mit der Tages-EMA 200 und der Wochen-EMA 50.",
"zones": [
 ["r","286–295 $","Widerstand: Hochs von Ende August und Anfang September (294.53 $)."],
 ["r","265–275 $","Widerstand: Hoch vom 14.9. (266.10 $), Tages-EMA 200 (265.60 $) und Wochen-EMA 50 (274 $)."],
 ["t","267 $","<b>Trigger:</b> Tagesschluss über dem Hoch vom 14.9. und der Tages-EMA 200. Ein erstes Signal kam am 15.10. (Schluss über 248.30 $)."],
 ["s","232–242 $","<b>Kaufzone 1:</b> Bodenbildung im Oktober (Tagesschlüsse 232.77 bis 242.27 $) und Tief vom 11.9. (241.51 $)."],
 ["s","200–212 $","<b>Kaufzone 2:</b> Tiefs von Ende Juni und Juli (202.73 $ Wochenschluss, 210.88 $ am 23.7.)."],
 ["r","224 $","Abbruch: Wochenschluss unter dem Tief vom 28.9. (224.67 $). Dann wäre das höhere Tief verloren."]
],
"smart": [
 "<b>Adobe selbst:</b> Neues Rückkaufprogramm über 25 Mrd. $ bis April 2030 (rund 25 % des Börsenwerts). In den ersten 9 Monaten 2026 für 6.9 Mrd. $ rund 26 Mio. Aktien zurückgekauft. Das sind rund 7 % des Börsenwerts pro Jahr.",
 "<b>Insider-Kauf:</b> Verwaltungsrat David Ricks (Chef von Eli Lilly) kaufte am 25.6.2026 10'000 Aktien zu 194.51 $ (1.95 Mio. $), fast am Tief.",
 "<b>Insider-Verkäufe:</b> CEO Shantanu Narayen verkaufte in 12 Monaten für rund 49.6 Mio. $ (zuletzt 125'000 Aktien zu rund 250 $ am 16./17.9.). Er gibt den Chefposten am 1.12.2026 ab. Ob die Verkäufe nach einem festen Plan liefen, ist nicht geprüft.",
 "<b>Analysten:</b> Mehrheit «Halten». MarketBeat: 9× Kaufen, 20× Halten, 7× Verkaufen, Kursziel im Schnitt 284 $ (195 bis 430 $). Zuletzt Herabstufungen von Wells Fargo (12.10., Ziel 225 $) und HSBC (13.10., Ziel 267 $). Für Kontra-Anleger: Viele Verkaufen-Stimmen bei einer Firma mit Rekord-Cashflow."
],
"seasnote": SEAS + "40 Jahre Daten (seit 1986). Oktober (+6.3 %, 68 % positive Jahre) und November (+3.4 %, 68 %) sind die stärksten Monate, Juni und Juli die schwächsten.",
"T": [
 ["Trend Woche (EMA 50/200)","Kurs unter beiden, EMA 50 unter 200 und fallend",2,20],
 ["Trend Tag (EMA 50/200)","Kurs über EMA 50, unter EMA 200: mögliche Wende",4,10],
 ["Struktur (SMC)","Woche: CHoCH im August und höheres Tief. Tag: erster CHoCH am 15.10., noch unbestätigt",13,20],
 ["RSI Tag/Woche","Tag aus 34 auf 55 gedreht, Woche 50 steigend, aber kein intakter Trend",10,15],
 ["A/D Tag/Woche","Tag: bullische Divergenz. Woche: leicht positiv",12,20],
 ["Smart Money","Start 3, Insider-Kauf Juni +4, Rückkauf rund 7 % pro Jahr +3, viele CEO-Verkäufe −3",7,10],
 ["Saisonalität","Oktober und November je 68 % positive Jahre",5,5]
],
"pro": [
 "Riesiger Free Cashflow (10.6 Mrd. $, 41 % vom Umsatz) und sehr hohe Kapitalrendite (57 %).",
 "Kauft jedes Jahr rund 7 % der eigenen Aktien zurück: Jede Aktie besitzt einen immer grösseren Teil der Firma.",
 "Sehr günstig: KGV 14 statt rund 41 im eigenen Schnitt, FCF-Rendite fast 11 %.",
 "Umsatz wächst weiter mit 12 %, acht Quartale in Folge besser als erwartet.",
 "Kontra-Lage: viel Angst, Analysten skeptisch, Tages-A/D zeigt Käufe bei tiefen Kursen."
],
"con": [
 "KI kann vor allem das günstige Kundensegment wegnehmen: kostenlose KI-Kopien, Canva, Figma, Claude Design.",
 "Wachstum aus eigener Kraft wird langsamer, im 4. Quartal braucht Adobe fast doppelt so viel Neugeschäft wie im 3. Quartal.",
 "Chefwechsel: neuer CEO ab 1.12.2026, Finanzchef ist nur interimistisch besetzt.",
 "Rückkäufe waren 2024 und 2025 grösser als der FCF und teils mit Schulden bezahlt. Das Netto-Cash ist weg.",
 "Der grosse Trend (Wochen-EMA 200 bei 369 $) zeigt klar nach unten."
],
"todo": [
 ["t","Beobachten","Alarm bei 267 $ (Trigger) und 242 $ (oberes Ende Kaufzone 1)."],
 ["s","Timing grün","Tagesschluss über 267 $ mit weiter steigender A/D. Oder ein Rücksetzer in 232–242 $, der über 224 $ hält. Fundamental: Adobe MAX (10. bis 12.11.) und die Zahlen im Dezember müssen zeigen, dass das Neugeschäft (ARR) wieder anzieht."],
 ["r","Abbruch","Wochenschluss unter 224 $. Dann wäre die Kaufzone 2 (200–212 $) das nächste Ziel."],
 ["","Nächste Zahlen","4. Quartal und Ziele für 2027: voraussichtlich 9. Dezember 2026 (nicht bestätigt). Vorher Adobe MAX vom 10. bis 12. November."]
],
"bands": [{"from":286,"to":295,"type":"res"},{"from":265,"to":275,"type":"res"},{"from":232,"to":242,"type":"sup"},{"from":200,"to":212,"type":"sup"}],
"refs": [{"v":267,"label":"Trigger 267"}],
"sources": L("https://stockanalysis.com/stocks/adbe/financials/","StockAnalysis.com") + " (Stand 15.10.2026), " + L("https://news.adobe.com/news/2026/09/adobe-q3fy26-financial-results","Adobe Q3 2026") + ", " + L("https://www.tikr.com/blog/adobe-stock-fell-6-after-a-beat-and-raise-quarter-the-market-got-it-wrong","TIKR zu Q2 2026") + ", " + L("https://247wallst.com/investing/2026/10/12/adobe-falls-4-as-wells-fargo-cuts-to-underweight-with-225-target-servicenow-climbs-3-intuit-ticks-up/","24/7 Wall St (12.10.2026)") + ", " + L("https://www.nasdaq.com/articles/adobe-names-anil-chakravarthy-next-ceo","Nasdaq: neuer CEO") + ", " + L("https://www.sherwood.news/markets/adobe-rises-on-usd25-billion-stock-buyback/","Sherwood: Rückkauf 25 Mrd. $") + ", " + L("https://www.marketbeat.com/stocks/NASDAQ/ADBE/insider-trades/","Insider (MarketBeat)") + "."
}
if __name__ == "__main__":
    json.dump(c, open(os.path.join(P, "config", "ADBE.json"), "w"), ensure_ascii=False, indent=1)
    print("ok", sum(r[2] for r in c["Q"]), sum(r[2] for r in c["T"]))
