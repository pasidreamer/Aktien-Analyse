import json, os, sys
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, P)
from helpers import L, ADW, RSIW, SEAS
c = {
"ticker": "R3NK", "name": "Renk Group", "datum": "23.10.2026", "waehrung": "EUR", "land": "Deutschland",
"meta": "RENK Group AG · Xetra: R3NK · Getriebe für Panzer und Militärfahrzeuge, Schiffsantriebe, Industriegetriebe · Augsburg, Deutschland",
"price": "36.31 €",
"pricemeta": "Schluss 23.10.2026 · 52 Wochen: 33.49 – 68.36 € · Allzeithoch rund 90 € (Wochenhoch Ende September 2025)",
"verdict": "Renk baut die Getriebe, mit denen Panzer wie der Leopard 2 fahren, und ist dort Weltmarktführer. Der Auftragsbestand ist auf den Rekord von 7.4 Mrd. € gestiegen, gut fünf Jahresumsätze. Trotzdem ist die Aktie vom Hoch (rund 90 €) auf 36.31 € gefallen, das sind rund −60 %. Der Hauptgrund ist echt: Das Wachstum ist 2026 fast stehen geblieben (1. Halbjahr nur +2.7 % nach +20 % im Jahr 2025), und am 21.10. kam eine tiefere Prognose. Dazu drücken Friedensgespräche, der Verkauf eines grossen Aktienpakets durch KNDS und Leerverkäufer. Qualität gelb (59), Timing rot (28). Der Abwärtstrend ist intakt. Ein erstes gutes Zeichen: Die Tages-A/D steigt, obwohl der Kurs tiefer ist.",
"about": "Renk entwickelt und baut Getriebe und Antriebe. Rund drei Viertel des Umsatzes kommen aus der Rüstung: Getriebe für Kettenfahrzeuge (Leopard 2, Puma, K2 in Südkorea, Abrams in den USA über RENK America), dazu Antriebe für Marineschiffe und U-Boote. Der Rest sind Industriegetriebe, zum Beispiel für Zementmühlen und Windkraft. Die Sparte Gleitlager wird an die österreichische Miba verkauft. Renk ist seit Februar 2024 an der Börse. Der Panzerbauer KNDS hält noch rund 10 %, nachdem er im Mai 2026 5.8 Mio. Aktien verkauft hat.",
"why": "Bis Anfang Oktober 2025 stieg die Aktie um über 360 % in einem Jahr auf rund 90 €. Am Kapitalmarkttag vom 20.11.2025 lag das Gewinnziel für 2027 (bereinigtes EBIT über 300 Mio. €) klar unter den Erwartungen der Analysten (365 Mio. €). Am 5.3.2026 meldete Renk Rekordzahlen für 2025, aber rund 200 Mio. € Aufträge rutschten ins Jahr 2026. Im April und Mai drückten Ukraine-Friedensgespräche, Bernstein nannte Hersteller von Landsystemen (Rheinmetall, Renk) am stärksten gefährdet. Im Mai verkaufte KNDS ein grosses Aktienpaket (262 Mio. €). Das 1. Halbjahr brachte nur +2.7 % Umsatz. Ende September senkte JPMorgan das Ziel und warnte vor einem schwachen 3. Quartal, die Bank of America stufte auf Neutral ab (Ziel 42.50 €). Am 8.10. fiel die Aktie auf 33.49 €. Am 21.10. kündigte Renk den Verkauf der Gleitlager an und gab eine neue Prognose ohne diese Sparte: Umsatz rund 1.4 Mrd. €, bereinigtes EBIT 240 bis 255 Mio. €. Das liegt eher am unteren Ende der alten Prognose. JPMorgan senkte das Ziel auf 50 €.",
"kpis": [
 ["w","Umsatzwachstum","+10 %","Letzte 12 Monate (selbst gerechnet). 2024 +23 %, 2025 +20 %, aber im 1. Halbjahr 2026 nur noch +2.7 %. Renk sagt, das 2. Halbjahr werde viel stärker."],
 ["w","Operative Marge","12.4 %","Letzte 12 Monate nach allen Kosten. Seit 2022 (7.7 %) jedes Jahr gestiegen. Renk zeigt die bereinigte Marge: 16.9 % (2025), Ziel 2030 über 20 %."],
 ["w","Gewinn pro Aktie (EPS)","0.99 €","Letzte 12 Monate, kaum mehr als 2025 (1.00 €). Vorher stark gestiegen: 0.16 € (2022), 0.32 € (2023), 0.53 € (2024)."],
 ["r","ROIC","9.9 %","Auf 100 € investiertes Kapital rund 10 € Gewinn. Noch tief, aber stark verbessert (2022: 5.6 %), weil die alten Schulden aus der Zeit vor dem Börsengang sinken."],
 ["w","Free Cashflow","rund 116 Mio. €","Letzte 12 Monate, 8 % vom Umsatz. Schwankt: 138 Mio. € (2024), 94 Mio. € (2025). Im 1. Halbjahr 2026 41 Mio. €, besser als erwartet."],
 ["g","Nettoschulden","0.37 Mrd. €","Mitte 2026. Das sind rund 1.4 Jahresgewinne vor Abschreibungen (EBITDA 2025: 264 Mio. €). Im Juli 2026 wurden die alten Kredite durch günstigere ersetzt (1.05 Mrd. €)."],
 ["w","KGV","36.7","Du zahlst rund 37 Jahresgewinne. Schnitt der Jahresenden seit dem Börsengang (2024 und 2025): rund 44. Also rund 17 % günstiger, aber nur zwei Vergleichswerte. Auf die erwarteten Gewinne 2027 gerechnet rund 18."],
 ["w","Dividende","1.6 %","0.58 € pro Aktie, einmal im Jahr (bezahlt am 15.6.2026). +38 % zum Vorjahr. Renk zahlt rund 40 % des bereinigten Gewinns aus."]
],
"revtitle": "Umsatz pro Quartal (Mio. €)", "revunit": "Mio. €", "epsunit": "€",
"revnote": "2025 wuchs jedes Quartal 15 bis 28 %, im 1. und 2. Quartal 2026 nur noch +3.9 % und +1.9 %. Quartale teils aus den Halbjahres- und 9-Monats-Zahlen selbst gerechnet. Die Gleitlager (2025: 128 Mio. € Umsatz) sind hier noch enthalten.",
"marginnote": "Nach allen Kosten (IFRS), nach TipRanks. Seit 2022 jedes Jahr höher. Bereinigt laut Renk: 16.2 % (2023), 16.6 % (2024), 16.9 % (2025), 15.4 % im 1. Halbjahr 2026.",
"finnote": "<b>Hinweis:</b> Renk ist erst seit Februar 2024 an der Börse, darum gibt es KGV-Werte nur für 2024 und 2025. Zahlen 2021 fehlen teilweise und sind weggelassen. Quellen: Umsatz nach Firma und MarketScreener, Marge, Gewinn pro Aktie, ROIC und KGV nach TipRanks, Free Cashflow nach TipRanks und MarketScreener. StockAnalysis war für diese Analyse nicht abrufbar.",
"FIN": [["2022",849,"+21.6 %","7.7 %",0.16,62,"5.6 %","–"],["2023",926,"+9.0 %","9.6 %",0.32,48,"5.7 %","–"],["2024",1141,"+23.2 %","10.2 %",0.53,138,"6.0 %","34.6"],["2025",1366,"+19.8 %","12.6 %",1.00,94,"11.6 %","53.6"],["Letzte 12 Mt.",1383,"+10 %","12.4 %",0.99,116,"9.9 %","36.7"]],
"QREV": [["Q3 24",268],["Q4 24",363],["Q1 25",273],["Q2 25",347],["Q3 25",308],["Q4 25",438],["Q1 26",284],["Q2 26",354]],
"revdec": 0,
"MARGIN": [["2022",7.7],["2023",9.6],["2024",10.2],["2025",12.6],["12 Mt.",12.4]],
"Q": [
 ["Umsatztrend","4 von 4 Quartalen über Vorjahr, aber das Tempo bricht ein (+21 % auf +2 %)",11,15],
 ["Wachstumstempo","Letzte 12 Monate rund +10 %, 1. Halbjahr 2026 nur +2.7 %",6,10],
 ["Operative Marge","12.4 % (3 Pkt.), seit 2022 jedes Jahr gestiegen (6 Pkt.)",9,15],
 ["Gewinnwachstum (EPS)","2022 bis 2025 stark gestiegen (0.16 → 1.00 €), letzte 12 Monate flach",8,10],
 ["Free Cashflow","Immer positiv, aber schwankend",6,10],
 ["ROIC","9.9 % (unter 10 %), klar steigend",3,15],
 ["Schulden","Nettoschulden/EBITDA rund 1.4",7,10],
 ["Bewertung vs. eigene Historie","KGV 36.7 statt Ø rund 44 (2024–2025), rund 17 % günstiger, nur kurze Historie",9,15]
],
"adwnote": ADW + "Die Wochen-A/D fällt seit dem Hoch 2025 mit dem Kurs: Ende September 2026 −13.5 bei 37 €, heute −14.3 bei 36 €. Es überwiegen die Verkäufer.",
"rsiwnote": RSIW + "Anfang Oktober bei 33, knapp über überverkauft, heute 38. Schwach, ohne Bodenzeichen.",
"addnote": "Positiv: Am 22.9. schloss der Kurs bei 41.08 € und die Tages-A/D stand bei 20.7. Heute ist der Kurs tiefer (36.31 €), die A/D aber höher (20.9). Auch nach dem Tief vom 8.10. (33.49 €, A/D 18.7) stieg sie schneller als der Kurs. Bei tieferen Preisen wird also mehr gekauft (bullische Divergenz).",
"ind": [
 ["Kurs vs. EMA 50","36.3 &lt; 40.2","36.3 &lt; 47.7","Unter der mittelfristigen Linie, auf beiden Zeitebenen."],
 ["Kurs vs. EMA 200","36.3 &lt; 47.4","36.3 &lt; 39.9","Unter der langfristigen Linie, auf beiden Zeitebenen."],
 ["EMA 50 vs. EMA 200","50 unter 200 (seit 9.3.2026)","50 noch über 200, fällt schnell","Der Trend zeigt klar nach unten."],
 ["RSI (14)","41.6","38.1","Tag aus 23 (8.10., stark überverkauft) erholt, Woche schwach."],
 ["A/D","höher bei tieferem Kurs (bullische Divergenz)","fällt mit dem Kurs","Tag positiv, Woche negativ."],
 ["Volumen","Ø 20 Tage 0.55 Mio. vs. Ø 100 Tage 0.53 Mio. Aktien","Normaler Handel."]
],
"smc": "Seit dem Wochenhoch von rund 90 € (Ende September 2025) ist Renk in einem klaren Abwärtstrend: tiefere Hochs (66.90 € im Januar, 61.94 € im März, 57.77 € im April, 56.85 € im Mai, 53.59 € im August) und tiefere Tiefs (49.11, 46.33, 42.12, 40.34 und 33.49 € am 8.10.2026). Im Tageschart liegt das letzte tiefere Hoch bei 42.74 € (21.9.). Die Erholung nach dem Oktober-Tief endete bisher bei 38.88 € (21.10.), knapp unter der Wochen-EMA 200 (39.90 €). Ein Change of Character nach oben fehlt noch. Gut: Das Tief vom 23.10. (35.65 €) liegt über dem Oktober-Tief.",
"zones": [
 ["r","47–50 €","Widerstand: Hochs und Tiefs vom Juli und August (46.51 bis 49.96 €), Tages-EMA 200 (47.40 €) und Wochen-EMA 50 (47.70 €)."],
 ["r","38.9–42.8 €","Widerstand: Hoch vom 21.10. (38.88 €), Wochen-EMA 200 (39.90 €), Tages-EMA 50 (40.20 €) und Hoch vom 21.9. (42.74 €)."],
 ["t","42.8 €","<b>Trigger:</b> Tagesschluss über dem letzten tieferen Hoch vom 21.9. Das wäre der erste Change of Character nach oben."],
 ["s","33.5–35.7 €","<b>Kaufzone 1:</b> Jahrestief vom 8.10. (33.49 €) und Tief vom 23.10. (35.65 €)."],
 ["s","29–31.2 €","<b>Kaufzone 2:</b> Tief vom April 2025 (31.17 €), vor der grossen Rally 2025."],
 ["r","33 €","Abbruch: Wochenschluss unter dem Oktober-Tief (33.49 €). Dann wäre die Kaufzone 2 das nächste Ziel."]
],
"smart": [
 "<b>Insider:</b> In den letzten 6 Monaten keine Käufe oder Verkäufe gefunden. Zuletzt am 6.3.2026: Vorständin Anja Mänz-Siebje kaufte bei 54.78 € (rund 30'000 €), eine dem CEO nahestehende Person kaufte und verkaufte fast gleich viel.",
 "<b>Grossaktionär verkauft:</b> KNDS verkaufte im Mai 2026 5.8 Mio. Aktien (rund 262 Mio. €, rund 45 € pro Aktie) und hält noch 10 %. Nach der Sperrfrist kann weiteres Angebot kommen.",
 "<b>Leerverkäufer:</b> AQR (1.78 %), Marshall Wace (über 1 %), PDT Partners (1.0 %) und Bridgewater (0.61 %, Anfang Oktober aufgestockt) wetten auf fallende Kurse, zusammen grob 5 % der Aktien. Keine Rückkäufe.",
 "<b>Analysten:</b> Mehrheit «Kaufen», Kursziel im Schnitt rund 60 € (MarketScreener, 17 Analysten). Die Ziele sinken aber: JPMorgan 75 → 62 → 50 € (21.10.), Bank of America Neutral mit 42.50 €."
],
"seasnote": SEAS + "Nur 2 bis 3 Jahre Daten (seit Februar 2024), darum kaum aussagekräftig. November und Dezember waren je einmal positiv und einmal negativ, der Januar zweimal stark positiv.",
"T": [
 ["Trend Woche (EMA 50/200)","Kurs unter beiden, EMA 50 noch über EMA 200, fällt aber schnell",4,20],
 ["Trend Tag (EMA 50/200)","Kurs unter beiden, EMA 50 unter EMA 200",1,10],
 ["Struktur (SMC)","Tiefere Hochs und tiefere Tiefs, noch kein Change of Character",3,20],
 ["RSI Tag/Woche","Tag aus 23 auf 42 erholt, Woche 38, kein intakter Trend",6,15],
 ["A/D Tag/Woche","Tag: bullische Divergenz. Woche: fällt mit dem Kurs",10,20],
 ["Smart Money","Start 3, keine Insider-Käufe, kein Rückkauf, Grossaktionär verkauft und Leerverkäufer −1",2,10],
 ["Saisonalität","Zu wenig Daten (seit 2024)",2,5]
],
"pro": [
 "Weltmarktführer bei Getrieben für Kettenfahrzeuge, Rekord-Auftragsbestand 7.4 Mrd. €.",
 "Lieferungen sind weit hinaus gebucht: KNDS-Auftrag für Leopard-2-Getriebe bis 2032, US-Rahmenvertrag bis zu 691 Mio. $.",
 "Analysten erwarten 2027 rund +18 % Umsatz, auf diese Gewinne gerechnet ist das KGV nur rund 18.",
 "Schulden moderat (1.4), Kredite günstiger refinanziert, Gleitlager-Verkauf bringt Geld.",
 "Tages-A/D steigt bei tieferem Kurs: Es wird wieder gekauft."
],
"con": [
 "Das Wachstum ist 2026 fast stehen geblieben (+2.7 % im 1. Halbjahr), die neue Prognose liegt eher am unteren Ende.",
 "Das Gewinnziel 2027 lag schon im November 2025 unter den Erwartungen.",
 "Angebotsdruck: KNDS hat verkauft und hält noch 10 %, dazu rund 5 % Leerverkäufer.",
 "Hohe Abhängigkeit von Landfahrzeugen, die bei einem Frieden in der Ukraine als Erste leiden würden.",
 "Klarer Abwärtstrend auf beiden Zeitebenen, keine Insider-Käufe am Tief."
],
"todo": [
 ["t","Beobachten","Alarm bei 42.80 € (Trigger) und 35.70 € (oberes Ende Kaufzone 1)."],
 ["s","Timing grün","Tagesschluss über 42.80 € mit weiter steigender A/D. Fundamental: Die Q3-Zahlen am 5.11. müssen zeigen, dass das Wachstum im 2. Halbjahr anzieht (Umsatz über dem Vorjahr von 308 Mio. €, Auftragseingang hoch)."],
 ["r","Abbruch","Wochenschluss unter 33 €. Dann wäre die Kaufzone 2 (29 bis 31.20 €) das nächste Ziel."],
 ["","Nächste Zahlen","9 Monate 2026 am 5. November 2026. Jahreszahlen 2026 und Prognose 2027 voraussichtlich im März 2027."]
],
"bands": [{"from":47,"to":50,"type":"res"},{"from":38.9,"to":42.8,"type":"res"},{"from":33.5,"to":35.7,"type":"sup"},{"from":29,"to":31.2,"type":"sup"}],
"refs": [{"v":42.8,"label":"Trigger 42.8"}],
"sources": L("https://de.marketscreener.com/kurs/aktie/RENK-GROUP-AG-160066728/finanzen/","MarketScreener") + " (Stand 23.10.2026), " + L("https://www.tipranks.com/stocks/de:r3nk/financials/ratios","TipRanks Kennzahlen") + ", " + L("https://www.produktion.de/ruestung-aerospace/renk-rekordjahr-dank-boomendem-verteidigungsgeschaeft/2622002","Renk Geschäftsjahr 2025") + ", " + L("https://www.kapitalmarktexperten.de/renk-group-aktie-auftragsbestand-auf-74-milliarden/","Renk H1 2026") + ", " + L("https://goldesel.de/aktien/news/renk-grounpv-aktie-jpmorgan-senkt-kursziel-auf-50-euro-halt-an-overweight-fest","Neue Prognose und JPMorgan (22.10.2026)") + ", " + L("https://stock3.com/news/renk-stellt-neue-langfristziele-vor-ebit-prognose-2027-unter-erwartungen-16805410","Kapitalmarkttag 2025") + ", " + L("https://www.boerse-express.com/news/articles/renk-aktie-knds-verkauft-58-millionen-aktien-925841","KNDS-Verkauf") + ", " + L("https://www.boerse-global.de/renk-group-aktie-leerverkaeufer-greifen-zu/830620","Leerverkäufer (4.10.2026)") + ". Im Branchenvergleich der App ist Renk noch nicht enthalten."
}
if __name__ == "__main__":
    json.dump(c, open(os.path.join(P, "config", "R3NK.json"), "w"), ensure_ascii=False, indent=1)
    print("ok", sum(r[2] for r in c["Q"]), sum(r[2] for r in c["T"]))
