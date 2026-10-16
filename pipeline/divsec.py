"""Dividenden-Abschnitt für die Cheat Sheets (Analyse-Seite und App)."""
import json, os

INFO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "div_info.json")
MON = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]
CUR = {"USD": "$", "CHF": "CHF", "EUR": "€", "GBp": "Pence"}


def info(t):
    return json.load(open(INFO)).get(t)


def months(ms):
    return ", ".join(MON[m - 1] for m in ms) if ms else "–"


def amount(v, cur):
    s = f"{v:.4f}".rstrip("0")
    s = s + "0" if s.endswith(".") else s
    if len(s.split(".")[1]) < 2:
        s = f"{v:.2f}"
    return f"{s} {CUR.get(cur, cur)}"


LAND = {"CHF": "Schweiz", "EUR": "Frankreich", "GBp": "Grossbritannien", "USD": "USA"}


def form(d, cur, land=None):
    if d.get("form"):
        return d["form"]
    land = land or LAND.get(cur, "")
    if land == "USA":
        return "Bar in US-Dollar aufs Konto. Die USA ziehen Quellensteuer ab, mit dem Formular W-8BEN bei Saxo in der Regel 15 %."
    if land == "Schweiz":
        return "Bar in Franken aufs Konto. Abzug von 35 % Verrechnungssteuer, die du mit der Steuererklärung zurückbekommst."
    if land == "Grossbritannien":
        return ("Bar in US-Dollar (über die US-Variante der Aktie, ADR). Grossbritannien zieht keine Quellensteuer ab, die ADR-Bank behält eine kleine Gebühr."
                if cur == "USD" else "Bar in Pfund aufs Konto. Grossbritannien zieht keine Quellensteuer ab.")
    if land == "Frankreich":
        return "Bar in Euro aufs Konto. Frankreich zieht Quellensteuer ab (je nach Bank 12.8 bis 25 %), einen Teil kannst du über die Steuererklärung anrechnen lassen."
    return "Bar aufs Konto, abzüglich Quellensteuer."


def section(t, cur, rendite=None, land=None):
    d = info(t)
    if not d:
        return ""
    if d.get("zahlt") is False:
        body = f'<p style="margin:0">{d["text"]}</p>'
    else:
        rows = [
            ("Wie oft", f'{d["pro_jahr"]}× pro Jahr ({d["rhythmus"]})'),
            ("Ex-Tag im", months(d.get("ex_monate"))),
            ("Geld auf dem Konto im", months(d.get("zahl_monate"))),
            ("Zahltage", d.get("zahl_text", "–")),
            ("Letzte Zahlung", amount(d["betrag"], cur) + " pro Aktie"),
        ]
        if rendite:
            rows.append(("Rendite", rendite))
        a = d.get("angekuendigt")
        if a:
            rows.append(("Angekündigt", f'Ex-Tag {a["ex"][8:10]}.{a["ex"][5:7]}.{a["ex"][:4]}, Zahltag {a["zahltag"][8:10]}.{a["zahltag"][5:7]}.{a["zahltag"][:4]}, {amount(a["betrag"], cur)}'))
        rows.append(("System", d["system"]))
        rows.append(("Form", form(d, cur, land)))
        if d.get("serie"):
            rows.append(("Geschichte", d["serie"]))
        trs = "".join(f"<tr><td style=\"white-space:nowrap;color:var(--muted)\">{k}</td><td>{v}</td></tr>" for k, v in rows)
        body = (f'<table>{trs}</table><p class="note" style="margin:10px 0 0"><b>Ex-Tag:</b> Du bekommst die Dividende nur, wenn du die Aktie am Abend vor dem Ex-Tag besitzt. '
                f'<b>Zahltag:</b> An diesem Tag kommt das Geld aufs Konto (in der Währung der Aktie, abzüglich Quellensteuer). Die nächsten genauen Termine zeigt die App unter «Termine».</p>')
    return f'<section>\n  <h2>Dividende</h2>\n  <div class="card tbl">{body}</div>\n</section>\n\n'


CH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chance")
SCHUB = {"stark": "Starker Wachstumsschub möglich", "mittel": "Wachstumsschub möglich", "schwach": "Kein grosser Schub in Sicht"}
SORGE = {"stimmung": "Vor allem Stimmung", "gemischt": "Echte Probleme, eher lösbar", "echt": "Das Geschäft verschlechtert sich"}


def chance(t):
    p = os.path.join(CH, f"{t}.json")
    return json.load(open(p)) if os.path.exists(p) else None


def chance_section(t, bew=None):
    c = chance(t)
    if not c:
        return ""
    e = lambda x: str(x).replace("&", "&amp;").replace("<", "&lt;")
    parts = []
    if bew and bew.get("wert") and bew.get("schnitt"):
        a = (1 - bew["wert"] / bew["schnitt"]) * 100
        txt = f"{a:.0f} % günstiger" if a >= 0 else f"{-a:.0f} % teurer"
        parts.append(f'<p style="margin:0 0 10px"><b>Bewertung:</b> {bew.get("typ","KGV")} {bew["wert"]:.1f} statt {bew["schnitt"]:.1f} im eigenen 5-Jahres-Schnitt, also {txt} als üblich (am Analysetag).</p>')
    parts.append(f'<h3>Was die Börse befürchtet</h3><p class="note" style="margin:4px 0">{e(SORGE.get(c.get("sorgen_art"), ""))}: {e(c.get("sorgen_art_text", ""))}</p><ul class="clean">' + "".join(f"<li>{e(x)}</li>" for x in c.get("sorgen", [])) + "</ul>")
    parts.append('<h3 style="margin-top:12px">Was die Sorgen beenden könnte</h3><ul class="clean">' + "".join(f'<li>{e(x["was"])} <span class="muted">({e(x.get("wann", ""))})</span></li>' for x in c.get("aufloeser", [])) + "</ul>")
    parts.append(f'<h3 style="margin-top:12px">Wachstumsschub: {e(SCHUB.get(c.get("schub_stufe"), ""))}</h3><ul class="clean">' + "".join(f'<li><b>{e(x["titel"])}:</b> {e(x["text"])} <span class="muted">({e(x.get("wann", ""))})</span></li>' for x in c.get("schub_treiber", [])) + "</ul>")
    if c.get("schub_beweis"):
        parts.append(f'<p style="margin:10px 0 0"><b>Woran du es erkennst:</b> {e(c["schub_beweis"])}</p>')
    if c.get("szenario"):
        parts.append(f'<p style="margin:10px 0 0"><b>Das Chancen-Szenario:</b> {e(c["szenario"])}</p>')
    if c.get("quellen"):
        parts.append('<p class="note" style="margin:10px 0 0">Quellen: ' + ", ".join(f'<a href="{e(q["url"])}" target="_blank" rel="noopener">{e(q["titel"])}</a>' for q in c["quellen"]) + "</p>")
    return '<section>\n  <h2>Worauf du achten solltest: Unterbewertung und Wachstumsschub</h2>\n  <div class="card">' + "".join(parts) + "</div>\n</section>\n\n"


def inject(html, t, cur, rendite=None, land=None, bew=None):
    key = "<section>\n  <h2>Pro und Contra</h2>"
    if key not in html:
        return html
    add = ""
    if "<h2>Worauf du achten solltest" not in html:
        add += chance_section(t, bew)
    if "<h2>Dividende</h2>" not in html:
        add += section(t, cur, rendite, land)
    return html.replace(key, add + key, 1) if add else html
