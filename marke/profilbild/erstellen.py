"""Profilbild-Entwürfe für @aktienampel26 rendern (1080×1080, kreissicher).

Aufruf: python marke/profilbild/erstellen.py
Ergebnis: marke/profilbild/<variante>.png und vorschau.png (so wirkt es als Kreis in Instagram)
"""
import asyncio, os

HIER = os.path.dirname(os.path.abspath(__file__))
ROT, GELB, GRUEN = "#E0483B", "#F0B429", "#2FA463"
TINTE, PAPIER = "#121212", "#F4F1EA"

SCHRIFT = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@800;900&display=swap">')

GLOW = """<filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
<feGaussianBlur stdDeviation="22" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>"""

# A: Balkendiagramm in Ampelfarben, steigend – Chart und Ampel in einem Zeichen
BALKEN = f"""<svg viewBox="0 0 1080 1080" xmlns="http://www.w3.org/2000/svg">
<defs>{GLOW}<radialGradient id="bg" cx="50%" cy="40%" r="75%"><stop offset="0" stop-color="#22242A"/><stop offset="1" stop-color="#0B0C0E"/></radialGradient></defs>
<rect width="1080" height="1080" fill="url(#bg)"/>
<g filter="url(#glow)">
<rect x="270" y="590" width="150" height="230" rx="34" fill="{ROT}"/>
<rect x="465" y="450" width="150" height="370" rx="34" fill="{GELB}"/>
<rect x="660" y="260" width="150" height="560" rx="34" fill="{GRUEN}"/>
</g>
<rect x="250" y="852" width="580" height="12" rx="6" fill="#F4F1EA" opacity=".9"/>
</svg>"""

# B: klassische Ampel im Zeitungsstil der Karussells, auf Grün
AMPEL = f"""<svg viewBox="0 0 1080 1080" xmlns="http://www.w3.org/2000/svg">
<defs>{GLOW}</defs>
<rect width="1080" height="1080" fill="{PAPIER}"/>
<rect x="395" y="160" width="290" height="760" rx="145" fill="{TINTE}"/>
<circle cx="540" cy="320" r="92" fill="{ROT}" opacity=".26"/>
<circle cx="540" cy="540" r="92" fill="{GELB}" opacity=".26"/>
<circle cx="540" cy="760" r="92" fill="{GRUEN}" filter="url(#glow)"/>
<circle cx="512" cy="732" r="22" fill="#fff" opacity=".35"/>
</svg>"""

# C: Trendlinie, die durch Rot, Gelb und Grün nach oben läuft
TREND = f"""<svg viewBox="0 0 1080 1080" xmlns="http://www.w3.org/2000/svg">
<defs>{GLOW}<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#16202E"/><stop offset="1" stop-color="#090D14"/></linearGradient></defs>
<rect width="1080" height="1080" fill="url(#bg)"/>
<polyline points="260,760 450,590 600,680 800,380" fill="none" stroke="{PAPIER}" stroke-width="40" stroke-linecap="round" stroke-linejoin="round"/>
<g filter="url(#glow)">
<circle cx="260" cy="760" r="78" fill="{ROT}"/>
<circle cx="450" cy="590" r="78" fill="{GELB}"/>
<circle cx="800" cy="380" r="96" fill="{GRUEN}"/>
</g>
</svg>"""

# D: Wortmarke wie der Kopf der Karussells, drei Ampelpunkte darüber
WORT = f"""<div style="width:1080px;height:1080px;background:{TINTE};display:flex;flex-direction:column;align-items:center;justify-content:center;gap:56px;font-family:'Inter Tight',sans-serif">
<div style="display:flex;gap:34px">{''.join(f'<span style="width:118px;height:118px;border-radius:50%;background:{c};box-shadow:0 0 60px {c}88"></span>' for c in (ROT, GELB, GRUEN))}</div>
<div style="color:{PAPIER};font-weight:900;font-size:150px;letter-spacing:-.05em;line-height:.9;text-align:center">AKTIEN<br>AMPEL</div></div>"""

VARIANTEN = {"a-balken": BALKEN, "b-ampel": AMPEL, "c-trend": TREND, "d-wortmarke": WORT}


def seite(inhalt):
    return f'<!doctype html><html><head><meta charset="utf-8">{SCHRIFT}<style>body{{margin:0}}svg{{display:block;width:1080px;height:1080px}}</style></head><body>{inhalt}</body></html>'


def vorschau():
    """Alle Varianten als Kreis, gross und in Feed-Grösse, auf weissem und dunklem Grund."""
    karten = ""
    for i, name in enumerate(VARIANTEN):
        buchstabe = "ABCD"[i]
        karten += f'''<div style="display:flex;flex-direction:column;align-items:center;gap:26px">
<img src="file:///{os.path.join(HIER, name + '.png').replace(os.sep, '/')}" style="width:300px;height:300px;border-radius:50%">
<div style="display:flex;gap:22px;align-items:center">
<img src="file:///{os.path.join(HIER, name + '.png').replace(os.sep, '/')}" style="width:88px;height:88px;border-radius:50%;border:1px solid #ddd">
<img src="file:///{os.path.join(HIER, name + '.png').replace(os.sep, '/')}" style="width:40px;height:40px;border-radius:50%"></div>
<b style="font:800 44px 'Inter Tight',sans-serif">{buchstabe}</b></div>'''
    return f'<div style="width:1600px;padding:60px 40px;background:#fff;display:flex;justify-content:space-around">{karten}</div>'


async def main():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--allow-file-access-from-files"])
        pg = await b.new_page(viewport={"width": 1080, "height": 1080})
        for name, inhalt in VARIANTEN.items():
            await pg.set_content(seite(inhalt), wait_until="networkidle")
            await pg.evaluate("document.fonts.ready")
            await pg.screenshot(path=os.path.join(HIER, name + ".png"))
        pg2 = await b.new_page(viewport={"width": 1600, "height": 520})
        open(os.path.join(HIER, "_vorschau.html"), "w", encoding="utf-8").write(seite(vorschau()))
        await pg2.goto("file:///" + os.path.join(HIER, "_vorschau.html").replace(os.sep, "/"), wait_until="networkidle")
        await pg2.screenshot(path=os.path.join(HIER, "vorschau.png"), full_page=True)
        os.remove(os.path.join(HIER, "_vorschau.html"))
        await b.close()
    print("fertig:", HIER)


if __name__ == "__main__":
    asyncio.run(main())
