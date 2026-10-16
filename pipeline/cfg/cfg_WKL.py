import json, os, sys
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, P)
from helpers import L, ADW, RSIW, SEAS
c = {
"ticker": "WKL", "name": "Wolters Kluwer", "datum": "16.10.2026", "waehrung": "EUR", "land": "Niederlande",
"meta": "Wolters Kluwer N.V. · Euronext Amsterdam: WKL · Fachinformationen und Software für Ärzte, Steuerberater, Juristen und Firmen · Alphen aan den Rijn, Niederlande",
"price": "81.64 €",
"pricemeta": "Stand 16.10.2026 · 52 Wochen: 54.64 – 115.15 € · Allzeithoch 181.30 € am 12.2.2025",
"verdict": "Wolters Kluwer ist eine Qualitätsfirma wie RELX: 85 % wiederkehrende Umsätze, Marge 29 %, Free Cashflow 1.4 Mrd. € und ein KGV von nur noch 15 statt rund 26. Die Aktie fiel vom Hoch 181.30 € (Februar 2025) auf 54.64 € (Juni 2026), weil die Börse fürchtet, dass KI wie Claude oder ChatGPT die teuren Fachdatenbanken ersetzt. Die Zahlen zeigen das bisher kaum: Wachstum 5 % statt 6 %. Qualität hellgrün (74), Timing gelb (52). Seit Juni hat die Aktie den Trend gedreht und ist um 49 % gestiegen, kurzfristig ist sie aber überkauft. Schwachpunkt nach deinem Schema: Rückkäufe und Dividende waren 2022 bis 2025 grösser als der Free Cashflow, die Schulden stiegen.",
"about": "Wolters Kluwer verkauft Fachwissen und Software im Abo. Health: UpToDate, das Nachschlagewerk für Ärzte in rund 2'500 US-Spitälern, und Medikamenten-Datenbanken. Tax & Accounting: Steuer- und Buchhaltungssoftware CCH Axcess für Treuhänder und Firmen. Financial & Corporate Compliance: Dienste für Banken und Firmengründungen. Legal & Regulatory: Rechtsdatenbanken und Kanzleisoftware. Corporate Performance & ESG: Software für Finanzplanung und Nachhaltigkeit. 85 % des Umsatzes kommen aus Abos und Verträgen, davon 24 % aus Cloud-Software (+14 %). Rund 60 % des Umsatzes stammen aus Nordamerika.",
"why": "Am 26. Februar 2025 kündigte die langjährige Chefin Nancy McKinstry ihren Rücktritt an, die Aktie fiel an einem Tag um 8 bis 14 %. Danach drückte die KI-Angst: Konkurrenten wie OpenEvidence (KI für Ärzte) und allgemeine KI-Modelle könnten UpToDate und die Rechtsdatenbanken ersetzen. Am 3. Februar 2026 stellte Anthropic ein Rechts-Plugin für Claude vor, Wolters Kluwer fiel an einem Tag um 10.5 %. Am 6. Mai fiel die Aktie um 13 %, weil das Wachstum im 1. Quartal bei 5 % blieb und nicht anzog. Ende Juni lag sie bei 54.64 €, rund 70 % unter dem Hoch. Die Halbjahreszahlen vom 5. August waren solide (Marge 29.4 %, Gewinn pro Aktie +14 % ohne Währungseffekte, Prognose bestätigt). JPMorgan (Juli) und Bernstein (Mai) stuften hoch. Im Oktober stieg die Aktie in einem Monat um 19 %. Einen klaren Auslöser dafür habe ich nicht gefunden.",
"kpis": [
 ["w","Organisches Wachstum","+5 %","1. Halbjahr 2026, ohne Zukäufe und Währungseffekte. 2021 bis 2025 jedes Jahr 6 %. Gemeldet −0.6 %, weil der Dollar schwach war (60 % des Umsatzes in den USA)."],
 ["g","Operative Marge","29.4 %","1. Halbjahr 2026 (bereinigt). Von 100 € Umsatz bleiben rund 29 € Betriebsgewinn. Seit 2021 jedes Jahr gestiegen (25.3 %). Sehr gut."],
 ["g","Gewinn pro Aktie (EPS)","5.42 €","Letzte 12 Monate, bereinigt. 2021: 3.38 €, also rund +12 % pro Jahr. Im 1. Halbjahr 2026 +14 % ohne Währungseffekte."],
 ["g","ROIC","18.2 %","Auf 100 € investiertes Kapital rund 18 € Gewinn. Gut und seit 2021 (13.7 %) gestiegen."],
 ["g","Free Cashflow","1.38 Mrd. €","Letzte 12 Monate (bereinigt), 22.5 % vom Umsatz. Seit 2021 von 1.0 Mrd. € gestiegen, nur 2023 ein kleiner Rückgang. 85 % Abo-Umsatz machen ihn gut planbar."],
 ["w","Nettoschulden","4.0 Mrd. €","2.0-mal der Betriebsgewinn vor Abschreibungen (EBITDA), im Zielband der Firma (1.5 bis 2.5). Seit 2021 verdoppelt, weil Rückkäufe und Dividende grösser waren als der Free Cashflow."],
 ["g","KGV","15.0","Auf den bereinigten Gewinn. Du zahlst 15 Jahresgewinne. Eigener Schnitt 2021–2025: rund 26. Also rund 43 % günstiger als üblich."],
 ["g","Dividende","3.1 %","2.52 € für 2025, zweimal pro Jahr: Schlussdividende 1.59 € (bezahlt 17.6.2026) und Zwischendividende 1.01 € (bezahlt 24.9.2026). Seit über 20 Jahren jedes Jahr erhöht."]
],
"revtitle": "Umsatz pro Halbjahr (Mio. €)", "revunit": "Mio. €", "epsunit": "€",
"revnote": "Wolters Kluwer berichtet halbjährlich. In Euro zuletzt leicht tiefer (−0.6 %), weil der Dollar schwach war. Ohne Währungseffekte +4 %, organisch +5 %.",
"marginnote": "Bereinigte operative Marge. Seit 2021 jedes Jahr gestiegen, im 1. Halbjahr 2026 auf 29.4 %. Für 2026 erwartet die Firma rund 28 %, weil sie im 2. Halbjahr mehr in KI-Produkte investiert.",
"finnote": "<b>Hinweis:</b> Marge, Gewinn pro Aktie und Free Cashflow sind die bereinigten Firmenwerte. Das KGV ist mit dem bereinigten Gewinn gerechnet. Die letzte Zeile ist Juli 2025 bis Juni 2026, Wachstum und Marge dort für das 1. Halbjahr 2026.",
"FIN": [["2021",4771,"+3.7 %","25.3 %",3.38,1010,"13.7 %","30.7"],["2022",5453,"+14.3 %","26.1 %",4.14,1220,"15.5 %","23.6"],["2023",5584,"+2.4 %","26.4 %",4.55,1164,"16.8 %","28.3"],["2024",5916,"+6.0 %","27.1 %",4.97,1276,"18.1 %","32.3"],["2025",6125,"+3.5 %","27.5 %",5.29,1348,"18.0 %","16.7"],["Letzte 12 Mt.",6106,"−0.6 %","29.4 %",5.42,1376,"18.2 %","15.0"]],
"QREV": [["H2 22",2853],["H1 23",2725],["H2 23",2859],["H1 24",2891],["H2 24",3025],["H1 25",3052],["H2 25",3073],["H1 26",3033]],
"revdec": 0,
"MARGIN": [["2021",25.3],["2022",26.1],["2023",26.4],["2024",27.1],["2025",27.5],["H1 26",29.4]],
"Q": [
 ["Umsatztrend","3 von 4 Halbjahren über Vorjahr in Euro, organisch alle positiv (+5 %)",10,15],
 ["Wachstumstempo","Organisch 5 % (vorher 6 %)",3,10],
 ["Operative Marge","29.4 % (9 Pkt.), seit 2021 jedes Jahr gestiegen (6 Pkt.)",15,15],
 ["Gewinnwachstum (EPS)","Bereinigt 2022–2025 rund +8.5 % pro Jahr, aktuell +14 % ohne Währungseffekte",8,10],
 ["Free Cashflow","Immer positiv, 3 von 4 Jahren gestiegen (2023 −4.6 %)",6,10],
 ["ROIC","18.2 % (10 Pkt.), seit 2021 steigend (+1)",11,15],
 ["Schulden","Nettoschulden/EBITDA 2.0",7,10],
 ["Bewertung vs. eigene Historie","KGV 15.0 statt Ø 26.3 (2021–2025), rund 43 % günstiger",14,15]
],
"adwnote": ADW + "Im Juni (Kurs 57 €) stand die Wochen-A/D bei 107, heute bei 111.7 bei 81.64 €. Sie steigt mit, aber viel schwächer als der Kurs: Der Anstieg seit Juni wird nur teilweise von grossen Käufen getragen.",
"rsiwnote": RSIW + "Von Januar bis Juni fast immer unter 30 (stark überverkauft, Tiefpunkt 15 im Februar), heute 67: kräftige Erholung, nahe überkauft.",
"addnote": "Am 3.9. stand der Kurs bei 70.58 € und die Tages-A/D bei −12.4. Heute steht der Kurs 16 % höher, die A/D aber tiefer bei −17.1 (grosser Abfluss am 18.9.). Seit dem 23.9. steigt sie wieder (−22.5 → −17.1). Gemischtes Bild.",
"ind": [
 ["Kurs vs. EMA 50","81.6 &gt; 70.3","81.6 &gt; 77.9","Über der mittelfristigen Linie, auf beiden Zeitebenen."],
 ["Kurs vs. EMA 200","81.6 &gt; 74.2","81.6 &lt; 103.7","Tag darüber, Woche noch weit darunter."],
 ["EMA 50 vs. EMA 200","50 unter 200 (seit März 2025), steigt aber","50 unter 200 (seit Dezember 2025)","Der grosse Trend ist noch abwärts, im Tageschart nähert sich das goldene Kreuz."],
 ["RSI (14)","77.5","66.7","Tag überkauft, Woche stark."],
 ["A/D","seit 23.9. steigend, aber tiefer als Anfang September","leicht steigend","Bestätigt den Anstieg nur teilweise."],
 ["Volumen","Ø 20 Tage 1.10 Mio. vs. Ø 100 Tage 1.23 Mio. Aktien","Der Anstieg läuft mit eher wenig Handel."]
],
"smc": "Vom Allzeithoch 181.30 € (Februar 2025) fiel Wolters Kluwer bis Juni 2026 in einem langen Abwärtstrend. Im Mai und Juni bildete sich ein doppelter Boden (55.90 € am 13.5. und 54.64 € am 25.6.). Danach höhere Tiefs: 59.16 € (23.7.), 64.86 € (11.9.), 65.84 € (1.10.). Am 12.10. brach der Kurs über die Hochs vom April (72.90 €) und Juli (74.12 €): Das ist ein bestätigter Change of Character nach oben, auch im Wochenchart. Seither stieg er auf 81.64 €. Die Aktie ist damit 49 % über dem Tief und im teuren Teil (Premium) der Bewegung. Nach so einem Ausbruch kommt oft ein Rücktest der Ausbruchszone 72 bis 75 €.",
"zones": [
 ["r","100–104 €","Widerstand: Wochen-EMA 200 (103.70 €)."],
 ["r","88–93 €","Widerstand: Jahresanfang 2026 (Hoch 93.12 € am 12.1.)."],
 ["t","83 €","<b>Trigger:</b> Tagesschluss über 83 € setzt den Ausbruch fort. Für einen Einstieg besser: Rücksetzer in Kaufzone 1."],
 ["s","72–75 €","<b>Kaufzone 1:</b> Ausbruchszone (Hochs April und Juli 72.90 / 74.12 €) und Tages-EMA 200 (74.20 €)."],
 ["s","65–68 €","<b>Kaufzone 2:</b> Tiefs vom September und Oktober (64.86 / 65.84 €)."],
 ["r","64.80 €","Abbruch: Wochenschluss unter dem Tief vom 11.9. Dann wäre die Wende gescheitert."]
],
"smart": [
 "<b>Wolters Kluwer selbst:</b> Rückkauf 2026 bis 500 Mio. € (rund 2.8 % des Börsenwerts), bis 16.9. für 264 Mio. € zu durchschnittlich 67.96 €. 2022 bis 2025 waren es jedes Jahr 1 bis 1.1 Mrd. €. Seit 2021 gibt es 13.6 % weniger Aktien.",
 "<b>Aufsichtsrat kauft:</b> Am 25./26.2.2026 kauften drei Aufsichtsräte nahe am Tief (zu 62.50 bis 64.12 €, zusammen rund 0.34 Mio. €), im November 2025 einer zu 97.49 €. Die Chefin Stacey Caywood kaufte im August 2025 zu 112.92 €.",
 "<b>Insider-Verkäufe:</b> Nur Verkäufe zur Steuerzahlung bei Aktienzuteilungen (CEO und CFO im Februar 2026). Keine freien Verkäufe.",
 "<b>Analysten:</b> Mehrheit positiv. StockAnalysis: 10× stark Kaufen, 2× Kaufen, 3× Halten, 1× Verkaufen. Kursziel im Schnitt 89.78 € (54 bis 120 €). Hochstufungen: Bernstein (Mai) und JPMorgan (Juli)."
],
"seasnote": SEAS + "31 Jahre Daten (seit 1995). September (+0.7 %, 69 %), Dezember (+2.1 %, 65 %) und Februar (68 %) sind gute Monate. Oktober +1.6 % (58 %), November +1.2 % (61 %).",
"T": [
 ["Trend Woche (EMA 50/200)","Kurs über EMA 50, unter EMA 200: mögliche Wende",8,20],
 ["Trend Tag (EMA 50/200)","Kurs über beiden, EMA 50 noch unter 200, aber steigend",7,10],
 ["Struktur (SMC)","Doppelter Boden, höhere Tiefs, CHoCH am 12.10. bestätigt, aber im Premium",14,20],
 ["RSI Tag/Woche","Tag 77.5 (überkauft), Woche 67",4,15],
 ["A/D Tag/Woche","Steigen mit, aber schwächer als der Kurs",8,20],
 ["Smart Money","Start 3, Rückkauf 2.8 % pro Jahr +3, Aufsichtsrats-Käufe älter als 6 Monate",6,10],
 ["Saisonalität","Oktober 58 %, November 61 %, Dezember 65 % positive Jahre",5,5]
],
"pro": [
 "85 % Abo-Umsatz, Kunden sind Spitäler, Treuhänder und Kanzleien, die die Produkte täglich brauchen.",
 "Marge steigt seit Jahren (29.4 %), Free Cashflow 1.38 Mrd. € (22.5 % vom Umsatz).",
 "KGV 15 statt rund 26, Free-Cashflow-Rendite 7.6 %, Dividende 3.1 % und seit über 20 Jahren steigend.",
 "UpToDate Expert AI bei über 90 % der US-Spitalkunden im Einsatz, Cloud-Software +14 %.",
 "Trendwende im Chart bestätigt, Aufsichtsräte kauften nahe am Tief."
],
"con": [
 "KI-Gefahr ist echt offen: Claude, ChatGPT und OpenEvidence könnten Preise und Kunden kosten. Preisdaten zeigt die Firma nicht.",
 "Wachstum etwas langsamer (5 % statt 6 %), Rechtsbereich am stärksten bedroht.",
 "Rückkäufe und Dividende waren 2022 bis 2025 grösser als der Free Cashflow, Schulden verdoppelt (4.0 Mrd. €).",
 "Höhere Investitionen in KI-Produkte könnten die Marge 2027 drücken (UBS).",
 "Kurzfristig überkauft (RSI 77.5) nach +49 % seit Juni."
],
"todo": [
 ["t","Beobachten","Alarm bei 75 € (oberes Ende Kaufzone 1) und 83 € (Trigger)."],
 ["s","Timing grün","Rücksetzer in 72–75 €, der hält, mit steigender A/D. Fundamental: Am 4.11. sollte das organische Wachstum mindestens 5 % bleiben und Tax & Accounting wie versprochen anziehen."],
 ["r","Abbruch","Wochenschluss unter 64.80 €."],
 ["","Nächste Zahlen","4. November 2026: Zwischenbericht 9 Monate (nur Umsatz und Wachstum, bestätigt). Jahreszahlen: 24. Februar 2027."]
],
"bands": [{"from":100,"to":104,"type":"res"},{"from":88,"to":93,"type":"res"},{"from":72,"to":75,"type":"sup"},{"from":65,"to":68,"type":"sup"}],
"refs": [{"v":83,"label":"Trigger 83"}],
"sources": L("https://stockanalysis.com/quote/ams/WKL/financials/","StockAnalysis.com") + " (Stand 16.10.2026), " + L("https://www.globenewswire.com/news-release/2026/08/05/3339046/0/en/Wolters-Kluwer-2026-Half-Year-Report.html","Wolters Kluwer Halbjahr 2026") + ", " + L("https://www.globenewswire.com/news-release/2026/02/25/3244280/0/en/wolters-kluwer-2025-full-year-report.html","Jahresbericht 2025") + ", " + L("https://www.canadianlawyermag.com/news/international/anthropic-legal-tool-jolts-share-price-of-global-legal-data-leaders/393665","Canadian Lawyer: Anthropic-Plugin") + ", " + L("https://www.debelegger.nl/post/aandeel-wolters-kluwer-daalt-vandaag-13-dit-is-waarom","De Belegger (6.5.2026)") + ", " + L("https://hl.co.uk/shares/shares-search-results/w/wolters-kluwer-cva-eur0.12/director-deals","Insider (HL)") + ", " + L("https://www.marketscreener.com/quote/stock/WOLTERS-KLUWER-N-V-6291/consensus/","Analysten (MarketScreener)") + "."
}
if __name__ == "__main__":
    json.dump(c, open(os.path.join(P, "config", "WKL.json"), "w"), ensure_ascii=False, indent=1)
    print("ok", sum(r[2] for r in c["Q"]), sum(r[2] for r in c["T"]))
