import json, os, sys
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, P)
from helpers import L, ADW, RSIW, SEAS
c = {
"ticker": "DRO", "name": "DroneShield", "datum": "04.11.2026", "waehrung": "AUD", "land": "Australien",
"meta": "DroneShield Ltd · ASX: DRO (in Australischen Dollar) · Drohnenabwehr: Geräte zum Erkennen und Stören von Drohnen, dazu Software im Abo · Sydney, Australien",
"price": "1.21 AUD",
"pricemeta": "Schluss 04.11.2026 · 52 Wochen: 1.21 bis 4.81 AUD · Allzeithoch rund 6.70 AUD (Oktober 2025) · sehr starke Kursschwankungen",
"verdict": "DroneShield wächst schnell: Umsatz 2025 plus 276 % auf 216.5 Mio. AUD, im 1. Halbjahr 2026 plus 74 %. Aber die Firma verdient kein Geld mehr: Im 1. Halbjahr 2026 stand ein Verlust von 32.2 Mio. AUD, und die Kasse schrumpfte in sechs Monaten von 210.6 auf 180 Mio. AUD. Dazu kommen die Aktienverkäufe des früheren Chefs im November 2025 (49.5 Mio. AUD) und eine laufende Untersuchung der Aufsicht ASIC. Die Aktie fiel vom Hoch (rund 6.70 AUD) auf 1.21 AUD, minus 82 %. Qualität orange (39), Timing rot (16). Bewertet nach Umsatz ist sie so günstig wie seit Jahren nicht (KUV rund 4 statt rund 11), der Abwärtstrend ist aber voll intakt.",
"about": "DroneShield aus Sydney baut Geräte, die feindliche Drohnen erkennen und mit Funkstörung zur Landung oder Umkehr zwingen: tragbare Störsender wie das «DroneGun», Sensoren für Fahrzeuge und feste Anlagen, und die Software «DroneSentry» mit künstlicher Intelligenz. Dazu kommt Software im Abo (SaaS, Updates für die Erkennung neuer Drohnentypen). Kunden sind vor allem Armeen: Im 1. Halbjahr 2026 kamen 85 % des Umsatzes von Militärkunden, 52 % aus Europa und Grossbritannien, 17 % aus den USA, 9 % aus dem Raum Asien-Pazifik. Die Firma hat 519 Mitarbeitende (Ende September 2026) und keine Schulden. Das Geschäft ist sprunghaft: Einzelne Grossaufträge bewegen den Umsatz eines Quartals stark.",
"why": "2025 stieg die Aktie um rund das Zehnfache, von 0.58 AUD im Februar auf ein Wochenhoch von 6.70 AUD Anfang Oktober. Vom 6. bis 12. November 2025 verkaufte der damalige Chef Oleg Vornik alle seine 14.81 Mio. Aktien für 49.5 Mio. AUD, zusammen mit Präsident Peter James und Verwaltungsrat Jethro Marks waren es fast 70 Mio. AUD. Kurz davor hatte DroneShield eine Meldung falsch als neuen Auftrag bezeichnet. Am 13.11.2025 fiel die Aktie um bis zu 31 %. Im Januar 2026 stieg sie mit dem Krieg im Nahen Osten wieder auf 4.81 AUD. Am 8.4.2026 trat Vornik ab, neuer Chef ist Angus Bean. Im Mai 2026 machte DroneShield publik, dass die Aufsicht ASIC die Meldungen und den Aktienhandel vom November 2025 untersucht. Am 28.7. nannte die Firma eine Umsatzprognose 2026 von 250 bis 270 Mio. AUD, Analysten hatten 323 Mio. erwartet. Am 26.8. folgte ein Halbjahresverlust von 32.2 Mio. AUD und eine tiefere Bruttomarge (60 statt 65 %). Am 15.10. lagen die festen Aufträge für 2026 bei 261 Mio. AUD, also nur in der Mitte der Prognose. Am 2.11. fiel die Aktie auf ein neues Jahrestief, heute schloss sie bei 1.21 AUD (minus 7.6 % zum Vortag). Für den Tagesverlust vom 4.11. habe ich keine Firmenmeldung gefunden.",
"kpis": [
 ["g","Umsatzwachstum","+74 %","1. Halbjahr 2026 (125.8 Mio. AUD). Für das ganze Jahr 2026 erwartet die Firma aber nur 250 bis 270 Mio. AUD, das sind +15 bis 25 %. Das 2. Halbjahr dürfte damit gleich hoch oder tiefer ausfallen als 2025 (144.2 Mio. AUD)."],
 ["r","Operative Marge","negativ","Die Firma verdient operativ kein Geld. 1. Halbjahr 2026: bereinigter Betriebsgewinn vor Abschreibungen (EBITDA) −12.4 Mio. AUD, Nettoverlust −32.2 Mio. AUD (−26 % vom Umsatz). 2025 lag die operative Marge bei −1.9 %."],
 ["r","Gewinn pro Aktie (EPS)","−0.03 AUD","Letzte 12 Monate, selbst gerechnet: rund −30.8 Mio. AUD Verlust geteilt durch rund 0.93 Mrd. Aktien. 2025 waren es knapp +0.004 AUD (Gewinn 3.5 Mio. AUD)."],
 ["w","Feste Aufträge","261 Mio. AUD","«Committed revenue» für 2026 am 12.10.2026: Aufträge, die unterschrieben sind und 2026 Umsatz werden. Für 2027 sind erst 29 Mio. AUD fest, für später 17 Mio. Die «Pipeline» von rund 2.2 Mrd. AUD (Mai 2026) sind nur Chancen, keine Aufträge."],
 ["w","Netto-Cash","180 Mio. AUD","Geld und Festgeld am 30.6.2026, keine Schulden. Aber in sechs Monaten flossen 30.6 Mio. AUD ab (210.6 auf 180 Mio.). Neue Zahlen zur Kasse gibt es erst mit dem Jahresbericht."],
 ["r","Verwässerung","+130 %","So viel mehr Aktien gibt es heute (rund 0.92 bis 0.96 Mrd.) als im Schnitt 2021 (398 Mio.). 2024 holte DroneShield über Kapitalerhöhungen rund 220 Mio. AUD, zuletzt 120 Mio. zu 1.15 AUD pro Aktie. Jede Aktie besitzt einen immer kleineren Teil der Firma."],
 ["g","Kurs-Umsatz-Verhältnis (KUV)","4.2","Weil es keinen Gewinn gibt, vergleiche ich Börsenwert (rund 1.13 Mrd. AUD) und Jahresumsatz (270 Mio. AUD). Du zahlst also gut 4 Jahresumsätze. Geschätzter Schnitt 2023 bis 2025: rund 11. Also rund 60 % günstiger als üblich."],
 ["w","Dividende","keine","DroneShield hat nie eine Dividende bezahlt und plant laut Firma (August 2026) auch keine. Das Geld fliesst ins Wachstum."]
],
"revtitle": "Umsatz pro Quartal (Mio. AUD)", "revunit": "Mio. AUD", "epsunit": "AUD",
"revnote": "Sehr sprunghaft. Q2 25 und Q2 26 selbst gerechnet aus Halbjahr minus Quartal. Für Q3 26 gibt es keine Zahl: Seit Mai 2026 muss DroneShield keine Quartalsberichte mehr veröffentlichen. Das Rekordquartal Q3 25 (92.9 Mio. AUD) war ein grosser Einzelauftrag.",
"marginnote": "Operativer Gewinn geteilt durch Umsatz. Nur 2023 positiv. Für das 1. Halbjahr 2026 liegt keine vergleichbare Zahl vor, der Nettoverlust betrug −26 % vom Umsatz.",
"finnote": "<b>Hinweis:</b> Geschäftsjahr = Kalenderjahr. Werte 2021 bis 2023 nach StockAnalysis, 2024 und 2025 nach FactSet (finanzen.net) und Firmenmeldungen. «Letzte 12 Mt.» bis 30.6.2026 selbst gerechnet (2025 minus 1. Halbjahr 2025 plus 1. Halbjahr 2026). Free Cashflow 2025 und für die letzten 12 Monate nicht verifiziert (operativer Cashflow 2025: +15.9 Mio. AUD, im 1. Halbjahr 2026 sank die Kasse um 30.6 Mio.). Keine sinnvolle Rendite auf das Kapital (ROIC), weil kaum Gewinn. KUV = Börsenwert geteilt durch Umsatz, Werte geschätzt aus Kurs und ungefährer Aktienzahl (2023: Kurs Ende Februar 2024).",
"FIN": [["2021",10.6,"+90.7 %","−61.1 %","−0.01",-6.8,"–","–"],["2022",16.9,"+59.3 %","−18.3 %","−0.00",-2.6,"–","–"],["2023",54.2,"+221 %","+5.0 %","0.02",7.8,"–","rund 9"],["2024",57.5,"+6 %","−23.5 %","−0.00",-68.6,"–","rund 11"],["2025",216.5,"+276 %","−1.9 %","0.004","–","–","rund 13"],["Letzte 12 Mt.",270.0,"–","negativ","−0.03","negativ","negativ","4.2"]],
"QREV": [["Q4 24",26.4],["Q1 25",33.5],["Q2 25",38.8],["Q3 25",92.9],["Q4 25",51.3],["Q1 26",74.1],["Q2 26",51.7]],
"revdec": 1,
"MARGIN": [["2021",-61.1],["2022",-18.3],["2023",5.0],["2024",-23.5],["2025",-1.9]],
"Q": [
 ["Umsatztrend","Halbjahre: H1 25, H2 25 und H1 26 klar über Vorjahr. Laut Prognose (250 bis 270 Mio.) liegt H2 26 bei 124 bis 144 Mio. AUD, also gleich oder unter H2 25 (144.2 Mio.). Wachstum bremst stark ab. Q3 26 nicht veröffentlicht",8,15],
 ["Wachstumstempo","Firmenprognose 2026: +15 bis 25 %",10,10],
 ["Operative Marge","Negativ (0 Pkt.). Seit 2021 besser geworden, aber 2024 und 2026 wieder tief im Minus: schwankend (2 Pkt.)",2,15],
 ["Gewinnwachstum (EPS)","Letzte 12 Monate Verlust von rund −0.03 AUD pro Aktie",0,10],
 ["Free Cashflow","In 4 der letzten 5 Jahre negativ oder nicht belegt, im 1. Halbjahr 2026 sank die Kasse um 30.6 Mio. AUD",0,10],
 ["ROIC","Wegen Verlusten negativ",2,15],
 ["Schulden","Keine Schulden, 180 Mio. AUD Geld (Netto-Cash)",10,10],
 ["Bewertung vs. eigene Historie","Verlustfirma, darum KUV: 4.2 statt geschätzt rund 11 (2023 bis 2025), über 30 % günstiger. Maximal 7 Punkte",7,15]
],
"adwnote": ADW + "Die Wochen-A/D fällt seit Juli 2026 mit dem Kurs: Anfang August −408, Ende September −541, heute −601. Kein Zeichen, dass grosse Käufer einsteigen.",
"rsiwnote": RSIW + "Ende Juli bei 32 (Kurs 1.70 AUD), heute bei 31.6, obwohl der Kurs 29 % tiefer steht. Eine kleine positive Abweichung, aber noch kein Bodensignal.",
"addnote": "Negativ. Beim Tief vom 15.10. (1.42 AUD Schluss) stand die Tages-A/D bei −210, heute bei −230. Neue Kurstiefs gehen mit neuen A/D-Tiefs einher: Die Verkäufer bestimmen das Bild.",
"ind": [
 ["Kurs vs. EMA 50","1.21 &lt; 1.61","1.21 &lt; 2.37","Auf beiden Zeitebenen klar darunter."],
 ["Kurs vs. EMA 200","1.21 &lt; 2.32","1.21 &lt; 1.79","Auch unter der langfristigen Linie, Woche rund 32 % darunter."],
 ["EMA 50 vs. EMA 200","50 unter 200 (seit 17.6.2026)","50 über 200 (seit November 2022), Abstand schrumpft schnell","Tag klar abwärts, die Woche zeigt noch den alten Aufwärtstrend, kippt aber."],
 ["RSI (14)","25.3","31.6","Tag überverkauft ohne Abweichung, Woche knapp über 30 mit kleiner positiver Abweichung."],
 ["A/D","fällt mit dem Kurs auf neue Tiefs","fällt mit dem Kurs","Beide Zeitebenen negativ."],
 ["Volumen","Ø 20 Tage 6.7 Mio. vs. Ø 100 Tage 10.4 Mio. Aktien","Weniger Handel als im Sommer, kein Ausverkauf mit hohem Volumen."]
],
"smc": "Seit dem Wochenhoch von 6.70 AUD (Anfang Oktober 2025) macht DroneShield tiefere Hochs: 4.81 AUD (Januar 2026), 4.72 AUD (März), 2.34 AUD (6.8.) und 1.86 AUD (2.10.). Auch die Tiefs fallen: 2.88 AUD (Februar), 1.65 AUD (3.8.), 1.54 AUD (28.9.), 1.41 AUD (15.10.). Mit dem Schluss bei 1.21 AUD am 4.11. ist auch das Panik-Tief vom November 2025 (1.62 AUD) deutlich gebrochen. Das ist eine klare Abwärtsstruktur ohne Change of Character. Im Tageschart war das letzte tiefere Hoch am 30.10. bei 1.51 AUD. Die nächste Haltestelle darunter ist der Bereich vom April und Mai 2025 (Wochenschlüsse 1.09 bis 1.21 AUD, Tief 1.16 AUD am 19.5.2025) und der Preis der Kapitalerhöhung vom Juli 2024 (1.15 AUD). Darunter liegt erst wieder die Zone 0.79 bis 0.90 AUD vom März und April 2025.",
"zones": [
 ["r","1.77 bis 1.86 AUD","Widerstand: Hochs vom 17.9. (1.77 AUD) und 2.10. (1.86 AUD)."],
 ["r","1.41 bis 1.52 AUD","Widerstand: gebrochene Tiefs vom 15./16.10. (1.41 AUD) und Hoch vom 30.10. (1.51 AUD)."],
 ["t","1.52 AUD","<b>Trigger:</b> Tagesschluss über dem letzten tieferen Hoch vom 30.10. (1.51 AUD). Dann wäre der erste Change of Character im Tageschart da."],
 ["s","1.09 bis 1.20 AUD","<b>Kaufzone 1:</b> Wochenschlüsse von März bis Mai 2025, Tief vom 19.5.2025 (1.16 AUD) und Preis der Kapitalerhöhung 2024 (1.15 AUD)."],
 ["s","0.79 bis 0.90 AUD","<b>Kaufzone 2:</b> Tief vom April 2025 (0.79 AUD) und Wochenschlüsse von März und April 2025 (0.88 bis 0.89 AUD)."],
 ["r","1.05 AUD","Abbruch: Wochenschluss unter 1.05 AUD. Dann wäre die Zone vom Frühling 2025 verloren."]
],
"smart": [
 "<b>Insider-Verkäufe:</b> Der frühere Chef Oleg Vornik verkaufte vom 6. bis 12.11.2025 alle 14.81 Mio. Aktien für 49.5 Mio. AUD (rund 3.34 AUD pro Aktie). Mit Präsident Peter James und Verwaltungsrat Jethro Marks zusammen fast 70 Mio. AUD. Die Aufsicht ASIC untersucht diese Tage seit Mai 2026, ein Ergebnis gibt es noch nicht. Vornik ist seit April 2026 nicht mehr Chef, James seit Mai nicht mehr Präsident.",
 "<b>Insider-Käufe:</b> Keine freien Käufe am Markt gefunden. Neue Aktien für Manager kommen nur aus Optionen und Leistungsrechten (zuletzt 250'000 Stück Ende Oktober 2026, ohne Zahlung).",
 "<b>Rückkäufe und Verwässerung:</b> Keine Rückkäufe. Die Aktienzahl stieg seit 2021 um rund 130 %, vor allem durch Kapitalerhöhungen 2024 (rund 100 und 120 Mio. AUD).",
 "<b>Grosse Investoren und Leerverkäufer:</b> JPMorgan meldete Ende Juli 2026 einen Anteil von 6.68 % (61.7 Mio. Aktien). Solche Meldungen grosser Banken hängen oft mit verliehenen Aktien zusammen. DroneShield gehört laut Daten der ASIC zu den am stärksten leerverkauften Aktien Australiens (Leerverkäufer wetten auf fallende Kurse).",
 "<b>Analysten:</b> Im Schnitt «Halten», mittleres Kursziel 1.96 AUD (Spanne 1.25 bis 2.60 AUD, Stand 2.11.2026). Canaccord Genuity Kaufen mit Ziel 2.60 AUD (16.10.), Jefferies Verkaufen mit Ziel 1.25 AUD (Mitte Oktober gesenkt von 1.45 AUD)."
],
"seasnote": SEAS + "Daten seit 2016, also nur 8 bis 11 Jahre. November (−3.3 %, 36 % positive Jahre) und Dezember (+3.7 %, aber nur 38 % positive Jahre) sind meist schwach, Januar ausgeglichen (+1.6 %, 50 %).",
"T": [
 ["Trend Woche (EMA 50/200)","Kurs klar unter beiden (32 % unter EMA 200), EMA 50 noch über 200, fällt aber steil",3,20],
 ["Trend Tag (EMA 50/200)","Kurs unter beiden, EMA 50 unter 200 seit 17.6.2026",1,10],
 ["Struktur (SMC)","Tiefere Hochs und tiefere Tiefs, Tief vom November 2025 gebrochen, kein Change of Character",1,20],
 ["RSI Tag/Woche","Tag 25 ohne Bodenzeichen, Woche 32 mit kleiner positiver Abweichung",6,15],
 ["A/D Tag/Woche","Beide fallen mit dem Kurs auf neue Tiefs",3,20],
 ["Smart Money","Start 3, gehäufte Insider-Verkäufe November 2025 (fast 70 Mio. AUD) −2, keine Käufe, kein Rückkauf, viele Leerverkäufer",1,10],
 ["Saisonalität","November 36 %, Dezember 38 %, Januar 50 % positive Jahre",1,5]
],
"pro": [
 "Starke Nachfrage nach Drohnenabwehr: Umsatz 2025 +276 %, 1. Halbjahr 2026 +74 %, eine Pipeline in über 60 Ländern.",
 "Keine Schulden und 180 Mio. AUD Geld (Juni 2026). Beim Verbrauch des 1. Halbjahres (30.6 Mio. AUD) reicht das rund drei Jahre (selbst gerechnet).",
 "Feste Aufträge von 261 Mio. AUD für 2026 decken die Prognose zur Mitte ab. Die Pipeline lag im Mai bei 2.2 Mrd. AUD, darunter ein Projekt über 750 Mio. US-Dollar in Verhandlung.",
 "Software im Abo wächst schnell (+229 % auf 11.5 Mio. AUD im 1. Halbjahr) und bringt planbare Einnahmen.",
 "Nach Umsatz bewertet so günstig wie seit Jahren nicht: KUV rund 4 statt rund 11."
],
"con": [
 "Verlust statt Gewinn: −32.2 Mio. AUD im 1. Halbjahr 2026, die Kosten stiegen um 122 %, die Kasse schrumpfte um 30.6 Mio. AUD.",
 "Das Wachstum bremst stark: Prognose 2026 nur +15 bis 25 %, für 2027 sind erst 29 Mio. AUD Aufträge fest.",
 "Vertrauensfrage: Der frühere Chef verkaufte alle Aktien kurz vor dem Absturz, die Aufsicht ASIC ermittelt, Chef, Präsident und Finanzchef sind neu.",
 "Starke Verwässerung: rund 130 % mehr Aktien seit 2021. Weitere Kapitalerhöhungen sind möglich, falls das Geld knapp wird.",
 "Seit Mai 2026 keine Quartalsberichte mehr. Anleger sehen Umsatz und Kasse nur noch zweimal im Jahr, das erhöht die Unsicherheit."
],
"todo": [
 ["t","Beobachten","Alarm bei 1.52 AUD (Trigger) und 1.20 AUD (oberes Ende Kaufzone 1)."],
 ["s","Timing grün","Erst ein Tagesschluss über 1.52 AUD mit steigender A/D würde den Abwärtstrend erstmals brechen. Oder eine Bodenbildung in 1.09 bis 1.20 AUD, die über 1.05 AUD hält. Fundamental: Die Jahreszahlen müssen zeigen, dass der Verlust schrumpft und die Kasse nicht weiter fällt. Wichtig sind auch neue feste Aufträge für 2027 und das Ergebnis der ASIC-Untersuchung."],
 ["r","Abbruch","Wochenschluss unter 1.05 AUD. Dann wäre die Kaufzone 2 (0.79 bis 0.90 AUD) das nächste Ziel."],
 ["","Nächste Zahlen","Jahreszahlen 2026 voraussichtlich Ende Februar 2027 (2025: am 25.2.2026), Datum noch nicht bestätigt. Möglich ist ein Zwischenbericht im Januar 2027. Quartalsberichte gibt es seit Mai 2026 nicht mehr."]
],
"bands": [{"from":1.77,"to":1.86,"type":"res"},{"from":1.41,"to":1.52,"type":"res"},{"from":1.09,"to":1.20,"type":"sup"},{"from":0.79,"to":0.90,"type":"sup"}],
"refs": [{"v":1.52,"label":"Trigger 1.52"}],
"sources": L("https://stockanalysis.com/quote/fra/DRH/financials","StockAnalysis.com") + " (Jahre 2020 bis 2024), " + L("https://www.finanzen.net/bilanz_guv/droneshield","finanzen.net Bilanz (FactSet)") + " (Stand 4.11.2026), " + L("https://www.fool.com.au/2026/02/25/droneshield-share-price-lifts-off-on-367-full-year-profit-surge/","Motley Fool: Jahreszahlen 2025 (25.2.2026)") + ", " + L("https://cfotech.co.uk/story/droneshield-posts-record-half-year-revenue-as-losses-grow","CFOtech: Halbjahr 2026 (26.8.2026)") + ", " + L("https://smallcaps.com.au/article/droneshield-logs-dollar261m-in-committed-revenue-as-counter-drone-business-scales","Small Caps: feste Aufträge 261 Mio. (15.10.2026)") + ", " + L("https://securitybrief.co.uk/story/droneshield-quarterly-revenue-jumps-121-to-aud-74-1m","SecurityBrief: Q1 2026") + ", " + L("https://www.listcorp.com/asx/dro/droneshield-limited/news/quarterly-activities-appendix-4c-cash-flow-report-3305921.html","Quartalsbericht Q4 2025 (27.1.2026)") + ", " + L("https://www.boerse-express.com/news/articles/droneshield-aktie-berichtspflichten-entfallen-ab-mai-907669","Börse Express: keine Quartalsberichte mehr (21.5.2026)") + ", " + L("https://www.fool.com.au/2025/11/13/why-is-the-droneshield-share-price-crashing-31-on-thursday","Motley Fool: CEO-Verkäufe (13.11.2025)") + ", " + L("https://www.investordaily.com.au/droneshield-under-asic-investigation/","InvestorDaily: ASIC-Untersuchung") + ", " + L("https://finanzen.net/nachricht/aktien/erwartungen-gegen-margen-droneshield-aktie-warum-selbst-volle-auftragsbuecher-nicht-ueberzeugen-00-16029146","finanzen.net: Analysten (2.11.2026)") + ", " + L("https://thebull.com.au/news/droneshield-shares-make-new-low-as-pressure-mounts/","The Bull (3.11.2026)") + ", " + L("https://www.boerse-express.com/news/articles/droneshield-aktie-232-millionen-auftrag-aus-europa-935929","Börse Express: JPMorgan-Anteil (5.8.2026)") + ", " + L("https://www.boerse-express.com/news/articles/droneshield-aktie-us750-millionen-deal-in-verhandlung-900413","Börse Express: Pipeline (1.5.2026)") + "."
}
if __name__ == "__main__":
    json.dump(c, open(os.path.join(P, "config", "DRO.json"), "w"), ensure_ascii=False, indent=1)
    print("ok", sum(r[2] for r in c["Q"]), sum(r[2] for r in c["T"]))
