import json, os, sys
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, P)
from helpers import L, ADW, RSIW, SEAS
c = {
"ticker": "BKNG", "name": "Booking Holdings", "datum": "15.10.2026", "waehrung": "USD", "land": "USA",
"meta": "Booking Holdings Inc. · NASDAQ: BKNG · Online-Reisebuchung (Booking.com, Priceline, Agoda, KAYAK, OpenTable) · Norwalk, USA",
"price": "165.80 $",
"pricemeta": "Schluss 15.10.2026 · 52 Wochen: 150.14 – 220.81 $ · Allzeithoch 233.58 $ im Juli 2025 (nach Aktiensplit 25:1 vom April 2026)",
"verdict": "Booking verdient sehr gut: 9.5 Mrd. $ Free Cashflow (34 % vom Umsatz), und fast alles geht an die Aktionäre zurück. Seit 2021 gibt es 27 % weniger Aktien. Die Börse fürchtet aber, dass KI-Assistenten von Google, OpenAI und Meta die Reisebuchung übernehmen. Darum fiel die Aktie seit August um 28 % auf 165.80 $, das KGV liegt bei 18 statt rund 29. Qualität grün (89), Timing gelb (55). Seit Februar hält der Boden bei 150 bis 155 $ dreimal, und die A/D zeigt beim letzten Tief mehr Käufe als vorher.",
"about": "Booking Holdings ist die grösste Online-Reisefirma der Welt. Booking.com vermittelt Hotels, Ferienwohnungen, Flüge und Mietautos, dazu kommen Priceline (USA), Agoda (Asien), KAYAK (Preisvergleich) und OpenTable (Restaurant-Reservationen). Booking verdient vor allem eine Provision pro Buchung, rund 15 % vom Zimmerpreis. Im 2. Quartal 2026 liefen Buchungen für 51 Mrd. $ über die Plattformen, 325 Mio. Übernachtungen. Rund zwei Drittel der Kunden kommen direkt (App oder Webseite), nicht über Google.",
"why": "Die Aktie fiel vom Hoch im Juli 2025 (233.58 $) zuerst bis 150.14 $ am 15. Mai 2026: Im Februar und April senkte Booking den Ausblick, der Krieg im Nahen Osten bremste Fernreisen, und KI-Assistenten wurden zur Angst Nummer eins. Nach starken Zahlen im August stieg sie bis 217.32 $. Dann folgten acht Wochen mit Verlusten in Folge, so viele wie noch nie seit dem Börsengang 1999: Am 8. September startete Meta den KI-Assistenten Muse, der Reisen bucht (−6.7 %). Am 9. September bestätigte ein EU-Gericht das Verbot der Übernahme von eTraveli (−3.8 %). Am 23. September ging Konkurrent Expedia eine Partnerschaft mit Muse ein, Booking nicht (−5.1 %). Anfang Oktober berichtete Reuters über eine mögliche Klage der US-Behörde FTC (über 500 Mio. $). Am 14. Oktober gründete Booking die eigene KI-Firma Vayo, die Aktie stieg an zwei Tagen um 5 %. Wichtig: Bisher kommen laut Booking deutlich unter 1 % der Buchungen über KI-Assistenten.",
"kpis": [
 ["w","Umsatzwachstum","+12.9 %","Letzte 12 Monate. Ohne Währungseffekte im 2. Quartal nur rund 7 %. Für 2026 erwartet Booking ein Wachstum im hohen einstelligen Bereich."],
 ["g","Operative Marge","34.9 %","Von 100 $ Umsatz bleiben rund 35 $ Betriebsgewinn. Seit 2021 von 24 % stark gestiegen, ein Sparprogramm (650 Mio. $ bis Ende 2027) hilft weiter."],
 ["g","Gewinn pro Aktie (EPS)","9.05 $","Letzte 12 Monate nach offiziellen Regeln. Bereinigt 2025 9.12 $ (+22 %), für 2026 erwartet Booking +12 bis +15 %."],
 ["g","ROIC","92 %","Auf 100 $ investiertes Kapital rund 92 $ Gewinn. Extrem hoch, auch weil das Eigenkapital wegen der Rückkäufe negativ ist."],
 ["g","Free Cashflow","9.5 Mrd. $","Letzte 12 Monate, 34 % vom Umsatz. Seit 2021 fast vervierfacht. Nur 6 % davon sind Löhne in Aktien: Der FCF ist echt."],
 ["g","Nettoschulden","3.4 Mrd. $","In 0.4 Jahren mit dem FCF bezahlt. Das Eigenkapital ist negativ (−10.8 Mrd. $), weil Booking mehr Aktien zurückkaufte als es Gewinn behielt. Kein Verlustproblem."],
 ["g","KGV","18.3","Du zahlst 18 Jahresgewinne. Eigener Schnitt 2022–2025: rund 28.6. Also rund 36 % günstiger als üblich, das KGV ist das tiefste seit über 10 Jahren."],
 ["w","Dividende","1.0 %","0.42 $ pro Quartal, 4× pro Jahr. Erst seit 2024, zuletzt +9.4 %. Zusammen mit den Rückkäufen gibt Booking rund 5 % des Börsenwerts pro Jahr zurück."]
],
"revtitle": "Umsatz pro Quartal (Mio. $)", "revunit": "Mio. $", "epsunit": "$",
"revnote": "Alle 8 Quartale über dem Vorjahr. Achtung Saison: Das 3. Quartal (Sommer) ist immer das grösste, das 1. das kleinste. Im 2. Quartal 2026 nur noch +8 %.",
"marginnote": "Von 24 % (2021, Corona-Erholung) auf rund 35 % gestiegen.",
"finnote": "<b>Hinweis:</b> Aktiensplit 25:1 am 2. April 2026, alle Werte pro Aktie sind angepasst. 2025 drückten ein Währungsverlust (1.4 Mrd. $) und eine Abschreibung auf KAYAK den offiziellen Gewinn. Das KGV-Mittel ist über 2022–2025 gerechnet, weil 2021 (KGV 85) noch von Corona verzerrt war.",
"FIN": [["2021",10958,"+61.2 %","24.0 %",1.13,2516,"32.6 %","84.6"],["2022",17090,"+56.0 %","28.5 %",3.05,6186,"75.4 %","25.6"],["2023",21365,"+25.0 %","27.7 %",4.70,6999,"63.5 %","28.9"],["2024",23739,"+11.1 %","32.0 %",6.91,7894,"53.1 %","28.0"],["2025",26917,"+13.4 %","35.2 %",6.62,9087,"60.9 %","31.9"],["Letzte 12 Mt.",28241,"+12.9 %","34.9 %",9.05,9539,"92.5 %","18.3"]],
"QREV": [["Q3 24",7994],["Q4 24",5471],["Q1 25",4762],["Q2 25",6798],["Q3 25",9008],["Q4 25",6349],["Q1 26",5532],["Q2 26",7352]],
"revdec": 0,
"MARGIN": [["2021",24.0],["2022",28.5],["2023",27.7],["2024",32.0],["2025",35.2],["12 Mt.",34.9]],
"Q": [
 ["Umsatztrend","4 von 4 Quartalen über Vorjahr, zuletzt aber nur noch +8 %",12,15],
 ["Wachstumstempo","Ohne Währungseffekte rund 7 bis 10 %, Ausblick 2026 hoch einstellig",6,10],
 ["Operative Marge","34.9 % (9 Pkt.), seit 2021 klar steigend (6 Pkt.)",15,15],
 ["Gewinnwachstum (EPS)","Bereinigt 2025 +22 %, Ausblick 2026 +12 bis +15 %",8,10],
 ["Free Cashflow","Jedes Jahr seit 2021 gestiegen",10,10],
 ["ROIC","Über 60 %, zuletzt 92 %",15,15],
 ["Schulden","Nettoschulden/EBITDA rund 0.3",9,10],
 ["Bewertung vs. eigene Historie","KGV 18.3 statt Ø 28.6 (2022–2025), rund 36 % günstiger",14,15]
],
"adwnote": ADW + "Wichtig: Beim Tief im Mai (Wochenschluss 154.13 $) stand die Wochen-A/D bei 499.4. Beim Tief Anfang Oktober (Wochenschluss 159.02 $) lag sie mit 498.9 gleich, heute bei 526.9. Bei ähnlichem Kurs wird eher gekauft als im Mai.",
"rsiwnote": RSIW + "Im Februar bei 29 (überverkauft), im August bei 65, heute 42: schwach, aber nicht überverkauft.",
"addnote": "Bullische Divergenz: Am 23.9. fiel der Kurs auf 155.37 $ bei einer A/D von 70.2. Am 5.10. fiel er tiefer auf 154.06 $, die A/D lag aber höher bei 72.7, heute bei 76.6. Trotz tieferem Kurs wurde mehr gekauft.",
"ind": [
 ["Kurs vs. EMA 50","165.8 &lt; 173.6","165.8 &lt; 183.6","Unter der mittelfristigen Linie, auf beiden Zeitebenen."],
 ["Kurs vs. EMA 200","165.8 &lt; 182.7","165.8 &gt; 164.4 (knapp)","Woche knapp über der langfristigen Linie."],
 ["EMA 50 vs. EMA 200","50 unter 200 (seit 23.9.2026)","50 über 200 (seit 2020)","Tag abwärts, Woche noch aufwärts."],
 ["RSI (14)","48.3","42.5","Tag: tieferes Kurstief am 5.10., aber höheres RSI-Tief (29.8 statt 21.4): bullische Divergenz."],
 ["A/D","höher bei tieferem Kurs","höher als beim Mai-Tief","Auf beiden Zeitebenen positiv."],
 ["Volumen","Ø 20 Tage 8.4 Mio. vs. Ø 100 Tage 7.2 Mio. Aktien","Mehr Handel als üblich im Abverkauf."]
],
"smc": "Seit Februar 2026 läuft Booking in einer grossen Spanne zwischen rund 150 und 218 $. Die Tiefs liegen fast gleich hoch: 150.62 $ (23.2.), 150.14 $ (20.5.) und 154.06 $ (5.10.). Das ist ein dreifacher Boden mit leicht höherem letzten Tief. Die Hochs: 193.92 $ (April) und 217.32 $ (August). Seit August fiel der Kurs in einer klaren Abwärtsbewegung mit tieferen Hochs und Tiefen. Am 15.10. stieg er bis 168.49 $ und schloss bei 165.80 $, knapp unter dem Hoch vom 28.9. (166.19 $). Ein Tagesschluss darüber wäre ein erster Change of Character. Darüber warten die Tages-EMAs (173.60 und 182.70 $) und die Wochen-EMA 50 (183.60 $) als Widerstand.",
"zones": [
 ["r","204–218 $","Widerstand: Hochs vom August (217.32 $)."],
 ["r","173–184 $","Widerstand: Tages-EMA 50 (173.60 $), Tages-EMA 200 (182.70 $), Wochen-EMA 50 (183.60 $)."],
 ["t","167 $","<b>Trigger:</b> Tagesschluss über dem Hoch vom 28.9. (166.19 $). Bestätigung über 177 $ (Hoch vom 10.9.)."],
 ["s","150–158 $","<b>Kaufzone:</b> Dreifacher Boden 150.14 / 150.62 / 154.06 $ von Februar, Mai und Oktober."],
 ["r","150 $","Abbruch: Wochenschluss unter dem Tief vom Mai (150.14 $). Dann ist der Boden gebrochen."]
],
"smart": [
 "<b>Booking selbst:</b> Kaufte in den letzten 12 Monaten für 10.5 Mrd. $ Aktien zurück (rund 8.5 % des Börsenwerts), im 1. Halbjahr 2026 für 7.4 Mrd. $ zu rund 173 $. Restprogramm Ende Juni: 14.5 Mrd. $ (rund 12 % des Börsenwerts).",
 "<b>Insider:</b> In 12 Monaten keine Käufe, 32 Verkäufe für rund 60.5 Mio. $. CEO Glenn Fogel verkaufte regelmässig jeden Monat (rund 31 Mio. $, zuletzt im April), Finanzchef Steenbergen im August für 4.2 Mio. $ zu 211 $.",
 "<b>Analysten:</b> Mehrheit positiv. MarketBeat: 3× stark Kaufen, 26× Kaufen, 7× Halten, 1× Verkaufen, Kursziel im Schnitt 234 $ (170 bis 298 $). Seit Ende September senken mehrere Banken die Ziele: Truist 216 $, Wells Fargo 190 $, Cantor 170 $ (12.10.)."
],
"seasnote": SEAS + "27 Jahre Daten (seit 1999). Februar bis April und November sind stark, September der schwächste Monat (−4.9 %, nur 41 % positive Jahre). Oktober +1.6 % (56 %).",
"T": [
 ["Trend Woche (EMA 50/200)","Kurs knapp über EMA 200, unter EMA 50: Rücksetzer im Aufwärtstrend",12,20],
 ["Trend Tag (EMA 50/200)","Kurs unter beiden, EMA 50 unter 200 seit 23.9.",1,10],
 ["Struktur (SMC)","Spanne 150–218 $ mit dreifachem Boden, seit August tiefere Hochs",8,20],
 ["RSI Tag/Woche","Bullische Divergenz im Tageschart (Kurs tiefer, RSI höher), RSI dreht nach oben",12,15],
 ["A/D Tag/Woche","Auf beiden Zeitebenen höher bei gleichem oder tieferem Kurs",16,20],
 ["Smart Money","Start 3, Rückkauf über 8 % pro Jahr +3, viele Insider-Verkäufe −3",3,10],
 ["Saisonalität","Oktober 56 %, November 58 %, Dezember 46 % positive Jahre",3,5]
],
"pro": [
 "Grösste Reiseplattform der Welt mit 9.5 Mrd. $ echtem Free Cashflow (wenig Löhne in Aktien).",
 "Gibt fast alles an die Aktionäre zurück: rund 4 % weniger Aktien pro Jahr plus Dividende.",
 "Sehr günstig: KGV 18 statt rund 29, FCF-Rendite 7.7 %.",
 "Zwei Drittel der Kunden kommen direkt, KI-Assistenten bringen bisher unter 1 % der Buchungen.",
 "Boden bei 150 bis 155 $ hält, Tages-A/D und RSI zeigen bullische Divergenzen."
],
"con": [
 "KI-Assistenten (Google, OpenAI, Meta Muse) könnten Booking zum reinen Zulieferer machen. Expedia arbeitet mit Muse, Booking nicht.",
 "Wachstum wird langsamer: Übernachtungen nur noch +3 bis +5 % erwartet.",
 "Rechtliche Risiken: mögliche FTC-Klage (über 500 Mio. $), EU-Regeln, eTraveli-Verbot.",
 "Rückkäufe teils mit neuen Schulden bezahlt, Eigenkapital negativ.",
 "Insider verkaufen laufend und kaufen nie, Tagestrend klar abwärts."
],
"todo": [
 ["t","Beobachten","Alarm bei 167 $ (Trigger) und 158 $ (oberes Ende Kaufzone)."],
 ["s","Timing grün","Tagesschluss über 167 $, danach über 177 $ mit weiter steigender A/D. Oder ein erneuter Test von 150–158 $, der hält. Fundamental: Am 3.11. sollten die Übernachtungen am oberen Ende der Prognose (+5 %) liegen."],
 ["r","Abbruch","Wochenschluss unter 150 $. Dann ist der dreifache Boden gebrochen."],
 ["","Nächste Zahlen","3. November 2026 nach US-Börsenschluss (3. Quartal, bestätigt). Erwartet: bereinigter Gewinn 4.49 $ pro Aktie, Umsatz 9.54 Mrd. $."]
],
"bands": [{"from":204,"to":218,"type":"res"},{"from":173,"to":184,"type":"res"},{"from":150,"to":158,"type":"sup"}],
"refs": [{"v":167,"label":"Trigger 167"}],
"sources": L("https://stockanalysis.com/stocks/bkng/financials/","StockAnalysis.com") + " (Stand 15.10.2026), " + L("https://s201.q4cdn.com/865305287/files/doc_financials/2026/q2/Q2-26-BKNG-Earnings-Release-Final.pdf","Booking Q2 2026") + ", " + L("https://www.tikr.com/blog/booking-holdings-bkng-shares-drop-expedia-meta-muse-ai-partnership","TIKR: Expedia und Muse") + ", " + L("https://www.tikr.com/blog/booking-holdings-faces-ftc-action-over-hotel-ads-more-than-500-million-at-stake","TIKR: FTC") + ", " + L("https://geekwire.com/2026/booking-holdings-unveils-ai-travel-startup-vayo-based-in-seattle-with-a-planned-100m-investment","GeekWire: Vayo") + ", " + L("https://www.marketbeat.com/stocks/NASDAQ/BKNG/insider-trades/","Insider (MarketBeat)") + ", " + L("https://www.marketbeat.com/stocks/NASDAQ/BKNG/forecast/","Analysten (MarketBeat)") + "."
}
if __name__ == "__main__":
    json.dump(c, open(os.path.join(P, "config", "BKNG.json"), "w"), ensure_ascii=False, indent=1)
    print("ok", sum(r[2] for r in c["Q"]), sum(r[2] for r in c["T"]))
